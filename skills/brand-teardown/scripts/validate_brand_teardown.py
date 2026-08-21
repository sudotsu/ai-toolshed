#!/usr/bin/env python3
"""Validate a deterministic, evidence-led brand teardown handoff."""

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
    "01-brand-and-business-model.md",
    "02-positioning-and-differentiation.md",
    "03-brand-architecture.md",
    "04-message-offer-and-customer-journey.md",
    "05-trust-proof-and-claims.md",
    "06-voice-and-verbal-identity.md",
    "07-visual-and-channel-system.md",
    "08-competitive-brand-landscape.md",
    "09-findings-register.md",
    "10-owner-decisions.md",
    "11-implementation-sequence.md",
    "12-review-coverage-and-limitations.md",
    "13-brand-claim-inventory.md",
    "findings.json",
    "coverage.json",
)

NARRATIVE_FILES = (
    "00-executive-verdict.md",
    "01-brand-and-business-model.md",
    "02-positioning-and-differentiation.md",
    "03-brand-architecture.md",
    "04-message-offer-and-customer-journey.md",
    "05-trust-proof-and-claims.md",
    "06-voice-and-verbal-identity.md",
    "07-visual-and-channel-system.md",
    "08-competitive-brand-landscape.md",
)

NARRATIVE_SECTIONS = {
    "00-executive-verdict.md": (
        "Brand thesis and audiences", "Verdict and strongest qualities",
        "Primary gaps, risks, and owner decisions", "Established-standard comparison",
        "Scope, assumptions, and completion requirements",
    ),
    "01-brand-and-business-model.md": (
        "Business, offer, and project type", "Audiences, roles, triggers, and proof needs",
        "Journey, alternatives, and inaction", "Stakeholder intent versus actual expression",
    ),
    "02-positioning-and-differentiation.md": (
        "Category, customer, problem, and outcome", "Supportable reasons to choose",
        "Crowded positions and open territory", "Experience alignment and limitations",
    ),
    "03-brand-architecture.md": (
        "Brand and identity inventory", "Ownership, endorsement, and hierarchy",
        "Naming, domain, and channel collisions", "Owner decisions and dependencies",
    ),
    "04-message-offer-and-customer-journey.md": (
        "Five-second, thirty-second, and deep comprehension", "Promise, support, proof, and objections",
        "Offer inventory, process, and next steps", "Mobile behavior and journey limitations",
    ),
    "05-trust-proof-and-claims.md": (
        "Proof system", "Claim inventory and contradictions",
        "Credentials, authority, safety, and provenance", "Verification boundaries and downstream review",
    ),
    "06-voice-and-verbal-identity.md": (
        "Recognizable voice and audience fit", "Confidence, humility, urgency, and generic language",
        "Cross-channel behavior", "Verbal strengths and preservation constraints",
    ),
    "07-visual-and-channel-system.md": (
        "Identity, hierarchy, and recognition", "Imagery, iconography, motion, and provenance",
        "Desktop, mobile, and format behavior", "Channel expression and unavailable surfaces",
    ),
    "08-competitive-brand-landscape.md": (
        "Selection and evidence boundary", "Category, trust, offer, and visual conventions",
        "Competitor strengths", "Crowded positions, open territory, and strategic consequence",
    ),
}

ACCESS_CATEGORIES = ControlledValues({
    "source_repository", "production_website", "stakeholder_context",
    "customer_research", "analytics_conversion_data", "social_channels",
    "review_profiles", "sales_operational_collateral", "visual_assets",
    "competitor_public_evidence",
})

MODULE_IDS = ControlledValues({
    "business_audience", "positioning_differentiation", "brand_architecture",
    "message_comprehension", "offer_customer_journey", "trust_proof_claims",
    "voice_verbal_identity", "visual_identity_recognition", "channel_expression",
    "competitive_landscape", "brand_risk_claim_discipline", "strategic_preservation",
})

MODULE_FACETS = {
    "business_audience": {"business_offer", "audience_roles", "triggers_outcomes", "risks_objections", "proof_needs"},
    "positioning_differentiation": {"category_clarity", "target_customer_clarity", "problem_outcome_clarity", "choice_reason", "supportable_differentiators", "experience_alignment"},
    "brand_architecture": {"brand_inventory", "ownership_relationships", "naming_domains_socials", "endorsement_and_hierarchy", "collision_or_dilution"},
    "message_comprehension": {"five_second_comprehension", "thirty_second_comprehension", "deep_comprehension", "promise_support_proof_cta", "metadata_heading_visual_alignment", "mobile_comprehension"},
    "offer_customer_journey": {"offer_inventory", "deliverable_scope_process", "cta_next_step", "readiness_and_entry_points", "price_guarantee_availability", "offer_dilution"},
    "trust_proof_claims": {"reviews_testimonials", "case_work_outcomes", "credentials_licensing_certifications", "team_owner_local_presence", "process_safety_transparency", "technical_or_repository_proof", "proof_placement_and_recency"},
    "voice_verbal_identity": {"recognizable_voice", "audience_and_situation_fit", "cross_channel_consistency", "confidence_humility", "generic_or_ai_phrasing", "manipulation_and_urgency", "authentic_voice_preservation"},
    "visual_identity_recognition": {"logo_wordmark", "color_typography", "layout_hierarchy_legibility", "imagery_iconography_video", "mobile_and_format_behavior", "category_distinctiveness", "offer_tone_alignment", "asset_provenance"},
    "channel_expression": {"website_and_landing_pages", "social_and_video", "email_sales_documents", "profiles_listings_repositories", "physical_collateral", "channel_specific_adaptation", "identity_contact_consistency"},
    "competitive_landscape": {"competitor_selection", "category_language", "visual_conventions", "trust_conventions", "offer_conventions", "competitor_strengths", "crowded_and_open_positions", "strategic_consequence"},
    "brand_risk_claim_discipline": {"credential_and_authority_risk", "superlatives_and_overpromise", "urgency_guarantee_pricing", "availability_service_area_staffing", "identity_contact_conflicts", "derivative_language_or_assets", "product_experience_contradictions", "legal_review_boundary"},
    "strategic_preservation": {"authentic_voice", "recognizable_assets", "specificity_and_usefulness", "verified_proof", "low_pressure_paths", "honest_limitations", "channel_variation"},
}

POLICY_ONLY_RESULT = re.compile(
    r"\b(?:is|are|was|were)\s+(?:treated|handled|assessed|evaluated|described|recorded)\s+as\b"
    r"|\b(?:requires?|needs?|must\s+have)\s+(?:current\s+)?(?:evidence|provenance|review)\b",
    re.IGNORECASE,
)

EVIDENCE_CLASSES = ControlledValues({
    "first_party_artifact", "controlled_observation", "live_observation",
    "stakeholder_statement", "customer_or_audience_evidence", "competitor_evidence",
    "independent_source", "strong_inference",
})
EVIDENCE_SCOPES = ControlledValues({
    "artifact_state", "stakeholder_intent", "audience_perception", "business_outcome",
    "competitor_state", "independent_verification",
})
PROJECT_TYPES = ControlledValues({
    "local_service", "software_developer_product", "saas",
    "agency_professional_service", "ecommerce", "creator_media", "nonprofit",
    "multi_brand", "other",
})
KINDS = ControlledValues({"gap", "risk", "opportunity", "investigation", "strength", "cross_domain"})
FINDING_STATUSES = ControlledValues({"open", "blocked", "decision_required", "retained_strength", "not_applicable", "resolved"})
SEVERITIES = ControlledValues({"critical", "high", "medium", "low", "informational"})
CONFIDENCES = ControlledValues({"confirmed", "high", "medium", "low"})
CLAIM_STATES = ControlledValues({"verified", "plausible_unverified", "unsupported", "contradicted", "not_applicable"})
JUDGMENT_BASES = ControlledValues({
    "observed_behavior", "audience_evidence", "category_evidence",
    "accessibility_or_legibility", "claim_or_provenance_evidence",
    "aesthetic_preference", "not_applicable",
})
OUTCOME_STATUSES = ControlledValues({"measured", "partial", "blocked", "not_applicable"})
DISCIPLINES = ControlledValues({"brand", "product", "seo", "accessibility", "legal", "conversion", "engineering", "operations", "mixed"})
IMPACTS = ControlledValues({"very_high", "high", "medium", "low", "unknown"})
EFFORTS = ControlledValues({"trivial", "small", "medium", "large", "initiative", "unknown"})
REVERSIBILITY = ControlledValues({"easy", "moderate", "hard", "unknown"})
DISPOSITIONS = ControlledValues({"implement", "investigate", "decide", "preserve", "accept_risk", "defer", "leave_alone"})
PHASE_TYPES = ControlledValues({"foundation_decision", "trust_claim_correction", "message_offer", "visual_system", "channel_rollout", "measurement_research", "externally_blocked", "preservation"})
CLAIM_TYPES = ControlledValues({
    "identity", "category", "audience", "offer", "credential", "licensing",
    "certification", "safety", "tenure", "pricing", "availability", "service_area",
    "guarantee", "outcome", "review", "technical_capability", "open_source",
    "privacy", "authority", "other",
})
CLAIM_INVENTORY_STATES = ControlledValues({"verified", "plausible_unverified", "unsupported", "contradicted", "outdated", "not_applicable"})
CLAIM_RISKS = ControlledValues({"high", "medium", "low", "informational"})
ACCESS_STATUSES = ControlledValues({"available", "partial", "blocked", "not_applicable"})
MODULE_STATUSES = ControlledValues({"passed", "failed", "partial", "blocked", "not_tested", "not_applicable"})
MATERIALITIES = ControlledValues({"defining", "high", "medium", "low"})
CHECK_METHODS = ControlledValues({
    "source_inspection", "live_site_review", "rendered_browser",
    "controlled_comprehension", "stakeholder_evidence", "customer_research",
    "analytics_analysis", "social_profile_review", "collateral_review",
    "competitor_research", "independent_verification",
})
METHOD_EVIDENCE_CLASSES = {
    "source_inspection": {"first_party_artifact"},
    "live_site_review": {"live_observation", "controlled_observation"},
    "rendered_browser": {"live_observation", "controlled_observation"},
    "controlled_comprehension": {"controlled_observation", "customer_or_audience_evidence"},
    "stakeholder_evidence": {"stakeholder_statement"},
    "customer_research": {"customer_or_audience_evidence"},
    "social_profile_review": {"first_party_artifact", "live_observation", "controlled_observation"},
    "collateral_review": {"first_party_artifact", "live_observation", "controlled_observation"},
    "competitor_research": {"competitor_evidence"},
    "independent_verification": {"independent_source"},
}
FACET_ACCESS_REQUIREMENTS = {
    ("channel_expression", "website_and_landing_pages"): {"production_website"},
    ("channel_expression", "social_and_video"): {"social_channels"},
    ("channel_expression", "email_sales_documents"): {"sales_operational_collateral"},
    ("channel_expression", "physical_collateral"): {"sales_operational_collateral"},
    ("channel_expression", "profiles_listings_repositories"): {"source_repository", "review_profiles", "social_channels"},
    ("trust_proof_claims", "reviews_testimonials"): {"review_profiles"},
    ("visual_identity_recognition", "asset_provenance"): {"visual_assets"},
}
CHECK_STATUSES = ControlledValues({"passed", "failed", "partial", "blocked", "not_applicable"})
SAMPLE_STATUSES = ControlledValues({"observed", "unavailable", "not_applicable"})
COMPETITOR_RELATIONSHIPS = ControlledValues({"direct_competitor", "substitute", "inaction", "category_benchmark"})

FINDING_KEYS = ControlledValues({
    "id", "title", "kind", "module", "status", "severity", "confidence",
    "evidence_quality", "claim_state", "judgment_basis", "outcome_evidence_status",
    "affected_brands", "affected_audiences", "affected_surfaces", "affected_channels",
    "evidence_ids", "evidence_links", "observed_condition", "desired_condition",
    "brand_consequence", "business_consequence", "trust_consequence",
    "differentiation_consequence", "recognition_consequence", "proof_or_claim_gap",
    "dependencies", "conflicts", "blocker", "owner_decision", "recommendation",
    "acceptance_criteria", "verification_methods", "preservation_constraints",
    "implementation_notes", "responsible_discipline", "priority", "implementation",
})
PRIORITY_KEYS = ControlledValues({"brand_impact", "business_impact", "effort", "reversibility"})
IMPLEMENTATION_KEYS = ControlledValues({"phase_id", "order", "disposition", "rationale", "validation_gate", "targets", "non_goals", "owner_or_external_actions"})
EVIDENCE_LINK_KEYS = ControlledValues({"evidence_id", "role", "claim"})
CLAIM_KEYS = ControlledValues({"id", "claim", "brand", "surfaces", "audiences", "claim_type", "state", "risk_level", "evidence_ids", "owner", "required_action", "verification_method"})
EVIDENCE_KEYS = ControlledValues({"id", "evidence_class", "evidence_scope", "title", "publisher_or_owner", "locator", "accessed_at", "volatile", "summary", "limitations", "artifact_path", "supersedes"})
PHASE_KEYS = ControlledValues({"id", "title", "phase_type", "rationale", "finding_ids", "validation_gate", "expected_outcome"})
ACCESS_KEYS = ControlledValues({"category", "status", "material_to_comprehensive", "coverage_window", "evidence_ids", "limitations", "next_step"})
MODULE_KEYS = ControlledValues({"id", "applicable", "materiality", "status", "check_ids", "finding_ids", "evidence_ids", "limitations", "next_step"})
CHECK_KEYS = ControlledValues({"id", "module_id", "facet", "method", "method_evidence", "status", "evidence_ids", "finding_ids", "result", "unknowns", "limitations", "limitation_refs", "available_work_completed"})
METHOD_EVIDENCE_KEYS = ControlledValues({"evidence_id", "role", "observation"})
SURFACE_KEYS = ControlledValues({"id", "surface", "locator", "brand", "audience", "channel", "viewport_or_format", "method", "status", "observed_at", "evidence_ids", "finding_ids", "observations", "limitations"})
COMPETITOR_KEYS = ControlledValues({"id", "name", "locator", "relationship", "observed_at", "status", "category_language", "trust_conventions", "offer_conventions", "visual_patterns", "strengths", "strategic_consequence", "evidence_ids", "limitations"})
LIMITATION_KEYS = ControlledValues({"id", "description", "status", "completion_requirement", "affected_module_ids"})
RECONCILIATION_KEYS = ControlledValues({"location", "finding_ids", "non_actionable_explanation"})

FINDING_ID = re.compile(r"^[A-Z][A-Z0-9]*-\d{3}$")
EVIDENCE_ID = re.compile(r"^EVID-\d{3}$")
CLAIM_ID = re.compile(r"^CLAIM-\d{3}$")
CHECK_ID = re.compile(r"^CHECK-\d{3}$")
SURFACE_ID = re.compile(r"^SURFACE-\d{3}$")
COMPETITOR_ID = re.compile(r"^COMP-\d{3}$")
LIMITATION_ID = re.compile(r"^LIMIT-\d{3}$")
REVIEW_STATUS_LINE = re.compile(r"^\*\*Review status:\*\*\s*(complete|provisional)\s*$", re.MULTILINE)
NOT_APPLICABLE = re.compile(r"^Not applicable — .+")


def load_object(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = harden_json(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read valid JSON from {path.name}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name} must contain a JSON object")
        return {}
    return value


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_na(value: Any) -> bool:
    return isinstance(value, str) and bool(NOT_APPLICABLE.match(value.strip()))


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


def string_list(value: Any, label: str, errors: list[str], *, required: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not nonempty(item) for item in value):
        errors.append(f"{label} must be an array of non-empty strings")
        return []
    if required and not value:
        errors.append(f"{label} must not be empty")
    return value


def normalize_identity_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def locator_host(value: Any) -> str:
    if not isinstance(value, str) or "://" not in value:
        return ""
    try:
        return (urlparse(value).hostname or "").lower().removeprefix("www.")
    except ValueError:
        return ""


def competitor_evidence_identifies_sample(root: Path, source: dict[str, Any], sample: dict[str, Any]) -> bool:
    """Return whether canonical evidence identifies the exact named competitor."""
    metadata_fields = (
        "title", "publisher_or_owner", "locator", "summary", "limitations", "artifact_path",
    )
    haystack = "\n".join(str(source.get(field, "")) for field in metadata_fields)
    artifact = source.get("artifact_path")
    if isinstance(artifact, str):
        path = root / artifact
        if path.is_file() and not path.is_symlink():
            try:
                with path.open("rb") as handle:
                    haystack += "\n" + handle.read(2_000_000).decode("utf-8", errors="ignore")
            except OSError:
                pass

    sample_name = normalize_identity_text(sample.get("name"))
    if sample_name and sample_name in normalize_identity_text(haystack):
        return True
    sample_host = locator_host(sample.get("locator"))
    return bool(sample_host and sample_host in haystack.lower())


def competitor_profile_fingerprint(sample: dict[str, Any]) -> tuple[Any, ...]:
    fields = (
        "category_language", "trust_conventions", "offer_conventions",
        "visual_patterns", "strengths",
    )
    arrays = []
    for field in fields:
        values = sample.get(field)
        if not isinstance(values, list):
            arrays.append(())
            continue
        arrays.append(tuple(sorted(normalize_identity_text(value) for value in values if nonempty(value))))
    return tuple(arrays)


def parse_date(value: Any, label: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be a YYYY-MM-DD string")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} has invalid date: {value!r}")
        return None


def validate_audit(data: dict[str, Any], errors: list[str]) -> tuple[date | None, int, str | None]:
    if data.get("schema_version") != "brand-teardown-v1":
        errors.append("findings.json schema_version must be 'brand-teardown-v1'")
    expected_top = {"schema_version", "audit", "evidence_sources", "claims", "implementation_phases", "findings"}
    exact_keys(data, expected_top, "findings.json", errors)
    audit = data.get("audit")
    required = {
        "project_name", "project_locator", "audited_revision", "production_locator",
        "audit_start_date", "audit_end_date", "research_window_days", "review_status",
        "project_type", "brands", "primary_audiences", "production_revision_status",
        "production_revision_evidence_ids", "zero_strengths_justification",
        "established_standard", "remaining_standard_gaps",
    }
    if not exact_keys(audit, required, "audit", errors):
        if not isinstance(audit, dict):
            return None, 0, None
    if not isinstance(audit, dict):
        # Never rely on assert for a safety guard: -O strips it.
        errors.append("audit must be an object")
        return None, 0, None
    for field in ("project_name", "project_locator", "audited_revision", "production_locator", "established_standard"):
        if not nonempty(audit.get(field)):
            errors.append(f"audit.{field} must be non-empty text")
    if nonempty(audit.get("established_standard")) and audit.get("established_standard", "").strip().lower() in {"best practice", "best practices", "industry standard"}:
        errors.append("audit.established_standard must name a concrete comparison basis")
    if audit.get("project_type") not in PROJECT_TYPES:
        errors.append(f"audit.project_type has invalid value: {audit.get('project_type')!r}")
    status = audit.get("review_status")
    if status not in {"complete", "provisional"}:
        errors.append(f"audit.review_status has invalid value: {status!r}")
        status = None
    for field in ("brands", "primary_audiences"):
        string_list(audit.get(field), f"audit.{field}", errors, required=True)
    gaps = string_list(audit.get("remaining_standard_gaps"), "audit.remaining_standard_gaps", errors)
    justification = audit.get("zero_strengths_justification")
    if justification is not None and not nonempty(justification):
        errors.append("audit.zero_strengths_justification must be text or null")
    production_status = audit.get("production_revision_status")
    if production_status not in {"verified", "unverified", "not_applicable"}:
        errors.append(f"audit.production_revision_status has invalid value: {production_status!r}")
    revision_evidence = string_list(audit.get("production_revision_evidence_ids"), "audit.production_revision_evidence_ids", errors)
    if production_status in {"verified", "unverified"} and not revision_evidence:
        errors.append(f"audit.production_revision_status {production_status} requires evidence IDs")
    if status == "complete" and production_status == "unverified":
        errors.append("false complete status: production revision is unverified")
    start = parse_date(audit.get("audit_start_date"), "audit.audit_start_date", errors)
    end = parse_date(audit.get("audit_end_date"), "audit.audit_end_date", errors)
    if start and end and start > end:
        errors.append("audit_start_date must not be after audit_end_date")
    window = audit.get("research_window_days")
    if not isinstance(window, int) or isinstance(window, bool) or not 1 <= window <= 30:
        errors.append("audit.research_window_days must be an integer from 1 to 30")
        window = 0
    if status == "complete" and gaps:
        # Remaining gaps are allowed, but the language must not describe missing required evidence.
        if any("blocked" in gap.lower() or "not tested" in gap.lower() for gap in gaps):
            errors.append("false complete status: remaining standard gaps contain blocked or untested required work")
    return end, window, status


def validate_evidence(root: Path, data: dict[str, Any], audit_end: date | None, window: int, errors: list[str]) -> dict[str, dict[str, Any]]:
    items = data.get("evidence_sources")
    if not isinstance(items, list) or not items:
        errors.append("evidence_sources must be a non-empty array")
        return {}
    result: dict[str, dict[str, Any]] = {}
    graph: dict[str, list[str]] = {}
    for index, item in enumerate(items, start=1):
        label = f"evidence_sources[{index}]"
        exact_keys(item, EVIDENCE_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        evid = item.get("id")
        if not isinstance(evid, str) or not EVIDENCE_ID.fullmatch(evid):
            errors.append(f"{label}.id is invalid: {evid!r}")
            continue
        if evid in result:
            errors.append(f"duplicate evidence ID: {evid}")
        result[evid] = item
        if item.get("evidence_class") not in EVIDENCE_CLASSES:
            errors.append(f"{evid} has invalid evidence_class: {item.get('evidence_class')!r}")
        if item.get("evidence_scope") not in EVIDENCE_SCOPES:
            errors.append(f"{evid} has invalid evidence_scope: {item.get('evidence_scope')!r}")
        for field in ("title", "publisher_or_owner", "locator", "summary", "limitations"):
            if not nonempty(item.get(field)):
                errors.append(f"{evid}.{field} must be non-empty text")
        if not isinstance(item.get("volatile"), bool):
            errors.append(f"{evid}.volatile must be boolean")
        artifact = item.get("artifact_path")
        if artifact is not None and not nonempty(artifact):
            errors.append(f"{evid}.artifact_path must be text or null")
        elif isinstance(artifact, str):
            artifact_rel = Path(artifact)
            if artifact_rel.is_absolute() or ".." in artifact_rel.parts or not artifact_rel.parts or artifact_rel.parts[0] != "evidence":
                errors.append(f"{evid}.artifact_path must be a relative path inside evidence/")
            else:
                artifact_file = root / artifact_rel
                try:
                    artifact_file.resolve().relative_to((root / "evidence").resolve())
                except ValueError:
                    errors.append(f"{evid}.artifact_path resolves outside evidence/")
                if artifact_file.is_symlink() or not artifact_file.is_file():
                    errors.append(f"{evid}.artifact_path does not name a regular in-handoff evidence file")
                elif artifact_file.stat().st_size < 128:
                    errors.append(f"{evid}.artifact_path is too small to substantiate the recorded evidence")
        supersedes = string_list(item.get("supersedes"), f"{evid}.supersedes", errors)
        graph[evid] = supersedes
        accessed = parse_date(item.get("accessed_at"), f"{evid}.accessed_at", errors)
        if accessed and audit_end:
            if accessed > audit_end:
                errors.append(f"{evid}.accessed_at is after audit_end_date")
            if item.get("volatile") is True and window and accessed < audit_end - timedelta(days=window):
                errors.append(f"{evid} volatile evidence is stale for the declared research window")
    for evid, supersedes in graph.items():
        for older in supersedes:
            if older not in result:
                errors.append(f"{evid}.supersedes references unknown evidence: {older}")
            if older == evid:
                errors.append(f"{evid} cannot supersede itself")
    visiting: set[str] = set()
    visited: set[str] = set()
    def walk(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            errors.append(f"evidence supersession cycle detected at {node}")
            return
        visiting.add(node)
        for older in graph.get(node, []):
            if older in graph:
                walk(older)
        visiting.remove(node)
        visited.add(node)
    for evid in graph:
        walk(evid)
    return result


def validate_production_revision_evidence(data: dict[str, Any], evidence: dict[str, dict[str, Any]], errors: list[str]) -> None:
    audit = data.get("audit", {})
    if not isinstance(audit, dict) or audit.get("production_revision_status") != "verified":
        return
    revision = audit.get("audited_revision")
    refs = audit.get("production_revision_evidence_ids")
    if not nonempty(revision) or not isinstance(refs, list):
        return
    revision_token = revision.strip().lower()
    candidates = [evidence[evid] for evid in refs if evid in evidence]
    aligned = False
    for source in candidates:
        text_value = " ".join(
            str(source.get(field, "")) for field in ("title", "locator", "summary")
        ).lower()
        class_ok = source.get("evidence_class") in {"controlled_observation", "live_observation", "independent_source"}
        revision_ok = revision_token in text_value or (len(revision_token) >= 7 and revision_token[:7] in text_value)
        alignment_ok = any(token in text_value for token in ("align", "match", "deployment", "default branch", "published commit"))
        if class_ok and revision_ok and alignment_ok:
            aligned = True
            break
    if not aligned:
        errors.append(
            "verified production revision requires controlled, live, or independent evidence that names the audited revision and alignment method"
        )


def validate_findings(data: dict[str, Any], evidence: dict[str, dict[str, Any]], errors: list[str]) -> dict[str, dict[str, Any]]:
    items = data.get("findings")
    if not isinstance(items, list) or not items:
        errors.append("findings must be a non-empty array")
        return {}
    result: dict[str, dict[str, Any]] = {}
    orders: dict[int, str] = {}
    observed_values: list[str] = []
    for index, item in enumerate(items, start=1):
        label = f"findings[{index}]"
        exact_keys(item, FINDING_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        fid = item.get("id")
        if not isinstance(fid, str) or not FINDING_ID.fullmatch(fid):
            errors.append(f"{label}.id is invalid: {fid!r}")
            continue
        if fid in result:
            errors.append(f"duplicate finding ID: {fid}")
        result[fid] = item
        for field in ("title", "observed_condition", "desired_condition", "brand_consequence", "business_consequence", "trust_consequence", "differentiation_consequence", "recognition_consequence", "proof_or_claim_gap", "recommendation"):
            if not nonempty(item.get(field)):
                errors.append(f"{fid}.{field} must be non-empty text")
        if nonempty(item.get("observed_condition")):
            observed_values.append(re.sub(r"\s+", " ", item["observed_condition"].strip().lower()))
        controls = {
            "kind": KINDS, "module": MODULE_IDS, "status": FINDING_STATUSES,
            "severity": SEVERITIES, "confidence": CONFIDENCES,
            "evidence_quality": EVIDENCE_CLASSES, "claim_state": CLAIM_STATES,
            "judgment_basis": JUDGMENT_BASES, "outcome_evidence_status": OUTCOME_STATUSES,
            "responsible_discipline": DISCIPLINES,
        }
        for field, allowed in controls.items():
            if item.get(field) not in allowed:
                errors.append(f"{fid} has invalid {field}: {item.get(field)!r}")
        for field in ("affected_brands", "affected_audiences", "affected_surfaces", "affected_channels", "evidence_ids", "acceptance_criteria", "verification_methods"):
            string_list(item.get(field), f"{fid}.{field}", errors, required=True)
        for field in ("dependencies", "conflicts", "preservation_constraints", "implementation_notes"):
            string_list(item.get(field), f"{fid}.{field}", errors)
        # string_list above already recorded errors for malformed entries. Filter to
        # strings here so unhashable values cannot crash evidence.get or Counter.
        raw_evidence_ids = item.get("evidence_ids") if isinstance(item.get("evidence_ids"), list) else []
        evidence_ids = [evid for evid in raw_evidence_ids if isinstance(evid, str)]
        referenced_classes: set[str] = set()
        referenced_scopes: set[str] = set()
        for evid in evidence_ids:
            source = evidence.get(evid)
            if source is None:
                errors.append(f"{fid} references unknown evidence ID: {evid}")
            else:
                referenced_classes.add(source.get("evidence_class"))
                referenced_scopes.add(source.get("evidence_scope"))
        comparison_text = " ".join(
            str(item.get(field, ""))
            for field in (
                "observed_condition", "desired_condition", "brand_consequence",
                "business_consequence", "trust_consequence", "differentiation_consequence",
                "recognition_consequence", "proof_or_claim_gap", "recommendation",
            )
        )
        if re.search(r"\b(competitor|competitors|category benchmark|compared with)\b", comparison_text, re.IGNORECASE):
            if "competitor_evidence" not in referenced_classes:
                errors.append(f"{fid} makes a competitor-dependent judgment without competitor evidence")
        if item.get("evidence_quality") in EVIDENCE_CLASSES and item.get("evidence_quality") not in referenced_classes:
            errors.append(f"{fid} evidence_quality is not represented by a referenced source")
        links = item.get("evidence_links")
        linked_ids: list[str] = []
        supports = 0
        contradicts = 0
        if not isinstance(links, list) or not links:
            errors.append(f"{fid}.evidence_links must be a non-empty array")
        else:
            for link_index, link in enumerate(links, start=1):
                link_label = f"{fid}.evidence_links[{link_index}]"
                exact_keys(link, EVIDENCE_LINK_KEYS, link_label, errors)
                if not isinstance(link, dict):
                    continue
                evid = link.get("evidence_id")
                if not isinstance(evid, str) or not EVIDENCE_ID.fullmatch(evid):
                    errors.append(f"{link_label}.evidence_id must be an evidence ID string")
                    continue
                linked_ids.append(evid)
                if link.get("role") not in {"supports", "contradicts", "context"}:
                    errors.append(f"{link_label}.role has invalid value: {link.get('role')!r}")
                if link.get("role") == "supports":
                    supports += 1
                if link.get("role") == "contradicts":
                    contradicts += 1
                if not nonempty(link.get("claim")):
                    errors.append(f"{link_label}.claim must be non-empty text")
            if Counter(linked_ids) != Counter(evidence_ids):
                errors.append(f"{fid}.evidence_links must account for each evidence_id exactly once")
            if supports == 0:
                errors.append(f"{fid}.evidence_links needs at least one supports entry")
        if contradicts and item.get("claim_state") not in {"contradicted", "plausible_unverified"}:
            errors.append(f"{fid} has contradictory evidence but does not calibrate claim_state")
        if item.get("claim_state") == "verified" and referenced_classes == {"strong_inference"}:
            errors.append(f"{fid} verified claim_state cannot rest only on strong inference")
        if item.get("outcome_evidence_status") == "measured" and not referenced_scopes.intersection({"audience_perception", "business_outcome"}):
            errors.append(f"{fid} measured outcome evidence requires audience-perception or business-outcome evidence")
        if item.get("kind") == "strength":
            if item.get("status") != "retained_strength" or item.get("severity") != "informational":
                errors.append(f"{fid} strength must be informational and retained_strength")
        if item.get("status") == "retained_strength" and item.get("kind") != "strength":
            errors.append(f"{fid} retained_strength status requires strength kind")
        if item.get("status") == "blocked" and not nonempty(item.get("blocker")):
            errors.append(f"{fid} blocked status requires blocker text")
        if item.get("status") != "blocked" and item.get("blocker") is not None and not is_na(item.get("blocker")):
            errors.append(f"{fid}.blocker must be null unless status is blocked")
        if item.get("status") == "decision_required" and not nonempty(item.get("owner_decision")):
            errors.append(f"{fid} decision_required status requires owner_decision text")
        if item.get("status") != "decision_required" and item.get("owner_decision") is not None and not is_na(item.get("owner_decision")):
            errors.append(f"{fid}.owner_decision must be null unless status is decision_required")
        if item.get("judgment_basis") == "aesthetic_preference" and item.get("severity") in {"critical", "high", "medium"}:
            errors.append(f"{fid} aesthetic preference cannot support medium, high, or critical severity")
        if item.get("severity") == "critical":
            if item.get("confidence") not in {"confirmed", "high"}:
                errors.append(f"{fid} critical severity requires confirmed or high confidence")
            if item.get("evidence_quality") == "strong_inference":
                errors.append(f"{fid} critical severity cannot rest on strong inference")
            consequence_text = f"{item.get('brand_consequence', '')} {item.get('business_consequence', '')}".lower()
            if not any(token in consequence_text for token in ("catastrophic", "existential", "unusable", "fraud", "immediate")):
                errors.append(f"{fid} critical severity lacks a demonstrated catastrophic or existential consequence")
        priority = item.get("priority")
        exact_keys(priority, PRIORITY_KEYS, f"{fid}.priority", errors)
        if isinstance(priority, dict):
            if priority.get("brand_impact") not in IMPACTS:
                errors.append(f"{fid}.priority.brand_impact has invalid value")
            if priority.get("business_impact") not in IMPACTS:
                errors.append(f"{fid}.priority.business_impact has invalid value")
            if priority.get("effort") not in EFFORTS:
                errors.append(f"{fid}.priority.effort has invalid value")
            if priority.get("reversibility") not in REVERSIBILITY:
                errors.append(f"{fid}.priority.reversibility has invalid value")
        implementation = item.get("implementation")
        exact_keys(implementation, IMPLEMENTATION_KEYS, f"{fid}.implementation", errors)
        if isinstance(implementation, dict):
            if implementation.get("disposition") not in DISPOSITIONS:
                errors.append(f"{fid}.implementation.disposition has invalid value")
            order = implementation.get("order")
            if not isinstance(order, int) or isinstance(order, bool) or order < 1:
                errors.append(f"{fid}.implementation.order must be a positive integer")
            elif order in orders:
                errors.append(f"duplicate implementation order {order}: {orders[order]} and {fid}")
            else:
                orders[order] = fid
            for field in ("phase_id", "rationale", "validation_gate"):
                if not nonempty(implementation.get(field)):
                    errors.append(f"{fid}.implementation.{field} must be non-empty text")
            string_list(implementation.get("targets"), f"{fid}.implementation.targets", errors, required=True)
            string_list(implementation.get("non_goals"), f"{fid}.implementation.non_goals", errors, required=True)
            actions = string_list(implementation.get("owner_or_external_actions"), f"{fid}.implementation.owner_or_external_actions", errors)
            if item.get("status") == "blocked" and not actions:
                errors.append(f"{fid} blocked finding needs an owner_or_external_action")
            if item.get("kind") == "strength" and implementation.get("disposition") != "preserve":
                errors.append(f"{fid} strength must use preserve disposition")
            if item.get("status") == "decision_required" and implementation.get("disposition") != "decide":
                errors.append(f"{fid} decision_required status must use decide disposition")
    if set(orders) != set(range(1, len(result) + 1)):
        errors.append("implementation orders must be contiguous from 1 through finding count")
    if len(observed_values) >= 4:
        repeats = Counter(observed_values)
        if any(count > max(2, len(observed_values) // 2) for count in repeats.values()):
            errors.append("findings contain excessive repeated generic observed conditions")
    generic_fragments = (
        "brand could be clearer", "improve brand consistency", "use better messaging",
        "build more trust", "differentiate from competitors", "improve visual identity",
    )
    for fid, item in result.items():
        observed = item.get("observed_condition", "").strip().lower() if isinstance(item.get("observed_condition"), str) else ""
        if observed in generic_fragments:
            errors.append(f"{fid} contains generic advice without project-specific evidence")
    return result


def validate_claims(data: dict[str, Any], evidence: dict[str, dict[str, Any]], errors: list[str]) -> dict[str, dict[str, Any]]:
    items = data.get("claims")
    if not isinstance(items, list) or not items:
        errors.append("claims must be a non-empty array")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items, start=1):
        label = f"claims[{index}]"
        exact_keys(item, CLAIM_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        cid = item.get("id")
        if not isinstance(cid, str) or not CLAIM_ID.fullmatch(cid):
            errors.append(f"{label}.id is invalid: {cid!r}")
            continue
        if cid in result:
            errors.append(f"duplicate claim ID: {cid}")
        result[cid] = item
        for field in ("claim", "brand", "owner", "required_action", "verification_method"):
            if not nonempty(item.get(field)):
                errors.append(f"{cid}.{field} must be non-empty text")
        string_list(item.get("surfaces"), f"{cid}.surfaces", errors, required=True)
        string_list(item.get("audiences"), f"{cid}.audiences", errors, required=True)
        refs = string_list(item.get("evidence_ids"), f"{cid}.evidence_ids", errors)
        for evid in refs:
            if evid not in evidence:
                errors.append(f"{cid} references unknown evidence ID: {evid}")
        if item.get("claim_type") not in CLAIM_TYPES:
            errors.append(f"{cid}.claim_type has invalid value")
        state = item.get("state")
        if state not in CLAIM_INVENTORY_STATES:
            errors.append(f"{cid}.state has invalid value")
        if item.get("risk_level") not in CLAIM_RISKS:
            errors.append(f"{cid}.risk_level has invalid value")
        if state in {"verified", "contradicted", "outdated"} and not refs:
            errors.append(f"{cid} {state} claim requires evidence")
    return result


def validate_graph_and_phases(data: dict[str, Any], findings: dict[str, dict[str, Any]], errors: list[str]) -> None:
    graph: dict[str, list[str]] = {}
    for fid, finding in findings.items():
        deps = finding.get("dependencies") if isinstance(finding.get("dependencies"), list) else []
        conflicts = finding.get("conflicts") if isinstance(finding.get("conflicts"), list) else []
        graph[fid] = []
        for dep in deps:
            if dep == fid:
                errors.append(f"{fid} cannot depend on itself")
            elif dep not in findings:
                errors.append(f"{fid} depends on unknown finding: {dep}")
            else:
                graph[fid].append(dep)
                implementation = finding.get("implementation")
                dependency_implementation = findings[dep].get("implementation")
                order = implementation.get("order") if isinstance(implementation, dict) else None
                dep_order = dependency_implementation.get("order") if isinstance(dependency_implementation, dict) else None
                if isinstance(order, int) and isinstance(dep_order, int) and dep_order >= order:
                    errors.append(f"{fid} dependency {dep} does not appear earlier in implementation order")
        for conflict in conflicts:
            if conflict == fid:
                errors.append(f"{fid} cannot conflict with itself")
            elif conflict not in findings:
                errors.append(f"{fid} conflicts with unknown finding: {conflict}")
            elif fid not in findings[conflict].get("conflicts", []):
                errors.append(f"conflict must be symmetric: {fid} <-> {conflict}")
    visiting: set[str] = set()
    visited: set[str] = set()
    def walk(node: str, trail: list[str]) -> None:
        if node in visited:
            return
        if node in visiting:
            errors.append(f"dependency cycle detected: {' -> '.join(trail + [node])}")
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            walk(dep, trail + [node])
        visiting.remove(node)
        visited.add(node)
    for fid in graph:
        walk(fid, [])

    phases = data.get("implementation_phases")
    if not isinstance(phases, list) or not phases:
        errors.append("implementation_phases must be a non-empty array")
        return
    phase_ids: set[str] = set()
    membership: list[str] = []
    for index, phase in enumerate(phases, start=1):
        label = f"implementation_phases[{index}]"
        exact_keys(phase, PHASE_KEYS, label, errors)
        if not isinstance(phase, dict):
            continue
        pid = phase.get("id")
        if not nonempty(pid):
            errors.append(f"{label}.id must be non-empty text")
            continue
        if pid in phase_ids:
            errors.append(f"duplicate implementation phase ID: {pid}")
        phase_ids.add(pid)
        if phase.get("phase_type") not in PHASE_TYPES:
            errors.append(f"{pid}.phase_type has invalid value")
        for field in ("title", "rationale", "validation_gate", "expected_outcome"):
            if not nonempty(phase.get(field)):
                errors.append(f"{pid}.{field} must be non-empty text")
        ids = string_list(phase.get("finding_ids"), f"{pid}.finding_ids", errors, required=True)
        membership.extend(ids)
        phase_orders: list[int] = []
        for fid in ids:
            if fid not in findings:
                errors.append(f"{pid} references unknown finding: {fid}")
                continue
            implementation = findings[fid].get("implementation")
            if not isinstance(implementation, dict):
                implementation = {}
            if implementation.get("phase_id") != pid:
                errors.append(f"{fid}.phase_id disagrees with phase {pid}")
            if isinstance(implementation.get("order"), int):
                phase_orders.append(implementation["order"])
        if phase_orders != sorted(phase_orders):
            errors.append(f"{pid}.finding_ids are not in implementation order")
    counts = Counter(membership)
    missing = sorted(set(findings) - set(membership))
    unknown = sorted(set(membership) - set(findings))
    repeated = sorted(fid for fid, count in counts.items() if count != 1)
    if missing:
        errors.append(f"findings missing from implementation phases: {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown findings in implementation phases: {', '.join(unknown)}")
    if repeated:
        errors.append(f"findings repeated in implementation phases: {', '.join(repeated)}")


def audit_mapping(findings_data: dict[str, Any]) -> dict[str, Any]:
    """Return findings_data["audit"] as a mapping.

    A malformed audit value (a list, string, or null) must produce collected
    validation errors rather than an AttributeError from a chained .get.
    """
    audit = findings_data.get("audit")
    return audit if isinstance(audit, dict) else {}


def validate_coverage(root: Path, data: dict[str, Any], findings_data: dict[str, Any], findings: dict[str, dict[str, Any]], evidence: dict[str, dict[str, Any]], audit_status: str | None, errors: list[str]) -> None:
    top = {"schema_version", "review_status", "access", "modules", "surface_checks", "surface_samples", "competitor_samples", "material_limitations", "narrative_reconciliation", "validator"}
    exact_keys(data, top, "coverage.json", errors)
    if data.get("schema_version") != "brand-teardown-coverage-v1":
        errors.append("coverage.json schema_version must be 'brand-teardown-coverage-v1'")
    status = data.get("review_status")
    if status not in {"complete", "provisional"}:
        errors.append(f"coverage.review_status has invalid value: {status!r}")
    if audit_status and status != audit_status:
        errors.append("review status differs between findings.json and coverage.json")
    provisional: list[str] = []

    access_items = data.get("access")
    access_seen: list[str] = []
    access_map: dict[str, dict[str, Any]] = {}
    production_available = False
    if not isinstance(access_items, list):
        errors.append("coverage.access must be an array")
        access_items = []
    for index, item in enumerate(access_items, start=1):
        label = f"access[{index}]"
        exact_keys(item, ACCESS_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        category = item.get("category")
        if not isinstance(category, str):
            # Unhashable values would crash the set test, access_map, and Counter.
            errors.append(f"{label}.category must be a string, got {type(category).__name__}")
            continue
        access_seen.append(category)
        if category not in ACCESS_CATEGORIES:
            errors.append(f"{label}.category has invalid value: {category!r}")
        else:
            access_map[category] = item
        access_status = item.get("status")
        if access_status not in ACCESS_STATUSES:
            errors.append(f"{category}.status has invalid value")
        if category == "production_website" and access_status in {"available", "partial"}:
            production_available = True
        if not isinstance(item.get("material_to_comprehensive"), bool):
            errors.append(f"{category}.material_to_comprehensive must be boolean")
        if not nonempty(item.get("coverage_window")) or not nonempty(item.get("next_step")):
            errors.append(f"{category} coverage_window and next_step must be non-empty text")
        for field in ("evidence_ids", "limitations"):
            refs = string_list(item.get(field), f"{category}.{field}", errors)
            if field == "evidence_ids":
                for evid in refs:
                    if evid not in evidence:
                        errors.append(f"{category} references unknown evidence ID: {evid}")
        if item.get("material_to_comprehensive") is True and access_status in {"partial", "blocked"}:
            provisional.append(f"material access {category} is {access_status}")
    counts = Counter(access_seen)
    if set(access_seen) != ACCESS_CATEGORIES:
        errors.append("coverage access categories must match the required set exactly")
    if any(count > 1 for count in counts.values()):
        errors.append("coverage access categories must not repeat")

    module_items = data.get("modules")
    module_map: dict[str, dict[str, Any]] = {}
    finding_modules: Counter[str] = Counter()
    if not isinstance(module_items, list):
        errors.append("coverage.modules must be an array")
        module_items = []
    for index, item in enumerate(module_items, start=1):
        label = f"modules[{index}]"
        exact_keys(item, MODULE_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        mid = item.get("id")
        if mid not in MODULE_IDS:
            errors.append(f"{label}.id has invalid value: {mid!r}")
            continue
        if mid in module_map:
            errors.append(f"duplicate module ID: {mid}")
        module_map[mid] = item
        if not isinstance(item.get("applicable"), bool):
            errors.append(f"{mid}.applicable must be boolean")
        if item.get("materiality") not in MATERIALITIES:
            errors.append(f"{mid}.materiality has invalid value")
        module_status = item.get("status")
        if module_status not in MODULE_STATUSES:
            errors.append(f"{mid}.status has invalid value")
        for field in ("check_ids", "finding_ids", "evidence_ids", "limitations"):
            values = string_list(item.get(field), f"{mid}.{field}", errors, required=field == "check_ids")
            if field == "finding_ids":
                for fid in values:
                    if fid not in findings:
                        errors.append(f"{mid} references unknown finding: {fid}")
                    else:
                        finding_modules[fid] += 1
            if field == "evidence_ids":
                for evid in values:
                    if evid not in evidence:
                        errors.append(f"{mid} references unknown evidence: {evid}")
        if not nonempty(item.get("next_step")):
            errors.append(f"{mid}.next_step must be non-empty text")
        if item.get("applicable") is False and module_status != "not_applicable":
            errors.append(f"{mid} non-applicable module must use not_applicable status")
        if item.get("applicable") is True and module_status == "not_applicable":
            errors.append(f"{mid} applicable module cannot use not_applicable status")
        if item.get("applicable") is True and item.get("materiality") in {"defining", "high"} and module_status in {"partial", "blocked", "not_tested"}:
            provisional.append(f"{item.get('materiality')} module {mid} is {module_status}")
    if set(module_map) != MODULE_IDS:
        errors.append("coverage modules must match the twelve required module IDs exactly")
    unmapped = sorted(fid for fid in findings if finding_modules[fid] == 0)
    repeated_mappings = sorted(fid for fid, count in finding_modules.items() if count > 1)
    if unmapped:
        errors.append(f"findings not mapped to any module: {', '.join(unmapped)}")
    if repeated_mappings:
        errors.append(f"findings mapped to more than one module: {', '.join(repeated_mappings)}")

    checks = data.get("surface_checks")
    check_map: dict[str, dict[str, Any]] = {}
    module_checks: defaultdict[str, list[str]] = defaultdict(list)
    result_texts: list[str] = []
    normalized_facet_results: list[str] = []
    limitation_texts: list[str] = []
    if not isinstance(checks, list) or not checks:
        errors.append("coverage.surface_checks must be a non-empty array")
        checks = []
    for index, item in enumerate(checks, start=1):
        label = f"surface_checks[{index}]"
        exact_keys(item, CHECK_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        cid = item.get("id")
        if not isinstance(cid, str) or not CHECK_ID.fullmatch(cid):
            errors.append(f"{label}.id is invalid: {cid!r}")
            continue
        if cid in check_map:
            errors.append(f"duplicate surface check ID: {cid}")
        check_map[cid] = item
        mid = item.get("module_id")
        if not isinstance(mid, str):
            # Unhashable values would crash module_checks indexing and the set test.
            errors.append(f"{cid}.module_id must be a string, got {type(mid).__name__}")
        else:
            module_checks[mid].append(cid)
            if mid not in MODULE_IDS:
                errors.append(f"{cid}.module_id has invalid value")
        if not nonempty(item.get("facet")):
            errors.append(f"{cid}.facet must be non-empty text")
        if item.get("method") not in CHECK_METHODS:
            errors.append(f"{cid}.method has invalid value")
        check_status = item.get("status")
        if check_status not in CHECK_STATUSES:
            errors.append(f"{cid}.status has invalid value")
        if item.get("available_work_completed") is not True:
            errors.append(f"{cid}.available_work_completed must be true before delivery")
            provisional.append(f"available work incomplete for {cid}")
        check_evidence: list[dict[str, Any]] = []
        for field, mapping in (("evidence_ids", evidence), ("finding_ids", findings)):
            values = string_list(item.get(field), f"{cid}.{field}", errors)
            for value in values:
                if value not in mapping:
                    errors.append(f"{cid} references unknown {field}: {value}")
                elif field == "evidence_ids":
                    check_evidence.append(mapping[value])
                elif findings[value].get("module") != mid:
                    errors.append(
                        f"{cid} finding {value} does not match its declared module "
                        f"{findings[value].get('module')}"
                    )
        method_links = item.get("method_evidence")
        linked_evidence: list[str] = []
        supporting_evidence: list[dict[str, Any]] = []
        support_count = 0
        if not isinstance(method_links, list):
            errors.append(f"{cid}.method_evidence must be an array")
            method_links = []
        for link_index, link in enumerate(method_links, start=1):
            link_label = f"{cid}.method_evidence[{link_index}]"
            exact_keys(link, METHOD_EVIDENCE_KEYS, link_label, errors)
            if not isinstance(link, dict):
                continue
            evid = link.get("evidence_id")
            if not isinstance(evid, str) or not EVIDENCE_ID.fullmatch(evid):
                errors.append(f"{link_label}.evidence_id must be an evidence ID string")
                continue
            linked_evidence.append(evid)
            role = link.get("role")
            if role not in {"supports_result", "context", "limitation"}:
                errors.append(f"{link_label}.role has invalid value: {role!r}")
            if not nonempty(link.get("observation")):
                errors.append(f"{link_label}.observation must be non-empty text")
            if role == "supports_result" and evid in evidence:
                support_count += 1
                supporting_evidence.append(evidence[evid])
        declared_evidence = item.get("evidence_ids") if isinstance(item.get("evidence_ids"), list) else []
        if Counter(linked_evidence) != Counter(declared_evidence):
            errors.append(f"{cid}.method_evidence must account for each evidence_id exactly once")
        if check_status in {"passed", "failed"} and support_count == 0:
            errors.append(f"{cid} {check_status} check requires method evidence that supports the result")

        method = item.get("method")
        required_classes = METHOD_EVIDENCE_CLASSES.get(method)
        cited_classes = {source.get("evidence_class") for source in supporting_evidence}
        if check_status in {"passed", "failed"} and required_classes and not cited_classes.intersection(required_classes):
            errors.append(
                f"{cid} method {method} requires compatible evidence class: "
                f"{', '.join(sorted(required_classes))}"
            )
        if check_status in {"passed", "failed"} and method == "analytics_analysis" and not any(
            source.get("evidence_scope") == "business_outcome" for source in supporting_evidence
        ):
            errors.append(f"{cid} method analytics_analysis requires business_outcome evidence")
        required_access = FACET_ACCESS_REQUIREMENTS.get((mid, item.get("facet")))
        if required_access:
            access_statuses = {
                access_map[category].get("status")
                for category in required_access if category in access_map
            }
            if access_statuses and access_statuses <= {"not_applicable"} and check_status != "not_applicable":
                errors.append(f"{cid} must be not_applicable because its required access is not applicable")
            elif access_statuses and access_statuses <= {"blocked", "not_applicable"} and check_status not in {"blocked", "not_applicable"}:
                errors.append(f"{cid} cannot be {check_status} while its required access is blocked or not applicable")
        if not nonempty(item.get("result")):
            errors.append(f"{cid}.result must be non-empty text")
        else:
            normalized_result = re.sub(r"\s+", " ", item["result"].strip().lower())
            result_texts.append(normalized_result)
            facet_text = str(item.get("facet", "")).replace("_", " ").lower()
            normalized_facet_results.append(re.sub(r"\s+", " ", normalized_result.replace(facet_text, "<facet>")))
            if check_status in {"passed", "failed"} and POLICY_ONLY_RESULT.search(item["result"]):
                errors.append(f"{cid} conclusive result states audit policy instead of an observed facet outcome")
        unknowns = string_list(item.get("unknowns"), f"{cid}.unknowns", errors)
        limitations = string_list(item.get("limitations"), f"{cid}.limitations", errors)
        limitation_texts.extend(re.sub(r"\s+", " ", value.strip().lower()) for value in limitations)
        refs = string_list(item.get("limitation_refs"), f"{cid}.limitation_refs", errors)
        if check_status in {"partial", "blocked"} and not unknowns:
            errors.append(f"{cid} {check_status} check requires facet-specific unknowns")
        if check_status in {"partial", "blocked"} and not limitations and not refs:
            errors.append(f"{cid} {check_status} check requires a limitation or reference")
    for mid, module in module_map.items():
        declared = module.get("check_ids") if isinstance(module.get("check_ids"), list) else []
        if Counter(declared) != Counter(module_checks.get(mid, [])):
            errors.append(f"{mid}.check_ids must account for every module check exactly once")
        owned = [check_map[cid] for cid in declared if cid in check_map]
        facets = [item.get("facet") for item in owned]
        if module.get("applicable") is False:
            if facets != ["module_scope"] or any(item.get("status") != "not_applicable" for item in owned):
                errors.append(f"{mid} non-applicable module needs one module_scope not_applicable check")
        else:
            missing = sorted(MODULE_FACETS[mid] - set(facets))
            extra = sorted(set(facets) - MODULE_FACETS[mid], key=str)
            duplicates = sorted((facet for facet, count in Counter(facets).items() if count > 1), key=str)
            if missing:
                errors.append(f"{mid} surface checks missing facets: {', '.join(missing)}")
            if extra:
                errors.append(f"{mid} surface checks contain unknown facets: {', '.join(map(str, extra))}")
            if duplicates:
                errors.append(f"{mid} surface check facets repeated: {', '.join(map(str, duplicates))}")
        statuses = {item.get("status") for item in owned}
        if module.get("status") == "passed" and statuses - {"passed", "not_applicable"}:
            errors.append(f"{mid} passed status disagrees with check statuses")
        if module.get("status") == "failed" and "failed" not in statuses:
            errors.append(f"{mid} failed status requires a failed check")
        if module.get("status") == "partial" and not statuses.intersection({"partial", "blocked"}):
            errors.append(f"{mid} partial status requires a partial or blocked check")
    for label, values in (("results", result_texts), ("limitations", limitation_texts)):
        counts = Counter(value for value in values if value)
        if values and any(count > max(2, len(values) // 5) for count in counts.values()):
            errors.append(f"surface checks contain excessive repeated boilerplate in {label}")
    normalized_counts = Counter(value for value in normalized_facet_results if value)
    if any(count > 2 for count in normalized_counts.values()):
        errors.append("surface checks contain facet-label variation over repeated boilerplate")

    limitation_items = data.get("material_limitations")
    limitation_map: dict[str, dict[str, Any]] = {}
    if not isinstance(limitation_items, list):
        errors.append("material_limitations must be an array")
        limitation_items = []
    for index, item in enumerate(limitation_items, start=1):
        label = f"material_limitations[{index}]"
        exact_keys(item, LIMITATION_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        lid = item.get("id")
        if not isinstance(lid, str) or not LIMITATION_ID.fullmatch(lid):
            errors.append(f"{label}.id is invalid: {lid!r}")
            continue
        if lid in limitation_map:
            errors.append(f"duplicate material limitation ID: {lid}")
        limitation_map[lid] = item
        for field in ("description", "completion_requirement"):
            if not nonempty(item.get(field)):
                errors.append(f"{lid}.{field} must be non-empty text")
        if item.get("status") not in {"open", "resolved"}:
            errors.append(f"{lid}.status has invalid value")
        modules = string_list(item.get("affected_module_ids"), f"{lid}.affected_module_ids", errors, required=True)
        for mid in modules:
            if mid not in MODULE_IDS:
                errors.append(f"{lid} references unknown module: {mid}")
        if item.get("status") == "open":
            provisional.append(f"material limitation {lid} is open")
    for cid, item in check_map.items():
        limitation_refs = item.get("limitation_refs")
        for ref in limitation_refs if isinstance(limitation_refs, list) else []:
            if isinstance(ref, str) and ref.startswith("access:"):
                if ref.split(":", 1)[1] not in ACCESS_CATEGORIES:
                    errors.append(f"{cid} references unknown access limitation: {ref}")
            elif ref not in limitation_map:
                errors.append(f"{cid} references unknown material limitation: {ref}")

    surface_items = data.get("surface_samples")
    surface_ids: set[str] = set()
    viewports: set[str] = set()
    if not isinstance(surface_items, list) or not surface_items:
        errors.append("surface_samples must be a non-empty array")
        surface_items = []
    for index, item in enumerate(surface_items, start=1):
        label = f"surface_samples[{index}]"
        exact_keys(item, SURFACE_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        sid = item.get("id")
        if not isinstance(sid, str) or not SURFACE_ID.fullmatch(sid):
            errors.append(f"{label}.id is invalid: {sid!r}")
            continue
        if sid in surface_ids:
            errors.append(f"duplicate surface sample ID: {sid}")
        surface_ids.add(sid)
        for field in ("surface", "locator", "brand", "audience", "channel", "viewport_or_format"):
            if not nonempty(item.get(field)):
                errors.append(f"{sid}.{field} must be non-empty text")
        if item.get("method") not in CHECK_METHODS:
            errors.append(f"{sid}.method has invalid value")
        sample_status = item.get("status")
        if sample_status not in SAMPLE_STATUSES:
            errors.append(f"{sid}.status has invalid value")
        # Only observed samples count toward the desktop/mobile coverage gate. An
        # unavailable or not_applicable sample records that the surface was NOT
        # captured, so counting it would let the gate pass on absent evidence.
        if sample_status == "observed" and isinstance(item.get("viewport_or_format"), str):
            viewports.add(item["viewport_or_format"].lower())
        parse_date(item.get("observed_at"), f"{sid}.observed_at", errors)
        refs = string_list(item.get("evidence_ids"), f"{sid}.evidence_ids", errors)
        fids = string_list(item.get("finding_ids"), f"{sid}.finding_ids", errors)
        observations = string_list(item.get("observations"), f"{sid}.observations", errors)
        limitations = string_list(item.get("limitations"), f"{sid}.limitations", errors)
        for evid in refs:
            if evid not in evidence:
                errors.append(f"{sid} references unknown evidence: {evid}")
        for fid in fids:
            if fid not in findings:
                errors.append(f"{sid} references unknown finding: {fid}")
        if sample_status == "observed" and (not refs or not observations):
            errors.append(f"{sid} observed sample requires evidence and observations")
        if sample_status == "observed":
            required_classes = METHOD_EVIDENCE_CLASSES.get(item.get("method"))
            sample_classes = {
                evidence[evid].get("evidence_class") for evid in refs if evid in evidence
            }
            if required_classes and not sample_classes.intersection(required_classes):
                errors.append(
                    f"{sid} method {item.get('method')} requires compatible evidence class: "
                    f"{', '.join(sorted(required_classes))}"
                )
            if item.get("method") == "analytics_analysis" and not any(
                evidence[evid].get("evidence_scope") == "business_outcome" for evid in refs if evid in evidence
            ):
                errors.append(f"{sid} method analytics_analysis requires business_outcome evidence")
        if sample_status == "unavailable" and (not refs or not limitations):
            errors.append(f"{sid} unavailable sample requires evidence and limitations")
    if production_available:
        has_desktop = any("desktop" in value or "wide" in value for value in viewports)
        has_mobile = any("mobile" in value or "narrow" in value for value in viewports)
        if not has_desktop or not has_mobile:
            errors.append("material available production website requires desktop and mobile surface samples")
        production_status = audit_mapping(findings_data).get("production_revision_status")
        if status == "complete" and production_status != "verified":
            errors.append("false complete status: available production website requires verified production revision")

    competitor_items = data.get("competitor_samples")
    competitor_ids: set[str] = set()
    observed_competitor = False
    unavailable_competitor = False
    observed_profiles: defaultdict[tuple[Any, ...], list[str]] = defaultdict(list)
    if not isinstance(competitor_items, list) or not competitor_items:
        errors.append("competitor_samples must be a non-empty array")
        competitor_items = []
    for index, item in enumerate(competitor_items, start=1):
        label = f"competitor_samples[{index}]"
        exact_keys(item, COMPETITOR_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        cid = item.get("id")
        if not isinstance(cid, str) or not COMPETITOR_ID.fullmatch(cid):
            errors.append(f"{label}.id is invalid: {cid!r}")
            continue
        if cid in competitor_ids:
            errors.append(f"duplicate competitor sample ID: {cid}")
        competitor_ids.add(cid)
        for field in ("name", "locator", "strategic_consequence"):
            if not nonempty(item.get(field)):
                errors.append(f"{cid}.{field} must be non-empty text")
        if item.get("relationship") not in COMPETITOR_RELATIONSHIPS:
            errors.append(f"{cid}.relationship has invalid value")
        parse_date(item.get("observed_at"), f"{cid}.observed_at", errors)
        competitor_status = item.get("status")
        if competitor_status not in SAMPLE_STATUSES:
            errors.append(f"{cid}.status has invalid value")
        competitor_evidence_ids: list[str] = []
        for field in ("category_language", "trust_conventions", "offer_conventions", "visual_patterns", "strengths", "evidence_ids", "limitations"):
            values = string_list(item.get(field), f"{cid}.{field}", errors)
            if field == "evidence_ids":
                competitor_evidence_ids = values
                for evid in values:
                    if evid not in evidence:
                        errors.append(f"{cid} references unknown evidence: {evid}")
        if competitor_status == "observed":
            observed_competitor = True
            if not competitor_evidence_ids:
                errors.append(f"{cid} observed competitor requires evidence")
            if item.get("relationship") != "inaction":
                matching_sources = [
                    evidence[evid]
                    for evid in competitor_evidence_ids
                    if evid in evidence
                    and evidence[evid].get("evidence_class") == "competitor_evidence"
                    and competitor_evidence_identifies_sample(root, evidence[evid], item)
                ]
                if not matching_sources:
                    errors.append(
                        f"{cid} observed competitor lacks sample-specific competitor evidence "
                        f"identifying its exact name or locator"
                    )
                observed_profiles[competitor_profile_fingerprint(item)].append(cid)
        if competitor_status == "unavailable":
            unavailable_competitor = True
            if not item.get("evidence_ids") or not item.get("limitations"):
                errors.append(f"{cid} unavailable competitor requires evidence and limitations")
    competitive = module_map.get("competitive_landscape", {})
    if competitive.get("applicable") is True:
        if not observed_competitor and not unavailable_competitor:
            errors.append("applicable competitive_landscape requires observed or evidenced-unavailable competitor samples")
        if unavailable_competitor and not observed_competitor and competitive.get("status") not in {"partial", "blocked"}:
            errors.append("competitive landscape with only unavailable evidence must be partial or blocked")
    for ids in (ids for ids in observed_profiles.values() if len(ids) > 1):
        errors.append(
            "observed competitor samples repeat an identical canonical evidence profile: "
            + ", ".join(sorted(ids))
        )

    reconciliation = data.get("narrative_reconciliation")
    covered_files: set[str] = set()
    if not isinstance(reconciliation, list) or not reconciliation:
        errors.append("narrative_reconciliation must be a non-empty array")
        reconciliation = []
    for index, item in enumerate(reconciliation, start=1):
        label = f"narrative_reconciliation[{index}]"
        exact_keys(item, RECONCILIATION_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        location = item.get("location")
        if not nonempty(location):
            errors.append(f"{label}.location must be non-empty text")
        else:
            for filename in NARRATIVE_FILES:
                if location.startswith(filename):
                    covered_files.add(filename)
        ids = string_list(item.get("finding_ids"), f"{label}.finding_ids", errors)
        for fid in ids:
            if fid not in findings:
                errors.append(f"{label} references unknown finding: {fid}")
        explanation = item.get("non_actionable_explanation")
        if ids and explanation not in {None, "None"} and not is_na(explanation):
            errors.append(f"{label} cannot contain findings and a substantive non-actionable explanation")
        if not ids and not nonempty(explanation):
            errors.append(f"{label} needs finding IDs or a non-actionable explanation")
        matched_file = None
        if isinstance(location, str):
            matched_file = next((filename for filename in NARRATIVE_FILES if location.startswith(filename)), None)
        if ids and matched_file and matched_file != "00-executive-verdict.md":
            narrative = (root / matched_file).read_text(encoding="utf-8")
            missing_ids = [
                fid for fid in ids
                if isinstance(fid, str)
                and not re.search(rf"(?<![A-Z0-9-]){re.escape(fid)}(?![A-Z0-9-])", narrative)
            ]
            if missing_ids:
                errors.append(
                    f"{matched_file} reconciliation maps findings not named in the narrative: "
                    + ", ".join(missing_ids)
                )
        if not ids and matched_file:
            narrative = (root / matched_file).read_text(encoding="utf-8")
            action_pattern = re.compile(
                r"\b(should|must|recommend(?:s|ed|ation)?)\b|"
                r"(?:^|[.!?]\s+)(?:Add|Remove|Replace|Decide|Implement|Change|Revise|Create|Adopt|Retain|Preserve)\b",
                re.IGNORECASE,
            )
            if action_pattern.search(narrative):
                errors.append(f"{matched_file} contains actionable language but its reconciliation has no finding IDs")
    missing_narratives = sorted(set(NARRATIVE_FILES) - covered_files)
    if missing_narratives:
        errors.append(f"narrative files missing reconciliation: {', '.join(missing_narratives)}")

    validator = data.get("validator")
    if not isinstance(validator, dict) or set(validator) != {"command", "result"}:
        errors.append("coverage.validator must contain exactly command and result")
    else:
        if not nonempty(validator.get("command")) or "validate_brand_teardown.py" not in validator.get("command", ""):
            errors.append("coverage.validator.command must name validate_brand_teardown.py")
        if validator.get("result") != "passed":
            errors.append("coverage.validator.result must be passed for delivery")

    strengths = [item for item in findings.values() if item.get("kind") == "strength" and item.get("status") == "retained_strength"]
    justification = audit_mapping(findings_data).get("zero_strengths_justification")
    if not strengths and not nonempty(justification):
        errors.append("zero retained strengths requires audit.zero_strengths_justification")
    if strengths and justification is not None:
        errors.append("zero_strengths_justification must be null when retained strengths exist")
    if status == "complete" and provisional:
        errors.append("false complete status: " + "; ".join(provisional))


def validate_status_and_generated(root: Path, expected_status: str | None, errors: list[str]) -> None:
    executive = (root / "00-executive-verdict.md").read_text(encoding="utf-8")
    match = REVIEW_STATUS_LINE.search(executive)
    if not match:
        errors.append("00-executive-verdict.md is missing an exact Review status line")
    elif expected_status and match.group(1) != expected_status:
        errors.append("executive verdict review status disagrees with canonical JSON")
    readme = (root / "README.md").read_text(encoding="utf-8")
    for token in ("findings.json", "coverage.json", "render_handoff.py", "validate_brand_teardown.py", "read-only"):
        if token.lower() not in readme.lower():
            errors.append(f"README.md must mention {token}")
    for label in (
        "Project", "Audited revision", "Production locator", "Audit dates",
        "Review status", "Boundary", "Canonical files", "Evidence limitations",
    ):
        if not re.search(rf"(?mi)^- \*\*{re.escape(label)}:\*\*\s+\S", readme):
            errors.append(f"README.md must contain a non-empty '{label}' metadata line")
    portable_commands = (
        "python3 <skill-directory>/scripts/render_handoff.py <brand-teardown-directory>",
        "python3 <skill-directory>/scripts/validate_brand_teardown.py <brand-teardown-directory>",
    )
    for command in portable_commands:
        if command not in readme:
            errors.append(f"README.md must contain the portable command: {command}")
    for filename, headings in NARRATIVE_SECTIONS.items():
        narrative = (root / filename).read_text(encoding="utf-8")
        paragraphs = [
            re.sub(r"\s+", " ", paragraph).strip().lower()
            for paragraph in re.split(r"\n\s*\n", narrative)
            if len(re.sub(r"\s+", " ", paragraph).strip()) >= 100
        ]
        repeated_paragraphs = [text for text, count in Counter(paragraphs).items() if count > 1]
        if repeated_paragraphs:
            errors.append(f"{filename} contains repeated substantive narrative paragraphs")
        for heading in headings:
            match = re.search(rf"(?m)^## {re.escape(heading)}\s*$", narrative)
            if not match:
                errors.append(f"{filename} missing required section: {heading}")
                continue
            body_start = match.end()
            next_heading = re.search(r"(?m)^## ", narrative[body_start:])
            body_end = body_start + next_heading.start() if next_heading else len(narrative)
            body = re.sub(r"\s+", " ", narrative[body_start:body_end]).strip()
            if len(body) < 120:
                errors.append(f"{filename} section '{heading}' is too thin for the report contract")
    try:
        expected = rendered_files(root)
    except Exception as exc:
        errors.append(f"cannot render canonical Markdown: {exc}")
        return
    for name, content in expected.items():
        path = root / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            errors.append(f"{name} disagrees with canonical JSON; rerun render_handoff.py")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"teardown directory does not exist: {root}"]
    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            errors.append(f"missing required file: {name}")
    if (root / "evidence").is_symlink() or not (root / "evidence").is_dir():
        errors.append("missing required directory: evidence")
    if errors:
        return errors
    findings_data = load_object(root / "findings.json", errors)
    coverage_data = load_object(root / "coverage.json", errors)
    if errors:
        return errors
    audit_end, window, status = validate_audit(findings_data, errors)
    evidence = validate_evidence(root, findings_data, audit_end, window, errors)
    audit_revision_refs = audit_mapping(findings_data).get("production_revision_evidence_ids", [])
    if isinstance(audit_revision_refs, list):
        for evid in audit_revision_refs:
            if evid not in evidence:
                errors.append(f"audit production revision references unknown evidence ID: {evid}")
    validate_production_revision_evidence(findings_data, evidence, errors)
    findings = validate_findings(findings_data, evidence, errors)
    validate_claims(findings_data, evidence, errors)
    validate_graph_and_phases(findings_data, findings, errors)
    validate_coverage(root, coverage_data, findings_data, findings, evidence, status, errors)
    validate_status_and_generated(root, status, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown", type=Path)
    args = parser.parse_args()
    errors = validate(args.teardown.resolve())
    if errors:
        print(f"Brand teardown validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Brand teardown validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
