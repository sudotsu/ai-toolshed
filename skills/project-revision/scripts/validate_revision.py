#!/usr/bin/env python3
"""Validate a schema-version-2 project-revision ledger against a teardown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REVISION_FILES = (
    "00-decisions-and-scope.md",
    "01-baseline-and-revalidation.md",
    "02-execution-plan.md",
    "03-implementation-ledger.md",
    "04-verification-and-handoff.md",
    "revision.json",
)
TOP_LEVEL = {
    "schema_version", "project", "teardown_path", "teardown_audited_revision",
    "implementation_start_revision", "implementation_end_revision",
    "revision_status", "generated_at", "existing_work_reconciled", "findings",
    "convergence_findings", "final_state",
}
FINDING_KEYS = {
    "id", "approval", "revalidation", "disposition", "sequence", "reason",
    "files_changed", "acceptance_results", "verification", "notes",
}
CONVERGENCE_KEYS = {
    "id", "title", "source", "severity", "status", "reason",
    "files_changed", "verification",
}
FINAL_STATE_KEYS = {
    "artifact_relationship", "review_convergence",
    "blocking_convergence_findings", "merge_readiness", "release_readiness",
    "delivery",
}
DELIVERY_KEYS = {"committed", "pushed", "pull_request_updated", "merged"}
APPROVALS = {"approved", "deferred", "rejected", "accepted-risk", "not-applicable"}
REVALIDATIONS = {"confirmed", "changed", "stale", "already-resolved", "not-applicable", "blocked"}
DISPOSITIONS = {
    "implemented", "already-satisfied", "retained", "deferred", "rejected",
    "accepted-risk", "not-applicable", "blocked",
}
ACCEPTANCE_STATUSES = {"passed", "failed", "not-applicable", "blocked"}
CONVERGENCE_SEVERITIES = {"critical", "high", "medium", "low"}
CONVERGENCE_STATUSES = {"fixed", "already-satisfied", "invalid", "open", "deferred", "blocked"}
BLOCKING_SEVERITIES = {"critical", "high", "medium"}
UNRESOLVED_CONVERGENCE = {"open", "deferred", "blocked"}
ARTIFACT_RELATIONSHIPS = {"working-tree", "artifact-only-descendant"}
REVIEW_CONVERGENCE = {"passed", "blocked"}
READINESS = {"ready", "not-ready", "not-applicable"}
DELIVERY_VALUES = {"verified", "not-performed", "unverified", "not-applicable"}
FINDING_HEADING = re.compile(r"^## ([A-Z][A-Z0-9]*-\d{3}) — (.+)$", re.MULTILINE)
CONVERGENCE_HEADING = re.compile(r"^### (REV-\d{3}) — (.+)$", re.MULTILINE)
ALLOWED_DISPOSITIONS = {
    "approved": {"implemented", "already-satisfied", "retained", "blocked"},
    "deferred": {"deferred"},
    "rejected": {"rejected"},
    "accepted-risk": {"accepted-risk"},
    "not-applicable": {"not-applicable"},
}
HANDOFF_MARKERS = {
    "revision_status": ("Revision status", {"complete", "partial", "blocked"}),
    "implementation_end_revision": ("Implementation endpoint", None),
    "artifact_relationship": ("Artifact relationship", ARTIFACT_RELATIONSHIPS),
    "review_convergence": ("Review convergence", REVIEW_CONVERGENCE),
    "blocking_convergence_findings": ("Blocking convergence findings", None),
    "merge_readiness": ("Merge readiness", READINESS),
    "release_readiness": ("Release readiness", READINESS),
}
DELIVERY_MARKERS = {
    "committed": "Committed",
    "pushed": "Pushed",
    "pull_request_updated": "Pull request updated",
    "merged": "Merged",
}


def load_object(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read {label}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label} must contain an object")
        return None
    return value


def require_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")


def require_string_list(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(f"{label} must be an array of strings")
        return False
    return True


def exact_keys(value: Any, expected: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        errors.append(f"{label} missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{label} has unexpected keys: {', '.join(extra)}")
    return not missing and not extra


def marker(handoff: str, label: str, errors: list[str]) -> str | None:
    match = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(\S(?:.*\S)?)\s*$", handoff, re.MULTILINE)
    if not match:
        errors.append(f"verification handoff is missing exact marker: **{label}:**")
        return None
    return match.group(1)


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

    teardown = load_object(teardown_path, "teardown findings.json", errors)
    revision = load_object(revision_root / "revision.json", "revision.json", errors)
    if teardown is None or revision is None:
        return errors

    teardown_findings = teardown.get("findings")
    if not isinstance(teardown_findings, list):
        errors.append("teardown findings must be an array")
        return errors
    teardown_by_id: dict[str, dict[str, Any]] = {}
    for item in teardown_findings:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append("teardown contains a finding without a valid id")
            continue
        if item["id"] in teardown_by_id:
            errors.append(f"teardown contains duplicate finding: {item['id']}")
        teardown_by_id[item["id"]] = item

    exact_keys(revision, TOP_LEVEL, "revision.json", errors)
    if revision.get("schema_version") != 2:
        errors.append("revision.json schema_version must be 2")
    if revision.get("revision_status") not in {"complete", "partial", "blocked"}:
        errors.append("revision_status must be complete, partial, or blocked")
    for key in (
        "project", "teardown_path", "teardown_audited_revision",
        "implementation_start_revision", "implementation_end_revision", "generated_at",
    ):
        require_string(revision.get(key), key, errors)
    generated_at = revision.get("generated_at")
    if isinstance(generated_at, str):
        try:
            datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        except ValueError:
            errors.append("generated_at must be an ISO-8601 timestamp")
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
    sequences: dict[int, str] = {}
    approved_incomplete = False
    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"revision finding {position} must be an object")
            continue
        finding_id = record.get("id")
        label = finding_id if isinstance(finding_id, str) else f"finding {position}"
        exact_keys(record, FINDING_KEYS, label, errors)
        if not isinstance(finding_id, str):
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
        require_string(record.get("reason"), f"{finding_id} reason", errors)

        sequence = record.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            errors.append(f"{finding_id} sequence must be a positive integer")
        elif sequence in sequences:
            errors.append(f"duplicate sequence {sequence}: {sequences[sequence]} and {finding_id}")
        else:
            sequences[sequence] = finding_id

        for key in ("files_changed", "verification", "notes"):
            require_string_list(record.get(key), f"{finding_id} {key}", errors)
        files_changed = record.get("files_changed")
        if disposition == "implemented" and isinstance(files_changed, list) and not files_changed:
            errors.append(f"{finding_id} is implemented but lists no changed files")
        if disposition == "already-satisfied" and revalidation != "already-resolved":
            errors.append(f"{finding_id} already-satisfied requires revalidation already-resolved")
        if disposition == "implemented" and revalidation in {"stale", "not-applicable", "blocked"}:
            errors.append(f"{finding_id} cannot be implemented with revalidation {revalidation!r}")

        results = record.get("acceptance_results")
        if not isinstance(results, list):
            errors.append(f"{finding_id} acceptance_results must be an array")
        else:
            if approval == "approved" and not results:
                errors.append(f"{finding_id} is approved but has no acceptance results")
            for result_index, result in enumerate(results, start=1):
                if not isinstance(result, dict) or set(result) != {"criterion", "status", "evidence"}:
                    errors.append(f"{finding_id} acceptance result {result_index} has invalid shape")
                    continue
                require_string(result.get("criterion"), f"{finding_id} acceptance criterion", errors)
                require_string(result.get("evidence"), f"{finding_id} acceptance evidence", errors)
                if result.get("status") not in ACCEPTANCE_STATUSES:
                    errors.append(f"{finding_id} has invalid acceptance status: {result.get('status')!r}")
                if approval == "approved" and result.get("status") in {"failed", "blocked"}:
                    approved_incomplete = True
        if approval == "approved" and disposition == "blocked":
            approved_incomplete = True

    teardown_ids = set(teardown_by_id)
    revision_ids = set(records_by_id)
    if teardown_ids - revision_ids:
        errors.append(f"revision missing findings: {', '.join(sorted(teardown_ids - revision_ids))}")
    if revision_ids - teardown_ids:
        errors.append(f"revision has unknown findings: {', '.join(sorted(revision_ids - teardown_ids))}")
    if set(sequences) != set(range(1, len(records_by_id) + 1)):
        errors.append("finding sequences must be contiguous from 1 through the finding count")

    ledger = (revision_root / "03-implementation-ledger.md").read_text(encoding="utf-8")
    ledger_matches = list(FINDING_HEADING.finditer(ledger))
    ledger_ids = [match.group(1) for match in ledger_matches]
    ledger_titles = {match.group(1): match.group(2).strip() for match in ledger_matches}
    ledger_counts = {finding_id: ledger_ids.count(finding_id) for finding_id in set(ledger_ids)}
    if teardown_ids - set(ledger_ids):
        errors.append(f"implementation ledger missing findings: {', '.join(sorted(teardown_ids - set(ledger_ids)))}")
    if set(ledger_ids) - teardown_ids:
        errors.append(f"implementation ledger has unknown findings: {', '.join(sorted(set(ledger_ids) - teardown_ids))}")
    repeated = sorted(finding_id for finding_id, count in ledger_counts.items() if count != 1)
    if repeated:
        errors.append(f"implementation ledger repeats findings: {', '.join(repeated)}")

    for finding_id in teardown_ids & revision_ids:
        teardown_finding = teardown_by_id[finding_id]
        record = records_by_id[finding_id]
        teardown_title = teardown_finding.get("title")
        if isinstance(teardown_title, str) and ledger_titles.get(finding_id) != teardown_title:
            errors.append(f"{finding_id} implementation ledger title does not match teardown")
        if record.get("disposition") == "retained":
            if teardown_finding.get("type") != "strength" and teardown_finding.get("action") != "retain":
                errors.append(f"{finding_id} retained disposition requires a strength or retain action")
            if record.get("files_changed"):
                errors.append(f"{finding_id} retained disposition must not list changed files")
        sequence = record.get("sequence")
        for dependency in teardown_finding.get("dependencies", []):
            dependency_record = records_by_id.get(dependency)
            if dependency_record is None:
                continue
            dependency_sequence = dependency_record.get("sequence")
            if isinstance(sequence, int) and isinstance(dependency_sequence, int) and dependency_sequence >= sequence:
                errors.append(f"{finding_id} sequence must follow dependency {dependency}")

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
                require_string(record.get(key), f"{convergence_id} {key}", errors)
            severity = record.get("severity")
            status = record.get("status")
            if severity not in CONVERGENCE_SEVERITIES:
                errors.append(f"{convergence_id} has invalid severity: {severity!r}")
            if status not in CONVERGENCE_STATUSES:
                errors.append(f"{convergence_id} has invalid status: {status!r}")
            files_ok = require_string_list(record.get("files_changed"), f"{convergence_id} files_changed", errors)
            verification_ok = require_string_list(record.get("verification"), f"{convergence_id} verification", errors)
            if status == "fixed":
                if files_ok and not record.get("files_changed"):
                    errors.append(f"{convergence_id} is fixed but lists no changed files")
                if verification_ok and not record.get("verification"):
                    errors.append(f"{convergence_id} is fixed but lists no verification")
            if severity in BLOCKING_SEVERITIES and status in UNRESOLVED_CONVERGENCE:
                blocking_count += 1

    convergence_matches = list(CONVERGENCE_HEADING.finditer(ledger))
    convergence_headings = [match.group(1) for match in convergence_matches]
    convergence_titles = {match.group(1): match.group(2).strip() for match in convergence_matches}
    convergence_heading_counts = {item: convergence_headings.count(item) for item in set(convergence_headings)}
    convergence_ids = set(convergence_by_id)
    if convergence_ids - set(convergence_headings):
        errors.append(f"implementation ledger missing convergence findings: {', '.join(sorted(convergence_ids - set(convergence_headings)))}")
    if set(convergence_headings) - convergence_ids:
        errors.append(f"implementation ledger has unknown convergence findings: {', '.join(sorted(set(convergence_headings) - convergence_ids))}")
    repeated_convergence = sorted(item for item, count in convergence_heading_counts.items() if count != 1)
    if repeated_convergence:
        errors.append(f"implementation ledger repeats convergence findings: {', '.join(repeated_convergence)}")
    for convergence_id in convergence_ids & set(convergence_headings):
        if convergence_titles.get(convergence_id) != convergence_by_id[convergence_id].get("title"):
            errors.append(f"{convergence_id} implementation ledger title does not match revision.json")

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

    if review_convergence == "passed" and blocking_count != 0:
        errors.append("review convergence cannot pass with blocking convergence findings")
    if merge_readiness == "ready":
        if review_convergence != "passed" or blocking_count != 0:
            errors.append("merge readiness requires passed review convergence and zero blocking findings")
        if revision.get("revision_status") == "blocked":
            errors.append("a blocked revision cannot be merge-ready")
        if revision.get("existing_work_reconciled") is not True:
            errors.append("merge readiness requires existing_work_reconciled true")
    if release_readiness == "ready":
        if merge_readiness != "ready":
            errors.append("release readiness requires merge readiness")
        if revision.get("revision_status") != "complete":
            errors.append("release readiness requires complete revision status")
    if artifact_relationship == "artifact-only-descendant" and delivery.get("committed") != "verified":
        errors.append("artifact-only-descendant requires a verified committed product endpoint")
    if delivery.get("pushed") == "verified" and delivery.get("committed") != "verified":
        errors.append("verified push requires verified commit state")
    if delivery.get("merged") == "verified":
        if delivery.get("committed") != "verified" or delivery.get("pushed") != "verified":
            errors.append("verified merge requires verified commit and push state")

    status = revision.get("revision_status")
    if status == "complete":
        if approved_incomplete:
            errors.append("complete revision has an incomplete approved finding")
        if revision.get("existing_work_reconciled") is not True:
            errors.append("complete revision requires existing_work_reconciled true")

    handoff = (revision_root / "04-verification-and-handoff.md").read_text(encoding="utf-8")
    marker_values: dict[str, str | None] = {}
    for key, (label, allowed) in HANDOFF_MARKERS.items():
        value = marker(handoff, label, errors)
        marker_values[key] = value
        if allowed is not None and value is not None and value not in allowed:
            errors.append(f"handoff marker {label} has invalid value: {value!r}")
    expected_markers = {
        "revision_status": revision.get("revision_status"),
        "implementation_end_revision": revision.get("implementation_end_revision"),
        "artifact_relationship": artifact_relationship,
        "review_convergence": review_convergence,
        "blocking_convergence_findings": str(declared_blocking) if isinstance(declared_blocking, int) else None,
        "merge_readiness": merge_readiness,
        "release_readiness": release_readiness,
    }
    for key, expected in expected_markers.items():
        if marker_values.get(key) is not None and expected is not None and marker_values[key] != expected:
            errors.append(f"handoff {HANDOFF_MARKERS[key][0]} differs from revision.json")
    for key, label in DELIVERY_MARKERS.items():
        value = marker(handoff, label, errors)
        expected = delivery.get(key)
        if value is not None and expected is not None and value != expected:
            errors.append(f"handoff {label} differs from revision.json")

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
