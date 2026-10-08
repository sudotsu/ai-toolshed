#!/usr/bin/env python3
"""Validate ux-ui-revision v2 against its exact validated teardown."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from validation_common import run_upstream_validator

AUTH = {
    "repository_edit",
    "design_file_edit",
    "cms_edit",
    "public_content_publish",
    "production_deploy",
    "external_profile_change",
    "analytics_mutation",
    "paid_purchase",
    "third_party_outreach",
    "merge",
}
EDIT_AUTHORITIES = {"repository_edit", "design_file_edit", "cms_edit"}
REVAL = {"confirmed", "changed", "stale", "already_resolved", "not_applicable", "blocked"}
APP = {"pending", "approved", "deferred", "rejected", "accepted_risk", "not_applicable"}
IMPL = {
    "not_started",
    "planned",
    "in_progress",
    "fixed",
    "preserved",
    "blocked",
    "deferred",
    "rejected",
    "accepted_risk",
    "not_applicable",
}
PRES = {"pending", "preserved", "regressed", "approved_tradeoff", "not_applicable"}
ACC = {"passed", "failed", "pending", "blocked", "not_applicable"}
LEVELS = [
    "source_inspection",
    "rendered_experience",
    "assistive_technology",
    "published_experience",
    "user_observation",
    "first_party_measurement",
    "business_outcome",
]
LEVEL_RANK = {name: index for index, name in enumerate(LEVELS)}
EXPERIENTIAL_PREFIXES = ("ui.", "ux.", "accessibility.", "competitive.")
BEHAVIORAL_BASES = {"first_party_measurement", "user_research", "user_sentiment"}
POST_CHANGE_BEHAVIOR_LEVELS = {"user_observation", "first_party_measurement", "business_outcome"}
TIMINGS = {"pre_change", "post_change"}


def obj(value):
    return isinstance(value, dict)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def enum_value(value, allowed):
    return isinstance(value, str) and value in allowed


def string_list(value):
    return [item for item in value if text(item)] if isinstance(value, list) else []


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name} cannot load: {exc}")
        return None


def validate_verification_evidence(fid: str, value, errors: list[str]):
    if not isinstance(value, list):
        errors.append(f"{fid}.verification_evidence must be list")
        return {}
    records = {}
    for index, record in enumerate(value):
        if not obj(record):
            errors.append(f"{fid}.verification_evidence[{index}] must be object")
            continue
        ref = record.get("ref")
        level = record.get("level")
        if not text(ref):
            errors.append(f"{fid}.verification_evidence[{index}].ref required")
            continue
        if ref in records:
            errors.append(f"{fid}.verification_evidence duplicate ref {ref}")
        if not enum_value(level, LEVEL_RANK):
            errors.append(f"{fid}.verification_evidence[{index}].level invalid")
        if "timing" in record and not enum_value(record.get("timing"), TIMINGS):
            errors.append(f"{fid}.verification_evidence[{index}].timing invalid")
        if "locator" in record and not text(record.get("locator")):
            errors.append(
                f"{fid}.verification_evidence[{index}].locator must be non-empty text when present"
            )
        records[ref] = record
    return records


def validate(td: Path, rvdir: Path, *, run_upstream=True):
    errors: list[str] = []
    if run_upstream:
        ok, message = run_upstream_validator(td)
        if not ok:
            return ["ux-ui-teardown upstream validation failed: " + str(message)[:2000]]

    src = load(td / "findings.json", errors)
    rv = load(rvdir / "revision.json", errors)
    if not obj(src) or not obj(rv):
        return errors or ["canonical documents must be objects"]

    if src.get("schema_version") != "ux-ui-teardown-v2":
        errors.append("upstream findings schema mismatch")
    if rv.get("schema_version") != "ux-ui-revision-v2":
        errors.append("revision schema_version must be ux-ui-revision-v2")
    if not enum_value(rv.get("mode"), {"planning-only", "implementation", "continuation"}):
        errors.append("revision mode invalid")

    source_meta = rv.get("source") if obj(rv.get("source")) else {}
    if not source_meta:
        errors.append("source must be object")
    else:
        if source_meta.get("teardown_findings_digest") != digest(td / "findings.json"):
            errors.append("source teardown digest mismatch")
        audit = src.get("audit") if obj(src.get("audit")) else {}
        if source_meta.get("teardown_revision") != audit.get("audited_revision"):
            errors.append("source teardown revision mismatch")

    baseline = rv.get("baseline") if obj(rv.get("baseline")) else {}
    if "baseline" in rv and not baseline:
        errors.append("baseline must be object")

    authority = rv.get("authority") if isinstance(rv.get("authority"), list) else []
    if not isinstance(rv.get("authority"), list):
        errors.append("authority must be list")
    authority_map = {}
    actions = []
    for index, row in enumerate(authority):
        if not obj(row):
            errors.append(f"authority[{index}] must be object")
            continue
        action = row.get("action")
        if not isinstance(action, str):
            errors.append(f"authority[{index}].action invalid")
            continue
        actions.append(action)
        authority_map[action] = row
        if action not in AUTH:
            errors.append(f"authority[{index}].action invalid")
        if not enum_value(row.get("status"), {"authorized", "not_authorized", "not_applicable"}):
            errors.append(f"authority[{index}].status invalid")
        if not isinstance(row.get("scope"), list) or not isinstance(row.get("evidence"), list):
            errors.append(f"authority[{index}] scope/evidence must be lists")
    if set(actions) != AUTH or len(actions) != len(AUTH):
        errors.append("authority must contain each action exactly once")
    if rv.get("mode") == "planning-only" and any(
        obj(row) and row.get("status") == "authorized" for row in authority
    ):
        errors.append("planning-only cannot authorize mutation actions")

    any_edit_authorized = any(
        authority_map.get(action, {}).get("status") == "authorized" for action in EDIT_AUTHORITIES
    )

    raw_source_findings = src.get("findings")
    source_rows = raw_source_findings if isinstance(raw_source_findings, list) else []
    if not isinstance(raw_source_findings, list):
        errors.append("upstream findings must be list")
    source_findings = {
        row["id"]: row for row in source_rows if obj(row) and text(row.get("id"))
    }

    rows = rv.get("findings") if isinstance(rv.get("findings"), list) else []
    if not isinstance(rv.get("findings"), list):
        errors.append("findings must be list")
    revision_map = {}

    for index, row in enumerate(rows):
        if not obj(row):
            errors.append(f"findings[{index}] must be object")
            continue
        fid = row.get("finding_id")
        if not text(fid):
            errors.append(f"findings[{index}].finding_id invalid")
            continue
        if fid in revision_map:
            errors.append(f"duplicate revision finding {fid}")
        revision_map[fid] = row
        source = source_findings.get(fid)
        if not source:
            errors.append(f"unknown finding {fid}")
            continue

        if row.get("original_status") != source.get("status"):
            errors.append(f"{fid} original_status mismatch")
        if not enum_value(row.get("revalidation"), REVAL):
            errors.append(f"{fid}.revalidation invalid")
        if not enum_value(row.get("approval"), APP):
            errors.append(f"{fid}.approval invalid")
        if not enum_value(row.get("implementation_status"), IMPL):
            errors.append(f"{fid}.implementation_status invalid")
        if not enum_value(row.get("preservation_status"), PRES):
            errors.append(f"{fid}.preservation_status invalid")

        for key in ["current_evidence", "changed_targets", "acceptance_results"]:
            if not isinstance(row.get(key), list):
                errors.append(f"{fid}.{key} must be list")

        changed_targets = string_list(row.get("changed_targets"))
        if isinstance(row.get("changed_targets"), list) and len(changed_targets) != len(
            row.get("changed_targets", [])
        ):
            errors.append(f"{fid}.changed_targets must be string list")

        changed_target_actions_raw = row.get("changed_target_actions", {})
        if not obj(changed_target_actions_raw):
            errors.append(f"{fid}.changed_target_actions must be object")
            changed_target_actions = {}
        else:
            changed_target_actions = changed_target_actions_raw
        if set(changed_target_actions) != set(changed_targets):
            errors.append(f"{fid}.changed_target_actions must map every changed target exactly once")
        for target, action in changed_target_actions.items():
            if not text(target) or not enum_value(action, EDIT_AUTHORITIES):
                errors.append(f"{fid}.changed_target_actions[{target!r}] invalid")
                continue
            if authority_map.get(action, {}).get("status") != "authorized":
                errors.append(f"{fid} changed target {target} requires authorized {action}")

        claims_edit_work = (
            enum_value(row.get("implementation_status"), {"in_progress", "fixed"})
            and row.get("revalidation") != "already_resolved"
        )
        if claims_edit_work and not changed_targets and not any_edit_authorized:
            errors.append(
                f"{fid} implementation work requires authorized repository/design/CMS edit authority"
            )

        if enum_value(row.get("revalidation"), {"confirmed", "changed", "already_resolved"}) and not row.get(
            "current_evidence"
        ):
            errors.append(f"{fid} revalidation requires current evidence")
        if enum_value(row.get("revalidation"), {"stale", "not_applicable"}) and row.get(
            "implementation_status"
        ) == "fixed":
            errors.append(f"{fid} stale/not_applicable cannot be fixed")

        verification = validate_verification_evidence(fid, row.get("verification_evidence"), errors)
        results = row.get("acceptance_results") if isinstance(row.get("acceptance_results"), list) else []
        criteria = [item.get("criterion") for item in results if obj(item) and text(item.get("criterion"))]
        raw_source_criteria = source.get("acceptance_criteria")
        source_criteria = string_list(raw_source_criteria)
        if not isinstance(raw_source_criteria, list) or len(source_criteria) != len(raw_source_criteria):
            errors.append(f"{fid} source acceptance_criteria must be string list")
        if Counter(criteria) != Counter(source_criteria) or len(criteria) != len(results):
            errors.append(f"{fid} acceptance_results must cover every source criterion exactly once")

        for result_index, result in enumerate(results):
            if (
                not obj(result)
                or not enum_value(result.get("status"), ACC)
                or not isinstance(result.get("evidence"), list)
            ):
                errors.append(f"{fid}.acceptance_results[{result_index}] invalid")
                continue
            evidence_refs = string_list(result.get("evidence"))
            if len(evidence_refs) != len(result.get("evidence", [])):
                errors.append(f"{fid}.acceptance_results[{result_index}].evidence must be string list")
            if result.get("status") == "passed" and not evidence_refs:
                errors.append(f"{fid}.acceptance_results[{result_index}] passed requires evidence")
            for evidence_ref in evidence_refs:
                if evidence_ref not in verification:
                    errors.append(
                        f"{fid}.acceptance_results[{result_index}] references unknown verification evidence {evidence_ref}"
                    )

        if row.get("implementation_status") == "fixed":
            if row.get("approval") != "approved":
                errors.append(f"{fid} fixed requires approved")
            if not enum_value(row.get("revalidation"), {"confirmed", "changed", "already_resolved"}):
                errors.append(f"{fid} fixed requires terminal current-state revalidation")
            if any(
                not obj(item) or not enum_value(item.get("status"), {"passed", "not_applicable"})
                for item in results
            ):
                errors.append(f"{fid} fixed has unmet acceptance criterion")
            if not verification:
                errors.append(f"{fid} fixed requires verification evidence")

            domains = string_list(source.get("domains"))
            experiential = any(domain.startswith(EXPERIENTIAL_PREFIXES) for domain in domains)
            linked_refs = {
                evidence_ref
                for result in results
                if obj(result) and result.get("status") == "passed"
                for evidence_ref in string_list(result.get("evidence"))
            }
            linked_levels = [
                LEVEL_RANK.get(verification[ref].get("level"), -1)
                for ref in linked_refs
                if ref in verification and isinstance(verification[ref].get("level"), str)
            ]
            if experiential and not any(
                level >= LEVEL_RANK["rendered_experience"] for level in linked_levels
            ):
                errors.append(
                    f"{fid} fixed experiential finding requires rendered_experience-or-higher acceptance evidence"
                )

            if source.get("judgment_basis") in BEHAVIORAL_BASES:
                post_change_behavior = any(
                    ref in verification
                    and verification[ref].get("level") in POST_CHANGE_BEHAVIOR_LEVELS
                    and verification[ref].get("timing") == "post_change"
                    for ref in linked_refs
                )
                if not post_change_behavior:
                    errors.append(
                        f"{fid} fixed behavioral/user finding requires post-change acceptance-linked behavioral evidence"
                    )

        if row.get("implementation_status") == "accepted_risk" and row.get("approval") != "accepted_risk":
            errors.append(f"{fid} accepted_risk requires accepted_risk approval")

        if rv.get("mode") == "planning-only":
            if row.get("changed_targets"):
                errors.append(f"{fid} planning-only cannot record changed targets")
            if enum_value(row.get("implementation_status"), {"in_progress", "fixed"}):
                errors.append(f"{fid} planning-only cannot claim implementation work")

        if source.get("kind") == "strength":
            strength_ok = row.get("implementation_status") == "preserved" or (
                row.get("preservation_status") == "approved_tradeoff"
                and row.get("approval") == "approved"
            )
            if not strength_ok:
                errors.append(f"{fid} retained strength must stay preserved or have approved tradeoff")
        if row.get("preservation_status") == "approved_tradeoff" and row.get("approval") != "approved":
            errors.append(f"{fid} approved_tradeoff requires approved")

    if set(revision_map) != set(source_findings):
        errors.append("revision must contain every teardown finding exactly once")

    decisions = rv.get("decisions") if isinstance(rv.get("decisions"), list) else []
    if not isinstance(rv.get("decisions"), list):
        errors.append("decisions must be list")
    decision_map = {}
    decision_links = {fid: [] for fid in source_findings}
    for index, decision in enumerate(decisions):
        if not obj(decision):
            errors.append(f"decisions[{index}] must be object")
            continue
        did = decision.get("id")
        if not isinstance(did, str) or not re.match(r"^DEC-\d{3}$", did):
            errors.append(f"decisions[{index}].id invalid")
            continue
        if did in decision_map:
            errors.append(f"duplicate decision {did}")
        decision_map[did] = decision
        finding_ids = decision.get("finding_ids") if isinstance(decision.get("finding_ids"), list) else []
        if not finding_ids or not all(
            isinstance(item, str) and item in source_findings for item in finding_ids
        ):
            errors.append(f"{did}.finding_ids invalid")
        for linked_fid in finding_ids:
            if isinstance(linked_fid, str) and linked_fid in decision_links:
                decision_links[linked_fid].append(decision)
        if (
            not text(decision.get("question"))
            or not isinstance(decision.get("options"), list)
            or not decision.get("options")
            or not all(text(item) for item in decision.get("options", []))
        ):
            errors.append(f"{did} question/options invalid")
        if not text(decision.get("recommendation")):
            errors.append(f"{did}.recommendation required")
        if not enum_value(decision.get("status"), {"pending", "resolved", "deferred"}):
            errors.append(f"{did}.status invalid")
        if not isinstance(decision.get("owner_evidence"), list):
            errors.append(f"{did}.owner_evidence must be list")
        if decision.get("status") == "resolved" and not decision.get("owner_evidence"):
            errors.append(f"{did} resolved requires owner evidence")

    for fid, source in source_findings.items():
        if source.get("status") == "decision_required":
            links = decision_links.get(fid, [])
            if not links:
                errors.append(f"{fid} decision_required finding needs linked decision")
            row = revision_map.get(fid, {})
            if row.get("implementation_status") == "fixed" and not any(
                decision.get("status") == "resolved" and decision.get("owner_evidence")
                for decision in links
            ):
                errors.append(f"{fid} fixed decision_required finding needs resolved owner decision")

    convergence = rv.get("convergence") if obj(rv.get("convergence")) else {}
    open_material = []
    if not convergence:
        errors.append("convergence must be object")
    else:
        if not enum_value(convergence.get("status"), {"not_started", "in_progress", "converged", "blocked"}):
            errors.append("convergence.status invalid")
        if convergence.get("status") == "converged":
            reviewed_revision = convergence.get("reviewed_revision")
            if not text(reviewed_revision) or reviewed_revision == "unrecorded":
                errors.append("converged requires concrete convergence.reviewed_revision")
        seen = set()
        items = convergence.get("findings") if isinstance(convergence.get("findings"), list) else []
        for index, item in enumerate(items):
            if not obj(item):
                errors.append(f"convergence.findings[{index}] must be object")
                continue
            cid = item.get("id")
            if not isinstance(cid, str) or not re.match(r"^REVUX-\d{3}$", cid):
                errors.append(f"convergence.findings[{index}].id invalid")
                continue
            if cid in seen:
                errors.append(f"duplicate convergence {cid}")
            seen.add(cid)
            if not enum_value(item.get("severity"), {"critical", "high", "medium", "low", "informational"}):
                errors.append(f"{cid}.severity invalid")
            if not enum_value(item.get("status"), {"open", "fixed", "accepted_risk", "not_applicable"}):
                errors.append(f"{cid}.status invalid")
            if item.get("status") == "open" and enum_value(
                item.get("severity"), {"critical", "high", "medium"}
            ):
                open_material.append(cid)

    readiness = rv.get("readiness") if obj(rv.get("readiness")) else {}
    if not readiness:
        errors.append("readiness must be object")
    else:
        if not enum_value(readiness.get("highest_evidence_level"), LEVEL_RANK):
            errors.append("readiness.highest_evidence_level invalid")
        if not enum_value(readiness.get("implementation"), {"not_started", "in_progress", "ready", "blocked"}):
            errors.append("readiness.implementation invalid")
        if not enum_value(readiness.get("integration"), {"not_started", "in_progress", "ready", "blocked"}):
            errors.append("readiness.integration invalid")
        if not enum_value(readiness.get("deployment"), {"not_performed", "performed", "blocked", "not_applicable"}):
            errors.append("readiness.deployment invalid")
        if not enum_value(readiness.get("publication"), {"not_performed", "performed", "blocked", "not_applicable"}):
            errors.append("readiness.publication invalid")
        if not enum_value(readiness.get("overall"), {"planned", "not_ready", "ready", "blocked"}):
            errors.append("readiness.overall invalid")
        if readiness.get("deployment") == "performed" and authority_map.get("production_deploy", {}).get(
            "status"
        ) != "authorized":
            errors.append("deployment performed without production_deploy authority")
        if readiness.get("publication") == "performed" and authority_map.get("public_content_publish", {}).get(
            "status"
        ) != "authorized":
            errors.append("publication performed without public_content_publish authority")
        if rv.get("mode") == "planning-only" and (
            readiness.get("deployment") == "performed" or readiness.get("publication") == "performed"
        ):
            errors.append("planning-only cannot claim deployment or publication")

        if readiness.get("overall") == "ready":
            if readiness.get("implementation") != "ready" or readiness.get("integration") != "ready":
                errors.append("overall ready requires implementation/integration ready")
            if convergence.get("status") != "converged":
                errors.append("overall ready requires convergence.status converged")
            reviewed_revision = convergence.get("reviewed_revision")
            if not text(reviewed_revision) or reviewed_revision == "unrecorded":
                errors.append("overall ready requires concrete convergence.reviewed_revision")
            current_revision = baseline.get("current_revision")
            if not text(current_revision) or current_revision == "unrecorded":
                errors.append("overall ready requires concrete baseline.current_revision")
            elif text(reviewed_revision) and reviewed_revision != current_revision:
                errors.append("overall ready convergence.reviewed_revision is stale")
            if open_material:
                errors.append(f"overall ready has open material convergence findings: {open_material}")
            for fid, row in revision_map.items():
                source = source_findings.get(fid)
                if not source:
                    continue
                if enum_value(row.get("revalidation"), {"blocked", "stale"}):
                    errors.append(f"overall ready has unrevalidated finding {fid}")
                if enum_value(row.get("implementation_status"), {"not_started", "planned", "in_progress", "blocked"}):
                    errors.append(f"overall ready has incomplete finding {fid}")
                if not enum_value(
                    row.get("preservation_status"), {"preserved", "approved_tradeoff", "not_applicable"}
                ):
                    errors.append(f"overall ready has unresolved preservation status for {fid}")
                if (
                    enum_value(source.get("status"), {"open", "decision_required"})
                    and enum_value(source.get("severity"), {"critical", "high", "medium"})
                    and not enum_value(row.get("approval"), {"approved", "deferred", "rejected", "accepted_risk"})
                ):
                    errors.append(f"overall ready has no terminal disposition for material finding {fid}")
                if (
                    source.get("status") == "decision_required"
                    and not enum_value(
                        row.get("implementation_status"),
                        {"deferred", "rejected", "accepted_risk", "not_applicable"},
                    )
                    and not any(
                        decision.get("status") == "resolved" for decision in decision_links.get(fid, [])
                    )
                ):
                    errors.append(f"overall ready has unresolved owner decision for {fid}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown", type=Path)
    parser.add_argument("revision", type=Path)
    args = parser.parse_args()
    errors = validate(args.teardown.resolve(), args.revision.resolve())
    if errors:
        print(f"UX/UI revision validation failed with {len(errors)} error(s):")
        for error in errors[:150]:
            print("-", error)
        return 1
    print("ux-ui-revision validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
