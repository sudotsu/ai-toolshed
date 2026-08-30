#!/usr/bin/env python3
"""Validate the brand-revision skill package and its declared regression suite."""
from __future__ import annotations

import argparse
import json
import os
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REQUIRED_TARGETS = {"claude-code", "codex", "claude-desktop-code", "chatgpt-desktop-codex"}
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER = re.compile(r"^---\n([\s\S]*?)\n---\n")


def validate(root: Path, run_tests: bool = True) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    manifest_path = root / "skill-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"invalid skill-manifest.json: {exc}"]
    if manifest.get("schema_version") != 1 or manifest.get("name") != "brand-revision":
        errors.append("manifest must declare schema_version 1 and name brand-revision")
    targets = manifest.get("targets")
    if not isinstance(targets, list) or set(targets) != REQUIRED_TARGETS:
        errors.append("manifest must declare exactly the four required runtime targets")
    required = manifest.get("required_files")
    if not isinstance(required, list) or not required:
        errors.append("manifest required_files must be a non-empty list")
        required = []
    for rel in required:
        if not isinstance(rel, str) or Path(rel).is_absolute() or ".." in Path(rel).parts:
            errors.append(f"invalid required_files path: {rel!r}")
        elif not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")

    skill_path = root / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        match = FRONTMATTER.match(text)
        if not match:
            errors.append("SKILL.md frontmatter is malformed")
        else:
            block = match.group(1)
            keys = [line.split(":", 1)[0].strip() for line in block.splitlines() if line and not line[0].isspace() and ":" in line]
            if set(keys) != {"name", "description"}:
                errors.append("SKILL.md frontmatter must contain only name and description")
            if not re.search(r"(?m)^name:\s*brand-revision\s*$", block):
                errors.append("SKILL.md name must be brand-revision")
            desc = re.search(r"(?m)^description:\s*(.+)$", block)
            if not desc or len(desc.group(1).strip()) < 80:
                errors.append("SKILL.md description must be specific and at least 80 characters")
    yaml_path = root / "agents/openai.yaml"
    if yaml_path.is_file():
        yaml = yaml_path.read_text(encoding="utf-8")
        for needle in ("display_name: Brand Revision", "short_description:", "default_prompt:", "$brand-revision"):
            if needle not in yaml.replace('"', ""):
                errors.append(f"agents/openai.yaml missing {needle!r}")

    for md in root.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            clean = target.split("#", 1)[0]
            if not clean or "://" in clean or clean.startswith("mailto:"):
                continue
            resolved = (md.parent / clean).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"{md.relative_to(root)} links outside the skill: {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken local link in {md.relative_to(root)}: {target}")

    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        for py in sorted((root / "scripts").glob("*.py")):
            try:
                py_compile.compile(str(py), cfile=str(temp_path / f"{py.stem}.pyc"), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"Python compile failed for {py.name}: {exc.msg}")
        if run_tests and not errors:
            env = os.environ.copy()
            env["PYTHONPYCACHEPREFIX"] = str(temp_path / "pycache")
            proc = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"],
                cwd=root / "scripts", env=env, capture_output=True, text=True, timeout=300, check=False,
            )
            if proc.returncode != 0:
                errors.append("validator regression tests failed:\n" + proc.stdout + proc.stderr)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-tests", action="store_true")
    args = parser.parse_args()
    errors = validate(args.skill, run_tests=not args.no_tests)
    if errors:
        print(f"Skill validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("brand-revision skill validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
