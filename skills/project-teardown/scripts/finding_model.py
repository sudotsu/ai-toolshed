#!/usr/bin/env python3
"""Shared finding schema constants and deterministic report rendering."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

FIELDS = (
    "type", "category", "severity", "confidence", "verification_state", "status",
    "impact", "evidence", "expected_behavior", "actual_behavior", "root_cause",
    "affected_components", "recommendation", "if_implemented", "if_unchanged",
    "dependencies", "dependents", "conflicts", "acceptance_criteria", "verification",
    "estimated_scope", "regression_risk", "action", "strategic_classification",
)

LEGACY_FIELDS = tuple(field for field in FIELDS if field != "verification_state")

MARKDOWN_LABELS = {
    "type": "Type",
    "category": "Category",
    "severity": "Severity",
    "confidence": "Confidence",
    "verification_state": "Verification state",
    "status": "Status",
    "impact": "Impact",
    "evidence": "Evidence",
    "expected_behavior": "Expected behavior",
    "actual_behavior": "Actual behavior",
    "root_cause": "Root cause",
    "affected_components": "Affected components",
    "recommendation": "Recommendation",
    "if_implemented": "If implemented",
    "if_unchanged": "If unchanged",
    "dependencies": "Dependencies",
    "dependents": "Dependents",
    "conflicts": "Conflicts",
    "acceptance_criteria": "Acceptance criteria",
    "verification": "Verification",
    "estimated_scope": "Estimated scope",
    "regression_risk": "Regression risk",
    "action": "Action",
    "strategic_classification": "Strategic classification",
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}


def canonical_finding_digest(finding: dict[str, Any]) -> str:
    payload = json.dumps(
        finding,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _render_evidence(items: list[dict[str, Any]]) -> str:
    if not items:
        return "None"
    rendered: list[str] = []
    for item in items:
        rendered.append(
            f"[{item.get('kind', '')}] {item.get('claim', '')} — "
            f"{item.get('source', '')} ({item.get('location', '')})"
        )
    return " ; ".join(rendered)


def _render_value(field: str, value: Any) -> str:
    if field == "evidence" and isinstance(value, list):
        return _render_evidence(value)
    if isinstance(value, list):
        return " | ".join(str(item) for item in value) if value else "None"
    return str(value)


def render_findings_register(payload: dict[str, Any]) -> str:
    schema_version = payload.get("schema_version")
    fields = FIELDS if schema_version == 3 else LEGACY_FIELDS
    findings = payload.get("findings")
    if not isinstance(findings, list):
        findings = []

    lines = [
        "# Findings Register",
        "",
        "<!-- Generated from findings.json by scripts/render_findings.py. Do not edit manually. -->",
        "",
    ]
    for finding in findings:
        finding_id = finding.get("id", "INVALID")
        title = finding.get("title", "Untitled finding")
        lines.extend([f"## {finding_id} — {title}", ""])
        for field in fields:
            lines.append(f"- **{MARKDOWN_LABELS[field]}:** {_render_value(field, finding.get(field))}")
        lines.append(f"- **JSON record digest:** {canonical_finding_digest(finding)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_readme(payload: dict[str, Any]) -> str:
    findings = payload.get("findings")
    if not isinstance(findings, list):
        findings = []
    status_counts = Counter(str(item.get("status", "unknown")) for item in findings if isinstance(item, dict))
    severity_counts = Counter(str(item.get("severity", "unknown")) for item in findings if isinstance(item, dict))
    top_findings = sorted(
        (item for item in findings if isinstance(item, dict) and item.get("type") != "strength"),
        key=lambda item: (SEVERITY_ORDER.get(str(item.get("severity")), 99), str(item.get("id", ""))),
    )[:5]

    core = payload.get("core_workflows_fully_exercised")
    core_text = "yes" if core is True else "no" if core is False else "not recorded"
    lines = [
        "# Project Teardown",
        "",
        "<!-- Generated from findings.json by scripts/render_readme.py. Do not edit generated metadata manually. -->",
        "",
        f"**Project:** {payload.get('project', '')}",
        f"**Audited revision:** {payload.get('audited_revision', '')}",
        f"**Review status:** {payload.get('review_status', '')}",
        f"**Core workflows fully exercised:** {core_text}",
        f"**Total findings:** {len(findings)}",
        f"**Generated at:** {payload.get('generated_at', '')}",
        "",
        "## Start here",
        "",
        "1. Read [00-executive-verdict.md](00-executive-verdict.md) for the overall judgment and completion limits.",
        "2. Read [05-findings-register.md](05-findings-register.md) for the generated human view of every finding.",
        "3. Read [06-implementation-sequence.md](06-implementation-sequence.md) for dependency-aware ordering.",
        "4. Read [07-review-coverage.md](07-review-coverage.md) for tested, partial, blocked, and unverified surfaces.",
        "5. Read [08-claims-inventory.md](08-claims-inventory.md) for credential, safety, guarantee, expertise, pricing, privacy, and capability claims.",
        "6. Use [findings.json](findings.json) as the canonical machine handoff for project-revision.",
        "",
        "## Highest-priority findings",
        "",
    ]
    if top_findings:
        for item in top_findings:
            lines.append(
                f"- **{item.get('id')} — {item.get('title')}** "
                f"({item.get('severity')}, {item.get('status')}, {item.get('verification_state', 'legacy')})"
            )
    else:
        lines.append("- None registered.")

    lines.extend(["", "## Finding summary", ""])
    for severity in ("critical", "high", "medium", "low", "informational"):
        lines.append(f"- {severity}: {severity_counts.get(severity, 0)}")
    lines.append("")
    for status in ("open", "blocked", "decision-required", "accepted-risk", "retained"):
        lines.append(f"- {status}: {status_counts.get(status, 0)}")
    lines.extend([
        "",
        "## Validation",
        "",
        "Run the project-report validator after generating the views:",
        "",
        "```bash",
        "python3 <skill-directory>/scripts/render_findings.py <project-teardown-directory>",
        "python3 <skill-directory>/scripts/render_readme.py <project-teardown-directory>",
        "python3 <skill-directory>/scripts/validate_teardown.py <project-teardown-directory>",
        "```",
        "",
        "Validator success proves structural and cross-file consistency, not that the audit was substantively complete.",
    ])
    return "\n".join(lines).rstrip() + "\n"
