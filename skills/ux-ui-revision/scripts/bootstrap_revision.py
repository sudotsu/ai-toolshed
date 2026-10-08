#!/usr/bin/env python3
"""Bootstrap a planning-only ux-ui-revision v2 artifact from validated teardown."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from validation_common import run_upstream_validator

AUTH = [
    "repository_edit",
    "design_file_edit",
    "cms_edit",
    "public_content_publish",
    "production_deploy",
    "external_profile_change",
    "analytics_mutation",
    "paid_purchase",
    "third_party_outreach",
    "merge",
]


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("teardown", type=Path)
    parser.add_argument("revision", type=Path)
    args = parser.parse_args()
    teardown = args.teardown.resolve()
    output = args.revision.resolve()

    ok, message = run_upstream_validator(teardown)
    if not ok:
        print("ux-ui-teardown upstream validation failed: " + str(message)[:2000], file=sys.stderr)
        return 1
    if output.exists() and any(output.iterdir()):
        print("refusing to overwrite non-empty revision directory", file=sys.stderr)
        return 1

    try:
        findings = json.loads((teardown / "findings.json").read_text(encoding="utf-8"))
        source_rows = findings["findings"]
        if not isinstance(source_rows, list):
            raise ValueError("findings must be a list")
        rows = []
        for source in source_rows:
            if not isinstance(source, dict):
                raise ValueError("every finding must be an object")
            criteria = source.get("acceptance_criteria")
            if not isinstance(criteria, list) or not all(isinstance(item, str) and item.strip() for item in criteria):
                raise ValueError(f"{source.get('id', '<unknown>')} acceptance_criteria must be a string list")
            is_strength = source.get("kind") == "strength"
            rows.append({
                "finding_id": source["id"],
                "original_status": source["status"],
                "revalidation": "blocked",
                "approval": "not_applicable" if is_strength else "pending",
                "implementation_status": "preserved" if is_strength else "planned",
                "current_evidence": [],
                "changed_targets": [],
                "changed_target_actions": {},
                "acceptance_results": [
                    {"criterion": criterion, "status": "pending", "evidence": []}
                    for criterion in criteria
                ],
                "verification_evidence": [],
                "preservation_status": "pending",
                "notes": "Planning scaffold; revalidate before implementation.",
            })
        data = {
            "schema_version": "ux-ui-revision-v2",
            "mode": "planning-only",
            "source": {
                "teardown_schema_version": findings["schema_version"],
                "teardown_revision": findings["audit"]["audited_revision"],
                "teardown_review_status": findings["audit"]["review_status"],
                "teardown_findings_digest": digest(teardown / "findings.json"),
            },
            "baseline": {
                "current_revision": "unrecorded",
                "working_tree_state": "unrecorded",
                "production_revision_status": "unrecorded",
                "captured_at": "unrecorded",
                "material_drift": False,
                "drift_notes": [],
            },
            "authority": [
                {"action": action, "status": "not_authorized", "scope": [], "evidence": []}
                for action in AUTH
            ],
            "findings": rows,
            "decisions": [],
            "convergence": {"reviewed_revision": "unrecorded", "status": "not_started", "findings": []},
            "readiness": {
                "implementation": "not_started",
                "integration": "not_started",
                "deployment": "not_performed",
                "publication": "not_performed",
                "user_outcome": "unverified",
                "business_outcome": "unverified",
                "overall": "planned",
                "highest_evidence_level": "source_inspection",
                "limitations": ["Planning scaffold only; current-state revalidation incomplete."],
            },
        }
    except Exception as exc:
        print(f"cannot build revision scaffold: {exc}", file=sys.stderr)
        return 1

    output.mkdir(parents=True, exist_ok=True)
    (output / "evidence").mkdir(exist_ok=True)
    (output / "revision.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")

    from render_revision import render

    for name, rendered in render(output).items():
        (output / name).write_text(rendered, encoding="utf-8", newline="\n")
    print(f"bootstrapped {len(rows)} finding row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
