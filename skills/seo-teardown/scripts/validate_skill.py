#!/usr/bin/env python3
"""Validate the seo-teardown skill package itself."""

from __future__ import annotations

import argparse
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REQUIRED = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/audit-methodology.md",
    "references/platform-research.md",
    "references/report-contract.md",
    "references/forward-testing.md",
    "scripts/render_handoff.py",
    "scripts/validate_seo_teardown.py",
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
    if not skill.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
    frontmatter_match = re.match(r"^---\n([\s\S]*?)\n---\n", skill)
    if not frontmatter_match:
        errors.append("SKILL.md frontmatter is malformed")
    else:
        frontmatter = frontmatter_match.group(1)
        if not re.search(r"^name:\s*seo-teardown\s*$", frontmatter, re.MULTILINE):
            errors.append("SKILL.md name must be seo-teardown")
        description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        if not description or len(description.group(1).strip()) < 80:
            errors.append("SKILL.md description must be specific and useful")

    yaml_text = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    for required_text in (
        "display_name: SEO Teardown",
        "short_description:",
        "default_prompt:",
        "$seo-teardown",
        "allow_implicit_invocation: true",
    ):
        if required_text not in yaml_text:
            errors.append(f"agents/openai.yaml missing {required_text!r}")

    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (path.parent / target).resolve()
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
                errors.append(f"Python compile failed for {path.name}: {exc.msg}")

    if run_tests and not errors:
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "-v", "test_validator.py"],
            cwd=root / "scripts",
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            errors.append("validator regression tests failed:\n" + proc.stdout + proc.stderr)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-tests", action="store_true")
    args = parser.parse_args()
    root = args.skill.resolve()
    errors = validate(root, run_tests=not args.no_tests)
    if errors:
        print(f"Skill validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("seo-teardown skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
