#!/usr/bin/env python3
"""Create a clearly provisional UX/UI teardown handoff for an actual project."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from render_handoff import render
from validate_ux_ui_teardown import ACCESS, AUDIENCE, PASSES, validate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--project-locator", required=True)
    parser.add_argument("--audited-revision", required=True)
    parser.add_argument("--project-type", required=True)
    parser.add_argument("--audience-scope", required=True, choices=sorted(AUDIENCE))
    parser.add_argument("--primary-user", required=True)
    parser.add_argument("--primary-goal", required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error("refusing to overwrite a non-empty teardown directory")

    today = date.today().isoformat()
    findings = {
        "schema_version": "ux-ui-teardown-v2",
        "audit": {
            "project_name": args.project_name,
            "project_locator": args.project_locator,
            "audited_revision": args.audited_revision,
            "production_locator": "",
            "production_revision_status": "not_applicable",
            "audit_start_date": today,
            "audit_end_date": today,
            "review_status": "provisional",
            "project_type": args.project_type,
            "audience_scope": args.audience_scope,
            "primary_user_groups": [args.primary_user],
            "primary_goals": [args.primary_goal],
            "owner_context": [],
            "competitor_benchmark_required": True,
            "competitor_benchmark_reason": "Selection and observation have not yet been completed.",
        },
        "evidence_sources": [],
        "competitor_set": [],
        "journeys": [],
        "experience_assessments": [],
        "findings": [],
    }
    coverage = {
        "schema_version": "ux-ui-teardown-coverage-v2",
        "review_status": "provisional",
        "access": [
            {
                "category": category,
                "status": "blocked",
                "material_to_complete": False,
                "evidence_ids": [],
                "limitations": ["Not assessed yet."],
                "next_step": "Assess access and evidence.",
            }
            for category in sorted(ACCESS)
        ],
        "passes": [
            {
                "id": name,
                "materiality": "defining" if name in {"ui_craft", "ux_experience"} else "supporting",
                "status": "not_tested",
                "finding_ids": [],
                "evidence_ids": [],
                "limitations": ["Not assessed yet."],
            }
            for name in sorted(PASSES)
        ],
        "viewports": [],
        "input_modes": [],
        "state_coverage": [],
        "material_limitations": [{
            "id": "LIMIT-001",
            "status": "open",
            "description": "Bootstrap scaffold; product experience not yet audited.",
            "completion_requirement": "Replace scaffold coverage with actual observations and resolve material gaps.",
        }],
        "validator": {"name": "validate_ux_ui_teardown.py", "status": "pending", "validated_at": today},
    }

    # Validate before creating directories so malformed arguments leave no partial handoff.
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        staged = Path(temp)
        for name, data in (("findings.json", findings), ("coverage.json", coverage)):
            (staged / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        errors = validate(staged)
        if errors:
            parser.error("invalid bootstrap arguments: " + "; ".join(errors[:10]))

    output.mkdir(parents=True, exist_ok=True)
    (output / "evidence").mkdir(exist_ok=True)
    for name, data in (("findings.json", findings), ("coverage.json", coverage)):
        (output / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    for name, content in render(output).items():
        (output / name).write_text(content, encoding="utf-8", newline="\n")
    print(f"bootstrapped provisional teardown in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
