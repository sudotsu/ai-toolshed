#!/usr/bin/env python3
"""Regression tests for validate_revision.py."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from render_revision_views import render_implementation_ledger, render_readme
from validation_common import canonical_digest
from validate_revision import validate


def teardown_finding(fid: str, title: str, *, kind: str = "defect", action: str = "fix", status: str = "open", deps=None):
    return {
        "id": fid,
        "title": title,
        "type": kind,
        "category": "reliability",
        "severity": "high" if kind != "strength" else "informational",
        "confidence": "confirmed",
        "status": status,
        "impact": "Impact",
        "evidence": [{"source": "src/example.ts:1", "observation": "Observed"}],
        "expected_behavior": "Expected",
        "actual_behavior": "Actual",
        "root_cause": "Cause",
        "affected_components": [f"src/{fid.lower()}.ts"],
        "recommendation": "Recommendation",
        "if_implemented": "Benefit",
        "if_unchanged": "Consequence",
        "dependencies": list(deps or []),
        "dependents": [],
        "conflicts": [],
        "acceptance_criteria": [f"{fid} criterion one", f"{fid} criterion two"],
        "verification": f"Verify {fid}",
        "estimated_scope": "small",
        "regression_risk": "medium",
        "action": action,
        "strategic_classification": ["release-gate"],
    }


def build_teardown() -> dict:
    items = [
        teardown_finding("TECH-001", "Repair behavior"),
        teardown_finding("PROD-001", "Choose product boundary", status="decision-required", deps=["TECH-001"]),
        teardown_finding("REL-001", "Verify external runtime", status="blocked", kind="investigation", action="investigate"),
        teardown_finding("STRENGTH-001", "Preserve clear workflow", status="retained", kind="strength", action="retain"),
    ]
    items[0]["dependents"] = ["PROD-001"]
    return {
        "schema_version": 2,
        "project": "owner/project",
        "audited_revision": "abc123",
        "review_status": "complete",
        "core_workflows_fully_exercised": True,
        "generated_at": "2026-07-17T12:00:00-05:00",
        "findings": items,
    }


def results_for(item: dict, status: str = "passed") -> list[dict]:
    return [
        {"criterion": criterion, "status": status, "evidence": f"Evidence for {criterion}"}
        for criterion in item["acceptance_criteria"]
    ]


def build_revision(teardown: dict) -> dict:
    by_id = {item["id"]: item for item in teardown["findings"]}
    records = [
        {
            "id": "TECH-001", "approval": "approved", "revalidation": "confirmed",
            "disposition": "implemented", "sequence": 1, "reason": "Confirmed and approved.",
            "files_changed": ["src/tech.ts"], "acceptance_results": results_for(by_id["TECH-001"]),
            "verification": ["Focused test passed", "Defining workflow passed"], "notes": [],
        },
        {
            "id": "PROD-001", "approval": "deferred", "revalidation": "confirmed",
            "disposition": "deferred", "sequence": 2, "reason": "Owner decision remains deferred.",
            "files_changed": [], "acceptance_results": [], "verification": [],
            "notes": ["No product behavior changed."],
        },
        {
            "id": "REL-001", "approval": "approved", "revalidation": "blocked",
            "disposition": "blocked", "sequence": 3, "reason": "Required external environment is unavailable.",
            "files_changed": [], "acceptance_results": results_for(by_id["REL-001"], "blocked"),
            "verification": ["Fail-safe behavior verified; positive environment check remains blocked."],
            "notes": ["External completion gate remains."],
        },
        {
            "id": "STRENGTH-001", "approval": "approved", "revalidation": "confirmed",
            "disposition": "retained", "sequence": 4, "reason": "The strength remains valuable.",
            "files_changed": [], "acceptance_results": results_for(by_id["STRENGTH-001"]),
            "verification": ["Original workflow remains unchanged."], "notes": [],
        },
    ]
    convergence = [{
        "id": "REV-001", "title": "Follow-up edge case", "source": "manual full-diff review",
        "severity": "medium", "status": "fixed", "reason": "The first implementation missed an edge case.",
        "files_changed": ["src/tech.ts"], "verification": ["Regression test passed"],
    }]
    return {
        "schema_version": 2,
        "project": teardown["project"],
        "teardown_path": "project-teardown",
        "teardown_audited_revision": teardown["audited_revision"],
        "implementation_start_revision": "abc123",
        "implementation_end_revision": "def456",
        "revision_status": "partial",
        "generated_at": "2026-07-17T13:00:00-05:00",
        "existing_work_reconciled": True,
        "findings": records,
        "convergence_findings": convergence,
        "final_state": {
            "artifact_relationship": "artifact-only-descendant",
            "review_convergence": "passed",
            "blocking_convergence_findings": 0,
            "merge_readiness": "ready",
            "release_readiness": "not-ready",
            "delivery": {
                "committed": "verified", "pushed": "verified",
                "pull_request_updated": "verified", "merged": "not-performed",
            },
        },
    }



def build_files(teardown: dict, revision: dict) -> dict[str, str]:
    ledger = render_implementation_ledger(teardown, revision)
    state = revision["final_state"]
    delivery = state["delivery"]
    handoff = f"""# Verification and handoff

**Revision status:** {revision['revision_status']}
**Implementation endpoint:** {revision['implementation_end_revision']}
**Artifact relationship:** {state['artifact_relationship']}
**Review convergence:** {state['review_convergence']}
**Manual adversarial review:** completed
**Current-head review after final product change:** completed
**Existing work reconciled:** {'yes' if revision['existing_work_reconciled'] else 'no'}
**Blocking convergence findings:** {state['blocking_convergence_findings']}
**Merge readiness:** {state['merge_readiness']}
**Release readiness:** {state['release_readiness']}
**Committed:** {delivery['committed']}
**Pushed:** {delivery['pushed']}
**Pull request updated:** {delivery['pull_request_updated']}
**Merged:** {delivery['merged']}
**Revision validator status:** passed

## Verification results

Focused and full checks are recorded.

## Review-source coverage

Manual and current-head review completed.

## Baseline reconciliation

Existing work was preserved and reconciled.

## Changed-path attribution

| Path | Classification | Finding IDs | Baseline relationship | Rationale |
| --- | --- | --- | --- | --- |
| src/tech.ts | approved-finding | TECH-001 REV-001 | Changed from baseline by approved work | Implements TECH-001 and fixes REV-001 |

## Limitations and blocked evidence

REL-001 remains externally blocked.

## Delivery state

Commit, push, PR, and merge states are recorded above.

## Validator result

The revision validator passed.
"""
    return {
        "README.md": render_readme(teardown, revision),
        "00-decisions-and-scope.md": """# Decisions and scope

## Owner decisions and approval matrix

All findings are classified.

## Constraints and preserved strengths

Existing behavior and strengths are preserved.

## Blocked evidence and authority boundaries

External limitations are explicit.
""",
        "01-baseline-and-revalidation.md": """# Baseline and revalidation

## Baseline state

The immutable baseline is recorded.

## Preservation inventory

Pre-existing work is inventoried.

## Current-state revalidation

Every finding is revalidated.
""",
        "02-execution-plan.md": """# Execution plan

## Dependency-aware execution plan

Dependencies are ordered.

## Verification plan

Focused and end-to-end checks are planned.

## Convergence plan

Full-diff review repeats after risky changes.

## Stop conditions

Stop on unresolved safety or preservation failures.
""",
        "03-implementation-ledger.md": ledger,
        "04-verification-and-handoff.md": handoff,
    }


class RevisionValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.teardown_root = self.root / "teardown"
        self.revision_root = self.root / "revision"
        self.teardown_root.mkdir()
        self.revision_root.mkdir()
        self.teardown = build_teardown()
        self.revision = build_revision(self.teardown)
        self.write()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, teardown=None, revision=None, mutate_files=None) -> None:
        teardown = teardown or self.teardown
        revision = revision or self.revision
        (self.teardown_root / "findings.json").write_text(json.dumps(teardown, indent=2), encoding="utf-8")
        (self.revision_root / "revision.json").write_text(json.dumps(revision, indent=2), encoding="utf-8")
        files = build_files(teardown, revision)
        if mutate_files:
            files = mutate_files(files)
        for name, text in files.items():
            (self.revision_root / name).write_text(text, encoding="utf-8")

    def errors(self, teardown=None, revision=None, mutate_files=None):
        self.write(teardown, revision, mutate_files)
        return validate(self.teardown_root, self.revision_root)

    def assert_error(self, needle, teardown=None, revision=None, mutate_files=None):
        errors = self.errors(teardown, revision, mutate_files)
        self.assertTrue(any(needle in error for error in errors), f"{needle!r} not in {errors}")

    def test_valid_partial_revision_passes(self):
        self.assertEqual([], validate(self.teardown_root, self.revision_root))

    def test_missing_required_file_fails(self):
        (self.revision_root / "02-execution-plan.md").unlink()
        self.assertIn("revision is missing required file: 02-execution-plan.md", validate(self.teardown_root, self.revision_root))

    def test_missing_readme_fails(self):
        (self.revision_root / "README.md").unlink()
        self.assertIn("revision is missing required file: README.md", validate(self.teardown_root, self.revision_root))

    def test_stale_readme_fails(self):
        def mutate(files):
            files["README.md"] = files["README.md"].replace("# Project Revision", "# Stale Summary")
            return files
        self.assert_error("README.md is missing or stale", mutate_files=mutate)

    def test_acceptance_clarification_in_notes_preserves_original_criteria(self):
        revision = copy.deepcopy(self.revision)
        revision["findings"][0]["notes"] = [
            "Clarification: verify the original observable outcome with a deterministic failure-path test; scope, authority, and risk are unchanged."
        ]
        self.write(revision=revision)
        self.assertEqual([], validate(self.teardown_root, self.revision_root))


    def test_schema_three_teardown_preserves_verification_state(self):
        teardown = copy.deepcopy(self.teardown)
        teardown["schema_version"] = 3
        for item in teardown["findings"]:
            item["verification_state"] = (
                "blocked" if item["status"] == "blocked"
                else "behaviorally-verified" if item["type"] == "strength"
                else "defect-conclusively-demonstrated"
            )
        revision = build_revision(teardown)
        self.write(teardown=teardown, revision=revision)
        self.assertEqual([], validate(self.teardown_root, self.revision_root))

    def test_ledger_verification_state_drift_fails(self):
        teardown = copy.deepcopy(self.teardown)
        teardown["schema_version"] = 3
        for item in teardown["findings"]:
            item["verification_state"] = "defect-conclusively-demonstrated"
        revision = build_revision(teardown)
        def mutate(files):
            files["03-implementation-ledger.md"] = files["03-implementation-ledger.md"].replace(
                "**Teardown verification state:** defect-conclusively-demonstrated",
                "**Teardown verification state:** source-only",
                1,
            )
            return files
        self.assert_error(
            "ledger teardown verification state differs",
            teardown=teardown,
            revision=revision,
            mutate_files=mutate,
        )

    def test_schema_version_must_be_two(self):
        revision = copy.deepcopy(self.revision)
        revision["schema_version"] = 1
        self.assert_error("schema_version must be 2", revision=revision)

    def test_timestamp_requires_timezone(self):
        revision = copy.deepcopy(self.revision)
        revision["generated_at"] = "2026-07-17T13:00:00"
        self.assert_error("generated_at must include a timezone", revision=revision)

    def test_missing_required_section_fails(self):
        def mutate(files):
            files["02-execution-plan.md"] = files["02-execution-plan.md"].replace("## Convergence plan", "## Review")
            return files
        self.assert_error("## Convergence plan", mutate_files=mutate)

    def test_revision_missing_finding_fails(self):
        revision = copy.deepcopy(self.revision)
        revision["findings"] = revision["findings"][1:]
        for i, record in enumerate(revision["findings"], 1): record["sequence"] = i
        self.assert_error("revision missing findings: TECH-001", revision=revision)

    def test_unknown_finding_fails(self):
        revision = copy.deepcopy(self.revision)
        revision["findings"][0]["id"] = "NEW-001"
        (self.revision_root / "revision.json").write_text(json.dumps(revision, indent=2), encoding="utf-8")
        errors = validate(self.teardown_root, self.revision_root)
        self.assertTrue(any("revision has unknown findings: NEW-001" in error for error in errors), errors)

    def test_duplicate_sequence_fails(self):
        revision = copy.deepcopy(self.revision)
        revision["findings"][1]["sequence"] = 1
        self.assert_error("duplicate sequence 1", revision=revision)

    def test_dependency_order_fails(self):
        revision = copy.deepcopy(self.revision)
        revision["findings"][0]["sequence"] = 2
        revision["findings"][1]["sequence"] = 1
        self.assert_error("PROD-001 sequence must follow dependency TECH-001", revision=revision)

    def test_approved_criteria_must_match_exactly(self):
        revision = copy.deepcopy(self.revision)
        revision["findings"][0]["acceptance_results"][0]["criterion"] = "Summary"
        self.assert_error("approved acceptance criteria must exactly match", revision=revision)

    def test_implemented_requires_changed_files(self):
        revision = copy.deepcopy(self.revision)
        revision["findings"][0]["files_changed"] = []
        self.assert_error("implemented but lists no changed files", revision=revision)

    def test_unsafe_changed_path_fails(self):
        revision = copy.deepcopy(self.revision)
        revision["findings"][0]["files_changed"] = ["../outside"]
        self.assert_error("not a safe relative project path", revision=revision)

    def test_blocked_requires_blocked_revalidation(self):
        revision = copy.deepcopy(self.revision)
        revision["findings"][2]["revalidation"] = "confirmed"
        self.assert_error("blocked disposition requires blocked revalidation", revision=revision)

    def test_blocked_requires_blocked_acceptance_result(self):
        revision = copy.deepcopy(self.revision)
        for result in revision["findings"][2]["acceptance_results"]: result["status"] = "passed"
        self.assert_error("blocked disposition requires at least one blocked", revision=revision)

    def test_retained_requires_strength(self):
        teardown = copy.deepcopy(self.teardown)
        teardown["findings"][3]["type"] = "defect"
        teardown["findings"][3]["action"] = "fix"
        self.assert_error("retained disposition requires a strength", teardown=teardown)

    def test_ledger_title_drift_fails(self):
        def mutate(files):
            files["03-implementation-ledger.md"] = files["03-implementation-ledger.md"].replace("TECH-001 — Repair behavior", "TECH-001 — Wrong title")
            return files
        self.assert_error("ledger title does not match teardown", mutate_files=mutate)

    def test_ledger_scalar_drift_fails(self):
        def mutate(files):
            files["03-implementation-ledger.md"] = files["03-implementation-ledger.md"].replace("**Approval:** approved", "**Approval:** deferred", 1)
            return files
        self.assert_error("Markdown Approval differs", mutate_files=mutate)

    def test_ledger_digest_drift_fails(self):
        def mutate(files):
            files["03-implementation-ledger.md"] = files["03-implementation-ledger.md"].replace(canonical_digest(self.revision["findings"][0]), "sha256:" + "0" * 64)
            return files
        self.assert_error("Markdown Revision record digest differs", mutate_files=mutate)

    def test_convergence_digest_drift_fails(self):
        def mutate(files):
            files["03-implementation-ledger.md"] = files["03-implementation-ledger.md"].replace(canonical_digest(self.revision["convergence_findings"][0]), "sha256:" + "0" * 64)
            return files
        self.assert_error("Markdown Convergence record digest differs", mutate_files=mutate)

    def test_fixed_convergence_requires_changed_files(self):
        revision = copy.deepcopy(self.revision)
        revision["convergence_findings"][0]["files_changed"] = []
        self.assert_error("is fixed but lists no changed files", revision=revision)

    def test_blocking_count_must_match(self):
        revision = copy.deepcopy(self.revision)
        revision["convergence_findings"][0]["status"] = "open"
        revision["convergence_findings"][0]["files_changed"] = []
        self.assert_error("computed count is 1", revision=revision)

    def test_passed_convergence_requires_manual_review(self):
        def mutate(files):
            files["04-verification-and-handoff.md"] = files["04-verification-and-handoff.md"].replace("**Manual adversarial review:** completed", "**Manual adversarial review:** blocked")
            return files
        self.assert_error("requires completed manual adversarial review", mutate_files=mutate)

    def test_passed_convergence_requires_current_head_review(self):
        def mutate(files):
            files["04-verification-and-handoff.md"] = files["04-verification-and-handoff.md"].replace("**Current-head review after final product change:** completed", "**Current-head review after final product change:** blocked")
            return files
        self.assert_error("requires completed current-head review", mutate_files=mutate)

    def test_complete_revision_cannot_have_blocked_approved_criterion(self):
        revision = copy.deepcopy(self.revision)
        revision["revision_status"] = "complete"
        revision["final_state"]["release_readiness"] = "ready"
        self.assert_error("complete revision has a failed or blocked", revision=revision)

    def test_merge_ready_requires_reconciled_existing_work(self):
        revision = copy.deepcopy(self.revision)
        revision["existing_work_reconciled"] = False
        self.assert_error("merge readiness requires existing_work_reconciled true", revision=revision)

    def test_release_ready_requires_complete(self):
        revision = copy.deepcopy(self.revision)
        revision["final_state"]["release_readiness"] = "ready"
        self.assert_error("release readiness requires complete revision status", revision=revision)

    def test_artifact_descendant_requires_verified_commit(self):
        revision = copy.deepcopy(self.revision)
        revision["final_state"]["delivery"]["committed"] = "unverified"
        revision["final_state"]["delivery"]["pushed"] = "unverified"
        revision["final_state"]["delivery"]["pull_request_updated"] = "unverified"
        self.assert_error("artifact-only-descendant requires a verified committed", revision=revision)

    def test_pr_update_requires_push(self):
        revision = copy.deepcopy(self.revision)
        revision["final_state"]["delivery"]["pushed"] = "unverified"
        self.assert_error("pull request update requires verified push", revision=revision)

    def test_handoff_marker_drift_fails(self):
        def mutate(files):
            files["04-verification-and-handoff.md"] = files["04-verification-and-handoff.md"].replace("**Merge readiness:** ready", "**Merge readiness:** not-ready")
            return files
        self.assert_error("handoff Merge readiness differs", mutate_files=mutate)

    def test_attribution_missing_path_fails(self):
        def mutate(files):
            files["04-verification-and-handoff.md"] = files["04-verification-and-handoff.md"].replace("| src/tech.ts | approved-finding | TECH-001 REV-001 | Changed from baseline by approved work | Implements TECH-001 and fixes REV-001 |\n", "")
            return files
        self.assert_error("changed path src/tech.ts from TECH-001 is missing", mutate_files=mutate)

    def test_attribution_missing_finding_id_fails(self):
        def mutate(files):
            files["04-verification-and-handoff.md"] = files["04-verification-and-handoff.md"].replace("TECH-001 REV-001", "TECH-001")
            return files
        self.assert_error("does not include REV-001", mutate_files=mutate)

    def test_validator_status_must_be_passed(self):
        def mutate(files):
            files["04-verification-and-handoff.md"] = files["04-verification-and-handoff.md"].replace("**Revision validator status:** passed", "**Revision validator status:** pending")
            return files
        self.assert_error("Revision validator status must be passed", mutate_files=mutate)


if __name__ == "__main__":
    unittest.main()
