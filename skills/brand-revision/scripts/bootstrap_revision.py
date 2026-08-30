#!/usr/bin/env python3
"""Create a total-coverage planning scaffold from a validated brand-teardown handoff."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from render_revision import render_to_disk
from validation_common import AUTHORITY_IDS, DELIVERY_KEYS, load_json, run_upstream_validator, utc_now


def _option(option_id: str, label: str, consequences: str, prerequisites: list[str], reversibility: str) -> dict[str, Any]:
    return {
        "id": option_id,
        "label": label,
        "consequences": consequences,
        "prerequisites": prerequisites,
        "reversibility": reversibility,
    }


def _decision_for(finding: dict[str, Any], number: int) -> dict[str, Any]:
    impl = finding.get("implementation", {}) if isinstance(finding.get("implementation"), dict) else {}
    priority = finding.get("priority", {}) if isinstance(finding.get("priority"), dict) else {}
    owner_decision = finding.get("owner_decision")
    owner_actions = impl.get("owner_or_external_actions", []) if isinstance(impl.get("owner_or_external_actions"), list) else []
    blocked = finding.get("status") == "blocked"
    question = owner_decision if isinstance(owner_decision, str) and owner_decision.strip() else (
        "Resolve the blocked owner or external prerequisite before this finding can proceed: " + "; ".join(str(x) for x in owner_actions)
    )
    category = "external-authority" if blocked else (
        "brand-architecture" if finding.get("module") == "brand_architecture" else "other"
    )
    recommendation = finding.get("recommendation") if isinstance(finding.get("recommendation"), str) else "Preserve current state until the owner selects an option."
    reversibility = priority.get("reversibility") if isinstance(priority.get("reversibility"), str) else "unknown"
    deps = finding.get("dependencies") if isinstance(finding.get("dependencies"), list) else []
    return {
        "id": f"DEC-{number:03d}",
        "finding_ids": [finding["id"]],
        "category": category,
        "status": "blocked" if blocked else "pending",
        "question": question,
        "options": [
            _option("OPT-A", "Approve the recommended direction", recommendation, list(deps), reversibility),
            _option("OPT-B", "Keep the current state", "No brand mutation occurs for this decision branch; dependent work remains blocked or deferred.", [], "easy"),
        ],
        "recommendation": recommendation,
        "owner_selection": None,
        "safe_default": "OPT-B",
        "consequences": "Dependent brand changes must not execute until this decision is resolved.",
        "prerequisites": list(deps) + [str(x) for x in owner_actions],
        "reversibility": reversibility,
        "evidence_ids": [],
    }


def build_scaffold(
    teardown_dir: Path,
    revision_dir: Path,
    findings_doc: dict[str, Any],
    coverage_doc: dict[str, Any],
    *,
    validator_result: str = "passed",
) -> dict[str, Any]:
    audit = findings_doc["audit"]
    source_findings = findings_doc["findings"]
    claims = findings_doc.get("claims", [])

    decisions: list[dict[str, Any]] = []
    for finding in source_findings:
        impl = finding.get("implementation", {}) if isinstance(finding.get("implementation"), dict) else {}
        owner_actions = impl.get("owner_or_external_actions", []) if isinstance(impl.get("owner_or_external_actions"), list) else []
        if finding.get("status") == "decision_required" or (finding.get("status") == "blocked" and owner_actions):
            decisions.append(_decision_for(finding, len(decisions) + 1))

    revision_findings: list[dict[str, Any]] = []
    for finding in source_findings:
        status = finding["status"]
        if status == "retained_strength":
            approval, disposition = "approved", "preserved"
            reason = "Retained strength is a preservation requirement; current-state verification remains pending."
        elif status == "not_applicable":
            approval, disposition = "not-applicable", "not-applicable"
            reason = "Canonical teardown marks this finding not applicable."
        elif status == "blocked":
            approval, disposition = "pending", "blocked"
            reason = finding.get("blocker") or "Canonical teardown records a blocker that must be resolved before implementation."
        else:
            approval, disposition = "pending", "planned"
            reason = "Owner approval and current-state revalidation are pending."
        acceptance = []
        for criterion in finding.get("acceptance_criteria", []):
            acceptance.append({
                "criterion": criterion,
                "status": "pending",
                "evidence_ids": [],
                "observation": "Current-state verification has not yet been completed for this criterion.",
            })
        preservation = list(finding.get("preservation_constraints", []))
        revision_findings.append({
            "id": finding["id"],
            "title": finding["title"],
            "source_status": status,
            "approval": approval,
            "revalidation": "pending",
            "disposition": disposition,
            "sequence": finding["implementation"]["order"],
            "dependencies": list(finding.get("dependencies", [])),
            "reason": reason,
            "acceptance_results": acceptance,
            "evidence_ids": [],
            "change_ids": [],
            "perception_test_ids": [],
            "preservation_constraints": preservation,
            "preservation_status": "pending" if preservation else "not-applicable",
            "completion_gates": list(finding["implementation"].get("owner_or_external_actions", [])) or ["Revalidate current state and satisfy every applicable original acceptance criterion."],
            "notes": "Bootstrap scaffold only; replace pending states with current evidence before implementation.",
        })

    claim_trace = [{
        "id": claim["id"],
        "claim": claim["claim"],
        "brand": claim["brand"],
        "source_state": claim["state"],
        "action": "pending",
        "target_state": claim["state"],
        "finding_ids": [],
        "change_ids": [],
        "evidence_ids": [],
        "verification_status": "pending",
        "notes": "Reconcile this canonical teardown claim against current state before changing or preserving it.",
    } for claim in claims]

    access_trace = [{
        "category": row["category"],
        "source_status": row["status"],
        "disposition": "pending",
        "completion_gate": row.get("next_step") or "Reassess current access and preserve any unresolved limitation.",
        "evidence_ids": [],
    } for row in coverage_doc.get("access", [])]
    module_trace = [{
        "id": row["id"],
        "source_status": row["status"],
        "disposition": "pending",
        "completion_gate": row.get("next_step") or "Reassess current module state after approved changes.",
        "evidence_ids": [],
    } for row in coverage_doc.get("modules", [])]
    check_trace = [{
        "id": row["id"],
        "source_status": row["status"],
        "disposition": "pending",
        "completion_gate": "Re-run or explicitly preserve this teardown surface check after relevant revision work.",
        "evidence_ids": [],
    } for row in coverage_doc.get("surface_checks", [])]
    limitation_trace = [{
        "id": row["id"],
        "description": row["description"],
        "source_status": row["status"],
        "disposition": "open" if row["status"] == "open" else "resolved",
        "completion_gate": row["completion_requirement"],
        "evidence_ids": [],
    } for row in coverage_doc.get("material_limitations", [])]

    authority = [{
        "id": auth_id,
        "state": "not-authorized",
        "scope": "No authority recorded in bootstrap scaffold.",
        "evidence_ids": [],
        "limitations": ["Owner authorization has not yet been recorded for this action class."],
    } for auth_id in AUTHORITY_IDS]

    delivery = {key: {"state": "not-performed", "evidence_ids": [], "observation": "No delivery action performed in planning scaffold."} for key in DELIVERY_KEYS}

    try:
        relative_teardown = os.path.relpath(teardown_dir.resolve(), revision_dir.resolve())
    except ValueError:
        relative_teardown = str(teardown_dir.resolve())

    return {
        "schema_version": "brand-revision-v1",
        "mode": "planning-only",
        "project": {
            "name": audit["project_name"],
            "locator": audit["project_locator"],
            "production_locator": audit.get("production_locator"),
        },
        "generated_at": utc_now(),
        "teardown": {
            "path": relative_teardown,
            "findings_schema": findings_doc["schema_version"],
            "coverage_schema": coverage_doc["schema_version"],
            "audited_revision": audit["audited_revision"],
            "review_status": audit["review_status"],
            "validator_command": "python3 <brand-teardown-skill>/scripts/validate_brand_teardown.py <brand-teardown-directory>",
            "validator_result": validator_result,
        },
        "workspace": {
            "implementation_start_revision": audit["audited_revision"],
            "product_endpoint": audit["audited_revision"],
            "endpoint_kind": "immutable-revision",
            "artifact_relationship": "working-tree",
            "existing_work_reconciled": False,
            "staged_paths": [],
            "unstaged_paths": [],
            "untracked_paths": [],
            "baseline_evidence_ids": [],
        },
        "decisions": decisions,
        "authority_matrix": authority,
        "findings": revision_findings,
        "claim_trace": claim_trace,
        "coverage_trace": {
            "access": access_trace,
            "modules": module_trace,
            "surface_checks": check_trace,
            "material_limitations": limitation_trace,
        },
        "changes": [],
        "evidence": [],
        "perception_tests": [],
        "convergence_findings": [],
        "rollouts": [],
        "readiness": {
            "revision_status": "planned",
            "review_convergence": "not-run",
            "integration": "not-ready",
            "deployment": "not-ready",
            "publication": "not-ready",
            "perception_validation": "not-started",
            "business_outcome": "unverified",
            "authorization_summary": "partial",
            "convergence_evidence_ids": [],
            "delivery": delivery,
            "unverified_outcomes": [
                "Audience comprehension, trust, differentiation, recognition, preference, and action clarity are not proven by planning or implementation alone.",
                "Conversion, qualified pipeline, completed work, and revenue effects remain unverified without first-party or business-outcome evidence.",
            ],
            "follow_up_actions": [
                "Revalidate every teardown finding against current source, production, and applicable channels.",
                "Resolve owner decisions and record exact authority before executing dependent changes.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown_directory", type=Path)
    parser.add_argument("revision_directory", type=Path)
    parser.add_argument("--skip-upstream-validation", action="store_true", help="Isolated tests only; never use for a production revision handoff.")
    args = parser.parse_args()
    teardown = args.teardown_directory.resolve()
    revision = args.revision_directory.resolve()

    if not args.skip_upstream_validation:
        ok, output = run_upstream_validator(teardown)
        if not ok:
            print("brand-teardown validation failed or could not run:")
            print(output)
            return 2

    findings, errors = load_json(teardown / "findings.json")
    coverage, more = load_json(teardown / "coverage.json")
    errors.extend(more)
    if errors:
        for error in errors:
            print(error)
        return 2
    if not isinstance(findings, dict) or findings.get("schema_version") != "brand-teardown-v1":
        print("findings.json must use brand-teardown-v1")
        return 2
    if not isinstance(coverage, dict) or coverage.get("schema_version") != "brand-teardown-coverage-v1":
        print("coverage.json must use brand-teardown-coverage-v1")
        return 2

    revision.mkdir(parents=True, exist_ok=True)
    (revision / "evidence").mkdir(exist_ok=True)
    data = build_scaffold(
        teardown, revision, findings, coverage,
        validator_result="skipped-for-isolated-test" if args.skip_upstream_validation else "passed",
    )
    (revision / "revision.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    render_to_disk(revision)
    print(f"Created brand-revision planning scaffold at {revision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
