#!/usr/bin/env python3
"""Generate or check the project-teardown README index from findings.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from finding_model import render_readme


def load_payload(root: Path) -> dict:
    path = root / "findings.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("findings.json must contain an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown", type=Path)
    parser.add_argument("--check", action="store_true", help="fail instead of writing when README.md differs")
    args = parser.parse_args()
    root = args.teardown.resolve()
    try:
        expected = render_readme(load_payload(root))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"Cannot render README.md: {exc}", file=sys.stderr)
        return 1
    target = root / "README.md"
    if args.check:
        try:
            actual = target.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Cannot read {target}: {exc}", file=sys.stderr)
            return 1
        if actual != expected:
            print("README.md is stale; rerun render_readme.py without --check", file=sys.stderr)
            return 1
        print("README.md is current")
        return 0
    target.write_text(expected, encoding="utf-8")
    print(f"Generated {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
