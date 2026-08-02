#!/usr/bin/env python3
"""Validate the seo-revision skill package and regression suite."""

from __future__ import annotations

import argparse
import os
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path


REQUIRED = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/revision-contract.md",
    "references/authority-and-external-actions.md",
    "references/verification-and-convergence.md",
    "references/forward-testing.md",
    "scripts/render_revision.py",
    "scripts/validate_seo_revision.py",
    "scripts/test_validator.py",
    "scripts/validate_skill.py",
)
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def validate(root: Path, run_tests: bool = True) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED:
        if not (root / rel).is_file():
            errors.append(f"missing skill file: {rel}")
    if errors:
        return errors

    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\n([\s\S]*?)\n---\n", skill)
    if not frontmatter:
        errors.append("SKILL.md frontmatter is malformed")
    else:
        body = frontmatter.group(1)
        if not re.search(r"^name:\s*seo-revision\s*$", body, re.MULTILINE):
            errors.append("SKILL.md name must be seo-revision")
        description = re.search(r"^description:\s*(.+)$", body, re.MULTILINE)
        if not description or len(description.group(1).strip()) < 100:
            errors.append("SKILL.md description must be specific and useful")
        keys = [
            line.split(":", 1)[0].strip()
            for line in body.splitlines()
            if ":" in line and not line.startswith((" ", "\t"))
        ]
        if keys != ["name", "description"]:
            errors.append("SKILL.md frontmatter may contain only name and description")

    yaml_text = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    yaml_requirements = (
        (r"(?m)^\s*display_name:\s*[\"']?SEO Revision[\"']?\s*$", "display_name: SEO Revision"),
        (r"(?m)^\s*short_description:\s*.+$", "short_description"),
        (r"(?m)^\s*default_prompt:\s*.+$", "default_prompt"),
        (r"\$seo-revision", "$seo-revision"),
    )
    for pattern, label in yaml_requirements:
        if not re.search(pattern, yaml_text):
            errors.append(f"agents/openai.yaml missing {label!r}")

    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
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
        for path in (root / "scripts").glob("*.py"):
            try:
                py_compile.compile(
                    str(path),
                    cfile=str(compile_root / f"{path.stem}.pyc"),
                    doraise=True,
                )
            except py_compile.PyCompileError as exc:
                errors.append(f"Python compilation failed for {path.name}: {exc.msg}")

        if run_tests and not errors:
            env = os.environ.copy()
            env["PYTHONPYCACHEPREFIX"] = str(compile_root / "runtime-cache")
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "unittest", "-v", "test_validator.py"],
                    cwd=root / "scripts",
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=180,
                )
            except subprocess.TimeoutExpired:
                errors.append("validator regression tests timed out after 180 seconds")
                return errors
            if proc.returncode != 0:
                errors.append(
                    "validator regression tests failed:\n" + proc.stdout + proc.stderr
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill", nargs="?", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--no-tests", action="store_true")
    args = parser.parse_args()
    errors = validate(args.skill.resolve(), run_tests=not args.no_tests)
    if errors:
        print(f"Skill validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("seo-revision skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
