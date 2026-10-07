#!/usr/bin/env python3
"""Validate ux-ui-teardown v2 canonical artifacts without crashing on malformed input."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    "evidence": re.compile(r"^EVID-\d{3}$"),
    "competitor": re.compile(r"^COMP-\d{3}$"),
    "journey": re.compile(r"^JOURNEY-\d{3}$"),
    "experience": re.compile(r"^EXP-\d{3}$"),
    "finding": re.compile(r"^UXUI-\d{3}$"),
    "viewport": re.compile(r"^VIEW-\d{3}$"),
    "state": re.compile(r"^STATE-\d{3}$"),
    "limit": re.compile(r"^LIMIT-\d{3}$"),
}
EVIDENCE_CLASSES = {
    "source_inspection", "rendered_observation", "interaction_reproduction",
    "standard_reference", "automated_measurement", "user_research",
    "user_sentiment", "first_party_analytics", "stakeholder_context",
    "design_system_reference", "competitor_measurement", "competitor_observation",
}
AUDIENCE = {"local", "regional", "national", "global", "mixed", "internal"}
CRITICALITY = {"primary", "high_risk", "secondary", "supporting"}
EFFORT = {"low", "moderate", "high", "contextual"}
JOURNEY_STATUS = {"passed", "failed", "partial", "blocked", "not_tested"}
AXES = {
    "visual_craft", "color_system", "typography", "composition", "visual_coherence",
    "audience_fit", "orientation_clarity", "journey_logic", "friction",
    "engagement_quality", "effort_payoff", "feedback_progress",
    "relevance_personalization", "trust", "recovery", "responsive_consistency",
    "perceived_performance", "accessibility_readability",
}
CONFIDENCE = {"confirmed", "high", "medium", "low"}
KINDS = {"gap", "risk", "opportunity", "investigation", "strength", "comparative"}
FINDING_STATUS = {"open", "blocked", "decision_required", "retained_strength", "not_applicable", "resolved"}
SEVERITY = {"critical", "high", "medium", "low", "informational"}
VERIFICATION = {"observed", "partially_observed", "inferred", "blocked"}
BASIS = {
    "standard_requirement", "observed_behavior", "visual_craft", "measured_comparison",
    "user_research", "user_sentiment", "first_party_measurement", "heuristic",
    "design_system_convention", "owner_context", "aesthetic_preference",
}
ACCESS = {"source_repository", "production_experience", "competitor_measurement", "user_sentiment", "design_system", "assistive_technology"}
PASSES = {"ui_craft", "ux_experience", "competitive_calibration", "accessibility_readability"}
PASS_STATUS = {"passed", "failed", "partial", "blocked", "not_tested", "not_applicable"}
VIEW_CLASSES = {"narrow_mobile", "wide_mobile", "tablet", "desktop", "large_desktop", "other"}
COVERAGE_STATUS = {"observed", "blocked", "not_applicable"}
INPUT_MODES = {"pointer_touch", "keyboard", "screen_reader", "other"}
STATE_CLASSES = {"default", "focus", "hover", "active", "disabled", "loading", "empty", "validation", "error", "success", "destructive", "offline_timeout"}
DOMAINS = {
    "ui.visual-craft", "ui.color", "ui.typography", "ui.composition", "ui.coherence",
    "ui.responsive", "ui.component-states", "ux.orientation", "ux.navigation",
    "ux.journey", "ux.friction", "ux.engagement", "ux.feedback", "ux.progress",
    "ux.relevance", "ux.trust", "ux.recovery", "ux.performance-perception",
    "ux.audience-fit", "accessibility.readability", "accessibility.keyboard",
    "accessibility.semantics", "competitive.calibration",
}


def obj(value):
    return isinstance(value, dict)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def slist(value):
    return [item for item in value if text(item)] if isinstance(value, list) else []


def load(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.name} cannot load: {exc}")
        return None


def ids(rows, pattern, label, errors):
    output = {}
    if not isinstance(rows, list):
        errors.append(f"{label} must be list")
        return output
    for index, row in enumerate(rows):
        if not obj(row):
            errors.append(f"{label}[{index}] must be object")
            continue
        ident = row.get("id")
        if not isinstance(ident, str) or not pattern.match(ident):
            errors.append(f"{label}[{index}].id invalid")
            continue
        if ident in output:
            errors.append(f"duplicate {label} id {ident}")
        output[ident] = row
    return output


def refs(value, known, label, errors, nonempty=False):
    values = slist(value)
    if not isinstance(value, list) or len(values) != len(value) or (nonempty and not values):
        prefix = "non-empty " if nonempty else ""
        errors.append(f"{label} must be {prefix}string list")
    for item in values:
        if item not in known:
            errors.append(f"{label} references unknown id {item}")
    return values


def validate(root: Path):
    errors: list[str] = []
    findings_doc = load(root / "findings.json", errors)
    coverage = load(root / "coverage.json", errors)
    if not obj(findings_doc) or not obj(coverage):
        return errors or ["canonical files must be objects"]

    if findings_doc.get("schema_version") != "ux-ui-teardown-v2":
        errors.append("findings schema_version must be ux-ui-teardown-v2")
    if coverage.get("schema_version") != "ux-ui-teardown-coverage-v2":
        errors.append("coverage schema_version must be ux-ui-teardown-coverage-v2")

    audit = findings_doc.get("audit") if obj(findings_doc.get("audit")) else {}
    if not audit:
        errors.append("audit must be object")
    required_audit = [
        "project_name", "project_locator", "audited_revision", "production_locator",
        "production_revision_status", "audit_start_date", "audit_end_date", "review_status",
        "project_type", "audience_scope", "primary_user_groups", "primary_goals",
        "owner_context", "competitor_benchmark_required", "competitor_benchmark_reason",
    ]
    for key in required_audit:
        if key not in audit:
            errors.append(f"audit missing {key}")
    for key in ["project_name", "project_locator", "audited_revision", "project_type", "competitor_benchmark_reason"]:
        if key in audit and not text(audit.get(key)):
            errors.append(f"audit.{key} must be non-empty text")
    if audit.get("review_status") not in {"complete", "provisional"}:
        errors.append("audit.review_status invalid")
    if audit.get("production_revision_status") not in {"verified", "unverified", "not_applicable"}:
        errors.append("audit.production_revision_status invalid")
    if audit.get("audience_scope") not in AUDIENCE:
        errors.append("audit.audience_scope invalid")
    if not isinstance(audit.get("primary_user_groups"), list) or not slist(audit.get("primary_user_groups")):
        errors.append("audit.primary_user_groups must be non-empty string list")
    if not isinstance(audit.get("primary_goals"), list) or not slist(audit.get("primary_goals")):
        errors.append("audit.primary_goals must be non-empty string list")
    owner_context = audit.get("owner_context")
    if not isinstance(owner_context, list) or len(slist(owner_context)) != len(owner_context if isinstance(owner_context, list) else []):
        errors.append("audit.owner_context must be string list")
    if not isinstance(audit.get("competitor_benchmark_required"), bool):
        errors.append("audit.competitor_benchmark_required must be bool")

    evidence = ids(findings_doc.get("evidence_sources"), PATTERNS["evidence"], "evidence_sources", errors)
    for eid, row in evidence.items():
        if row.get("evidence_class") not in EVIDENCE_CLASSES:
            errors.append(f"{eid}.evidence_class invalid")
        for key in ["title", "locator", "accessed_at", "summary"]:
            if not text(row.get(key)):
                errors.append(f"{eid}.{key} must be non-empty text")
        limitations = row.get("limitations")
        if not isinstance(limitations, list) or len(slist(limitations)) != len(limitations if isinstance(limitations, list) else []):
            errors.append(f"{eid}.limitations must be string list")

    competitors = ids(findings_doc.get("competitor_set"), PATTERNS["competitor"], "competitor_set", errors)
    competitor_comparison_refs = {}
    for cid, row in competitors.items():
        if row.get("selection_status") not in {"measured", "owner_supplied", "reference_only"}:
            errors.append(f"{cid}.selection_status invalid")
        for key in ["name", "locator", "relevance_reason"]:
            if not text(row.get(key)):
                errors.append(f"{cid}.{key} must be non-empty text")
        selection_refs = refs(
            row.get("selection_evidence_ids"), set(evidence), f"{cid}.selection_evidence_ids", errors,
            nonempty=row.get("selection_status") == "measured",
        )
        comparison_refs = refs(row.get("comparison_evidence_ids"), set(evidence), f"{cid}.comparison_evidence_ids", errors)
        competitor_comparison_refs[cid] = set(comparison_refs)
        if not slist(row.get("surfaces_compared")):
            errors.append(f"{cid}.surfaces_compared must be non-empty string list")
        if row.get("selection_status") == "measured" and not any(
            evidence.get(ref, {}).get("evidence_class") == "competitor_measurement" for ref in selection_refs
        ):
            errors.append(f"{cid} measured competitor requires competitor_measurement evidence")
        if comparison_refs and not any(
            evidence.get(ref, {}).get("evidence_class") == "competitor_observation" for ref in comparison_refs
        ):
            errors.append(f"{cid} comparison_evidence_ids require competitor_observation evidence")

    journeys = ids(findings_doc.get("journeys"), PATTERNS["journey"], "journeys", errors)
    journey_declared_views = {}
    journey_declared_modes = {}
    journey_declared_states = {}
    for jid, row in journeys.items():
        if row.get("criticality") not in CRITICALITY:
            errors.append(f"{jid}.criticality invalid")
        if row.get("effort_budget") not in EFFORT:
            errors.append(f"{jid}.effort_budget invalid")
        if row.get("status") not in JOURNEY_STATUS:
            errors.append(f"{jid}.status invalid")
        for key in ["title", "user_group", "trigger", "intended_outcome", "engagement_intent", "expected_payoff", "context_notes"]:
            if not text(row.get(key)):
                errors.append(f"{jid}.{key} must be non-empty text")
        if not slist(row.get("steps")):
            errors.append(f"{jid}.steps must be non-empty string list")
        refs(row.get("evidence_ids"), set(evidence), f"{jid}.evidence_ids", errors, nonempty=True)
        for key in ["viewport_ids", "input_modes", "state_ids", "limitations"]:
            value = row.get(key)
            if not isinstance(value, list) or len(slist(value)) != len(value if isinstance(value, list) else []):
                errors.append(f"{jid}.{key} must be string list")
        journey_declared_views[jid] = set(slist(row.get("viewport_ids")))
        journey_declared_modes[jid] = set(slist(row.get("input_modes")))
        journey_declared_states[jid] = set(slist(row.get("state_ids")))

    experiences = ids(findings_doc.get("experience_assessments"), PATTERNS["experience"], "experience_assessments", errors)
    experiences_by_journey = {jid: set() for jid in journeys}
    axes_seen = set()
    comparative_assessments = []
    for xid, row in experiences.items():
        axis = row.get("axis")
        if not isinstance(axis, str) or axis not in AXES:
            errors.append(f"{xid}.axis invalid")
            axis = None
        if axis is not None:
            axes_seen.add(axis)
        if row.get("confidence") not in CONFIDENCE:
            errors.append(f"{xid}.confidence invalid")
        for key in ["surface_target", "verdict", "observation", "reasoning", "desired_direction"]:
            if not text(row.get(key)):
                errors.append(f"{xid}.{key} must be non-empty text")
        jids = refs(row.get("journey_ids"), set(journeys), f"{xid}.journey_ids", errors)
        evidence_refs = refs(row.get("evidence_ids"), set(evidence), f"{xid}.evidence_ids", errors, nonempty=True)
        cids = refs(row.get("competitor_ids"), set(competitors), f"{xid}.competitor_ids", errors)
        if cids:
            comparative_assessments.append((set(cids), set(evidence_refs), xid))
        for jid in jids:
            if axis is not None:
                experiences_by_journey.setdefault(jid, set()).add(axis)

    findings = ids(findings_doc.get("findings"), PATTERNS["finding"], "findings", errors)
    for fid, row in findings.items():
        if row.get("kind") not in KINDS:
            errors.append(f"{fid}.kind invalid")
        if row.get("status") not in FINDING_STATUS:
            errors.append(f"{fid}.status invalid")
        if row.get("severity") not in SEVERITY:
            errors.append(f"{fid}.severity invalid")
        if row.get("confidence") not in CONFIDENCE:
            errors.append(f"{fid}.confidence invalid")
        if row.get("verification_state") not in VERIFICATION:
            errors.append(f"{fid}.verification_state invalid")
        if row.get("judgment_basis") not in BASIS:
            errors.append(f"{fid}.judgment_basis invalid")
        domains = slist(row.get("domains"))
        raw_domains = row.get("domains")
        if not domains or not isinstance(raw_domains, list) or len(domains) != len(raw_domains) or any(domain not in DOMAINS for domain in domains):
            errors.append(f"{fid}.domains invalid")
        if row.get("judgment_basis") == "aesthetic_preference" and row.get("severity") not in {"low", "informational"}:
            errors.append(f"{fid} aesthetic_preference cannot exceed low severity")
        if row.get("judgment_basis") == "visual_craft" and row.get("severity") == "critical":
            errors.append(f"{fid} visual_craft alone cannot be critical")
        competitor_ids = refs(row.get("competitor_ids"), set(competitors), f"{fid}.competitor_ids", errors)
        if row.get("judgment_basis") == "measured_comparison" and not competitor_ids:
            errors.append(f"{fid} measured_comparison requires competitor_ids")
        if row.get("kind") == "strength" and (row.get("severity") != "informational" or row.get("status") != "retained_strength"):
            errors.append(f"{fid} strength must be informational retained_strength")
        for key in ["title", "observed_condition", "desired_condition", "user_consequence", "business_risk"]:
            if not text(row.get(key)):
                errors.append(f"{fid}.{key} must be non-empty text")
        for key in ["surface_targets", "acceptance_criteria", "verification_methods"]:
            if not slist(row.get(key)):
                errors.append(f"{fid}.{key} must be non-empty string list")
        refs(row.get("journey_ids"), set(journeys), f"{fid}.journey_ids", errors)
        refs(row.get("evidence_ids"), set(evidence), f"{fid}.evidence_ids", errors, nonempty=True)
        for key in ["standard_refs", "implementation_targets", "preservation_constraints", "dependencies", "conflicts", "non_goals"]:
            value = row.get(key)
            if not isinstance(value, list) or len(slist(value)) != len(value if isinstance(value, list) else []):
                errors.append(f"{fid}.{key} must be string list")
        if row.get("kind") != "strength" and row.get("status") not in {"not_applicable", "resolved"} and not text(row.get("recommendation")):
            errors.append(f"{fid}.recommendation required")
        for dependency in slist(row.get("dependencies")):
            if dependency not in findings:
                errors.append(f"{fid} unknown dependency {dependency}")
        for conflict in slist(row.get("conflicts")):
            if conflict not in findings:
                errors.append(f"{fid} unknown conflict {conflict}")
            elif fid not in slist(findings[conflict].get("conflicts")):
                errors.append(f"{fid} conflict with {conflict} not symmetric")

    if coverage.get("review_status") not in {"complete", "provisional"}:
        errors.append("coverage.review_status invalid")
    if coverage.get("review_status") != audit.get("review_status"):
        errors.append("review_status mismatch")

    access_rows = coverage.get("access") if isinstance(coverage.get("access"), list) else []
    if not isinstance(coverage.get("access"), list):
        errors.append("coverage.access must be list")
    categories = []
    for index, row in enumerate(access_rows):
        if not obj(row):
            errors.append(f"access[{index}] must be object")
            continue
        category = row.get("category")
        if not isinstance(category, str):
            errors.append(f"access[{index}].category invalid")
            continue
        categories.append(category)
        if category not in ACCESS:
            errors.append(f"access[{index}].category invalid")
        if row.get("status") not in {"available", "partial", "blocked", "not_applicable"}:
            errors.append(f"access[{index}].status invalid")
        if not isinstance(row.get("material_to_complete"), bool):
            errors.append(f"access[{index}].material_to_complete must be bool")
        refs(row.get("evidence_ids"), set(evidence), f"access[{index}].evidence_ids", errors)
    if set(categories) != ACCESS or len(categories) != len(ACCESS):
        errors.append("coverage.access must contain each category exactly once")

    pass_rows = coverage.get("passes") if isinstance(coverage.get("passes"), list) else []
    if not isinstance(coverage.get("passes"), list):
        errors.append("coverage.passes must be list")
    pass_map = {}
    for index, row in enumerate(pass_rows):
        if not obj(row):
            errors.append(f"passes[{index}] must be object")
            continue
        pid = row.get("id")
        if not isinstance(pid, str):
            errors.append(f"passes[{index}].id invalid")
            continue
        if pid in pass_map:
            errors.append(f"duplicate pass {pid}")
        pass_map[pid] = row
        if pid not in PASSES:
            errors.append(f"passes[{index}].id invalid")
        if row.get("materiality") not in {"defining", "high", "supporting"}:
            errors.append(f"{pid}.materiality invalid")
        if row.get("status") not in PASS_STATUS:
            errors.append(f"{pid}.status invalid")
        refs(row.get("finding_ids"), set(findings), f"{pid}.finding_ids", errors)
        refs(row.get("evidence_ids"), set(evidence), f"{pid}.evidence_ids", errors)
    if set(pass_map) != PASSES:
        errors.append("coverage.passes must contain all four passes exactly once")

    viewports = ids(coverage.get("viewports"), PATTERNS["viewport"], "viewports", errors)
    observed_views = {jid: set() for jid in journeys}
    for vid, row in viewports.items():
        if row.get("class") not in VIEW_CLASSES:
            errors.append(f"{vid}.class invalid")
        if row.get("status") not in COVERAGE_STATUS:
            errors.append(f"{vid}.status invalid")
        jids = refs(row.get("journey_ids"), set(journeys), f"{vid}.journey_ids", errors)
        refs(row.get("evidence_ids"), set(evidence), f"{vid}.evidence_ids", errors, nonempty=row.get("status") == "observed")
        if row.get("status") == "observed":
            for jid in jids:
                observed_views.setdefault(jid, set()).add(row.get("class"))

    input_rows = coverage.get("input_modes") if isinstance(coverage.get("input_modes"), list) else []
    if not isinstance(coverage.get("input_modes"), list):
        errors.append("coverage.input_modes must be list")
    observed_modes = {jid: set() for jid in journeys}
    input_map = {}
    seen_modes = set()
    for index, row in enumerate(input_rows):
        if not obj(row):
            errors.append(f"input_modes[{index}] must be object")
            continue
        mode = row.get("mode")
        if not isinstance(mode, str):
            errors.append(f"input_modes[{index}].mode invalid")
            continue
        if mode not in INPUT_MODES:
            errors.append(f"input_modes[{index}].mode invalid")
        if mode in seen_modes:
            errors.append(f"duplicate input mode {mode}")
        seen_modes.add(mode)
        input_map[mode] = row
        if row.get("status") not in COVERAGE_STATUS:
            errors.append(f"input_modes[{index}].status invalid")
        jids = refs(row.get("journey_ids"), set(journeys), f"input_modes[{index}].journey_ids", errors)
        refs(row.get("evidence_ids"), set(evidence), f"input_modes[{index}].evidence_ids", errors, nonempty=row.get("status") == "observed")
        if row.get("status") == "observed":
            for jid in jids:
                observed_modes.setdefault(jid, set()).add(mode)

    states = ids(coverage.get("state_coverage"), PATTERNS["state"], "state_coverage", errors)
    for sid, row in states.items():
        if row.get("state") not in STATE_CLASSES:
            errors.append(f"{sid}.state invalid")
        jid = row.get("journey_id")
        if jid not in journeys:
            errors.append(f"{sid}.journey_id invalid")
        if row.get("status") not in COVERAGE_STATUS:
            errors.append(f"{sid}.status invalid")
        refs(row.get("viewport_ids"), set(viewports), f"{sid}.viewport_ids", errors, nonempty=row.get("status") == "observed")
        refs(row.get("evidence_ids"), set(evidence), f"{sid}.evidence_ids", errors, nonempty=row.get("status") == "observed")
        modes = slist(row.get("input_modes"))
        if not isinstance(row.get("input_modes"), list) or len(modes) != len(row.get("input_modes", []) if isinstance(row.get("input_modes"), list) else []) or any(mode not in INPUT_MODES for mode in modes):
            errors.append(f"{sid}.input_modes invalid")
        refs(row.get("finding_ids"), set(findings), f"{sid}.finding_ids", errors)

    # Canonical journey coverage references must resolve and be reciprocal.
    for jid in journeys:
        for vid in journey_declared_views.get(jid, set()):
            if vid not in viewports:
                errors.append(f"{jid}.viewport_ids references unknown id {vid}")
            elif jid not in slist(viewports[vid].get("journey_ids")):
                errors.append(f"{jid} viewport {vid} is not reciprocal")
        for sid in journey_declared_states.get(jid, set()):
            if sid not in states:
                errors.append(f"{jid}.state_ids references unknown id {sid}")
            elif states[sid].get("journey_id") != jid:
                errors.append(f"{jid} state {sid} belongs to another journey")
        for mode in journey_declared_modes.get(jid, set()):
            if mode not in INPUT_MODES:
                errors.append(f"{jid}.input_modes contains unsupported mode {mode}")
                continue
            coverage_row = input_map.get(mode)
            if coverage_row is None:
                errors.append(f"{jid}.input_modes has no coverage row for {mode}")
            elif jid not in slist(coverage_row.get("journey_ids")):
                errors.append(f"{jid} input mode {mode} is not reciprocal")

    limitations = ids(coverage.get("material_limitations"), PATTERNS["limit"], "material_limitations", errors)
    for lid, row in limitations.items():
        if row.get("status") not in {"open", "resolved"}:
            errors.append(f"{lid}.status invalid")
        if not text(row.get("description")) or not text(row.get("completion_requirement")):
            errors.append(f"{lid} description/completion_requirement required")

    complete = audit.get("review_status") == "complete"
    interactive = audit.get("project_type") in {"website", "web_app", "saas", "ecommerce", "local_service", "agency_professional_service"}
    benchmark_required = audit.get("competitor_benchmark_required") is True
    if complete:
        if any(obj(row) and row.get("material_to_complete") is True and row.get("status") in {"partial", "blocked"} for row in access_rows):
            errors.append("complete review has material access partial/blocked")
        if any(row.get("status") == "open" for row in limitations.values()):
            errors.append("complete review cannot have open material limitations")
        for pid in ["ui_craft", "ux_experience"]:
            if pass_map.get(pid, {}).get("status") not in {"passed", "failed"}:
                errors.append(f"complete review requires completed {pid} pass")

        if benchmark_required:
            if pass_map.get("competitive_calibration", {}).get("status") not in {"passed", "failed"}:
                errors.append("complete review requires competitive calibration pass")
            measured_ids = [cid for cid, row in competitors.items() if row.get("selection_status") == "measured"]
            if len(measured_ids) < 2:
                errors.append("complete benchmark-required review requires at least two measured competitors")
            for cid in measured_ids:
                refs_for_comp = competitor_comparison_refs.get(cid, set())
                if not any(evidence.get(ref, {}).get("evidence_class") == "competitor_observation" for ref in refs_for_comp):
                    errors.append(f"complete benchmark-required review requires competitor_observation evidence for {cid}")
            valid_comparative = False
            for cids, assessment_evidence, xid in comparative_assessments:
                if len(cids) < 2:
                    continue
                linked_observations = set().union(*(competitor_comparison_refs.get(cid, set()) for cid in cids))
                observed_refs = {
                    ref for ref in linked_observations
                    if evidence.get(ref, {}).get("evidence_class") == "competitor_observation"
                }
                if observed_refs and assessment_evidence.intersection(observed_refs):
                    valid_comparative = True
                    break
            if not valid_comparative:
                errors.append("complete benchmark-required review requires a comparative assessment citing actual competitor_observation evidence for at least two competitors")

        for axis in ["visual_craft", "color_system", "audience_fit"]:
            if axis not in axes_seen:
                errors.append(f"complete review missing {axis} assessment")

        material_journeys = [(jid, row) for jid, row in journeys.items() if row.get("criticality") in {"primary", "high_risk"}]
        for jid, journey in material_journeys:
            if journey.get("status") in {"partial", "blocked", "not_tested"}:
                errors.append(f"complete review has incomplete material journey {jid}")
            if not experiences_by_journey.get(jid):
                errors.append(f"complete material journey {jid} has no experience assessment")
            if interactive:
                missing = {"narrow_mobile", "desktop"} - observed_views.get(jid, set())
                if missing:
                    errors.append(f"complete material journey {jid} missing viewports: {sorted(missing)}")
                if "pointer_touch" not in observed_modes.get(jid, set()):
                    errors.append(f"complete material journey {jid} missing pointer/touch coverage")
        if interactive and not any(obj(row) and row.get("mode") == "keyboard" and row.get("status") == "observed" for row in input_rows):
            errors.append("complete interactive review requires representative keyboard coverage")
        if audit.get("production_locator") and audit.get("production_revision_status") == "unverified":
            errors.append("complete public review cannot have unverified production revision")
        if not any(row.get("evidence_class") == "rendered_observation" for row in evidence.values()):
            errors.append("complete review requires rendered observation evidence")

    validator = coverage.get("validator")
    if not obj(validator) or validator.get("status") not in {"passed", "pending"} or not text(validator.get("name")) or not text(validator.get("validated_at")):
        errors.append("coverage.validator invalid")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print(f"UX/UI teardown validation failed with {len(errors)} error(s):")
        for error in errors[:150]:
            print("-", error)
        return 1
    print("ux-ui-teardown validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
