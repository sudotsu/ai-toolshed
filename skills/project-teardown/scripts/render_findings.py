#!/usr/bin/env python3
"""Generate or check 05-findings-register.md from canonical findings.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from finding_model import render_findings_register


def load_payload(root: Path) -> dict:
    path = root / "findings.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("findings.json must contain an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown", type=Path)
    parser.add_argument("--check", action="store_true", help="fail instead of writing when the generated view differs")
    args = parser.parse_args()
    root = args.teardown.resolve()
    try:
        expected = render_findings_register(load_payload(root))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"Cannot render findings register: {exc}", file=sys.stderr)
        return 1
    target = root / "05-findings-register.md"
    if args.check:
        try:
            actual = target.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Cannot read {target}: {exc}", file=sys.stderr)
            return 1
        if actual != expected:
            print("05-findings-register.md is stale; rerun render_findings.py without --check", file=sys.stderr)
            return 1
        print("Findings register is current")
        return 0
    try:
        target.write_text(expected, encoding="utf-8")
    except OSError as exc:
        print(f"Cannot write {target}: {exc}", file=sys.stderr)
        return 1
    print(f"Generated {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
