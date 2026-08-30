#!/usr/bin/env python3
"""Deterministically render human-readable brand-revision views from revision.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validator_shape import _shape_revision

GENERATED_FILES = (
    "README.md",
    "00-decisions-authority-and-scope.md",
    "01-baseline-and-revalidation.md",
    "02-strategy-execution-and-rollout-plan.md",
    "03-implementation-ledger.md",
    "04-claims-and-preservation-ledger.md",
    "05-convergence-and-perception-verification.md",
    "06-readiness-and-handoff.md",
)


def _s(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple)):
        return ", ".join(_s(item) for item in value) if value else "—"
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    text = str(value).replace("\n", " ").strip()
    return text or "—"


def _esc(value: Any) -> str:
    return _s(value).replace("|", "\\|")


def _heading(title: str) -> str:
    return f"# {title}\n\n"


def _obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _rows(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _strings(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _ordered_findings(data: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        _rows(data.get("findings")),
        key=lambda item: item.get("sequence") if isinstance(item.get("sequence"), int) else 10**9,
    )


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(_esc(cell) for cell in row) + " |")
    if len(out) == 2:
        out.append("| " + " | ".join("—" for _ in headers) + " |")
    return "\n".join(out) + "\n\n"


def render_all(data: dict[str, Any]) -> dict[str, str]:
    data = _obj(data)
    project = _obj(data.get("project"))
    teardown = _obj(data.get("teardown"))
    workspace = _obj(data.get("workspace"))
    readiness = _obj(data.get("readiness"))

    readme = _heading("Brand Revision")
    readme += f"- **Project:** {_s(project.get('name'))}\n"
    readme += f"- **Project locator:** {_s(project.get('locator'))}\n"
    readme += f"- **Production locator:** {_s(project.get('production_locator'))}\n"
    readme += f"- **Mode:** {_s(data.get('mode'))}\n"
    readme += f"- **Generated at:** {_s(data.get('generated_at'))}\n"
    readme += f"- **Teardown review status:** {_s(teardown.get('review_status'))}\n"
    readme += f"- **Audited revision:** {_s(teardown.get('audited_revision'))}\n"
    readme += f"- **Revision status:** {_s(readiness.get('revision_status'))}\n"
    readme += "- **Canonical file:** `revision.json`\n\n"
    readme += "Generated views are deterministic. Regenerate with `python3 <skill-directory>/scripts/render_revision.py <brand-revision-directory>` and validate with `python3 <skill-directory>/scripts/validate_brand_revision.py <brand-teardown-directory> <brand-revision-directory>`.\n"

    decisions = _heading("Decisions, authority, and scope")
    decisions += "## Owner decisions\n\n"
    decisions += _table(
        ["ID", "Category", "Status", "Findings", "Question", "Owner selection", "Safe default"],
        [[d.get("id"), d.get("category"), d.get("status"), d.get("finding_ids"), d.get("question"), d.get("owner_selection"), d.get("safe_default")] for d in _rows(data.get("decisions"))],
    )
    decisions += "## Authority matrix\n\n"
    decisions += _table(
        ["Authority", "State", "Scope", "Limitations"],
        [[a.get("id"), a.get("state"), a.get("scope"), a.get("limitations")] for a in _rows(data.get("authority_matrix"))],
    )

    baseline = _heading("Baseline and revalidation")
    baseline += "## Workspace baseline\n\n"
    baseline += _table(
        ["Field", "Value"],
        [["Implementation start revision", workspace.get("implementation_start_revision")], ["Product endpoint", workspace.get("product_endpoint")], ["Endpoint kind", workspace.get("endpoint_kind")], ["Artifact relationship", workspace.get("artifact_relationship")], ["Existing work reconciled", workspace.get("existing_work_reconciled")], ["Staged paths", workspace.get("staged_paths")], ["Unstaged paths", workspace.get("unstaged_paths")], ["Untracked paths", workspace.get("untracked_paths")]],
    )
    baseline += "## Finding revalidation\n\n"
    baseline += _table(
        ["Seq", "Finding", "Source", "Approval", "Revalidation", "Disposition", "Preservation", "Dependencies", "Reason"],
        [[f.get("sequence"), f"{f.get('id')} — {f.get('title')}", f.get("source_status"), f.get("approval"), f.get("revalidation"), f.get("disposition"), f.get("preservation_status"), f.get("dependencies"), f.get("reason")] for f in _ordered_findings(data)],
    )
    baseline += "## Coverage trace\n\n"
    cov = _obj(data.get("coverage_trace"))
    for label, key, id_key in (("Access", "access", "category"), ("Modules", "modules", "id"), ("Surface checks", "surface_checks", "id"), ("Material limitations", "material_limitations", "id")):
        baseline += f"### {label}\n\n"
        baseline += _table(
            ["ID", "Source status", "Disposition", "Completion gate"],
            [[row.get(id_key), row.get("source_status"), row.get("disposition"), row.get("completion_gate")] for row in _rows(cov.get(key))],
        )

    plan = _heading("Strategy, execution, and rollout plan")
    plan += "## Dependency-ordered findings\n\n"
    for f in _ordered_findings(data):
        if not isinstance(f, dict):
            continue
        plan += f"### {f.get('sequence')}. {f.get('id')} — {f.get('title')}\n\n"
        plan += f"- Approval: {_s(f.get('approval'))}\n- Revalidation: {_s(f.get('revalidation'))}\n- Disposition: {_s(f.get('disposition'))}\n- Dependencies: {_s(f.get('dependencies'))}\n- Completion gates: {_s(f.get('completion_gates'))}\n- Preservation constraints: {_s(f.get('preservation_constraints'))}\n\n"
    plan += "## Rollouts\n\n"
    plan += _table(
        ["ID", "State", "Changes", "Authority", "Rollback"],
        [[r.get("id"), r.get("state"), r.get("change_ids"), r.get("authority_ids"), r.get("rollback_plan")] for r in _rows(data.get("rollouts"))],
    )
    plan += "## Planned perception tests\n\n"
    plan += _table(
        ["ID", "Status", "Findings", "Dimensions", "Audience", "Protocol"],
        [[p.get("id"), p.get("status"), p.get("finding_ids"), p.get("dimensions"), p.get("audience_segment"), p.get("protocol")] for p in _rows(data.get("perception_tests"))],
    )

    implementation = _heading("Implementation ledger")
    implementation += _table(
        ["ID", "Scope", "Findings", "Targets", "Risk", "Authorities", "Description"],
        [[c.get("id"), c.get("scope"), c.get("finding_ids"), c.get("targets"), c.get("risk_level"), c.get("authority_ids"), c.get("description")] for c in _rows(data.get("changes"))],
    )
    implementation += "## Acceptance results\n\n"
    for f in _ordered_findings(data):
        if not isinstance(f, dict):
            continue
        implementation += f"### {f.get('id')} — {f.get('title')}\n\n"
        implementation += _table(
            ["Status", "Criterion", "Evidence", "Observation"],
            [[a.get("status"), a.get("criterion"), a.get("evidence_ids"), a.get("observation")] for a in _rows(f.get("acceptance_results"))],
        )

    claims = _heading("Claims and preservation ledger")
    claims += "## Claim trace\n\n"
    claims += _table(
        ["Claim", "Brand", "Source", "Action", "Target", "Verification", "Findings", "Changes"],
        [[f"{c.get('id')} — {c.get('claim')}", c.get("brand"), c.get("source_state"), c.get("action"), c.get("target_state"), c.get("verification_status"), c.get("finding_ids"), c.get("change_ids")] for c in _rows(data.get("claim_trace"))],
    )
    claims += "## Preservation trace\n\n"
    claims += _table(
        ["Finding", "Status", "Constraints", "Evidence"],
        [[f.get("id"), f.get("preservation_status"), f.get("preservation_constraints"), f.get("evidence_ids")] for f in _rows(data.get("findings")) if f.get("preservation_constraints")],
    )

    verification = _heading("Convergence and perception verification")
    verification += "## Evidence\n\n"
    verification += _table(
        ["ID", "Level", "Method", "Status", "Observation", "Limitations"],
        [[e.get("id"), e.get("level"), e.get("method"), e.get("status"), e.get("observation"), e.get("limitations")] for e in _rows(data.get("evidence"))],
    )
    verification += "## Convergence findings\n\n"
    verification += _table(
        ["ID", "Severity", "Status", "Source", "Reopened findings", "Reason"],
        [[c.get("id"), c.get("severity"), c.get("status"), c.get("source"), c.get("reopened_finding_ids"), c.get("reason")] for c in _rows(data.get("convergence_findings"))],
    )
    verification += "## Perception tests\n\n"
    verification += _table(
        ["ID", "Status", "Dimensions", "Audience", "Sample", "Baseline", "Result", "Limitations"],
        [[p.get("id"), p.get("status"), p.get("dimensions"), p.get("audience_segment"), p.get("sample_source"), p.get("baseline"), p.get("result"), p.get("limitations")] for p in _rows(data.get("perception_tests"))],
    )

    handoff = _heading("Readiness and handoff")
    handoff += _table(
        ["Dimension", "State"],
        [["Revision status", readiness.get("revision_status")], ["Review convergence", readiness.get("review_convergence")], ["Integration", readiness.get("integration")], ["Deployment", readiness.get("deployment")], ["Publication", readiness.get("publication")], ["Perception validation", readiness.get("perception_validation")], ["Business outcome", readiness.get("business_outcome")], ["Authorization summary", readiness.get("authorization_summary")]],
    )
    handoff += "## Delivery\n\n"
    delivery = _obj(readiness.get("delivery"))
    handoff += _table(
        ["Action", "State", "Observation", "Evidence"],
        [[key, value.get("state"), value.get("observation"), value.get("evidence_ids")] for key, value in delivery.items() if isinstance(value, dict)],
    )
    handoff += "## Unverified outcomes\n\n"
    for item in _strings(readiness.get("unverified_outcomes")):
        handoff += f"- {_s(item)}\n"
    if not _strings(readiness.get("unverified_outcomes")):
        handoff += "- None recorded.\n"
    handoff += "\n## Follow-up actions\n\n"
    for item in _strings(readiness.get("follow_up_actions")):
        handoff += f"- {_s(item)}\n"
    if not _strings(readiness.get("follow_up_actions")):
        handoff += "- None recorded.\n"

    return {
        "README.md": readme,
        "00-decisions-authority-and-scope.md": decisions,
        "01-baseline-and-revalidation.md": baseline,
        "02-strategy-execution-and-rollout-plan.md": plan,
        "03-implementation-ledger.md": implementation,
        "04-claims-and-preservation-ledger.md": claims,
        "05-convergence-and-perception-verification.md": verification,
        "06-readiness-and-handoff.md": handoff,
    }


def load_renderable_revision(path: Path) -> dict[str, Any]:
    """Load revision.json and reject syntax or structural defects before rendering."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"could not read revision artifact {path}: {exc}") from None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in revision artifact {path}: {exc}") from None

    shape_errors: list[str] = []
    _shape_revision(data, shape_errors)
    if shape_errors:
        details = "\n".join(f"- {error}" for error in shape_errors)
        raise ValueError(f"cannot render invalid revision artifact {path}:\n{details}")
    assert isinstance(data, dict)
    return data


def render_to_disk(root: Path) -> None:
    root = root.resolve()
    data = load_renderable_revision(root / "revision.json")
    for name, content in render_all(data).items():
        (root / name).write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision_directory", type=Path)
    args = parser.parse_args()
    try:
        render_to_disk(args.revision_directory)
    except ValueError as exc:
        print(exc)
        return 2
    print(f"Rendered {len(GENERATED_FILES)} brand-revision view(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())