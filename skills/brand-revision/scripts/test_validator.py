#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from bootstrap_revision import build_scaffold
from render_revision import render_to_disk
from validate_brand_revision import validate
from validation_common import parse_frontmatter_name


def teardown_docs() -> tuple[dict, dict]:
    findings = {
        "schema_version": "brand-teardown-v1",
        "audit": {
            "project_name": "Fixture Developer Product",
            "project_locator": "https://example.invalid/repo",
            "audited_revision": "abc123",
            "production_locator": "https://example.invalid",
            "review_status": "provisional",
        },
        "claims": [
            {"id": "CLAIM-001", "claim": "Local-first CLI agent", "brand": "Fixture", "state": "verified"},
            {"id": "CLAIM-002", "claim": "Fastest agent in the market", "brand": "Fixture", "state": "unsupported"},
        ],
        "findings": [
            {
                "id": "FIND-001", "title": "Choose the product identity hierarchy", "status": "decision_required",
                "module": "brand_architecture", "owner_decision": "Choose whether the CLI or parent project leads the public identity.",
                "recommendation": "Lead with the CLI product and endorse it from the parent project.",
                "priority": {"reversibility": "moderate"}, "dependencies": [],
                "acceptance_criteria": ["One public identity hierarchy is documented and used consistently."],
                "preservation_constraints": ["Preserve the existing product name unless the owner explicitly changes it."],
                "implementation": {"order": 1, "owner_or_external_actions": []},
            },
            {
                "id": "FIND-002", "title": "Replace unsupported category-superiority language", "status": "open",
                "module": "trust_proof_claims", "owner_decision": None, "recommendation": "Use supportable capability language.",
                "priority": {"reversibility": "easy"}, "dependencies": ["FIND-001"],
                "acceptance_criteria": ["Unsupported superiority language is removed or supported by current evidence."],
                "preservation_constraints": [],
                "implementation": {"order": 2, "owner_or_external_actions": []},
            },
            {
                "id": "FIND-003", "title": "Preserve the blunt technical voice", "status": "retained_strength",
                "module": "voice_verbal_identity", "owner_decision": None, "recommendation": "Preserve direct technical wording.",
                "priority": {"reversibility": "easy"}, "dependencies": [],
                "acceptance_criteria": ["Direct technical voice remains recognizable after revision."],
                "preservation_constraints": ["Do not corporate-wash the product voice."],
                "implementation": {"order": 3, "owner_or_external_actions": []},
            },
            {
                "id": "FIND-004", "title": "Measure comprehension with real technical users", "status": "blocked",
                "module": "message_comprehension", "owner_decision": None, "recommendation": "Run a bounded comprehension test.",
                "blocker": "No recruited audience sample is available.",
                "priority": {"reversibility": "easy"}, "dependencies": ["FIND-002"],
                "acceptance_criteria": ["Representative technical users can identify category, audience, and next action."],
                "preservation_constraints": [],
                "implementation": {"order": 4, "owner_or_external_actions": ["Recruit or authorize access to representative technical users."]},
            },
        ],
    }
    coverage = {
        "schema_version": "brand-teardown-coverage-v1",
        "access": [{"category": "source_repository", "status": "available", "next_step": "Reinspect current source."}],
        "modules": [{"id": "brand_architecture", "status": "failed", "next_step": "Revalidate the identity hierarchy."}],
        "surface_checks": [{"id": "CHECK-001", "status": "partial"}],
        "material_limitations": [{
            "id": "LIMIT-001", "description": "No recruited audience sample was available.", "status": "open",
            "completion_requirement": "Run the planned audience comprehension test with a representative sample."
        }],
    }
    return findings, coverage


def write_case(root: Path) -> tuple[Path, Path, dict]:
    teardown_dir = root / "brand-teardown"
    revision_dir = root / "brand-revision"
    teardown_dir.mkdir(parents=True)
    revision_dir.mkdir(parents=True)
    (revision_dir / "evidence").mkdir()
    findings, coverage = teardown_docs()
    (teardown_dir / "findings.json").write_text(json.dumps(findings, indent=2), encoding="utf-8")
    (teardown_dir / "coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    data = build_scaffold(teardown_dir, revision_dir, findings, coverage)
    (revision_dir / "revision.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    render_to_disk(revision_dir)
    return teardown_dir, revision_dir, data


def save_revision(revision_dir: Path, data: dict) -> None:
    (revision_dir / "revision.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    render_to_disk(revision_dir)


class BrandRevisionValidatorTests(unittest.TestCase):
    def validate_data(self, mutate=None, *, rerender=True) -> list[str]:
        with tempfile.TemporaryDirectory() as temp:
            td, rd, data = write_case(Path(temp))
            if mutate:
                mutate(data, rd)
            (rd / "revision.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
            markdown_is_current = False
            if rerender:
                try:
                    render_to_disk(rd)
                    markdown_is_current = True
                except ValueError:
                    # Structural-invalid cases are expected to be rejected before rendering.
                    pass
            return validate(td, rd, run_upstream=False, check_markdown=markdown_is_current)

    def assert_invalid(self, mutate, contains: str, *, rerender=True) -> None:
        errors = self.validate_data(mutate, rerender=rerender)
        self.assertTrue(any(contains in e for e in errors), errors)

    def test_bootstrap_planning_fixture_passes(self):
        self.assertEqual(self.validate_data(), [])

    def test_bootstrap_skip_flag_does_not_forge_passed_upstream_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            td = root / "brand-teardown"
            rd = root / "brand-revision"
            td.mkdir()
            findings, coverage = teardown_docs()
            (td / "findings.json").write_text(json.dumps(findings), encoding="utf-8")
            (td / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("bootstrap_revision.py")), str(td), str(rd), "--skip-upstream-validation"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads((rd / "revision.json").read_text(encoding="utf-8"))
            self.assertEqual(data["teardown"]["validator_result"], "skipped-for-isolated-test")
            errors = validate(td, rd, run_upstream=False, check_markdown=True)
            self.assertTrue(any("validator_result must be passed" in e for e in errors), errors)

    def test_bootstrap_refuses_to_overwrite_existing_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            td = root / "brand-teardown"
            rd = root / "brand-revision"
            td.mkdir()
            rd.mkdir()
            findings, coverage = teardown_docs()
            (td / "findings.json").write_text(json.dumps(findings), encoding="utf-8")
            (td / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
            sentinel = rd / "revision.json"
            sentinel.write_text("owner state must survive\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("bootstrap_revision.py")), str(td), str(rd), "--skip-upstream-validation"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("refusing to overwrite", proc.stdout)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "owner state must survive\n")

    def test_frontmatter_name_must_match_exactly(self):
        self.assertEqual(parse_frontmatter_name("---\nname: brand-teardown\n---\nbody\n"), "brand-teardown")
        self.assertEqual(parse_frontmatter_name("---\nname: 'brand-teardown'\n---\n"), "brand-teardown")
        self.assertEqual(parse_frontmatter_name("---\nname: brand-teardown-v2\n---\n"), "brand-teardown-v2")
        self.assertIsNone(parse_frontmatter_name("---\ndescription: name: brand-teardown\n---\n"))
        self.assertIsNone(parse_frontmatter_name("prose only: name: brand-teardown\n"))

    def test_missing_finding_rejected(self):
        self.assert_invalid(lambda d, _: d["findings"].pop(), "missing canonical teardown IDs")

    def test_dependency_type_mutation_fails_cleanly(self):
        self.assert_invalid(lambda d, _: d["findings"][1].__setitem__("dependencies", {}), "must be an array")

    def test_acceptance_nested_type_mutation_fails_cleanly(self):
        self.assert_invalid(lambda d, _: d["findings"][1].__setitem__("acceptance_results", [42]), "must be an object")

    def test_malformed_teardown_coverage_row_is_path_aware(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rd, _ = write_case(Path(temp))
            coverage = json.loads((td / "coverage.json").read_text(encoding="utf-8"))
            coverage["access"] = [42]
            (td / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
            errors = validate(td, rd, run_upstream=False, check_markdown=True)
            self.assertTrue(any("teardown.coverage.access[0] must be an object" in e for e in errors), errors)
            self.assertFalse(any("validator internal guard" in e for e in errors), errors)

    def test_renderer_rejects_malformed_json_and_wrong_shape(self):
        with tempfile.TemporaryDirectory() as temp:
            rd = Path(temp) / "brand-revision"
            rd.mkdir()
            path = rd / "revision.json"
            path.write_text("{not json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid JSON in revision artifact"):
                render_to_disk(rd)
            path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "revision.json missing required key"):
                render_to_disk(rd)

    def test_decision_required_cannot_be_approved_while_pending(self):
        def mutate(d, _):
            d["findings"][0]["approval"] = "approved"
        self.assert_invalid(mutate, "cannot be approved until its owner decision is resolved")

    def test_retained_strength_cannot_be_implemented_without_tradeoff(self):
        def mutate(d, _):
            d["findings"][2]["disposition"] = "implemented"
        self.assert_invalid(mutate, "must remain preserved")

    def test_acceptance_criterion_drift_rejected(self):
        def mutate(d, _):
            d["findings"][1]["acceptance_results"][0]["criterion"] = "Different criterion"
        self.assert_invalid(mutate, "acceptance criteria must exactly match teardown")

    def test_claim_omission_rejected(self):
        self.assert_invalid(lambda d, _: d["claim_trace"].pop(), "claim_trace missing canonical claim IDs")

    def test_revision_claim_verification_requires_fresh_claim_evidence(self):
        def mutate(d, _):
            d["claim_trace"][0]["verification_status"] = "verified"
        self.assert_invalid(mutate, "cannot be verified in the revision")

    def test_source_verified_claim_does_not_require_fresh_evidence_during_planning(self):
        # Regression for real Omaha bootstrap: upstream verified state is not itself a fresh revision verification claim.
        self.assertEqual(self.validate_data(), [])

    def test_open_material_limitation_cannot_disappear(self):
        self.assert_invalid(lambda d, _: d["coverage_trace"]["material_limitations"].clear(), "must account for every canonical teardown limitation")

    def test_open_material_limitation_cannot_be_resolved_without_evidence(self):
        def mutate(d, _):
            d["coverage_trace"]["material_limitations"][0]["disposition"] = "resolved"
        self.assert_invalid(mutate, "cannot be resolved without completed evidence")

    def test_planning_only_rejects_actual_change(self):
        def mutate(d, _):
            d["changes"] = [{
                "id": "CHG-001", "scope": "content", "finding_ids": ["FIND-002"], "convergence_ids": [],
                "targets": ["README.md"], "description": "Change copy.", "authority_ids": ["AUTH-CONTENT-EDIT"],
                "risk_level": "low", "risk_categories": ["claim"], "rollout_id": None, "evidence_ids": []
            }]
        self.assert_invalid(mutate, "planning-only revision must not contain actual changes")

    def test_change_requires_authorized_scope(self):
        def mutate(d, _):
            d["mode"] = "implementation"
            d["findings"][1]["approval"] = "approved"
            d["changes"] = [{
                "id": "CHG-001", "scope": "content", "finding_ids": ["FIND-002"], "convergence_ids": [],
                "targets": ["README.md"], "description": "Change copy.", "authority_ids": ["AUTH-CONTENT-EDIT"],
                "risk_level": "low", "risk_categories": ["claim"], "rollout_id": None, "evidence_ids": []
            }]
        self.assert_invalid(mutate, "requires authority AUTH-CONTENT-EDIT to be authorized")

    def test_high_risk_change_requires_rollout(self):
        def mutate(d, _):
            d["mode"] = "implementation"
            d["findings"][1]["approval"] = "approved"
            next(a for a in d["authority_matrix"] if a["id"] == "AUTH-CONTENT-EDIT")["state"] = "authorized"
            d["changes"] = [{
                "id": "CHG-001", "scope": "content", "finding_ids": ["FIND-002"], "convergence_ids": [],
                "targets": ["README.md"], "description": "High-risk public claim rewrite.", "authority_ids": ["AUTH-CONTENT-EDIT"],
                "risk_level": "high", "risk_categories": ["claim"], "rollout_id": None, "evidence_ids": []
            }]
        self.assert_invalid(mutate, "high-risk change CHG-001 requires a valid rollout_id")

    def test_activated_rollout_requires_direct_published_channel_evidence(self):
        def mutate(d, _):
            d["mode"] = "implementation"
            d["findings"][1]["approval"] = "approved"
            next(a for a in d["authority_matrix"] if a["id"] == "AUTH-CONTENT-EDIT")["state"] = "authorized"
            next(a for a in d["authority_matrix"] if a["id"] == "AUTH-PUBLISH")["state"] = "authorized"
            d["evidence"] = [{
                "id": "REV-EVID-001", "level": "business-outcome", "method": "business-record-analysis",
                "status": "completed", "observation": "Revenue record exists after the rollout.",
                "artifact_path": None, "limitations": [], "observed_at": "2026-08-30T00:00:00Z"
            }]
            d["changes"] = [{
                "id": "CHG-001", "scope": "content", "finding_ids": ["FIND-002"], "convergence_ids": [],
                "targets": ["README.md"], "description": "High-risk public claim rewrite.",
                "authority_ids": ["AUTH-CONTENT-EDIT"], "risk_level": "high", "risk_categories": ["claim"],
                "rollout_id": "ROLLOUT-001", "evidence_ids": []
            }]
            d["rollouts"] = [{
                "id": "ROLLOUT-001", "change_ids": ["CHG-001"], "state": "activated",
                "inventory": ["README.md"], "representative_samples": ["README.md"],
                "collision_checks": ["No conflicting public claim found."], "rollback_plan": "Revert CHG-001.",
                "authority_ids": ["AUTH-PUBLISH"], "evidence_ids": ["REV-EVID-001"]
            }]
        self.assert_invalid(mutate, "requires direct completed published-channel evidence")

    def test_completed_perception_test_requires_audience_observation(self):
        def mutate(d, _):
            d["perception_tests"] = [{
                "id": "PERCEPT-001", "finding_ids": ["FIND-004"], "dimensions": ["comprehension"], "status": "completed",
                "audience_segment": "CLI developers", "sample_source": "Convenience sample", "protocol": "Five-second comprehension prompt",
                "baseline": "No baseline available before change.", "result": "Participants understood the category.", "limitations": [], "evidence_ids": []
            }]
        self.assert_invalid(mutate, "requires audience-observation evidence")

    def test_business_outcome_observed_requires_business_evidence(self):
        def mutate(d, _):
            d["readiness"]["business_outcome"] = "observed"
        self.assert_invalid(mutate, "observed business_outcome requires completed business-outcome evidence")

    def test_markdown_drift_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rd, _ = write_case(Path(temp))
            (rd / "03-implementation-ledger.md").write_text("drift\n", encoding="utf-8")
            errors = validate(td, rd, run_upstream=False, check_markdown=True)
            self.assertTrue(any("generated Markdown drift" in e for e in errors), errors)

    def test_malformed_representative_nested_fields_never_crash(self):
        mutations = [
            lambda d: d["decisions"][0].__setitem__("options", {}),
            lambda d: d["authority_matrix"][0].__setitem__("evidence_ids", {}),
            lambda d: d["claim_trace"][0].__setitem__("finding_ids", 7),
            lambda d: d["coverage_trace"].__setitem__("surface_checks", {}),
            lambda d: d["readiness"].__setitem__("delivery", []),
        ]
        for index, mut in enumerate(mutations):
            with self.subTest(index=index):
                errors = self.validate_data(lambda d, _, mut=mut: mut(d))
                self.assertTrue(errors)
                self.assertFalse(any("validator internal guard" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()