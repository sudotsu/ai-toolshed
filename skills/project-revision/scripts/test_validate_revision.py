#!/usr/bin/env python3
"""Focused regression tests for validate_revision.py."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_revision import validate


class RevisionValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.teardown = self.root / "project-teardown"
        self.revision = self.root / "project-revision"
        self.teardown.mkdir()
        self.revision.mkdir()
        (self.teardown / "findings.json").write_text(json.dumps({
            "project": "owner/project",
            "audited_revision": "base-sha",
            "findings": [{
                "id": "TECH-001",
                "title": "Repair behavior",
                "type": "defect",
                "action": "fix",
                "dependencies": [],
            }],
        }), encoding="utf-8")
        self.payload = {
            "schema_version": 2,
            "project": "owner/project",
            "teardown_path": "project-teardown",
            "teardown_audited_revision": "base-sha",
            "implementation_start_revision": "base-sha",
            "implementation_end_revision": "product-sha",
            "revision_status": "complete",
            "generated_at": "2026-07-13T12:00:00Z",
            "existing_work_reconciled": True,
            "findings": [{
                "id": "TECH-001",
                "approval": "approved",
                "revalidation": "confirmed",
                "disposition": "implemented",
                "sequence": 1,
                "reason": "Current reproduction confirmed the defect.",
                "files_changed": ["src/example.ts"],
                "acceptance_results": [{
                    "criterion": "Behavior succeeds",
                    "status": "passed",
                    "evidence": "Focused regression passed.",
                }],
                "verification": ["unit test passed"],
                "notes": [],
            }],
            "convergence_findings": [{
                "id": "REV-001",
                "title": "Follow-up regression",
                "source": "manual full-diff review",
                "severity": "medium",
                "status": "fixed",
                "reason": "The implementation introduced an edge-case failure.",
                "files_changed": ["src/example.ts", "src/example.test.ts"],
                "verification": ["failure-path regression passed"],
            }],
            "final_state": {
                "artifact_relationship": "artifact-only-descendant",
                "review_convergence": "passed",
                "blocking_convergence_findings": 0,
                "merge_readiness": "ready",
                "release_readiness": "ready",
                "delivery": {
                    "committed": "verified",
                    "pushed": "verified",
                    "pull_request_updated": "verified",
                    "merged": "not-performed",
                },
            },
        }
        self._write_fixture(self.payload)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _handoff(self, payload: dict) -> str:
        state = payload["final_state"]
        delivery = state["delivery"]
        return "\n".join([
            f"**Revision status:** {payload['revision_status']}",
            f"**Implementation endpoint:** {payload['implementation_end_revision']}",
            f"**Artifact relationship:** {state['artifact_relationship']}",
            f"**Review convergence:** {state['review_convergence']}",
            f"**Blocking convergence findings:** {state['blocking_convergence_findings']}",
            f"**Merge readiness:** {state['merge_readiness']}",
            f"**Release readiness:** {state['release_readiness']}",
            f"**Committed:** {delivery['committed']}",
            f"**Pushed:** {delivery['pushed']}",
            f"**Pull request updated:** {delivery['pull_request_updated']}",
            f"**Merged:** {delivery['merged']}",
            "",
            "All required checks passed.",
        ])

    def _write_fixture(self, payload: dict, handoff: str | None = None) -> None:
        for name in (
            "00-decisions-and-scope.md",
            "01-baseline-and-revalidation.md",
            "02-execution-plan.md",
        ):
            (self.revision / name).write_text(f"# {name}\n", encoding="utf-8")
        (self.revision / "03-implementation-ledger.md").write_text(
            "# Implementation ledger\n\n"
            "## TECH-001 — Repair behavior\n\nImplemented.\n\n"
            "# Convergence findings\n\n"
            "### REV-001 — Follow-up regression\n\nFixed.\n",
            encoding="utf-8",
        )
        (self.revision / "04-verification-and-handoff.md").write_text(
            handoff if handoff is not None else self._handoff(payload),
            encoding="utf-8",
        )
        (self.revision / "revision.json").write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_valid_schema_two_artifact_passes(self) -> None:
        self.assertEqual(validate(self.teardown, self.revision), [])

    def test_blocking_review_finding_prevents_passed_convergence_and_readiness(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["revision_status"] = "partial"
        finding = payload["convergence_findings"][0]
        finding["status"] = "open"
        finding["files_changed"] = []
        payload["final_state"]["blocking_convergence_findings"] = 1
        payload["final_state"]["release_readiness"] = "not-ready"
        self._write_fixture(payload)
        errors = validate(self.teardown, self.revision)
        self.assertTrue(any("review convergence cannot pass" in error for error in errors))
        self.assertTrue(any("merge readiness requires" in error for error in errors))

    def test_computed_blocking_count_must_match_declared_count(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["convergence_findings"][0]["status"] = "blocked"
        payload["convergence_findings"][0]["files_changed"] = []
        self._write_fixture(payload)
        errors = validate(self.teardown, self.revision)
        self.assertTrue(any("computed count is 1" in error for error in errors))

    def test_handoff_markers_must_match_json(self) -> None:
        handoff = self._handoff(self.payload).replace(
            "**Implementation endpoint:** product-sha",
            "**Implementation endpoint:** stale-sha",
        )
        self._write_fixture(self.payload, handoff)
        errors = validate(self.teardown, self.revision)
        self.assertIn("handoff Implementation endpoint differs from revision.json", errors)

    def test_schema_one_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["schema_version"] = 1
        self._write_fixture(payload)
        self.assertIn("revision.json schema_version must be 2", validate(self.teardown, self.revision))

    def test_merge_readiness_requires_reconciled_existing_work(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["revision_status"] = "partial"
        payload["existing_work_reconciled"] = False
        payload["final_state"]["release_readiness"] = "not-ready"
        self._write_fixture(payload)
        self.assertIn(
            "merge readiness requires existing_work_reconciled true",
            validate(self.teardown, self.revision),
        )

    def test_artifact_descendant_requires_verified_commit(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["final_state"]["delivery"]["committed"] = "unverified"
        payload["final_state"]["delivery"]["pushed"] = "unverified"
        payload["final_state"]["delivery"]["pull_request_updated"] = "unverified"
        self._write_fixture(payload)
        self.assertIn(
            "artifact-only-descendant requires a verified committed product endpoint",
            validate(self.teardown, self.revision),
        )


if __name__ == "__main__":
    unittest.main()
