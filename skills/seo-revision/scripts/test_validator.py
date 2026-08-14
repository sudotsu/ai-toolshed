#!/usr/bin/env python3
"""Regression tests for the seo-revision validator."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from render_revision import render_to_disk
from validate_seo_revision import AUTHORITY_IDS, locate_seo_teardown, validate


def locate_seo_teardown_fixture() -> Path | None:
    """Find seo-teardown for test fixtures only.

    The production locator in validate_seo_revision deliberately searches only
    installed skill roots, because a real revision run must validate against the
    skill the operator actually installed. Tests additionally accept the sibling
    checkout so the suite executes in a clean repository or CI runner instead of
    silently skipping every case. This does not relax any production rule.
    """
    installed = locate_seo_teardown()
    if installed is not None and (installed / "scripts" / "test_validator.py").is_file():
        return installed
    sibling = Path(__file__).resolve().parents[2] / "seo-teardown"
    if (sibling / "SKILL.md").is_file() and (sibling / "scripts" / "test_validator.py").is_file():
        return sibling
    return None


def load_upstream_fixture_module():
    skill = locate_seo_teardown_fixture()
    if skill is None:
        return None
    path = skill / "scripts" / "test_validator.py"
    spec = importlib.util.spec_from_file_location("seo_teardown_test_fixture", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load upstream seo-teardown fixture")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UPSTREAM = load_upstream_fixture_module()
# Resolved seo-teardown skill root, passed explicitly to validate() so the
# suite does not depend on an installed skill being present.
SEO_TEARDOWN_SKILL = locate_seo_teardown_fixture()


class FixtureLocationTests(unittest.TestCase):
    def test_installed_skill_without_fixture_module_falls_back_to_sibling(self):
        with tempfile.TemporaryDirectory() as temp:
            installed = Path(temp) / "seo-teardown"
            (installed / "scripts").mkdir(parents=True)
            (installed / "SKILL.md").write_text("---\nname: seo-teardown\n---\n", encoding="utf-8")
            (installed / "scripts" / "validate_seo_teardown.py").write_text("", encoding="utf-8")
            with patch(f"{__name__}.locate_seo_teardown", return_value=installed):
                resolved = locate_seo_teardown_fixture()
        self.assertEqual(Path(__file__).resolve().parents[2] / "seo-teardown", resolved)


def evidence(
    evid: str,
    level: str,
    method: str,
    observation: str,
    *,
    status: str = "completed",
    limitations: list[str] | None = None,
) -> dict:
    return {
        "id": evid,
        "level": level,
        "method": method,
        "status": status,
        "observation": observation,
        "artifact_path": None,
        "limitations": limitations or [],
        "observed_at": "2026-07-30T12:00:00Z",
    }


def delivery_item(observation: str = "No action was performed.") -> dict:
    return {"state": "not-performed", "evidence_ids": [], "observation": observation}


def authority_matrix() -> list[dict]:
    return [
        {
            "id": aid,
            "state": "not-requested",
            "scope": "No authority requested for this planning-only fixture.",
            "evidence_ids": [],
            "limitations": [],
        }
        for aid in sorted(AUTHORITY_IDS)
    ]


def base_revision(teardown: Path) -> dict:
    findings_data = json.loads((teardown / "findings.json").read_text(encoding="utf-8"))
    coverage_data = json.loads((teardown / "coverage.json").read_text(encoding="utf-8"))
    findings = []
    for sequence, source in enumerate(findings_data["findings"], start=1):
        findings.append(
            {
                "id": source["id"],
                "title": source["title"],
                "approval": "approved",
                "revalidation": "confirmed",
                "disposition": "planned",
                "sequence": sequence,
                "dependencies": copy.deepcopy(source["dependencies"]),
                "reason": "Current source inspection confirms this item remains relevant to the revision plan.",
                "acceptance_results": [
                    {
                        "criterion": criterion,
                        "status": "pending",
                        "evidence_ids": [],
                        "observation": "Implementation and current-environment verification remain a completion gate.",
                    }
                    for criterion in source["acceptance_criteria"]
                ],
                "evidence_ids": ["REV-EVID-001"],
                "change_ids": [],
                "experiment_ids": [],
                "completion_gates": [
                    "Implement only after owner approval and verify at the evidence level required by the teardown."
                ],
                "notes": [],
            }
        )

    access = [
        {
            "category": item["category"],
            "source_status": item["status"],
            "disposition": "not-applicable"
            if item["status"] == "not_applicable"
            else "preserve",
            "completion_gate": "Preserve the teardown access boundary and obtain the named access before making higher-level claims.",
            "evidence_ids": [],
        }
        for item in coverage_data["access"]
    ]
    checks = [
        {
            "id": item["id"],
            "source_status": item["status"],
            "disposition": "not-applicable"
            if item["status"] == "not_applicable"
            else "completion-gate",
            "completion_gate": "Re-run this exact facet after affected implementation and retain its source limitation.",
            "evidence_ids": [],
        }
        for item in coverage_data["surface_checks"]
    ]
    limitations = [
        {
            "id": item["id"],
            "source_status": item["status"],
            "disposition": "resolved" if item["status"] == "resolved" else "open",
            "completion_gate": item["completion_requirement"],
            "evidence_ids": [],
        }
        for item in coverage_data["material_limitations"]
    ]
    non_pursuits = [
        {
            "topic": item["topic"],
            "rationale": item["rationale"],
            "preservation_rule": "Do not introduce this rejected tactic during implementation or experimentation.",
            "evidence_ids": [],
        }
        for item in coverage_data["deliberate_non_pursuits"]
    ]
    audit = findings_data["audit"]
    return {
        "schema_version": "seo-revision-v1",
        "mode": "planning-only",
        "project": {
            "name": audit["project_name"],
            "locator": audit["project_locator"],
        },
        "generated_at": "2026-07-30T12:00:00Z",
        "teardown": {
            "path": str(teardown),
            "findings_schema": "seo-teardown-v3",
            "coverage_schema": "seo-teardown-coverage-v3",
            "audited_revision": audit["audited_revision"],
            "review_status": audit["review_status"],
            "validator_command": "python3 <seo-teardown>/scripts/validate_seo_teardown.py <teardown>",
            "validator_result": "passed",
        },
        "workspace": {
            "implementation_start_revision": audit["audited_revision"],
            "product_endpoint": f"planning baseline at {audit['audited_revision']}",
            "endpoint_kind": "working-tree",
            "artifact_relationship": "working-tree",
            "existing_work_reconciled": True,
            "staged_paths": [],
            "unstaged_paths": [],
            "untracked_paths": [],
            "baseline_evidence_ids": ["REV-EVID-001"],
        },
        "decisions": [],
        "authority_matrix": authority_matrix(),
        "findings": findings,
        "coverage_trace": {
            "access": access,
            "surface_checks": checks,
            "material_limitations": limitations,
            "deliberate_non_pursuits": non_pursuits,
        },
        "changes": [],
        "evidence": [
            evidence(
                "REV-EVID-001",
                "source-inspection",
                "source-inspection",
                "Captured the immutable teardown fixture and planning baseline without modifying it.",
            )
        ],
        "url_verifications": [],
        "experiments": [],
        "convergence_findings": [],
        "rollouts": [],
        "readiness": {
            "revision_status": "planned",
            "review_convergence": "not-run",
            "integration": "not-ready",
            "deployment": "not-ready",
            "publication": "not-ready",
            "search_validation": "not-started",
            "experiment_status": "not-applicable",
            "authorization_summary": "partial",
            "convergence_evidence_ids": [],
            "delivery": {
                "committed": delivery_item(),
                "pushed": delivery_item(),
                "pull_request": delivery_item(),
                "merged": delivery_item(),
                "deployed": delivery_item(),
                "published": delivery_item(),
                "search_platform_actions": delivery_item(),
                "external_profile_actions": delivery_item(),
            },
            "unverified_outcomes": [
                "Planning-only execution did not test implementation, deployment, indexing, visibility, citation, traffic, or qualified outcomes."
            ],
            "follow_up_actions": [
                "Resolve owner decisions and authorize the exact implementation scope before product edits."
            ],
        },
    }


def implementation_revision(teardown: Path) -> dict:
    payload = base_revision(teardown)
    payload["mode"] = "implementation"
    payload["evidence"].extend(
        [
            evidence(
                "REV-EVID-002",
                "build-unit",
                "build-unit",
                "Focused unit and build checks passed for the robots directive change.",
            ),
            evidence(
                "REV-EVID-003",
                "local-render",
                "rendered-browser",
                "The local rendered canonical route no longer contains the unintended noindex directive.",
            ),
            evidence(
                "REV-EVID-004",
                "deployed-production",
                "live-fetch",
                "A disposable production-like fixture returned HTTP 200 and the intended eligibility state.",
            ),
            evidence(
                "REV-EVID-005",
                "source-inspection",
                "owner-authorization",
                "The owner authorized local repository edits for this disposable test.",
            ),
            evidence(
                "REV-EVID-006",
                "source-inspection",
                "source-inspection",
                "A complete baseline-to-current adversarial diff review found no unresolved medium-or-higher defect.",
            ),
        ]
    )
    local = next(item for item in payload["authority_matrix"] if item["id"] == "local_repository_edits")
    local.update(
        {
            "state": "authorized",
            "scope": "Local edits inside the disposable regression fixture only.",
            "evidence_ids": ["REV-EVID-005"],
        }
    )
    if len(payload["findings"]) < 2:
        raise AssertionError("upstream fixture must contain at least two findings")
    first, second = payload["findings"][:2]
    first.update(
        {
            "disposition": "implemented",
            "acceptance_results": [
                {
                    "criterion": first["acceptance_results"][0]["criterion"],
                    "status": "passed",
                    "evidence_ids": ["REV-EVID-003"],
                    "observation": "The local rendered canonical response contains no noindex directive.",
                }
            ],
            "evidence_ids": ["REV-EVID-002", "REV-EVID-003"],
            "change_ids": ["CHG-001"],
        }
    )
    second.update(
        {
            "disposition": "preserved",
            "acceptance_results": [
                {
                    "criterion": second["acceptance_results"][0]["criterion"],
                    "status": "passed",
                    "evidence_ids": ["REV-EVID-003"],
                    "observation": "The no-account conversion path remains usable in the rendered journey.",
                }
            ],
            "evidence_ids": ["REV-EVID-003"],
        }
    )
    payload["changes"] = [
        {
            "id": "CHG-001",
            "scope": "repository",
            "finding_ids": [first["id"]],
            "convergence_ids": [],
            "targets": ["Disposable fixture canonical route robots directive"],
            "description": "Removed the unintended noindex directive in the disposable fixture.",
            "external_authority_ids": ["local_repository_edits"],
            "risk_level": "low",
            "risk_categories": [],
            "rollout_id": None,
            "evidence_ids": ["REV-EVID-002", "REV-EVID-003"],
        }
    ]
    payload["url_verifications"] = [
        {
            "id": "VERIFY-URL-001",
            "url": "https://example.test/product",
            "environment": "production",
            "method_evidence": [
                {
                    "method": "live-fetch",
                    "status": "completed",
                    "observation": "The disposable production-like route returned HTTP 200 with eligible robots state.",
                    "evidence_ids": ["REV-EVID-004"],
                    "limitations": ["This is a controlled fixture, not a public search-platform observation."],
                }
            ],
            "observations": [
                {
                    "dimension": "http",
                    "status": "observed",
                    "value": 200,
                    "supported_by_methods": ["live-fetch"],
                    "evidence_ids": ["REV-EVID-004"],
                    "limitations": [],
                },
                {
                    "dimension": "eligibility",
                    "status": "observed",
                    "value": "eligible",
                    "supported_by_methods": ["live-fetch"],
                    "evidence_ids": ["REV-EVID-004"],
                    "limitations": ["Eligibility does not prove indexing or visibility."],
                },
            ],
            "evidence_ids": ["REV-EVID-004"],
            "limitations": ["No search-platform outcome was observed."],
        }
    ]
    payload["readiness"].update(
        {
            "revision_status": "complete",
            "review_convergence": "passed",
            "integration": "ready",
            "deployment": "not-ready",
            "publication": "not-applicable",
            "search_validation": "eligibility-verified",
            "authorization_summary": "partial",
            "convergence_evidence_ids": ["REV-EVID-006"],
            "unverified_outcomes": [
                "Indexing, visibility, citation, traffic, conversion, and qualified-business outcomes remain unverified."
            ],
            "follow_up_actions": [
                "Obtain deployment authority and verify the actual production revision before activation."
            ],
        }
    )
    return payload


@unittest.skipIf(UPSTREAM is None, "installed seo-teardown skill is required for regression tests")
class SEORevisionValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.teardown = self.root / "seo-teardown"
        self.revision = self.root / "seo-revision"
        assert UPSTREAM is not None
        UPSTREAM.write_fixture(self.teardown)
        self.revision.mkdir()
        (self.revision / "evidence").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, payload: dict, *, render: bool = True) -> None:
        (self.revision / "revision.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        if render:
            render_to_disk(self.revision)

    def errors(self, payload: dict) -> list[str]:
        self.write(payload)
        return validate(self.teardown, self.revision, seo_teardown_skill=SEO_TEARDOWN_SKILL)

    def assert_error(self, payload: dict, fragment: str) -> None:
        errors = self.errors(payload)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_valid_planning_fixture_passes(self) -> None:
        payload = base_revision(self.teardown)
        self.assertEqual(self.errors(payload), [])

    def test_valid_implementation_fixture_passes(self) -> None:
        payload = implementation_revision(self.teardown)
        self.assertEqual(self.errors(payload), [])

    def test_missing_teardown_finding_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        payload["findings"].pop()
        self.assert_error(payload, "revision missing teardown findings")

    def test_broken_dependency_order_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        payload["findings"][0]["dependencies"] = [payload["findings"][1]["id"]]
        self.assert_error(payload, "dependencies do not exactly match teardown")

    def test_missing_acceptance_criterion_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        payload["findings"][0]["acceptance_results"] = []
        self.assert_error(payload, "must account for every teardown criterion exactly once")

    def test_missing_surface_check_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        payload["coverage_trace"]["surface_checks"].pop()
        self.assert_error(payload, "must account for every teardown check exactly once")

    def test_missing_deliberate_non_pursuit_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        payload["coverage_trace"]["deliberate_non_pursuits"] = []
        self.assert_error(payload, "must preserve teardown topics and rationales exactly")

    def test_unhashable_trace_values_are_rejected_without_crashing(self) -> None:
        payload = base_revision(self.teardown)
        payload["coverage_trace"]["surface_checks"][0]["id"] = {}
        payload["coverage_trace"]["material_limitations"].append({
            "id": [],
            "source_status": "open",
            "disposition": "tracked",
            "completion_gate": "Resolve before completion.",
            "evidence_ids": [],
        })
        payload["coverage_trace"]["deliberate_non_pursuits"][0]["topic"] = {}
        errors = self.errors(payload)
        self.assertTrue(any("surface_checks[1].id must be non-empty text" in error for error in errors), errors)
        self.assertTrue(any("material_limitations[1].id must be non-empty text" in error for error in errors), errors)
        self.assertTrue(any("deliberate_non_pursuits[1].topic must be non-empty text" in error for error in errors), errors)

    def test_planning_only_change_record_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        payload["changes"] = [
            {
                "id": "CHG-001",
                "scope": "repository",
                "finding_ids": [payload["findings"][0]["id"]],
                "convergence_ids": [],
                "targets": ["fixture"],
                "description": "Changed the fixture.",
                "external_authority_ids": [],
                "risk_level": "low",
                "risk_categories": [],
                "rollout_id": None,
                "evidence_ids": ["REV-EVID-001"],
            }
        ]
        payload["findings"][0]["change_ids"] = ["CHG-001"]
        self.assert_error(payload, "planning-only mode cannot contain actual change records")

    def test_planning_only_convergence_record_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        payload["convergence_findings"] = [{
            "id": "REV-001",
            "title": "Unimplemented convergence claim",
            "source": "planning artifact",
            "severity": "low",
            "status": "deferred",
            "reason": "No implementation occurred.",
            "reopened_finding_ids": [],
            "change_ids": [],
            "evidence_ids": [],
        }]
        self.assert_error(payload, "planning-only mode cannot contain convergence findings")

    def test_false_search_visibility_success_is_rejected(self) -> None:
        payload = implementation_revision(self.teardown)
        payload["readiness"]["search_validation"] = "visibility-observed"
        self.assert_error(payload, "lacks required URL/search observation evidence")

    def test_failed_method_cannot_support_observed_url_state(self) -> None:
        payload = implementation_revision(self.teardown)
        method = payload["url_verifications"][0]["method_evidence"][0]
        method["status"] = "failed"
        method["limitations"] = ["The fetch failed before observation."]
        self.assert_error(payload, "cannot be supported by non-completed method")

    def test_source_evidence_cannot_claim_index_observation(self) -> None:
        payload = implementation_revision(self.teardown)
        url = payload["url_verifications"][0]
        url["method_evidence"].append(
            {
                "method": "source-inspection",
                "status": "completed",
                "observation": "Source declares an indexable route.",
                "evidence_ids": ["REV-EVID-001"],
                "limitations": [],
            }
        )
        url["observations"].append(
            {
                "dimension": "index",
                "status": "observed",
                "value": "indexed",
                "supported_by_methods": ["source-inspection"],
                "evidence_ids": ["REV-EVID-001"],
                "limitations": [],
            }
        )
        url["evidence_ids"].append("REV-EVID-001")
        self.assert_error(payload, "requires SERP or platform data")

    def test_owner_authorization_alone_cannot_prove_eligibility(self) -> None:
        payload = implementation_revision(self.teardown)
        url = payload["url_verifications"][0]
        url["method_evidence"].append({
            "method": "owner-authorization",
            "status": "completed",
            "observation": "The owner authorized local repository edits.",
            "evidence_ids": ["REV-EVID-005"],
            "limitations": [],
        })
        eligibility = next(item for item in url["observations"] if item["dimension"] == "eligibility")
        eligibility["supported_by_methods"] = ["owner-authorization"]
        eligibility["evidence_ids"] = ["REV-EVID-005"]
        url["evidence_ids"].append("REV-EVID-005")
        self.assert_error(payload, "requires a completed source, render, or live method")

    def test_local_eligibility_does_not_prove_post_deployment_eligibility(self) -> None:
        payload = implementation_revision(self.teardown)
        payload["url_verifications"][0]["environment"] = "local"
        self.assert_error(
            payload,
            "search validation eligibility-verified lacks required URL/search observation evidence",
        )

    def test_unauthorized_external_change_is_rejected(self) -> None:
        payload = implementation_revision(self.teardown)
        change = payload["changes"][0]
        change["scope"] = "external-system"
        change["external_authority_ids"] = ["search_platform_actions"]
        change["evidence_ids"] = ["REV-EVID-004"]
        self.assert_error(payload, "lacks authorized authority search_platform_actions")

    def test_local_change_without_local_edit_authority_is_rejected(self) -> None:
        payload = implementation_revision(self.teardown)
        local = next(
            item
            for item in payload["authority_matrix"]
            if item["id"] == "local_repository_edits"
        )
        local.update({"state": "not-requested", "evidence_ids": []})
        self.assert_error(
            payload, "change lacks authorized authority local_repository_edits"
        )

    def test_high_risk_change_without_rollout_is_rejected(self) -> None:
        payload = implementation_revision(self.teardown)
        payload["changes"][0]["risk_level"] = "high"
        payload["changes"][0]["risk_categories"] = ["canonical-noindex"]
        self.assert_error(payload, "high-risk change requires a rollout")

    def test_unresolved_medium_convergence_blocks_readiness(self) -> None:
        payload = implementation_revision(self.teardown)
        payload["convergence_findings"] = [
            {
                "id": "REV-001",
                "title": "Implementation regression",
                "source": "manual full-diff review",
                "severity": "medium",
                "status": "open",
                "reason": "The current implementation leaves an affected route inconsistent.",
                "reopened_finding_ids": [payload["findings"][0]["id"]],
                "change_ids": [],
                "evidence_ids": ["REV-EVID-006"],
            }
        ]
        self.assert_error(payload, "review convergence cannot pass with blocking convergence findings")

    def test_experiment_inflation_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        finding = payload["findings"][0]
        finding["disposition"] = "experiment-planned"
        finding["experiment_ids"] = ["EXP-001"]
        payload["experiments"] = [
            {
                "id": "EXP-001",
                "finding_ids": [finding["id"]],
                "status": "validated",
                "hypothesis": "A controlled change may improve qualified discovery.",
                "evidence_basis": "The teardown records an evidence-supported opportunity.",
                "segment": "Fixture commercial route",
                "affected_pages_queries": ["https://example.test/product"],
                "baseline": "No search-platform baseline is available.",
                "primary_metric": "Qualified organic conversions",
                "guardrails": ["No loss of conversion usability"],
                "sample_requirement": "Observe a complete declared measurement window.",
                "expected_time_to_evidence": "Four weeks",
                "confounders": ["Search-platform volatility"],
                "stop_rollback_criteria": "Stop if conversion usability regresses.",
                "decision_rule": "Retain only if the primary metric improves without guardrail regression.",
                "observation_owner": "Fixture owner",
                "next_review_at": "2026-08-30",
                "evidence_ids": ["REV-EVID-001"],
            }
        ]
        payload["readiness"]["experiment_status"] = "validated"
        self.assert_error(payload, "validated experiment requires completed outcome observation evidence")

    def test_markdown_drift_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        self.write(payload)
        path = self.revision / "03-implementation-ledger.md"
        path.write_text(path.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8")
        errors = validate(self.teardown, self.revision, seo_teardown_skill=SEO_TEARDOWN_SKILL)
        self.assertTrue(any("disagrees with revision.json" in error for error in errors), errors)

    def test_artifact_descendant_requires_immutable_verified_commit(self) -> None:
        payload = implementation_revision(self.teardown)
        payload["workspace"]["artifact_relationship"] = "artifact-only-descendant"
        self.assert_error(payload, "requires an immutable product endpoint")

    def test_verified_deployment_requires_authority_and_production_evidence(self) -> None:
        payload = implementation_revision(self.teardown)
        payload["readiness"]["delivery"]["deployed"] = {
            "state": "verified",
            "evidence_ids": ["REV-EVID-002"],
            "observation": "Deployment claimed from a build result.",
        }
        self.assert_error(payload, "verified delivery deployed lacks authorized authority deployment")

    def test_pending_decision_blocks_approved_implementation(self) -> None:
        payload = implementation_revision(self.teardown)
        fid = payload["findings"][0]["id"]
        payload["findings"][0]["revalidation"] = "changed"
        payload["decisions"] = [
            {
                "id": "DEC-001",
                "finding_ids": [fid],
                "status": "pending",
                "question": "Which changed implementation should be used?",
                "options": [
                    {
                        "id": "no-change",
                        "label": "No change",
                        "consequences": ["The current behavior remains."],
                        "prerequisites": [],
                        "reversibility": "Immediate",
                    },
                    {
                        "id": "revised-change",
                        "label": "Revised change",
                        "consequences": ["The changed implementation proceeds."],
                        "prerequisites": ["Owner approval"],
                        "reversibility": "Easy",
                    },
                ],
                "recommendation": "Use the safe default until the changed premise is approved.",
                "owner_selection": None,
                "safe_default": "No change",
                "consequences": ["Implementation remains blocked pending the decision."],
                "prerequisites": ["Owner selection"],
                "reversibility": "Easy",
            }
        ]
        self.assert_error(payload, "pending decision blocks approved implementation")

    def test_placeholder_evidence_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        payload["evidence"][0]["observation"] = "TODO: fill this in"
        self.assert_error(payload, "contains placeholder boilerplate")

    def test_upstream_teardown_failure_is_rejected(self) -> None:
        payload = base_revision(self.teardown)
        source = self.teardown / "11-findings-register.md"
        source.write_text(source.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8")
        self.write(payload)
        errors = validate(self.teardown, self.revision, seo_teardown_skill=SEO_TEARDOWN_SKILL)
        self.assertTrue(any("exact upstream seo-teardown validation failed" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
