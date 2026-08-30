#!/usr/bin/env python3
"""Validate a brand-revision artifact against its canonical brand-teardown handoff."""
from __future__ import annotations

import argparse
from pathlib import Path

from validation_common import load_json, run_upstream_validator
from validator_common import _shape_teardown
from validator_shape import _shape_revision
from validator_semantic import _semantic_validate


def validate(teardown_dir: Path, revision_dir: Path, *, run_upstream: bool = True, check_markdown: bool = True) -> list[str]:
    teardown_dir = teardown_dir.resolve()
    revision_dir = revision_dir.resolve()
    errors: list[str] = []

    for name in ("findings.json", "coverage.json"):
        if not (teardown_dir / name).is_file():
            errors.append(f"missing teardown file: {name}")
    if not (revision_dir / "revision.json").is_file():
        errors.append("missing required file: revision.json")
    if not (revision_dir / "evidence").is_dir():
        errors.append("missing required directory: evidence")
    if errors:
        return errors

    if run_upstream:
        ok, output = run_upstream_validator(teardown_dir)
        if not ok:
            errors.append("brand-teardown upstream validation failed: " + output)
            return errors

    findings, e1 = load_json(teardown_dir / "findings.json")
    coverage, e2 = load_json(teardown_dir / "coverage.json")
    data, e3 = load_json(revision_dir / "revision.json")
    errors.extend(e1 + e2 + e3)
    if errors:
        return errors

    shape_errors: list[str] = []
    _shape_teardown(findings, coverage, shape_errors)
    _shape_revision(data, shape_errors)
    if shape_errors:
        return shape_errors

    assert isinstance(findings, dict) and isinstance(coverage, dict) and isinstance(data, dict)
    try:
        _semantic_validate(findings, coverage, data, revision_dir, errors, check_markdown)
    except Exception as exc:
        errors.append(f"validator internal guard caught unexpected semantic error: {type(exc).__name__}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown_directory", type=Path)
    parser.add_argument("revision_directory", type=Path)
    parser.add_argument("--skip-upstream-validation", action="store_true", help="Isolated tests only; never use to claim a production handoff is valid.")
    parser.add_argument("--skip-markdown-check", action="store_true", help="Testing/debug only.")
    args = parser.parse_args()
    errors = validate(
        args.teardown_directory,
        args.revision_directory,
        run_upstream=not args.skip_upstream_validation,
        check_markdown=not args.skip_markdown_check,
    )
    if errors:
        print(f"Brand revision validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("brand-revision validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
