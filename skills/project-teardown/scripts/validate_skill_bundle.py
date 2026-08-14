#!/usr/bin/env python3
"""Validate the integrity and installability of this skill bundle."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ALLOWED_TOP_LEVEL = {"SKILL.md", "agents", "assets", "references", "scripts"}
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER_PATTERN = re.compile(r"\A---\n([\s\S]*?)\n---\n")
FRONTMATTER_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.+)$")
QUOTED_YAML_VALUE = re.compile(r'^\s{2}(display_name|short_description|default_prompt):\s+"([^"\\]*(?:\\.[^"\\]*)*)"\s*$')


def read_utf8(path: Path, errors: list[str]) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"cannot read {path.relative_to(path.parents[1])}: {exc}")
        return ""
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{path.name} must not contain a UTF-8 BOM")
    if b"\r\n" in raw or b"\r" in raw:
        errors.append(f"{path.name} must use LF line endings")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{path.name} is not valid UTF-8: {exc}")
        return ""


def parse_frontmatter(text: str, errors: list[str]) -> dict[str, str]:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        errors.append("SKILL.md must begin with YAML frontmatter delimited by ---")
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        parsed = FRONTMATTER_LINE.match(line)
        if not parsed:
            errors.append(f"SKILL.md has unsupported frontmatter line: {line!r}")
            continue
        values[parsed.group(1)] = parsed.group(2).strip().strip('"')
    expected = {"name", "description"}
    if set(values) != expected:
        missing = sorted(expected - set(values))
        extra = sorted(set(values) - expected)
        if missing:
            errors.append(f"SKILL.md frontmatter missing keys: {', '.join(missing)}")
        if extra:
            errors.append(f"SKILL.md frontmatter has unexpected keys: {', '.join(extra)}")
    return values


def validate_openai_yaml(root: Path, skill_name: str, errors: list[str]) -> None:
    path = root / "agents" / "openai.yaml"
    if not path.is_file():
        errors.append("missing agents/openai.yaml")
        return
    text = read_utf8(path, errors)
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != "interface:":
        errors.append("agents/openai.yaml must contain only an interface mapping")
        return
    if any(not line.startswith("  ") for line in lines[1:]):
        errors.append("agents/openai.yaml contains unsupported top-level keys")
    values = {}
    for line in lines[1:]:
        match = QUOTED_YAML_VALUE.match(line)
        if not match:
            errors.append(f"agents/openai.yaml has invalid or unquoted line: {line!r}")
            continue
        values[match.group(1)] = match.group(2)
    expected = {"display_name", "short_description", "default_prompt"}
    if set(values) != expected:
        errors.append("agents/openai.yaml must define display_name, short_description, and default_prompt exactly once")
    description = values.get("short_description", "")
    if description and not 25 <= len(description) <= 64:
        errors.append("agents/openai.yaml short_description must be 25-64 characters")
    if values.get("default_prompt") and f"${skill_name}" not in values["default_prompt"]:
        errors.append(f"agents/openai.yaml default_prompt must mention ${skill_name}")


def validate_links(root: Path, errors: list[str]) -> None:
    for path in sorted(root.rglob("*.md")):
        text = read_utf8(path, errors)
        for target in LINK_PATTERN.findall(text):
            target = target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            resolved = (path.parent / target_path).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(root)} links outside the skill bundle: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(root)} has a broken relative link: {target}")


def validate(root: Path, mode: str = "installed") -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return ["skill root does not exist or is not a directory"]
    unexpected = sorted(path.name for path in root.iterdir() if path.name not in ALLOWED_TOP_LEVEL)
    if unexpected:
        errors.append(f"unexpected top-level entries: {', '.join(unexpected)}")
    if mode not in {"installed", "package"}:
        return [f"unknown validation mode: {mode}"]
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if path.is_symlink():
            errors.append(f"skill bundle must not contain symlinks: {rel}")
        if mode == "package" and ("__pycache__" in rel.parts or path.suffix == ".pyc"):
            errors.append(f"skill package contains generated Python cache: {rel}")

    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        errors.append("missing SKILL.md")
        return errors
    skill_text = read_utf8(skill_path, errors)
    frontmatter = parse_frontmatter(skill_text, errors)
    skill_name = frontmatter.get("name", "")
    if skill_name and root.name != skill_name:
        errors.append(f"skill folder name {root.name!r} does not match frontmatter name {skill_name!r}")
    if frontmatter.get("description") and len(frontmatter["description"].strip()) < 40:
        errors.append("SKILL.md description is too vague to support reliable invocation")
    if not re.search(r"^#\s+\S", skill_text, re.MULTILINE):
        errors.append("SKILL.md is missing a top-level heading")

    validate_openai_yaml(root, skill_name, errors)
    validate_links(root, errors)

    schemas = sorted(root.rglob("*.schema.json"))
    for path in schemas:
        try:
            value = json.loads(read_utf8(path, errors))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(root)} is invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.relative_to(root)} must contain a JSON object")

    scripts_dir = root / "scripts"
    validators = sorted(scripts_dir.glob("validate_*.py")) if scripts_dir.is_dir() else []
    tests = sorted(scripts_dir.glob("test_*.py")) if scripts_dir.is_dir() else []
    if not validators:
        errors.append("skill bundle must contain at least one scripts/validate_*.py validator")
    if not tests:
        errors.append("skill bundle must contain at least one scripts/test_*.py regression suite")
    for path in sorted(scripts_dir.glob("*.py")) if scripts_dir.is_dir() else []:
        text = read_utf8(path, errors)
        if path.name.startswith(("validate_", "test_")):
            if not text.startswith("#!/usr/bin/env python3\n"):
                errors.append(f"{path.relative_to(root)} must begin with a Python 3 shebang")
            if os.name != "nt" and not os.access(path, os.X_OK):
                errors.append(f"{path.relative_to(root)} must be executable")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--mode",
        choices=("installed", "package"),
        default="installed",
        help="installed ignores runtime caches; package rejects generated caches before distribution",
    )
    args = parser.parse_args()
    errors = validate(args.skill_directory.resolve(), mode=args.mode)
    if errors:
        print("Skill bundle validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Skill bundle validation passed ({args.mode} mode).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
