#!/usr/bin/env python3
"""Validate a project-teardown handoff, including its implementation graph."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "00-executive-verdict.md",
    "01-product-and-market.md",
    "02-user-experience.md",
    "03-technical-audit.md",
    "04-security-and-reliability.md",
    "05-findings-register.md",
    "06-implementation-sequence.md",
    "07-review-coverage.md",
    "findings.json",
)

FIELDS = (
    "type", "category", "severity", "confidence", "status", "impact", "evidence",
    "expected_behavior", "actual_behavior", "root_cause", "affected_components",
    "recommendation", "if_implemented", "if_unchanged", "dependencies", "dependents",
    "conflicts", "acceptance_criteria", "verification", "estimated_scope",
    "regression_risk", "action", "strategic_classification",
)

MARKDOWN_LABELS = {
    "type": "Type", "category": "Category", "severity": "Severity",
    "confidence": "Confidence", "status": "Status", "impact": "Impact",
    "evidence": "Evidence", "expected_behavior": "Expected behavior",
    "actual_behavior": "Actual behavior", "root_cause": "Root cause",
    "affected_components": "Affected components", "recommendation": "Recommendation",
    "if_implemented": "If implemented", "if_unchanged": "If unchanged",
    "dependencies": "Dependencies", "dependents": "Dependents", "conflicts": "Conflicts",
    "acceptance_criteria": "Acceptance criteria", "verification": "Verification",
    "estimated_scope": "Estimated scope", "regression_risk": "Regression risk",
    "action": "Action", "strategic_classification": "Strategic classification",
}

CONTROLLED = {
    "type": {"defect", "shortcoming", "recommendation", "opportunity", "investigation", "strength"},
    "severity": {"critical", "high", "medium", "low", "informational"},
    "confidence": {"confirmed", "high", "medium", "low"},
    "status": {"open", "blocked", "decision-required", "accepted-risk"},
    "estimated_scope": {"trivial", "small", "medium", "large", "initiative"},
    "regression_risk": {"low", "medium", "high"},
    "action": {"fix", "add", "change", "remove", "investigate", "decide", "retain"},
}

ARRAY_FIELDS = {
    "evidence", "affected_components", "dependencies", "dependents", "conflicts",
    "acceptance_criteria", "strategic_classification",
}

TOP_LEVEL = {"schema_version", "project", "audited_revision", "review_status", "generated_at", "findings"}
COVERAGE_STATUSES = {"passed", "failed", "partial", "blocked", "not-tested", "not-applicable"}
FINDING_HEADING = re.compile(r"^## ([A-Z][A-Z0-9]*-\d{3}) — (.+)$", re.MULTILINE)
FIELD_LINE = re.compile(r"^- \*\*(.+?):\*\*\s*(.+)$", re.MULTILINE)
ID_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*-\d{3}\b")
REVIEW_STATUS = re.compile(r"^\*\*Review status:\*\*\s*(complete|provisional)\s*$", re.MULTILINE)
CORE_STATUS = re.compile(r"^\*\*Core workflows fully exercised:\*\*\s*(yes|no)\s*$", re.MULTILINE)


def read_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read findings.json: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append("findings.json must contain an object")
        return None
    return value


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    visited: set[str] = set()
    active: list[str] = []

    def walk(node: str) -> list[str] | None:
        if node in active:
            start = active.index(node)
            return active[start:] + [node]
        if node in visited:
            return None
        active.append(node)
        for dependency in graph.get(node, []):
            cycle = walk(dependency)
            if cycle:
                return cycle
        active.pop()
        visited.add(node)
        return None

    for node in graph:
        cycle = walk(node)
        if cycle:
            return cycle
    return None


def validate_json(data: dict[str, Any], errors: list[str]) -> dict[str, dict[str, Any]]:
    missing_top = sorted(TOP_LEVEL - set(data))
    extra_top = sorted(set(data) - TOP_LEVEL)
    if missing_top:
        errors.append(f"findings.json missing top-level keys: {', '.join(missing_top)}")
    if extra_top:
        errors.append(f"findings.json has unexpected top-level keys: {', '.join(extra_top)}")
    if data.get("schema_version") != 1:
        errors.append("findings.json schema_version must be 1")
    if data.get("review_status") not in {"complete", "provisional"}:
        errors.append("findings.json review_status must be complete or provisional")

    findings = data.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("findings.json findings must be a non-empty array")
        return {}

    indexed: dict[str, dict[str, Any]] = {}
    required = {"id", "title", *FIELDS}
    for position, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"finding {position} must be an object")
            continue
        finding_id = finding.get("id")
        label = finding_id if isinstance(finding_id, str) else f"finding {position}"
        missing = sorted(required - set(finding))
        extra = sorted(set(finding) - required)
        if missing:
            errors.append(f"{label} missing JSON keys: {', '.join(missing)}")
        if extra:
            errors.append(f"{label} has unexpected JSON keys: {', '.join(extra)}")
        if not isinstance(finding_id, str) or not ID_TOKEN.fullmatch(finding_id):
            errors.append(f"{label} has invalid id")
            continue
        if finding_id in indexed:
            errors.append(f"duplicate finding ID in JSON: {finding_id}")
            continue
        indexed[finding_id] = finding

        for field, allowed in CONTROLLED.items():
            if finding.get(field) not in allowed:
                errors.append(f"{finding_id} has invalid {field}: {finding.get(field)!r}")
        for field in ARRAY_FIELDS:
            if not isinstance(finding.get(field), list):
                errors.append(f"{finding_id} {field} must be an array")
        for field in ("dependencies", "dependents", "conflicts"):
            values = finding.get(field)
            if not isinstance(values, list):
                continue
            if any(not isinstance(value, str) or not ID_TOKEN.fullmatch(value) for value in values):
                errors.append(f"{finding_id} {field} must contain only finding ID strings")
        evidence = finding.get("evidence")
        if isinstance(evidence, list):
            for evidence_index, item in enumerate(evidence, start=1):
                if not isinstance(item, dict) or set(item) != {"kind", "source", "location", "claim"}:
                    errors.append(f"{finding_id} evidence item {evidence_index} has invalid shape")
        for field in required - ARRAY_FIELDS - {"id"}:
            value = finding.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{finding_id} {field} must be a non-empty string")

    ids = set(indexed)
    for finding_id, finding in indexed.items():
        for field in ("dependencies", "dependents", "conflicts"):
            values = finding.get(field)
            if not isinstance(values, list):
                continue
            for related in values:
                if not isinstance(related, str) or not ID_TOKEN.fullmatch(related):
                    continue
                if related not in ids:
                    errors.append(f"{finding_id} {field} references unknown ID: {related}")
                if related == finding_id:
                    errors.append(f"{finding_id} cannot reference itself in {field}")

    for finding_id, finding in indexed.items():
        dependencies = [
            value for value in finding.get("dependencies", [])
            if isinstance(value, str) and ID_TOKEN.fullmatch(value)
        ]
        dependents = [
            value for value in finding.get("dependents", [])
            if isinstance(value, str) and ID_TOKEN.fullmatch(value)
        ]
        for dependency in dependencies:
            if finding_id not in indexed.get(dependency, {}).get("dependents", []):
                errors.append(f"{finding_id} depends on {dependency}, but reverse dependent link is missing")
        for dependent in dependents:
            if finding_id not in indexed.get(dependent, {}).get("dependencies", []):
                errors.append(f"{finding_id} names {dependent} as dependent, but reverse dependency is missing")

    graph = {
        finding_id: [
            value for value in finding.get("dependencies", [])
            if isinstance(value, str) and ID_TOKEN.fullmatch(value)
        ]
        for finding_id, finding in indexed.items()
    }
    cycle = find_cycle(graph)
    if cycle:
        errors.append(f"dependency cycle: {' -> '.join(cycle)}")
    return indexed


def parse_markdown_register(register: str, errors: list[str]) -> dict[str, dict[str, str]]:
    matches = list(FINDING_HEADING.finditer(register))
    parsed: dict[str, dict[str, str]] = {}
    for index, match in enumerate(matches):
        finding_id, title = match.groups()
        if finding_id in parsed:
            errors.append(f"duplicate finding ID in Markdown: {finding_id}")
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(register)
        fields = dict(FIELD_LINE.findall(register[match.end():end]))
        missing = [label for label in MARKDOWN_LABELS.values() if label not in fields]
        if missing:
            errors.append(f"{finding_id} missing Markdown fields: {', '.join(missing)}")
        parsed[finding_id] = {"title": title, **fields}
    if not parsed:
        errors.append("findings register contains no valid finding headings")
    return parsed


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}
    for name in REQUIRED_FILES:
        path = root / name
        if not path.is_file():
            errors.append(f"missing required file: {name}")
        elif name.endswith(".md"):
            texts[name] = path.read_text(encoding="utf-8")
    if errors:
        return errors

    data = read_json(root / "findings.json", errors)
    json_findings = validate_json(data, errors) if data is not None else {}
    markdown_findings = parse_markdown_register(texts["05-findings-register.md"], errors)

    if set(json_findings) != set(markdown_findings):
        errors.append("Markdown and JSON finding ID sets differ")
    for finding_id in set(json_findings) & set(markdown_findings):
        json_finding = json_findings[finding_id]
        md_finding = markdown_findings[finding_id]
        if json_finding.get("title") != md_finding.get("title"):
            errors.append(f"{finding_id} title differs between Markdown and JSON")
        for field in CONTROLLED:
            label = MARKDOWN_LABELS[field]
            if json_finding.get(field) != md_finding.get(label):
                errors.append(f"{finding_id} {field} differs between Markdown and JSON")
        for field in ("dependencies", "dependents", "conflicts"):
            label = MARKDOWN_LABELS[field]
            markdown_value = md_finding.get(label, "")
            markdown_ids = (
                set()
                if markdown_value.strip().lower() == "none"
                else {value.strip() for value in markdown_value.split(",") if value.strip()}
            )
            json_ids = {
                value for value in json_finding.get(field, [])
                if isinstance(value, str) and ID_TOKEN.fullmatch(value)
            }
            if json_ids != markdown_ids:
                errors.append(f"{finding_id} {field} differs between Markdown and JSON")

    executive = texts["00-executive-verdict.md"]
    coverage = texts["07-review-coverage.md"]
    executive_status = REVIEW_STATUS.search(executive)
    coverage_status = REVIEW_STATUS.search(coverage)
    core_status = CORE_STATUS.search(coverage)
    if not executive_status:
        errors.append("executive verdict is missing an exact Review status line")
    if not coverage_status:
        errors.append("review coverage is missing an exact Review status line")
    if not core_status:
        errors.append("review coverage is missing an exact Core workflows fully exercised line")
    statuses = [match.group(1) for match in (executive_status, coverage_status) if match]
    if data and isinstance(data.get("review_status"), str):
        statuses.append(data["review_status"])
    if len(set(statuses)) > 1:
        errors.append("review status differs across executive verdict, coverage, and JSON")
    if core_status and core_status.group(1) == "no" and "complete" in statuses:
        errors.append("review must be provisional when core workflows were not fully exercised")

    sequence = texts["06-implementation-sequence.md"]
    ledger_match = re.search(r"^## Coverage ledger\s*$([\s\S]*)", sequence, re.MULTILINE)
    if not ledger_match:
        errors.append("implementation sequence is missing a Coverage ledger section")
    else:
        ledger_ids = ID_TOKEN.findall(ledger_match.group(1))
        counts = Counter(ledger_ids)
        ids = set(json_findings)
        missing = sorted(ids - set(ledger_ids))
        unknown = sorted(set(ledger_ids) - ids)
        repeated = sorted(item for item, count in counts.items() if count != 1)
        if missing:
            errors.append(f"findings missing from coverage ledger: {', '.join(missing)}")
        if unknown:
            errors.append(f"unknown IDs in coverage ledger: {', '.join(unknown)}")
        if repeated:
            errors.append(f"finding IDs repeated in coverage ledger: {', '.join(repeated)}")
        order = {finding_id: index for index, finding_id in enumerate(ledger_ids)}
        for finding_id, finding in json_findings.items():
            for dependency in finding.get("dependencies", []):
                if not isinstance(dependency, str) or not ID_TOKEN.fullmatch(dependency):
                    continue
                if dependency in order and finding_id in order and order[dependency] > order[finding_id]:
                    errors.append(f"coverage ledger places {finding_id} before dependency {dependency}")

    surface_match = re.search(r"^## Surface coverage\s*$([\s\S]*?)(?=^## |\Z)", coverage, re.MULTILINE)
    if not surface_match:
        errors.append("review coverage is missing Surface coverage")
    else:
        rows: list[list[str]] = []
        for line in surface_match.group(1).splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                continue
            rows.append(cells)
        header = ["surface", "importance", "status", "evidence", "limitations", "next step"]
        if not rows or [cell.lower() for cell in rows[0]] != header:
            errors.append("Surface coverage table has an invalid or missing header")
        for row_index, row in enumerate(rows[1:], start=1):
            if len(row) != 6:
                errors.append(f"Surface coverage row {row_index} must contain six columns")
            elif row[2] not in COVERAGE_STATUSES:
                errors.append(f"Surface coverage row {row_index} has invalid status: {row[2]!r}")

    for heading in ("Narrative reconciliation", "Validator result"):
        if heading not in coverage:
            errors.append(f"review coverage is missing {heading}")
    return errors


def fixture_finding() -> dict[str, Any]:
    finding: dict[str, Any] = {
        "id": "TEST-001", "title": "Fixture", "type": "strength", "category": "test",
        "severity": "informational", "confidence": "confirmed", "status": "accepted-risk",
        "impact": "Validates the validator.", "evidence": [],
        "expected_behavior": "Validator passes.", "actual_behavior": "Validator passes.",
        "root_cause": "Self-test fixture.", "affected_components": ["validator"],
        "recommendation": "Retain.", "if_implemented": "Already present.",
        "if_unchanged": "Self-test remains valid.", "dependencies": [], "dependents": [],
        "conflicts": [], "acceptance_criteria": ["Self-test passes."],
        "verification": "Run --self-test.", "estimated_scope": "trivial",
        "regression_risk": "low", "action": "retain", "strategic_classification": [],
    }
    return finding


def self_test() -> int:
    finding = fixture_finding()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        for name in REQUIRED_FILES:
            if name.endswith(".md"):
                (root / name).write_text(f"# {name}\n", encoding="utf-8")
        (root / "00-executive-verdict.md").write_text("# Verdict\n\n**Review status:** complete\n", encoding="utf-8")
        lines = ["# Findings", "", "## TEST-001 — Fixture", ""]
        for field in FIELDS:
            label = MARKDOWN_LABELS[field]
            value = finding[field]
            rendered = ", ".join(value) if isinstance(value, list) else value
            rendered = rendered or "None"
            lines.append(f"- **{label}:** {rendered}")
        (root / "05-findings-register.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        (root / "06-implementation-sequence.md").write_text("# Sequence\n\n## Coverage ledger\n\n- TEST-001\n", encoding="utf-8")
        (root / "07-review-coverage.md").write_text(
            "# Coverage\n\n**Review status:** complete\n\n**Core workflows fully exercised:** yes\n\n"
            "## Surface coverage\n\n| Surface | Importance | Status | Evidence | Limitations | Next step |\n"
            "|---|---|---|---|---|---|\n| Core | defining | passed | fixture | None | None |\n\n"
            "## Narrative reconciliation\n\nNone.\n\n## Validator result\n\nPending.\n",
            encoding="utf-8",
        )
        data = {
            "schema_version": 1, "project": "fixture", "audited_revision": "fixture",
            "review_status": "complete", "generated_at": "2026-01-01T00:00:00Z",
            "findings": [finding],
        }
        (root / "findings.json").write_text(json.dumps(data), encoding="utf-8")
        errors = validate(root)
        if errors:
            print("Self-test failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
    malformed = fixture_finding()
    malformed["dependencies"] = [{}]
    malformed["dependents"] = [[]]
    malformed["conflicts"] = [1]
    malformed_errors: list[str] = []
    validate_json(
        {
            "schema_version": 1,
            "project": "fixture",
            "audited_revision": "fixture",
            "review_status": "complete",
            "generated_at": "2026-01-01T00:00:00Z",
            "findings": [malformed],
        },
        malformed_errors,
    )
    if sum("must contain only finding ID strings" in error for error in malformed_errors) != 3:
        print("Self-test failed: malformed relationship values were not rejected", file=sys.stderr)
        return 1
    print("Self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
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
