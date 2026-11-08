from __future__ import annotations

import json
import copy
import tempfile
import unittest
import subprocess
import sys
from pathlib import Path

import render_handoff
from validate_ux_ui_teardown import validate


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def write_fixture(root: Path, complete=True):
    evidence = [
        {"id": "EVID-001", "evidence_class": "rendered_observation", "title": "rendered", "locator": "prod", "accessed_at": "2026-10-06", "summary": "observed UI", "limitations": []},
        {"id": "EVID-002", "evidence_class": "competitor_measurement", "title": "measurement A", "locator": "source-a", "accessed_at": "2026-10-06", "summary": "measured competitor A", "limitations": []},
        {"id": "EVID-003", "evidence_class": "competitor_measurement", "title": "measurement B", "locator": "source-b", "accessed_at": "2026-10-06", "summary": "measured competitor B", "limitations": []},
        {"id": "EVID-004", "evidence_class": "competitor_observation", "title": "comparison", "locator": "competitors", "accessed_at": "2026-10-06", "summary": "compared equivalent surfaces", "limitations": []},
    ]
    findings = {
        "schema_version": "ux-ui-teardown-v2",
        "audit": {
            "project_name": "Fixture",
            "project_locator": "repo",
            "audited_revision": "abc",
            "production_locator": "https://example.test",
            "production_revision_status": "verified",
            "audit_start_date": "2026-10-06",
            "audit_end_date": "2026-10-06",
            "review_status": "complete" if complete else "provisional",
            "project_type": "website",
            "audience_scope": "global",
            "primary_user_groups": ["buyer"],
            "primary_goals": ["complete task"],
            "owner_context": ["high consideration"],
            "competitor_benchmark_required": True,
            "competitor_benchmark_reason": "public commercial product",
        },
        "evidence_sources": evidence,
        "competitor_set": [
            {"id": "COMP-001", "name": "A", "locator": "a", "selection_status": "measured", "selection_evidence_ids": ["EVID-002"], "comparison_evidence_ids": ["EVID-004"], "relevance_reason": "measured leader", "surfaces_compared": ["home"], "limitations": []},
            {"id": "COMP-002", "name": "B", "locator": "b", "selection_status": "measured", "selection_evidence_ids": ["EVID-003"], "comparison_evidence_ids": ["EVID-004"], "relevance_reason": "measured leader", "surfaces_compared": ["home"], "limitations": []},
        ],
        "journeys": [
            {"id": "JOURNEY-001", "title": "primary", "user_group": "buyer", "trigger": "arrives", "intended_outcome": "finish", "criticality": "primary", "steps": ["start", "finish"], "effort_budget": "contextual", "engagement_intent": "help user choose", "expected_payoff": "relevant result", "context_notes": "guided flow appropriate", "viewport_ids": ["VIEW-001", "VIEW-002"], "input_modes": ["pointer_touch", "keyboard"], "state_ids": ["STATE-001"], "evidence_ids": ["EVID-001"], "status": "passed", "limitations": []}
        ],
        "experience_assessments": [
            {"id": "EXP-001", "journey_ids": ["JOURNEY-001"], "surface_target": "home", "axis": "visual_craft", "verdict": "strong", "confidence": "high", "evidence_ids": ["EVID-001"], "competitor_ids": [], "observation": "coherent hierarchy", "reasoning": "spacing and composition are consistent", "desired_direction": "preserve"},
            {"id": "EXP-002", "journey_ids": ["JOURNEY-001"], "surface_target": "home", "axis": "color_system", "verdict": "strong", "confidence": "high", "evidence_ids": ["EVID-001"], "competitor_ids": [], "observation": "coherent palette", "reasoning": "surface and CTA colors have clear roles", "desired_direction": "preserve"},
            {"id": "EXP-003", "journey_ids": ["JOURNEY-001"], "surface_target": "home", "axis": "audience_fit", "verdict": "appropriate", "confidence": "medium", "evidence_ids": ["EVID-001"], "competitor_ids": [], "observation": "appropriate for audience", "reasoning": "tone and scope fit target", "desired_direction": "preserve"},
            {"id": "EXP-004", "journey_ids": ["JOURNEY-001"], "surface_target": "flow", "axis": "engagement_quality", "verdict": "productive", "confidence": "high", "evidence_ids": ["EVID-001", "EVID-004"], "competitor_ids": ["COMP-001", "COMP-002"], "observation": "effort produces relevance", "reasoning": "choices narrow later information", "desired_direction": "preserve"},
        ],
        "findings": [
            {"id": "UXUI-001", "title": "Retain guided relevance", "kind": "strength", "domains": ["ux.engagement"], "status": "retained_strength", "severity": "informational", "confidence": "high", "verification_state": "observed", "judgment_basis": "observed_behavior", "standard_refs": [], "journey_ids": ["JOURNEY-001"], "surface_targets": ["flow"], "evidence_ids": ["EVID-001"], "competitor_ids": [], "observed_condition": "choices narrow later content", "desired_condition": "preserve useful participation", "user_consequence": "less irrelevant information", "business_risk": "losing specificity would weaken experience", "recommendation": "", "acceptance_criteria": ["guided choices continue to affect later content"], "verification_methods": ["rerun flow"], "implementation_targets": [], "preservation_constraints": ["do not flatten into generic form"], "dependencies": [], "conflicts": [], "non_goals": []}
        ],
    }
    coverage = {
        "schema_version": "ux-ui-teardown-coverage-v2",
        "review_status": findings["audit"]["review_status"],
        "access": [
            {"category": category, "status": "available" if category in {"production_experience", "competitor_measurement"} else "not_applicable", "material_to_complete": category in {"production_experience", "competitor_measurement"}, "evidence_ids": ["EVID-001"] if category == "production_experience" else (["EVID-002", "EVID-003"] if category == "competitor_measurement" else []), "limitations": [], "next_step": "none"}
            for category in ["source_repository", "production_experience", "competitor_measurement", "user_sentiment", "design_system", "assistive_technology"]
        ],
        "passes": [
            {"id": "ui_craft", "materiality": "defining", "status": "passed", "finding_ids": ["UXUI-001"], "evidence_ids": ["EVID-001"], "limitations": []},
            {"id": "ux_experience", "materiality": "defining", "status": "passed", "finding_ids": ["UXUI-001"], "evidence_ids": ["EVID-001"], "limitations": []},
            {"id": "competitive_calibration", "materiality": "high", "status": "passed", "finding_ids": [], "evidence_ids": ["EVID-002", "EVID-003", "EVID-004"], "limitations": []},
            {"id": "accessibility_readability", "materiality": "supporting", "status": "passed", "finding_ids": [], "evidence_ids": ["EVID-001"], "limitations": []},
        ],
        "viewports": [
            {"id": "VIEW-001", "label": "mobile", "width": 390, "height": 844, "class": "narrow_mobile", "status": "observed", "journey_ids": ["JOURNEY-001"], "evidence_ids": ["EVID-001"], "limitations": []},
            {"id": "VIEW-002", "label": "desktop", "width": 1440, "height": 1000, "class": "desktop", "status": "observed", "journey_ids": ["JOURNEY-001"], "evidence_ids": ["EVID-001"], "limitations": []},
        ],
        "input_modes": [
            {"mode": "pointer_touch", "status": "observed", "journey_ids": ["JOURNEY-001"], "evidence_ids": ["EVID-001"], "limitations": []},
            {"mode": "keyboard", "status": "observed", "journey_ids": ["JOURNEY-001"], "evidence_ids": ["EVID-001"], "limitations": []},
            {"mode": "screen_reader", "status": "not_applicable", "journey_ids": [], "evidence_ids": [], "limitations": []},
            {"mode": "other", "status": "not_applicable", "journey_ids": [], "evidence_ids": [], "limitations": []},
        ],
        "state_coverage": [
            {"id": "STATE-001", "state": "default", "label": "default", "journey_id": "JOURNEY-001", "step": "start", "surface_target": "flow", "trigger": "load", "status": "observed", "viewport_ids": ["VIEW-001", "VIEW-002"], "input_modes": ["pointer_touch", "keyboard"], "evidence_ids": ["EVID-001"], "finding_ids": ["UXUI-001"], "limitations": []}
        ],
        "material_limitations": [],
        "validator": {"name": "validate_ux_ui_teardown.py", "status": "passed", "validated_at": "2026-10-06"},
    }
    write_json(root / "findings.json", findings)
    write_json(root / "coverage.json", coverage)


class Tests(unittest.TestCase):
    def test_bootstrap_creates_valid_provisional_handoff(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "handoff"
            command = [
                sys.executable, str(Path(__file__).parent / "bootstrap_teardown.py"), str(output),
                "--project-name", "Test app", "--project-locator", "repo",
                "--audited-revision", "abc", "--project-type", "web_app",
                "--audience-scope", "internal", "--primary-user", "operator",
                "--primary-goal", "complete task",
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(validate(output), [])
            self.assertEqual(read_json(output / "findings.json")["audit"]["review_status"], "provisional")
            self.assertEqual(read_json(output / "coverage.json")["material_limitations"][0]["status"], "open")
            repeated = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertNotEqual(repeated.returncode, 0)

    def pair(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        write_fixture(root)
        return temp, root

    def test_valid_complete(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        self.assertEqual(validate(root), [])

    def test_complete_visual_conclusions_need_their_own_rendered_evidence(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        data = read_json(root / "findings.json")
        data["evidence_sources"].append({
            "id": "EVID-005", "evidence_class": "source_inspection", "title": "source",
            "locator": "repo", "accessed_at": "2026-10-08", "summary": "CSS source only",
            "limitations": [],
        })
        data["experience_assessments"][0]["evidence_ids"] = ["EVID-005"]
        data["findings"][0]["domains"] = ["ui.visual-craft"]
        data["findings"][0]["evidence_ids"] = ["EVID-005"]
        write_json(root / "findings.json", data)
        errors = validate(root)
        self.assertTrue(any("EXP-001 visual conclusion" in error for error in errors))
        self.assertTrue(any("UXUI-001 visual finding" in error for error in errors))

    def test_string_fields_reject_unhashable_values_without_crashing(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)

        def string_paths(node, path=()):
            if isinstance(node, dict):
                for key, value in node.items():
                    if isinstance(value, str):
                        yield path + (key,)
                    elif isinstance(value, (dict, list)):
                        yield from string_paths(value, path + (key,))
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    yield from string_paths(value, path + (index,))

        for name in ("findings.json", "coverage.json"):
            path = root / name
            original = read_json(path)
            for field_path in string_paths(original):
                mutated = copy.deepcopy(original)
                container = mutated
                for part in field_path[:-1]:
                    container = container[part]
                container[field_path[-1]] = []
                write_json(path, mutated)
                with self.subTest(file=name, field=field_path):
                    self.assertTrue(validate(root))
            write_json(path, original)

    def test_complete_requires_measured_competitors(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        data = read_json(root / "findings.json")
        data["competitor_set"][0]["selection_status"] = "owner_supplied"
        data["competitor_set"][1]["selection_status"] = "owner_supplied"
        write_json(root / "findings.json", data)
        self.assertTrue(any("at least two measured" in error for error in validate(root)))

    def test_complete_requires_actual_competitor_observation(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        data = read_json(root / "findings.json")
        for competitor in data["competitor_set"]:
            competitor["comparison_evidence_ids"] = []
        data["experience_assessments"][3]["evidence_ids"] = ["EVID-001"]
        write_json(root / "findings.json", data)
        errors = validate(root)
        self.assertTrue(any("competitor_observation evidence for COMP-001" in error for error in errors))
        self.assertTrue(any("comparative assessment citing actual competitor_observation" in error for error in errors))

    def test_global_mobile_does_not_cover_primary_journey(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        coverage = read_json(root / "coverage.json")
        coverage["viewports"][0]["journey_ids"] = []
        write_json(root / "coverage.json", coverage)
        self.assertTrue(any("not reciprocal" in error or "missing viewports" in error for error in validate(root)))

    def test_dangling_journey_coverage_references_fail(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        data = read_json(root / "findings.json")
        journey = data["journeys"][0]
        journey["viewport_ids"] = ["VIEW-999"]
        journey["state_ids"] = ["STATE-999"]
        journey["input_modes"] = ["bogus"]
        write_json(root / "findings.json", data)
        errors = validate(root)
        self.assertTrue(any("VIEW-999" in error for error in errors))
        self.assertTrue(any("STATE-999" in error for error in errors))
        self.assertTrue(any("unsupported mode bogus" in error for error in errors))

    def test_material_access_blocks_complete(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        coverage = read_json(root / "coverage.json")
        next(row for row in coverage["access"] if row["category"] == "competitor_measurement")["status"] = "partial"
        write_json(root / "coverage.json", coverage)
        self.assertTrue(any("material access" in error for error in validate(root)))

    def test_aesthetic_preference_cannot_be_high(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        data = read_json(root / "findings.json")
        finding = data["findings"][0]
        finding.update({"kind": "gap", "status": "open", "severity": "high", "judgment_basis": "aesthetic_preference", "recommendation": "change"})
        write_json(root / "findings.json", data)
        self.assertTrue(any("aesthetic_preference" in error for error in validate(root)))

    def test_visual_craft_alone_not_critical(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        data = read_json(root / "findings.json")
        finding = data["findings"][0]
        finding.update({"kind": "gap", "status": "open", "severity": "critical", "judgment_basis": "visual_craft", "recommendation": "fix"})
        write_json(root / "findings.json", data)
        self.assertTrue(any("visual_craft alone" in error for error in validate(root)))

    def test_malformed_lists_return_errors_not_traceback(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        coverage = read_json(root / "coverage.json")
        coverage["viewports"][0]["journey_ids"] = 5
        write_json(root / "coverage.json", coverage)
        self.assertTrue(validate(root))

    def test_unhashable_values_return_errors_not_traceback(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        data = read_json(root / "findings.json")
        coverage = read_json(root / "coverage.json")
        data["evidence_sources"][0]["evidence_class"] = ["rendered_observation"]
        data["experience_assessments"][0]["axis"] = ["visual_craft"]
        coverage["access"][0]["category"] = {"bad": "value"}
        coverage["passes"][0]["id"] = ["ui_craft"]
        coverage["input_modes"][0]["mode"] = {"bad": "value"}
        write_json(root / "findings.json", data)
        write_json(root / "coverage.json", coverage)
        errors = validate(root)
        self.assertTrue(errors)
        self.assertTrue(any("evidence_class invalid" in error for error in errors))
        self.assertTrue(any("axis invalid" in error for error in errors))
        self.assertTrue(any("category invalid" in error for error in errors))
        self.assertTrue(any("id invalid" in error for error in errors))
        self.assertTrue(any("mode invalid" in error for error in errors))

    def test_unhashable_state_journey_id_returns_error_not_traceback(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        coverage = read_json(root / "coverage.json")
        coverage["state_coverage"][0]["journey_id"] = []
        write_json(root / "coverage.json", coverage)
        errors = validate(root)
        self.assertTrue(any("STATE-001.journey_id invalid" in error for error in errors))

    def test_mixed_acceptance_criteria_is_rejected(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        data = read_json(root / "findings.json")
        data["findings"][0]["acceptance_criteria"] = ["valid", ["nested"]]
        write_json(root / "findings.json", data)
        errors = validate(root)
        self.assertTrue(any("UXUI-001.acceptance_criteria must be non-empty string list" in error for error in errors))

    def test_screen_reader_not_required_for_complete(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        self.assertEqual(validate(root), [])

    def test_renderer_deterministic(self):
        temp, root = self.pair()
        self.addCleanup(temp.cleanup)
        self.assertEqual(render_handoff.render(root), render_handoff.render(root))


if __name__ == "__main__":
    unittest.main()
