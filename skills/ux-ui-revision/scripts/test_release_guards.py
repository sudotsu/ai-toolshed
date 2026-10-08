from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import test_validator as base
from validate_ux_ui_revision import digest, validate


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def make_fixed_gap(td: Path, rv: Path):
    base.make_source_gap(td, rv)
    data = base.read_json(rv / "revision.json")
    row = data["findings"][0]
    row.update({
        "revalidation": "confirmed",
        "current_evidence": ["current"],
        "implementation_status": "fixed",
        "approval": "approved",
        "preservation_status": "not_applicable",
        "verification_evidence": [
            {"ref": "rendered-check", "level": "rendered_experience", "timing": "post_change"}
        ],
    })
    row["acceptance_results"][0].update({"status": "passed", "evidence": ["rendered-check"]})
    data["mode"] = "implementation"
    return data, row


class FinalReleaseGuards(unittest.TestCase):
    def test_bootstrap_includes_target_action_map(self):
        with tempfile.TemporaryDirectory() as temp:
            _td, rv = base.pair(Path(temp))
            data = base.read_json(rv / "revision.json")
            self.assertEqual(data["findings"][0]["changed_target_actions"], {})

    def test_changed_target_requires_its_mapped_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = base.pair(Path(temp))
            data, row = make_fixed_gap(td, rv)
            row["changed_targets"] = ["src/flow.tsx"]
            row["changed_target_actions"] = {"src/flow.tsx": "cms_edit"}
            base.authorize_repository_edit(data)
            write_json(rv / "revision.json", data)
            errors = validate(td, rv)
            self.assertTrue(any("requires authorized cms_edit" in error for error in errors))

    def test_changed_target_action_keys_must_match_targets(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = base.pair(Path(temp))
            data, row = make_fixed_gap(td, rv)
            row["changed_targets"] = ["src/flow.tsx"]
            row["changed_target_actions"] = {}
            base.authorize_repository_edit(data)
            write_json(rv / "revision.json", data)
            errors = validate(td, rv)
            self.assertTrue(any("map every changed target exactly once" in error for error in errors))

    def test_behavioral_finding_requires_new_post_change_behavior_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = base.pair(Path(temp))
            base.make_source_gap(td, rv)

            findings = base.read_json(td / "findings.json")
            findings["findings"][0]["judgment_basis"] = "first_party_measurement"
            write_json(td / "findings.json", findings)

            data = base.read_json(rv / "revision.json")
            data["source"]["teardown_findings_digest"] = digest(td / "findings.json")
            data["mode"] = "implementation"
            row = data["findings"][0]
            row.update({
                "revalidation": "confirmed",
                "current_evidence": ["current"],
                "implementation_status": "fixed",
                "approval": "approved",
                "preservation_status": "not_applicable",
                "verification_evidence": [
                    {"ref": "measurement", "level": "first_party_measurement"}
                ],
            })
            row["acceptance_results"][0].update({"status": "passed", "evidence": ["measurement"]})
            base.authorize_repository_edit(data)
            write_json(rv / "revision.json", data)

            errors = validate(td, rv, run_upstream=False)
            self.assertTrue(any("post-change acceptance-linked behavioral evidence" in error for error in errors))

            row["verification_evidence"][0]["timing"] = "post_change"
            write_json(rv / "revision.json", data)
            errors = validate(td, rv, run_upstream=False)
            self.assertFalse(any("post-change acceptance-linked behavioral evidence" in error for error in errors))

    def test_ready_requires_current_convergence_review(self):
        with tempfile.TemporaryDirectory() as temp:
            td, rv = base.pair(Path(temp))
            data = base.read_json(rv / "revision.json")
            row = data["findings"][0]
            row["revalidation"] = "confirmed"
            row["current_evidence"] = ["current"]
            row["preservation_status"] = "preserved"
            data["baseline"]["current_revision"] = "rev-current"
            data["readiness"]["implementation"] = "ready"
            data["readiness"]["integration"] = "ready"
            data["readiness"]["overall"] = "ready"
            write_json(rv / "revision.json", data)

            errors = validate(td, rv)
            self.assertTrue(any("requires convergence.status converged" in error for error in errors))

            data["convergence"]["status"] = "converged"
            data["convergence"]["reviewed_revision"] = "rev-old"
            write_json(rv / "revision.json", data)
            errors = validate(td, rv)
            self.assertTrue(any("reviewed_revision is stale" in error for error in errors))

            data["convergence"]["reviewed_revision"] = "rev-current"
            write_json(rv / "revision.json", data)
            errors = validate(td, rv)
            self.assertFalse(any("convergence" in error and "ready" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
