#!/usr/bin/env python3
"""Structural shape validation for canonical brand-revision state."""
from __future__ import annotations

from typing import Any

from validator_common import (
    ACCEPTANCE_STATES, APPROVALS, AUTHORITY_STATES, AUTH_SUMMARY, BUSINESS_READINESS,
    CHANGE_SCOPES, CLAIM_ACTIONS, CLAIM_STATES, CLAIM_VERIFY_STATES, CONVERGENCE_READINESS,
    CONVERGENCE_SEVERITIES, CONVERGENCE_STATES, DECISION_CATEGORIES, DELIVERY_KEYS,
    DELIVERY_STATES, DISPOSITIONS, EVIDENCE_LEVELS, EVIDENCE_METHODS, EVIDENCE_STATES,
    PERCEPTION_DIMENSIONS, PERCEPTION_READINESS, PERCEPTION_STATES, PRESERVATION_STATES,
    READY_STATES, REQUIRED_TOP, REVALIDATIONS, REVISION_STATUSES, RISK_CATEGORIES,
    RISK_LEVELS, ROLLOUT_STATES, _arr, _bool, _enum, _int, _obj, _required, _str, _str_list,
)

def _shape_revision(data: Any, errors: list[str]) -> bool:
    root = _obj(data, "revision.json", errors)
    if root is None:
        return False
    _required(root, REQUIRED_TOP, "revision.json", errors, exact=True)
    if errors:
        return False
    _str(root.get("schema_version"), "revision.schema_version", errors)
    _enum(root.get("mode"), {"planning-only", "implementation", "continuation"}, "revision.mode", errors)
    _str(root.get("generated_at"), "revision.generated_at", errors)

    project = _obj(root.get("project"), "revision.project", errors)
    if project is not None:
        _required(project, {"name", "locator", "production_locator"}, "revision.project", errors, exact=True)
        _str(project.get("name"), "revision.project.name", errors)
        _str(project.get("locator"), "revision.project.locator", errors)
        if project.get("production_locator") is not None:
            _str(project.get("production_locator"), "revision.project.production_locator", errors, nullable=True)

    teardown = _obj(root.get("teardown"), "revision.teardown", errors)
    if teardown is not None:
        keys = {"path", "findings_schema", "coverage_schema", "audited_revision", "review_status", "validator_command", "validator_result"}
        _required(teardown, keys, "revision.teardown", errors, exact=True)
        for key in keys:
            _str(teardown.get(key), f"revision.teardown.{key}", errors)

    workspace = _obj(root.get("workspace"), "revision.workspace", errors)
    if workspace is not None:
        keys = {"implementation_start_revision", "product_endpoint", "endpoint_kind", "artifact_relationship", "existing_work_reconciled", "staged_paths", "unstaged_paths", "untracked_paths", "baseline_evidence_ids"}
        _required(workspace, keys, "revision.workspace", errors, exact=True)
        _str(workspace.get("implementation_start_revision"), "revision.workspace.implementation_start_revision", errors)
        _str(workspace.get("product_endpoint"), "revision.workspace.product_endpoint", errors)
        _enum(workspace.get("endpoint_kind"), {"immutable-revision", "working-tree"}, "revision.workspace.endpoint_kind", errors)
        _enum(workspace.get("artifact_relationship"), {"working-tree", "artifact-only-descendant"}, "revision.workspace.artifact_relationship", errors)
        _bool(workspace.get("existing_work_reconciled"), "revision.workspace.existing_work_reconciled", errors)
        for key in ("staged_paths", "unstaged_paths", "untracked_paths", "baseline_evidence_ids"):
            _str_list(workspace.get(key), f"revision.workspace.{key}", errors)

    decisions = _arr(root.get("decisions"), "revision.decisions", errors)
    if decisions is not None:
        for i, row in enumerate(decisions):
            item = _obj(row, f"revision.decisions[{i}]", errors)
            if item is None:
                continue
            keys = {"id", "finding_ids", "category", "status", "question", "options", "recommendation", "owner_selection", "safe_default", "consequences", "prerequisites", "reversibility", "evidence_ids"}
            _required(item, keys, f"revision.decisions[{i}]", errors, exact=True)
            _str(item.get("id"), f"revision.decisions[{i}].id", errors)
            _str_list(item.get("finding_ids"), f"revision.decisions[{i}].finding_ids", errors, allow_empty=False)
            _enum(item.get("category"), DECISION_CATEGORIES, f"revision.decisions[{i}].category", errors)
            _enum(item.get("status"), {"pending", "resolved", "blocked"}, f"revision.decisions[{i}].status", errors)
            for key in ("question", "recommendation", "safe_default", "consequences", "reversibility"):
                _str(item.get(key), f"revision.decisions[{i}].{key}", errors)
            if item.get("owner_selection") is not None:
                _str(item.get("owner_selection"), f"revision.decisions[{i}].owner_selection", errors, nullable=True)
            _str_list(item.get("prerequisites"), f"revision.decisions[{i}].prerequisites", errors)
            _str_list(item.get("evidence_ids"), f"revision.decisions[{i}].evidence_ids", errors)
            options = _arr(item.get("options"), f"revision.decisions[{i}].options", errors)
            if options is not None:
                if not options:
                    errors.append(f"revision.decisions[{i}].options must not be empty")
                for j, opt in enumerate(options):
                    o = _obj(opt, f"revision.decisions[{i}].options[{j}]", errors)
                    if o is None:
                        continue
                    _required(o, {"id", "label", "consequences", "prerequisites", "reversibility"}, f"revision.decisions[{i}].options[{j}]", errors, exact=True)
                    for key in ("id", "label", "consequences", "reversibility"):
                        _str(o.get(key), f"revision.decisions[{i}].options[{j}].{key}", errors)
                    _str_list(o.get("prerequisites"), f"revision.decisions[{i}].options[{j}].prerequisites", errors)

    authority = _arr(root.get("authority_matrix"), "revision.authority_matrix", errors)
    if authority is not None:
        for i, row in enumerate(authority):
            item = _obj(row, f"revision.authority_matrix[{i}]", errors)
            if item is None:
                continue
            _required(item, {"id", "state", "scope", "evidence_ids", "limitations"}, f"revision.authority_matrix[{i}]", errors, exact=True)
            _str(item.get("id"), f"revision.authority_matrix[{i}].id", errors)
            _enum(item.get("state"), AUTHORITY_STATES, f"revision.authority_matrix[{i}].state", errors)
            _str(item.get("scope"), f"revision.authority_matrix[{i}].scope", errors)
            _str_list(item.get("evidence_ids"), f"revision.authority_matrix[{i}].evidence_ids", errors)
            _str_list(item.get("limitations"), f"revision.authority_matrix[{i}].limitations", errors)

    findings = _arr(root.get("findings"), "revision.findings", errors)
    if findings is not None:
        for i, row in enumerate(findings):
            item = _obj(row, f"revision.findings[{i}]", errors)
            if item is None:
                continue
            keys = {"id", "title", "source_status", "approval", "revalidation", "disposition", "sequence", "dependencies", "reason", "acceptance_results", "evidence_ids", "change_ids", "perception_test_ids", "preservation_constraints", "preservation_status", "completion_gates", "notes"}
            _required(item, keys, f"revision.findings[{i}]", errors, exact=True)
            for key in ("id", "title", "source_status", "reason", "notes"):
                _str(item.get(key), f"revision.findings[{i}].{key}", errors)
            _enum(item.get("approval"), APPROVALS, f"revision.findings[{i}].approval", errors)
            _enum(item.get("revalidation"), REVALIDATIONS, f"revision.findings[{i}].revalidation", errors)
            _enum(item.get("disposition"), DISPOSITIONS, f"revision.findings[{i}].disposition", errors)
            _int(item.get("sequence"), f"revision.findings[{i}].sequence", errors, positive=True)
            for key in ("dependencies", "evidence_ids", "change_ids", "perception_test_ids", "preservation_constraints", "completion_gates"):
                _str_list(item.get(key), f"revision.findings[{i}].{key}", errors)
            _enum(item.get("preservation_status"), PRESERVATION_STATES, f"revision.findings[{i}].preservation_status", errors)
            results = _arr(item.get("acceptance_results"), f"revision.findings[{i}].acceptance_results", errors)
            if results is not None:
                if not results:
                    errors.append(f"revision.findings[{i}].acceptance_results must not be empty")
                for j, res in enumerate(results):
                    r = _obj(res, f"revision.findings[{i}].acceptance_results[{j}]", errors)
                    if r is None:
                        continue
                    _required(r, {"criterion", "status", "evidence_ids", "observation"}, f"revision.findings[{i}].acceptance_results[{j}]", errors, exact=True)
                    _str(r.get("criterion"), f"revision.findings[{i}].acceptance_results[{j}].criterion", errors)
                    _enum(r.get("status"), ACCEPTANCE_STATES, f"revision.findings[{i}].acceptance_results[{j}].status", errors)
                    _str_list(r.get("evidence_ids"), f"revision.findings[{i}].acceptance_results[{j}].evidence_ids", errors)
                    _str(r.get("observation"), f"revision.findings[{i}].acceptance_results[{j}].observation", errors)

    claims = _arr(root.get("claim_trace"), "revision.claim_trace", errors)
    if claims is not None:
        for i, row in enumerate(claims):
            item = _obj(row, f"revision.claim_trace[{i}]", errors)
            if item is None:
                continue
            keys = {"id", "claim", "brand", "source_state", "action", "target_state", "finding_ids", "change_ids", "evidence_ids", "verification_status", "notes"}
            _required(item, keys, f"revision.claim_trace[{i}]", errors, exact=True)
            for key in ("id", "claim", "brand", "source_state", "notes"):
                _str(item.get(key), f"revision.claim_trace[{i}].{key}", errors)
            _enum(item.get("action"), CLAIM_ACTIONS, f"revision.claim_trace[{i}].action", errors)
            _enum(item.get("target_state"), CLAIM_STATES, f"revision.claim_trace[{i}].target_state", errors)
            _enum(item.get("verification_status"), CLAIM_VERIFY_STATES, f"revision.claim_trace[{i}].verification_status", errors)
            for key in ("finding_ids", "change_ids", "evidence_ids"):
                _str_list(item.get(key), f"revision.claim_trace[{i}].{key}", errors)

    coverage = _obj(root.get("coverage_trace"), "revision.coverage_trace", errors)
    if coverage is not None:
        _required(coverage, {"access", "modules", "surface_checks", "material_limitations"}, "revision.coverage_trace", errors, exact=True)
        specs = {
            "access": ("category", {"pending", "action", "decision", "blocker", "preserve", "not-applicable", "resolved"}),
            "modules": ("id", {"pending", "action", "decision", "blocker", "preserve", "completion-gate", "not-applicable", "resolved"}),
            "surface_checks": ("id", {"pending", "action", "decision", "blocker", "preserve", "perception-test", "completion-gate", "not-applicable", "resolved"}),
        }
        for key, (idkey, allowed) in specs.items():
            rows = _arr(coverage.get(key), f"revision.coverage_trace.{key}", errors)
            if rows is None:
                continue
            for i, row in enumerate(rows):
                item = _obj(row, f"revision.coverage_trace.{key}[{i}]", errors)
                if item is None:
                    continue
                _required(item, {idkey, "source_status", "disposition", "completion_gate", "evidence_ids"}, f"revision.coverage_trace.{key}[{i}]", errors, exact=True)
                _str(item.get(idkey), f"revision.coverage_trace.{key}[{i}].{idkey}", errors)
                _str(item.get("source_status"), f"revision.coverage_trace.{key}[{i}].source_status", errors)
                _enum(item.get("disposition"), allowed, f"revision.coverage_trace.{key}[{i}].disposition", errors)
                _str(item.get("completion_gate"), f"revision.coverage_trace.{key}[{i}].completion_gate", errors)
                _str_list(item.get("evidence_ids"), f"revision.coverage_trace.{key}[{i}].evidence_ids", errors)
        rows = _arr(coverage.get("material_limitations"), "revision.coverage_trace.material_limitations", errors)
        if rows is not None:
            for i, row in enumerate(rows):
                item = _obj(row, f"revision.coverage_trace.material_limitations[{i}]", errors)
                if item is None:
                    continue
                keys = {"id", "description", "source_status", "disposition", "completion_gate", "evidence_ids"}
                _required(item, keys, f"revision.coverage_trace.material_limitations[{i}]", errors, exact=True)
                for key in ("id", "description", "source_status", "completion_gate"):
                    _str(item.get(key), f"revision.coverage_trace.material_limitations[{i}].{key}", errors)
                _enum(item.get("disposition"), {"open", "resolved", "not-applicable"}, f"revision.coverage_trace.material_limitations[{i}].disposition", errors)
                _str_list(item.get("evidence_ids"), f"revision.coverage_trace.material_limitations[{i}].evidence_ids", errors)

    changes = _arr(root.get("changes"), "revision.changes", errors)
    if changes is not None:
        for i, row in enumerate(changes):
            item = _obj(row, f"revision.changes[{i}]", errors)
            if item is None:
                continue
            keys = {"id", "scope", "finding_ids", "convergence_ids", "targets", "description", "authority_ids", "risk_level", "risk_categories", "rollout_id", "evidence_ids"}
            _required(item, keys, f"revision.changes[{i}]", errors, exact=True)
            _str(item.get("id"), f"revision.changes[{i}].id", errors)
            _enum(item.get("scope"), CHANGE_SCOPES, f"revision.changes[{i}].scope", errors)
            for key in ("finding_ids", "convergence_ids", "targets", "authority_ids", "risk_categories", "evidence_ids"):
                _str_list(item.get(key), f"revision.changes[{i}].{key}", errors, allow_empty=(key not in {"targets", "authority_ids"}))
            _str(item.get("description"), f"revision.changes[{i}].description", errors)
            _enum(item.get("risk_level"), RISK_LEVELS, f"revision.changes[{i}].risk_level", errors)
            if isinstance(item.get("risk_categories"), list):
                for value in item["risk_categories"]:
                    if isinstance(value, str) and value not in RISK_CATEGORIES:
                        errors.append(f"revision.changes[{i}].risk_categories contains invalid value: {value}")
            if item.get("rollout_id") is not None:
                _str(item.get("rollout_id"), f"revision.changes[{i}].rollout_id", errors, nullable=True)

    evidence = _arr(root.get("evidence"), "revision.evidence", errors)
    if evidence is not None:
        for i, row in enumerate(evidence):
            item = _obj(row, f"revision.evidence[{i}]", errors)
            if item is None:
                continue
            keys = {"id", "level", "method", "status", "observation", "artifact_path", "limitations", "observed_at"}
            _required(item, keys, f"revision.evidence[{i}]", errors, exact=True)
            _str(item.get("id"), f"revision.evidence[{i}].id", errors)
            _enum(item.get("level"), set(EVIDENCE_LEVELS), f"revision.evidence[{i}].level", errors)
            _enum(item.get("method"), set(EVIDENCE_METHODS), f"revision.evidence[{i}].method", errors)
            _enum(item.get("status"), EVIDENCE_STATES, f"revision.evidence[{i}].status", errors)
            if item.get("observation") is not None:
                _str(item.get("observation"), f"revision.evidence[{i}].observation", errors, nullable=True)
            if item.get("artifact_path") is not None:
                _str(item.get("artifact_path"), f"revision.evidence[{i}].artifact_path", errors, nullable=True)
            _str_list(item.get("limitations"), f"revision.evidence[{i}].limitations", errors)
            _str(item.get("observed_at"), f"revision.evidence[{i}].observed_at", errors)

    perception = _arr(root.get("perception_tests"), "revision.perception_tests", errors)
    if perception is not None:
        for i, row in enumerate(perception):
            item = _obj(row, f"revision.perception_tests[{i}]", errors)
            if item is None:
                continue
            keys = {"id", "finding_ids", "dimensions", "status", "audience_segment", "sample_source", "protocol", "baseline", "result", "limitations", "evidence_ids"}
            _required(item, keys, f"revision.perception_tests[{i}]", errors, exact=True)
            _str(item.get("id"), f"revision.perception_tests[{i}].id", errors)
            _str_list(item.get("finding_ids"), f"revision.perception_tests[{i}].finding_ids", errors)
            dims = _str_list(item.get("dimensions"), f"revision.perception_tests[{i}].dimensions", errors, allow_empty=False)
            if dims:
                for value in dims:
                    if value not in PERCEPTION_DIMENSIONS:
                        errors.append(f"revision.perception_tests[{i}].dimensions contains invalid value: {value}")
            _enum(item.get("status"), PERCEPTION_STATES, f"revision.perception_tests[{i}].status", errors)
            for key in ("audience_segment", "sample_source", "protocol", "baseline"):
                _str(item.get(key), f"revision.perception_tests[{i}].{key}", errors)
            if item.get("result") is not None:
                _str(item.get("result"), f"revision.perception_tests[{i}].result", errors, nullable=True)
            _str_list(item.get("limitations"), f"revision.perception_tests[{i}].limitations", errors)
            _str_list(item.get("evidence_ids"), f"revision.perception_tests[{i}].evidence_ids", errors)

    convergence = _arr(root.get("convergence_findings"), "revision.convergence_findings", errors)
    if convergence is not None:
        for i, row in enumerate(convergence):
            item = _obj(row, f"revision.convergence_findings[{i}]", errors)
            if item is None:
                continue
            keys = {"id", "title", "source", "severity", "status", "reason", "reopened_finding_ids", "change_ids", "evidence_ids"}
            _required(item, keys, f"revision.convergence_findings[{i}]", errors, exact=True)
            for key in ("id", "title", "source", "reason"):
                _str(item.get(key), f"revision.convergence_findings[{i}].{key}", errors)
            _enum(item.get("severity"), CONVERGENCE_SEVERITIES, f"revision.convergence_findings[{i}].severity", errors)
            _enum(item.get("status"), CONVERGENCE_STATES, f"revision.convergence_findings[{i}].status", errors)
            for key in ("reopened_finding_ids", "change_ids", "evidence_ids"):
                _str_list(item.get(key), f"revision.convergence_findings[{i}].{key}", errors)

    rollouts = _arr(root.get("rollouts"), "revision.rollouts", errors)
    if rollouts is not None:
        for i, row in enumerate(rollouts):
            item = _obj(row, f"revision.rollouts[{i}]", errors)
            if item is None:
                continue
            keys = {"id", "change_ids", "state", "inventory", "representative_samples", "collision_checks", "rollback_plan", "authority_ids", "evidence_ids"}
            _required(item, keys, f"revision.rollouts[{i}]", errors, exact=True)
            _str(item.get("id"), f"revision.rollouts[{i}].id", errors)
            _str_list(item.get("change_ids"), f"revision.rollouts[{i}].change_ids", errors, allow_empty=False)
            _enum(item.get("state"), ROLLOUT_STATES, f"revision.rollouts[{i}].state", errors)
            for key in ("inventory", "representative_samples", "collision_checks", "authority_ids", "evidence_ids"):
                _str_list(item.get(key), f"revision.rollouts[{i}].{key}", errors, allow_empty=(key in {"evidence_ids"}))
            _str(item.get("rollback_plan"), f"revision.rollouts[{i}].rollback_plan", errors)

    readiness = _obj(root.get("readiness"), "revision.readiness", errors)
    if readiness is not None:
        keys = {"revision_status", "review_convergence", "integration", "deployment", "publication", "perception_validation", "business_outcome", "authorization_summary", "convergence_evidence_ids", "delivery", "unverified_outcomes", "follow_up_actions"}
        _required(readiness, keys, "revision.readiness", errors, exact=True)
        _enum(readiness.get("revision_status"), REVISION_STATUSES, "revision.readiness.revision_status", errors)
        _enum(readiness.get("review_convergence"), CONVERGENCE_READINESS, "revision.readiness.review_convergence", errors)
        for key in ("integration", "deployment", "publication"):
            _enum(readiness.get(key), READY_STATES, f"revision.readiness.{key}", errors)
        _enum(readiness.get("perception_validation"), PERCEPTION_READINESS, "revision.readiness.perception_validation", errors)
        _enum(readiness.get("business_outcome"), BUSINESS_READINESS, "revision.readiness.business_outcome", errors)
        _enum(readiness.get("authorization_summary"), AUTH_SUMMARY, "revision.readiness.authorization_summary", errors)
        _str_list(readiness.get("convergence_evidence_ids"), "revision.readiness.convergence_evidence_ids", errors)
        _str_list(readiness.get("unverified_outcomes"), "revision.readiness.unverified_outcomes", errors)
        _str_list(readiness.get("follow_up_actions"), "revision.readiness.follow_up_actions", errors)
        delivery = _obj(readiness.get("delivery"), "revision.readiness.delivery", errors)
        if delivery is not None:
            _required(delivery, set(DELIVERY_KEYS), "revision.readiness.delivery", errors, exact=True)
            for key in DELIVERY_KEYS:
                item = _obj(delivery.get(key), f"revision.readiness.delivery.{key}", errors)
                if item is None:
                    continue
                _required(item, {"state", "evidence_ids", "observation"}, f"revision.readiness.delivery.{key}", errors, exact=True)
                _enum(item.get("state"), DELIVERY_STATES, f"revision.readiness.delivery.{key}.state", errors)
                _str_list(item.get("evidence_ids"), f"revision.readiness.delivery.{key}.evidence_ids", errors)
                _str(item.get("observation"), f"revision.readiness.delivery.{key}.observation", errors)
    return not errors
