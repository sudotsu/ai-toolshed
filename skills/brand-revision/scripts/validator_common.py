#!/usr/bin/env python3
"""Structural primitives and shared invariants for brand-revision validation."""
from __future__ import annotations

import re
from typing import Any, Iterable

from validation_common import (
    AUTHORITY_IDS, DELIVERY_KEYS, EVIDENCE_LEVELS, EVIDENCE_METHODS, PLACEHOLDER_TOKENS,
)

REQUIRED_TOP = {
    "schema_version",
    "mode",
    "project",
    "generated_at",
    "teardown",
    "workspace",
    "decisions",
    "authority_matrix",
    "findings",
    "claim_trace",
    "coverage_trace",
    "changes",
    "evidence",
    "perception_tests",
    "convergence_findings",
    "rollouts",
    "readiness",
}

DECISION_CATEGORIES = {
    "brand-architecture", "positioning", "audience", "promise", "offer", "guarantee",
    "founder-posture", "visual-identity", "claim-posture", "channel-migration",
    "accepted-risk", "external-authority", "other",
}
APPROVALS = {"pending", "approved", "deferred", "rejected", "accepted-risk", "not-applicable"}
REVALIDATIONS = {"pending", "confirmed", "changed", "stale", "already-resolved", "not-applicable", "blocked"}
DISPOSITIONS = {"planned", "implemented", "already-satisfied", "preserved", "deferred", "rejected", "accepted-risk", "not-applicable", "blocked", "investigating"}
PRESERVATION_STATES = {"pending", "preserved", "owner-approved-tradeoff", "not-applicable", "failed"}
ACCEPTANCE_STATES = {"pending", "passed", "failed", "blocked", "not-applicable"}
CLAIM_ACTIONS = {"pending", "preserve", "correct", "qualify", "remove", "verify", "not-applicable", "unchanged"}
CLAIM_STATES = {"verified", "plausible_unverified", "unsupported", "contradicted", "outdated", "not_applicable"}
CLAIM_VERIFY_STATES = {"pending", "verified", "unverified", "blocked", "not-applicable"}
CHANGE_SCOPES = {"repository", "content", "asset", "configuration", "cms", "external-profile", "business-listing", "published-channel", "other"}
RISK_LEVELS = {"low", "medium", "high"}
RISK_CATEGORIES = {"brand-architecture", "claim", "credential", "guarantee", "offer", "identity-recognition", "domain-channel-migration", "proof-publication", "customer-journey", "accessibility-legibility", "seo-discoverability", "analytics-measurement", "other"}
PERCEPTION_DIMENSIONS = {"comprehension", "trust", "differentiation", "recognition", "preference", "action-clarity"}
PERCEPTION_STATES = {"planned", "completed", "blocked", "not-applicable"}
CONVERGENCE_SEVERITIES = {"critical", "high", "medium", "low"}
CONVERGENCE_STATES = {"fixed", "already-satisfied", "invalid", "open", "deferred", "blocked"}
ROLLOUT_STATES = {"planned", "staged", "activated", "verified", "blocked", "not-required"}
AUTHORITY_STATES = {"authorized", "not-authorized", "not-requested", "blocked"}
EVIDENCE_STATES = {"completed", "failed", "blocked", "not-applicable"}
DELIVERY_STATES = {"verified", "not-performed", "unverified", "not-applicable"}
REVISION_STATUSES = {"planned", "complete", "partial", "blocked"}
CONVERGENCE_READINESS = {"not-run", "passed", "blocked"}
READY_STATES = {"ready", "not-ready", "not-applicable"}
PERCEPTION_READINESS = {"not-started", "observed", "partially-observed", "blocked", "not-applicable"}
BUSINESS_READINESS = {"unverified", "observed", "blocked", "not-applicable"}
AUTH_SUMMARY = {"complete", "partial", "blocked"}

CHANGE_AUTHORITY = {
    "repository": "AUTH-REPOSITORY-EDIT",
    "content": "AUTH-CONTENT-EDIT",
    "asset": "AUTH-ASSET-EDIT",
    "configuration": "AUTH-CONFIGURATION-EDIT",
    "cms": "AUTH-CMS-MUTATION",
    "external-profile": "AUTH-SOCIAL-PROFILE",
    "business-listing": "AUTH-BUSINESS-LISTING",
    "published-channel": "AUTH-PUBLISH",
}
DELIVERY_AUTHORITY = {
    "committed": "AUTH-COMMIT",
    "pushed": "AUTH-PUSH",
    "pull_request": "AUTH-PULL-REQUEST",
    "merged": "AUTH-MERGE",
    "deployed": "AUTH-DEPLOY",
    "published": "AUTH-PUBLISH",
    "social_profile_changes": "AUTH-SOCIAL-PROFILE",
    "business_listing_changes": "AUTH-BUSINESS-LISTING",
    "outreach": "AUTH-OUTREACH",
}
ID_PATTERNS = {
    "decision": re.compile(r"^DEC-\d{3}$"),
    "change": re.compile(r"^CHG-\d{3}$"),
    "evidence": re.compile(r"^REV-EVID-\d{3}$"),
    "perception": re.compile(r"^PERCEPT-\d{3}$"),
    "convergence": re.compile(r"^REV-\d{3}$"),
    "rollout": re.compile(r"^ROLLOUT-\d{3}$"),
}


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    return type(value).__name__


def _obj(value: Any, path: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object, got {_type_name(value)}")
        return None
    return value


def _arr(value: Any, path: str, errors: list[str]) -> list[Any] | None:
    if not isinstance(value, list):
        errors.append(f"{path} must be an array, got {_type_name(value)}")
        return None
    return value


def _str(value: Any, path: str, errors: list[str], *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string" + (" or null" if nullable else ""))
        return None
    return value


def _bool(value: Any, path: str, errors: list[str]) -> bool | None:
    if not isinstance(value, bool):
        errors.append(f"{path} must be a boolean")
        return None
    return value


def _enum(value: Any, allowed: set[str], path: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or value not in allowed:
        errors.append(f"{path} must be one of {sorted(allowed)}")
        return None
    return value


def _int(value: Any, path: str, errors: list[str], *, positive: bool = False) -> int | None:
    if not isinstance(value, int) or isinstance(value, bool) or (positive and value <= 0):
        errors.append(f"{path} must be {'a positive ' if positive else 'an '}integer")
        return None
    return value


def _str_list(value: Any, path: str, errors: list[str], *, allow_empty: bool = True) -> list[str] | None:
    arr = _arr(value, path, errors)
    if arr is None:
        return None
    if not allow_empty and not arr:
        errors.append(f"{path} must not be empty")
    bad = [i for i, item in enumerate(arr) if not isinstance(item, str) or not item.strip()]
    for i in bad:
        errors.append(f"{path}[{i}] must be a non-empty string")
    if len(arr) != len(set(item for item in arr if isinstance(item, str))):
        errors.append(f"{path} must not contain duplicate strings")
    return arr if not bad else None


def _required(obj: dict[str, Any], keys: Iterable[str], path: str, errors: list[str], *, exact: bool = False) -> None:
    expected = set(keys)
    missing = sorted(expected - set(obj))
    if missing:
        errors.append(f"{path} missing required key(s): {', '.join(missing)}")
    if exact:
        extra = sorted(set(obj) - expected)
        if extra:
            errors.append(f"{path} contains unexpected key(s): {', '.join(extra)}")


def _unique_ids(items: list[Any], path: str, errors: list[str], pattern: re.Pattern[str] | None = None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(items):
        row = _obj(item, f"{path}[{i}]", errors)
        if row is None:
            continue
        rid = _str(row.get("id"), f"{path}[{i}].id", errors)
        if rid is None:
            continue
        if pattern and not pattern.match(rid):
            errors.append(f"{path}[{i}].id has invalid format: {rid}")
        if rid in out:
            errors.append(f"duplicate ID in {path}: {rid}")
        else:
            out[rid] = row
    return out


def _completed_evidence(evidence_by_id: dict[str, dict[str, Any]], evidence_ids: Any) -> bool:
    if not isinstance(evidence_ids, list) or not evidence_ids:
        return False
    for eid in evidence_ids:
        row = evidence_by_id.get(eid) if isinstance(eid, str) else None
        if row is None or row.get("status") != "completed":
            return False
    return True


def _evidence_with_level(evidence_by_id: dict[str, dict[str, Any]], ids: Any, level: str) -> bool:
    return isinstance(ids, list) and any(isinstance(eid, str) and evidence_by_id.get(eid, {}).get("status") == "completed" and evidence_by_id.get(eid, {}).get("level") == level for eid in ids)


def _evidence_with_method(evidence_by_id: dict[str, dict[str, Any]], ids: Any, method: str) -> bool:
    return isinstance(ids, list) and any(isinstance(eid, str) and evidence_by_id.get(eid, {}).get("status") == "completed" and evidence_by_id.get(eid, {}).get("method") == method for eid in ids)


def _shape_teardown(findings: Any, coverage: Any, errors: list[str]) -> bool:
    f = _obj(findings, "teardown.findings.json", errors)
    c = _obj(coverage, "teardown.coverage.json", errors)
    if f is None or c is None:
        return False
    _required(f, {"schema_version", "audit", "claims", "findings"}, "teardown.findings.json", errors)
    _required(c, {"schema_version", "access", "modules", "surface_checks", "material_limitations"}, "teardown.coverage.json", errors)
    audit = _obj(f.get("audit"), "teardown.audit", errors)
    if audit is not None:
        _required(audit, {"project_name", "project_locator", "audited_revision", "production_locator", "review_status"}, "teardown.audit", errors)
        for key in ("project_name", "project_locator", "audited_revision", "review_status"):
            _str(audit.get(key), f"teardown.audit.{key}", errors)
        if audit.get("production_locator") is not None:
            _str(audit.get("production_locator"), "teardown.audit.production_locator", errors, nullable=True)
    sf = _arr(f.get("findings"), "teardown.findings", errors)
    if sf is not None:
        for i, row in enumerate(sf):
            item = _obj(row, f"teardown.findings[{i}]", errors)
            if item is None:
                continue
            _required(item, {"id", "title", "status", "dependencies", "acceptance_criteria", "preservation_constraints", "implementation"}, f"teardown.findings[{i}]", errors)
            _str(item.get("id"), f"teardown.findings[{i}].id", errors)
            _str(item.get("title"), f"teardown.findings[{i}].title", errors)
            _str(item.get("status"), f"teardown.findings[{i}].status", errors)
            _str_list(item.get("dependencies"), f"teardown.findings[{i}].dependencies", errors)
            _str_list(item.get("acceptance_criteria"), f"teardown.findings[{i}].acceptance_criteria", errors, allow_empty=False)
            _str_list(item.get("preservation_constraints"), f"teardown.findings[{i}].preservation_constraints", errors)
            impl = _obj(item.get("implementation"), f"teardown.findings[{i}].implementation", errors)
            if impl is not None:
                _required(impl, {"order"}, f"teardown.findings[{i}].implementation", errors)
                _int(impl.get("order"), f"teardown.findings[{i}].implementation.order", errors, positive=True)
    claims = _arr(f.get("claims"), "teardown.claims", errors)
    if claims is not None:
        for i, row in enumerate(claims):
            item = _obj(row, f"teardown.claims[{i}]", errors)
            if item is None:
                continue
            _required(item, {"id", "claim", "brand", "state"}, f"teardown.claims[{i}]", errors)
            for key in ("id", "claim", "brand", "state"):
                _str(item.get(key), f"teardown.claims[{i}].{key}", errors)

    for key, idkey in (("access", "category"), ("modules", "id"), ("surface_checks", "id")):
        rows = _arr(c.get(key), f"teardown.coverage.{key}", errors)
        if rows is None:
            continue
        for i, row in enumerate(rows):
            item = _obj(row, f"teardown.coverage.{key}[{i}]", errors)
            if item is None:
                continue
            _required(item, {idkey, "status"}, f"teardown.coverage.{key}[{i}]", errors)
            _str(item.get(idkey), f"teardown.coverage.{key}[{i}].{idkey}", errors)
            _str(item.get("status"), f"teardown.coverage.{key}[{i}].status", errors)
            if item.get("next_step") is not None:
                _str(item.get("next_step"), f"teardown.coverage.{key}[{i}].next_step", errors, nullable=True)

    limits = _arr(c.get("material_limitations"), "teardown.coverage.material_limitations", errors)
    if limits is not None:
        for i, row in enumerate(limits):
            item = _obj(row, f"teardown.coverage.material_limitations[{i}]", errors)
            if item is None:
                continue
            _required(item, {"id", "description", "status", "completion_requirement"}, f"teardown.coverage.material_limitations[{i}]", errors)
            for field in ("id", "description", "status", "completion_requirement"):
                _str(item.get(field), f"teardown.coverage.material_limitations[{i}].{field}", errors)
    return not errors