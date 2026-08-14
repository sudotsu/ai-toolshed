#!/usr/bin/env python3
"""Validate an SEO teardown's deterministic, evidence-calibrated handoff contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from render_handoff import rendered_files

class _HardenedList(list):
    """List that is hashable by identity.

    Canonical JSON is untrusted. A list appearing where a scalar belongs would
    otherwise raise TypeError the moment it reaches a set membership test, a
    dict key, or Counter, aborting validation with a traceback instead of a
    bounded error list. Hashing by identity makes those operations succeed and
    return "not a member", so the surrounding check reports a normal
    invalid-value error. isinstance(x, list) is unaffected, so every existing
    type check still behaves identically.
    """

    __slots__ = ()
    __hash__ = object.__hash__


class _HardenedDict(dict):
    """Dict that is hashable by identity. See _HardenedList."""

    __slots__ = ()
    __hash__ = object.__hash__


def harden_json(value):
    """Recursively replace JSON containers with identity-hashable equivalents."""
    if isinstance(value, dict):
        return _HardenedDict((key, harden_json(item)) for key, item in value.items())
    if isinstance(value, list):
        return _HardenedList(harden_json(item) for item in value)
    return value

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

REQUIRED_FILES = (
    "README.md",
    "00-executive-verdict.md",
    "01-search-business-model.md",
    "02-evidence-and-access.md",
    "03-live-search-and-competitors.md",
    "04-technical-discovery-indexation.md",
    "05-content-entity-authority.md",
    "06-platform-and-vertical-modules.md",
    "07-measurement-and-experiments.md",
    "08-owner-decisions-and-blockers.md",
    "09-implementation-sequence.md",
    "10-review-coverage.md",
    "11-findings-register.md",
    "findings.json",
    "coverage.json",
)

NARRATIVE_FILES = (
    "00-executive-verdict.md",
    "01-search-business-model.md",
    "02-evidence-and-access.md",
    "03-live-search-and-competitors.md",
    "04-technical-discovery-indexation.md",
    "05-content-entity-authority.md",
    "06-platform-and-vertical-modules.md",
    "07-measurement-and-experiments.md",
    "08-owner-decisions-and-blockers.md",
)

ACCESS_CATEGORIES = ControlledValues({
    "source_repository",
    "production_website",
    "google_search_console",
    "bing_webmaster_tools",
    "analytics",
    "crawl_logs",
    "google_business_profile",
    "merchant_feeds",
    "rank_tracking",
    "conversion_records",
    "location_serp_testing",
})

MODULE_IDS = ControlledValues({
    "business_search_model",
    "live_search",
    "crawl_render_index",
    "information_architecture",
    "content_evidence",
    "ai_discovery",
    "structured_data",
    "entity_authority",
    "local_seo",
    "performance_experience_accessibility",
    "vertical_systems",
    "search_policy_risk",
    "measurement_experimentation",
    "strategy_prioritization",
})

EVIDENCE_CLASSES = ControlledValues({
    "official_documentation",
    "first_party_data",
    "controlled_test",
    "direct_observation",
    "strong_inference",
    "industry_correlation",
    "unverified_theory",
})

CONTROLLED = {
    "review_status": {"complete", "provisional"},
    "kind": {"defect", "shortcoming", "opportunity", "investigation", "experiment", "strength", "risk"},
    "status": {"open", "blocked", "decision_required", "accepted_risk", "passed"},
    "severity": {"critical", "high", "medium", "low", "informational"},
    "confidence": {"confirmed", "high", "medium", "low"},
    "claim_basis": {
        "documented_eligibility",
        "demonstrated_harm",
        "credible_opportunity",
        "policy_exposure",
        "hypothesis",
        "preserved_strength",
    },
    "likelihood": {"near_certain", "likely", "plausible", "unknown"},
    "action": {
        "fix",
        "add",
        "change",
        "consolidate",
        "remove",
        "preserve",
        "investigate",
        "experiment",
        "decide",
        "accept",
        "leave_alone",
    },
    "expected_business_value": {"very_high", "high", "medium", "low", "unknown"},
    "effort": {"trivial", "small", "medium", "large", "initiative", "unknown"},
    "reversibility": {"easy", "moderate", "hard", "unknown"},
    "time_to_evidence": {"immediate", "days", "weeks", "months", "unknown"},
    "downside": {"high", "medium", "low", "unknown"},
    "disposition": {
        "implement",
        "investigate",
        "experiment",
        "decide",
        "preserve",
        "accept_risk",
        "defer",
        "leave_alone",
    },
    "access_status": {"available", "partial", "blocked", "not_applicable"},
    "module_status": {"passed", "failed", "partial", "blocked", "not_tested", "not_applicable"},
    "materiality": {"defining", "high", "medium", "low"},
    "production_revision_status": {"verified", "unverified", "not_applicable"},
    "evidence_role": {"supports", "contradicts", "context"},
    "technical_eligibility": {"eligible", "ineligible", "partial", "unknown", "not_applicable"},
    "observed_performance": {"present", "absent_in_sample", "mixed", "unknown", "not_applicable"},
    "consequence_type": {"eligibility", "observed_visibility", "conversion", "policy", "trust", "quality", "measurement", "none"},
    "funnel_stage": {"discovery", "comparison", "decision", "conversion", "retention", "post_purchase", "not_applicable"},
    "qualifiedness": {"qualified", "proxy", "unknown", "not_applicable"},
    "measurement_status": {"measured", "partial", "blocked", "not_applicable"},
    "verification_mode": {"source", "rendered", "live", "platform_data", "controlled_test", "mixed"},
    "check_method": {"source_inspection", "live_fetch", "rendered_browser", "controlled_test", "platform_data", "serp_observation", "first_party_analysis", "external_research"},
    "check_status": {"passed", "failed", "partial", "blocked", "not_applicable"},
    "target_observation": {"present", "absent", "mixed", "not_observed"},
    "source_revision_alignment": {"matched", "mismatched", "unverified", "not_applicable"},
    "index_eligibility": {"eligible", "ineligible", "partial", "unknown", "not_applicable"},
    "observed_index_state": {"indexed", "not_seen_in_sample", "mixed", "unknown", "not_applicable"},
    "winner_observation_status": {"observed", "unavailable", "not_applicable"},
    "winner_kind": {"domain", "url", "named_entity"},
    "method_status": {"completed", "failed", "blocked", "not_applicable"},
    "url_observation_status": {"observed", "unavailable", "not_applicable"},
}

CHECK_ID = re.compile(r"^CHECK-\d{3}$")
SERP_ID = re.compile(r"^SERP-\d{3}$")
URL_SAMPLE_ID = re.compile(r"^URL-\d{3}$")
LIMITATION_ID = re.compile(r"^LIMIT-\d{3}$")
HOSTNAME = re.compile(r"^(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$")
GENERIC_WINNER_LABELS = ControlledValues({
    "competitors", "local competitors", "publishers", "strategy publishers",
    "cost publishers", "tools", "generators",
    "local service sites", "service sites", "websites", "sites",
    "third-party listings", "directories", "forums", "blogs",
})

MODULE_FACETS = {
    "business_search_model": {"audience_geography", "funnel_value", "qualified_conversion", "intent_demand"},
    "live_search": {"query_sampling", "result_features", "actual_competitors", "target_presence"},
    "crawl_render_index": {"robots_controls", "sitemaps", "canonicals_http", "render_discoverability", "production_index_evidence"},
    "information_architecture": {"taxonomy_navigation", "internal_links", "template_scale_or_orphans", "query_page_overlap"},
    "content_evidence": {"intent_satisfaction", "originality_information_gain", "claim_support", "authorship_review", "duplication_scaled_risk"},
    "ai_discovery": {"crawler_controls", "ordinary_eligibility", "passage_source_clarity", "observability"},
    "structured_data": {"syntax_presence", "content_parity", "platform_eligibility", "entity_graph"},
    "entity_authority": {"identity_consistency", "reputation_reviews", "mentions_links"},
    "local_seo": {"gbp_state", "nap_alignment", "local_serp", "local_landing_pages", "local_conversion"},
    "performance_experience_accessibility": {"field_data", "lab_or_source", "mobile_accessibility", "conversion_friction"},
    "vertical_systems": {"vertical_requirements", "feeds_or_data", "policy_or_rights"},
    "search_policy_risk": {"spam_policy", "security_manual_action", "regulated_legal", "structured_data_policy"},
    "measurement_experimentation": {"stack_inventory", "baseline", "qualified_conversion", "attribution_zero_click", "experiments"},
    "strategy_prioritization": {"dependency_order", "business_value", "preserved_strengths", "deliberate_non_pursuits"},
}

FINDING_ID = re.compile(r"^[A-Z][A-Z0-9]*-\d{3}$")
EVIDENCE_ID = re.compile(r"^EVID-\d{3}$")
REVIEW_STATUS_LINE = re.compile(r"^\*\*Review status:\*\*\s*(complete|provisional)\s*$", re.MULTILINE)
ID_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*-\d{3}\b")
NOT_APPLICABLE = re.compile(r"^Not applicable — .+")

FINDING_REQUIRED = (
    "id",
    "title",
    "kind",
    "domain",
    "status",
    "severity",
    "confidence",
    "evidence_quality",
    "claim_basis",
    "likelihood",
    "action",
    "business_impact",
    "search_consequence",
    "affected_queries",
    "affected_urls_or_entities",
    "platforms",
    "evidence_ids",
    "reproduction",
    "root_cause",
    "recommendation",
    "if_implemented",
    "if_unchanged",
    "acceptance_criteria",
    "verification",
    "dependencies",
    "conflicts",
    "blocker",
    "owner_decision",
    "priority",
    "measurement",
    "implementation",
    "evidence_links",
    "search_state",
    "conversion_linkage",
    "implementation_scope",
    "verification_context",
)

PRIORITY_REQUIRED = (
    "expected_business_value",
    "effort",
    "reversibility",
    "time_to_evidence",
    "downside",
)

MEASUREMENT_REQUIRED = (
    "baseline",
    "primary_metric",
    "guardrail_metrics",
    "time_horizon",
    "confounders",
    "rollback_criteria",
    "decision_rule",
)

IMPLEMENTATION_REQUIRED = (
    "phase_id",
    "order",
    "disposition",
    "rationale",
    "validation_gate",
)


def load_object(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = harden_json(json.load(handle))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read valid JSON from {path.name}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path.name} must contain a JSON object")
        return {}
    return data


def parse_iso(value: Any, label: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be a YYYY-MM-DD string")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} has invalid date: {value!r}")
        return None


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_na(value: Any) -> bool:
    return isinstance(value, str) and bool(NOT_APPLICABLE.match(value.strip()))


def require_fields(obj: dict[str, Any], fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    missing = [field for field in fields if field not in obj]
    if missing:
        errors.append(f"{label} missing fields: {', '.join(missing)}")


def validate_audit(findings_data: dict[str, Any], errors: list[str]) -> tuple[date | None, int, str | None]:
    if findings_data.get("schema_version") != "seo-teardown-v3":
        errors.append("findings.json schema_version must be 'seo-teardown-v3'")
    audit = findings_data.get("audit")
    if not isinstance(audit, dict):
        errors.append("findings.json audit must be an object")
        return None, 0, None
    required = (
        "project_name",
        "project_locator",
        "audited_revision",
        "production_locator",
        "audit_start_date",
        "audit_end_date",
        "research_window_days",
        "review_status",
        "business_model",
        "primary_geographies",
        "production_revision_status",
        "production_revision_evidence_ids",
    )
    require_fields(audit, required, "audit", errors)
    for field in ("project_name", "project_locator", "audited_revision", "production_locator", "business_model"):
        if field in audit and not nonempty_string(audit[field]):
            errors.append(f"audit.{field} must be non-empty text")
    status = audit.get("review_status")
    if status not in CONTROLLED["review_status"]:
        errors.append(f"audit.review_status has invalid value: {status!r}")
    start = parse_iso(audit.get("audit_start_date"), "audit.audit_start_date", errors)
    end = parse_iso(audit.get("audit_end_date"), "audit.audit_end_date", errors)
    if start and end and start > end:
        errors.append("audit_start_date must not be after audit_end_date")
    window = audit.get("research_window_days")
    if not isinstance(window, int) or isinstance(window, bool) or not 1 <= window <= 30:
        errors.append("audit.research_window_days must be an integer from 1 to 30")
        window = 0
    geographies = audit.get("primary_geographies")
    if not isinstance(geographies, list) or not geographies or not all(nonempty_string(item) for item in geographies):
        errors.append("audit.primary_geographies must be a non-empty list of strings")
    return end, window, status if isinstance(status, str) else None


def validate_evidence(
    findings_data: dict[str, Any], audit_end: date | None, research_window: int, errors: list[str]
) -> dict[str, dict[str, Any]]:
    items = findings_data.get("evidence_sources")
    if not isinstance(items, list) or not items:
        errors.append("findings.json evidence_sources must be a non-empty list")
        return {}
    evidence_map: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items, start=1):
        label = f"evidence_sources[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        required = (
            "id",
            "evidence_class",
            "title",
            "publisher_or_owner",
            "locator",
            "accessed_at",
            "platform_sensitive",
            "summary",
            "limitations",
            "artifact_path",
        )
        require_fields(item, required, label, errors)
        evid = item.get("id")
        if not isinstance(evid, str) or not EVIDENCE_ID.fullmatch(evid):
            errors.append(f"{label}.id is invalid: {evid!r}")
            continue
        if evid in evidence_map:
            errors.append(f"duplicate evidence ID: {evid}")
        evidence_map[evid] = item
        if item.get("evidence_class") not in EVIDENCE_CLASSES:
            errors.append(f"{evid} has invalid evidence_class: {item.get('evidence_class')!r}")
        for field in ("title", "publisher_or_owner", "locator", "summary", "limitations"):
            if not nonempty_string(item.get(field)):
                errors.append(f"{evid}.{field} must be non-empty text")
        artifact = item.get("artifact_path")
        if artifact is not None and not nonempty_string(artifact):
            errors.append(f"{evid}.artifact_path must be text or null")
        if not isinstance(item.get("platform_sensitive"), bool):
            errors.append(f"{evid}.platform_sensitive must be boolean")
        accessed = parse_iso(item.get("accessed_at"), f"{evid}.accessed_at", errors)
        if accessed and audit_end:
            if accessed > audit_end:
                errors.append(f"{evid} accessed_at is after audit_end_date")
            if item.get("platform_sensitive") is True and research_window:
                earliest = audit_end - timedelta(days=research_window)
                if accessed < earliest:
                    errors.append(
                        f"{evid} platform-sensitive evidence is stale for the declared research window"
                    )
    return evidence_map


def validate_findings(
    findings_data: dict[str, Any], evidence_map: dict[str, dict[str, Any]], errors: list[str]
) -> dict[str, dict[str, Any]]:
    items = findings_data.get("findings")
    if not isinstance(items, list) or not items:
        errors.append("findings.json findings must be a non-empty list")
        return {}
    finding_map: dict[str, dict[str, Any]] = {}
    orders: dict[int, str] = {}
    for index, item in enumerate(items, start=1):
        label = f"findings[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        require_fields(item, FINDING_REQUIRED, label, errors)
        fid = item.get("id")
        if not isinstance(fid, str) or not FINDING_ID.fullmatch(fid):
            errors.append(f"{label}.id is invalid: {fid!r}")
            continue
        if fid in finding_map:
            errors.append(f"duplicate finding ID: {fid}")
        finding_map[fid] = item

        for field in ("title", "domain", "business_impact", "search_consequence", "reproduction", "root_cause", "recommendation", "if_implemented", "if_unchanged"):
            if not nonempty_string(item.get(field)):
                errors.append(f"{fid}.{field} must be non-empty text")

        for field in ("kind", "status", "severity", "confidence", "claim_basis", "likelihood", "action"):
            if item.get(field) not in CONTROLLED[field]:
                errors.append(f"{fid} has invalid {field}: {item.get(field)!r}")
        if item.get("evidence_quality") not in EVIDENCE_CLASSES:
            errors.append(f"{fid} has invalid evidence_quality: {item.get('evidence_quality')!r}")

        for field in ("affected_queries", "affected_urls_or_entities"):
            value = item.get(field)
            if value is not None and (not isinstance(value, list) or not all(nonempty_string(v) for v in value)):
                errors.append(f"{fid}.{field} must be a list of non-empty strings or null")
        for field in ("platforms", "evidence_ids", "acceptance_criteria", "verification", "dependencies", "conflicts"):
            value = item.get(field)
            if not isinstance(value, list):
                errors.append(f"{fid}.{field} must be a list")
            elif field in {"platforms", "evidence_ids", "acceptance_criteria", "verification"} and not value:
                errors.append(f"{fid}.{field} must not be empty")
            elif not all(nonempty_string(v) for v in value):
                errors.append(f"{fid}.{field} must contain only non-empty strings")

        referenced_evidence_classes: set[str] = set()
        for evid in item.get("evidence_ids", []) if isinstance(item.get("evidence_ids"), list) else []:
            if evid not in evidence_map:
                errors.append(f"{fid} references unknown evidence ID: {evid}")
            else:
                evidence_class = evidence_map[evid].get("evidence_class")
                if isinstance(evidence_class, str):
                    referenced_evidence_classes.add(evidence_class)
        if item.get("evidence_quality") in EVIDENCE_CLASSES and item.get("evidence_quality") not in referenced_evidence_classes:
            errors.append(
                f"{fid} evidence_quality {item.get('evidence_quality')!r} is not represented by a referenced evidence source"
            )

        if item.get("kind") == "strength":
            if not (
                item.get("severity") == "informational"
                and item.get("status") == "passed"
                and item.get("action") == "preserve"
                and item.get("claim_basis") == "preserved_strength"
            ):
                errors.append(f"{fid} strength must be informational, passed, preserve, preserved_strength")
        if item.get("claim_basis") == "hypothesis" and item.get("kind") not in {"investigation", "experiment"}:
            errors.append(f"{fid} hypothesis must be an investigation or experiment")
        if item.get("kind") == "experiment" and item.get("severity") in {"critical", "high"}:
            errors.append(f"{fid} experiment cannot have critical or high severity")
        if item.get("evidence_quality") == "unverified_theory" and item.get("kind") not in {"investigation", "experiment"}:
            errors.append(f"{fid} unverified_theory may only support investigation or experiment")
        if item.get("severity") == "critical":
            if item.get("likelihood") not in {"near_certain", "likely"}:
                errors.append(f"{fid} critical severity requires likely or near_certain likelihood")
            if item.get("evidence_quality") in {"industry_correlation", "unverified_theory"}:
                errors.append(f"{fid} critical severity cannot rest on weak evidence quality")
        if item.get("status") == "blocked" and not nonempty_string(item.get("blocker")):
            errors.append(f"{fid} blocked status requires blocker text")
        if item.get("status") != "blocked" and item.get("blocker") is not None and not is_na(item.get("blocker")):
            errors.append(f"{fid} blocker must be null/Not applicable unless status is blocked")
        if item.get("status") == "decision_required" and not nonempty_string(item.get("owner_decision")):
            errors.append(f"{fid} decision_required status requires owner_decision text")
        if item.get("status") != "decision_required" and item.get("owner_decision") is not None and not is_na(item.get("owner_decision")):
            errors.append(f"{fid} owner_decision must be null/Not applicable unless decision_required")

        evidence_links = item.get("evidence_links")
        if not isinstance(evidence_links, list) or not evidence_links:
            errors.append(f"{fid}.evidence_links must be a non-empty list")
        else:
            linked_ids: list[str] = []
            support_count = 0
            for link_index, link in enumerate(evidence_links, start=1):
                link_label = f"{fid}.evidence_links[{link_index}]"
                if not isinstance(link, dict):
                    errors.append(f"{link_label} must be an object")
                    continue
                require_fields(link, ("evidence_id", "role", "claim"), link_label, errors)
                evid = link.get("evidence_id")
                if not nonempty_string(evid):
                    errors.append(f"{link_label}.evidence_id must be an evidence ID string")
                    continue
                linked_ids.append(evid)
                if evid not in evidence_map:
                    errors.append(f"{link_label} references unknown evidence ID: {evid}")
                if link.get("role") not in CONTROLLED["evidence_role"]:
                    errors.append(f"{link_label}.role has invalid value: {link.get('role')!r}")
                if link.get("role") == "supports":
                    support_count += 1
                if not nonempty_string(link.get("claim")):
                    errors.append(f"{link_label}.claim must be non-empty text")
            evidence_ids = item.get("evidence_ids") if isinstance(item.get("evidence_ids"), list) else []
            if Counter(linked_ids) != Counter(evidence_ids):
                errors.append(f"{fid}.evidence_links must account for each evidence_id exactly once")
            if support_count == 0:
                errors.append(f"{fid}.evidence_links needs at least one supports entry")

        search_state = item.get("search_state")
        if not isinstance(search_state, dict):
            errors.append(f"{fid}.search_state must be an object")
        else:
            require_fields(search_state, ("technical_eligibility", "observed_performance", "consequence_type"), f"{fid}.search_state", errors)
            for field in ("technical_eligibility", "observed_performance", "consequence_type"):
                if search_state.get(field) not in CONTROLLED[field]:
                    errors.append(f"{fid}.search_state.{field} has invalid value: {search_state.get(field)!r}")
            if search_state.get("observed_performance") in {"present", "absent_in_sample", "mixed"}:
                observational = {"direct_observation", "first_party_data", "controlled_test"}
                if not referenced_evidence_classes.intersection(observational):
                    errors.append(f"{fid} observed_performance requires observational or first-party evidence")

        conversion = item.get("conversion_linkage")
        if not isinstance(conversion, dict):
            errors.append(f"{fid}.conversion_linkage must be an object")
        else:
            require_fields(conversion, ("conversion_target", "funnel_stage", "qualifiedness", "measurement_status"), f"{fid}.conversion_linkage", errors)
            for field in ("funnel_stage", "qualifiedness", "measurement_status"):
                if conversion.get(field) not in CONTROLLED[field]:
                    errors.append(f"{fid}.conversion_linkage.{field} has invalid value: {conversion.get(field)!r}")
            if conversion.get("funnel_stage") == "not_applicable":
                if not is_na(conversion.get("conversion_target")):
                    errors.append(f"{fid}.conversion_target must explain not applicability")
            elif not nonempty_string(conversion.get("conversion_target")):
                errors.append(f"{fid}.conversion_target must be non-empty text")

        scope = item.get("implementation_scope")
        if not isinstance(scope, dict):
            errors.append(f"{fid}.implementation_scope must be an object")
        else:
            require_fields(scope, ("targets", "non_goals", "owner_or_external_actions"), f"{fid}.implementation_scope", errors)
            for field in ("targets", "non_goals", "owner_or_external_actions"):
                value = scope.get(field)
                if not isinstance(value, list) or not all(nonempty_string(v) for v in value):
                    errors.append(f"{fid}.implementation_scope.{field} must be a list of strings")
            if isinstance(scope.get("targets"), list) and not scope.get("targets"):
                errors.append(f"{fid}.implementation_scope.targets must not be empty")
            if isinstance(scope.get("non_goals"), list) and not scope.get("non_goals"):
                errors.append(f"{fid}.implementation_scope.non_goals must not be empty")
            if item.get("status") == "blocked" and not scope.get("owner_or_external_actions"):
                errors.append(f"{fid} blocked finding needs an owner_or_external_action")

        verification_context = item.get("verification_context")
        if not isinstance(verification_context, dict):
            errors.append(f"{fid}.verification_context must be an object")
        else:
            require_fields(verification_context, ("mode", "environment", "limitations"), f"{fid}.verification_context", errors)
            if verification_context.get("mode") not in CONTROLLED["verification_mode"]:
                errors.append(f"{fid}.verification_context.mode has invalid value: {verification_context.get('mode')!r}")
            if not nonempty_string(verification_context.get("environment")):
                errors.append(f"{fid}.verification_context.environment must be non-empty text")
            if not isinstance(verification_context.get("limitations"), list) or not all(nonempty_string(v) for v in verification_context.get("limitations", [])):
                errors.append(f"{fid}.verification_context.limitations must be a list of strings")
            if verification_context.get("mode") == "source" and isinstance(search_state, dict) and search_state.get("observed_performance") not in {"unknown", "not_applicable"}:
                errors.append(f"{fid} source-only verification cannot claim observed search performance")

        priority = item.get("priority")
        if not isinstance(priority, dict):
            errors.append(f"{fid}.priority must be an object")
        else:
            require_fields(priority, PRIORITY_REQUIRED, f"{fid}.priority", errors)
            for field in PRIORITY_REQUIRED:
                if priority.get(field) not in CONTROLLED[field]:
                    errors.append(f"{fid}.priority.{field} has invalid value: {priority.get(field)!r}")

        measurement = item.get("measurement")
        if not isinstance(measurement, dict):
            errors.append(f"{fid}.measurement must be an object")
        else:
            require_fields(measurement, MEASUREMENT_REQUIRED, f"{fid}.measurement", errors)
            for field in ("guardrail_metrics", "confounders"):
                if not isinstance(measurement.get(field), list) or not all(nonempty_string(v) for v in measurement.get(field, [])):
                    errors.append(f"{fid}.measurement.{field} must be a list of strings")
            for field in ("baseline", "primary_metric", "time_horizon", "rollback_criteria", "decision_rule"):
                if not nonempty_string(measurement.get(field)):
                    errors.append(f"{fid}.measurement.{field} must be non-empty text")
            if item.get("kind") in {"opportunity", "investigation", "experiment"}:
                if is_na(measurement.get("primary_metric")) or is_na(measurement.get("decision_rule")):
                    errors.append(f"{fid} {item.get('kind')} requires a real primary metric and decision rule")

        implementation = item.get("implementation")
        if not isinstance(implementation, dict):
            errors.append(f"{fid}.implementation must be an object")
        else:
            require_fields(implementation, IMPLEMENTATION_REQUIRED, f"{fid}.implementation", errors)
            if implementation.get("disposition") not in CONTROLLED["disposition"]:
                errors.append(f"{fid} has invalid implementation disposition: {implementation.get('disposition')!r}")
            order = implementation.get("order")
            if not isinstance(order, int) or isinstance(order, bool) or order <= 0:
                errors.append(f"{fid}.implementation.order must be a positive integer")
            elif order in orders:
                errors.append(f"duplicate implementation order {order}: {orders[order]} and {fid}")
            else:
                orders[order] = fid
            for field in ("phase_id", "rationale", "validation_gate"):
                if not nonempty_string(implementation.get(field)):
                    errors.append(f"{fid}.implementation.{field} must be non-empty text")
            if item.get("kind") == "strength" and implementation.get("disposition") != "preserve":
                errors.append(f"{fid} strength must use preserve disposition")
            if item.get("status") == "accepted_risk" and implementation.get("disposition") != "accept_risk":
                errors.append(f"{fid} accepted_risk status must use accept_risk disposition")
            if item.get("status") == "decision_required" and implementation.get("disposition") != "decide":
                errors.append(f"{fid} decision_required status must use decide disposition")
            if item.get("kind") == "experiment" and implementation.get("disposition") != "experiment":
                errors.append(f"{fid} experiment kind must use experiment disposition")
    # Reject placeholder prose that makes a structurally valid finding unusable by a revision agent.
    prohibited_fragments = (
        "the documented consequence is removed",
        "the documented harm, uncertainty, or opportunity cost remains",
        "observed current state is documented in the cited evidence",
        "project-specific qualified conversion or search metric named in the finding",
        "proceed only when the stated evidence threshold or metric supports the hypothesis",
    )
    for fid, item in finding_map.items():
        candidates = [
            item.get("if_implemented"),
            item.get("if_unchanged"),
            item.get("measurement", {}).get("baseline") if isinstance(item.get("measurement"), dict) else None,
            item.get("measurement", {}).get("primary_metric") if isinstance(item.get("measurement"), dict) else None,
            item.get("measurement", {}).get("decision_rule") if isinstance(item.get("measurement"), dict) else None,
        ]
        for value in candidates:
            lowered = value.lower() if isinstance(value, str) else ""
            if any(fragment in lowered for fragment in prohibited_fragments):
                errors.append(f"{fid} contains placeholder implementation-readiness language")
                break

    if len(finding_map) >= 4:
        for field_name, extractor in (
            ("if_implemented", lambda x: x.get("if_implemented")),
            ("if_unchanged", lambda x: x.get("if_unchanged")),
            ("measurement.baseline", lambda x: x.get("measurement", {}).get("baseline") if isinstance(x.get("measurement"), dict) else None),
        ):
            values = [extractor(item) for item in finding_map.values()]
            counts = Counter(value for value in values if nonempty_string(value))
            repeated = [value for value, count in counts.items() if count > max(2, len(finding_map) // 2)]
            if repeated:
                errors.append(f"findings contain excessive repeated boilerplate in {field_name}")
    return finding_map


def validate_graph_and_phases(findings_data: dict[str, Any], finding_map: dict[str, dict[str, Any]], errors: list[str]) -> None:
    phase_items = findings_data.get("implementation_phases")
    if not isinstance(phase_items, list) or not phase_items:
        errors.append("implementation_phases must be a non-empty list")
        return
    phase_map: dict[str, dict[str, Any]] = {}
    phase_membership: list[str] = []
    for index, phase in enumerate(phase_items, start=1):
        label = f"implementation_phases[{index}]"
        if not isinstance(phase, dict):
            errors.append(f"{label} must be an object")
            continue
        required = ("id", "title", "rationale", "finding_ids", "validation_gate", "expected_outcome")
        require_fields(phase, required, label, errors)
        pid = phase.get("id")
        if not nonempty_string(pid):
            errors.append(f"{label}.id must be non-empty text")
            continue
        if pid in phase_map:
            errors.append(f"duplicate implementation phase ID: {pid}")
        phase_map[pid] = phase
        for field in ("title", "rationale", "validation_gate", "expected_outcome"):
            if not nonempty_string(phase.get(field)):
                errors.append(f"{pid}.{field} must be non-empty text")
        ids = phase.get("finding_ids")
        if not isinstance(ids, list) or not ids or not all(nonempty_string(fid) for fid in ids):
            errors.append(f"{pid}.finding_ids must be a non-empty list of IDs")
            continue
        phase_membership.extend(ids)
        orders = []
        for fid in ids:
            if fid not in finding_map:
                errors.append(f"{pid} references unknown finding: {fid}")
                continue
            finding = finding_map[fid]
            implementation = finding.get("implementation", {})
            if implementation.get("phase_id") != pid:
                errors.append(f"{fid} phase_id disagrees with implementation phase {pid}")
            order = implementation.get("order")
            if isinstance(order, int):
                orders.append(order)
        if orders != sorted(orders):
            errors.append(f"{pid}.finding_ids are not in implementation order")

    membership_counts = Counter(phase_membership)
    missing = sorted(set(finding_map) - set(phase_membership))
    unknown = sorted(set(phase_membership) - set(finding_map))
    repeated = sorted(fid for fid, count in membership_counts.items() if count != 1)
    if missing:
        errors.append(f"findings missing from implementation phases: {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown findings in implementation phases: {', '.join(unknown)}")
    if repeated:
        errors.append(f"findings repeated in implementation phases: {', '.join(repeated)}")

    graph: dict[str, list[str]] = {}
    for fid, finding in finding_map.items():
        deps = finding.get("dependencies") if isinstance(finding.get("dependencies"), list) else []
        conflicts = finding.get("conflicts") if isinstance(finding.get("conflicts"), list) else []
        graph[fid] = []
        for dep in deps:
            if dep == fid:
                errors.append(f"{fid} cannot depend on itself")
            elif dep not in finding_map:
                errors.append(f"{fid} depends on unknown finding: {dep}")
            else:
                graph[fid].append(dep)
                current_order = finding.get("implementation", {}).get("order")
                dep_order = finding_map[dep].get("implementation", {}).get("order")
                if isinstance(current_order, int) and isinstance(dep_order, int) and dep_order >= current_order:
                    errors.append(f"{fid} dependency {dep} does not appear earlier in implementation order")
        for conflict in conflicts:
            if conflict == fid:
                errors.append(f"{fid} cannot conflict with itself")
            elif conflict not in finding_map:
                errors.append(f"{fid} conflicts with unknown finding: {conflict}")
            else:
                other = finding_map[conflict].get("conflicts", [])
                if not isinstance(other, list) or fid not in other:
                    errors.append(f"conflict must be symmetric: {fid} <-> {conflict}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visited:
            return
        if node in visiting:
            cycle_start = trail.index(node) if node in trail else 0
            cycle = trail[cycle_start:] + [node]
            errors.append(f"dependency cycle detected: {' -> '.join(cycle)}")
            return
        visiting.add(node)
        trail.append(node)
        for dep in graph.get(node, []):
            visit(dep, trail)
        trail.pop()
        visiting.remove(node)
        visited.add(node)

    for fid in graph:
        visit(fid, [])


def validate_coverage(
    coverage_data: dict[str, Any],
    finding_map: dict[str, dict[str, Any]],
    evidence_map: dict[str, dict[str, Any]],
    audit_status: str | None,
    errors: list[str],
) -> None:
    if coverage_data.get("schema_version") != "seo-teardown-coverage-v3":
        errors.append("coverage.json schema_version must be 'seo-teardown-coverage-v3'")
    coverage_status = coverage_data.get("review_status")
    if coverage_status not in CONTROLLED["review_status"]:
        errors.append(f"coverage.review_status has invalid value: {coverage_status!r}")
    if audit_status and coverage_status != audit_status:
        errors.append("review status differs between findings.json audit and coverage.json")

    access = coverage_data.get("access")
    seen_access: list[str] = []
    provisional_reasons: list[str] = []
    if not isinstance(access, list):
        errors.append("coverage.access must be a list")
    else:
        for index, item in enumerate(access, start=1):
            label = f"coverage.access[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            required = (
                "category",
                "status",
                "coverage_window",
                "material_to_comprehensive",
                "evidence_ids",
                "limitations",
                "next_step",
            )
            require_fields(item, required, label, errors)
            category = item.get("category")
            seen_access.append(category)
            if category not in ACCESS_CATEGORIES:
                errors.append(f"{label} has invalid category: {category!r}")
            if item.get("status") not in CONTROLLED["access_status"]:
                errors.append(f"{category} has invalid access status: {item.get('status')!r}")
            if not isinstance(item.get("material_to_comprehensive"), bool):
                errors.append(f"{category}.material_to_comprehensive must be boolean")
            for field in ("evidence_ids", "limitations"):
                if not isinstance(item.get(field), list) or not all(nonempty_string(v) for v in item.get(field, [])):
                    errors.append(f"{category}.{field} must be a list of strings")
            for evid in item.get("evidence_ids", []) if isinstance(item.get("evidence_ids"), list) else []:
                if evid not in evidence_map:
                    errors.append(f"{category} references unknown evidence ID: {evid}")
            for field in ("coverage_window", "next_step"):
                if not nonempty_string(item.get(field)):
                    errors.append(f"{category}.{field} must be non-empty text")
            if item.get("material_to_comprehensive") is True and item.get("status") in {"partial", "blocked"}:
                provisional_reasons.append(f"material access {category} is {item.get('status')}")
            if item.get("material_to_comprehensive") is True and item.get("status") == "not_applicable":
                errors.append(f"{category} cannot be material_to_comprehensive and not_applicable")
        counts = Counter(seen_access)
        missing = sorted(ACCESS_CATEGORIES - set(seen_access))
        extra = sorted(set(seen_access) - ACCESS_CATEGORIES)
        duplicates = sorted(key for key, count in counts.items() if count > 1)
        if missing:
            errors.append(f"coverage access categories missing: {', '.join(missing)}")
        if extra:
            errors.append(f"unknown coverage access categories: {', '.join(str(x) for x in extra)}")
        if duplicates:
            errors.append(f"duplicate coverage access categories: {', '.join(str(x) for x in duplicates)}")

    modules = coverage_data.get("modules")
    seen_modules: list[str] = []
    finding_module_count: Counter[str] = Counter()
    if not isinstance(modules, list):
        errors.append("coverage.modules must be a list")
    else:
        for index, item in enumerate(modules, start=1):
            label = f"coverage.modules[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            required = (
                "id",
                "applicable",
                "materiality",
                "status",
                "finding_ids",
                "evidence_ids",
                "limitations",
                "next_step",
            )
            require_fields(item, required, label, errors)
            module_id = item.get("id")
            seen_modules.append(module_id)
            if module_id not in MODULE_IDS:
                errors.append(f"{label} has invalid module id: {module_id!r}")
            if not isinstance(item.get("applicable"), bool):
                errors.append(f"{module_id}.applicable must be boolean")
            if item.get("materiality") not in CONTROLLED["materiality"]:
                errors.append(f"{module_id} has invalid materiality: {item.get('materiality')!r}")
            if item.get("status") not in CONTROLLED["module_status"]:
                errors.append(f"{module_id} has invalid status: {item.get('status')!r}")
            for field in ("finding_ids", "evidence_ids", "limitations"):
                if not isinstance(item.get(field), list) or not all(nonempty_string(v) for v in item.get(field, [])):
                    errors.append(f"{module_id}.{field} must be a list of strings")
            if not nonempty_string(item.get("next_step")):
                errors.append(f"{module_id}.next_step must be non-empty text")
            for fid in item.get("finding_ids", []) if isinstance(item.get("finding_ids"), list) else []:
                if fid not in finding_map:
                    errors.append(f"{module_id} references unknown finding ID: {fid}")
                else:
                    finding_module_count[fid] += 1
            for evid in item.get("evidence_ids", []) if isinstance(item.get("evidence_ids"), list) else []:
                if evid not in evidence_map:
                    errors.append(f"{module_id} references unknown evidence ID: {evid}")
            applicable = item.get("applicable")
            status = item.get("status")
            if applicable is False and status != "not_applicable":
                errors.append(f"{module_id} non-applicable module must use not_applicable status")
            if applicable is True and status == "not_applicable":
                errors.append(f"{module_id} applicable module cannot use not_applicable status")
            if status in {"failed", "partial", "blocked"} and not item.get("finding_ids") and not item.get("limitations"):
                errors.append(f"{module_id} {status} module needs a finding or limitation")
            if applicable is True and item.get("materiality") in {"defining", "high"} and status in {"partial", "blocked", "not_tested"}:
                provisional_reasons.append(f"{item.get('materiality')} module {module_id} is {status}")
        counts = Counter(seen_modules)
        missing = sorted(MODULE_IDS - set(seen_modules))
        extra = sorted(set(seen_modules) - MODULE_IDS)
        duplicates = sorted(key for key, count in counts.items() if count > 1)
        if missing:
            errors.append(f"coverage modules missing: {', '.join(missing)}")
        if extra:
            errors.append(f"unknown coverage modules: {', '.join(str(x) for x in extra)}")
        if duplicates:
            errors.append(f"duplicate coverage modules: {', '.join(str(x) for x in duplicates)}")
    unmapped = sorted(fid for fid in finding_map if finding_module_count[fid] == 0)
    if unmapped:
        errors.append(f"findings not mapped to any coverage module: {', '.join(unmapped)}")

    limitations = coverage_data.get("material_limitations")
    if not isinstance(limitations, list):
        errors.append("coverage.material_limitations must be a list")
    else:
        for index, item in enumerate(limitations, start=1):
            label = f"material_limitations[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            required = ("id", "description", "status", "completion_requirement")
            require_fields(item, required, label, errors)
            for field in ("id", "description", "status", "completion_requirement"):
                if not nonempty_string(item.get(field)):
                    errors.append(f"{label}.{field} must be non-empty text")
            if item.get("status") != "resolved":
                provisional_reasons.append(f"material limitation {item.get('id')} is unresolved")

    reconciliation = coverage_data.get("narrative_reconciliation")
    reconciled_files: set[str] = set()
    if not isinstance(reconciliation, list) or not reconciliation:
        errors.append("coverage.narrative_reconciliation must be a non-empty list")
    else:
        for index, item in enumerate(reconciliation, start=1):
            label = f"narrative_reconciliation[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            required = ("location", "finding_ids", "non_actionable_explanation")
            require_fields(item, required, label, errors)
            location = item.get("location")
            if not nonempty_string(location):
                errors.append(f"{label}.location must be non-empty text")
            else:
                for filename in NARRATIVE_FILES:
                    if str(location).startswith(filename):
                        reconciled_files.add(filename)
            ids = item.get("finding_ids")
            if not isinstance(ids, list) or not all(nonempty_string(v) for v in ids):
                errors.append(f"{label}.finding_ids must be a list of strings")
                ids = []
            for fid in ids:
                if fid not in finding_map:
                    errors.append(f"{label} references unknown finding: {fid}")
            explanation = item.get("non_actionable_explanation")
            if ids and explanation not in (None, "None") and not is_na(explanation):
                errors.append(f"{label} must not contain both finding IDs and a substantive non-actionable explanation")
            if not ids and not nonempty_string(explanation):
                errors.append(f"{label} needs finding IDs or a non-actionable explanation")
        missing_files = sorted(set(NARRATIVE_FILES) - reconciled_files)
        if missing_files:
            errors.append(f"narrative files missing reconciliation entries: {', '.join(missing_files)}")

    validator = coverage_data.get("validator")
    if not isinstance(validator, dict):
        errors.append("coverage.validator must be an object")
    else:
        if not nonempty_string(validator.get("command")) or "validate_seo_teardown.py" not in validator.get("command", ""):
            errors.append("coverage.validator.command must name validate_seo_teardown.py")
        if validator.get("result") != "passed":
            errors.append("coverage.validator.result must be 'passed' for delivery")

    if coverage_status == "complete" and provisional_reasons:
        errors.append("false complete status: " + "; ".join(provisional_reasons))



def normalized_prose(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def generic_winner(value: str) -> bool:
    normalized = normalized_prose(value).strip(" .,:;()[]")
    if normalized in GENERIC_WINNER_LABELS:
        return True
    generic_tokens = {
        "competitor", "competitors", "local", "service", "services", "site", "sites",
        "publisher", "publishers", "tool", "tools", "generator", "generators",
        "cost", "strategy", "education", "third-party",
        "listing", "listings", "directory", "directories", "forum", "forums", "blog", "blogs",
    }
    tokens = set(re.findall(r"[a-z0-9-]+", normalized))
    return bool(tokens) and tokens <= generic_tokens


def validate_v3_details(
    findings_data: dict[str, Any],
    coverage_data: dict[str, Any],
    finding_map: dict[str, dict[str, Any]],
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    audit = findings_data.get("audit", {})
    revision_status = audit.get("production_revision_status")
    if revision_status not in CONTROLLED["production_revision_status"]:
        errors.append(f"audit.production_revision_status has invalid value: {revision_status!r}")
    revision_evidence = audit.get("production_revision_evidence_ids")
    if not isinstance(revision_evidence, list) or not all(nonempty_string(v) for v in revision_evidence):
        errors.append("audit.production_revision_evidence_ids must be a list of strings")
        revision_evidence = []
    for evid in revision_evidence:
        if evid not in evidence_map:
            errors.append(f"audit production revision references unknown evidence ID: {evid}")
    if revision_status in {"verified", "unverified"} and not revision_evidence:
        errors.append(f"audit.production_revision_status {revision_status} requires evidence IDs")
    if audit.get("review_status") == "complete" and revision_status == "unverified":
        errors.append("false complete status: production revision is unverified")

    access_items = coverage_data.get("access") if isinstance(coverage_data.get("access"), list) else []
    access_map = {item.get("category"): item for item in access_items if isinstance(item, dict)}
    limitation_items = coverage_data.get("material_limitations") if isinstance(coverage_data.get("material_limitations"), list) else []
    limitation_map = {item.get("id"): item for item in limitation_items if isinstance(item, dict) and nonempty_string(item.get("id"))}

    modules = coverage_data.get("modules") if isinstance(coverage_data.get("modules"), list) else []
    module_map = {m.get("id"): m for m in modules if isinstance(m, dict)}
    checks = coverage_data.get("surface_checks")
    check_map: dict[str, dict[str, Any]] = {}
    module_check_ids: defaultdict[str, list[str]] = defaultdict(list)
    applicable_results: list[str] = []
    applicable_limitations: list[str] = []
    if not isinstance(checks, list) or not checks:
        errors.append("coverage.surface_checks must be a non-empty list")
        checks = []
    for index, check in enumerate(checks, start=1):
        label = f"surface_checks[{index}]"
        if not isinstance(check, dict):
            errors.append(f"{label} must be an object")
            continue
        required = (
            "id", "module_id", "facet", "method", "status", "evidence_ids", "finding_ids",
            "result", "unknowns", "limitations", "limitation_refs", "available_work_completed",
        )
        require_fields(check, required, label, errors)
        cid = check.get("id")
        if not isinstance(cid, str) or not CHECK_ID.fullmatch(cid):
            errors.append(f"{label}.id is invalid: {cid!r}")
            continue
        if cid in check_map:
            errors.append(f"duplicate surface check ID: {cid}")
        check_map[cid] = check
        module_id = check.get("module_id")
        module_check_ids[module_id].append(cid)
        if module_id not in MODULE_IDS:
            errors.append(f"{cid}.module_id is invalid: {module_id!r}")
        if not nonempty_string(check.get("facet")):
            errors.append(f"{cid}.facet must be non-empty text")
        if check.get("method") not in CONTROLLED["check_method"]:
            errors.append(f"{cid}.method has invalid value: {check.get('method')!r}")
        if check.get("status") not in CONTROLLED["check_status"]:
            errors.append(f"{cid}.status has invalid value: {check.get('status')!r}")
        if check.get("available_work_completed") is not True:
            errors.append(f"{cid}.available_work_completed must be true before delivery")
        for field, mapping in (("evidence_ids", evidence_map), ("finding_ids", finding_map)):
            values = check.get(field)
            if not isinstance(values, list) or not all(nonempty_string(v) for v in values):
                errors.append(f"{cid}.{field} must be a list of strings")
                values = []
            for value in values:
                if value not in mapping:
                    errors.append(f"{cid} references unknown {field[:-4]}: {value}")
        if not nonempty_string(check.get("result")):
            errors.append(f"{cid}.result must be non-empty text")
        unknowns = check.get("unknowns")
        if not isinstance(unknowns, list) or not all(nonempty_string(v) for v in unknowns or []):
            errors.append(f"{cid}.unknowns must be a list of strings")
            unknowns = []
        limitations = check.get("limitations")
        if not isinstance(limitations, list) or not all(nonempty_string(v) for v in limitations or []):
            errors.append(f"{cid}.limitations must be a list of strings")
            limitations = []
        refs = check.get("limitation_refs")
        if not isinstance(refs, list) or not all(nonempty_string(v) for v in refs or []):
            errors.append(f"{cid}.limitation_refs must be a list of strings")
            refs = []
        for ref in refs:
            if ref.startswith("access:"):
                category = ref.split(":", 1)[1]
                if category not in access_map:
                    errors.append(f"{cid} references unknown access limitation: {ref}")
            elif ref not in limitation_map:
                errors.append(f"{cid} references unknown material limitation: {ref}")
        if check.get("status") in {"partial", "blocked"} and not unknowns:
            errors.append(f"{cid} {check.get('status')} check requires facet-specific unknowns")
        if check.get("status") in {"partial", "blocked"} and not (limitations or refs):
            errors.append(f"{cid} {check.get('status')} check requires a limitation or canonical limitation reference")
        if check.get("status") != "not_applicable":
            applicable_results.append(normalized_prose(check.get("result", "")))
            applicable_limitations.extend(normalized_prose(v) for v in limitations)

    prohibited_surface_fragments = (
        "the cited unavailable evidence prevents a definitive conclusion while all remaining available work is complete",
        "insufficient evidence to determine this facet",
        "additional data is needed",
        "more data is needed",
    )
    for value in applicable_results + applicable_limitations:
        if any(fragment in value for fragment in prohibited_surface_fragments):
            errors.append("surface checks contain project-generic coverage boilerplate")
            break
    for label, values in (("results", applicable_results), ("limitations", applicable_limitations)):
        counts = Counter(v for v in values if v)
        if any(count > max(2, len(values) // 5) for count in counts.values()):
            errors.append(f"surface checks contain excessive repeated boilerplate in {label}")

    for module_id in MODULE_IDS:
        module = module_map.get(module_id)
        if not isinstance(module, dict):
            continue
        check_ids = module.get("check_ids")
        if not isinstance(check_ids, list) or not check_ids or not all(nonempty_string(v) for v in check_ids):
            errors.append(f"{module_id}.check_ids must be a non-empty list of strings")
            check_ids = []
        for cid in check_ids:
            if cid not in check_map:
                errors.append(f"{module_id} references unknown surface check: {cid}")
            elif check_map[cid].get("module_id") != module_id:
                errors.append(f"{module_id} references check {cid} owned by another module")
        if Counter(check_ids) != Counter(module_check_ids.get(module_id, [])):
            errors.append(f"{module_id}.check_ids must account for every module surface check exactly once")
        module_checks = [check_map[cid] for cid in check_ids if cid in check_map]
        facets = [c.get("facet") for c in module_checks]
        if module.get("applicable") is False:
            if facets != ["module_scope"] or any(c.get("status") != "not_applicable" for c in module_checks):
                errors.append(f"{module_id} non-applicable module needs one module_scope not_applicable check")
        else:
            required_facets = MODULE_FACETS[module_id]
            missing = sorted(required_facets - set(facets))
            extra = sorted(set(facets) - required_facets)
            duplicates = sorted(f for f, count in Counter(facets).items() if count > 1)
            if missing:
                errors.append(f"{module_id} surface checks missing facets: {', '.join(missing)}")
            if extra:
                errors.append(f"{module_id} surface checks contain unknown facets: {', '.join(extra)}")
            if duplicates:
                errors.append(f"{module_id} surface check facets repeated: {', '.join(duplicates)}")
        statuses = {c.get("status") for c in module_checks}
        if module.get("status") == "passed" and statuses - {"passed", "not_applicable"}:
            errors.append(f"{module_id} passed status disagrees with failing/partial/blocked checks")
        if module.get("status") == "failed" and "failed" not in statuses:
            errors.append(f"{module_id} failed status requires at least one failed surface check")
        if module.get("status") == "partial" and not statuses.intersection({"partial", "blocked"}):
            errors.append(f"{module_id} partial status requires a partial or blocked surface check")

    def validate_ledger(name: str, id_pattern: re.Pattern[str], required: tuple[str, ...]) -> list[dict[str, Any]]:
        items = coverage_data.get(name)
        if not isinstance(items, list):
            errors.append(f"coverage.{name} must be a list")
            return []
        seen: set[str] = set()
        valid: list[dict[str, Any]] = []
        for index, item in enumerate(items, start=1):
            label = f"{name}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            require_fields(item, required, label, errors)
            ident = item.get("id")
            if not isinstance(ident, str) or not id_pattern.fullmatch(ident):
                errors.append(f"{label}.id is invalid: {ident!r}")
                continue
            if ident in seen:
                errors.append(f"duplicate {name} ID: {ident}")
            seen.add(ident)
            valid.append(item)
        return valid

    serp_samples = validate_ledger(
        "serp_samples", SERP_ID,
        ("id", "query", "engine_or_surface", "location", "device", "observed_at", "result_features", "winner_observation", "target_observation", "evidence_ids", "limitations"),
    )
    for item in serp_samples:
        sid = item["id"]
        for field in ("query", "engine_or_surface", "location", "device"):
            if not nonempty_string(item.get(field)):
                errors.append(f"{sid}.{field} must be non-empty text")
        parse_iso(item.get("observed_at"), f"{sid}.observed_at", errors)
        for field in ("result_features", "evidence_ids", "limitations"):
            if not isinstance(item.get(field), list) or not all(nonempty_string(v) for v in item.get(field, [])):
                errors.append(f"{sid}.{field} must be a list of strings")
        if item.get("target_observation") not in CONTROLLED["target_observation"]:
            errors.append(f"{sid}.target_observation has invalid value: {item.get('target_observation')!r}")
        for evid in item.get("evidence_ids", []):
            if evid not in evidence_map:
                errors.append(f"{sid} references unknown evidence ID: {evid}")
        winner = item.get("winner_observation")
        if not isinstance(winner, dict):
            errors.append(f"{sid}.winner_observation must be an object")
            continue
        require_fields(winner, ("status", "results", "reason", "evidence_ids"), f"{sid}.winner_observation", errors)
        winner_status = winner.get("status")
        if winner_status not in CONTROLLED["winner_observation_status"]:
            errors.append(f"{sid}.winner_observation.status has invalid value: {winner_status!r}")
        results = winner.get("results")
        if not isinstance(results, list):
            errors.append(f"{sid}.winner_observation.results must be a list")
            results = []
        winner_evidence = winner.get("evidence_ids")
        if not isinstance(winner_evidence, list) or not all(nonempty_string(v) for v in winner_evidence or []):
            errors.append(f"{sid}.winner_observation.evidence_ids must be a list of strings")
            winner_evidence = []
        for evid in winner_evidence:
            if evid not in evidence_map:
                errors.append(f"{sid}.winner_observation references unknown evidence ID: {evid}")
            if evid not in item.get("evidence_ids", []):
                errors.append(f"{sid}.winner_observation evidence must also appear in sample evidence_ids: {evid}")
        if winner_status == "observed":
            if not results:
                errors.append(f"{sid} observed winner state requires at least one concrete result")
            if not winner_evidence:
                errors.append(f"{sid} observed winner state requires evidence")
        elif winner_status in {"unavailable", "not_applicable"}:
            if results:
                errors.append(f"{sid} {winner_status} winner state must not contain results")
            if not nonempty_string(winner.get("reason")):
                errors.append(f"{sid} {winner_status} winner state requires a reason")
            if not winner_evidence:
                errors.append(f"{sid} {winner_status} winner state requires evidence")
        for rindex, result in enumerate(results, start=1):
            rlabel = f"{sid}.winner_observation.results[{rindex}]"
            if not isinstance(result, dict):
                errors.append(f"{rlabel} must be an object")
                continue
            require_fields(result, ("kind", "value", "position"), rlabel, errors)
            kind = result.get("kind")
            value = result.get("value")
            if kind not in CONTROLLED["winner_kind"]:
                errors.append(f"{rlabel}.kind has invalid value: {kind!r}")
            if not nonempty_string(value) or not nonempty_string(result.get("position")):
                errors.append(f"{rlabel} value and position must be non-empty text")
                continue
            if kind == "domain" and not HOSTNAME.fullmatch(value.strip().lower()):
                errors.append(f"{rlabel}.value must be a concrete hostname")
            elif kind == "url":
                parsed = urlparse(value.strip())
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    errors.append(f"{rlabel}.value must be a concrete HTTP(S) URL")
            elif kind == "named_entity" and generic_winner(value):
                errors.append(f"{rlabel}.value is a generic winner category, not a concrete named entity")

    url_samples = validate_ledger(
        "url_samples", URL_SAMPLE_ID,
        ("id", "url", "role", "method_evidence", "source_revision_alignment", "http_observation", "eligibility_observation", "index_observation", "canonical_observation", "render_observation", "finding_ids", "evidence_ids", "limitations"),
    )
    for item in url_samples:
        uid = item["id"]
        for field in ("url", "role"):
            if not nonempty_string(item.get(field)):
                errors.append(f"{uid}.{field} must be non-empty text")
        method_items = item.get("method_evidence")
        method_map: dict[str, dict[str, Any]] = {}
        if not isinstance(method_items, list) or not method_items:
            errors.append(f"{uid}.method_evidence must be a non-empty list")
            method_items = []
        for mindex, method_item in enumerate(method_items, start=1):
            mlabel = f"{uid}.method_evidence[{mindex}]"
            if not isinstance(method_item, dict):
                errors.append(f"{mlabel} must be an object")
                continue
            require_fields(method_item, ("method", "status", "observation", "evidence_ids", "limitations"), mlabel, errors)
            method = method_item.get("method")
            status = method_item.get("status")
            if method not in CONTROLLED["check_method"]:
                errors.append(f"{mlabel}.method has invalid value: {method!r}")
                continue
            if method in method_map:
                errors.append(f"{uid} repeats method evidence for {method}")
            method_map[method] = method_item
            if status not in CONTROLLED["method_status"]:
                errors.append(f"{mlabel}.status has invalid value: {status!r}")
            if not nonempty_string(method_item.get("observation")):
                errors.append(f"{mlabel}.observation must be non-empty text")
            for field in ("evidence_ids", "limitations"):
                values = method_item.get(field)
                if not isinstance(values, list) or not all(nonempty_string(v) for v in values or []):
                    errors.append(f"{mlabel}.{field} must be a list of strings")
            if status == "completed" and not method_item.get("evidence_ids"):
                errors.append(f"{mlabel} completed method requires evidence IDs")
            if status in {"failed", "blocked"} and not method_item.get("limitations"):
                errors.append(f"{mlabel} {status} method requires limitations")
            for evid in method_item.get("evidence_ids", []):
                if evid not in evidence_map:
                    errors.append(f"{mlabel} references unknown evidence ID: {evid}")
        top_evidence = item.get("evidence_ids")
        if not isinstance(top_evidence, list) or not all(nonempty_string(v) for v in top_evidence or []):
            errors.append(f"{uid}.evidence_ids must be a list of strings")
            top_evidence = []
        for evid in top_evidence:
            if evid not in evidence_map:
                errors.append(f"{uid} references unknown evidence ID: {evid}")
        for field in ("finding_ids", "limitations"):
            values = item.get(field)
            if not isinstance(values, list) or not all(nonempty_string(v) for v in values or []):
                errors.append(f"{uid}.{field} must be a list of strings")
        for fid in item.get("finding_ids", []):
            if fid not in finding_map:
                errors.append(f"{uid} references unknown finding ID: {fid}")
        if item.get("source_revision_alignment") not in CONTROLLED["source_revision_alignment"]:
            errors.append(f"{uid}.source_revision_alignment has invalid value: {item.get('source_revision_alignment')!r}")

        observation_specs = {
            "http_observation": None,
            "eligibility_observation": CONTROLLED["index_eligibility"],
            "index_observation": CONTROLLED["observed_index_state"],
            "canonical_observation": None,
            "render_observation": None,
        }
        all_observation_evidence: set[str] = set()
        for oname, allowed_values in observation_specs.items():
            obs = item.get(oname)
            if not isinstance(obs, dict):
                errors.append(f"{uid}.{oname} must be an object")
                continue
            require_fields(obs, ("status", "value", "supported_by_methods", "evidence_ids", "limitations"), f"{uid}.{oname}", errors)
            ostatus = obs.get("status")
            if ostatus not in CONTROLLED["url_observation_status"]:
                errors.append(f"{uid}.{oname}.status has invalid value: {ostatus!r}")
            methods = obs.get("supported_by_methods")
            if not isinstance(methods, list) or not all(nonempty_string(v) for v in methods or []):
                errors.append(f"{uid}.{oname}.supported_by_methods must be a list of strings")
                methods = []
            oevidence = obs.get("evidence_ids")
            if not isinstance(oevidence, list) or not all(nonempty_string(v) for v in oevidence or []):
                errors.append(f"{uid}.{oname}.evidence_ids must be a list of strings")
                oevidence = []
            olimits = obs.get("limitations")
            if not isinstance(olimits, list) or not all(nonempty_string(v) for v in olimits or []):
                errors.append(f"{uid}.{oname}.limitations must be a list of strings")
                olimits = []
            for method in methods:
                if method not in method_map:
                    errors.append(f"{uid}.{oname} references undeclared method: {method}")
            for evid in oevidence:
                all_observation_evidence.add(evid)
                if evid not in evidence_map:
                    errors.append(f"{uid}.{oname} references unknown evidence ID: {evid}")
            value = obs.get("value")
            if ostatus == "observed":
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"{uid}.{oname} observed state requires a value")
                if not methods or not oevidence:
                    errors.append(f"{uid}.{oname} observed state requires completed methods and evidence")
                for method in methods:
                    if method_map.get(method, {}).get("status") != "completed":
                        errors.append(f"{uid}.{oname} cannot be supported by non-completed method {method}")
                if allowed_values is not None and value not in allowed_values:
                    errors.append(f"{uid}.{oname}.value has invalid controlled value: {value!r}")
                if oname == "http_observation":
                    if not isinstance(value, int) or isinstance(value, bool) or not 100 <= value <= 599:
                        errors.append(f"{uid}.http_observation.value must be an HTTP integer")
                    if not set(methods).intersection({"live_fetch", "controlled_test"}):
                        errors.append(f"{uid}.http_observation requires completed live_fetch or controlled_test evidence")
                if oname == "render_observation" and "rendered_browser" not in methods:
                    errors.append(f"{uid}.render_observation requires completed rendered_browser evidence")
                if oname == "index_observation" and value in {"indexed", "not_seen_in_sample", "mixed"} and not set(methods).intersection({"serp_observation", "platform_data"}):
                    errors.append(f"{uid}.index_observation requires completed SERP or platform evidence")
            elif ostatus in {"unavailable", "not_applicable"}:
                if value is not None:
                    errors.append(f"{uid}.{oname} {ostatus} state must use null value")
                if not olimits:
                    errors.append(f"{uid}.{oname} {ostatus} state requires a limitation/reason")
                if ostatus == "not_applicable" and methods:
                    errors.append(f"{uid}.{oname} not_applicable state must not claim supporting methods")
                if ostatus == "unavailable" and not oevidence:
                    errors.append(f"{uid}.{oname} unavailable state requires evidence")
        method_evidence_ids = {e for m in method_items if isinstance(m, dict) for e in m.get("evidence_ids", [])}
        expected_evidence = method_evidence_ids | all_observation_evidence
        if set(top_evidence) != expected_evidence:
            errors.append(f"{uid}.evidence_ids must exactly reconcile method and observation evidence")

    live_module = module_map.get("live_search", {})
    if live_module.get("applicable") is True and not serp_samples:
        errors.append("applicable live_search module requires at least one SERP sample")
    production_access = next((a for a in coverage_data.get("access", []) if isinstance(a, dict) and a.get("category") == "production_website"), {})
    if production_access.get("status") in {"available", "partial"} and not url_samples:
        errors.append("available production website requires at least one URL sample")

    non_pursuits = coverage_data.get("deliberate_non_pursuits")
    if not isinstance(non_pursuits, list) or not non_pursuits:
        errors.append("coverage.deliberate_non_pursuits must be a non-empty list")
    else:
        for index, item in enumerate(non_pursuits, start=1):
            label = f"deliberate_non_pursuits[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            require_fields(item, ("topic", "rationale", "evidence_ids"), label, errors)
            if not nonempty_string(item.get("topic")) or not nonempty_string(item.get("rationale")):
                errors.append(f"{label} topic and rationale must be non-empty text")
            if not isinstance(item.get("evidence_ids"), list) or not all(nonempty_string(v) for v in item.get("evidence_ids", [])):
                errors.append(f"{label}.evidence_ids must be a list of strings")
            for evid in item.get("evidence_ids", []):
                if evid not in evidence_map:
                    errors.append(f"{label} references unknown evidence ID: {evid}")

def validate_status_files(root: Path, expected_status: str | None, errors: list[str]) -> None:
    executive = (root / "00-executive-verdict.md").read_text(encoding="utf-8")
    match = REVIEW_STATUS_LINE.search(executive)
    if not match:
        errors.append("00-executive-verdict.md is missing an exact Review status line")
    elif expected_status and match.group(1) != expected_status:
        errors.append("executive verdict review status disagrees with canonical JSON")

    readme = (root / "README.md").read_text(encoding="utf-8")
    for token in ("findings.json", "coverage.json", "validate_seo_teardown.py", "read-only"):
        if token.lower() not in readme.lower():
            errors.append(f"README.md must mention {token}")


def validate_owner_file(root: Path, finding_map: dict[str, dict[str, Any]], errors: list[str]) -> None:
    text = (root / "08-owner-decisions-and-blockers.md").read_text(encoding="utf-8")
    tokens = set(ID_TOKEN.findall(text))
    required = {
        fid
        for fid, finding in finding_map.items()
        if finding.get("status") in {"blocked", "decision_required"}
    }
    missing = sorted(required - tokens)
    if missing:
        errors.append(f"08-owner-decisions-and-blockers.md missing blocked/decision findings: {', '.join(missing)}")
    if not required and "None" not in text:
        errors.append("08-owner-decisions-and-blockers.md must state None when no blockers or decisions exist")


def validate_generated(root: Path, errors: list[str]) -> None:
    try:
        expected = rendered_files(root)
    except Exception as exc:  # deterministic renderer errors should be surfaced cleanly
        errors.append(f"cannot render canonical Markdown: {exc}")
        return
    for name, content in expected.items():
        path = root / name
        if path.read_text(encoding="utf-8") != content:
            errors.append(f"{name} disagrees with canonical JSON; rerun render_handoff.py")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"teardown directory does not exist: {root}"]
    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            errors.append(f"missing required file: {name}")
    if not (root / "evidence").is_dir():
        errors.append("missing required directory: evidence")
    if errors:
        return errors

    findings_data = load_object(root / "findings.json", errors)
    coverage_data = load_object(root / "coverage.json", errors)
    if errors:
        return errors

    audit_end, research_window, audit_status = validate_audit(findings_data, errors)
    evidence_map = validate_evidence(findings_data, audit_end, research_window, errors)
    finding_map = validate_findings(findings_data, evidence_map, errors)
    validate_graph_and_phases(findings_data, finding_map, errors)
    validate_coverage(coverage_data, finding_map, evidence_map, audit_status, errors)
    validate_v3_details(findings_data, coverage_data, finding_map, evidence_map, errors)
    validate_status_files(root, audit_status, errors)
    validate_owner_file(root, finding_map, errors)
    validate_generated(root, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown", type=Path, help="Path to the seo-teardown directory")
    args = parser.parse_args()
    root = args.teardown.resolve()
    errors = validate(root)
    if errors:
        print(f"SEO teardown validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SEO teardown validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
