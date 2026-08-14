#!/usr/bin/env python3
"""Validate a planning-only project-revision document against a teardown."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from validation_common import (
    ID_PATTERN,
    canonical_digest,
    load_object,
    marker,
    markdown_section,
    parse_labeled_fields,
    read_text,
    split_pipe,
)

REQUIRED_SECTIONS = (
    "Purpose and boundary",
    "Current-state revalidation",
    "Delta from the original teardown",
    "Owner decisions required",
    "Proposed implementation sequence",
    "Traceability ledger",
    "Blockers and completion gates",
    "What was not done",
)
REQUIRED_FIELDS = (
    "Teardown status",
    "Teardown verification state",
    "Revalidation",
    "Plan treatment",
    "Dependencies",
    "Owner decision",
    "Blocker or completion gate",
    "Acceptance criteria carried forward",
    "Verification carried forward",
    "Affected surfaces carried forward",
    "Plan action",
    "Notes",
    "Teardown record digest",
)
REVALIDATIONS = {"confirmed", "changed", "stale", "already-resolved", "not-applicable", "blocked"}
TREATMENTS = {
    "implement", "owner-decision", "investigate", "blocker", "defer",
    "accepted-risk", "retain", "no-action",
}
TRACE_HEADING = re.compile(r"^### ([A-Z][A-Z0-9]*-\d{3}) — (.+)$", re.MULTILINE)
PROHIBITED_MARKERS = (
    "Revision status", "Implementation endpoint", "Artifact relationship",
    "Review convergence", "Merge readiness", "Release readiness", "Committed",
    "Pushed", "Pull request updated", "Merged",
)


def teardown_index(teardown: dict[str, Any], errors: list[str]) -> dict[str, dict[str, Any]]:
    findings = teardown.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("teardown findings must be a non-empty array")
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for position, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"teardown finding {position} must be an object")
            continue
        finding_id = finding.get("id")
        if not isinstance(finding_id, str) or not ID_PATTERN.fullmatch(finding_id):
            errors.append(f"teardown finding {position} has an invalid id")
            continue
        if finding_id in indexed:
            errors.append(f"teardown contains duplicate finding: {finding_id}")
            continue
        indexed[finding_id] = finding
    return indexed


def parse_traceability(text: str, errors: list[str]) -> dict[str, dict[str, str]]:
    section = markdown_section(text, "Traceability ledger")
    if section is None:
        return {}
    matches = list(TRACE_HEADING.finditer(section))
    records: dict[str, dict[str, str]] = {}
    counts = Counter(match.group(1) for match in matches)
    for finding_id, count in sorted(counts.items()):
        if count != 1:
            errors.append(f"traceability ledger repeats finding: {finding_id}")
    for index, match in enumerate(matches):
        finding_id = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        body = section[match.end():end]
        fields = parse_labeled_fields(body)
        fields["__title__"] = match.group(2).strip()
        missing = [field for field in REQUIRED_FIELDS if field not in fields]
        extra = sorted(set(fields) - set(REQUIRED_FIELDS) - {"__title__"})
        if missing:
            errors.append(f"{finding_id} traceability section missing fields: {', '.join(missing)}")
        if extra:
            errors.append(f"{finding_id} traceability section has unexpected fields: {', '.join(extra)}")
        records[finding_id] = fields
    return records


def validate(teardown_root: Path, planning_document: Path) -> list[str]:
    errors: list[str] = []
    teardown_path = teardown_root / "findings.json"
    if not teardown_path.is_file():
        return ["teardown is missing findings.json"]
    if not planning_document.is_file():
        return ["planning document does not exist"]

    teardown = load_object(teardown_path, "teardown findings.json", errors)
    text = read_text(planning_document, "planning document", errors)
    if teardown is None:
        return errors
    if teardown.get("schema_version") not in {1, 2, 3}:
        errors.append("teardown findings.json schema_version must be 1, 2, or 3")
    findings = teardown_index(teardown, errors)

    expected_markers = {
        "Artifact mode": "planning-only",
        "Product edits performed": "no",
        "Convergence testing performed": "no",
        "Teardown review status": teardown.get("review_status"),
        "Teardown finding count": str(len(findings)),
    }
    for label, expected in expected_markers.items():
        value = marker(text, label, errors)
        if value is not None and expected is not None and value != expected:
            errors.append(f"planning marker {label} differs from the teardown or planning-only contract")
    current_revision = marker(text, "Current revision checked", errors)
    if current_revision is not None and not current_revision.strip():
        errors.append("Current revision checked must be non-empty")

    for heading in REQUIRED_SECTIONS:
        if markdown_section(text, heading) is None:
            errors.append(f"planning document is missing required section: ## {heading}")

    for label in PROHIBITED_MARKERS:
        if re.search(rf"^\*\*{re.escape(label)}:\*\*", text, re.MULTILINE):
            errors.append(f"planning-only document contains implementation handoff marker: **{label}:**")

    records = parse_traceability(text, errors)
    expected_ids = set(findings)
    actual_ids = set(records)
    if expected_ids - actual_ids:
        errors.append(f"traceability ledger missing findings: {', '.join(sorted(expected_ids - actual_ids))}")
    if actual_ids - expected_ids:
        errors.append(f"traceability ledger has unknown findings: {', '.join(sorted(actual_ids - expected_ids))}")

    for finding_id in sorted(expected_ids & actual_ids):
        original = findings[finding_id]
        fields = records[finding_id]
        title = original.get("title")
        if fields.get("__title__") != title:
            errors.append(f"{finding_id} title does not match the teardown")
        if fields.get("Teardown status") != original.get("status"):
            errors.append(f"{finding_id} teardown status does not match findings.json")
        expected_verification_state = original.get("verification_state", "legacy-not-recorded")
        if fields.get("Teardown verification state") != expected_verification_state:
            errors.append(f"{finding_id} teardown verification state does not match findings.json")

        revalidation = fields.get("Revalidation")
        treatment = fields.get("Plan treatment")
        if revalidation not in REVALIDATIONS:
            errors.append(f"{finding_id} has invalid Revalidation: {revalidation!r}")
        if treatment not in TREATMENTS:
            errors.append(f"{finding_id} has invalid Plan treatment: {treatment!r}")

        expected_dependencies = original.get("dependencies", [])
        actual_dependencies = split_pipe(fields.get("Dependencies", ""))
        if actual_dependencies != expected_dependencies:
            errors.append(f"{finding_id} dependencies do not exactly match the teardown")
        expected_criteria = original.get("acceptance_criteria", [])
        actual_criteria = split_pipe(fields.get("Acceptance criteria carried forward", ""))
        if actual_criteria != expected_criteria:
            errors.append(f"{finding_id} acceptance criteria do not exactly match the teardown")
        expected_verification = original.get("verification", "")
        if fields.get("Verification carried forward") != expected_verification:
            errors.append(f"{finding_id} verification does not exactly match the teardown")
        expected_surfaces = original.get("affected_components", [])
        actual_surfaces = split_pipe(fields.get("Affected surfaces carried forward", ""))
        if actual_surfaces != expected_surfaces:
            errors.append(f"{finding_id} affected surfaces do not exactly match the teardown")
        if fields.get("Teardown record digest") != canonical_digest(original):
            errors.append(f"{finding_id} teardown record digest does not match findings.json")

        owner_decision = fields.get("Owner decision", "")
        blocker = fields.get("Blocker or completion gate", "")
        plan_action = fields.get("Plan action", "")
        if not plan_action or plan_action == "None":
            errors.append(f"{finding_id} must have a concrete Plan action")
        if revalidation == "blocked" and blocker in {"", "None"}:
            errors.append(f"{finding_id} blocked revalidation requires a specific blocker or completion gate")
        if treatment == "owner-decision" and owner_decision in {"", "None"}:
            errors.append(f"{finding_id} owner-decision treatment requires the unresolved decision")
        if treatment == "blocker" and blocker in {"", "None"}:
            errors.append(f"{finding_id} blocker treatment requires a specific blocker or completion gate")
        if treatment == "no-action" and revalidation not in {"stale", "already-resolved", "not-applicable"}:
            errors.append(f"{finding_id} no-action is only valid for stale, already-resolved, or not-applicable findings")
        if original.get("type") == "strength" or original.get("action") == "retain":
            if treatment != "retain":
                errors.append(f"{finding_id} is a retained strength and must use Plan treatment retain")
        if original.get("status") == "decision-required" and treatment != "owner-decision":
            if owner_decision in {"", "None"} and revalidation not in {"stale", "already-resolved", "not-applicable"}:
                errors.append(f"{finding_id} still requires an owner decision")
        if original.get("status") == "blocked" and treatment not in {"blocker", "investigate", "no-action"}:
            errors.append(f"{finding_id} original blocked status must remain an explicit blocker or investigation")

    delta = markdown_section(text, "Delta from the original teardown") or ""
    delta_subsections = (
        "Teardown recommendations translated or reorganized",
        "New implementation or sequencing recommendations",
        "Genuinely new findings from current-state revalidation",
    )
    for heading in delta_subsections:
        if not re.search(rf"^### {re.escape(heading)}\s*$", delta, re.MULTILINE):
            errors.append(f"Delta section is missing required subsection: ### {heading}")
    new_section_match = re.search(
        r"^### Genuinely new findings from current-state revalidation\s*$([\s\S]*?)(?=^### |\Z)",
        delta,
        re.MULTILINE,
    )
    if new_section_match:
        new_body = new_section_match.group(1)
        if "No genuinely new findings were discovered." not in new_body:
            referenced = set(re.findall(r"\b[A-Z][A-Z0-9]*-\d{3}\b", new_body))
            if not (referenced - expected_ids):
                errors.append(
                    "new-findings delta must state the exact no-new-findings sentence or identify a genuinely new finding ID"
                )

    not_done = markdown_section(text, "What was not done") or ""
    required_statements = (
        "No product code, tests, configuration, manifests, deployment files, or operational content were edited.",
        "No implementation convergence testing was performed.",
    )
    for statement in required_statements:
        if statement not in not_done:
            errors.append(f"What was not done must include: {statement}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown_directory", type=Path)
    parser.add_argument("planning_document", type=Path)
    args = parser.parse_args()
    errors = validate(args.teardown_directory.resolve(), args.planning_document.resolve())
    if errors:
        print("Project revision plan validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Project revision plan validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
