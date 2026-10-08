#!/usr/bin/env python3
"""Validate the ux-ui-teardown skill package, portability metadata, and tests."""
from __future__ import annotations

import argparse
import json
import py_compile
import re
import subprocess
import tempfile
from pathlib import Path

SKILL_NAME = "ux-ui-teardown"
DISPLAY_NAME = "UX/UI Teardown"
TARGETS = {"claude-code", "codex", "claude-desktop-code", "chatgpt-desktop-codex"}
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def text(value):
    return isinstance(value, str) and bool(value.strip())


def validate(root: Path, run_tests: bool = True) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "skill-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"invalid manifest: {exc}"]
    if not isinstance(manifest, dict):
        return ["skill-manifest.json must be an object"]
    if manifest.get("schema_version") != 1:
        errors.append("skill-manifest.json schema_version must be 1")
    if manifest.get("name") != SKILL_NAME:
        errors.append(f"skill-manifest.json name must be {SKILL_NAME}")
    targets = manifest.get("targets")
    if not isinstance(targets, list) or not all(isinstance(item, str) for item in targets) or set(targets) != TARGETS or len(targets) != len(TARGETS):
        errors.append("skill-manifest.json must declare each supported runtime target exactly once")
    required_files = manifest.get("required_files")
    if not isinstance(required_files, list) or not required_files or not all(text(item) for item in required_files):
        errors.append("skill-manifest.json required_files must be a non-empty string list")
        required_files = []
    for rel in required_files:
        if not (root / rel).is_file():
            errors.append(f"missing skill file: {rel}")

    skill_path = root / "SKILL.md"
    if skill_path.is_file():
        skill = skill_path.read_text(encoding="utf-8")
        match = re.match(r"^---\n([\s\S]*?)\n---\n", skill)
        if not match:
            errors.append("SKILL.md frontmatter is malformed")
        else:
            frontmatter = match.group(1)
            keys = [
                line.split(":", 1)[0].strip()
                for line in frontmatter.splitlines()
                if ":" in line and not line.startswith((" ", "\t"))
            ]
            if keys != ["name", "description"]:
                errors.append("SKILL.md frontmatter may contain only name and description")
            if not re.search(rf"^name:\s*{re.escape(SKILL_NAME)}\s*$", frontmatter, re.MULTILINE):
                errors.append(f"SKILL.md name must be {SKILL_NAME}")
            description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
            minimum = manifest.get("frontmatter", {}).get("description_min_length", 80) if isinstance(manifest.get("frontmatter"), dict) else 80
            if not description or len(description.group(1).strip()) < minimum:
                errors.append(f"SKILL.md description must be at least {minimum} characters")

    adapter_path = root / "agents" / "openai.yaml"
    if adapter_path.is_file():
        adapter = adapter_path.read_text(encoding="utf-8")
        checks = [
            (rf"(?m)^\s*display_name:\s*[\"']?{re.escape(DISPLAY_NAME)}[\"']?\s*$", "display_name"),
            (r"(?m)^\s*short_description:\s*.+$", "short_description"),
            (r"(?m)^\s*default_prompt:\s*.+$", "default_prompt"),
            (re.escape(f"${SKILL_NAME}"), f"${SKILL_NAME}"),
        ]
        for pattern, label in checks:
            if not re.search(pattern, adapter):
                errors.append(f"agents/openai.yaml missing {label}")

    for path in root.rglob("*.md"):
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            clean = target.split("#", 1)[0]
            if not clean or "://" in clean or clean.startswith("mailto:"):
                continue
            resolved = (path.parent / clean).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(root)} links outside the skill: {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken local link in {path.relative_to(root)}: {target}")

    with tempfile.TemporaryDirectory() as temp:
        compile_root = Path(temp)
        scripts = root / "scripts"
        if scripts.is_dir():
            for path in scripts.glob("*.py"):
                try:
                    py_compile.compile(str(path), cfile=str(compile_root / f"{path.stem}.pyc"), doraise=True)
                except py_compile.PyCompileError as exc:
                    errors.append(f"Python compilation failed for {path.name}: {exc.msg}")

    tests = manifest.get("tests", [])
    if not isinstance(tests, list):
        errors.append("skill-manifest.json tests must be a list")
        tests = []
    if run_tests and not errors:
        for index, test in enumerate(tests):
            if not isinstance(test, dict) or not isinstance(test.get("command"), list) or not all(text(item) for item in test.get("command", [])):
                errors.append(f"tests[{index}] command invalid")
                continue
            cwd = root / test.get("cwd", ".")
            timeout = test.get("timeout_seconds", 300)
            try:
                proc = subprocess.run(test["command"], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=timeout)
            except (OSError, subprocess.TimeoutExpired) as exc:
                errors.append(f"tests[{index}] failed to run: {exc}")
                continue
            if proc.returncode != 0:
                errors.append(f"tests[{index}] failed:\n{proc.stdout}{proc.stderr}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-tests", action="store_true")
    args = parser.parse_args()
    errors = validate(args.root.resolve(), run_tests=not args.no_tests)
    if errors:
        print(f"Skill validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("ux-ui-teardown package validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
