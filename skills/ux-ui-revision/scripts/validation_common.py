#!/usr/bin/env python3
"""Safe upstream-validation helpers for ux-ui-revision scripts."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


def parse_frontmatter_name(text: str) -> str | None:
    """Return the single YAML-frontmatter name scalar."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None

    values: list[str] = []
    for raw in lines[1:end]:
        match = re.match(r"^\s*name\s*:\s*(.*?)\s*$", raw)
        if not match:
            continue
        value = match.group(1).strip()
        if " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values.append(value)
    return values[0] if len(values) == 1 and values[0] else None


def locate_ux_ui_teardown_validator() -> Path | None:
    """Find the exact installed or sibling ux-ui-teardown validator."""
    candidates: list[Path] = []
    env = os.environ.get("UX_UI_TEARDOWN_SKILL")
    if env:
        candidates.append(Path(env))

    here = Path(__file__).resolve()
    try:
        candidates.append(here.parents[2] / "ux-ui-teardown")
    except IndexError:
        pass

    candidates.extend(
        [
            Path.home() / ".agents" / "skills" / "ux-ui-teardown",
            Path.home() / ".claude" / "skills" / "ux-ui-teardown",
        ]
    )

    seen: set[Path] = set()
    for root in candidates:
        try:
            root = root.expanduser().resolve()
        except OSError:
            continue
        if root in seen:
            continue
        seen.add(root)

        skill = root / "SKILL.md"
        validator = root / "scripts" / "validate_ux_ui_teardown.py"
        if not skill.is_file() or not validator.is_file():
            continue
        try:
            text = skill.read_text(encoding="utf-8")
        except OSError:
            continue
        if parse_frontmatter_name(text) == "ux-ui-teardown":
            return validator
    return None


def run_upstream_validator(teardown_dir: Path) -> tuple[bool, str]:
    """Run the exact ux-ui-teardown validator and return success plus output."""
    validator = locate_ux_ui_teardown_validator()
    if validator is None:
        return False, "could not locate installed ux-ui-teardown validator"
    try:
        proc = subprocess.run(
            [sys.executable, str(validator), str(teardown_dir.resolve())],
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"ux-ui-teardown validator could not run: {exc}"

    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        return False, output or f"ux-ui-teardown validator exited {proc.returncode}"
    return True, output or "passed"
