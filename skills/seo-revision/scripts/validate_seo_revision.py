#!/usr/bin/env python3
"""Validate an seo-revision artifact against an exact validated seo-teardown v3 handoff."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from render_revision import rendered_files


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
    "00-decisions-authority-and-scope.md",
    "01-baseline-drift-and-revalidation.md",
    "02-execution-rollout-and-measurement-plan.md",
    "03-implementation-ledger.md",
    "04-convergence-ledger.md",
    "05-production-search-and-experiment-verification.md",
    "06-readiness-and-handoff.md",
    "revision.json",
)

TOP_KEYS = ControlledValues({
    "schema_version",
    "mode",
    "project",
    "generated_at",
    "teardown",
    "workspace",
    "decisions",
    "authority_matrix",
    "findings",
    "coverage_trace",
    "changes",
    "evidence",
    "url_verifications",
    "experiments",
    "convergence_findings",
    "rollouts",
    "readiness",
})
PROJECT_KEYS = ControlledValues({"name", "locator"})
TEARDOWN_KEYS = ControlledValues({
    "path",
    "findings_schema",
    "coverage_schema",
    "audited_revision",
    "review_status",
    "validator_command",
    "validator_result",
})
WORKSPACE_KEYS = ControlledValues({
    "implementation_start_revision",
    "product_endpoint",
    "endpoint_kind",
    "artifact_relationship",
    "existing_work_reconciled",
    "staged_paths",
    "unstaged_paths",
    "untracked_paths",
    "baseline_evidence_ids",
})
DECISION_KEYS = ControlledValues({
    "id",
    "finding_ids",
    "status",
    "question",
    "options",
    "recommendation",
    "owner_selection",
    "safe_default",
    "consequences",
    "prerequisites",
    "reversibility",
})
OPTION_KEYS = ControlledValues({"id", "label", "consequences", "prerequisites", "reversibility"})
AUTHORITY_KEYS = ControlledValues({"id", "state", "scope", "evidence_ids", "limitations"})
FINDING_KEYS = ControlledValues({
    "id",
    "title",
    "approval",
    "revalidation",
    "disposition",
    "sequence",
    "dependencies",
    "reason",
    "acceptance_results",
    "evidence_ids",
    "change_ids",
    "experiment_ids",
    "completion_gates",
    "notes",
})
ACCEPTANCE_KEYS = ControlledValues({"criterion", "status", "evidence_ids", "observation"})
TRACE_KEYS = ControlledValues({"access", "surface_checks", "material_limitations", "deliberate_non_pursuits"})
ACCESS_TRACE_KEYS = ControlledValues({"category", "source_status", "disposition", "completion_gate", "evidence_ids"})
CHECK_TRACE_KEYS = ControlledValues({"id", "source_status", "disposition", "completion_gate", "evidence_ids"})
LIMIT_TRACE_KEYS = ControlledValues({"id", "source_status", "disposition", "completion_gate", "evidence_ids"})
NON_PURSUIT_KEYS = ControlledValues({"topic", "rationale", "preservation_rule", "evidence_ids"})
CHANGE_KEYS = ControlledValues({
    "id",
    "scope",
    "finding_ids",
    "convergence_ids",
    "targets",
    "description",
    "external_authority_ids",
    "risk_level",
    "risk_categories",
    "rollout_id",
    "evidence_ids",
})
EVIDENCE_KEYS = ControlledValues({
    "id",
    "level",
    "method",
    "status",
    "observation",
    "artifact_path",
    "limitations",
    "observed_at",
})
URL_KEYS = ControlledValues({
    "id",
    "url",
    "environment",
    "method_evidence",
    "observations",
    "evidence_ids",
    "limitations",
})
METHOD_KEYS = ControlledValues({"method", "status", "observation", "evidence_ids", "limitations"})
OBSERVATION_KEYS = ControlledValues({
    "dimension",
    "status",
    "value",
    "supported_by_methods",
    "evidence_ids",
    "limitations",
})
EXPERIMENT_KEYS = ControlledValues({
    "id",
    "finding_ids",
    "status",
    "hypothesis",
    "evidence_basis",
    "segment",
    "affected_pages_queries",
    "baseline",
    "primary_metric",
    "guardrails",
    "sample_requirement",
    "expected_time_to_evidence",
    "confounders",
    "stop_rollback_criteria",
    "decision_rule",
    "observation_owner",
    "next_review_at",
    "evidence_ids",
})
CONVERGENCE_KEYS = ControlledValues({
    "id",
    "title",
    "source",
    "severity",
    "status",
    "reason",
    "reopened_finding_ids",
    "change_ids",
    "evidence_ids",
})
ROLLOUT_KEYS = ControlledValues({
    "id",
    "change_ids",
    "state",
    "inventory",
    "representative_samples",
    "collision_checks",
    "rollback_plan",
    "evidence_ids",
})
READINESS_KEYS = ControlledValues({
    "revision_status",
    "review_convergence",
    "integration",
    "deployment",
    "publication",
    "search_validation",
    "experiment_status",
    "authorization_summary",
    "convergence_evidence_ids",
    "delivery",
    "unverified_outcomes",
    "follow_up_actions",
})
DELIVERY_KEYS = ControlledValues({
    "committed",
    "pushed",
    "pull_request",
    "merged",
    "deployed",
    "published",
    "search_platform_actions",
    "external_profile_actions",
})
DELIVERY_ITEM_KEYS = ControlledValues({"state", "evidence_ids", "observation"})

AUTHORITY_IDS = ControlledValues({
    "local_repository_edits",
    "cms_content_database_edits",
    "commit_push",
    "pull_request",
    "merge",
    "deployment",
    "publication",
    "search_controls_activation",
    "search_platform_actions",
    "profile_listing_actions",
    "analytics_tracking_actions",
    "outreach_third_party",
    "purchases_external_services",
    "regulated_content_approval",
})
DELIVERY_AUTHORITY = {
    "committed": "commit_push",
    "pushed": "commit_push",
    "pull_request": "pull_request",
    "merged": "merge",
    "deployed": "deployment",
    "published": "publication",
    "search_platform_actions": "search_platform_actions",
    "external_profile_actions": "profile_listing_actions",
}
CHANGE_SCOPE_AUTHORITY = {
    "repository": "local_repository_edits",
    "content": "local_repository_edits",
    "configuration": "local_repository_edits",
    "asset": "local_repository_edits",
    "cms": "cms_content_database_edits",
}

MODES = ControlledValues({"planning-only", "implementation"})
ENDPOINT_KINDS = ControlledValues({"immutable-revision", "working-tree"})
ARTIFACT_RELATIONSHIPS = ControlledValues({"working-tree", "artifact-only-descendant"})
DECISION_STATUSES = ControlledValues({"pending", "resolved", "blocked"})
AUTHORITY_STATES = ControlledValues({"authorized", "not-authorized", "not-requested", "blocked"})
APPROVALS = ControlledValues({"approved", "deferred", "rejected", "accepted-risk", "not-applicable"})
REVALIDATIONS = ControlledValues({"confirmed", "changed", "stale", "already-resolved", "not-applicable", "blocked"})
DISPOSITIONS = ControlledValues({
    "planned",
    "implemented",
    "already-satisfied",
    "preserved",
    "deferred",
    "rejected",
    "accepted-risk",
    "not-applicable",
    "blocked",
    "experiment-planned",
    "experiment-launched",
    "experiment-observing",
})
ALLOWED_DISPOSITIONS = {
    "approved": {
        "planned",
        "implemented",
        "already-satisfied",
        "preserved",
        "blocked",
        "experiment-planned",
        "experiment-launched",
        "experiment-observing",
    },
    "deferred": {"deferred"},
    "rejected": {"rejected"},
    "accepted-risk": {"accepted-risk"},
    "not-applicable": {"not-applicable"},
}
ACCEPTANCE_STATUSES = ControlledValues({"pending", "passed", "failed", "blocked", "not-applicable"})
ACCESS_DISPOSITIONS = ControlledValues({"action", "decision", "blocker", "preserve", "not-applicable"})
CHECK_DISPOSITIONS = ControlledValues({
    "action",
    "decision",
    "blocker",
    "preserve",
    "experiment",
    "completion-gate",
    "not-applicable",
})
LIMIT_DISPOSITIONS = ControlledValues({"open", "resolved", "not-applicable"})
CHANGE_SCOPES = ControlledValues({"repository", "cms", "content", "configuration", "asset", "external-system"})
RISK_LEVELS = ControlledValues({"low", "medium", "high"})
RISK_CATEGORIES = ControlledValues({
    "redirect-url-migration",
    "canonical-noindex",
    "robots-sitemap",
    "structured-data",
    "programmatic-template",
    "dynamic-user-url",
    "content-removal",
    "analytics-consent",
    "conversion-path",
    "profile-listing",
    "regulated-claim",
    "javascript-rendering",
    "browser-mobile-accessibility",
    "other",
})
EVIDENCE_LEVELS = ControlledValues({
    "source-inspection",
    "build-unit",
    "local-render",
    "preview-staging",
    "deployed-production",
    "search-platform-observation",
    "business-outcome",
})
EVIDENCE_METHODS = ControlledValues({
    "source-inspection",
    "build-unit",
    "controlled-test",
    "local-crawl",
    "rendered-browser",
    "live-fetch",
    "platform-data",
    "serp-observation",
    "first-party-analysis",
    "external-research",
    "owner-authorization",
})
EVIDENCE_STATUSES = ControlledValues({"completed", "failed", "blocked", "not-applicable"})
URL_ENVIRONMENTS = ControlledValues({"local", "preview-staging", "production"})
OBSERVATION_DIMENSIONS = ControlledValues({
    "http",
    "canonical",
    "render",
    "eligibility",
    "index",
    "visibility",
    "ai-citation",
    "conversion",
    "business-outcome",
})
OBSERVATION_STATUSES = ControlledValues({"observed", "unavailable", "not-applicable"})
EXPERIMENT_STATUSES = ControlledValues({"planned", "launched", "observing", "validated", "rejected", "blocked"})
CONVERGENCE_SEVERITIES = ControlledValues({"critical", "high", "medium", "low"})
CONVERGENCE_STATUSES = ControlledValues({"fixed", "already-satisfied", "invalid", "open", "deferred", "blocked"})
ROLLOUT_STATES = ControlledValues({"not-required", "planned", "staged", "activated", "verified", "blocked"})
REVISION_STATUSES = ControlledValues({"planned", "complete", "partial", "blocked"})
REVIEW_CONVERGENCE = ControlledValues({"not-run", "passed", "blocked"})
READY_STATES = ControlledValues({"ready", "not-ready", "not-applicable"})
SEARCH_VALIDATION = ControlledValues({
    "not-started",
    "eligibility-verified",
    "index-observed",
    "visibility-observed",
    "outcome-observed",
    "blocked",
    "not-applicable",
})
EXPERIMENT_SUMMARY = ControlledValues({
    "not-applicable",
    "planned",
    "launched",
    "observing",
    "validated",
    "rejected",
    "blocked",
    "mixed",
})
AUTHORIZATION_SUMMARY = ControlledValues({"complete", "partial", "blocked"})
DELIVERY_STATES = ControlledValues({"verified", "not-performed", "unverified", "not-applicable"})

ID_PATTERNS = {
    "decision": re.compile(r"^DEC-\d{3}$"),
    "change": re.compile(r"^CHG-\d{3}$"),
    "evidence": re.compile(r"^REV-EVID-\d{3}$"),
    "url": re.compile(r"^VERIFY-URL-\d{3}$"),
    "experiment": re.compile(r"^EXP-\d{3}$"),
    "convergence": re.compile(r"^REV-\d{3}$"),
    "rollout": re.compile(r"^ROLLOUT-\d{3}$"),
}
PLACEHOLDER = re.compile(r"\b(?:todo|tbd|placeholder|lorem ipsum|coming soon)\b|<fill", re.IGNORECASE)


def load_object(path: Path, label: str, errors: list[str]) -> dict[str, Any]:
    try:
        value = harden_json(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read {label}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label} must contain an object")
        return {}
    return value


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


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_text(value: Any, label: str, errors: list[str], *, allow_placeholder: bool = False) -> None:
    if not nonempty(value):
        errors.append(f"{label} must be non-empty text")
    elif not allow_placeholder and PLACEHOLDER.search(value):
        errors.append(f"{label} contains placeholder boilerplate")


def require_string_list(
    value: Any,
    label: str,
    errors: list[str],
    *,
    nonempty_list: bool = False,
    placeholders: bool = False,
) -> list[str]:
    if not isinstance(value, list) or any(not nonempty(item) for item in value):
        errors.append(f"{label} must be a list of non-empty strings")
        return []
    if nonempty_list and not value:
        errors.append(f"{label} must not be empty")
    if placeholders and any(PLACEHOLDER.search(item) for item in value):
        errors.append(f"{label} contains placeholder boilerplate")
    return value


def unique_id(value: Any, kind: str, seen: set[str], label: str, errors: list[str]) -> str | None:
    pattern = ID_PATTERNS[kind]
    if not isinstance(value, str) or not pattern.fullmatch(value):
        errors.append(f"{label} has invalid {kind} id: {value!r}")
        return None
    if value in seen:
        errors.append(f"duplicate {kind} id: {value}")
        return None
    seen.add(value)
    return value


def parse_time(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO-8601 timestamp")
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp")


def read_frontmatter_name(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.match(r"^---\n([\s\S]*?)\n---\n", text)
    if not match:
        return None
    name = re.search(r"^name:\s*(.+?)\s*$", match.group(1), re.MULTILINE)
    return name.group(1).strip() if name else None


def locate_seo_teardown(explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        root = explicit.resolve()
        if read_frontmatter_name(root / "SKILL.md") == "seo-teardown":
            return root
        return None
    candidates: list[Path] = []
    roots: list[Path] = [Path.home() / ".agents" / "skills"]
    codex_homes = [Path.home() / ".codex"]
    if os.environ.get("CODEX_HOME"):
        codex_homes.insert(0, Path(os.environ["CODEX_HOME"]).expanduser())
    for codex_home in codex_homes:
        roots.extend((codex_home / "skills" / "remote-skills", codex_home / "skills"))
    for root in roots:
        if not root.is_dir():
            continue
        candidates.extend(root.glob("skill-*/SKILL.md"))
        candidates.extend(root.glob("seo-teardown/SKILL.md"))
    for skill_md in candidates:
        if read_frontmatter_name(skill_md) == "seo-teardown":
            return skill_md.parent
    return None


def run_upstream_validator(teardown_root: Path, skill_root: Path | None, errors: list[str]) -> Path | None:
    resolved = locate_seo_teardown(skill_root)
    if resolved is None:
        errors.append("cannot locate an installed skill with name frontmatter seo-teardown")
        return None
    validator = resolved / "scripts" / "validate_seo_teardown.py"
    if not validator.is_file():
        errors.append("installed seo-teardown is missing scripts/validate_seo_teardown.py")
        return None
    try:
        proc = subprocess.run(
            [sys.executable, str(validator), str(teardown_root)],
            cwd=validator.parent,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        errors.append("exact upstream seo-teardown validation timed out after 120 seconds")
        return resolved
    if proc.returncode != 0:
        detail = (proc.stdout + proc.stderr).strip()
        errors.append("exact upstream seo-teardown validation failed" + (f": {detail}" if detail else ""))
    return resolved


def validate_evidence(items: Any, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append("evidence must be a list")
        return {}
    seen: set[str] = set()
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items, start=1):
        label = f"evidence[{index}]"
        if not exact_keys(item, EVIDENCE_KEYS, label, errors):
            if not isinstance(item, dict):
                continue
        evid = unique_id(item.get("id"), "evidence", seen, label, errors)
        if evid is None:
            continue
        result[evid] = item
        if item.get("level") not in EVIDENCE_LEVELS:
            errors.append(f"{evid} has invalid evidence level: {item.get('level')!r}")
        if item.get("method") not in EVIDENCE_METHODS:
            errors.append(f"{evid} has invalid evidence method: {item.get('method')!r}")
        status = item.get("status")
        if status not in EVIDENCE_STATUSES:
            errors.append(f"{evid} has invalid evidence status: {status!r}")
        require_text(item.get("observation"), f"{evid} observation", errors)
        limitations = require_string_list(item.get("limitations"), f"{evid} limitations", errors, placeholders=True)
        artifact = item.get("artifact_path")
        if artifact is not None and not nonempty(artifact):
            errors.append(f"{evid} artifact_path must be text or null")
        parse_time(item.get("observed_at"), f"{evid} observed_at", errors)
        if status in {"failed", "blocked"} and not limitations:
            errors.append(f"{evid} {status} evidence requires limitations")
    return result


def validate_refs(
    refs: Any,
    label: str,
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    nonempty_list: bool = False,
    completed: bool = False,
) -> list[str]:
    values = require_string_list(refs, label, errors, nonempty_list=nonempty_list)
    for evid in values:
        item = evidence_map.get(evid)
        if item is None:
            errors.append(f"{label} references unknown evidence: {evid}")
        elif completed and item.get("status") != "completed":
            errors.append(f"{label} cannot rely on non-completed evidence: {evid}")
    return values


def validate_header(
    data: dict[str, Any],
    teardown_findings: dict[str, Any],
    teardown_coverage: dict[str, Any],
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
) -> tuple[str | None, dict[str, dict[str, Any]]]:
    exact_keys(data, TOP_KEYS, "revision.json", errors)
    if data.get("schema_version") != "seo-revision-v1":
        errors.append("schema_version must be 'seo-revision-v1'")
    mode = data.get("mode")
    if mode not in MODES:
        errors.append(f"mode has invalid value: {mode!r}")
        mode = None
    parse_time(data.get("generated_at"), "generated_at", errors)

    project = data.get("project")
    exact_keys(project, PROJECT_KEYS, "project", errors)
    if isinstance(project, dict):
        require_text(project.get("name"), "project.name", errors)
        require_text(project.get("locator"), "project.locator", errors)
        source_name = teardown_findings.get("audit", {}).get("project_name")
        if project.get("name") != source_name:
            errors.append("project.name does not match teardown audit.project_name")

    teardown = data.get("teardown")
    exact_keys(teardown, TEARDOWN_KEYS, "teardown", errors)
    if isinstance(teardown, dict):
        require_text(teardown.get("path"), "teardown.path", errors)
        if teardown.get("findings_schema") != "seo-teardown-v3":
            errors.append("teardown.findings_schema must be seo-teardown-v3")
        if teardown.get("coverage_schema") != "seo-teardown-coverage-v3":
            errors.append("teardown.coverage_schema must be seo-teardown-coverage-v3")
        audit = teardown_findings.get("audit", {})
        if teardown.get("audited_revision") != audit.get("audited_revision"):
            errors.append("teardown.audited_revision does not match canonical teardown")
        if teardown.get("review_status") != audit.get("review_status"):
            errors.append("teardown.review_status does not match canonical teardown")
        if teardown.get("validator_result") != "passed":
            errors.append("teardown.validator_result must be passed")
        command = teardown.get("validator_command")
        if not nonempty(command) or "validate_seo_teardown.py" not in command:
            errors.append("teardown.validator_command must name validate_seo_teardown.py")
        if teardown_coverage.get("schema_version") != teardown.get("coverage_schema"):
            errors.append("teardown coverage schema identity does not match coverage.json")
        if teardown_findings.get("schema_version") != teardown.get("findings_schema"):
            errors.append("teardown findings schema identity does not match findings.json")

    workspace = data.get("workspace")
    exact_keys(workspace, WORKSPACE_KEYS, "workspace", errors)
    if isinstance(workspace, dict):
        for key in ("implementation_start_revision", "product_endpoint"):
            require_text(workspace.get(key), f"workspace.{key}", errors)
        if workspace.get("endpoint_kind") not in ENDPOINT_KINDS:
            errors.append(f"workspace.endpoint_kind has invalid value: {workspace.get('endpoint_kind')!r}")
        relationship = workspace.get("artifact_relationship")
        if relationship not in ARTIFACT_RELATIONSHIPS:
            errors.append(f"workspace.artifact_relationship has invalid value: {relationship!r}")
        if not isinstance(workspace.get("existing_work_reconciled"), bool):
            errors.append("workspace.existing_work_reconciled must be boolean")
        for key in ("staged_paths", "unstaged_paths", "untracked_paths"):
            require_string_list(workspace.get(key), f"workspace.{key}", errors)
        validate_refs(
            workspace.get("baseline_evidence_ids"),
            "workspace.baseline_evidence_ids",
            evidence_map,
            errors,
            nonempty_list=True,
        )
        if relationship == "artifact-only-descendant" and workspace.get("endpoint_kind") != "immutable-revision":
            errors.append("artifact-only-descendant requires an immutable product endpoint")
    return mode, {}


def validate_decisions(
    items: Any,
    teardown_by_id: dict[str, dict[str, Any]],
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], Counter[str]]:
    if not isinstance(items, list):
        errors.append("decisions must be a list")
        return {}, Counter()
    seen: set[str] = set()
    result: dict[str, dict[str, Any]] = {}
    coverage: Counter[str] = Counter()
    for index, item in enumerate(items, start=1):
        label = f"decisions[{index}]"
        exact_keys(item, DECISION_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        did = unique_id(item.get("id"), "decision", seen, label, errors)
        if did is None:
            continue
        result[did] = item
        finding_ids = require_string_list(item.get("finding_ids"), f"{did}.finding_ids", errors, nonempty_list=True)
        for fid in finding_ids:
            if fid not in teardown_by_id:
                errors.append(f"{did} references unknown finding: {fid}")
            else:
                coverage[fid] += 1
        status = item.get("status")
        if status not in DECISION_STATUSES:
            errors.append(f"{did} has invalid status: {status!r}")
        for key in ("question", "recommendation", "safe_default", "reversibility"):
            require_text(item.get(key), f"{did}.{key}", errors)
        for key in ("consequences", "prerequisites"):
            require_string_list(item.get(key), f"{did}.{key}", errors, nonempty_list=True, placeholders=True)
        selection = item.get("owner_selection")
        if status == "resolved":
            require_text(selection, f"{did}.owner_selection", errors)
        elif selection is not None:
            errors.append(f"{did}.owner_selection must be null unless status is resolved")
        options = item.get("options")
        if not isinstance(options, list) or len(options) < 2:
            errors.append(f"{did}.options must contain at least two concrete options")
            options = []
        option_ids: set[str] = set()
        for option_index, option in enumerate(options, start=1):
            olabel = f"{did}.options[{option_index}]"
            exact_keys(option, OPTION_KEYS, olabel, errors)
            if not isinstance(option, dict):
                continue
            oid = option.get("id")
            require_text(oid, f"{olabel}.id", errors)
            if isinstance(oid, str):
                if oid in option_ids:
                    errors.append(f"{did} repeats option id: {oid}")
                option_ids.add(oid)
            require_text(option.get("label"), f"{olabel}.label", errors)
            require_text(option.get("reversibility"), f"{olabel}.reversibility", errors)
            require_string_list(option.get("consequences"), f"{olabel}.consequences", errors, nonempty_list=True)
            require_string_list(option.get("prerequisites"), f"{olabel}.prerequisites", errors)
        if status == "resolved" and selection not in option_ids:
            errors.append(f"{did}.owner_selection must match an option id")
    return result, coverage


def validate_authority(
    items: Any,
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append("authority_matrix must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items, start=1):
        label = f"authority_matrix[{index}]"
        exact_keys(item, AUTHORITY_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        aid = item.get("id")
        if aid not in AUTHORITY_IDS:
            errors.append(f"{label} has invalid authority id: {aid!r}")
            continue
        if aid in result:
            errors.append(f"duplicate authority id: {aid}")
        result[aid] = item
        state = item.get("state")
        if state not in AUTHORITY_STATES:
            errors.append(f"{aid} has invalid authority state: {state!r}")
        require_text(item.get("scope"), f"{aid}.scope", errors)
        refs = validate_refs(item.get("evidence_ids"), f"{aid}.evidence_ids", evidence_map, errors)
        require_string_list(item.get("limitations"), f"{aid}.limitations", errors)
        if state == "authorized" and not refs:
            errors.append(f"{aid} authorized state requires evidence")
    missing = sorted(AUTHORITY_IDS - set(result))
    if missing:
        errors.append(f"authority matrix missing ids: {', '.join(missing)}")
    return result


def validate_findings(
    items: Any,
    teardown_by_id: dict[str, dict[str, Any]],
    evidence_map: dict[str, dict[str, Any]],
    mode: str | None,
    decision_coverage: Counter[str],
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], bool]:
    if not isinstance(items, list):
        errors.append("findings must be a list")
        return {}, True
    result: dict[str, dict[str, Any]] = {}
    sequences: dict[int, str] = {}
    approved_incomplete = False
    actual_dispositions = {"implemented", "already-satisfied", "preserved", "experiment-launched", "experiment-observing"}
    for index, item in enumerate(items, start=1):
        label = f"findings[{index}]"
        exact_keys(item, FINDING_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        fid = item.get("id")
        if not isinstance(fid, str) or fid not in teardown_by_id:
            errors.append(f"{label} references unknown finding: {fid!r}")
            continue
        if fid in result:
            errors.append(f"duplicate revision finding: {fid}")
            continue
        result[fid] = item
        source = teardown_by_id[fid]
        if item.get("title") != source.get("title"):
            errors.append(f"{fid} title does not match teardown")
        approval = item.get("approval")
        revalidation = item.get("revalidation")
        disposition = item.get("disposition")
        if approval not in APPROVALS:
            errors.append(f"{fid} has invalid approval: {approval!r}")
        if revalidation not in REVALIDATIONS:
            errors.append(f"{fid} has invalid revalidation: {revalidation!r}")
        if disposition not in DISPOSITIONS:
            errors.append(f"{fid} has invalid disposition: {disposition!r}")
        if approval in ALLOWED_DISPOSITIONS and disposition not in ALLOWED_DISPOSITIONS[approval]:
            errors.append(f"{fid} disposition {disposition!r} is incompatible with approval {approval!r}")
        if mode == "planning-only" and disposition in actual_dispositions:
            errors.append(f"{fid} planning-only mode cannot claim actual disposition {disposition!r}")
        if disposition == "implemented" and revalidation in {"stale", "not-applicable", "blocked"}:
            errors.append(f"{fid} cannot be implemented with revalidation {revalidation!r}")
        if disposition == "already-satisfied" and revalidation != "already-resolved":
            errors.append(f"{fid} already-satisfied requires already-resolved revalidation")
        if mode == "implementation" and source.get("kind") == "strength" and approval == "approved" and disposition != "preserved":
            errors.append(f"{fid} approved strength must be preserved")
        require_text(item.get("reason"), f"{fid}.reason", errors)

        sequence = item.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            errors.append(f"{fid}.sequence must be a positive integer")
        elif sequence in sequences:
            errors.append(f"duplicate finding sequence {sequence}: {sequences[sequence]} and {fid}")
        else:
            sequences[sequence] = fid

        deps = require_string_list(item.get("dependencies"), f"{fid}.dependencies", errors)
        if Counter(deps) != Counter(source.get("dependencies", [])):
            errors.append(f"{fid}.dependencies do not exactly match teardown")
        for key in ("completion_gates", "notes"):
            require_string_list(item.get(key), f"{fid}.{key}", errors, placeholders=True)
        validate_refs(item.get("evidence_ids"), f"{fid}.evidence_ids", evidence_map, errors)
        require_string_list(item.get("change_ids"), f"{fid}.change_ids", errors)
        require_string_list(item.get("experiment_ids"), f"{fid}.experiment_ids", errors)

        results = item.get("acceptance_results")
        if not isinstance(results, list):
            errors.append(f"{fid}.acceptance_results must be a list")
            results = []
        source_criteria = source.get("acceptance_criteria", [])
        seen_criteria: list[str] = []
        for result_index, acceptance in enumerate(results, start=1):
            alabel = f"{fid}.acceptance_results[{result_index}]"
            exact_keys(acceptance, ACCEPTANCE_KEYS, alabel, errors)
            if not isinstance(acceptance, dict):
                continue
            criterion = acceptance.get("criterion")
            require_text(criterion, f"{alabel}.criterion", errors, allow_placeholder=True)
            if isinstance(criterion, str):
                seen_criteria.append(criterion)
            status = acceptance.get("status")
            if status not in ACCEPTANCE_STATUSES:
                errors.append(f"{alabel} has invalid status: {status!r}")
            validate_refs(
                acceptance.get("evidence_ids"),
                f"{alabel}.evidence_ids",
                evidence_map,
                errors,
                completed=status == "passed",
            )
            require_text(acceptance.get("observation"), f"{alabel}.observation", errors)
            if approval == "approved" and status in {"pending", "failed", "blocked"}:
                approved_incomplete = True
        if Counter(seen_criteria) != Counter(source_criteria):
            errors.append(f"{fid}.acceptance_results must account for every teardown criterion exactly once")
        if approval == "approved" and not results:
            errors.append(f"{fid} approved finding requires acceptance results")
        if disposition == "implemented" and not item.get("change_ids"):
            errors.append(f"{fid} implemented disposition requires a mapped change")
        if disposition in {"experiment-planned", "experiment-launched", "experiment-observing"} and not item.get("experiment_ids"):
            errors.append(f"{fid} experiment disposition requires an experiment")
        if approval == "approved" and disposition == "blocked":
            approved_incomplete = True

        decision_required = (
            source.get("status") in {"decision_required", "blocked"}
            or revalidation == "changed"
            or approval == "accepted-risk"
            or bool(source.get("implementation_scope", {}).get("owner_or_external_actions"))
        )
        if decision_required and decision_coverage[fid] == 0:
            errors.append(f"{fid} requires an owner decision record")

    missing = sorted(set(teardown_by_id) - set(result))
    extra = sorted(set(result) - set(teardown_by_id))
    if missing:
        errors.append(f"revision missing teardown findings: {', '.join(missing)}")
    if extra:
        errors.append(f"revision has unknown findings: {', '.join(extra)}")
    if set(sequences) != set(range(1, len(result) + 1)):
        errors.append("finding sequences must be contiguous from 1 through finding count")
    for fid, item in result.items():
        seq = item.get("sequence")
        for dep in item.get("dependencies", []):
            dep_item = result.get(dep)
            if dep_item and isinstance(seq, int) and isinstance(dep_item.get("sequence"), int):
                if dep_item["sequence"] >= seq:
                    errors.append(f"{fid} sequence must follow dependency {dep}")
    return result, approved_incomplete


def validate_trace(
    trace: Any,
    coverage: dict[str, Any],
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    exact_keys(trace, TRACE_KEYS, "coverage_trace", errors)
    if not isinstance(trace, dict):
        return

    source_access = {
        item.get("category"): item
        for item in coverage.get("access", [])
        if isinstance(item, dict)
    }
    access_items = trace.get("access")
    seen_access: dict[str, dict[str, Any]] = {}
    if not isinstance(access_items, list):
        errors.append("coverage_trace.access must be a list")
        access_items = []
    for index, item in enumerate(access_items, start=1):
        label = f"coverage_trace.access[{index}]"
        exact_keys(item, ACCESS_TRACE_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        category = item.get("category")
        if category in seen_access:
            errors.append(f"coverage_trace repeats access category: {category}")
        seen_access[category] = item
        source = source_access.get(category)
        if source is None:
            errors.append(f"coverage_trace has unknown access category: {category}")
        elif item.get("source_status") != source.get("status"):
            errors.append(f"coverage_trace access {category} source_status does not match teardown")
        if item.get("disposition") not in ACCESS_DISPOSITIONS:
            errors.append(f"coverage_trace access {category} has invalid disposition")
        require_text(item.get("completion_gate"), f"coverage_trace access {category} completion_gate", errors)
        validate_refs(item.get("evidence_ids"), f"coverage_trace access {category} evidence_ids", evidence_map, errors)
    if set(seen_access) != set(source_access):
        errors.append("coverage_trace.access must account for every teardown access row exactly once")

    source_checks: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(coverage.get("surface_checks", []), start=1):
        if not isinstance(item, dict):
            continue
        cid = item.get("id")
        if not nonempty(cid):
            errors.append(f"teardown coverage surface_checks[{index}].id must be non-empty text")
            continue
        source_checks[cid] = item
    check_items = trace.get("surface_checks")
    seen_checks: dict[str, dict[str, Any]] = {}
    if not isinstance(check_items, list):
        errors.append("coverage_trace.surface_checks must be a list")
        check_items = []
    for index, item in enumerate(check_items, start=1):
        label = f"coverage_trace.surface_checks[{index}]"
        exact_keys(item, CHECK_TRACE_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        cid = item.get("id")
        if not nonempty(cid):
            errors.append(f"{label}.id must be non-empty text")
            continue
        if cid in seen_checks:
            errors.append(f"coverage_trace repeats surface check: {cid}")
        seen_checks[cid] = item
        source = source_checks.get(cid)
        if source is None:
            errors.append(f"coverage_trace has unknown surface check: {cid}")
        elif item.get("source_status") != source.get("status"):
            errors.append(f"coverage_trace check {cid} source_status does not match teardown")
        if item.get("disposition") not in CHECK_DISPOSITIONS:
            errors.append(f"coverage_trace check {cid} has invalid disposition")
        require_text(item.get("completion_gate"), f"coverage_trace check {cid} completion_gate", errors)
        validate_refs(item.get("evidence_ids"), f"coverage_trace check {cid} evidence_ids", evidence_map, errors)
    if set(seen_checks) != set(source_checks):
        errors.append("coverage_trace.surface_checks must account for every teardown check exactly once")

    source_limits: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(coverage.get("material_limitations", []), start=1):
        if not isinstance(item, dict):
            continue
        lid = item.get("id")
        if not nonempty(lid):
            errors.append(f"teardown coverage material_limitations[{index}].id must be non-empty text")
            continue
        source_limits[lid] = item
    limit_items = trace.get("material_limitations")
    seen_limits: dict[str, dict[str, Any]] = {}
    if not isinstance(limit_items, list):
        errors.append("coverage_trace.material_limitations must be a list")
        limit_items = []
    for index, item in enumerate(limit_items, start=1):
        label = f"coverage_trace.material_limitations[{index}]"
        exact_keys(item, LIMIT_TRACE_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        lid = item.get("id")
        if not nonempty(lid):
            errors.append(f"{label}.id must be non-empty text")
            continue
        if lid in seen_limits:
            errors.append(f"coverage_trace repeats material limitation: {lid}")
        seen_limits[lid] = item
        source = source_limits.get(lid)
        if source is None:
            errors.append(f"coverage_trace has unknown material limitation: {lid}")
        elif item.get("source_status") != source.get("status"):
            errors.append(f"coverage_trace limitation {lid} source_status does not match teardown")
        if item.get("disposition") not in LIMIT_DISPOSITIONS:
            errors.append(f"coverage_trace limitation {lid} has invalid disposition")
        require_text(item.get("completion_gate"), f"coverage_trace limitation {lid} completion_gate", errors)
        validate_refs(item.get("evidence_ids"), f"coverage_trace limitation {lid} evidence_ids", evidence_map, errors)
    if set(seen_limits) != set(source_limits):
        errors.append("coverage_trace.material_limitations must account for every teardown limitation exactly once")

    source_non = coverage.get("deliberate_non_pursuits", [])
    source_pairs: Counter[tuple[str, str]] = Counter()
    for index, item in enumerate(source_non, start=1):
        if not isinstance(item, dict):
            continue
        topic = item.get("topic")
        rationale = item.get("rationale")
        label = f"teardown coverage deliberate_non_pursuits[{index}]"
        if not nonempty(topic):
            errors.append(f"{label}.topic must be non-empty text")
        if not nonempty(rationale):
            errors.append(f"{label}.rationale must be non-empty text")
        if nonempty(topic) and nonempty(rationale):
            source_pairs[(topic, rationale)] += 1
    non_items = trace.get("deliberate_non_pursuits")
    if not isinstance(non_items, list):
        errors.append("coverage_trace.deliberate_non_pursuits must be a list")
        non_items = []
    actual_pairs: Counter[tuple[str, str]] = Counter()
    for index, item in enumerate(non_items, start=1):
        label = f"coverage_trace.deliberate_non_pursuits[{index}]"
        exact_keys(item, NON_PURSUIT_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        topic = item.get("topic")
        rationale = item.get("rationale")
        require_text(topic, f"{label}.topic", errors)
        require_text(rationale, f"{label}.rationale", errors)
        if nonempty(topic) and nonempty(rationale):
            actual_pairs[(topic, rationale)] += 1
        require_text(item.get("preservation_rule"), f"{label}.preservation_rule", errors)
        validate_refs(item.get("evidence_ids"), f"{label}.evidence_ids", evidence_map, errors)
    if actual_pairs != source_pairs:
        errors.append("coverage_trace.deliberate_non_pursuits must preserve teardown topics and rationales exactly")


def validate_changes(
    items: Any,
    findings: dict[str, dict[str, Any]],
    authority: dict[str, dict[str, Any]],
    evidence_map: dict[str, dict[str, Any]],
    mode: str | None,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append("changes must be a list")
        return {}
    seen: set[str] = set()
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items, start=1):
        label = f"changes[{index}]"
        exact_keys(item, CHANGE_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        cid = unique_id(item.get("id"), "change", seen, label, errors)
        if cid is None:
            continue
        result[cid] = item
        if mode == "planning-only":
            errors.append(f"{cid} planning-only mode cannot contain actual change records")
        if item.get("scope") not in CHANGE_SCOPES:
            errors.append(f"{cid} has invalid scope: {item.get('scope')!r}")
        finding_ids = require_string_list(item.get("finding_ids"), f"{cid}.finding_ids", errors)
        convergence_ids = require_string_list(item.get("convergence_ids"), f"{cid}.convergence_ids", errors)
        if not finding_ids and not convergence_ids:
            errors.append(f"{cid} must map to a finding or convergence finding")
        for fid in finding_ids:
            finding = findings.get(fid)
            if finding is None:
                errors.append(f"{cid} references unknown finding: {fid}")
            elif finding.get("approval") != "approved":
                errors.append(f"{cid} maps to non-approved finding: {fid}")
            elif cid not in finding.get("change_ids", []):
                errors.append(f"{cid} is not reciprocally listed by finding {fid}")
        require_string_list(item.get("targets"), f"{cid}.targets", errors, nonempty_list=True, placeholders=True)
        require_text(item.get("description"), f"{cid}.description", errors)
        authority_ids = require_string_list(item.get("external_authority_ids"), f"{cid}.external_authority_ids", errors)
        for aid in authority_ids:
            if aid not in AUTHORITY_IDS:
                errors.append(f"{cid} references unknown authority: {aid}")
        risk = item.get("risk_level")
        if risk not in RISK_LEVELS:
            errors.append(f"{cid} has invalid risk_level: {risk!r}")
        categories = require_string_list(item.get("risk_categories"), f"{cid}.risk_categories", errors)
        for category in categories:
            if category not in RISK_CATEGORIES:
                errors.append(f"{cid} has invalid risk category: {category}")
        rollout_id = item.get("rollout_id")
        if rollout_id is not None and (not isinstance(rollout_id, str) or not ID_PATTERNS["rollout"].fullmatch(rollout_id)):
            errors.append(f"{cid}.rollout_id must be ROLLOUT-### or null")
        refs = validate_refs(
            item.get("evidence_ids"),
            f"{cid}.evidence_ids",
            evidence_map,
            errors,
            nonempty_list=True,
            completed=True,
        )
        required_authority = CHANGE_SCOPE_AUTHORITY.get(item.get("scope"))
        if required_authority is not None:
            if required_authority not in authority_ids:
                errors.append(f"{cid} {item.get('scope')} change must list authority {required_authority}")
            if authority.get(required_authority, {}).get("state") != "authorized":
                errors.append(f"{cid} change lacks authorized authority {required_authority}")
        for fid in finding_ids:
            if findings.get(fid, {}).get("disposition") not in {
                "implemented",
                "experiment-launched",
                "experiment-observing",
            }:
                errors.append(f"{cid} maps to finding {fid} without an executed disposition")
        if risk == "high" and rollout_id is None:
            errors.append(f"{cid} high-risk change requires a rollout")
        if risk == "high" and not categories:
            errors.append(f"{cid} high-risk change requires at least one risk category")
        if item.get("scope") == "external-system":
            if not authority_ids:
                errors.append(f"{cid} external-system change requires explicit authority ids")
            for aid in authority_ids:
                if authority.get(aid, {}).get("state") != "authorized":
                    errors.append(f"{cid} external-system change lacks authorized authority {aid}")
            if not any(
                evidence_map.get(ref, {}).get("status") == "completed"
                and evidence_map.get(ref, {}).get("level") in {"deployed-production", "search-platform-observation"}
                for ref in refs
            ):
                errors.append(f"{cid} external-system change requires completed external-state evidence")
    return result


def validate_urls(
    items: Any,
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    if not isinstance(items, list):
        errors.append("url_verifications must be a list")
        return {}, set()
    seen: set[str] = set()
    result: dict[str, dict[str, Any]] = {}
    observed_dimensions: set[str] = set()
    for index, item in enumerate(items, start=1):
        label = f"url_verifications[{index}]"
        exact_keys(item, URL_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        uid = unique_id(item.get("id"), "url", seen, label, errors)
        if uid is None:
            continue
        result[uid] = item
        require_text(item.get("url"), f"{uid}.url", errors)
        environment = item.get("environment")
        if environment not in URL_ENVIRONMENTS:
            errors.append(f"{uid} has invalid environment: {environment!r}")
        require_string_list(item.get("limitations"), f"{uid}.limitations", errors)

        methods = item.get("method_evidence")
        method_map: dict[str, dict[str, Any]] = {}
        if not isinstance(methods, list) or not methods:
            errors.append(f"{uid}.method_evidence must be a non-empty list")
            methods = []
        method_evidence_ids: set[str] = set()
        for method_index, method in enumerate(methods, start=1):
            mlabel = f"{uid}.method_evidence[{method_index}]"
            exact_keys(method, METHOD_KEYS, mlabel, errors)
            if not isinstance(method, dict):
                continue
            name = method.get("method")
            if name not in EVIDENCE_METHODS:
                errors.append(f"{mlabel} has invalid method: {name!r}")
                continue
            if name in method_map:
                errors.append(f"{uid} repeats method evidence for {name}")
            method_map[name] = method
            status = method.get("status")
            if status not in EVIDENCE_STATUSES:
                errors.append(f"{mlabel} has invalid status: {status!r}")
            require_text(method.get("observation"), f"{mlabel}.observation", errors)
            refs = validate_refs(
                method.get("evidence_ids"),
                f"{mlabel}.evidence_ids",
                evidence_map,
                errors,
                nonempty_list=status != "not-applicable",
                completed=status == "completed",
            )
            method_evidence_ids.update(refs)
            limitations = require_string_list(method.get("limitations"), f"{mlabel}.limitations", errors)
            if status in {"failed", "blocked"} and not limitations:
                errors.append(f"{mlabel} {status} method requires limitations")

        observations = item.get("observations")
        if not isinstance(observations, list) or not observations:
            errors.append(f"{uid}.observations must be a non-empty list")
            observations = []
        seen_dimensions: set[str] = set()
        observation_evidence_ids: set[str] = set()
        for obs_index, observation in enumerate(observations, start=1):
            olabel = f"{uid}.observations[{obs_index}]"
            exact_keys(observation, OBSERVATION_KEYS, olabel, errors)
            if not isinstance(observation, dict):
                continue
            dimension = observation.get("dimension")
            if dimension not in OBSERVATION_DIMENSIONS:
                errors.append(f"{olabel} has invalid dimension: {dimension!r}")
                continue
            if dimension in seen_dimensions:
                errors.append(f"{uid} repeats observation dimension: {dimension}")
            seen_dimensions.add(dimension)
            status = observation.get("status")
            if status not in OBSERVATION_STATUSES:
                errors.append(f"{olabel} has invalid status: {status!r}")
            method_names = require_string_list(observation.get("supported_by_methods"), f"{olabel}.supported_by_methods", errors)
            refs = validate_refs(
                observation.get("evidence_ids"),
                f"{olabel}.evidence_ids",
                evidence_map,
                errors,
                nonempty_list=status != "not-applicable",
                completed=status == "observed",
            )
            observation_evidence_ids.update(refs)
            limitations = require_string_list(observation.get("limitations"), f"{olabel}.limitations", errors)
            value = observation.get("value")
            if status == "observed":
                observed_dimensions.add(dimension)
                if environment == "production":
                    observed_dimensions.add(f"production:{dimension}")
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"{olabel} observed state requires a value")
                if not method_names:
                    errors.append(f"{olabel} observed state requires supporting methods")
                for method_name in method_names:
                    method = method_map.get(method_name)
                    if method is None:
                        errors.append(f"{olabel} references undeclared method: {method_name}")
                    elif method.get("status") != "completed":
                        errors.append(f"{olabel} cannot be supported by non-completed method {method_name}")
                levels = {evidence_map.get(ref, {}).get("level") for ref in refs}
                if dimension == "http":
                    if not set(method_names).intersection({"live-fetch", "controlled-test"}):
                        errors.append(f"{olabel} requires completed live-fetch or controlled-test")
                    if environment == "production" and "deployed-production" not in levels:
                        errors.append(f"{olabel} production HTTP observation requires deployed-production evidence")
                elif dimension == "canonical":
                    if not set(method_names).intersection({"live-fetch", "rendered-browser", "controlled-test"}):
                        errors.append(f"{olabel} requires live, rendered, or controlled evidence")
                elif dimension == "render" and "rendered-browser" not in method_names:
                    errors.append(f"{olabel} requires rendered-browser evidence")
                elif dimension == "eligibility":
                    if not set(method_names).intersection(
                        {"source-inspection", "local-crawl", "rendered-browser", "live-fetch", "controlled-test"}
                    ):
                        errors.append(f"{olabel} requires a completed source, render, or live method")
                elif dimension in {"index", "visibility", "ai-citation"}:
                    if not set(method_names).intersection({"serp-observation", "platform-data"}):
                        errors.append(f"{olabel} requires SERP or platform data")
                    if "search-platform-observation" not in levels:
                        errors.append(f"{olabel} requires search-platform-observation evidence")
                elif dimension == "conversion":
                    if not levels.intersection({"deployed-production", "business-outcome"}):
                        errors.append(f"{olabel} conversion observation requires deployed or business evidence")
                elif dimension == "business-outcome":
                    if "first-party-analysis" not in method_names or "business-outcome" not in levels:
                        errors.append(f"{olabel} requires first-party business-outcome evidence")
            elif status in {"unavailable", "not-applicable"}:
                if value is not None:
                    errors.append(f"{olabel} {status} state must use null value")
                if status == "unavailable" and not limitations:
                    errors.append(f"{olabel} unavailable state requires limitations")
                if status == "not-applicable" and method_names:
                    errors.append(f"{olabel} not-applicable state cannot claim supporting methods")

        top_refs = validate_refs(item.get("evidence_ids"), f"{uid}.evidence_ids", evidence_map, errors)
        if set(top_refs) != method_evidence_ids | observation_evidence_ids:
            errors.append(f"{uid}.evidence_ids must exactly reconcile method and observation evidence")
    return result, observed_dimensions


def validate_experiments(
    items: Any,
    findings: dict[str, dict[str, Any]],
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append("experiments must be a list")
        return {}
    seen: set[str] = set()
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items, start=1):
        label = f"experiments[{index}]"
        exact_keys(item, EXPERIMENT_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        eid = unique_id(item.get("id"), "experiment", seen, label, errors)
        if eid is None:
            continue
        result[eid] = item
        finding_ids = require_string_list(item.get("finding_ids"), f"{eid}.finding_ids", errors, nonempty_list=True)
        for fid in finding_ids:
            finding = findings.get(fid)
            if finding is None:
                errors.append(f"{eid} references unknown finding: {fid}")
            elif eid not in finding.get("experiment_ids", []):
                errors.append(f"{eid} is not reciprocally listed by finding {fid}")
        status = item.get("status")
        if status not in EXPERIMENT_STATUSES:
            errors.append(f"{eid} has invalid status: {status!r}")
        for key in (
            "hypothesis",
            "evidence_basis",
            "segment",
            "baseline",
            "primary_metric",
            "sample_requirement",
            "expected_time_to_evidence",
            "stop_rollback_criteria",
            "decision_rule",
            "observation_owner",
            "next_review_at",
        ):
            require_text(item.get(key), f"{eid}.{key}", errors)
        for key in ("affected_pages_queries", "guardrails", "confounders"):
            require_string_list(item.get(key), f"{eid}.{key}", errors, nonempty_list=True, placeholders=True)
        refs = validate_refs(item.get("evidence_ids"), f"{eid}.evidence_ids", evidence_map, errors)
        if status in {"validated", "rejected"}:
            valid_refs = [
                ref
                for ref in refs
                if evidence_map.get(ref, {}).get("status") == "completed"
                and evidence_map.get(ref, {}).get("level") in {"search-platform-observation", "business-outcome"}
            ]
            if not valid_refs:
                errors.append(f"{eid} {status} experiment requires completed outcome observation evidence")
    return result


def validate_convergence(
    items: Any,
    findings: dict[str, dict[str, Any]],
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], int]:
    if not isinstance(items, list):
        errors.append("convergence_findings must be a list")
        return {}, 0
    seen: set[str] = set()
    result: dict[str, dict[str, Any]] = {}
    blocking = 0
    for index, item in enumerate(items, start=1):
        label = f"convergence_findings[{index}]"
        exact_keys(item, CONVERGENCE_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        rid = unique_id(item.get("id"), "convergence", seen, label, errors)
        if rid is None:
            continue
        result[rid] = item
        for key in ("title", "source", "reason"):
            require_text(item.get(key), f"{rid}.{key}", errors)
        severity = item.get("severity")
        status = item.get("status")
        if severity not in CONVERGENCE_SEVERITIES:
            errors.append(f"{rid} has invalid severity: {severity!r}")
        if status not in CONVERGENCE_STATUSES:
            errors.append(f"{rid} has invalid status: {status!r}")
        reopened = require_string_list(item.get("reopened_finding_ids"), f"{rid}.reopened_finding_ids", errors)
        for fid in reopened:
            if fid not in findings:
                errors.append(f"{rid} reopens unknown finding: {fid}")
        change_ids = require_string_list(item.get("change_ids"), f"{rid}.change_ids", errors)
        refs = validate_refs(item.get("evidence_ids"), f"{rid}.evidence_ids", evidence_map, errors)
        if status == "fixed":
            if not change_ids:
                errors.append(f"{rid} fixed status requires a mapped change")
            if not any(evidence_map.get(ref, {}).get("status") == "completed" for ref in refs):
                errors.append(f"{rid} fixed status requires completed verification evidence")
        if severity in {"critical", "high", "medium"} and status in {"open", "deferred", "blocked"}:
            blocking += 1
    return result, blocking


def validate_rollouts(
    items: Any,
    changes: dict[str, dict[str, Any]],
    evidence_map: dict[str, dict[str, Any]],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append("rollouts must be a list")
        return {}
    seen: set[str] = set()
    result: dict[str, dict[str, Any]] = {}
    change_membership: Counter[str] = Counter()
    for index, item in enumerate(items, start=1):
        label = f"rollouts[{index}]"
        exact_keys(item, ROLLOUT_KEYS, label, errors)
        if not isinstance(item, dict):
            continue
        rid = unique_id(item.get("id"), "rollout", seen, label, errors)
        if rid is None:
            continue
        result[rid] = item
        change_ids = require_string_list(item.get("change_ids"), f"{rid}.change_ids", errors, nonempty_list=True)
        for cid in change_ids:
            change = changes.get(cid)
            if change is None:
                errors.append(f"{rid} references unknown change: {cid}")
            else:
                change_membership[cid] += 1
                if change.get("rollout_id") != rid:
                    errors.append(f"{rid} does not match {cid}.rollout_id")
        state = item.get("state")
        if state not in ROLLOUT_STATES:
            errors.append(f"{rid} has invalid rollout state: {state!r}")
        for key in ("inventory", "representative_samples", "collision_checks"):
            require_string_list(item.get(key), f"{rid}.{key}", errors, nonempty_list=True, placeholders=True)
        require_text(item.get("rollback_plan"), f"{rid}.rollback_plan", errors)
        refs = validate_refs(item.get("evidence_ids"), f"{rid}.evidence_ids", evidence_map, errors)
        if state in {"activated", "verified"}:
            if not any(
                evidence_map.get(ref, {}).get("status") == "completed"
                and evidence_map.get(ref, {}).get("level") in {"deployed-production", "search-platform-observation"}
                for ref in refs
            ):
                errors.append(f"{rid} {state} rollout requires completed deployed or platform evidence")
    for cid, change in changes.items():
        rollout_id = change.get("rollout_id")
        if rollout_id is not None and rollout_id not in result:
            errors.append(f"{cid} references unknown rollout: {rollout_id}")
        if change.get("risk_level") == "high":
            if change_membership[cid] != 1:
                errors.append(f"{cid} high-risk change must appear in exactly one rollout")
            elif result.get(rollout_id, {}).get("state") == "not-required":
                errors.append(f"{cid} high-risk change cannot use not-required rollout")
    return result


def validate_cross_links(
    findings: dict[str, dict[str, Any]],
    changes: dict[str, dict[str, Any]],
    experiments: dict[str, dict[str, Any]],
    convergence: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    for fid, finding in findings.items():
        for cid in finding.get("change_ids", []):
            if cid not in changes:
                errors.append(f"{fid} references unknown change: {cid}")
            elif fid not in changes[cid].get("finding_ids", []):
                errors.append(f"{fid} change reference is not reciprocal: {cid}")
        for eid in finding.get("experiment_ids", []):
            if eid not in experiments:
                errors.append(f"{fid} references unknown experiment: {eid}")
            elif fid not in experiments[eid].get("finding_ids", []):
                errors.append(f"{fid} experiment reference is not reciprocal: {eid}")
    for cid, change in changes.items():
        for rid in change.get("convergence_ids", []):
            if rid not in convergence:
                errors.append(f"{cid} references unknown convergence finding: {rid}")
            elif cid not in convergence[rid].get("change_ids", []):
                errors.append(f"{cid} convergence reference is not reciprocal: {rid}")
    for rid, item in convergence.items():
        for cid in item.get("change_ids", []):
            if cid not in changes:
                errors.append(f"{rid} references unknown change: {cid}")
            elif rid not in changes[cid].get("convergence_ids", []):
                errors.append(f"{rid} change reference is not reciprocal: {cid}")


def validate_readiness(
    readiness: Any,
    mode: str | None,
    workspace: dict[str, Any],
    authority: dict[str, dict[str, Any]],
    evidence_map: dict[str, dict[str, Any]],
    changes: dict[str, dict[str, Any]],
    convergence: dict[str, dict[str, Any]],
    convergence_blocking: int,
    rollouts: dict[str, dict[str, Any]],
    experiments: dict[str, dict[str, Any]],
    approved_incomplete: bool,
    observed_dimensions: set[str],
    errors: list[str],
) -> None:
    exact_keys(readiness, READINESS_KEYS, "readiness", errors)
    if not isinstance(readiness, dict):
        return
    revision_status = readiness.get("revision_status")
    review = readiness.get("review_convergence")
    integration = readiness.get("integration")
    deployment = readiness.get("deployment")
    publication = readiness.get("publication")
    search = readiness.get("search_validation")
    experiment_status = readiness.get("experiment_status")
    auth_summary = readiness.get("authorization_summary")
    if revision_status not in REVISION_STATUSES:
        errors.append(f"readiness.revision_status has invalid value: {revision_status!r}")
    if review not in REVIEW_CONVERGENCE:
        errors.append(f"readiness.review_convergence has invalid value: {review!r}")
    for key, value in (("integration", integration), ("deployment", deployment), ("publication", publication)):
        if value not in READY_STATES:
            errors.append(f"readiness.{key} has invalid value: {value!r}")
    if search not in SEARCH_VALIDATION:
        errors.append(f"readiness.search_validation has invalid value: {search!r}")
    if experiment_status not in EXPERIMENT_SUMMARY:
        errors.append(f"readiness.experiment_status has invalid value: {experiment_status!r}")
    if auth_summary not in AUTHORIZATION_SUMMARY:
        errors.append(f"readiness.authorization_summary has invalid value: {auth_summary!r}")
    convergence_refs = validate_refs(
        readiness.get("convergence_evidence_ids"),
        "readiness.convergence_evidence_ids",
        evidence_map,
        errors,
        completed=review == "passed",
    )
    require_string_list(readiness.get("unverified_outcomes"), "readiness.unverified_outcomes", errors, placeholders=True)
    require_string_list(readiness.get("follow_up_actions"), "readiness.follow_up_actions", errors, placeholders=True)

    delivery = readiness.get("delivery")
    exact_keys(delivery, DELIVERY_KEYS, "readiness.delivery", errors)
    delivery_states: dict[str, str] = {}
    if isinstance(delivery, dict):
        for action in DELIVERY_KEYS:
            item = delivery.get(action)
            exact_keys(item, DELIVERY_ITEM_KEYS, f"readiness.delivery.{action}", errors)
            if not isinstance(item, dict):
                continue
            state = item.get("state")
            delivery_states[action] = state
            if state not in DELIVERY_STATES:
                errors.append(f"delivery {action} has invalid state: {state!r}")
            refs = validate_refs(
                item.get("evidence_ids"),
                f"delivery {action} evidence_ids",
                evidence_map,
                errors,
                nonempty_list=state == "verified",
                completed=state == "verified",
            )
            require_text(item.get("observation"), f"delivery {action} observation", errors)
            if state == "verified":
                aid = DELIVERY_AUTHORITY[action]
                if authority.get(aid, {}).get("state") != "authorized":
                    errors.append(f"verified delivery {action} lacks authorized authority {aid}")
                levels = {evidence_map.get(ref, {}).get("level") for ref in refs}
                if action in {"deployed", "published"} and "deployed-production" not in levels:
                    errors.append(f"verified delivery {action} requires deployed-production evidence")
                if action in {"search_platform_actions", "external_profile_actions"} and not levels.intersection(
                    {"search-platform-observation", "deployed-production"}
                ):
                    errors.append(f"verified delivery {action} requires external-state evidence")

    if delivery_states.get("pushed") == "verified" and delivery_states.get("committed") != "verified":
        errors.append("verified push requires verified commit")
    if delivery_states.get("merged") == "verified" and delivery_states.get("pushed") != "verified":
        errors.append("verified merge requires verified push")
    if workspace.get("artifact_relationship") == "artifact-only-descendant":
        if delivery_states.get("committed") != "verified":
            errors.append("artifact-only-descendant requires verified committed product endpoint")

    if mode == "planning-only":
        if revision_status != "planned":
            errors.append("planning-only mode requires planned revision status")
        if review != "not-run":
            errors.append("planning-only mode cannot claim convergence")
        if changes:
            errors.append("planning-only mode cannot contain changes")
        if convergence:
            errors.append("planning-only mode cannot contain convergence findings")
        if any(value == "ready" for value in (integration, deployment, publication)):
            errors.append("planning-only mode cannot claim ready integration, deployment, or publication")
        if any(state == "verified" for state in delivery_states.values()):
            errors.append("planning-only mode cannot claim verified delivery")
        if convergence_refs:
            errors.append("planning-only mode cannot claim convergence evidence")

    if review == "passed":
        if convergence_blocking:
            errors.append("review convergence cannot pass with blocking convergence findings")
        if not convergence_refs:
            errors.append("passed convergence requires completed convergence evidence")
    if integration == "ready":
        if review != "passed" or convergence_blocking:
            errors.append("integration readiness requires passed convergence and zero blocking findings")
        if workspace.get("existing_work_reconciled") is not True:
            errors.append("integration readiness requires existing work reconciliation")
        if approved_incomplete:
            errors.append("integration readiness cannot coexist with incomplete approved criteria")
    if deployment == "ready":
        if integration != "ready":
            errors.append("deployment readiness requires integration readiness")
        for change in changes.values():
            if change.get("risk_level") == "high":
                rollout = rollouts.get(change.get("rollout_id"), {})
                if rollout.get("state") not in {"staged", "activated", "verified"}:
                    errors.append("deployment readiness requires high-risk rollouts staged or stronger")
    if publication == "ready":
        if authority.get("publication", {}).get("state") != "authorized":
            errors.append("publication readiness requires publication authority")
        if integration != "ready":
            errors.append("publication readiness requires integration readiness")
    if revision_status == "complete":
        if approved_incomplete:
            errors.append("complete revision has incomplete approved work")
        if workspace.get("existing_work_reconciled") is not True:
            errors.append("complete revision requires existing work reconciliation")
        if review != "passed":
            errors.append("complete revision requires passed convergence")

    search_requirements = {
        "eligibility-verified": {"production:eligibility"},
        "index-observed": {"index"},
        "visibility-observed": {"visibility", "ai-citation"},
        "outcome-observed": {"business-outcome"},
    }
    required = search_requirements.get(search)
    if required and not observed_dimensions.intersection(required):
        errors.append(f"search validation {search} lacks required URL/search observation evidence")

    statuses = {item.get("status") for item in experiments.values()}
    if not experiments and experiment_status != "not-applicable":
        errors.append("experiment_status must be not-applicable when there are no experiments")
    if experiments and experiment_status != "mixed":
        normalized = {
            "planned": "planned",
            "launched": "launched",
            "observing": "observing",
            "validated": "validated",
            "rejected": "rejected",
            "blocked": "blocked",
        }
        if len(statuses) != 1 or normalized.get(next(iter(statuses), None)) != experiment_status:
            errors.append("readiness.experiment_status does not summarize experiment records")


def validate_generated(revision_root: Path, errors: list[str]) -> None:
    try:
        expected = rendered_files(revision_root)
    except Exception as exc:
        errors.append(f"cannot render canonical revision Markdown: {exc}")
        return
    for name, content in expected.items():
        path = revision_root / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            errors.append(f"{name} disagrees with revision.json; rerun render_revision.py")


def validate(
    teardown_root: Path,
    revision_root: Path,
    *,
    seo_teardown_skill: Path | None = None,
    run_upstream: bool = True,
) -> list[str]:
    errors: list[str] = []
    if not teardown_root.is_dir():
        return [f"teardown directory does not exist: {teardown_root}"]
    if not revision_root.is_dir():
        return [f"revision directory does not exist: {revision_root}"]
    if run_upstream:
        run_upstream_validator(teardown_root, seo_teardown_skill, errors)
    for name in ("findings.json", "coverage.json"):
        if not (teardown_root / name).is_file():
            errors.append(f"teardown is missing {name}")
    for name in REQUIRED_FILES:
        if not (revision_root / name).is_file():
            errors.append(f"revision is missing required file: {name}")
    if not (revision_root / "evidence").is_dir():
        errors.append("revision is missing evidence directory")
    if errors:
        return errors

    teardown_findings = load_object(teardown_root / "findings.json", "teardown findings.json", errors)
    teardown_coverage = load_object(teardown_root / "coverage.json", "teardown coverage.json", errors)
    data = load_object(revision_root / "revision.json", "revision.json", errors)
    if errors:
        return errors

    source_items = teardown_findings.get("findings")
    if not isinstance(source_items, list):
        errors.append("teardown findings must be a list")
        return errors
    teardown_by_id = {
        item.get("id"): item
        for item in source_items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if len(teardown_by_id) != len(source_items):
        errors.append("teardown findings contain invalid or duplicate IDs")
        return errors

    evidence_map = validate_evidence(data.get("evidence"), errors)
    mode, _ = validate_header(data, teardown_findings, teardown_coverage, evidence_map, errors)
    _, decision_coverage = validate_decisions(
        data.get("decisions"), teardown_by_id, evidence_map, errors
    )
    authority = validate_authority(data.get("authority_matrix"), evidence_map, errors)
    findings, approved_incomplete = validate_findings(
        data.get("findings"),
        teardown_by_id,
        evidence_map,
        mode,
        decision_coverage,
        errors,
    )
    validate_trace(data.get("coverage_trace"), teardown_coverage, evidence_map, errors)
    changes = validate_changes(
        data.get("changes"), findings, authority, evidence_map, mode, errors
    )
    _, observed_dimensions = validate_urls(
        data.get("url_verifications"), evidence_map, errors
    )
    experiments = validate_experiments(
        data.get("experiments"), findings, evidence_map, errors
    )
    convergence, convergence_blocking = validate_convergence(
        data.get("convergence_findings"), findings, evidence_map, errors
    )
    rollouts = validate_rollouts(data.get("rollouts"), changes, evidence_map, errors)
    validate_cross_links(findings, changes, experiments, convergence, errors)

    if mode == "implementation":
        for decision in data.get("decisions", []):
            if not isinstance(decision, dict) or decision.get("status") != "pending":
                continue
            if any(findings.get(fid, {}).get("approval") == "approved" for fid in decision.get("finding_ids", [])):
                errors.append(f"{decision.get('id')} pending decision blocks approved implementation")

    validate_readiness(
        data.get("readiness"),
        mode,
        data.get("workspace", {}) if isinstance(data.get("workspace"), dict) else {},
        authority,
        evidence_map,
        changes,
        convergence,
        convergence_blocking,
        rollouts,
        experiments,
        approved_incomplete,
        observed_dimensions,
        errors,
    )
    validate_generated(revision_root, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown", type=Path)
    parser.add_argument("revision", type=Path)
    parser.add_argument("--seo-teardown-skill", type=Path)
    args = parser.parse_args()
    errors = validate(
        args.teardown.resolve(),
        args.revision.resolve(),
        seo_teardown_skill=args.seo_teardown_skill.resolve()
        if args.seo_teardown_skill
        else None,
    )
    if errors:
        print(f"SEO revision validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SEO revision validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
