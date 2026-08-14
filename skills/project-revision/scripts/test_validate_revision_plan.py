#!/usr/bin/env python3
"""Regression tests for validate_revision_plan.py."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from validation_common import canonical_digest
from validate_revision_plan import validate


def finding(fid: str, title: str, *, status: str = "open", kind: str = "defect", action: str = "fix", deps=None):
    return {
        "id": fid,
        "title": title,
        "type": kind,
        "category": "reliability",
        "severity": "high" if kind != "strength" else "informational",
        "confidence": "confirmed",
        "status": status,
        "impact": f"Impact for {fid}",
        "evidence": [{"source": "src/example.ts:1", "observation": f"Evidence for {fid}"}],
        "expected_behavior": "Expected behavior",
        "actual_behavior": "Actual behavior",
        "root_cause": "Root cause",
        "affected_components": [f"src/{fid.lower()}.ts", "CLI workflow"],
        "recommendation": "Recommendation",
        "if_implemented": "Improved state",
        "if_unchanged": "Risk remains",
        "dependencies": list(deps or []),
        "dependents": [],
        "conflicts": [],
        "acceptance_criteria": [f"{fid} criterion one", f"{fid} criterion two"],
        "verification": f"Run verification for {fid}",
        "estimated_scope": "small",
        "regression_risk": "medium",
        "action": action,
        "strategic_classification": ["release-gate"] if kind != "strength" else ["retained-strength"],
    }


def build_teardown() -> dict:
    findings = [
        finding("TECH-001", "Repair behavior"),
        finding("PROD-001", "Choose product boundary", status="decision-required", deps=["TECH-001"]),
        finding("REL-001", "Verify external runtime", status="blocked", kind="investigation", action="investigate"),
        finding("STRENGTH-001", "Preserve clear workflow", status="retained", kind="strength", action="retain"),
    ]
    findings[0]["dependents"] = ["PROD-001"]
    return {
        "schema_version": 2,
        "project": "owner/project",
        "audited_revision": "abc123",
        "review_status": "complete",
        "core_workflows_fully_exercised": True,
        "generated_at": "2026-07-17T12:00:00-05:00",
        "findings": findings,
    }


def trace_section(item: dict) -> str:
    treatment = "implement"
    owner = "None"
    blocker = "None"
    revalidation = "confirmed"
    if item["status"] == "decision-required":
        treatment = "owner-decision"
        owner = "Choose option A or option B before implementation."
    elif item["status"] == "blocked":
        treatment = "blocker"
        revalidation = "blocked"
        blocker = "Run the required external environment check."
    elif item["type"] == "strength":
        treatment = "retain"
    deps = " | ".join(item["dependencies"]) or "None"
    criteria = " | ".join(item["acceptance_criteria"]) or "None"
    surfaces = " | ".join(item["affected_components"]) or "None"
    return f"""### {item['id']} — {item['title']}

- **Teardown status:** {item['status']}
- **Teardown verification state:** {item.get('verification_state', 'legacy-not-recorded')}
- **Revalidation:** {revalidation}
- **Plan treatment:** {treatment}
- **Dependencies:** {deps}
- **Owner decision:** {owner}
- **Blocker or completion gate:** {blocker}
- **Acceptance criteria carried forward:** {criteria}
- **Verification carried forward:** {item['verification']}
- **Affected surfaces carried forward:** {surfaces}
- **Plan action:** Carry out the current evidence-backed action for {item['id']}.
- **Notes:** None
- **Teardown record digest:** {canonical_digest(item)}
"""


def build_plan(teardown: dict) -> str:
    traces = "\n".join(trace_section(item) for item in teardown["findings"])
    return f"""# Project revision plan

**Artifact mode:** planning-only
**Product edits performed:** no
**Convergence testing performed:** no
**Teardown review status:** {teardown['review_status']}
**Teardown finding count:** {len(teardown['findings'])}
**Current revision checked:** abc123

## Purpose and boundary

Plan only.

## Current-state revalidation

Every finding was checked.

## Delta from the original teardown

### Teardown recommendations translated or reorganized

The plan reorganizes the original work.

### New implementation or sequencing recommendations

These remain recommendations.

### Genuinely new findings from current-state revalidation

No genuinely new findings were discovered.

## Owner decisions required

PROD-001 remains unresolved.

## Proposed implementation sequence

Follow dependency order.

## Traceability ledger

{traces}

## Blockers and completion gates

REL-001 remains blocked on the external environment.

## What was not done

No product code, tests, configuration, manifests, deployment files, or operational content were edited.

No implementation convergence testing was performed.
"""


class RevisionPlanValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.teardown_root = self.root / "project-teardown"
        self.teardown_root.mkdir()
        self.plan_path = self.root / "plan.md"
        self.teardown = build_teardown()
        self.write()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, teardown=None, plan=None) -> None:
        teardown = teardown or self.teardown
        (self.teardown_root / "findings.json").write_text(json.dumps(teardown, indent=2), encoding="utf-8")
        self.plan_path.write_text(plan or build_plan(teardown), encoding="utf-8")

    def assert_error_contains(self, needle: str, teardown=None, plan=None) -> None:
        self.write(teardown, plan)
        self.assertTrue(any(needle in error for error in validate(self.teardown_root, self.plan_path)), needle)

    def test_valid_plan_passes(self) -> None:
        self.assertEqual([], validate(self.teardown_root, self.plan_path))

    def test_missing_planning_marker_fails(self) -> None:
        plan = build_plan(self.teardown).replace("**Product edits performed:** no\n", "")
        self.assert_error_contains("**Product edits performed:**", plan=plan)


    def test_schema_three_teardown_preserves_verification_state(self) -> None:
        teardown = copy.deepcopy(self.teardown)
        teardown["schema_version"] = 3
        for item in teardown["findings"]:
            item["verification_state"] = (
                "blocked" if item["status"] == "blocked"
                else "behaviorally-verified" if item["type"] == "strength"
                else "defect-conclusively-demonstrated"
            )
        self.write(teardown=teardown, plan=build_plan(teardown))
        self.assertEqual([], validate(self.teardown_root, self.plan_path))

    def test_verification_state_drift_fails(self) -> None:
        teardown = copy.deepcopy(self.teardown)
        teardown["schema_version"] = 3
        for item in teardown["findings"]:
            item["verification_state"] = "defect-conclusively-demonstrated"
        plan = build_plan(teardown).replace(
            "**Teardown verification state:** defect-conclusively-demonstrated",
            "**Teardown verification state:** source-only",
            1,
        )
        self.assert_error_contains("teardown verification state does not match", teardown=teardown, plan=plan)

    def test_wrong_finding_count_fails(self) -> None:
        plan = build_plan(self.teardown).replace("**Teardown finding count:** 4", "**Teardown finding count:** 3")
        self.assert_error_contains("Teardown finding count differs", plan=plan)

    def test_missing_required_section_fails(self) -> None:
        plan = build_plan(self.teardown).replace("## Owner decisions required", "## Decisions")
        self.assert_error_contains("## Owner decisions required", plan=plan)

    def test_missing_finding_fails(self) -> None:
        plan = build_plan(self.teardown)
        start = plan.index("### TECH-001")
        end = plan.index("### PROD-001")
        plan = plan[:start] + plan[end:]
        self.assert_error_contains("traceability ledger missing findings: TECH-001", plan=plan)

    def test_unknown_finding_fails(self) -> None:
        extra = trace_section({**self.teardown["findings"][0], "id": "NEW-001", "title": "New"})
        plan = build_plan(self.teardown).replace("## Blockers and completion gates", extra + "\n## Blockers and completion gates")
        self.assert_error_contains("traceability ledger has unknown findings: NEW-001", plan=plan)

    def test_duplicate_finding_fails(self) -> None:
        duplicate = trace_section(self.teardown["findings"][0])
        plan = build_plan(self.teardown).replace("## Blockers and completion gates", duplicate + "\n## Blockers and completion gates")
        self.assert_error_contains("traceability ledger repeats finding: TECH-001", plan=plan)

    def test_status_drift_fails(self) -> None:
        plan = build_plan(self.teardown).replace("**Teardown status:** open", "**Teardown status:** accepted-risk", 1)
        self.assert_error_contains("TECH-001 teardown status does not match", plan=plan)

    def test_dependency_drift_fails(self) -> None:
        plan = build_plan(self.teardown).replace("**Dependencies:** TECH-001", "**Dependencies:** None", 1)
        self.assert_error_contains("PROD-001 dependencies do not exactly match", plan=plan)

    def test_acceptance_criteria_drift_fails(self) -> None:
        plan = build_plan(self.teardown).replace("TECH-001 criterion two", "summarized criterion", 1)
        self.assert_error_contains("TECH-001 acceptance criteria do not exactly match", plan=plan)

    def test_affected_surface_drift_fails(self) -> None:
        plan = build_plan(self.teardown).replace("src/tech-001.ts | CLI workflow", "src/tech-001.ts", 1)
        self.assert_error_contains("TECH-001 affected surfaces do not exactly match", plan=plan)

    def test_digest_drift_fails(self) -> None:
        plan = build_plan(self.teardown).replace(canonical_digest(self.teardown["findings"][0]), "sha256:" + "0" * 64, 1)
        self.assert_error_contains("TECH-001 teardown record digest does not match", plan=plan)

    def test_strength_must_be_retained(self) -> None:
        plan = build_plan(self.teardown).replace("**Plan treatment:** retain", "**Plan treatment:** implement", 1)
        self.assert_error_contains("STRENGTH-001 is a retained strength", plan=plan)

    def test_unresolved_decision_must_remain_explicit(self) -> None:
        plan = build_plan(self.teardown).replace("**Plan treatment:** owner-decision", "**Plan treatment:** implement", 1).replace(
            "**Owner decision:** Choose option A or option B before implementation.", "**Owner decision:** None", 1
        )
        self.assert_error_contains("PROD-001 still requires an owner decision", plan=plan)

    def test_blocker_must_remain_explicit(self) -> None:
        plan = build_plan(self.teardown).replace("**Blocker or completion gate:** Run the required external environment check.", "**Blocker or completion gate:** None", 1)
        self.assert_error_contains("REL-001 blocked revalidation requires", plan=plan)

    def test_false_implementation_handoff_marker_fails(self) -> None:
        plan = build_plan(self.teardown).replace("## What was not done", "**Merge readiness:** ready\n\n## What was not done")
        self.assert_error_contains("implementation handoff marker", plan=plan)

    def test_missing_no_new_findings_statement_fails(self) -> None:
        plan = build_plan(self.teardown).replace("No genuinely new findings were discovered.", "Nothing else changed.")
        self.assert_error_contains("new-findings delta must state", plan=plan)

    def test_missing_no_product_edits_statement_fails(self) -> None:
        plan = build_plan(self.teardown).replace(
            "No product code, tests, configuration, manifests, deployment files, or operational content were edited.",
            "No edits occurred.",
        )
        self.assert_error_contains("No product code, tests", plan=plan)

    def test_no_action_requires_resolved_revalidation(self) -> None:
        plan = build_plan(self.teardown).replace("**Plan treatment:** implement", "**Plan treatment:** no-action", 1)
        self.assert_error_contains("TECH-001 no-action is only valid", plan=plan)


if __name__ == "__main__":
    unittest.main()
