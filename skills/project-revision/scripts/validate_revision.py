#!/usr/bin/env python3
"""Validate an implementation-mode project-revision artifact against its teardown."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from render_revision_views import render_implementation_ledger, render_readme
from validation_common import (
    ID_PATTERN,
    canonical_digest,
    exact_keys,
    load_object,
    marker,
    markdown_section,
    parse_labeled_fields,
    read_text,
    require_nonempty_string,
    reject_round_trip_delimiters,
    require_string_list,
    split_pipe,
    validate_timestamp,
)

class ControlledValues(frozenset):
    """A controlled-vocabulary set whose membership test never raises.

    Canonical JSON is untrusted input. ``"x" in ALLOWED`` raises TypeError when
    the candidate is a list or dict, which aborts validation with a traceback
    instead of a bounded error list. An unhashable value is by definition not a
    member of a set of strings, so returning False lets the surrounding check
    report a normal invalid-value error.
    """

    __slots__ = ()

    def __contains__(self, item: object) -> bool:
        try:
            return super().__contains__(item)
        except TypeError:
            return False

REVISION_FILES = (
    "README.md",
    "00-decisions-and-scope.md",
    "01-baseline-and-revalidation.md",
    "02-execution-plan.md",
    "03-implementation-ledger.md",
    "04-verification-and-handoff.md",
    "revision.json",
)
TOP_LEVEL = ControlledValues({
    "schema_version", "project", "teardown_path", "teardown_audited_revision",
    "implementation_start_revision", "implementation_end_revision",
    "revision_status", "generated_at", "existing_work_reconciled", "findings",
    "convergence_findings", "final_state",
})
FINDING_KEYS = ControlledValues({
    "id", "approval", "revalidation", "disposition", "sequence", "reason",
    "files_changed", "acceptance_results", "verification", "notes",
})
CONVERGENCE_KEYS = ControlledValues({
    "id", "title", "source", "severity", "status", "reason",
    "files_changed", "verification",
})
FINAL_STATE_KEYS = ControlledValues({
    "artifact_relationship", "review_convergence", "blocking_convergence_findings",
    "merge_readiness", "release_readiness", "delivery",
})
DELIVERY_KEYS = ControlledValues({"committed", "pushed", "pull_request_updated", "merged"})
APPROVALS = ControlledValues({"approved", "deferred", "rejected", "accepted-risk", "not-applicable"})
REVALIDATIONS = ControlledValues({"confirmed", "changed", "stale", "already-resolved", "not-applicable", "blocked"})
DISPOSITIONS = ControlledValues({
    "implemented", "already-satisfied", "retained", "deferred", "rejected",
    "accepted-risk", "not-applicable", "blocked",
})
ACCEPTANCE_STATUSES = ControlledValues({"passed", "failed", "not-applicable", "blocked"})
CONVERGENCE_SEVERITIES = ControlledValues({"critical", "high", "medium", "low"})
CONVERGENCE_STATUSES = ControlledValues({"fixed", "already-satisfied", "invalid", "open", "deferred", "blocked"})
BLOCKING_SEVERITIES = ControlledValues({"critical", "high", "medium"})
UNRESOLVED_CONVERGENCE = ControlledValues({"open", "deferred", "blocked"})
# Statuses that assert a verified conclusion, so verification must be present.
RESOLVED_CONVERGENCE = ControlledValues({"fixed", "already-satisfied", "invalid"})
# Statuses that assert nothing changed at current head.
NO_CHANGE_CONVERGENCE = ControlledValues({"already-satisfied", "invalid"})
ARTIFACT_RELATIONSHIPS = ControlledValues({"working-tree", "artifact-only-descendant"})
REVIEW_CONVERGENCE = ControlledValues({"passed", "blocked"})
READINESS = ControlledValues({"ready", "not-ready", "not-applicable"})
DELIVERY_VALUES = ControlledValues({"verified", "not-performed", "unverified", "not-applicable"})
REVIEW_COMPLETION = ControlledValues({"completed", "blocked"})
ALLOWED_DISPOSITIONS = {
    "approved": {"implemented", "already-satisfied", "retained", "blocked"},
    "deferred": {"deferred"},
    "rejected": {"rejected"},
    "accepted-risk": {"accepted-risk"},
    "not-applicable": {"not-applicable"},
}
FINDING_HEADING = re.compile(r"^## ([A-Z][A-Z0-9]*-\d{3}) — (.+)$", re.MULTILINE)
CONVERGENCE_HEADING = re.compile(r"^## (REV-\d{3}) — (.+)$", re.MULTILINE)
REQUIRED_LEDGER_FIELDS = (
    "Approval", "Teardown verification state", "Revalidation", "Disposition", "Sequence", "Reason", "Files changed",
    "Acceptance results", "Verification", "Notes", "Revision record digest",
)
REQUIRED_CONVERGENCE_FIELDS = (
    "Source", "Severity", "Status", "Reason", "Files changed", "Verification",
    "Convergence record digest",
)
REQUIRED_SECTIONS = {
    "00-decisions-and-scope.md": (
        "Owner decisions and approval matrix",
        "Constraints and preserved strengths",
        "Blocked evidence and authority boundaries",
    ),
    "01-baseline-and-revalidation.md": (
        "Baseline state",
        "Preservation inventory",
        "Current-state revalidation",
    ),
    "02-execution-plan.md": (
        "Dependency-aware execution plan",
        "Verification plan",
        "Convergence plan",
        "Stop conditions",
    ),
    "04-verification-and-handoff.md": (
        "Verification results",
        "Review-source coverage",
        "Baseline reconciliation",
        "Changed-path attribution",
        "Limitations and blocked evidence",
        "Delivery state",
        "Validator result",
    ),
}
HANDOFF_MARKERS = {
    "revision_status": ("Revision status", {"complete", "partial", "blocked"}),
    "implementation_end_revision": ("Implementation endpoint", None),
    "artifact_relationship": ("Artifact relationship", ARTIFACT_RELATIONSHIPS),
    "review_convergence": ("Review convergence", REVIEW_CONVERGENCE),
    "manual_review": ("Manual adversarial review", REVIEW_COMPLETION),
    "current_head_review": ("Current-head review after final product change", REVIEW_COMPLETION),
    "existing_work_reconciled": ("Existing work reconciled", {"yes", "no"}),
    "blocking_convergence_findings": ("Blocking convergence findings", None),
    "merge_readiness": ("Merge readiness", READINESS),
    "release_readiness": ("Release readiness", READINESS),
    "validator_status": ("Revision validator status", {"passed", "pending", "failed"}),
}
DELIVERY_MARKERS = {
    "committed": "Committed",
    "pushed": "Pushed",
    "pull_request_updated": "Pull request updated",
    "merged": "Merged",
}
ATTRIBUTION_CLASSES = ControlledValues({
    "approved-finding", "convergence-fix", "preserved-existing-work",
    "revision-artifact", "generated-ignored",
})


def index_teardown(teardown: dict[str, Any], errors: list[str]) -> dict[str, dict[str, Any]]:
    if teardown.get("schema_version") not in {1, 2, 3}:
        errors.append("teardown findings.json schema_version must be 1, 2, or 3")
    for key in ("project", "audited_revision"):
        require_nonempty_string(teardown.get(key), f"teardown {key}", errors)
    findings = teardown.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("teardown findings must be a non-empty array")
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for position, item in enumerate(findings, start=1):
        if not isinstance(item, dict):
            errors.append(f"teardown finding {position} must be an object")
            continue
        finding_id = item.get("id")
        if not isinstance(finding_id, str) or not ID_PATTERN.fullmatch(finding_id):
            errors.append(f"teardown finding {position} has an invalid id")
            continue
        if finding_id in indexed:
            errors.append(f"teardown contains duplicate finding: {finding_id}")
            continue
        require_nonempty_string(item.get("title"), f"{finding_id} teardown title", errors)
        for key in ("acceptance_criteria", "dependencies"):
            if not isinstance(item.get(key), list) or any(not isinstance(value, str) or not value.strip() for value in item.get(key, [])):
                errors.append(f"{finding_id} teardown {key} must be an array of non-empty strings")
        indexed[finding_id] = item
    return indexed


def parse_acceptance_results(value: str, finding_id: str, errors: list[str]) -> list[dict[str, str]]:
    if value.strip() == "None":
        return []
    results: list[dict[str, str]] = []
    for index, entry in enumerate(value.split(" | "), start=1):
        parts = [part.strip() for part in entry.split(" => ")]
        if len(parts) != 3 or any(not part for part in parts):
            errors.append(f"{finding_id} Markdown acceptance result {index} must use criterion => status => evidence")
            continue
        results.append({"criterion": parts[0], "status": parts[1], "evidence": parts[2]})
    return results


def parse_finding_ledger(text: str, errors: list[str]) -> dict[str, dict[str, str]]:
    boundary = re.search(r"^# Convergence findings\s*$", text, re.MULTILINE)
    finding_text = text[:boundary.start()] if boundary else text
    matches = list(FINDING_HEADING.finditer(finding_text))
    records: dict[str, dict[str, str]] = {}
    counts = Counter(match.group(1) for match in matches)
    for finding_id, count in sorted(counts.items()):
        if count != 1:
            errors.append(f"implementation ledger repeats finding: {finding_id}")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(finding_text)
        fields = parse_labeled_fields(finding_text[match.end():end])
        fields["__title__"] = match.group(2).strip()
        missing = [field for field in REQUIRED_LEDGER_FIELDS if field not in fields]
        extra = sorted(set(fields) - set(REQUIRED_LEDGER_FIELDS) - {"__title__"})
        if missing:
            errors.append(f"{match.group(1)} ledger section missing fields: {', '.join(missing)}")
        if extra:
            errors.append(f"{match.group(1)} ledger section has unexpected fields: {', '.join(extra)}")
        records[match.group(1)] = fields
    return records


def parse_convergence_ledger(text: str, errors: list[str]) -> dict[str, dict[str, str]]:
    boundary = re.search(r"^# Convergence findings\s*$", text, re.MULTILINE)
    if not boundary:
        errors.append("implementation ledger is missing exact heading: # Convergence findings")
        return {}
    section = text[boundary.end():]
    matches = list(CONVERGENCE_HEADING.finditer(section))
    records: dict[str, dict[str, str]] = {}
    counts = Counter(match.group(1) for match in matches)
    for finding_id, count in sorted(counts.items()):
        if count != 1:
            errors.append(f"implementation ledger repeats convergence finding: {finding_id}")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        fields = parse_labeled_fields(section[match.end():end])
        fields["__title__"] = match.group(2).strip()
        missing = [field for field in REQUIRED_CONVERGENCE_FIELDS if field not in fields]
        extra = sorted(set(fields) - set(REQUIRED_CONVERGENCE_FIELDS) - {"__title__"})
        if missing:
            errors.append(f"{match.group(1)} convergence section missing fields: {', '.join(missing)}")
        if extra:
            errors.append(f"{match.group(1)} convergence section has unexpected fields: {', '.join(extra)}")
        records[match.group(1)] = fields
    return records


def parse_attribution(text: str, errors: list[str]) -> dict[str, set[str]]:
    section = markdown_section(text, "Changed-path attribution")
    if section is None:
        return {}
    rows = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        errors.append("Changed-path attribution must contain a Markdown table")
        return {}
    parsed = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
    expected = ["path", "classification", "finding ids", "baseline relationship", "rationale"]
    if [cell.lower() for cell in parsed[0]] != expected:
        errors.append("Changed-path attribution table has an invalid header")
        return {}
    mapping: dict[str, set[str]] = {}
    for index, row in enumerate(parsed[2:], start=1):
        if len(row) != 5:
            errors.append(f"Changed-path attribution row {index} must have five columns")
            continue
        path, classification, ids_cell, baseline, rationale = row
        if not path:
            errors.append(f"Changed-path attribution row {index} has an empty path")
            continue
        if classification not in ATTRIBUTION_CLASSES:
            errors.append(f"Changed-path attribution row {index} has invalid classification: {classification!r}")
        if not baseline or not rationale:
            errors.append(f"Changed-path attribution row {index} must explain baseline relationship and rationale")
        ids = set(re.findall(r"\b(?:[A-Z][A-Z0-9]*-\d{3}|REV-\d{3})\b", ids_cell))
        if path in mapping:
            errors.append(f"Changed-path attribution repeats path: {path}")
        mapping[path] = ids
    return mapping


def validate(teardown_root: Path, revision_root: Path) -> list[str]:
    errors: list[str] = []
    teardown_path = teardown_root / "findings.json"
    if not teardown_path.is_file():
        errors.append("teardown is missing findings.json")
    for name in REVISION_FILES:
        if not (revision_root / name).is_file():
            errors.append(f"revision is missing required file: {name}")
    if errors:
        return errors

    texts = {
        name: read_text(revision_root / name, name, errors)
        for name in REVISION_FILES
        if name.endswith(".md")
    }
    for name, headings in REQUIRED_SECTIONS.items():
        text = texts.get(name, "")
        for heading in headings:
            if markdown_section(text, heading) is None:
                errors.append(f"{name} is missing required section: ## {heading}")

    teardown = load_object(teardown_path, "teardown findings.json", errors)
    revision = load_object(revision_root / "revision.json", "revision.json", errors)
    if teardown is None or revision is None:
        return errors
    teardown_by_id = index_teardown(teardown, errors)

    try:
        expected_readme = render_readme(teardown, revision)
        expected_ledger = render_implementation_ledger(teardown, revision)
    except (KeyError, TypeError, ValueError, AttributeError):
        expected_readme = None
        expected_ledger = None
    if expected_readme is not None and texts.get("README.md") != expected_readme:
        errors.append("README.md is missing or stale; regenerate canonical revision views")
    if expected_ledger is not None and texts.get("03-implementation-ledger.md") != expected_ledger:
        errors.append("03-implementation-ledger.md is missing or stale; regenerate canonical revision views")

    exact_keys(revision, TOP_LEVEL, "revision.json", errors)
    if revision.get("schema_version") != 2:
        errors.append("revision.json schema_version must be 2")
    if revision.get("revision_status") not in {"complete", "partial", "blocked"}:
        errors.append("revision_status must be complete, partial, or blocked")
    for key in (
        "project", "teardown_path", "teardown_audited_revision",
        "implementation_start_revision", "implementation_end_revision",
    ):
        require_nonempty_string(revision.get(key), key, errors)
    validate_timestamp(revision.get("generated_at"), "generated_at", errors)
    if not isinstance(revision.get("existing_work_reconciled"), bool):
        errors.append("existing_work_reconciled must be a boolean")
    if revision.get("project") != teardown.get("project"):
        errors.append("revision project does not match teardown project")
    if revision.get("teardown_audited_revision") != teardown.get("audited_revision"):
        errors.append("revision teardown_audited_revision does not match teardown audited_revision")

    records = revision.get("findings")
    if not isinstance(records, list):
        errors.append("revision findings must be an array")
        return errors
    records_by_id: dict[str, dict[str, Any]] = {}
    sequence_to_id: dict[int, str] = {}
    approved_failed = False
    approved_blocked = False

    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"revision finding {position} must be an object")
            continue
        finding_id = record.get("id")
        label = finding_id if isinstance(finding_id, str) else f"finding {position}"
        exact_keys(record, FINDING_KEYS, label, errors)
        if not isinstance(finding_id, str) or not ID_PATTERN.fullmatch(finding_id):
            errors.append(f"{label} has invalid id")
            continue
        if finding_id in records_by_id:
            errors.append(f"duplicate revision finding: {finding_id}")
            continue
        records_by_id[finding_id] = record

        approval = record.get("approval")
        revalidation = record.get("revalidation")
        disposition = record.get("disposition")
        if approval not in APPROVALS:
            errors.append(f"{finding_id} has invalid approval: {approval!r}")
        if revalidation not in REVALIDATIONS:
            errors.append(f"{finding_id} has invalid revalidation: {revalidation!r}")
        if disposition not in DISPOSITIONS:
            errors.append(f"{finding_id} has invalid disposition: {disposition!r}")
        if approval in ALLOWED_DISPOSITIONS and disposition not in ALLOWED_DISPOSITIONS[approval]:
            errors.append(f"{finding_id} disposition {disposition!r} is incompatible with approval {approval!r}")
        if revalidation in {"stale", "not-applicable"} and (approval, disposition) != ("not-applicable", "not-applicable"):
            errors.append(f"{finding_id} {revalidation} revalidation requires not-applicable approval and disposition")
        if revalidation == "already-resolved" and disposition != "already-satisfied":
            errors.append(f"{finding_id} already-resolved revalidation requires already-satisfied disposition")
        if disposition == "already-satisfied" and revalidation != "already-resolved":
            errors.append(f"{finding_id} already-satisfied disposition requires already-resolved revalidation")
        if disposition == "blocked" and revalidation != "blocked":
            errors.append(f"{finding_id} blocked disposition requires blocked revalidation")
        require_nonempty_string(record.get("reason"), f"{finding_id} reason", errors)

        sequence = record.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            errors.append(f"{finding_id} sequence must be a positive integer")
        elif sequence in sequence_to_id:
            errors.append(f"duplicate sequence {sequence}: {sequence_to_id[sequence]} and {finding_id}")
        else:
            sequence_to_id[sequence] = finding_id

        files = require_string_list(record.get("files_changed"), f"{finding_id} files_changed", errors, safe_paths=True)
        verification = require_string_list(record.get("verification"), f"{finding_id} verification", errors)
        require_string_list(record.get("notes"), f"{finding_id} notes", errors)
        results = record.get("acceptance_results")
        parsed_results: list[dict[str, Any]] = []
        if not isinstance(results, list):
            errors.append(f"{finding_id} acceptance_results must be an array")
        else:
            for result_index, result in enumerate(results, start=1):
                if not exact_keys(result, {"criterion", "status", "evidence"}, f"{finding_id} acceptance result {result_index}", errors):
                    continue
                require_nonempty_string(result.get("criterion"), f"{finding_id} acceptance criterion {result_index}", errors)
                require_nonempty_string(result.get("evidence"), f"{finding_id} acceptance evidence {result_index}", errors)
                for part_name in ("criterion", "evidence"):
                    part = result.get(part_name)
                    if isinstance(part, str):
                        reject_round_trip_delimiters(
                            part, f"{finding_id} acceptance {part_name} {result_index}", errors
                        )
                if result.get("status") not in ACCEPTANCE_STATUSES:
                    errors.append(f"{finding_id} has invalid acceptance status: {result.get('status')!r}")
                parsed_results.append(result)

        original = teardown_by_id.get(finding_id)
        if original:
            expected_criteria = original.get("acceptance_criteria", [])
            actual_criteria = [result.get("criterion") for result in parsed_results]
            if approval == "approved" and actual_criteria != expected_criteria:
                errors.append(f"{finding_id} approved acceptance criteria must exactly match the teardown in order")
            if approval != "approved":
                unknown = sorted(set(actual_criteria) - set(expected_criteria))
                if unknown:
                    errors.append(f"{finding_id} acceptance results contain criteria not present in the teardown: {', '.join(unknown)}")
            duplicates = sorted(item for item, count in Counter(actual_criteria).items() if item and count > 1)
            if duplicates:
                errors.append(f"{finding_id} acceptance results repeat criteria: {', '.join(duplicates)}")

        statuses = [result.get("status") for result in parsed_results]
        if approval == "approved" and not parsed_results:
            errors.append(f"{finding_id} is approved but has no acceptance results")
        if approval == "approved" and "failed" in statuses:
            approved_failed = True
        if approval == "approved" and ("blocked" in statuses or disposition == "blocked"):
            approved_blocked = True

        if disposition == "implemented":
            if not files:
                errors.append(f"{finding_id} is implemented but lists no changed files")
            if not verification:
                errors.append(f"{finding_id} is implemented but lists no verification")
            if any(status not in {"passed", "not-applicable"} for status in statuses):
                errors.append(f"{finding_id} implemented disposition requires passed or not-applicable acceptance results")
        elif disposition == "already-satisfied":
            if files:
                errors.append(f"{finding_id} already-satisfied disposition must not list changed files")
            if not verification:
                errors.append(f"{finding_id} already-satisfied disposition requires verification")
            if any(status not in {"passed", "not-applicable"} for status in statuses):
                errors.append(f"{finding_id} already-satisfied disposition requires passed or not-applicable acceptance results")
        elif disposition == "retained":
            if files:
                errors.append(f"{finding_id} retained disposition must not list changed files")
            if not verification:
                errors.append(f"{finding_id} retained disposition requires preservation verification")
        elif disposition == "blocked":
            if files:
                errors.append(f"{finding_id} blocked disposition must not list changed files")
            if "blocked" not in statuses:
                errors.append(f"{finding_id} blocked disposition requires at least one blocked acceptance result")
        elif files:
            errors.append(f"{finding_id} disposition {disposition!r} must not list changed files")

    teardown_ids = set(teardown_by_id)
    revision_ids = set(records_by_id)
    if teardown_ids - revision_ids:
        errors.append(f"revision missing findings: {', '.join(sorted(teardown_ids - revision_ids))}")
    if revision_ids - teardown_ids:
        errors.append(f"revision has unknown findings: {', '.join(sorted(revision_ids - teardown_ids))}")
    if set(sequence_to_id) != set(range(1, len(records_by_id) + 1)):
        errors.append("finding sequences must be contiguous from 1 through the finding count")

    for finding_id in sorted(teardown_ids & revision_ids):
        original = teardown_by_id[finding_id]
        record = records_by_id[finding_id]
        if record.get("disposition") == "retained":
            if original.get("type") != "strength" and original.get("action") != "retain":
                errors.append(f"{finding_id} retained disposition requires a strength or retain action")
        sequence = record.get("sequence")
        for dependency in original.get("dependencies", []):
            dependency_record = records_by_id.get(dependency)
            if dependency_record is None:
                continue
            dependency_sequence = dependency_record.get("sequence")
            if isinstance(sequence, int) and isinstance(dependency_sequence, int) and dependency_sequence >= sequence:
                errors.append(f"{finding_id} sequence must follow dependency {dependency}")

    ledger_text = texts.get("03-implementation-ledger.md", "")
    ledger_records = parse_finding_ledger(ledger_text, errors)
    if teardown_ids - set(ledger_records):
        errors.append(f"implementation ledger missing findings: {', '.join(sorted(teardown_ids - set(ledger_records)))}")
    if set(ledger_records) - teardown_ids:
        errors.append(f"implementation ledger has unknown findings: {', '.join(sorted(set(ledger_records) - teardown_ids))}")
    for finding_id in sorted(teardown_ids & revision_ids & set(ledger_records)):
        original = teardown_by_id[finding_id]
        record = records_by_id[finding_id]
        fields = ledger_records[finding_id]
        if fields.get("__title__") != original.get("title"):
            errors.append(f"{finding_id} implementation ledger title does not match teardown")
        expected_verification_state = original.get("verification_state", "legacy-not-recorded")
        if fields.get("Teardown verification state") != expected_verification_state:
            errors.append(f"{finding_id} ledger teardown verification state differs from findings.json")
        scalar_expectations = {
            "Approval": record.get("approval"),
            "Revalidation": record.get("revalidation"),
            "Disposition": record.get("disposition"),
            "Sequence": str(record.get("sequence")),
            "Reason": record.get("reason"),
            "Revision record digest": canonical_digest(record),
        }
        for label, expected in scalar_expectations.items():
            if fields.get(label) != expected:
                errors.append(f"{finding_id} Markdown {label} differs from revision.json")
        array_expectations = {
            "Files changed": record.get("files_changed", []),
            "Verification": record.get("verification", []),
            "Notes": record.get("notes", []),
        }
        for label, expected in array_expectations.items():
            if split_pipe(fields.get(label, "")) != expected:
                errors.append(f"{finding_id} Markdown {label} differs from revision.json")
        if parse_acceptance_results(fields.get("Acceptance results", ""), finding_id, errors) != record.get("acceptance_results"):
            errors.append(f"{finding_id} Markdown Acceptance results differ from revision.json")

    convergence = revision.get("convergence_findings")
    convergence_by_id: dict[str, dict[str, Any]] = {}
    blocking_count = 0
    if not isinstance(convergence, list):
        errors.append("convergence_findings must be an array")
    else:
        for position, record in enumerate(convergence, start=1):
            if not isinstance(record, dict):
                errors.append(f"convergence finding {position} must be an object")
                continue
            convergence_id = record.get("id")
            label = convergence_id if isinstance(convergence_id, str) else f"convergence finding {position}"
            exact_keys(record, CONVERGENCE_KEYS, label, errors)
            if not isinstance(convergence_id, str) or not re.fullmatch(r"REV-\d{3}", convergence_id):
                errors.append(f"{label} must have an id matching REV-<NNN>")
                continue
            if convergence_id in convergence_by_id:
                errors.append(f"duplicate convergence finding: {convergence_id}")
                continue
            convergence_by_id[convergence_id] = record
            for key in ("title", "source", "reason"):
                require_nonempty_string(record.get(key), f"{convergence_id} {key}", errors)
            severity = record.get("severity")
            status = record.get("status")
            if severity not in CONVERGENCE_SEVERITIES:
                errors.append(f"{convergence_id} has invalid severity: {severity!r}")
            if status not in CONVERGENCE_STATUSES:
                errors.append(f"{convergence_id} has invalid status: {status!r}")
            files = require_string_list(record.get("files_changed"), f"{convergence_id} files_changed", errors, safe_paths=True)
            # Contract section 9: verification is required for fixed,
            # already-satisfied, and invalid. An open, deferred, or blocked
            # finding has nothing to verify yet.
            verification = require_string_list(
                record.get("verification"),
                f"{convergence_id} verification",
                errors,
                allow_empty=status not in RESOLVED_CONVERGENCE,
            )
            if status == "fixed" and not files:
                errors.append(f"{convergence_id} is fixed but lists no changed files")
            # Contract section 9: only already-satisfied and invalid assert that
            # nothing changed at current head.
            if status in NO_CHANGE_CONVERGENCE and files:
                errors.append(f"{convergence_id} status {status!r} must not list changed files")
            if severity in BLOCKING_SEVERITIES and status in UNRESOLVED_CONVERGENCE:
                blocking_count += 1

    convergence_ledger = parse_convergence_ledger(ledger_text, errors)
    convergence_ids = set(convergence_by_id)
    if convergence_ids - set(convergence_ledger):
        errors.append(f"implementation ledger missing convergence findings: {', '.join(sorted(convergence_ids - set(convergence_ledger)))}")
    if set(convergence_ledger) - convergence_ids:
        errors.append(f"implementation ledger has unknown convergence findings: {', '.join(sorted(set(convergence_ledger) - convergence_ids))}")
    for convergence_id in sorted(convergence_ids & set(convergence_ledger)):
        record = convergence_by_id[convergence_id]
        fields = convergence_ledger[convergence_id]
        scalar_expectations = {
            "__title__": record.get("title"),
            "Source": record.get("source"),
            "Severity": record.get("severity"),
            "Status": record.get("status"),
            "Reason": record.get("reason"),
            "Convergence record digest": canonical_digest(record),
        }
        for label, expected in scalar_expectations.items():
            if fields.get(label) != expected:
                errors.append(f"{convergence_id} Markdown {label} differs from revision.json")
        for label, key in (("Files changed", "files_changed"), ("Verification", "verification")):
            if split_pipe(fields.get(label, "")) != record.get(key):
                errors.append(f"{convergence_id} Markdown {label} differs from revision.json")

    final_state = revision.get("final_state")
    if not exact_keys(final_state, FINAL_STATE_KEYS, "final_state", errors):
        final_state = final_state if isinstance(final_state, dict) else {}
    artifact_relationship = final_state.get("artifact_relationship")
    review_convergence = final_state.get("review_convergence")
    merge_readiness = final_state.get("merge_readiness")
    release_readiness = final_state.get("release_readiness")
    declared_blocking = final_state.get("blocking_convergence_findings")
    if artifact_relationship not in ARTIFACT_RELATIONSHIPS:
        errors.append(f"final_state has invalid artifact_relationship: {artifact_relationship!r}")
    if review_convergence not in REVIEW_CONVERGENCE:
        errors.append(f"final_state has invalid review_convergence: {review_convergence!r}")
    if merge_readiness not in READINESS:
        errors.append(f"final_state has invalid merge_readiness: {merge_readiness!r}")
    if release_readiness not in READINESS:
        errors.append(f"final_state has invalid release_readiness: {release_readiness!r}")
    if not isinstance(declared_blocking, int) or isinstance(declared_blocking, bool) or declared_blocking < 0:
        errors.append("final_state blocking_convergence_findings must be a non-negative integer")
    elif declared_blocking != blocking_count:
        errors.append(f"blocking_convergence_findings is {declared_blocking} but computed count is {blocking_count}")

    delivery = final_state.get("delivery")
    if not exact_keys(delivery, DELIVERY_KEYS, "final_state delivery", errors):
        delivery = delivery if isinstance(delivery, dict) else {}
    for key in DELIVERY_KEYS:
        if delivery.get(key) not in DELIVERY_VALUES:
            errors.append(f"delivery {key} has invalid value: {delivery.get(key)!r}")
    if artifact_relationship == "artifact-only-descendant" and delivery.get("committed") != "verified":
        errors.append("artifact-only-descendant requires a verified committed product endpoint")
    if delivery.get("pushed") == "verified" and delivery.get("committed") != "verified":
        errors.append("verified push requires verified commit state")
    if delivery.get("pull_request_updated") == "verified" and delivery.get("pushed") != "verified":
        errors.append("verified pull request update requires verified push state")
    if delivery.get("merged") == "verified" and (delivery.get("committed") != "verified" or delivery.get("pushed") != "verified"):
        errors.append("verified merge requires verified commit and push state")

    handoff = texts.get("04-verification-and-handoff.md", "")
    handoff_values: dict[str, str | None] = {}
    for key, (label, allowed) in HANDOFF_MARKERS.items():
        value = marker(handoff, label, errors)
        handoff_values[key] = value
        if allowed is not None and value is not None and value not in allowed:
            errors.append(f"handoff marker {label} has invalid value: {value!r}")
    expected_markers = {
        "revision_status": revision.get("revision_status"),
        "implementation_end_revision": revision.get("implementation_end_revision"),
        "artifact_relationship": artifact_relationship,
        "review_convergence": review_convergence,
        "existing_work_reconciled": "yes" if revision.get("existing_work_reconciled") else "no",
        "blocking_convergence_findings": str(declared_blocking) if isinstance(declared_blocking, int) else None,
        "merge_readiness": merge_readiness,
        "release_readiness": release_readiness,
    }
    for key, expected in expected_markers.items():
        if handoff_values.get(key) is not None and expected is not None and handoff_values[key] != expected:
            errors.append(f"handoff {HANDOFF_MARKERS[key][0]} differs from revision.json")
    for key, label in DELIVERY_MARKERS.items():
        value = marker(handoff, label, errors)
        expected = delivery.get(key)
        if value is not None and expected is not None and value != expected:
            errors.append(f"handoff {label} differs from revision.json")

    manual_review = handoff_values.get("manual_review")
    current_head_review = handoff_values.get("current_head_review")
    if review_convergence == "passed":
        if blocking_count:
            errors.append("review convergence cannot pass with blocking convergence findings")
        if manual_review != "completed":
            errors.append("passed review convergence requires completed manual adversarial review")
        if current_head_review != "completed":
            errors.append("passed review convergence requires completed current-head review after the final product change")
    if revision.get("revision_status") == "complete":
        if approved_failed or approved_blocked:
            errors.append("complete revision has a failed or blocked approved acceptance criterion")
        if revision.get("existing_work_reconciled") is not True:
            errors.append("complete revision requires existing_work_reconciled true")
        if review_convergence != "passed":
            errors.append("complete revision requires passed review convergence")
    if merge_readiness == "ready":
        if review_convergence != "passed" or blocking_count:
            errors.append("merge readiness requires passed review convergence and zero blocking convergence findings")
        if revision.get("revision_status") == "blocked":
            errors.append("a blocked revision cannot be merge-ready")
        if revision.get("existing_work_reconciled") is not True:
            errors.append("merge readiness requires existing_work_reconciled true")
        if approved_failed:
            errors.append("merge readiness cannot be ready with failed approved acceptance criteria")
    if release_readiness == "ready":
        if merge_readiness != "ready":
            errors.append("release readiness requires merge readiness")
        if revision.get("revision_status") != "complete":
            errors.append("release readiness requires complete revision status")
        if approved_blocked:
            errors.append("release readiness cannot be ready with blocked approved acceptance criteria")
    if handoff_values.get("validator_status") != "passed":
        errors.append("final handoff Revision validator status must be passed")

    attribution = parse_attribution(handoff, errors)
    all_known_ids = revision_ids | convergence_ids
    for path, ids in attribution.items():
        unknown = sorted(ids - all_known_ids)
        if unknown:
            errors.append(f"Changed-path attribution for {path} references unknown IDs: {', '.join(unknown)}")
    for finding_id, record in records_by_id.items():
        for path in record.get("files_changed", []):
            if path not in attribution:
                errors.append(f"changed path {path} from {finding_id} is missing from Changed-path attribution")
            elif finding_id not in attribution[path]:
                errors.append(f"Changed-path attribution for {path} does not include {finding_id}")
    for convergence_id, record in convergence_by_id.items():
        for path in record.get("files_changed", []):
            if path not in attribution:
                errors.append(f"changed path {path} from {convergence_id} is missing from Changed-path attribution")
            elif convergence_id not in attribution[path]:
                errors.append(f"Changed-path attribution for {path} does not include {convergence_id}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown_directory", type=Path)
    parser.add_argument("revision_directory", type=Path)
    args = parser.parse_args()
    errors = validate(args.teardown_directory.resolve(), args.revision_directory.resolve())
    if errors:
        print("Project revision validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Project revision validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
