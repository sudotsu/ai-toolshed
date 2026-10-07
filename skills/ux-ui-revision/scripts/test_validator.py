from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TD = HERE.parents[1] / "ux-ui-teardown" / "scripts"
sys.path.insert(0, str(TD))
spec = importlib.util.spec_from_file_location("td_fixture", TD / "test_validator.py")
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
write_fixture = fixture_module.write_fixture
sys.path.insert(0, str(HERE))

import bootstrap_revision
import render_revision
from validate_ux_ui_revision import validate


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def bootstrap(td: Path, rv: Path):
    old = sys.argv[:]
    sys.argv = ["bootstrap_revision.py", str(td), str(rv)]
    try:
        return bootstrap_revision.main()
    finally:
        sys.argv = old


def pair(base: Path):
    td = base / "td"
    rv = base / "rv"
    td.mkdir()
    write_fixture(td)
    assert bootstrap(td, rv) == 0
    return td, rv


def make_source_gap(td: Path, rv: Path):
    findings = read_json(td / "findings.json")
    source = findings["findings"][0]
    source.update({"kind": "gap", "status": "open", "severity": "medium", "recommendation": "fix"})
    write_json(td / "findings.json", findings)
    shutil.rmtree(rv)
    assert bootstrap(td, rv) == 0


class Tests(unittest.TestCase):
    def test_bootstrap_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            self.assertEqual(validate(td, rv), [])

    def test_invalid_upstream_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            coverage = read_json(td / "coverage.json")
            coverage["review_status"] = "bogus"
            write_json(td / "coverage.json", coverage)
            self.assertTrue(any("upstream validation failed" in error for error in validate(td, rv)))

    def test_fixed_requires_every_acceptance_criterion(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            make_source_gap(td, rv)
            data = read_json(rv / "revision.json")
            row = data["findings"][0]
            row.update({
                "revalidation": "confirmed",
                "current_evidence": ["current"],
                "implementation_status": "fixed",
                "approval": "approved",
                "verification_evidence": [{"ref": "rendered", "level": "rendered_experience"}],
                "acceptance_results": [],
                "preservation_status": "not_applicable",
            })
            data["mode"] = "implementation"
            write_json(rv / "revision.json", data)
            self.assertTrue(any("exactly once" in error for error in validate(td, rv)))

    def test_fixed_experiential_finding_requires_rendered_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            make_source_gap(td, rv)
            data = read_json(rv / "revision.json")
            row = data["findings"][0]
            row.update({
                "revalidation": "confirmed",
                "current_evidence": ["source-current"],
                "implementation_status": "fixed",
                "approval": "approved",
                "preservation_status": "not_applicable",
                "verification_evidence": [{"ref": "source-diff", "level": "source_inspection"}],
            })
            row["acceptance_results"][0].update({"status": "passed", "evidence": ["source-diff"]})
            data["mode"] = "implementation"
            write_json(rv / "revision.json", data)
            self.assertTrue(any("rendered_experience-or-higher" in error for error in validate(td, rv)))

    def test_fixed_experiential_finding_accepts_linked_rendered_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            make_source_gap(td, rv)
            data = read_json(rv / "revision.json")
            row = data["findings"][0]
            row.update({
                "revalidation": "confirmed",
                "current_evidence": ["rendered-current"],
                "implementation_status": "fixed",
                "approval": "approved",
                "preservation_status": "not_applicable",
                "verification_evidence": [{"ref": "rendered-check", "level": "rendered_experience", "locator": "browser://flow"}],
            })
            row["acceptance_results"][0].update({"status": "passed", "evidence": ["rendered-check"]})
            data["mode"] = "implementation"
            write_json(rv / "revision.json", data)
            errors = validate(td, rv)
            self.assertFalse(any("fixed experiential" in error for error in errors))
            self.assertFalse(any("unknown verification evidence" in error for error in errors))

    def test_planning_only_forbids_implementation_claims(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            data = read_json(rv / "revision.json")
            data["findings"][0]["implementation_status"] = "fixed"
            write_json(rv / "revision.json", data)
            self.assertTrue(any("planning-only cannot claim implementation work" in error for error in validate(td, rv)))

    def test_planning_only_forbids_authorized_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            data = read_json(rv / "revision.json")
            next(row for row in data["authority"] if row["action"] == "repository_edit")["status"] = "authorized"
            write_json(rv / "revision.json", data)
            self.assertTrue(any("planning-only cannot authorize" in error for error in validate(td, rv)))

    def test_accepted_risk_requires_matching_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            data = read_json(rv / "revision.json")
            row = data["findings"][0]
            row["implementation_status"] = "accepted_risk"
            row["approval"] = "pending"
            write_json(rv / "revision.json", data)
            self.assertTrue(any("accepted_risk requires" in error for error in validate(td, rv)))

    def test_strength_approved_tradeoff_is_allowed(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            data = read_json(rv / "revision.json")
            row = data["findings"][0]
            row["implementation_status"] = "planned"
            row["preservation_status"] = "approved_tradeoff"
            row["approval"] = "approved"
            write_json(rv / "revision.json", data)
            errors = validate(td, rv)
            self.assertFalse(any("retained strength" in error for error in errors))

    def test_decision_required_needs_linked_decision(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            findings = read_json(td / "findings.json")
            source = findings["findings"][0]
            source.update({"kind": "gap", "status": "decision_required", "severity": "medium", "recommendation": "choose"})
            write_json(td / "findings.json", findings)
            shutil.rmtree(rv)
            self.assertEqual(bootstrap(td, rv), 0)
            self.assertTrue(any("needs linked decision" in error for error in validate(td, rv)))

    def test_resolved_decision_requires_owner_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            data = read_json(rv / "revision.json")
            data["decisions"] = [{
                "id": "DEC-001",
                "finding_ids": ["UXUI-001"],
                "question": "Choose?",
                "options": ["a", "b"],
                "recommendation": "a",
                "status": "resolved",
                "owner_evidence": [],
            }]
            write_json(rv / "revision.json", data)
            self.assertTrue(any("resolved requires owner evidence" in error for error in validate(td, rv)))

    def test_ready_material_pending_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            make_source_gap(td, rv)
            data = read_json(rv / "revision.json")
            row = data["findings"][0]
            row["revalidation"] = "confirmed"
            row["current_evidence"] = ["x"]
            row["implementation_status"] = "rejected"
            row["preservation_status"] = "not_applicable"
            data["mode"] = "implementation"
            data["readiness"]["implementation"] = "ready"
            data["readiness"]["integration"] = "ready"
            data["readiness"]["overall"] = "ready"
            write_json(rv / "revision.json", data)
            self.assertTrue(any("terminal disposition" in error for error in validate(td, rv)))

    def test_ready_rejects_blocked_revalidation(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            data = read_json(rv / "revision.json")
            row = data["findings"][0]
            row["implementation_status"] = "preserved"
            row["preservation_status"] = "preserved"
            data["readiness"]["implementation"] = "ready"
            data["readiness"]["integration"] = "ready"
            data["readiness"]["overall"] = "ready"
            write_json(rv / "revision.json", data)
            self.assertTrue(any("unrevalidated finding" in error for error in validate(td, rv)))

    def test_unknown_finding_ready_returns_error_not_traceback(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            data = read_json(rv / "revision.json")
            unknown = dict(data["findings"][0])
            unknown["finding_id"] = "UXUI-999"
            data["findings"].append(unknown)
            data["readiness"]["implementation"] = "ready"
            data["readiness"]["integration"] = "ready"
            data["readiness"]["overall"] = "ready"
            write_json(rv / "revision.json", data)
            errors = validate(td, rv)
            self.assertTrue(any("unknown finding UXUI-999" in error for error in errors))

    def test_deploy_requires_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            data = read_json(rv / "revision.json")
            data["readiness"]["deployment"] = "performed"
            write_json(rv / "revision.json", data)
            self.assertTrue(any("deployment performed" in error for error in validate(td, rv)))

    def test_digest_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            findings = read_json(td / "findings.json")
            findings["audit"]["project_name"] = "changed"
            write_json(td / "findings.json", findings)
            self.assertTrue(any("digest mismatch" in error for error in validate(td, rv, run_upstream=False)))

    def test_renderer_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = pair(Path(temp))
            self.assertEqual(render_revision.render(rv), render_revision.render(rv))


if __name__ == "__main__":
    unittest.main()
