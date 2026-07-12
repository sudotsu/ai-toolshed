#!/usr/bin/env python3
"""Validate the deterministic handoff contract for a project teardown."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path


REQUIRED_FILES = (
    "00-executive-verdict.md",
    "01-product-and-market.md",
    "02-user-experience.md",
    "03-technical-audit.md",
    "04-security-and-reliability.md",
    "05-findings-register.md",
    "06-implementation-sequence.md",
    "07-review-coverage.md",
)

REQUIRED_FIELDS = (
    "Type",
    "Category",
    "Severity",
    "Confidence",
    "Status",
    "Impact",
    "Evidence",
    "Expected behavior",
    "Actual behavior",
    "Root cause",
    "Affected components",
    "Recommendation",
    "If implemented",
    "If unchanged",
    "Dependencies",
    "Dependents",
    "Conflicts",
    "Acceptance criteria",
    "Verification",
    "Estimated scope",
    "Regression risk",
    "Action",
    "Strategic classification",
)

CONTROLLED = {
    "Type": {"defect", "shortcoming", "recommendation", "opportunity", "investigation", "strength"},
    "Severity": {"critical", "high", "medium", "low", "informational"},
    "Confidence": {"confirmed", "high", "medium", "low"},
    "Status": {"open", "blocked", "decision-required", "accepted-risk"},
    "Estimated scope": {"trivial", "small", "medium", "large", "initiative"},
    "Regression risk": {"low", "medium", "high"},
    "Action": {"fix", "add", "change", "remove", "investigate", "decide", "retain"},
}

FINDING_HEADING = re.compile(r"^## ([A-Z][A-Z0-9]*-\d{3}) — (.+)$", re.MULTILINE)
FIELD_LINE = re.compile(r"^- \*\*(.+?):\*\*\s*(.+)$", re.MULTILINE)
ID_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*-\d{3}\b")
REVIEW_STATUS = re.compile(r"^\*\*Review status:\*\*\s*(complete|provisional)\s*$", re.MULTILINE)
CORE_STATUS = re.compile(r"^\*\*Core workflows fully exercised:\*\*\s*(yes|no)\s*$", re.MULTILINE)
COVERAGE_STATUSES = {"passed", "failed", "partial", "blocked", "not-tested", "not-applicable"}


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}

    for name in REQUIRED_FILES:
        path = root / name
        if not path.is_file():
            errors.append(f"missing required file: {name}")
        else:
            texts[name] = path.read_text(encoding="utf-8")

    if errors:
        return errors

    executive = texts["00-executive-verdict.md"]
    coverage = texts["07-review-coverage.md"]
    executive_status = REVIEW_STATUS.search(executive)
    coverage_status = REVIEW_STATUS.search(coverage)
    core_status = CORE_STATUS.search(coverage)

    if not executive_status:
        errors.append("00-executive-verdict.md is missing an exact Review status line")
    if not coverage_status:
        errors.append("07-review-coverage.md is missing an exact Review status line")
    if not core_status:
        errors.append("07-review-coverage.md is missing an exact Core workflows fully exercised line")
    if executive_status and coverage_status and executive_status.group(1) != coverage_status.group(1):
        errors.append("review status differs between executive verdict and review coverage")
    if core_status and core_status.group(1) == "no" and coverage_status and coverage_status.group(1) != "provisional":
        errors.append("review must be provisional when core workflows were not fully exercised")

    register = texts["05-findings-register.md"]
    matches = list(FINDING_HEADING.finditer(register))
    if not matches:
        errors.append("findings register contains no valid finding headings")
        return errors

    ids = [match.group(1) for match in matches]
    duplicates = [finding_id for finding_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate finding IDs: {', '.join(sorted(duplicates))}")

    for index, match in enumerate(matches):
        finding_id = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(register)
        block = register[match.end():end]
        fields = dict(FIELD_LINE.findall(block))
        missing = [field for field in REQUIRED_FIELDS if field not in fields]
        if missing:
            errors.append(f"{finding_id} missing fields: {', '.join(missing)}")
        for field, allowed in CONTROLLED.items():
            value = fields.get(field)
            if value is not None and value not in allowed:
                errors.append(f"{finding_id} has invalid {field} value: {value!r}")

    sequence = texts["06-implementation-sequence.md"]
    ledger_match = re.search(r"^## Coverage ledger\s*$([\s\S]*)", sequence, re.MULTILINE)
    if not ledger_match:
        errors.append("06-implementation-sequence.md is missing a Coverage ledger section")
    else:
        ledger_ids = ID_TOKEN.findall(ledger_match.group(1))
        counts = Counter(ledger_ids)
        missing_from_ledger = sorted(set(ids) - set(ledger_ids))
        unknown_in_ledger = sorted(set(ledger_ids) - set(ids))
        repeated_in_ledger = sorted(finding_id for finding_id, count in counts.items() if count != 1)
        if missing_from_ledger:
            errors.append(f"findings missing from coverage ledger: {', '.join(missing_from_ledger)}")
        if unknown_in_ledger:
            errors.append(f"unknown IDs in coverage ledger: {', '.join(unknown_in_ledger)}")
        if repeated_in_ledger:
            errors.append(f"finding IDs repeated in coverage ledger: {', '.join(repeated_in_ledger)}")

    if "Narrative reconciliation" not in coverage:
        errors.append("07-review-coverage.md is missing Narrative reconciliation")
    surface_match = re.search(
        r"^## Surface coverage\s*$([\s\S]*?)(?=^## |\Z)", coverage, re.MULTILINE
    )
    if not surface_match:
        errors.append("07-review-coverage.md is missing Surface coverage")
    else:
        table_rows = []
        for line in surface_match.group(1).splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                continue
            table_rows.append(cells)
        if len(table_rows) < 2:
            errors.append("Surface coverage must contain a header and at least one data row")
        else:
            header = [cell.lower() for cell in table_rows[0]]
            expected_header = ["surface", "importance", "status", "evidence", "limitations", "next step"]
            if header != expected_header:
                errors.append("Surface coverage table has an invalid header")
            for row_number, row in enumerate(table_rows[1:], start=1):
                if len(row) != 6:
                    errors.append(f"Surface coverage row {row_number} must contain six columns")
                elif row[2] not in COVERAGE_STATUSES:
                    errors.append(f"Surface coverage row {row_number} has invalid status: {row[2]!r}")
    if "Validator result" not in coverage:
        errors.append("07-review-coverage.md is missing Validator result")

    return errors


def self_test() -> int:
    fields = "\n".join(
        f"- **{field}:** {next(iter(CONTROLLED[field])) if field in CONTROLLED else 'None'}"
        for field in REQUIRED_FIELDS
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        for name in REQUIRED_FILES:
            (root / name).write_text(f"# {name}\n", encoding="utf-8")
        (root / "00-executive-verdict.md").write_text(
            "# Verdict\n\n**Review status:** complete\n", encoding="utf-8"
        )
        (root / "05-findings-register.md").write_text(
            f"# Findings register\n\n## TEST-001 — Fixture\n\n{fields}\n", encoding="utf-8"
        )
        (root / "06-implementation-sequence.md").write_text(
            "# Sequence\n\n## Coverage ledger\n\n- TEST-001\n", encoding="utf-8"
        )
        (root / "07-review-coverage.md").write_text(
            "# Coverage\n\n**Review status:** complete\n\n"
            "**Core workflows fully exercised:** yes\n\n"
            "## Surface coverage\n\n"
            "| Surface | Importance | Status | Evidence | Limitations | Next step |\n"
            "|---|---|---|---|---|---|\n"
            "| Core workflow | defining | passed | fixture | None | None |\n\n"
            "## Narrative reconciliation\n\n## Validator result\n",
            encoding="utf-8",
        )
        errors = validate(root)
        if errors:
            print("Self-test failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
    print("Self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown", nargs="?", type=Path, help="Path to the project-teardown directory")
    parser.add_argument("--self-test", action="store_true", help="Run the validator's built-in fixture test")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.teardown is None:
        parser.error("teardown path is required unless --self-test is used")

    errors = validate(args.teardown)
    if errors:
        print(f"Teardown validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Teardown validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
