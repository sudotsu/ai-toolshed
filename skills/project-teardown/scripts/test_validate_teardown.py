#!/usr/bin/env python3
"""Regression tests for validate_teardown.py."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from finding_model import render_findings_register, render_readme
from validate_teardown import validate


class TeardownValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project-teardown"
        self.root.mkdir()
        (self.root / "evidence").mkdir()
        self.findings = [
            self._finding(
                "TECH-001",
                "Repair core behavior",
                dependencies=[],
                dependents=["UX-001"],
            ),
            self._finding(
                "UX-001",
                "Expose recovery guidance",
                dependencies=["TECH-001"],
                dependents=[],
            ),
            self._strength(),
        ]
        self.payload = {
            "schema_version": 3,
            "project": "owner/project",
            "audited_revision": "abc123-clean",
            "review_status": "complete",
            "core_workflows_fully_exercised": True,
            "generated_at": "2026-07-17T12:00:00Z",
            "findings": self.findings,
        }
        self._write_fixture()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _finding(
        self,
        finding_id: str,
        title: str,
        *,
        dependencies: list[str],
        dependents: list[str],
    ) -> dict:
        return {
            "id": finding_id,
            "title": title,
            "type": "defect",
            "category": "runtime",
            "severity": "medium",
            "confidence": "confirmed",
            "verification_state": "defect-conclusively-demonstrated",
            "status": "open",
            "impact": f"{title} affects the intended workflow.",
            "evidence": [{
                "kind": "runtime",
                "source": "manual reproduction",
                "location": "evidence/reproduction.txt",
                "claim": f"{title} reproduced.",
            }],
            "expected_behavior": "The workflow completes and recovers safely.",
            "actual_behavior": "The workflow fails under the reproduced condition.",
            "root_cause": "Confirmed implementation defect.",
            "affected_components": ["src/example.ts"],
            "recommendation": "Repair the behavior and add regression coverage.",
            "if_implemented": "The defining workflow becomes reliable.",
            "if_unchanged": "Users continue to encounter the failure.",
            "dependencies": dependencies,
            "dependents": dependents,
            "conflicts": [],
            "acceptance_criteria": ["The reproduction passes.", "The failure path remains bounded."],
            "verification": "Run the focused regression and defining workflow.",
            "estimated_scope": "small",
            "regression_risk": "medium",
            "action": "fix",
            "strategic_classification": [],
        }

    def _strength(self) -> dict:
        return {
            "id": "STRENGTH-001",
            "title": "Preserve clear onboarding",
            "type": "strength",
            "category": "onboarding",
            "severity": "informational",
            "confidence": "confirmed",
            "verification_state": "behaviorally-verified",
            "status": "retained",
            "impact": "Clear onboarding reduces first-run failure.",
            "evidence": [{
                "kind": "runtime",
                "source": "clean-user walkthrough",
                "location": "evidence/onboarding.txt",
                "claim": "The documented first run completed without hidden steps.",
            }],
            "expected_behavior": "Onboarding remains clear.",
            "actual_behavior": "Onboarding is clear.",
            "root_cause": "Deliberate product design.",
            "affected_components": ["README.md", "src/cli.ts"],
            "recommendation": "Preserve this behavior through later changes.",
            "if_implemented": "Not applicable — already present.",
            "if_unchanged": "The strength remains available.",
            "dependencies": [],
            "dependents": [],
            "conflicts": [],
            "acceptance_criteria": ["The clean-user first run remains successful."],
            "verification": "Repeat the clean-user walkthrough after revision.",
            "estimated_scope": "trivial",
            "regression_risk": "low",
            "action": "retain",
            "strategic_classification": ["ahead of the curve"],
        }

    def _render_register(self) -> str:
        return render_findings_register(self.payload)

    def _coverage(self) -> str:
        if self.payload["schema_version"] == 3:
            surface = """| Surface | Importance | Status | Verification class | Evidence level | Evidence | Limitations | Next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Defining workflow | defining | passed | behaviorally-verified | behavioral | evidence/reproduction.txt | None | Retest after revision |
| Supported runtime | required | passed | behaviorally-verified | mixed | Build and behavioral smoke | None | Keep in CI |"""
        else:
            surface = """| Surface | Importance | Status | Evidence level | Evidence | Limitations | Next step |
| --- | --- | --- | --- | --- | --- | --- |
| Defining workflow | defining | passed | behavioral | evidence/reproduction.txt | None | Retest after revision |
| Supported runtime | required | passed | mixed | Build and behavioral smoke | None | Keep in CI |"""
        return f"""# Review Coverage

**Review status:** complete
**Core workflows fully exercised:** yes
**Validator status:** passed

## Surface coverage

{surface}

## Narrative reconciliation

| Report section | Classification | Finding IDs | Rationale |
| --- | --- | --- | --- |
| 01-product-and-market.md | context | None | No separate strategic action beyond registered findings. |
| 02-user-experience.md | mixed | UX-001, STRENGTH-001 | One actionable recovery issue and one retained strength. |
| 03-technical-audit.md | actionable | TECH-001 | Runtime defect requires implementation. |
| 04-security-and-reliability.md | passed-check | None | No additional actionable security observation. |

## Finding counts

**Total findings:** 3

### By severity

### By status

### By type

### By action

## Validator result

Command completed successfully.
"""

    def _write_fixture(self) -> None:
        generic = {
            "00-executive-verdict.md": "# Executive Verdict\n\n**Review status:** complete\n\nComplete evidence-led review.\n",
            "01-product-and-market.md": "# Product and Market\n\nCurrent benchmark analysis.\n",
            "02-user-experience.md": "# User Experience\n\nTested journeys and strengths.\n",
            "03-technical-audit.md": "# Technical Audit\n\nRuntime and source analysis.\n",
            "04-security-and-reliability.md": "# Security and Reliability\n\nTrust-boundary analysis.\n",
        }
        for name, content in generic.items():
            (self.root / name).write_text(content, encoding="utf-8")
        (self.root / "05-findings-register.md").write_text(self._render_register(), encoding="utf-8")
        (self.root / "README.md").write_text(render_readme(self.payload), encoding="utf-8")
        (self.root / "08-claims-inventory.md").write_text(
            """# Claims Inventory

## Claims

| Claim ID | Claim text | Location | Category | Required evidence | Evidence found | Verification state | Disposition | Related finding IDs | Required action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CLAIM-000 | No material external claims identified | Whole product | other | Not applicable | Not applicable | not-applicable | not-applicable | None | Continue monitoring for material claims |
""",
            encoding="utf-8",
        )
        (self.root / "06-implementation-sequence.md").write_text(
            """# Implementation Sequence

## Coverage ledger

| Sequence | Finding ID | Planned disposition | Prerequisites | Rationale |
| --- | --- | --- | --- | --- |
| 1 | TECH-001 | fix | None | Foundation first. |
| 2 | UX-001 | fix | TECH-001 | Depends on repaired behavior. |
| 3 | STRENGTH-001 | retain | None | Preserve onboarding. |
""",
            encoding="utf-8",
        )
        (self.root / "07-review-coverage.md").write_text(self._coverage(), encoding="utf-8")
        (self.root / "findings.json").write_text(
            json.dumps(self.payload, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.root / "evidence" / "reproduction.txt").write_text("sanitized", encoding="utf-8")
        (self.root / "evidence" / "onboarding.txt").write_text("sanitized", encoding="utf-8")

    def _rewrite(self) -> None:
        self._write_fixture()

    def test_valid_schema_three_artifact_passes(self) -> None:
        self.assertEqual(validate(self.root), [])

    def test_legacy_schema_one_remains_supported(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["schema_version"] = 1
        payload.pop("core_workflows_fully_exercised")
        for finding in payload["findings"]:
            finding.pop("verification_state")
        payload["findings"][-1]["status"] = "accepted-risk"
        self.payload = payload
        self._rewrite()
        self.assertEqual(validate(self.root), [])

    def test_missing_evidence_directory_fails(self) -> None:
        (self.root / "evidence" / "reproduction.txt").unlink()
        (self.root / "evidence" / "onboarding.txt").unlink()
        (self.root / "evidence").rmdir()
        self.assertIn("missing required directory: evidence", validate(self.root))

    def test_digest_drift_is_detected(self) -> None:
        self.payload["findings"][0]["impact"] = "Changed only in JSON."
        (self.root / "findings.json").write_text(json.dumps(self.payload), encoding="utf-8")
        errors = validate(self.root)
        self.assertTrue(any("05-findings-register.md is stale" in error for error in errors))

    def test_reverse_dependency_is_required(self) -> None:
        self.payload["findings"][0]["dependents"] = []
        self._rewrite()
        self.assertTrue(any("reverse dependent link is missing" in error for error in validate(self.root)))

    def test_conflicts_are_symmetric(self) -> None:
        self.payload["findings"][0]["conflicts"] = ["UX-001"]
        self._rewrite()
        self.assertTrue(any("reverse conflict link is missing" in error for error in validate(self.root)))

    def test_dependency_cycle_is_detected(self) -> None:
        self.payload["findings"][0]["dependencies"] = ["UX-001"]
        self.payload["findings"][1]["dependents"] = ["TECH-001"]
        self._rewrite()
        self.assertTrue(any("dependency cycle" in error for error in validate(self.root)))

    def test_duplicate_array_values_are_rejected(self) -> None:
        self.payload["findings"][0]["affected_components"] = ["src/example.ts", "src/example.ts"]
        self._rewrite()
        self.assertTrue(any("contains duplicates" in error for error in validate(self.root)))

    def test_confirmed_finding_requires_evidence(self) -> None:
        self.payload["findings"][0]["evidence"] = []
        self._rewrite()
        self.assertIn("TECH-001 confirmed confidence requires evidence", validate(self.root))

    def test_strength_semantics_are_enforced(self) -> None:
        self.payload["findings"][-1]["status"] = "open"
        self._rewrite()
        self.assertTrue(any("strength requires" in error for error in validate(self.root)))

    def test_decision_status_and_action_must_match(self) -> None:
        self.payload["findings"][0]["status"] = "decision-required"
        self._rewrite()
        self.assertTrue(any("must occur together" in error for error in validate(self.root)))

    def test_complete_review_cannot_have_required_gap(self) -> None:
        coverage = self._coverage().replace(
            "| Supported runtime | required | passed | behaviorally-verified | mixed | Build and behavioral smoke | None | Keep in CI |",
            "| Supported runtime | required | blocked | blocked | none | No behavioral evidence | No runtime access | Obtain runtime access |",
        )
        (self.root / "07-review-coverage.md").write_text(coverage, encoding="utf-8")
        self.assertIn("complete review has a defining or required coverage gap", validate(self.root))

    def test_core_workflow_json_marker_must_match(self) -> None:
        self.payload["core_workflows_fully_exercised"] = False
        (self.root / "findings.json").write_text(json.dumps(self.payload), encoding="utf-8")
        self.assertTrue(any("core workflow status differs" in error for error in validate(self.root)))

    def test_coverage_ledger_must_follow_dependencies(self) -> None:
        path = self.root / "06-implementation-sequence.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "| 1 | TECH-001 | fix | None | Foundation first. |\n| 2 | UX-001 | fix | TECH-001 | Depends on repaired behavior. |",
            "| 1 | UX-001 | fix | TECH-001 | Incorrect order. |\n| 2 | TECH-001 | fix | None | Too late. |",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("before dependency" in error for error in validate(self.root)))

    def test_narrative_reconciliation_must_cover_all_core_files(self) -> None:
        path = self.root / "07-review-coverage.md"
        text = path.read_text(encoding="utf-8").replace(
            "| 04-security-and-reliability.md | passed-check | None | No additional actionable security observation. |\n",
            "",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("missing report files" in error for error in validate(self.root)))

    def test_actionable_reconciliation_requires_finding_ids(self) -> None:
        path = self.root / "07-review-coverage.md"
        text = path.read_text(encoding="utf-8").replace(
            "| 03-technical-audit.md | actionable | TECH-001 |",
            "| 03-technical-audit.md | actionable | None |",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("actionable but has no finding IDs" in error for error in validate(self.root)))

    def test_total_findings_must_match(self) -> None:
        path = self.root / "07-review-coverage.md"
        path.write_text(path.read_text(encoding="utf-8").replace("**Total findings:** 3", "**Total findings:** 2"), encoding="utf-8")
        self.assertIn("review coverage Total findings does not match findings.json", validate(self.root))

    def test_validator_status_must_be_passed(self) -> None:
        path = self.root / "07-review-coverage.md"
        path.write_text(path.read_text(encoding="utf-8").replace("**Validator status:** passed", "**Validator status:** pending"), encoding="utf-8")
        self.assertIn("review coverage Validator status must be passed for final delivery", validate(self.root))


    def test_schema_two_remains_supported(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["schema_version"] = 2
        for finding in payload["findings"]:
            finding.pop("verification_state")
        self.payload = payload
        self._rewrite()
        self.assertEqual(validate(self.root), [])

    def test_stale_generated_register_is_single_root_error(self) -> None:
        (self.root / "05-findings-register.md").write_text("# Findings Register\n\nbroken\n", encoding="utf-8")
        errors = validate(self.root)
        self.assertEqual(
            [error for error in errors if "05-findings-register.md" in error],
            ["05-findings-register.md is stale or manually edited; regenerate it from findings.json with render_findings.py"],
        )
        self.assertFalse(any("Markdown and JSON finding ID sets differ" in error for error in errors))

    def test_stale_readme_fails(self) -> None:
        (self.root / "README.md").write_text("# Project Teardown\n", encoding="utf-8")
        self.assertTrue(any("README.md is stale" in error for error in validate(self.root)))

    def test_unresolved_claim_requires_related_finding(self) -> None:
        path = self.root / "08-claims-inventory.md"
        path.write_text(
            """# Claims Inventory

## Claims

| Claim ID | Claim text | Location | Category | Required evidence | Evidence found | Verification state | Disposition | Related finding IDs | Required action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CLAIM-001 | Certified expert | homepage | credential | Current credential | None | unsupported | remove | None | Remove claim |
""",
            encoding="utf-8",
        )
        self.assertTrue(any("requires a related finding" in error for error in validate(self.root)))

    def test_blocked_surface_requires_blocked_verification_class(self) -> None:
        coverage = self._coverage().replace(
            "| Supported runtime | required | passed | behaviorally-verified |",
            "| Supported runtime | required | blocked | operationally-unverified |",
        ).replace("**Review status:** complete", "**Review status:** provisional")
        coverage = coverage.replace("**Core workflows fully exercised:** yes", "**Core workflows fully exercised:** no")
        coverage = coverage.replace("| Build and behavioral smoke | None | Keep in CI |", "| Build evidence | Missing runtime | Obtain runtime |")
        self.payload["review_status"] = "provisional"
        self.payload["core_workflows_fully_exercised"] = False
        (self.root / "00-executive-verdict.md").write_text(
            "# Executive Verdict\n\n**Review status:** provisional\n", encoding="utf-8"
        )
        (self.root / "07-review-coverage.md").write_text(coverage, encoding="utf-8")
        (self.root / "findings.json").write_text(json.dumps(self.payload, indent=2) + "\n", encoding="utf-8")
        (self.root / "05-findings-register.md").write_text(render_findings_register(self.payload), encoding="utf-8")
        (self.root / "README.md").write_text(render_readme(self.payload), encoding="utf-8")
        self.assertTrue(any("blocked status requires blocked verification class" in error for error in validate(self.root)))

    def test_timestamp_requires_timezone(self) -> None:
        self.payload["generated_at"] = "2026-07-17T12:00:00"
        self._rewrite()
        self.assertIn("findings.json generated_at must include a timezone", validate(self.root))


if __name__ == "__main__":
    unittest.main()
