#!/usr/bin/env python3
"""Semantic reconciliation and evidence/readiness validation for brand revision."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from render_revision import GENERATED_FILES, render_all
from validator_common import (
    AUTHORITY_IDS, CHANGE_AUTHORITY, DELIVERY_AUTHORITY, ID_PATTERNS, PLACEHOLDER_TOKENS,
    _completed_evidence, _evidence_with_level, _evidence_with_method, _unique_ids,
)

def _scan_placeholders(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _scan_placeholders(item, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _scan_placeholders(item, f"{path}[{i}]", errors)
    elif isinstance(value, str):
        lower = value.lower()
        for token in PLACEHOLDER_TOKENS:
            if token.lower() in lower:
                errors.append(f"{path} contains forbidden placeholder token {token!r}")
                break


def _semantic_validate(teardown: dict[str, Any], coverage: dict[str, Any], data: dict[str, Any], revision_dir: Path, errors: list[str], check_markdown: bool) -> None:
    if teardown.get("schema_version") != "brand-teardown-v1":
        errors.append("teardown findings schema must be brand-teardown-v1")
    if coverage.get("schema_version") != "brand-teardown-coverage-v1":
        errors.append("teardown coverage schema must be brand-teardown-coverage-v1")
    if data.get("schema_version") != "brand-revision-v1":
        errors.append("revision schema_version must be brand-revision-v1")

    audit = teardown["audit"]
    project = data["project"]
    td = data["teardown"]
    expected_project = (audit["project_name"], audit["project_locator"], audit.get("production_locator"))
    actual_project = (project["name"], project["locator"], project.get("production_locator"))
    if actual_project != expected_project:
        errors.append("revision.project must exactly match canonical teardown project name, locator, and production locator")
    if td["findings_schema"] != teardown["schema_version"] or td["coverage_schema"] != coverage["schema_version"]:
        errors.append("revision.teardown schema declarations do not match canonical teardown")
    if td["audited_revision"] != audit["audited_revision"]:
        errors.append("revision.teardown.audited_revision must equal canonical teardown")
    if td["review_status"] != audit["review_status"]:
        errors.append("revision.teardown.review_status must equal canonical teardown")
    if td["validator_result"] != "passed":
        errors.append("revision.teardown.validator_result must be passed")

    decision_by_id = _unique_ids(data["decisions"], "revision.decisions", errors, ID_PATTERNS["decision"])
    authority_by_id = _unique_ids(data["authority_matrix"], "revision.authority_matrix", errors)
    finding_by_id = _unique_ids(data["findings"], "revision.findings", errors)
    claim_by_id = _unique_ids(data["claim_trace"], "revision.claim_trace", errors)
    change_by_id = _unique_ids(data["changes"], "revision.changes", errors, ID_PATTERNS["change"])
    evidence_by_id = _unique_ids(data["evidence"], "revision.evidence", errors, ID_PATTERNS["evidence"])
    perception_by_id = _unique_ids(data["perception_tests"], "revision.perception_tests", errors, ID_PATTERNS["perception"])
    convergence_by_id = _unique_ids(data["convergence_findings"], "revision.convergence_findings", errors, ID_PATTERNS["convergence"])
    rollout_by_id = _unique_ids(data["rollouts"], "revision.rollouts", errors, ID_PATTERNS["rollout"])

    if set(authority_by_id) != set(AUTHORITY_IDS):
        errors.append("authority_matrix must contain exactly the fifteen canonical authority IDs")
    authority_state = {key: row.get("state") for key, row in authority_by_id.items()}

    source_by_id = {row["id"]: row for row in teardown["findings"]}
    if set(finding_by_id) != set(source_by_id):
        missing = sorted(set(source_by_id) - set(finding_by_id))
        extra = sorted(set(finding_by_id) - set(source_by_id))
        if missing:
            errors.append(f"revision findings missing canonical teardown IDs: {missing}")
        if extra:
            errors.append(f"revision findings contain unknown IDs: {extra}")

    decision_cover: dict[str, list[dict[str, Any]]] = {}
    for dec in decision_by_id.values():
        for fid in dec["finding_ids"]:
            if fid not in source_by_id:
                errors.append(f"decision {dec['id']} references unknown finding {fid}")
            decision_cover.setdefault(fid, []).append(dec)
        option_ids = {o.get("id") for o in dec["options"] if isinstance(o, dict)}
        if dec["safe_default"] not in option_ids:
            errors.append(f"decision {dec['id']} safe_default must reference one of its options")
        if dec["status"] == "resolved":
            if dec["owner_selection"] not in option_ids:
                errors.append(f"resolved decision {dec['id']} must select a valid option")
            if not _completed_evidence(evidence_by_id, dec["evidence_ids"]):
                errors.append(f"resolved decision {dec['id']} requires completed owner-authorization evidence")
            elif not _evidence_with_method(evidence_by_id, dec["evidence_ids"], "owner-authorization"):
                errors.append(f"resolved decision {dec['id']} requires owner-authorization evidence method")
        elif dec["owner_selection"] is not None:
            errors.append(f"decision {dec['id']} owner_selection must be null unless status is resolved")

    sequences: dict[str, int] = {}
    for fid, src in source_by_id.items():
        rev = finding_by_id.get(fid)
        if rev is None:
            continue
        if rev["title"] != src["title"]:
            errors.append(f"finding {fid} title must exactly match teardown")
        if rev["source_status"] != src["status"]:
            errors.append(f"finding {fid} source_status must exactly match teardown")
        if rev["dependencies"] != src["dependencies"]:
            errors.append(f"finding {fid} dependencies must exactly match teardown")
        if rev["preservation_constraints"] != src["preservation_constraints"]:
            errors.append(f"finding {fid} preservation_constraints must exactly match teardown")
        expected_sequence = src["implementation"]["order"]
        if rev["sequence"] != expected_sequence:
            errors.append(f"finding {fid} sequence must preserve teardown implementation order {expected_sequence}")
        sequences[fid] = rev["sequence"]
        src_criteria = src["acceptance_criteria"]
        rev_criteria = [row["criterion"] for row in rev["acceptance_results"]]
        if rev_criteria != src_criteria:
            errors.append(f"finding {fid} acceptance criteria must exactly match teardown in order")
        if src["status"] == "decision_required":
            if fid not in decision_cover:
                errors.append(f"decision-required finding {fid} must be covered by a decision")
            if rev["approval"] == "approved" and not any(d["status"] == "resolved" for d in decision_cover.get(fid, [])):
                errors.append(f"finding {fid} cannot be approved until its owner decision is resolved")
        if src["status"] == "retained_strength":
            if rev["preservation_status"] != "owner-approved-tradeoff" and rev["disposition"] != "preserved":
                errors.append(f"retained strength {fid} must remain preserved unless an owner-approved tradeoff is recorded")
        if rev["preservation_status"] == "preserved":
            if not _completed_evidence(evidence_by_id, rev["evidence_ids"]):
                errors.append(f"finding {fid} preservation_status preserved requires completed evidence")
        if rev["preservation_status"] == "owner-approved-tradeoff":
            if not any(d["status"] == "resolved" for d in decision_cover.get(fid, [])):
                errors.append(f"finding {fid} owner-approved preservation tradeoff requires a resolved decision")
        if rev["disposition"] == "implemented":
            if rev["approval"] != "approved":
                errors.append(f"implemented finding {fid} must be approved")
            if rev["revalidation"] not in {"confirmed", "changed"}:
                errors.append(f"implemented finding {fid} must be revalidated confirmed or changed")
            if not rev["change_ids"]:
                errors.append(f"implemented finding {fid} requires at least one mapped change")
            if any(r["status"] in {"pending", "failed", "blocked"} for r in rev["acceptance_results"]):
                errors.append(f"implemented finding {fid} cannot have pending, failed, or blocked acceptance results")
        if rev["disposition"] == "already-satisfied":
            if rev["revalidation"] != "already-resolved":
                errors.append(f"already-satisfied finding {fid} requires already-resolved revalidation")
        if rev["approval"] == "deferred" and rev["disposition"] != "deferred":
            errors.append(f"deferred finding {fid} must use deferred disposition")
        if rev["approval"] == "rejected" and rev["disposition"] != "rejected":
            errors.append(f"rejected finding {fid} must use rejected disposition")
        if rev["approval"] == "accepted-risk" and rev["disposition"] != "accepted-risk":
            errors.append(f"accepted-risk finding {fid} must use accepted-risk disposition")
        if rev["approval"] == "not-applicable" and rev["disposition"] != "not-applicable":
            errors.append(f"not-applicable finding {fid} must use not-applicable disposition")
        for result in rev["acceptance_results"]:
            for eid in result["evidence_ids"]:
                if eid not in evidence_by_id:
                    errors.append(f"finding {fid} acceptance result references unknown evidence {eid}")
            if result["status"] == "passed" and not _completed_evidence(evidence_by_id, result["evidence_ids"]):
                errors.append(f"finding {fid} passed acceptance criterion requires completed evidence")
        for eid in rev["evidence_ids"]:
            if eid not in evidence_by_id:
                errors.append(f"finding {fid} references unknown evidence {eid}")
        for cid in rev["change_ids"]:
            if cid not in change_by_id:
                errors.append(f"finding {fid} references unknown change {cid}")
        for pid in rev["perception_test_ids"]:
            if pid not in perception_by_id:
                errors.append(f"finding {fid} references unknown perception test {pid}")

    for fid, src in source_by_id.items():
        for dep in src["dependencies"]:
            if dep not in source_by_id:
                errors.append(f"canonical teardown finding {fid} references unknown dependency {dep}")
            elif dep in sequences and fid in sequences and sequences[dep] >= sequences[fid]:
                errors.append(f"finding dependency order invalid: {dep} must precede {fid}")

    source_claims = {row["id"]: row for row in teardown.get("claims", [])}
    if set(claim_by_id) != set(source_claims):
        missing = sorted(set(source_claims) - set(claim_by_id))
        extra = sorted(set(claim_by_id) - set(source_claims))
        if missing:
            errors.append(f"claim_trace missing canonical claim IDs: {missing}")
        if extra:
            errors.append(f"claim_trace contains unknown claim IDs: {extra}")
    for cid, src in source_claims.items():
        row = claim_by_id.get(cid)
        if row is None:
            continue
        for key in ("claim", "brand"):
            if row[key] != src[key]:
                errors.append(f"claim {cid} {key} must exactly match teardown")
        if row["source_state"] != src["state"]:
            errors.append(f"claim {cid} source_state must exactly match teardown")
        for fid in row["finding_ids"]:
            if fid not in source_by_id:
                errors.append(f"claim {cid} references unknown finding {fid}")
        for ch in row["change_ids"]:
            if ch not in change_by_id:
                errors.append(f"claim {cid} references unknown change {ch}")
        for eid in row["evidence_ids"]:
            if eid not in evidence_by_id:
                errors.append(f"claim {cid} references unknown evidence {eid}")
        if row["verification_status"] == "verified":
            if not _evidence_with_method(evidence_by_id, row["evidence_ids"], "claim-verification"):
                errors.append(f"claim {cid} cannot be verified in the revision without completed claim-verification evidence")
        if row["action"] in {"correct", "qualify", "remove"} and data["mode"] != "planning-only" and not row["change_ids"]:
            errors.append(f"implemented claim action {row['action']} for {cid} requires a mapped change")

    trace = data["coverage_trace"]
    coverage_specs = [
        ("access", "category", "status"),
        ("modules", "id", "status"),
        ("surface_checks", "id", "status"),
    ]
    for key, idkey, statuskey in coverage_specs:
        source_rows = {row[idkey]: row for row in coverage.get(key, [])}
        revision_rows = {row[idkey]: row for row in trace[key]}
        if set(source_rows) != set(revision_rows):
            errors.append(f"coverage_trace.{key} must account for every canonical teardown item exactly once")
        for rid, src in source_rows.items():
            rev = revision_rows.get(rid)
            if rev and rev["source_status"] != src[statuskey]:
                errors.append(f"coverage_trace.{key} {rid} source_status must match teardown")
            if rev:
                for eid in rev["evidence_ids"]:
                    if eid not in evidence_by_id:
                        errors.append(f"coverage_trace.{key} {rid} references unknown evidence {eid}")
    source_limits = {row["id"]: row for row in coverage.get("material_limitations", [])}
    revision_limits = {row["id"]: row for row in trace["material_limitations"]}
    if set(source_limits) != set(revision_limits):
        errors.append("coverage_trace.material_limitations must account for every canonical teardown limitation exactly once")
    for lid, src in source_limits.items():
        rev = revision_limits.get(lid)
        if not rev:
            continue
        if rev["description"] != src["description"] or rev["source_status"] != src["status"]:
            errors.append(f"material limitation {lid} description and source_status must match teardown")
        if src["status"] == "open" and rev["disposition"] == "resolved" and not _completed_evidence(evidence_by_id, rev["evidence_ids"]):
            errors.append(f"open teardown limitation {lid} cannot be resolved without completed evidence")

    for eid, row in evidence_by_id.items():
        if row["status"] == "completed" and (row.get("observation") is None or not str(row.get("observation")).strip()):
            errors.append(f"completed evidence {eid} requires a concrete observation")
        if row["status"] in {"failed", "blocked"} and not row["limitations"]:
            errors.append(f"{row['status']} evidence {eid} requires limitations")
        artifact = row.get("artifact_path")
        if artifact:
            p = Path(artifact)
            if p.is_absolute() or ".." in p.parts:
                errors.append(f"evidence {eid} artifact_path must be a safe relative path")
            else:
                full = revision_dir / p
                if not full.is_file():
                    errors.append(f"evidence {eid} artifact_path does not exist: {artifact}")

    for chid, row in change_by_id.items():
        if not row["finding_ids"] and not row["convergence_ids"]:
            errors.append(f"change {chid} must map to at least one finding or convergence finding")
        for fid in row["finding_ids"]:
            if fid not in finding_by_id:
                errors.append(f"change {chid} references unknown finding {fid}")
            elif finding_by_id[fid]["approval"] != "approved":
                errors.append(f"change {chid} maps to finding {fid} that is not approved")
        for rid in row["convergence_ids"]:
            if rid not in convergence_by_id:
                errors.append(f"change {chid} references unknown convergence finding {rid}")
        for auth in row["authority_ids"]:
            if auth not in authority_by_id:
                errors.append(f"change {chid} references unknown authority {auth}")
            elif authority_state.get(auth) != "authorized":
                errors.append(f"change {chid} requires authority {auth} to be authorized")
        required_auth = CHANGE_AUTHORITY.get(row["scope"])
        if required_auth and required_auth not in row["authority_ids"]:
            errors.append(f"change {chid} scope {row['scope']} requires authority {required_auth}")
        if row["risk_level"] == "high":
            rollout_id = row.get("rollout_id")
            if not rollout_id or rollout_id not in rollout_by_id:
                errors.append(f"high-risk change {chid} requires a valid rollout_id")
            elif chid not in rollout_by_id[rollout_id]["change_ids"]:
                errors.append(f"high-risk change {chid} rollout {rollout_id} must include the change")
        for eid in row["evidence_ids"]:
            if eid not in evidence_by_id:
                errors.append(f"change {chid} references unknown evidence {eid}")

    for rid, row in rollout_by_id.items():
        for chid in row["change_ids"]:
            if chid not in change_by_id:
                errors.append(f"rollout {rid} references unknown change {chid}")
        for auth in row["authority_ids"]:
            if auth not in authority_by_id:
                errors.append(f"rollout {rid} references unknown authority {auth}")
            elif row["state"] in {"activated", "verified"} and authority_state.get(auth) != "authorized":
                errors.append(f"rollout {rid} cannot be {row['state']} without authorized {auth}")
        if row["state"] in {"activated", "verified"} and not _completed_evidence(evidence_by_id, row["evidence_ids"]):
            errors.append(f"rollout {rid} state {row['state']} requires completed evidence")

    for pid, row in perception_by_id.items():
        for fid in row["finding_ids"]:
            if fid not in finding_by_id:
                errors.append(f"perception test {pid} references unknown finding {fid}")
        for eid in row["evidence_ids"]:
            if eid not in evidence_by_id:
                errors.append(f"perception test {pid} references unknown evidence {eid}")
        if row["status"] == "completed":
            if not row.get("result"):
                errors.append(f"completed perception test {pid} requires a result")
            if not _evidence_with_level(evidence_by_id, row["evidence_ids"], "audience-observation"):
                errors.append(f"completed perception test {pid} requires audience-observation evidence")

    for rid, row in convergence_by_id.items():
        for fid in row["reopened_finding_ids"]:
            if fid not in finding_by_id:
                errors.append(f"convergence finding {rid} reopens unknown finding {fid}")
        for cid in row["change_ids"]:
            if cid not in change_by_id:
                errors.append(f"convergence finding {rid} references unknown change {cid}")
        for eid in row["evidence_ids"]:
            if eid not in evidence_by_id:
                errors.append(f"convergence finding {rid} references unknown evidence {eid}")
        if row["status"] == "fixed":
            if not row["change_ids"]:
                errors.append(f"fixed convergence finding {rid} requires a mapped change")
            if not _completed_evidence(evidence_by_id, row["evidence_ids"]):
                errors.append(f"fixed convergence finding {rid} requires completed evidence")

    readiness = data["readiness"]
    blocking_convergence = [row for row in convergence_by_id.values() if row["severity"] in {"critical", "high", "medium"} and row["status"] in {"open", "deferred", "blocked"}]
    failed_approved = []
    preservation_incomplete = []
    for row in finding_by_id.values():
        if row["approval"] == "approved" and any(r["status"] == "failed" for r in row["acceptance_results"]):
            failed_approved.append(row["id"])
        if row["approval"] == "approved" and row["preservation_constraints"] and row["preservation_status"] in {"pending", "failed"}:
            preservation_incomplete.append(row["id"])

    if data["mode"] == "planning-only":
        if data["changes"]:
            errors.append("planning-only revision must not contain actual changes")
        if readiness["revision_status"] not in {"planned", "blocked"}:
            errors.append("planning-only revision_status must be planned or blocked")
        if readiness["review_convergence"] not in {"not-run", "blocked"}:
            errors.append("planning-only review_convergence must be not-run or blocked")
        if any(readiness[key] == "ready" for key in ("integration", "deployment", "publication")):
            errors.append("planning-only revision cannot claim ready integration, deployment, or publication")
        for key, row in readiness["delivery"].items():
            if row["state"] == "verified":
                errors.append(f"planning-only revision cannot claim verified delivery action {key}")

    if readiness["review_convergence"] == "passed":
        if blocking_convergence:
            errors.append("review_convergence cannot pass with open/deferred/blocked critical/high/medium convergence findings")
        if not _completed_evidence(evidence_by_id, readiness["convergence_evidence_ids"]):
            errors.append("passed review_convergence requires completed convergence evidence")

    if readiness["integration"] == "ready":
        if not data["workspace"]["existing_work_reconciled"]:
            errors.append("integration readiness requires existing_work_reconciled true")
        if readiness["review_convergence"] != "passed":
            errors.append("integration readiness requires passed review_convergence")
        if failed_approved:
            errors.append(f"integration readiness blocked by failed approved findings: {failed_approved}")
        if preservation_incomplete:
            errors.append(f"integration readiness blocked by unresolved preservation status: {preservation_incomplete}")
    if readiness["deployment"] == "ready" and readiness["integration"] != "ready":
        errors.append("deployment readiness requires integration ready")
    if readiness["publication"] == "ready":
        if readiness["deployment"] not in {"ready", "not-applicable"}:
            errors.append("publication readiness requires deployment ready or not-applicable")
        if authority_state.get("AUTH-PUBLISH") != "authorized":
            errors.append("publication readiness requires AUTH-PUBLISH authorized")

    if readiness["perception_validation"] in {"observed", "partially-observed"}:
        evidence_ids = [eid for row in perception_by_id.values() if row["status"] == "completed" for eid in row["evidence_ids"]]
        if not _evidence_with_level(evidence_by_id, evidence_ids, "audience-observation"):
            errors.append("observed perception_validation requires completed audience-observation evidence")
    if readiness["business_outcome"] == "observed":
        all_ids = list(evidence_by_id)
        if not _evidence_with_level(evidence_by_id, all_ids, "business-outcome"):
            errors.append("observed business_outcome requires completed business-outcome evidence")

    for key, row in readiness["delivery"].items():
        for eid in row["evidence_ids"]:
            if eid not in evidence_by_id:
                errors.append(f"delivery {key} references unknown evidence {eid}")
        if row["state"] == "verified":
            auth = DELIVERY_AUTHORITY[key]
            if authority_state.get(auth) != "authorized":
                errors.append(f"verified delivery {key} requires authority {auth} authorized")
            if not _completed_evidence(evidence_by_id, row["evidence_ids"]):
                errors.append(f"verified delivery {key} requires completed evidence")
            if key in {"deployed", "published", "social_profile_changes", "business_listing_changes"} and not any(
                evidence_by_id[eid]["level"] in {"published-channel", "first-party-measurement", "business-outcome"}
                for eid in row["evidence_ids"] if eid in evidence_by_id and evidence_by_id[eid]["status"] == "completed"
            ):
                errors.append(f"verified delivery {key} requires published-channel or higher evidence")

    if readiness["revision_status"] == "complete":
        approved = [row for row in finding_by_id.values() if row["approval"] == "approved"]
        for row in approved:
            if row["disposition"] in {"planned", "blocked", "investigating"}:
                errors.append(f"complete revision cannot leave approved finding {row['id']} in {row['disposition']} disposition")
            if any(result["status"] in {"pending", "failed", "blocked"} for result in row["acceptance_results"]):
                errors.append(f"complete revision cannot leave approved finding {row['id']} with incomplete acceptance results")
        if blocking_convergence:
            errors.append("complete revision cannot contain blocking convergence findings")

    _scan_placeholders(data, "revision", errors)

    if check_markdown:
        expected = render_all(data)
        for name in GENERATED_FILES:
            path = revision_dir / name
            if not path.is_file():
                errors.append(f"missing generated file: {name}")
                continue
            actual = path.read_text(encoding="utf-8")
            wanted = expected[name].rstrip() + "\n"
            if actual != wanted:
                errors.append(f"generated Markdown drift: {name} does not match revision.json")
