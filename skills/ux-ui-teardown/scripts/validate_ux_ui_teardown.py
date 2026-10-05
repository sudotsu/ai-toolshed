#!/usr/bin/env python3
"""Validate ux-ui-teardown canonical artifacts without crashing on malformed input."""

from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

FINDING_ID = re.compile(r"^UXUI-\d{3}$")
EVID_ID = re.compile(r"^EVID-\d{3}$")
JOURNEY_ID = re.compile(r"^JOURNEY-\d{3}$")
VIEW_ID = re.compile(r"^VIEW-\d{3}$")
STATE_ID = re.compile(r"^STATE-\d{3}$")
LIMIT_ID = re.compile(r"^LIMIT-\d{3}$")

SEVERITIES = {"critical", "high", "medium", "low", "informational"}
CONFIDENCE = {"confirmed", "high", "medium", "low"}
VERIFICATION = {"observed", "partially_observed", "inferred", "blocked"}
KINDS = {"gap", "risk", "opportunity", "investigation", "strength", "cross_domain"}
STATUSES = {"open", "blocked", "decision_required", "retained_strength", "not_applicable", "resolved"}
BASIS = {"standard_requirement", "observed_behavior", "user_research", "first_party_measurement", "heuristic", "design_system_convention", "aesthetic_preference"}
EVIDENCE_CLASSES = {"source_inspection", "rendered_observation", "interaction_reproduction", "standard_reference", "automated_measurement", "user_research", "first_party_analytics", "stakeholder_context", "design_system_reference"}
DOMAINS = {
    "ux.orientation", "ux.information-architecture", "ux.navigation", "ux.discoverability", "ux.task-flow", "ux.forms", "ux.feedback", "ux.error-recovery", "ux.cognitive-load", "ux.trust", "ux.conversion",
    "ui.visual-hierarchy", "ui.typography", "ui.spacing", "ui.color", "ui.layout", "ui.consistency", "ui.responsive", "ui.motion", "ui.component-states",
    "accessibility.semantics", "accessibility.keyboard", "accessibility.focus", "accessibility.contrast", "accessibility.target-size", "accessibility.reflow", "accessibility.motion",
    "system.design-system", "system.performance-perception",
}
MODULES = {
    "orientation_comprehension", "information_architecture_navigation", "interaction_affordance_feedback", "task_flow_forms_recovery", "responsive_adaptive_layout",
    "accessibility_semantics_keyboard", "visual_hierarchy_legibility", "trust_conversion", "design_system_consistency", "performance_perception",
}
ACCESS = {"source_repository", "production_experience", "analytics", "user_research", "design_system", "assistive_technology"}
VIEW_CLASSES = {"narrow_mobile", "wide_mobile", "tablet", "desktop", "large_desktop", "other"}
COVERAGE_STATUS = {"observed", "blocked", "not_applicable"}
INPUT_MODES = {"pointer_touch", "keyboard", "screen_reader", "voice_switch", "other"}
STATE_CLASSES = {"default", "focus", "hover", "active", "disabled", "loading", "empty", "validation", "error", "success", "destructive", "offline_timeout"}


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required file: {path.name}")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name} invalid JSON: {exc}")
    return None


def is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any, allow_empty: bool = True) -> bool:
    return isinstance(value, list) and (allow_empty or bool(value)) and all(is_nonempty_text(item) for item in value)


def obj(value: Any) -> bool:
    return isinstance(value, dict)


def exact_keys(data: Any, keys: set[str], label: str, errors: list[str]) -> bool:
    if not obj(data):
        errors.append(f"{label} must be an object")
        return False
    missing = sorted(keys - set(data))
    extra = sorted(set(data) - keys)
    if missing:
        errors.append(f"{label} missing keys: {missing}")
    if extra:
        errors.append(f"{label} unexpected keys: {extra}")
    return not missing and not extra


def unique_ids(items: Any, pattern: re.Pattern[str], label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    seen: set[str] = set()
    out: dict[str, dict[str, Any]] = {}
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return out
    for index, item in enumerate(items):
        if not obj(item):
            errors.append(f"{label}[{index}] must be an object")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not pattern.match(ident):
            errors.append(f"{label}[{index}].id invalid: {ident!r}")
            continue
        if ident in seen:
            errors.append(f"{label} duplicate id: {ident}")
        seen.add(ident)
        out[ident] = item
    return out


def check_refs(values: Any, known: set[str], label: str, errors: list[str], allow_empty: bool = True) -> list[str]:
    if not string_list(values, allow_empty=allow_empty):
        errors.append(f"{label} must be {'a' if allow_empty else 'a non-empty'} string list")
        return []
    result = list(values)
    for value in result:
        if value not in known:
            errors.append(f"{label} references unknown id {value}")
    return result


def cycle_check(findings: dict[str, dict[str, Any]], errors: list[str]) -> None:
    graph: dict[str, list[str]] = {}
    for fid, finding in findings.items():
        deps = finding.get("dependencies", [])
        graph[fid] = [item for item in deps if isinstance(item, str) and item in findings]
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str, path: list[str]) -> None:
        if node in visiting:
            errors.append("dependency cycle: " + " -> ".join(path + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph.get(node, []):
            dfs(dependency, path + [node])
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        dfs(node, [])


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    fdoc = load_json(root / "findings.json", errors)
    cdoc = load_json(root / "coverage.json", errors)
    if not obj(fdoc) or not obj(cdoc):
        return errors or ["canonical files must be objects"]

    exact_keys(fdoc, {"schema_version", "audit", "evidence_sources", "journeys", "findings"}, "findings.json", errors)
    exact_keys(cdoc, {"schema_version", "review_status", "access", "modules", "viewports", "input_modes", "state_coverage", "material_limitations", "validator"}, "coverage.json", errors)
    if fdoc.get("schema_version") != "ux-ui-teardown-v1":
        errors.append("findings schema_version must be ux-ui-teardown-v1")
    if cdoc.get("schema_version") != "ux-ui-teardown-coverage-v1":
        errors.append("coverage schema_version must be ux-ui-teardown-coverage-v1")

    audit = fdoc.get("audit")
    audit_keys = {"project_name", "project_locator", "audited_revision", "production_locator", "production_revision_status", "audit_start_date", "audit_end_date", "review_status", "project_type", "primary_user_groups", "primary_goals"}
    if exact_keys(audit, audit_keys, "audit", errors):
        for key in ("project_name", "project_locator", "audited_revision", "production_locator", "project_type"):
            if not is_nonempty_text(audit.get(key)):
                errors.append(f"audit.{key} must be non-empty text")
        if audit.get("review_status") not in {"complete", "provisional"}:
            errors.append("audit.review_status invalid")
        if audit.get("production_revision_status") not in {"verified", "unverified", "not_applicable"}:
            errors.append("audit.production_revision_status invalid")
        if not string_list(audit.get("primary_user_groups"), allow_empty=False):
            errors.append("audit.primary_user_groups must be non-empty strings")
        if not string_list(audit.get("primary_goals"), allow_empty=False):
            errors.append("audit.primary_goals must be non-empty strings")

    evid = unique_ids(fdoc.get("evidence_sources"), EVID_ID, "evidence_sources", errors)
    for eid, evidence in evid.items():
        exact_keys(evidence, {"id", "evidence_class", "title", "locator", "accessed_at", "volatile", "summary", "limitations"}, eid, errors)
        if evidence.get("evidence_class") not in EVIDENCE_CLASSES:
            errors.append(f"{eid}.evidence_class invalid")
        for key in ("title", "locator", "accessed_at", "summary"):
            if not is_nonempty_text(evidence.get(key)):
                errors.append(f"{eid}.{key} must be non-empty text")
        if not isinstance(evidence.get("volatile"), bool):
            errors.append(f"{eid}.volatile must be boolean")
        if not isinstance(evidence.get("limitations"), list):
            errors.append(f"{eid}.limitations must be a list")

    journeys = unique_ids(fdoc.get("journeys"), JOURNEY_ID, "journeys", errors)
    for jid, journey in journeys.items():
        keys = {"id", "title", "user_group", "trigger", "intended_outcome", "criticality", "entry_points", "steps", "required_states", "viewport_ids", "input_modes", "evidence_ids", "status", "limitations"}
        exact_keys(journey, keys, jid, errors)
        if journey.get("criticality") not in {"primary", "secondary", "supporting", "high_risk"}:
            errors.append(f"{jid}.criticality invalid")
        if journey.get("status") not in {"passed", "failed", "partial", "blocked", "not_tested"}:
            errors.append(f"{jid}.status invalid")
        for key in ("title", "user_group", "trigger", "intended_outcome"):
            if not is_nonempty_text(journey.get(key)):
                errors.append(f"{jid}.{key} must be non-empty text")
        for key in ("entry_points", "steps", "viewport_ids", "input_modes", "evidence_ids"):
            if not string_list(journey.get(key), allow_empty=False):
                errors.append(f"{jid}.{key} must be a non-empty string list")
        if not string_list(journey.get("limitations")):
            errors.append(f"{jid}.limitations must be a string list")
        required_states = journey.get("required_states")
        if not string_list(required_states, allow_empty=False) or any(state not in STATE_CLASSES for state in required_states if isinstance(state, str)):
            errors.append(f"{jid}.required_states invalid")
        check_refs(journey.get("evidence_ids"), set(evid), f"{jid}.evidence_ids", errors, allow_empty=False)

    findings = unique_ids(fdoc.get("findings"), FINDING_ID, "findings", errors)
    for fid, finding in findings.items():
        keys = {"id", "title", "kind", "domains", "status", "severity", "confidence", "verification_state", "judgment_basis", "standard_refs", "journey_ids", "surface_targets", "evidence_ids", "observed_condition", "desired_condition", "user_consequence", "business_risk", "recommendation", "acceptance_criteria", "verification_methods", "implementation_targets", "preservation_constraints", "dependencies", "conflicts", "non_goals"}
        exact_keys(finding, keys, fid, errors)
        if finding.get("kind") not in KINDS:
            errors.append(f"{fid}.kind invalid")
        if finding.get("status") not in STATUSES:
            errors.append(f"{fid}.status invalid")
        if finding.get("severity") not in SEVERITIES:
            errors.append(f"{fid}.severity invalid")
        if finding.get("confidence") not in CONFIDENCE:
            errors.append(f"{fid}.confidence invalid")
        if finding.get("verification_state") not in VERIFICATION:
            errors.append(f"{fid}.verification_state invalid")
        if finding.get("judgment_basis") not in BASIS:
            errors.append(f"{fid}.judgment_basis invalid")
        domains = finding.get("domains")
        if not string_list(domains, allow_empty=False) or any(domain not in DOMAINS for domain in domains if isinstance(domain, str)):
            errors.append(f"{fid}.domains invalid")
        if finding.get("judgment_basis") == "aesthetic_preference" and finding.get("severity") not in {"low", "informational"}:
            errors.append(f"{fid} aesthetic_preference cannot exceed low severity")
        if finding.get("judgment_basis") == "heuristic" and finding.get("severity") == "critical":
            errors.append(f"{fid} heuristic alone cannot be critical")
        if finding.get("judgment_basis") == "standard_requirement" and not string_list(finding.get("standard_refs"), allow_empty=False):
            errors.append(f"{fid} standard_requirement requires standard_refs")
        if finding.get("kind") == "strength" and (finding.get("severity") != "informational" or finding.get("status") != "retained_strength"):
            errors.append(f"{fid} strength must be informational retained_strength")
        for key in ("title", "observed_condition", "desired_condition", "user_consequence", "business_risk"):
            if not is_nonempty_text(finding.get(key)):
                errors.append(f"{fid}.{key} must be non-empty text")
        for key in ("surface_targets", "acceptance_criteria", "verification_methods"):
            if not string_list(finding.get(key), allow_empty=False):
                errors.append(f"{fid}.{key} must be non-empty string list")
        check_refs(finding.get("journey_ids"), set(journeys), f"{fid}.journey_ids", errors, allow_empty=False)
        check_refs(finding.get("evidence_ids"), set(evid), f"{fid}.evidence_ids", errors, allow_empty=False)
        for key in ("standard_refs", "implementation_targets", "preservation_constraints", "dependencies", "conflicts", "non_goals"):
            if not string_list(finding.get(key)):
                errors.append(f"{fid}.{key} must be a string list")
        if finding.get("kind") != "strength" and finding.get("status") not in {"not_applicable", "resolved"} and not is_nonempty_text(finding.get("recommendation")):
            errors.append(f"{fid}.recommendation required")
        for dependency in finding.get("dependencies", []) if isinstance(finding.get("dependencies"), list) else []:
            if not isinstance(dependency, str):
                errors.append(f"{fid} dependencies must contain only finding id strings")
                continue
            if dependency not in findings:
                errors.append(f"{fid} references unknown dependency {dependency}")
            if dependency == fid:
                errors.append(f"{fid} cannot depend on itself")
        for conflict in finding.get("conflicts", []) if isinstance(finding.get("conflicts"), list) else []:
            if not isinstance(conflict, str):
                errors.append(f"{fid} conflicts must contain only finding id strings")
                continue
            if conflict not in findings:
                errors.append(f"{fid} references unknown conflict {conflict}")
            elif fid not in findings[conflict].get("conflicts", []):
                errors.append(f"{fid} conflict with {conflict} is not symmetric")
    cycle_check(findings, errors)

    if cdoc.get("review_status") not in {"complete", "provisional"}:
        errors.append("coverage.review_status invalid")
    if obj(audit) and cdoc.get("review_status") != audit.get("review_status"):
        errors.append("review_status mismatch between canonical files")

    access = cdoc.get("access")
    if not isinstance(access, list):
        errors.append("coverage.access must be a list")
        access = []
    categories: list[str] = []
    for index, row in enumerate(access):
        label = f"access[{index}]"
        if not obj(row):
            errors.append(f"{label} must be object")
            continue
        exact_keys(row, {"category", "status", "material_to_comprehensive", "evidence_ids", "limitations", "next_step"}, label, errors)
        category = row.get("category")
        categories.append(category)
        if category not in ACCESS:
            errors.append(f"{label}.category invalid")
        if row.get("status") not in {"available", "partial", "blocked", "not_applicable"}:
            errors.append(f"{label}.status invalid")
        if not isinstance(row.get("material_to_comprehensive"), bool):
            errors.append(f"{label}.material_to_comprehensive must be bool")
        check_refs(row.get("evidence_ids"), set(evid), f"{label}.evidence_ids", errors)
        if not string_list(row.get("limitations")):
            errors.append(f"{label}.limitations must be string list")
        if not is_nonempty_text(row.get("next_step")):
            errors.append(f"{label}.next_step must be non-empty text")
    if set(categories) != ACCESS or len(categories) != len(ACCESS):
        errors.append("coverage.access must contain each access category exactly once")

    modules = cdoc.get("modules")
    if not isinstance(modules, list):
        errors.append("coverage.modules must be a list")
        modules = []
    module_ids: list[str] = []
    for index, module in enumerate(modules):
        label = f"modules[{index}]"
        if not obj(module):
            errors.append(f"{label} must be object")
            continue
        exact_keys(module, {"id", "materiality", "status", "finding_ids", "evidence_ids", "limitations"}, label, errors)
        mid = module.get("id")
        module_ids.append(mid)
        if mid not in MODULES:
            errors.append(f"{label}.id invalid")
        if module.get("materiality") not in {"defining", "high", "medium", "low"}:
            errors.append(f"{mid}.materiality invalid")
        if module.get("status") not in {"passed", "failed", "partial", "blocked", "not_tested", "not_applicable"}:
            errors.append(f"{mid}.status invalid")
        check_refs(module.get("finding_ids"), set(findings), f"{mid}.finding_ids", errors)
        check_refs(module.get("evidence_ids"), set(evid), f"{mid}.evidence_ids", errors)
        if not string_list(module.get("limitations")):
            errors.append(f"{mid}.limitations must be string list")
    if set(module_ids) != MODULES or len(module_ids) != len(MODULES):
        errors.append("coverage.modules must contain each module exactly once")

    viewports = unique_ids(cdoc.get("viewports"), VIEW_ID, "viewports", errors)
    observed_view_classes_by_journey: dict[str, set[str]] = {jid: set() for jid in journeys}
    for vid, viewport in viewports.items():
        exact_keys(viewport, {"id", "label", "width", "height", "class", "status", "journey_ids", "evidence_ids", "limitations"}, vid, errors)
        if not is_nonempty_text(viewport.get("label")):
            errors.append(f"{vid}.label must be non-empty text")
        if not isinstance(viewport.get("width"), int) or isinstance(viewport.get("width"), bool) or viewport.get("width", 0) <= 0:
            errors.append(f"{vid}.width invalid")
        if not isinstance(viewport.get("height"), int) or isinstance(viewport.get("height"), bool) or viewport.get("height", 0) <= 0:
            errors.append(f"{vid}.height invalid")
        if viewport.get("class") not in VIEW_CLASSES:
            errors.append(f"{vid}.class invalid")
        if viewport.get("status") not in COVERAGE_STATUS:
            errors.append(f"{vid}.status invalid")
        jids = check_refs(viewport.get("journey_ids"), set(journeys), f"{vid}.journey_ids", errors, allow_empty=False)
        evidence_ids = check_refs(viewport.get("evidence_ids"), set(evid), f"{vid}.evidence_ids", errors, allow_empty=viewport.get("status") != "observed")
        if not string_list(viewport.get("limitations")):
            errors.append(f"{vid}.limitations must be string list")
        if viewport.get("status") == "observed":
            if not evidence_ids:
                errors.append(f"{vid} observed viewport requires evidence")
            for jid in jids:
                if jid in observed_view_classes_by_journey and viewport.get("class") in VIEW_CLASSES:
                    observed_view_classes_by_journey[jid].add(viewport.get("class"))

    input_modes = cdoc.get("input_modes")
    if not isinstance(input_modes, list):
        errors.append("coverage.input_modes must be a list")
        input_modes = []
    seen_modes: set[str] = set()
    observed_modes_by_journey: dict[str, set[str]] = {jid: set() for jid in journeys}
    for index, mode_row in enumerate(input_modes):
        label = f"input_modes[{index}]"
        if not obj(mode_row):
            errors.append(f"{label} must be object")
            continue
        exact_keys(mode_row, {"mode", "status", "journey_ids", "evidence_ids", "limitations"}, label, errors)
        mode = mode_row.get("mode")
        if mode not in INPUT_MODES:
            errors.append(f"{label}.mode invalid")
        elif mode in seen_modes:
            errors.append(f"coverage.input_modes duplicate mode: {mode}")
        else:
            seen_modes.add(mode)
        if mode_row.get("status") not in COVERAGE_STATUS:
            errors.append(f"{label}.status invalid")
        jids = check_refs(mode_row.get("journey_ids"), set(journeys), f"{label}.journey_ids", errors, allow_empty=False)
        evidence_ids = check_refs(mode_row.get("evidence_ids"), set(evid), f"{label}.evidence_ids", errors, allow_empty=mode_row.get("status") != "observed")
        if not string_list(mode_row.get("limitations")):
            errors.append(f"{label}.limitations must be string list")
        if mode_row.get("status") == "observed":
            if not evidence_ids:
                errors.append(f"{label} observed input mode requires evidence")
            for jid in jids:
                if jid in observed_modes_by_journey and mode in INPUT_MODES:
                    observed_modes_by_journey[jid].add(mode)

    states = unique_ids(cdoc.get("state_coverage"), STATE_ID, "state_coverage", errors)
    observed_states_by_journey: dict[str, set[str]] = {jid: set() for jid in journeys}
    for sid, state in states.items():
        keys = {"id", "state", "label", "journey_id", "step", "surface_target", "trigger", "status", "viewport_ids", "input_modes", "evidence_ids", "finding_ids", "limitations"}
        exact_keys(state, keys, sid, errors)
        state_class = state.get("state")
        if state_class not in STATE_CLASSES:
            errors.append(f"{sid}.state invalid")
        for key in ("label", "step", "surface_target", "trigger"):
            if not is_nonempty_text(state.get(key)):
                errors.append(f"{sid}.{key} must be non-empty text")
        jid = state.get("journey_id")
        if not isinstance(jid, str) or jid not in journeys:
            errors.append(f"{sid}.journey_id references unknown journey {jid!r}")
        if state.get("status") not in COVERAGE_STATUS:
            errors.append(f"{sid}.status invalid")
        viewport_ids = check_refs(state.get("viewport_ids"), set(viewports), f"{sid}.viewport_ids", errors, allow_empty=state.get("status") != "observed")
        state_modes = state.get("input_modes")
        if not string_list(state_modes, allow_empty=state.get("status") != "observed") or any(mode not in INPUT_MODES for mode in state_modes if isinstance(mode, str)):
            errors.append(f"{sid}.input_modes invalid")
            state_modes = []
        evidence_ids = check_refs(state.get("evidence_ids"), set(evid), f"{sid}.evidence_ids", errors, allow_empty=state.get("status") != "observed")
        check_refs(state.get("finding_ids"), set(findings), f"{sid}.finding_ids", errors)
        if not string_list(state.get("limitations")):
            errors.append(f"{sid}.limitations must be string list")
        if state.get("status") == "observed":
            if not evidence_ids or not viewport_ids or not state_modes:
                errors.append(f"{sid} observed state requires evidence, viewport_ids, and input_modes")
            if jid in journeys and state_class in STATE_CLASSES:
                observed_states_by_journey[jid].add(state_class)
            for vid in viewport_ids:
                viewport = viewports.get(vid)
                if viewport and jid not in viewport.get("journey_ids", []):
                    errors.append(f"{sid} viewport {vid} is not linked to journey {jid}")
            for mode in state_modes:
                matching_rows = [row for row in input_modes if obj(row) and row.get("mode") == mode and row.get("status") == "observed" and jid in row.get("journey_ids", [])]
                if not matching_rows:
                    errors.append(f"{sid} input mode {mode} is not observed for journey {jid}")

    for jid, journey in journeys.items():
        declared_viewports = journey.get("viewport_ids") if isinstance(journey.get("viewport_ids"), list) else []
        for vid in declared_viewports:
            if vid not in viewports:
                errors.append(f"{jid}.viewport_ids references unknown viewport {vid}")
            elif jid not in viewports[vid].get("journey_ids", []):
                errors.append(f"{jid} viewport {vid} does not link back to journey")
        declared_modes = journey.get("input_modes") if isinstance(journey.get("input_modes"), list) else []
        for mode in declared_modes:
            if mode not in INPUT_MODES:
                errors.append(f"{jid}.input_modes invalid value {mode}")
            elif not any(obj(row) and row.get("mode") == mode and jid in row.get("journey_ids", []) for row in input_modes):
                errors.append(f"{jid} input mode {mode} has no coverage row linked to journey")

    limits = unique_ids(cdoc.get("material_limitations"), LIMIT_ID, "material_limitations", errors)
    for lid, limitation in limits.items():
        exact_keys(limitation, {"id", "description", "status", "completion_requirement", "affected_module_ids"}, lid, errors)
        for key in ("description", "completion_requirement"):
            if not is_nonempty_text(limitation.get(key)):
                errors.append(f"{lid}.{key} must be non-empty text")
        if limitation.get("status") not in {"open", "resolved"}:
            errors.append(f"{lid}.status invalid")
        if not string_list(limitation.get("affected_module_ids"), allow_empty=False) or any(mid not in MODULES for mid in limitation.get("affected_module_ids", []) if isinstance(mid, str)):
            errors.append(f"{lid}.affected_module_ids invalid")

    complete = obj(audit) and audit.get("review_status") == "complete"
    interactive_web = obj(audit) and audit.get("project_type") in {"website", "web_app", "saas", "ecommerce", "local_service", "agency_professional_service"}
    if complete:
        if any(limit.get("status") == "open" for limit in limits.values()):
            errors.append("complete review cannot have open material limitations")
        for module in modules:
            if obj(module) and module.get("materiality") in {"defining", "high"} and module.get("status") in {"partial", "blocked", "not_tested"}:
                errors.append(f"complete review has incomplete material module {module.get('id')}")
        for jid, journey in journeys.items():
            if journey.get("criticality") not in {"primary", "high_risk"}:
                continue
            if journey.get("status") in {"partial", "blocked", "not_tested"}:
                errors.append(f"complete review has incomplete material journey {jid}")
            required_states = set(journey.get("required_states", [])) if isinstance(journey.get("required_states"), list) else set()
            missing_states = sorted(required_states - observed_states_by_journey.get(jid, set()))
            if missing_states:
                errors.append(f"complete material journey {jid} missing observed required states: {missing_states}")
            if interactive_web:
                missing_view_classes = sorted({"narrow_mobile", "desktop"} - observed_view_classes_by_journey.get(jid, set()))
                if missing_view_classes:
                    errors.append(f"complete material journey {jid} missing observed viewport classes: {missing_view_classes}")
                missing_modes = sorted({"pointer_touch", "keyboard"} - observed_modes_by_journey.get(jid, set()))
                if missing_modes:
                    errors.append(f"complete material journey {jid} missing observed input modes: {missing_modes}")
        if audit.get("production_locator") and audit.get("production_revision_status") == "unverified":
            errors.append("complete public review cannot have unverified production revision")

    validator = cdoc.get("validator")
    if not obj(validator):
        errors.append("coverage.validator must be object")
    else:
        exact_keys(validator, {"name", "status", "validated_at"}, "coverage.validator", errors)
        if not is_nonempty_text(validator.get("name")) or not is_nonempty_text(validator.get("validated_at")):
            errors.append("coverage.validator name and validated_at must be non-empty text")
        if validator.get("status") not in {"passed", "failed"}:
            errors.append("coverage.validator.status invalid")
        if complete and validator.get("status") != "passed":
            errors.append("complete review requires validator.status passed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print(f"UX/UI teardown validation failed with {len(errors)} error(s):")
        for error in errors[:100]:
            print(f"- {error}")
        return 1
    print("ux-ui-teardown validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
