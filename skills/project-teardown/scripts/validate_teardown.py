#!/usr/bin/env python3
"""Validate a project-teardown handoff and its cross-file integrity."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from finding_model import (
    FIELDS,
    LEGACY_FIELDS,
    MARKDOWN_LABELS,
    canonical_finding_digest,
    render_findings_register,
    render_readme,
)


BASE_REQUIRED_FILES = (
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

SCHEMA_THREE_FILES = ("README.md", "08-claims-inventory.md")

CONTROLLED = {
    "type": {"defect", "shortcoming", "recommendation", "opportunity", "investigation", "strength"},
    "severity": {"critical", "high", "medium", "low", "informational"},
    "confidence": {"confirmed", "high", "medium", "low"},
    "verification_state": {
        "behaviorally-verified", "defect-conclusively-demonstrated",
        "operationally-unverified", "partially-verified", "source-only",
        "research-verified", "owner-provided", "blocked", "not-applicable",
    },
    "estimated_scope": {"trivial", "small", "medium", "large", "initiative"},
    "regression_risk": {"low", "medium", "high"},
    "action": {"fix", "add", "change", "remove", "investigate", "decide", "retain"},
}
STATUS_BY_SCHEMA = {
    1: {"open", "blocked", "decision-required", "accepted-risk"},
    2: {"open", "blocked", "decision-required", "accepted-risk", "retained"},
    3: {"open", "blocked", "decision-required", "accepted-risk", "retained"},
}
ARRAY_FIELDS = {
    "evidence", "affected_components", "dependencies", "dependents", "conflicts",
    "acceptance_criteria", "strategic_classification",
}
STRING_ARRAY_FIELDS = ARRAY_FIELDS - {"evidence"}
SCALAR_FIELDS = set(FIELDS) - ARRAY_FIELDS
LEGACY_SCALAR_FIELDS = set(LEGACY_FIELDS) - ARRAY_FIELDS
TOP_LEVEL_BY_SCHEMA = {
    1: {"schema_version", "project", "audited_revision", "review_status", "generated_at", "findings"},
    2: {
        "schema_version", "project", "audited_revision", "review_status",
        "core_workflows_fully_exercised", "generated_at", "findings",
    },
    3: {
        "schema_version", "project", "audited_revision", "review_status",
        "core_workflows_fully_exercised", "generated_at", "findings",
    },
}
COVERAGE_STATUSES = {"passed", "failed", "partial", "blocked", "not-tested", "not-applicable"}
COVERAGE_IMPORTANCE = {"defining", "required", "major", "supporting", "research"}
EVIDENCE_LEVELS = {
    "behavioral", "test", "build-only", "source-only", "research",
    "owner-provided", "mixed", "none",
}
RECONCILIATION_CLASSIFICATIONS = {"actionable", "passed-check", "limitation", "deferred", "context", "mixed"}
WORKFLOW_VERIFICATION = {
    "behaviorally-verified", "defect-conclusively-demonstrated",
    "operationally-unverified", "partially-verified", "source-only",
    "research-verified", "owner-provided", "blocked", "not-applicable",
}
CLAIM_CATEGORIES = {
    "credential", "licensing", "insurance", "safety", "diagnosis", "expertise",
    "guarantee", "pricing", "performance", "statistics", "privacy", "capability", "other",
}
CLAIM_STATES = {"verified", "unsupported", "contradicted", "partially-verified", "blocked", "not-applicable"}
CLAIM_DISPOSITIONS = {"retain", "qualify", "remove", "replace", "investigate", "owner-decision", "not-applicable"}
FINDING_HEADING = re.compile(r"^## ([A-Z][A-Z0-9]*-\d{3}) — (.+)$", re.MULTILINE)
FIELD_LINE = re.compile(r"^- \*\*(.+?):\*\*\s*(.+)$", re.MULTILINE)
ID_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*-\d{3}\b")
REVIEW_STATUS = re.compile(r"^\*\*Review status:\*\*\s*(complete|provisional)\s*$", re.MULTILINE)
CORE_STATUS = re.compile(r"^\*\*Core workflows fully exercised:\*\*\s*(yes|no)\s*$", re.MULTILINE)
VALIDATOR_STATUS = re.compile(r"^\*\*Validator status:\*\*\s*(passed|pending|failed)\s*$", re.MULTILINE)
TOTAL_FINDINGS = re.compile(r"^\*\*Total findings:\*\*\s*(\d+)\s*$", re.MULTILINE)
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def read_text(path: Path, label: str, errors: list[str]) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read {label}: {exc}")
        return ""
    if not text.strip():
        errors.append(f"{label} is empty")
    elif not re.search(r"^#\s+\S", text, re.MULTILINE):
        errors.append(f"{label} is missing a top-level Markdown heading")
    return text


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


def require_nonempty_string(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return False
    return True


def validate_timestamp(value: Any, label: str, errors: list[str]) -> None:
    if not require_nonempty_string(value, label, errors):
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp")
        return
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone")


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


def validate_string_array(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be an array")
        return []
    cleaned: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label} item {index} must be a non-empty string")
            continue
        cleaned.append(item)
    duplicates = sorted(item for item, count in Counter(cleaned).items() if count > 1)
    if duplicates:
        errors.append(f"{label} contains duplicates: {', '.join(duplicates)}")
    return cleaned


def validate_json(data: dict[str, Any], errors: list[str]) -> tuple[int | None, dict[str, dict[str, Any]]]:
    schema_version = data.get("schema_version")
    if schema_version not in TOP_LEVEL_BY_SCHEMA:
        errors.append("findings.json schema_version must be 1, 2, or 3")
        return None, {}

    expected_top = TOP_LEVEL_BY_SCHEMA[schema_version]
    missing_top = sorted(expected_top - set(data))
    extra_top = sorted(set(data) - expected_top)
    if missing_top:
        errors.append(f"findings.json missing top-level keys: {', '.join(missing_top)}")
    if extra_top:
        errors.append(f"findings.json has unexpected top-level keys: {', '.join(extra_top)}")

    require_nonempty_string(data.get("project"), "findings.json project", errors)
    require_nonempty_string(data.get("audited_revision"), "findings.json audited_revision", errors)
    validate_timestamp(data.get("generated_at"), "findings.json generated_at", errors)
    if data.get("review_status") not in {"complete", "provisional"}:
        errors.append("findings.json review_status must be complete or provisional")
    if schema_version in {2, 3} and not isinstance(data.get("core_workflows_fully_exercised"), bool):
        errors.append("findings.json core_workflows_fully_exercised must be a boolean")

    findings = data.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("findings.json findings must be a non-empty array")
        return schema_version, {}

    indexed: dict[str, dict[str, Any]] = {}
    finding_fields = FIELDS if schema_version == 3 else LEGACY_FIELDS
    required = {"id", "title", *finding_fields}
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

        require_nonempty_string(finding.get("title"), f"{finding_id} title", errors)
        for field, allowed in CONTROLLED.items():
            if field not in finding_fields:
                continue
            if finding.get(field) not in allowed:
                errors.append(f"{finding_id} has invalid {field}: {finding.get(field)!r}")
        if finding.get("status") not in STATUS_BY_SCHEMA[schema_version]:
            errors.append(f"{finding_id} has invalid status: {finding.get('status')!r}")

        scalar_fields = SCALAR_FIELDS if schema_version == 3 else LEGACY_SCALAR_FIELDS
        for field in scalar_fields - set(CONTROLLED) - {"status"}:
            require_nonempty_string(finding.get(field), f"{finding_id} {field}", errors)

        for field in STRING_ARRAY_FIELDS:
            validate_string_array(finding.get(field), f"{finding_id} {field}", errors)

        evidence = finding.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{finding_id} evidence must be an array")
        else:
            for evidence_index, item in enumerate(evidence, start=1):
                if not isinstance(item, dict) or set(item) != {"kind", "source", "location", "claim"}:
                    errors.append(f"{finding_id} evidence item {evidence_index} has invalid shape")
                    continue
                for key in ("kind", "source", "location", "claim"):
                    require_nonempty_string(item.get(key), f"{finding_id} evidence item {evidence_index} {key}", errors)

        finding_type = finding.get("type")
        status = finding.get("status")
        action = finding.get("action")
        severity = finding.get("severity")
        confidence = finding.get("confidence")
        if schema_version in {2, 3}:
            if finding_type == "strength":
                if severity != "informational" or status != "retained" or action != "retain":
                    errors.append(f"{finding_id} strength requires informational severity, retained status, and retain action")
            if status == "retained" and not (finding_type == "strength" or action == "retain"):
                errors.append(f"{finding_id} retained status requires a strength or retain action")
        if (status == "decision-required") != (action == "decide"):
            errors.append(f"{finding_id} decision-required status and decide action must occur together")
        if confidence == "confirmed" and isinstance(evidence, list) and not evidence:
            errors.append(f"{finding_id} confirmed confidence requires evidence")
        if severity == "critical":
            if confidence not in {"confirmed", "high"}:
                errors.append(f"{finding_id} critical severity requires confirmed or high confidence")
            if isinstance(evidence, list) and not evidence:
                errors.append(f"{finding_id} critical severity requires evidence")

    ids = set(indexed)
    for finding_id, finding in indexed.items():
        for field in ("dependencies", "dependents", "conflicts"):
            values = finding.get(field)
            if not isinstance(values, list):
                continue
            for related in values:
                if not isinstance(related, str):
                    continue
                if related not in ids:
                    errors.append(f"{finding_id} {field} references unknown ID: {related}")
                if related == finding_id:
                    errors.append(f"{finding_id} cannot reference itself in {field}")

    for finding_id, finding in indexed.items():
        for dependency in finding.get("dependencies", []):
            if dependency in indexed and finding_id not in indexed[dependency].get("dependents", []):
                errors.append(f"{finding_id} depends on {dependency}, but reverse dependent link is missing")
        for dependent in finding.get("dependents", []):
            if dependent in indexed and finding_id not in indexed[dependent].get("dependencies", []):
                errors.append(f"{finding_id} names {dependent} as dependent, but reverse dependency is missing")
        for conflict in finding.get("conflicts", []):
            if conflict in indexed and finding_id not in indexed[conflict].get("conflicts", []):
                errors.append(f"{finding_id} conflicts with {conflict}, but reverse conflict link is missing")

    graph = {finding_id: finding.get("dependencies", []) for finding_id, finding in indexed.items()}
    cycle = find_cycle(graph)
    if cycle:
        errors.append(f"dependency cycle: {' -> '.join(cycle)}")
    return schema_version, indexed


def parse_markdown_register(register: str, errors: list[str], schema_version: int | None = None) -> dict[str, dict[str, str]]:
    matches = list(FINDING_HEADING.finditer(register))
    parsed: dict[str, dict[str, str]] = {}
    fields = FIELDS if schema_version == 3 else LEGACY_FIELDS
    required_labels = [*(MARKDOWN_LABELS[field] for field in fields), "JSON record digest"]
    for index, match in enumerate(matches):
        finding_id, title = match.groups()
        if finding_id in parsed:
            errors.append(f"duplicate finding ID in Markdown: {finding_id}")
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(register)
        section = register[match.end():end]
        pairs = FIELD_LINE.findall(section)
        counts = Counter(label for label, _ in pairs)
        repeated = sorted(label for label, count in counts.items() if count > 1)
        if repeated:
            errors.append(f"{finding_id} repeats Markdown fields: {', '.join(repeated)}")
        parsed_fields = dict(pairs)
        missing = [label for label in required_labels if label not in parsed_fields]
        if missing:
            errors.append(f"{finding_id} missing Markdown fields: {', '.join(missing)}")
        digest = parsed_fields.get("JSON record digest")
        if digest is not None and not DIGEST_PATTERN.fullmatch(digest):
            errors.append(f"{finding_id} has invalid JSON record digest")
        parsed[finding_id] = {"title": title.strip(), **parsed_fields}
    if not parsed:
        errors.append("findings register contains no valid finding headings")
    return parsed


def parse_table(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def section_after_heading(text: str, heading: str) -> str | None:
    match = re.search(rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)", text, re.MULTILINE)
    return match.group(1) if match else None


CLAIM_ID = re.compile(r"^CLAIM-\d{3}$")


def validate_claims_inventory(text: str, findings: dict[str, dict[str, Any]], errors: list[str]) -> None:
    section = section_after_heading(text, "Claims")
    if section is None:
        errors.append("claims inventory is missing exact section: ## Claims")
        return
    rows = parse_table(section)
    header = [
        "claim id", "claim text", "location", "category", "required evidence",
        "evidence found", "verification state", "disposition", "related finding ids",
        "required action",
    ]
    if not rows or [cell.lower() for cell in rows[0]] != header:
        errors.append("Claims inventory table has an invalid or missing header")
        return
    claim_ids: list[str] = []
    for row_index, row in enumerate(rows[1:], start=1):
        if len(row) != 10:
            errors.append(f"Claims inventory row {row_index} must contain ten columns")
            continue
        claim_id, claim_text, location, category, required_evidence, evidence_found, state, disposition, ids_cell, action = row
        if not CLAIM_ID.fullmatch(claim_id):
            errors.append(f"Claims inventory row {row_index} has invalid claim ID: {claim_id!r}")
        else:
            claim_ids.append(claim_id)
        if not claim_text or not location or not required_evidence or not evidence_found or not action:
            errors.append(f"Claims inventory row {row_index} contains an empty required field")
        if category not in CLAIM_CATEGORIES:
            errors.append(f"Claims inventory row {row_index} has invalid category: {category!r}")
        if state not in CLAIM_STATES:
            errors.append(f"Claims inventory row {row_index} has invalid verification state: {state!r}")
        if disposition not in CLAIM_DISPOSITIONS:
            errors.append(f"Claims inventory row {row_index} has invalid disposition: {disposition!r}")
        related = ID_TOKEN.findall(ids_cell)
        unknown = sorted(set(related) - set(findings))
        if unknown:
            errors.append(f"Claims inventory row {row_index} references unknown findings: {', '.join(unknown)}")
        if state in {"unsupported", "contradicted", "partially-verified", "blocked"} and not related:
            errors.append(f"Claims inventory row {row_index} requires a related finding for unresolved claim evidence")
        if disposition == "retain" and state != "verified":
            errors.append(f"Claims inventory row {row_index} may retain a claim only when verified")
        if state == "not-applicable" and disposition != "not-applicable":
            errors.append(f"Claims inventory row {row_index} not-applicable state requires not-applicable disposition")
        if disposition == "not-applicable" and state != "not-applicable":
            errors.append(f"Claims inventory row {row_index} not-applicable disposition requires not-applicable state")
    duplicates = sorted(item for item, count in Counter(claim_ids).items() if count > 1)
    if duplicates:
        errors.append(f"Claims inventory repeats claim IDs: {', '.join(duplicates)}")
    if len(rows) <= 1:
        errors.append("Claims inventory must contain at least one claim row or explicit CLAIM-000 not-applicable row")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return ["teardown root does not exist or is not a directory"]

    findings_path = root / "findings.json"
    if not findings_path.is_file():
        return ["missing required file: findings.json"]
    data = read_json(findings_path, errors)
    schema_version = data.get("schema_version") if isinstance(data, dict) else None
    required_files = list(BASE_REQUIRED_FILES)
    if schema_version == 3:
        required_files.extend(SCHEMA_THREE_FILES)

    texts: dict[str, str] = {}
    for name in required_files:
        path = root / name
        if not path.is_file():
            errors.append(f"missing required file: {name}")
        elif name.endswith(".md"):
            texts[name] = read_text(path, name, errors)
    evidence_dir = root / "evidence"
    if not evidence_dir.is_dir():
        errors.append("missing required directory: evidence")
    if any(error.startswith("missing required") for error in errors):
        return errors

    schema_version, json_findings = validate_json(data, errors) if data is not None else (None, {})

    register_text = texts.get("05-findings-register.md", "")
    if schema_version == 3 and data is not None:
        if register_text != render_findings_register(data):
            errors.append(
                "05-findings-register.md is stale or manually edited; regenerate it from findings.json with render_findings.py"
            )
        readme_text = texts.get("README.md", "")
        if readme_text != render_readme(data):
            errors.append("README.md is stale; regenerate it from findings.json with render_readme.py")
        validate_claims_inventory(texts.get("08-claims-inventory.md", ""), json_findings, errors)
    else:
        parse_error_count = len(errors)
        markdown_findings = parse_markdown_register(register_text, errors, schema_version)
        register_parsed_cleanly = len(errors) == parse_error_count and bool(markdown_findings)
        if register_parsed_cleanly:
            if set(json_findings) != set(markdown_findings):
                errors.append("Markdown and JSON finding ID sets differ")
            for finding_id in set(json_findings) & set(markdown_findings):
                json_finding = json_findings[finding_id]
                md_finding = markdown_findings[finding_id]
                if json_finding.get("title") != md_finding.get("title"):
                    errors.append(f"{finding_id} title differs between Markdown and JSON")
                for field in (set(CONTROLLED) - {"verification_state"}) | {"status"}:
                    label = MARKDOWN_LABELS[field]
                    if json_finding.get(field) != md_finding.get(label):
                        errors.append(f"{finding_id} {field} differs between Markdown and JSON")
                for field in LEGACY_SCALAR_FIELDS - set(CONTROLLED) - {"status"}:
                    label = MARKDOWN_LABELS[field]
                    if json_finding.get(field) != md_finding.get(label):
                        errors.append(f"{finding_id} {field} differs between Markdown and JSON")
                for field in ("dependencies", "dependents", "conflicts"):
                    label = MARKDOWN_LABELS[field]
                    md_ids = ID_TOKEN.findall(md_finding.get(label, ""))
                    if set(md_ids) != set(json_finding.get(field, [])):
                        errors.append(f"{finding_id} {field} differs between Markdown and JSON")
                expected_digest = canonical_finding_digest(json_finding)
                if md_finding.get("JSON record digest") != expected_digest:
                    errors.append(f"{finding_id} JSON record digest does not match findings.json")

    executive = texts.get("00-executive-verdict.md", "")
    coverage = texts.get("07-review-coverage.md", "")
    executive_status = REVIEW_STATUS.search(executive)
    coverage_status = REVIEW_STATUS.search(coverage)
    core_status = CORE_STATUS.search(coverage)
    validator_status = VALIDATOR_STATUS.search(coverage)
    if not executive_status:
        errors.append("executive verdict is missing an exact Review status line")
    if not coverage_status:
        errors.append("review coverage is missing an exact Review status line")
    if not core_status:
        errors.append("review coverage is missing an exact Core workflows fully exercised line")
    if not validator_status:
        errors.append("review coverage is missing an exact Validator status line")
    elif validator_status.group(1) != "passed":
        errors.append("review coverage Validator status must be passed for final delivery")

    statuses = [match.group(1) for match in (executive_status, coverage_status) if match]
    if data and isinstance(data.get("review_status"), str):
        statuses.append(data["review_status"])
    if len(set(statuses)) > 1:
        errors.append("review status differs across executive verdict, coverage, and JSON")
    if core_status:
        core_yes = core_status.group(1) == "yes"
        if schema_version in {2, 3} and data and data.get("core_workflows_fully_exercised") is not core_yes:
            errors.append("core workflow status differs between review coverage and findings.json")
        if not core_yes and "complete" in statuses:
            errors.append("review must be provisional when core workflows were not fully exercised")

    sequence = texts.get("06-implementation-sequence.md", "")
    ledger_section = section_after_heading(sequence, "Coverage ledger")
    if ledger_section is None:
        errors.append("implementation sequence is missing a Coverage ledger section")
    else:
        rows = parse_table(ledger_section)
        expected_header = ["sequence", "finding id", "planned disposition", "prerequisites", "rationale"]
        if not rows or [cell.lower() for cell in rows[0]] != expected_header:
            errors.append("Coverage ledger table has an invalid or missing header")
        ledger_ids: list[str] = []
        sequences: list[int] = []
        for row_index, row in enumerate(rows[1:], start=1):
            if len(row) != 5:
                errors.append(f"Coverage ledger row {row_index} must contain five columns")
                continue
            try:
                sequences.append(int(row[0]))
            except ValueError:
                errors.append(f"Coverage ledger row {row_index} has invalid sequence: {row[0]!r}")
            if not ID_TOKEN.fullmatch(row[1]):
                errors.append(f"Coverage ledger row {row_index} has invalid finding ID: {row[1]!r}")
            else:
                ledger_ids.append(row[1])
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
        if sequences and sequences != list(range(1, len(sequences) + 1)):
            errors.append("Coverage ledger sequences must be contiguous from 1")
        order = {finding_id: index for index, finding_id in enumerate(ledger_ids)}
        for finding_id, finding in json_findings.items():
            for dependency in finding.get("dependencies", []):
                if dependency in order and finding_id in order and order[dependency] > order[finding_id]:
                    errors.append(f"coverage ledger places {finding_id} before dependency {dependency}")

    surface_section = section_after_heading(coverage, "Surface coverage")
    defining_or_required_gap = False
    if surface_section is None:
        errors.append("review coverage is missing Surface coverage")
    else:
        rows = parse_table(surface_section)
        if schema_version == 3:
            header = [
                "surface", "importance", "status", "verification class", "evidence level",
                "evidence", "limitations", "next step",
            ]
            expected_columns = 8
        else:
            header = ["surface", "importance", "status", "evidence level", "evidence", "limitations", "next step"]
            expected_columns = 7
        valid_header = bool(rows) and [cell.lower() for cell in rows[0]] == header
        if not valid_header:
            errors.append("Surface coverage table has an invalid or missing header")
        if valid_header:
            for row_index, row in enumerate(rows[1:], start=1):
                if len(row) != expected_columns:
                    errors.append(f"Surface coverage row {row_index} must contain {expected_columns} columns")
                    continue
                importance, status = row[1], row[2]
                if schema_version == 3:
                    verification_class, evidence_level = row[3], row[4]
                    limitations, next_step = row[6], row[7]
                    if verification_class not in WORKFLOW_VERIFICATION:
                        errors.append(f"Surface coverage row {row_index} has invalid verification class: {verification_class!r}")
                    if status == "blocked" and verification_class != "blocked":
                        errors.append(f"Surface coverage row {row_index} blocked status requires blocked verification class")
                    if status == "not-tested" and verification_class != "operationally-unverified":
                        errors.append(f"Surface coverage row {row_index} not-tested status requires operationally-unverified verification class")
                    if status == "partial" and verification_class not in {"partially-verified", "operationally-unverified", "source-only"}:
                        errors.append(f"Surface coverage row {row_index} partial status has incompatible verification class")
                else:
                    evidence_level = row[3]
                    limitations, next_step = row[5], row[6]
                if importance not in COVERAGE_IMPORTANCE:
                    errors.append(f"Surface coverage row {row_index} has invalid importance: {importance!r}")
                if status not in COVERAGE_STATUSES:
                    errors.append(f"Surface coverage row {row_index} has invalid status: {status!r}")
                if evidence_level not in EVIDENCE_LEVELS:
                    errors.append(f"Surface coverage row {row_index} has invalid evidence level: {evidence_level!r}")
                if importance in {"defining", "required"} and status not in {"passed", "not-applicable"}:
                    defining_or_required_gap = True
                if status in {"partial", "blocked", "not-tested"} and (not limitations or not next_step):
                    errors.append(f"Surface coverage row {row_index} must explain limitations and next step")
    if "complete" in statuses and defining_or_required_gap:
        errors.append("complete review has a defining or required coverage gap")

    reconciliation_section = section_after_heading(coverage, "Narrative reconciliation")
    if reconciliation_section is None:
        errors.append("review coverage is missing Narrative reconciliation")
    else:
        rows = parse_table(reconciliation_section)
        header = ["report section", "classification", "finding ids", "rationale"]
        valid_header = bool(rows) and [cell.lower() for cell in rows[0]] == header
        if not valid_header:
            errors.append("Narrative reconciliation table has an invalid or missing header")
        covered_files: set[str] = set()
        if valid_header:
            for row_index, row in enumerate(rows[1:], start=1):
                if len(row) != 4:
                    errors.append(f"Narrative reconciliation row {row_index} must contain four columns")
                    continue
                report_section, classification, ids_cell, rationale = row
                if classification not in RECONCILIATION_CLASSIFICATIONS:
                    errors.append(f"Narrative reconciliation row {row_index} has invalid classification: {classification!r}")
                row_ids = ID_TOKEN.findall(ids_cell)
                unknown = sorted(set(row_ids) - set(json_findings))
                if unknown:
                    errors.append(f"Narrative reconciliation row {row_index} references unknown IDs: {', '.join(unknown)}")
                if classification in {"actionable", "mixed"} and not row_ids:
                    errors.append(f"Narrative reconciliation row {row_index} is actionable but has no finding IDs")
                if not rationale.strip():
                    errors.append(f"Narrative reconciliation row {row_index} is missing rationale")
                for required_file in BASE_REQUIRED_FILES[1:5]:
                    if required_file in report_section:
                        covered_files.add(required_file)
        missing_files = sorted(set(BASE_REQUIRED_FILES[1:5]) - covered_files)
        if missing_files:
            errors.append(f"Narrative reconciliation missing report files: {', '.join(missing_files)}")

    total_match = TOTAL_FINDINGS.search(coverage)
    if not total_match:
        errors.append("review coverage is missing an exact Total findings line")
    elif int(total_match.group(1)) != len(json_findings):
        errors.append("review coverage Total findings does not match findings.json")

    if "## Validator result" not in coverage:
        errors.append("review coverage is missing Validator result")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown", type=Path)
    parser.add_argument("--verbose", action="store_true", help="print every validation error instead of a bounded summary")
    args = parser.parse_args()
    errors = validate(args.teardown.resolve())
    if errors:
        print(f"Teardown validation failed with {len(errors)} error(s):", file=sys.stderr)
        visible = errors if args.verbose else errors[:20]
        for error in visible:
            print(f"- {error}", file=sys.stderr)
        if not args.verbose and len(errors) > len(visible):
            print(
                f"- ... {len(errors) - len(visible)} additional error(s) suppressed; rerun with --verbose",
                file=sys.stderr,
            )
        return 1
    print("Teardown validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
