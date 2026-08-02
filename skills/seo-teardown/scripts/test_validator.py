#!/usr/bin/env python3
"""Regression tests for the SEO teardown validator."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_handoff import render_to_disk
from validate_seo_teardown import MODULE_FACETS, MODULE_IDS, NARRATIVE_FILES, validate


def base_findings() -> dict:
    data = {
        "schema_version": "seo-teardown-v3",
        "audit": {
            "project_name": "Fixture SaaS",
            "project_locator": "https://example.test/repository",
            "audited_revision": "abc123",
            "production_locator": "https://example.test/",
            "audit_start_date": "2026-07-28",
            "audit_end_date": "2026-07-30",
            "research_window_days": 7,
            "review_status": "complete",
            "business_model": "SaaS",
            "primary_geographies": ["United States"],
            "production_revision_status": "verified",
            "production_revision_evidence_ids": ["EVID-002"],
        },
        "evidence_sources": [
            {
                "id": "EVID-001",
                "evidence_class": "official_documentation",
                "title": "Current platform eligibility documentation",
                "publisher_or_owner": "Search platform",
                "locator": "https://example.test/docs",
                "accessed_at": "2026-07-30",
                "platform_sensitive": True,
                "summary": "Documents the applicable crawl and snippet eligibility requirement.",
                "limitations": "Documentation does not guarantee indexing or ranking.",
                "artifact_path": None,
            },
            {
                "id": "EVID-002",
                "evidence_class": "controlled_test",
                "title": "Rendered response test",
                "publisher_or_owner": "Audit fixture",
                "locator": "evidence/render-test.txt",
                "accessed_at": "2026-07-30",
                "platform_sensitive": False,
                "summary": "The canonical page returned a blocking directive in the rendered HTML.",
                "limitations": "Single audited revision.",
                "artifact_path": "evidence/render-test.txt",
            },
        ],
        "implementation_phases": [
            {
                "id": "P1",
                "title": "Restore eligibility",
                "rationale": "Resolve the demonstrated technical blocker before growth work.",
                "finding_ids": ["INDEX-001"],
                "validation_gate": "Canonical URL is eligible in a repeated render test.",
                "expected_outcome": "The page can be considered for indexing.",
            },
            {
                "id": "P2",
                "title": "Preserve strengths",
                "rationale": "Prevent regression of a useful conversion path.",
                "finding_ids": ["STR-001"],
                "validation_gate": "Conversion path remains available after changes.",
                "expected_outcome": "Existing qualified-user flow is retained.",
            },
        ],
        "findings": [
            {
                "id": "INDEX-001",
                "title": "A canonical commercial page is excluded by a rendered noindex directive",
                "kind": "defect",
                "domain": "crawl and index eligibility",
                "status": "open",
                "severity": "high",
                "confidence": "confirmed",
                "evidence_quality": "controlled_test",
                "claim_basis": "documented_eligibility",
                "likelihood": "near_certain",
                "action": "fix",
                "business_impact": "Qualified non-brand discovery cannot accrue to the intended conversion page.",
                "search_consequence": "The URL is ineligible for normal indexing while the directive is present.",
                "affected_queries": ["commercial comparison query"],
                "affected_urls_or_entities": ["https://example.test/product"],
                "platforms": ["Google Search", "Bing"],
                "evidence_ids": ["EVID-001", "EVID-002"],
                "reproduction": "Fetch and render /product, then inspect the robots meta directive.",
                "root_cause": "The production template emits noindex for the canonical product route.",
                "recommendation": "Remove the unintended directive after confirming the route should be public.",
                "if_implemented": "The page becomes technically eligible; indexing and ranking remain unguaranteed.",
                "if_unchanged": "The intended page remains unable to earn normal organic visibility.",
                "acceptance_criteria": ["Rendered canonical response contains no noindex directive."],
                "verification": ["Repeat source and rendered-DOM inspection, then inspect platform index evidence."],
                "dependencies": [],
                "conflicts": [],
                "blocker": None,
                "owner_decision": None,
                "priority": {
                    "expected_business_value": "very_high",
                    "effort": "small",
                    "reversibility": "easy",
                    "time_to_evidence": "days",
                    "downside": "low",
                },
                "measurement": {
                    "baseline": "Canonical page is currently excluded by directive.",
                    "primary_metric": "Index eligibility and subsequent platform index status.",
                    "guardrail_metrics": ["No unintended staging or private routes become indexable."],
                    "time_horizon": "Immediate technical verification; indexing observation over subsequent crawls.",
                    "confounders": ["Crawler recrawl timing", "Other canonicalization signals"],
                    "rollback_criteria": "Restore the directive if the route is confirmed private or duplicative.",
                    "decision_rule": "Accept when the intended public URL is eligible and no protected route exposure is introduced.",
                },
                "implementation": {
                    "phase_id": "P1",
                    "order": 1,
                    "disposition": "implement",
                    "rationale": "Technical eligibility is prerequisite to downstream opportunity.",
                    "validation_gate": "Rendered page and index inspection confirm the intended state.",
                },
            },
            {
                "id": "STR-001",
                "title": "The primary conversion path is visible and usable without an account",
                "kind": "strength",
                "domain": "qualified conversion",
                "status": "passed",
                "severity": "informational",
                "confidence": "confirmed",
                "evidence_quality": "controlled_test",
                "claim_basis": "preserved_strength",
                "likelihood": "near_certain",
                "action": "preserve",
                "business_impact": "Qualified visitors can complete the primary action with low friction.",
                "search_consequence": "Organic landing pages retain a direct conversion path.",
                "affected_queries": None,
                "affected_urls_or_entities": ["https://example.test/product"],
                "platforms": ["Website"],
                "evidence_ids": ["EVID-002"],
                "reproduction": "Open the canonical page and complete the visible primary action without signing in.",
                "root_cause": "The current product flow deliberately avoids an account gate.",
                "recommendation": "Preserve the no-account primary conversion path during SEO implementation.",
                "if_implemented": "No new work is required beyond regression protection.",
                "if_unchanged": "The useful conversion strength remains available.",
                "acceptance_criteria": ["The primary action remains visible and usable without account creation."],
                "verification": ["Repeat the conversion journey after each relevant release."],
                "dependencies": [],
                "conflicts": [],
                "blocker": None,
                "owner_decision": None,
                "priority": {
                    "expected_business_value": "high",
                    "effort": "trivial",
                    "reversibility": "easy",
                    "time_to_evidence": "immediate",
                    "downside": "low",
                },
                "measurement": {
                    "baseline": "The no-account path is currently available.",
                    "primary_metric": "Not applicable — preserved strength, not a growth experiment.",
                    "guardrail_metrics": ["Conversion completion remains functional."],
                    "time_horizon": "Each release affecting the journey.",
                    "confounders": [],
                    "rollback_criteria": "Not applicable — no change is proposed.",
                    "decision_rule": "Not applicable — preserve unless a documented business constraint requires reconsideration.",
                },
                "implementation": {
                    "phase_id": "P2",
                    "order": 2,
                    "disposition": "preserve",
                    "rationale": "SEO changes must not add avoidable conversion friction.",
                    "validation_gate": "Regression journey passes.",
                },
            },
        ],
    }


    common_non_goals = ["Do not infer ranking or traffic improvement from technical eligibility alone."]
    index = data["findings"][0]
    index.update({
        "evidence_links": [
            {"evidence_id": "EVID-001", "role": "supports", "claim": "The platform documentation establishes that noindex blocks normal index eligibility."},
            {"evidence_id": "EVID-002", "role": "supports", "claim": "The controlled render test observed the directive on the canonical route."},
        ],
        "search_state": {"technical_eligibility": "ineligible", "observed_performance": "unknown", "consequence_type": "eligibility"},
        "conversion_linkage": {"conversion_target": "Qualified product signup", "funnel_stage": "decision", "qualifiedness": "qualified", "measurement_status": "blocked"},
        "implementation_scope": {"targets": ["Canonical product route robots directive"], "non_goals": common_non_goals, "owner_or_external_actions": []},
        "verification_context": {"mode": "mixed", "environment": "Audited source plus rendered canonical response", "limitations": ["Platform index state was not available."]},
    })
    strength = data["findings"][1]
    strength.update({
        "evidence_links": [
            {"evidence_id": "EVID-002", "role": "supports", "claim": "The controlled journey completed without an account gate."},
        ],
        "search_state": {"technical_eligibility": "not_applicable", "observed_performance": "not_applicable", "consequence_type": "conversion"},
        "conversion_linkage": {"conversion_target": "Qualified product signup", "funnel_stage": "conversion", "qualifiedness": "qualified", "measurement_status": "blocked"},
        "implementation_scope": {"targets": ["No-account conversion path"], "non_goals": common_non_goals, "owner_or_external_actions": []},
        "verification_context": {"mode": "controlled_test", "environment": "Rendered browser journey", "limitations": []},
    })
    return data


def base_coverage() -> dict:
    access = []
    available = {"source_repository", "production_website"}
    categories = {
        "source_repository", "production_website", "google_search_console",
        "bing_webmaster_tools", "analytics", "crawl_logs", "google_business_profile",
        "merchant_feeds", "rank_tracking", "conversion_records", "location_serp_testing",
    }
    for category in sorted(categories):
        status = "available" if category in available else "not_applicable"
        access.append({
            "category": category,
            "status": status,
            "coverage_window": "Audited revision" if status == "available" else "Not applicable — fixture scope",
            "material_to_comprehensive": category in available,
            "evidence_ids": ["EVID-002"] if category == "production_website" else [],
            "limitations": [],
            "next_step": "None — sufficient for fixture" if status == "available" else "None — not applicable",
        })

    applicable_ids = {
        "business_search_model", "crawl_render_index", "content_evidence",
        "measurement_experimentation", "strategy_prioritization",
    }
    checks = []
    modules = []
    check_counter = 1
    for module_id in sorted(MODULE_IDS):
        applicable = module_id in applicable_ids
        check_ids = []
        facets = sorted(MODULE_FACETS[module_id]) if applicable else ["module_scope"]
        finding_ids = []
        evidence_ids = []
        module_status = "passed" if applicable else "not_applicable"
        if module_id == "crawl_render_index":
            finding_ids = ["INDEX-001"]
            evidence_ids = ["EVID-001", "EVID-002"]
            module_status = "failed"
        elif module_id == "content_evidence":
            finding_ids = ["STR-001"]
            evidence_ids = ["EVID-002"]
        for facet in facets:
            cid = f"CHECK-{check_counter:03d}"
            check_counter += 1
            check_ids.append(cid)
            status = "not_applicable" if not applicable else "passed"
            fids = []
            evids = evidence_ids[:]
            result = (f"{module_id}.{facet} is outside fixture scope." if not applicable else f"{module_id}.{facet} was explicitly tested and passed.")
            if module_id == "crawl_render_index" and facet == "canonicals_http":
                status = "failed"
                fids = ["INDEX-001"]
                result = "Rendered canonical page contains a blocking noindex directive."
            elif module_id == "content_evidence" and facet == "intent_satisfaction":
                fids = ["STR-001"]
            checks.append({
                "id": cid, "module_id": module_id, "facet": facet,
                "method": "controlled_test" if applicable else "external_research",
                "status": status, "evidence_ids": evids, "finding_ids": fids,
                "result": result, "unknowns": [], "limitations": [], "limitation_refs": [], "available_work_completed": True,
            })
        modules.append({
            "id": module_id, "applicable": applicable,
            "materiality": "high" if applicable else "low",
            "status": module_status, "check_ids": check_ids,
            "finding_ids": finding_ids, "evidence_ids": evidence_ids,
            "limitations": [],
            "next_step": "None — covered" if applicable else "None — not applicable",
        })

    reconciliation = []
    for filename in NARRATIVE_FILES:
        ids = ["INDEX-001", "STR-001"] if filename == "00-executive-verdict.md" else []
        reconciliation.append({
            "location": f"{filename} — complete file",
            "finding_ids": ids,
            "non_actionable_explanation": "None" if ids else "Fixture contains context or passed checks only.",
        })

    return {
        "schema_version": "seo-teardown-coverage-v3",
        "review_status": "complete",
        "access": access,
        "modules": modules,
        "surface_checks": checks,
        "serp_samples": [{
            "id": "SERP-001", "query": "fixture product", "engine_or_surface": "Google web search sample",
            "location": "United States", "device": "desktop", "observed_at": "2026-07-30",
            "result_features": ["organic results"],
            "winner_observation": {
                "status": "observed",
                "results": [
                    {"kind": "domain", "value": "example.test", "position": "organic result 1"},
                    {"kind": "named_entity", "value": "Fixture SaaS", "position": "organic result 2"},
                ],
                "reason": None,
                "evidence_ids": ["EVID-002"],
            },
            "target_observation": "present", "evidence_ids": ["EVID-002"], "limitations": ["Single snapshot."],
        }],
        "url_samples": [{
            "id": "URL-001", "url": "https://example.test/product", "role": "canonical commercial route",
            "method_evidence": [
                {"method": "live_fetch", "status": "completed", "observation": "The route returned HTTP 200.", "evidence_ids": ["EVID-002"], "limitations": []},
                {"method": "rendered_browser", "status": "completed", "observation": "The rendered DOM exposed the robots directive.", "evidence_ids": ["EVID-002"], "limitations": []},
            ],
            "source_revision_alignment": "matched",
            "http_observation": {"status": "observed", "value": 200, "supported_by_methods": ["live_fetch"], "evidence_ids": ["EVID-002"], "limitations": []},
            "eligibility_observation": {"status": "observed", "value": "ineligible", "supported_by_methods": ["rendered_browser"], "evidence_ids": ["EVID-002"], "limitations": []},
            "index_observation": {"status": "unavailable", "value": None, "supported_by_methods": ["live_fetch"], "evidence_ids": ["EVID-002"], "limitations": ["No platform or SERP index evidence was captured."]},
            "canonical_observation": {"status": "observed", "value": "Self-canonical is present.", "supported_by_methods": ["rendered_browser"], "evidence_ids": ["EVID-002"], "limitations": []},
            "render_observation": {"status": "observed", "value": "Rendered noindex directive was observed.", "supported_by_methods": ["rendered_browser"], "evidence_ids": ["EVID-002"], "limitations": []},
            "finding_ids": ["INDEX-001", "STR-001"], "evidence_ids": ["EVID-002"], "limitations": ["Single audited revision."],
        }],
        "deliberate_non_pursuits": [{
            "topic": "Generic keyword-density and content-length targets",
            "rationale": "No project evidence makes arbitrary density or word count a useful response.",
            "evidence_ids": ["EVID-001"],
        }],
        "material_limitations": [],
        "narrative_reconciliation": reconciliation,
        "validator": {
            "command": "python3 <skill-directory>/scripts/validate_seo_teardown.py <seo-teardown-directory>",
            "result": "passed",
        },
    }


def write_fixture(root: Path, findings: dict | None = None, coverage: dict | None = None) -> None:
    findings = copy.deepcopy(findings or base_findings())
    coverage = copy.deepcopy(coverage or base_coverage())
    root.mkdir(parents=True, exist_ok=True)
    (root / "evidence").mkdir(exist_ok=True)
    (root / "evidence" / "render-test.txt").write_text("fixture evidence\n", encoding="utf-8")
    (root / "findings.json").write_text(json.dumps(findings, indent=2), encoding="utf-8")
    (root / "coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    (root / "README.md").write_text(
        "# Fixture SEO teardown\n\nRead-only audit. Canonical files: findings.json and coverage.json. "
        "Run validate_seo_teardown.py.\n",
        encoding="utf-8",
    )
    for filename in NARRATIVE_FILES:
        content = f"# {filename}\n\n"
        if filename == "00-executive-verdict.md":
            content += "**Review status:** complete\n"
        elif filename == "08-owner-decisions-and-blockers.md":
            content += "None\n"
        else:
            content += "Fixture narrative.\n"
        (root / filename).write_text(content, encoding="utf-8")
    render_to_disk(root)


class ValidatorRegressionTests(unittest.TestCase):
    def assert_invalid(self, mutator, expected: str) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "seo-teardown"
            findings = base_findings()
            coverage = base_coverage()
            mutator(findings, coverage)
            write_fixture(root, findings, coverage)
            errors = validate(root)
            self.assertTrue(any(expected in error for error in errors), errors)

    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "seo-teardown"
            write_fixture(root)
            self.assertEqual(validate(root), [])

    def test_missing_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "seo-teardown"
            write_fixture(root)
            (root / "03-live-search-and-competitors.md").unlink()
            self.assertTrue(any("missing required file" in error for error in validate(root)))

    def test_markdown_json_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "seo-teardown"
            write_fixture(root)
            path = root / "11-findings-register.md"
            path.write_text(path.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
            self.assertTrue(any("disagrees with canonical JSON" in error for error in validate(root)))

    def test_unknown_dependency_is_rejected(self) -> None:
        self.assert_invalid(
            lambda f, c: f["findings"][1].update({"dependencies": ["NOPE-999"]}),
            "depends on unknown finding",
        )

    def test_cycle_is_rejected(self) -> None:
        def mutate(findings, _coverage):
            findings["findings"][0]["dependencies"] = ["STR-001"]
            findings["findings"][1]["dependencies"] = ["INDEX-001"]

        self.assert_invalid(mutate, "dependency cycle detected")

    def test_invalid_implementation_order_is_rejected(self) -> None:
        self.assert_invalid(
            lambda f, c: f["findings"][0]["dependencies"].append("STR-001"),
            "does not appear earlier in implementation order",
        )

    def test_false_complete_with_blocked_material_access_is_rejected(self) -> None:
        def mutate(_findings, coverage):
            item = next(x for x in coverage["access"] if x["category"] == "production_website")
            item["status"] = "blocked"
            item["limitations"] = ["Production unavailable"]

        self.assert_invalid(mutate, "false complete status")

    def test_missing_module_is_rejected(self) -> None:
        self.assert_invalid(lambda f, c: c["modules"].pop(), "coverage modules missing")

    def test_unmapped_finding_is_rejected(self) -> None:
        def mutate(_findings, coverage):
            for module in coverage["modules"]:
                module["finding_ids"] = [fid for fid in module["finding_ids"] if fid != "STR-001"]

        self.assert_invalid(mutate, "findings not mapped to any coverage module")

    def test_high_severity_experiment_is_rejected(self) -> None:
        def mutate(findings, _coverage):
            item = findings["findings"][0]
            item["kind"] = "experiment"
            item["claim_basis"] = "hypothesis"
            item["implementation"]["disposition"] = "experiment"

        self.assert_invalid(mutate, "experiment cannot have critical or high severity")

    def test_unverified_theory_defect_is_rejected(self) -> None:
        self.assert_invalid(
            lambda f, c: f["findings"][0].update({"evidence_quality": "unverified_theory"}),
            "unverified_theory may only support investigation or experiment",
        )


    def test_evidence_quality_requires_matching_source_class(self) -> None:
        self.assert_invalid(
            lambda f, c: f["findings"][0].update({"evidence_quality": "first_party_data"}),
            "is not represented by a referenced evidence source",
        )

    def test_stale_platform_research_is_rejected(self) -> None:
        self.assert_invalid(
            lambda f, c: f["evidence_sources"][0].update({"accessed_at": "2026-06-01"}),
            "platform-sensitive evidence is stale",
        )

    def test_missing_owner_decision_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "seo-teardown"
            findings = base_findings()
            coverage = base_coverage()
            item = findings["findings"][0]
            item["status"] = "decision_required"
            item["owner_decision"] = "Confirm whether this route should be public."
            item["implementation"]["disposition"] = "decide"
            write_fixture(root, findings, coverage)
            errors = validate(root)
            self.assertTrue(any("missing blocked/decision findings" in error for error in errors), errors)


    def test_placeholder_implementation_language_is_rejected(self) -> None:
        self.assert_invalid(
            lambda f, c: f["findings"][0].update({"if_implemented": "The documented consequence is removed or the opportunity becomes measurable."}),
            "placeholder implementation-readiness language",
        )

    def test_missing_required_surface_facet_is_rejected(self) -> None:
        def mutate(_findings, coverage):
            module = next(m for m in coverage["modules"] if m["id"] == "crawl_render_index")
            cid = module["check_ids"].pop()
            coverage["surface_checks"] = [c for c in coverage["surface_checks"] if c["id"] != cid]
        self.assert_invalid(mutate, "surface checks missing facets")

    def test_incomplete_available_work_is_rejected(self) -> None:
        self.assert_invalid(lambda f, c: c["surface_checks"][0].update({"available_work_completed": False}), "available_work_completed must be true")

    def test_evidence_link_mismatch_is_rejected(self) -> None:
        self.assert_invalid(lambda f, c: f["findings"][0]["evidence_links"].pop(), "must account for each evidence_id exactly once")

    def test_missing_supporting_evidence_role_is_rejected(self) -> None:
        def mutate(findings, _coverage):
            for link in findings["findings"][0]["evidence_links"]:
                link["role"] = "context"
        self.assert_invalid(mutate, "needs at least one supports entry")

    def test_missing_conversion_linkage_is_rejected(self) -> None:
        self.assert_invalid(lambda f, c: f["findings"][0].pop("conversion_linkage"), "missing fields: conversion_linkage")

    def test_source_only_cannot_claim_observed_performance(self) -> None:
        def mutate(findings, _coverage):
            findings["findings"][0]["verification_context"]["mode"] = "source"
            findings["findings"][0]["search_state"]["observed_performance"] = "absent_in_sample"
        self.assert_invalid(mutate, "source-only verification cannot claim observed search performance")

    def test_missing_deliberate_non_pursuits_is_rejected(self) -> None:
        self.assert_invalid(lambda f, c: c.update({"deliberate_non_pursuits": []}), "deliberate_non_pursuits must be a non-empty list")

    def test_available_production_requires_url_sample(self) -> None:
        self.assert_invalid(lambda f, c: c.update({"url_samples": []}), "available production website requires at least one URL sample")

    def test_false_complete_with_unverified_production_revision_is_rejected(self) -> None:
        self.assert_invalid(lambda f, c: f["audit"].update({"production_revision_status": "unverified"}), "production revision is unverified")

    def test_generic_serp_winner_category_is_rejected(self) -> None:
        def mutate(_findings, coverage):
            coverage["serp_samples"][0]["winner_observation"]["results"] = [
                {"kind": "named_entity", "value": "local competitors", "position": "organic results"}
            ]
        self.assert_invalid(mutate, "generic winner category")

    def test_unavailable_serp_winners_with_reason_and_evidence_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "seo-teardown"
            findings = base_findings()
            coverage = base_coverage()
            coverage["serp_samples"][0]["winner_observation"] = {
                "status": "unavailable", "results": [],
                "reason": "The search artifact recorded result types but no reliable domain, URL, or named entity.",
                "evidence_ids": ["EVID-002"],
            }
            write_fixture(root, findings, coverage)
            self.assertEqual(validate(root), [])

    def test_unavailable_serp_winners_without_reason_are_rejected(self) -> None:
        def mutate(_findings, coverage):
            coverage["serp_samples"][0]["winner_observation"] = {
                "status": "unavailable", "results": [], "reason": None, "evidence_ids": ["EVID-002"]
            }
        self.assert_invalid(mutate, "unavailable winner state requires a reason")

    def test_failed_live_fetch_cannot_support_http_observation(self) -> None:
        def mutate(_findings, coverage):
            method = coverage["url_samples"][0]["method_evidence"][0]
            method.update({"status": "failed", "limitations": ["Connection failed before an HTTP response was captured."]})
        self.assert_invalid(mutate, "cannot be supported by non-completed method live_fetch")

    def test_blocked_browser_cannot_support_render_observation(self) -> None:
        def mutate(_findings, coverage):
            method = coverage["url_samples"][0]["method_evidence"][1]
            method.update({"status": "blocked", "limitations": ["Browser execution was unavailable."]})
        self.assert_invalid(mutate, "cannot be supported by non-completed method rendered_browser")

    def test_url_method_evidence_must_reconcile(self) -> None:
        self.assert_invalid(
            lambda f, c: c["url_samples"][0]["method_evidence"][0].update({"evidence_ids": ["EVID-001"]}),
            "evidence_ids must exactly reconcile method and observation evidence",
        )

    def test_repeated_surface_results_are_rejected(self) -> None:
        def mutate(_findings, coverage):
            candidates = [c for c in coverage["surface_checks"] if c["status"] != "not_applicable"][:6]
            for check in candidates:
                check["result"] = "Public evidence was reviewed and the facet was assessed."
        self.assert_invalid(mutate, "excessive repeated boilerplate in results")

    def test_repeated_surface_limitations_are_rejected(self) -> None:
        def mutate(_findings, coverage):
            candidates = [c for c in coverage["surface_checks"] if c["status"] != "not_applicable"][:6]
            for check in candidates:
                check["limitations"] = ["The same generic access limitation applies."]
        self.assert_invalid(mutate, "excessive repeated boilerplate in limitations")

    def test_shared_limitation_references_may_repeat(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "seo-teardown"
            findings = base_findings()
            coverage = base_coverage()
            coverage["material_limitations"] = [{
                "id": "LIMIT-001", "description": "Shared fixture access boundary.",
                "status": "resolved", "completion_requirement": "None — regression fixture only.",
            }]
            for check in [c for c in coverage["surface_checks"] if c["status"] != "not_applicable"][:6]:
                check["limitation_refs"] = ["LIMIT-001"]
            write_fixture(root, findings, coverage)
            self.assertEqual(validate(root), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
