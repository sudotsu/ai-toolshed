#!/usr/bin/env python3
"""Positive and negative regression fixtures for the brand teardown validator."""

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

from render_handoff import render_findings, render_sequence, render_to_disk
from validate_brand_teardown import ACCESS_CATEGORIES, MODULE_FACETS, MODULE_IDS, NARRATIVE_FILES, NARRATIVE_SECTIONS, validate


def evidence(evid: str, evidence_class: str, evidence_scope: str, title: str, *, volatile: bool = False, summary: str | None = None) -> dict:
    return {
        "id": evid,
        "evidence_class": evidence_class,
        "evidence_scope": evidence_scope,
        "title": title,
        "publisher_or_owner": "Fixture owner",
        "locator": f"evidence/{evid.lower()}.txt",
        "accessed_at": "2026-08-08",
        "volatile": volatile,
        "summary": summary or f"Project-specific fixture evidence for {title.lower()}.",
        "limitations": "Synthetic validator fixture; it proves contract behavior only.",
        "artifact_path": f"evidence/{evid.lower()}.txt",
        "supersedes": [],
    }


def base_findings() -> dict:
    common_non_goals = ["Do not infer improved customer perception or revenue from implementation alone."]
    return {
        "schema_version": "brand-teardown-v1",
        "audit": {
            "project_name": "Fixture Forge",
            "project_locator": "https://example.test/repository",
            "audited_revision": "abc123",
            "production_locator": "https://example.test/",
            "audit_start_date": "2026-08-07",
            "audit_end_date": "2026-08-08",
            "research_window_days": 7,
            "review_status": "complete",
            "project_type": "software_developer_product",
            "brands": ["Fixture Forge"],
            "primary_audiences": ["Independent software developers"],
            "production_revision_status": "verified",
            "production_revision_evidence_ids": ["EVID-002"],
            "zero_strengths_justification": None,
            "established_standard": "Clear developer-tool positioning, evidence-backed claims, and deterministic technical documentation demonstrated by the category benchmark in COMP-001.",
            "remaining_standard_gaps": ["Audience preference remains unmeasured after the message correction."],
        },
        "evidence_sources": [
            evidence("EVID-001", "first_party_artifact", "artifact_state", "Repository and homepage claim capture"),
            evidence("EVID-002", "controlled_observation", "artifact_state", "Desktop and mobile comprehension review", summary="Controlled comparison confirmed audited revision abc123 matches the production deployment identifier for the captured desktop and mobile surfaces."),
            evidence("EVID-003", "competitor_evidence", "competitor_state", "Concrete Benchmark Tool category capture", volatile=True),
            evidence("EVID-004", "customer_or_audience_evidence", "audience_perception", "Moderated developer comprehension session"),
        ],
        "claims": [
            {
                "id": "CLAIM-001", "claim": "Fixture Forge is a developer tool.", "brand": "Fixture Forge",
                "surfaces": ["Homepage", "README"], "audiences": ["Independent software developers"],
                "claim_type": "category", "state": "verified", "risk_level": "low",
                "evidence_ids": ["EVID-001"], "owner": "Project owner",
                "required_action": "Retain the category claim consistently.",
                "verification_method": "Inspect the current homepage and README at the audited revision.",
            },
            {
                "id": "CLAIM-002", "claim": "Fixture Forge makes every integration effortless.", "brand": "Fixture Forge",
                "surfaces": ["Homepage hero"], "audiences": ["Independent software developers"],
                "claim_type": "outcome", "state": "unsupported", "risk_level": "medium",
                "evidence_ids": ["EVID-001"], "owner": "Project owner",
                "required_action": "Narrow the promise to a demonstrated integration outcome.",
                "verification_method": "Re-run integration tasks and compare the revised claim with observed behavior.",
            },
        ],
        "implementation_phases": [
            {
                "id": "P1", "title": "Clarify the primary promise", "phase_type": "message_offer",
                "rationale": "Correct the unsupported universal promise before wider channel rollout.",
                "finding_ids": ["MSG-001"],
                "validation_gate": "Desktop and mobile comprehension tests identify category, audience, bounded promise, and next step.",
                "expected_outcome": "The message becomes specific and supportable; preference remains an outcome to measure.",
            },
            {
                "id": "P2", "title": "Preserve authentic technical voice", "phase_type": "preservation",
                "rationale": "Prevent the correction from erasing a verified source of audience comprehension.",
                "finding_ids": ["STR-001"],
                "validation_gate": "Developer-language examples and direct tone remain recognizable after edits.",
                "expected_outcome": "The useful voice survives the message correction.",
            },
        ],
        "findings": [
            {
                "id": "MSG-001",
                "title": "The homepage promise is universal but its proof is bounded",
                "kind": "gap", "module": "message_comprehension", "status": "open",
                "severity": "medium", "confidence": "confirmed",
                "evidence_quality": "controlled_observation", "claim_state": "unsupported",
                "judgment_basis": "observed_behavior", "outcome_evidence_status": "partial",
                "affected_brands": ["Fixture Forge"],
                "affected_audiences": ["Independent software developers"],
                "affected_surfaces": ["Homepage hero", "README introduction"],
                "affected_channels": ["Website", "GitHub"],
                "evidence_ids": ["EVID-001", "EVID-002"],
                "evidence_links": [
                    {"evidence_id": "EVID-001", "role": "supports", "claim": "The homepage makes the universal effortless-integration claim."},
                    {"evidence_id": "EVID-002", "role": "supports", "claim": "The controlled comprehension pass found no proof supporting universal scope."},
                ],
                "observed_condition": "The homepage promises every integration will be effortless while the README demonstrates one bounded integration path.",
                "desired_condition": "The primary promise names the supported developer job and confines the outcome to demonstrated behavior.",
                "brand_consequence": "The broad promise makes the otherwise specific developer identity feel generic.",
                "business_consequence": "Qualified developers may abandon evaluation when the promise appears broader than the proof.",
                "trust_consequence": "The mismatch invites skepticism about adjacent technical claims.",
                "differentiation_consequence": "Universal ease language is interchangeable with competing developer tools.",
                "recognition_consequence": "The generic promise displaces the memorable integration-boundary explanation.",
                "proof_or_claim_gap": "No cited artifact demonstrates effortless behavior across every integration.",
                "dependencies": [], "conflicts": [], "blocker": None, "owner_decision": None,
                "recommendation": "Replace the universal claim with the demonstrated integration outcome and surface the proof beside it.",
                "acceptance_criteria": ["Homepage and README use the same bounded primary promise.", "A developer comprehension pass identifies the category, supported job, proof, and next step."],
                "verification_methods": ["Inspect desktop and mobile hero states.", "Repeat a controlled developer comprehension session without seeding the intended answer."],
                "preservation_constraints": ["Keep the direct technical vocabulary recorded in STR-001."],
                "implementation_notes": ["Treat preference and conversion effects as unverified until measured."],
                "responsible_discipline": "brand",
                "priority": {"brand_impact": "high", "business_impact": "medium", "effort": "small", "reversibility": "easy"},
                "implementation": {
                    "phase_id": "P1", "order": 1, "disposition": "implement",
                    "rationale": "Claim correction is the prerequisite for channel reuse.",
                    "validation_gate": "The revised promise is consistent, bounded, and comprehensible on desktop and mobile.",
                    "targets": ["Homepage hero", "README introduction"],
                    "non_goals": common_non_goals,
                    "owner_or_external_actions": [],
                },
            },
            {
                "id": "STR-001",
                "title": "Direct technical language helps developers recognize the intended audience",
                "kind": "strength", "module": "strategic_preservation", "status": "retained_strength",
                "severity": "informational", "confidence": "confirmed",
                "evidence_quality": "customer_or_audience_evidence", "claim_state": "verified",
                "judgment_basis": "audience_evidence", "outcome_evidence_status": "measured",
                "affected_brands": ["Fixture Forge"],
                "affected_audiences": ["Independent software developers"],
                "affected_surfaces": ["README examples", "Homepage technical explanation"],
                "affected_channels": ["Website", "GitHub"],
                "evidence_ids": ["EVID-004"],
                "evidence_links": [
                    {"evidence_id": "EVID-004", "role": "supports", "claim": "Moderated developers correctly identified the intended audience from the direct technical language."},
                ],
                "observed_condition": "Moderated developers used the README's direct technical terms to identify that the tool is built for them.",
                "desired_condition": "Message corrections retain the direct technical vocabulary and concrete examples.",
                "brand_consequence": "The voice makes the project feel operated by practitioners rather than a generic software marketer.",
                "business_consequence": "Qualified evaluators can self-select without reading the full documentation.",
                "trust_consequence": "Concrete technical language signals familiarity with the developer's work.",
                "differentiation_consequence": "The practitioner voice separates the project from abstract ease-of-use claims.",
                "recognition_consequence": "Repeated technical phrases create a recognizable verbal pattern.",
                "proof_or_claim_gap": "Not applicable — this retained strength is supported by the moderated comprehension evidence.",
                "dependencies": ["MSG-001"], "conflicts": [], "blocker": None, "owner_decision": None,
                "recommendation": "Preserve the direct technical language while narrowing the unsupported promise.",
                "acceptance_criteria": ["Direct technical vocabulary and concrete examples remain present after the message revision."],
                "verification_methods": ["Compare revised copy with the preserved language inventory and repeat the comprehension prompt."],
                "preservation_constraints": ["Do not replace practitioner language with generic professional or AI-generated phrasing."],
                "implementation_notes": ["Measure recognition again only if the verbal system changes materially."],
                "responsible_discipline": "brand",
                "priority": {"brand_impact": "high", "business_impact": "medium", "effort": "trivial", "reversibility": "easy"},
                "implementation": {
                    "phase_id": "P2", "order": 2, "disposition": "preserve",
                    "rationale": "The strength is a constraint on the preceding message correction.",
                    "validation_gate": "The preserved phrases remain and developers still identify the intended audience.",
                    "targets": ["README examples", "Homepage technical explanation"],
                    "non_goals": common_non_goals,
                    "owner_or_external_actions": [],
                },
            },
        ],
    }


def base_coverage() -> dict:
    access = []
    available = {"source_repository", "production_website", "customer_research", "competitor_public_evidence", "visual_assets", "social_channels", "review_profiles", "sales_operational_collateral"}
    for category in sorted(ACCESS_CATEGORIES):
        status = "available" if category in available else "not_applicable"
        evids = []
        if category == "production_website":
            evids = ["EVID-002"]
        elif category == "customer_research":
            evids = ["EVID-004"]
        elif category == "competitor_public_evidence":
            evids = ["EVID-003"]
        elif category in {"source_repository", "visual_assets"}:
            evids = ["EVID-001"]
        access.append({
            "category": category,
            "status": status,
            "material_to_comprehensive": category in available,
            "coverage_window": "Audited 2026-08-08 fixture state" if status == "available" else "Not applicable — fixture project has no such material surface",
            "evidence_ids": evids,
            "limitations": [],
            "next_step": "None — sufficient fixture evidence" if status == "available" else "None — not applicable to this fixture",
        })

    modules = []
    checks = []
    counter = 1
    for module_id in sorted(MODULE_IDS):
        check_ids = []
        module_finding_ids = []
        module_evidence_ids = ["EVID-002"]
        module_status = "passed"
        if module_id == "message_comprehension":
            module_finding_ids = ["MSG-001"]
            module_evidence_ids = ["EVID-001", "EVID-002"]
            module_status = "failed"
        elif module_id == "strategic_preservation":
            module_finding_ids = ["STR-001"]
            module_evidence_ids = ["EVID-004"]
        elif module_id == "competitive_landscape":
            module_evidence_ids = ["EVID-003"]
        for facet in sorted(MODULE_FACETS[module_id]):
            cid = f"CHECK-{counter:03d}"
            counter += 1
            check_ids.append(cid)
            status = "passed"
            finding_ids = []
            result = f"Fixture review established a project-specific result for {module_id}.{facet}."
            if module_id == "message_comprehension" and facet == "five_second_comprehension":
                status = "failed"
                finding_ids = ["MSG-001"]
                result = "The five-second homepage pass surfaced a universal ease claim without the bounded integration proof."
            elif module_id == "strategic_preservation" and facet == "authentic_voice":
                finding_ids = ["STR-001"]
                result = "Moderated developers recognized the intended audience from the direct technical language."
            method = "controlled_comprehension"
            if module_id == "strategic_preservation":
                method = "customer_research"
            elif module_id == "competitive_landscape":
                method = "competitor_research"
            checks.append({
                "id": cid, "module_id": module_id, "facet": facet,
                "method": method,
                "status": status, "evidence_ids": module_evidence_ids[:], "finding_ids": finding_ids,
                "method_evidence": [
                    {
                        "evidence_id": evid,
                        "role": "supports_result",
                        "observation": result if index == 0 else f"Additional support for the {module_id}.{facet} result.",
                    }
                    for index, evid in enumerate(module_evidence_ids)
                ],
                "result": result, "unknowns": [], "limitations": [], "limitation_refs": [],
                "available_work_completed": True,
            })
        modules.append({
            "id": module_id, "applicable": True, "materiality": "high",
            "status": module_status, "check_ids": check_ids,
            "finding_ids": module_finding_ids, "evidence_ids": module_evidence_ids,
            "limitations": [], "next_step": "Address mapped finding" if module_finding_ids else "None — module covered",
        })

    reconciliation = []
    for filename in NARRATIVE_FILES:
        ids = []
        if filename == "00-executive-verdict.md":
            ids = ["MSG-001", "STR-001"]
        elif filename == "04-message-offer-and-customer-journey.md":
            ids = ["MSG-001"]
        elif filename == "06-voice-and-verbal-identity.md":
            ids = ["STR-001"]
        reconciliation.append({
            "location": f"{filename} — complete file",
            "finding_ids": ids,
            "non_actionable_explanation": None if ids else "Fixture narrative contains passed checks or context only.",
        })

    return {
        "schema_version": "brand-teardown-coverage-v1",
        "review_status": "complete",
        "access": access,
        "modules": modules,
        "surface_checks": checks,
        "surface_samples": [
            {
                "id": "SURFACE-001", "surface": "Homepage", "locator": "https://example.test/",
                "brand": "Fixture Forge", "audience": "Independent software developers",
                "channel": "Website", "viewport_or_format": "desktop 1440px",
                "method": "rendered_browser", "status": "observed", "observed_at": "2026-08-08",
                "evidence_ids": ["EVID-002"], "finding_ids": ["MSG-001"],
                "observations": ["The universal promise appears before bounded technical proof."],
                "limitations": ["Controlled reviewer observation does not prove general audience perception."],
            },
            {
                "id": "SURFACE-002", "surface": "Homepage", "locator": "https://example.test/",
                "brand": "Fixture Forge", "audience": "Independent software developers",
                "channel": "Website", "viewport_or_format": "mobile 390px",
                "method": "rendered_browser", "status": "observed", "observed_at": "2026-08-08",
                "evidence_ids": ["EVID-002"], "finding_ids": ["MSG-001"],
                "observations": ["The bounded proof remains below the first mobile viewport."],
                "limitations": ["One representative mobile viewport was tested."],
            },
        ],
        "competitor_samples": [
            {
                "id": "COMP-001", "name": "Concrete Benchmark Tool", "locator": "https://benchmark.example/",
                "relationship": "category_benchmark", "observed_at": "2026-08-08", "status": "observed",
                "category_language": ["Names the developer job in the primary heading."],
                "trust_conventions": ["Links each capability to runnable documentation."],
                "offer_conventions": ["Provides a bounded free local workflow."],
                "visual_patterns": ["Uses code examples as the primary proof artifact."],
                "strengths": ["Promise and proof appear together."],
                "strategic_consequence": "Fixture Forge can compete through a more specific integration boundary and practitioner voice rather than a broader ease claim.",
                "evidence_ids": ["EVID-003"], "limitations": ["Single dated category benchmark; not evidence of market-wide preference."],
            }
        ],
        "material_limitations": [],
        "narrative_reconciliation": reconciliation,
        "validator": {"command": "python3 <skill-directory>/scripts/validate_brand_teardown.py <brand-teardown-directory>", "result": "passed"},
    }


def write_fixture(root: Path, findings: dict | None = None, coverage: dict | None = None) -> None:
    findings = copy.deepcopy(findings or base_findings())
    coverage = copy.deepcopy(coverage or base_coverage())
    root.mkdir(parents=True, exist_ok=True)
    (root / "evidence").mkdir(exist_ok=True)
    for item in findings["evidence_sources"]:
        artifact = item.get("artifact_path")
        if artifact:
            path = root / artifact
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                f"Evidence manifest for {item['id']}\n\nTitle: {item['title']}\nLocator: {item['locator']}\n"
                f"Summary: {item['summary']}\nLimitations: {item['limitations']}\n"
                "This synthetic file exists only to exercise artifact containment and substantive-size validation.\n",
                encoding="utf-8",
            )
    (root / "findings.json").write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    (root / "coverage.json").write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
    (root / "README.md").write_text(
        "# Fixture brand teardown\n\n"
        "- **Project:** Fixture Forge\n"
        "- **Audited revision:** abc123\n"
        "- **Production locator:** https://example.test/\n"
        "- **Audit dates:** 2026-08-07 through 2026-08-08\n"
        "- **Review status:** complete\n"
        "- **Boundary:** read-only audit; no project or external state changed\n"
        "- **Canonical files:** findings.json and coverage.json\n"
        "- **Evidence limitations:** synthetic validator fixture; no real audience outcome claim\n\n"
        "Render with `python3 <skill-directory>/scripts/render_handoff.py <brand-teardown-directory>` "
        "and validate with `python3 <skill-directory>/scripts/validate_brand_teardown.py <brand-teardown-directory>`.\n",
        encoding="utf-8",
    )
    for filename in NARRATIVE_FILES:
        content = f"# {filename}\n\n"
        if filename == "00-executive-verdict.md":
            content += "**Review status:** complete\n\n"
        for heading in NARRATIVE_SECTIONS[filename]:
            content += (
                f"## {heading}\n\n"
                f"Fixture Forge evidence records a bounded, project-specific account of {heading.lower()}. "
                "The canonical finding and coverage ledgers distinguish artifact state, reviewer observation, audience evidence, and business outcomes. "
                "This substantive fixture paragraph verifies report topology without asserting facts about a real organization.\n\n"
            )
        mapped_ids = next(
            (
                row["finding_ids"]
                for row in coverage["narrative_reconciliation"]
                if row["location"].startswith(filename)
            ),
            [],
        )
        if mapped_ids:
            content += "Canonical finding references: " + ", ".join(mapped_ids) + ".\n"
        (root / filename).write_text(content, encoding="utf-8")
    render_to_disk(root)


class BrandValidatorTests(unittest.TestCase):
    def assert_invalid(self, mutator, fragment: str) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "brand-teardown"
            write_fixture(root)
            findings = base_findings()
            coverage = base_coverage()
            mutator(findings, coverage)
            (root / "findings.json").write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
            (root / "coverage.json").write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
            # Regenerate the derived Markdown so the assertion below fires for the
            # mutation under test, not for an incidental stale-generated-file error.
            render_to_disk(root)
            errors = validate(root)
            self.assertTrue(any(fragment in error for error in errors), errors)

    def test_positive_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "brand-teardown"
            write_fixture(root)
            self.assertEqual(validate(root), [])

    def test_method_requires_compatible_evidence(self) -> None:
        def mutate(_findings, coverage):
            coverage["surface_checks"][0]["method"] = "competitor_research"

        self.assert_invalid(mutate, "requires compatible evidence class")

    def test_conclusive_result_cannot_be_policy_only(self) -> None:
        def mutate(_findings, coverage):
            check = coverage["surface_checks"][0]
            check["result"] = "Availability and staffing are treated as volatile and require current evidence."
            check["method_evidence"][0]["observation"] = check["result"]

        self.assert_invalid(mutate, "states audit policy instead of an observed facet outcome")

    def test_finding_module_mapping_must_match_declared_module(self) -> None:
        def mutate(_findings, coverage):
            target = next(item for item in coverage["surface_checks"] if item["module_id"] == "business_audience")
            target["finding_ids"] = ["MSG-001"]
            module = next(item for item in coverage["modules"] if item["id"] == "business_audience")
            module["finding_ids"] = ["MSG-001"]

        self.assert_invalid(mutate, "does not match its declared module")

    def test_competitive_narrative_reconciliation_is_required(self) -> None:
        def mutate(_findings, coverage):
            coverage["narrative_reconciliation"] = [
                item for item in coverage["narrative_reconciliation"]
                if not item["location"].startswith("08-competitive-brand-landscape.md")
            ]

        self.assert_invalid(mutate, "narrative files missing reconciliation")

    def test_nonexecutive_narrative_mapping_requires_literal_finding_reference(self) -> None:
        def mutate(_findings, coverage):
            row = next(
                item for item in coverage["narrative_reconciliation"]
                if item["location"].startswith("01-brand-and-business-model.md")
            )
            row["finding_ids"] = ["MSG-001"]
            row["non_actionable_explanation"] = None

        self.assert_invalid(mutate, "reconciliation maps findings not named in the narrative")

    def test_narrative_sections_cannot_be_thin_stubs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "brand-teardown"
            write_fixture(root)
            (root / "01-brand-and-business-model.md").write_text(
                "# Brand and business model\n\n## Business, offer, and project type\n\nToo short.\n",
                encoding="utf-8",
            )
            self.assertTrue(any("missing required section" in error or "too thin" in error for error in validate(root)))

    def test_narrative_cannot_repeat_substantive_paragraphs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "brand-teardown"
            write_fixture(root)
            path = root / "01-brand-and-business-model.md"
            text_value = path.read_text(encoding="utf-8")
            repeated = "This repeated project-specific paragraph is intentionally long enough to represent substantive prose while proving that exact duplication across report sections is rejected by the narrative quality gate."
            path.write_text(text_value + f"\n\n{repeated}\n\n{repeated}\n", encoding="utf-8")
            errors = validate(root)
            self.assertTrue(any("repeated substantive narrative paragraphs" in error for error in errors), errors)

    def test_readme_requires_portable_skill_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "brand-teardown"
            write_fixture(root)
            path = root / "README.md"
            text_value = path.read_text(encoding="utf-8")
            text_value = text_value.replace(
                "python3 <skill-directory>/scripts/render_handoff.py <brand-teardown-directory>",
                "python3 /data/local/skills/brand-teardown/scripts/render_handoff.py .",
            )
            path.write_text(text_value, encoding="utf-8")
            errors = validate(root)
            self.assertTrue(any("README.md must contain the portable command" in error for error in errors), errors)

    def test_readme_rejects_appended_absolute_skill_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "brand-teardown"
            write_fixture(root)
            path = root / "README.md"
            path.write_text(
                path.read_text(encoding="utf-8")
                + "\n`python3 /machine/skills/brand-teardown/scripts/render_handoff.py .`\n"
                + "`python3 C:\\machine\\skills\\brand-teardown\\scripts\\validate_brand_teardown.py .`\n",
                encoding="utf-8",
            )
            errors = validate(root)
            self.assertTrue(any("absolute command path to render_handoff.py" in error for error in errors), errors)
            self.assertTrue(any("absolute command path to validate_brand_teardown.py" in error for error in errors), errors)

    def test_actionable_narrative_requires_finding_reconciliation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "brand-teardown"
            write_fixture(root)
            path = root / "08-competitive-brand-landscape.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nThe project should replace its category line.\n", encoding="utf-8")
            errors = validate(root)
            self.assertTrue(any("contains actionable language" in error for error in errors), errors)

    def test_actionable_narrative_allows_mapped_and_context_only_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "brand-teardown"
            coverage = base_coverage()
            coverage["narrative_reconciliation"].append({
                "location": "04-message-offer-and-customer-journey.md — additional context",
                "finding_ids": [],
                "non_actionable_explanation": "This row records supporting journey context only.",
            })
            write_fixture(root, coverage=coverage)
            path = root / "04-message-offer-and-customer-journey.md"
            path.write_text(
                path.read_text(encoding="utf-8") + "\nThe project should retain the mapped correction.\n",
                encoding="utf-8",
            )
            self.assertEqual(validate(root), [])

    def test_access_ledger_must_agree_with_channel_facet(self) -> None:
        def mutate(_findings, coverage):
            access = next(item for item in coverage["access"] if item["category"] == "social_channels")
            access["status"] = "not_applicable"
            access["evidence_ids"] = []

        self.assert_invalid(mutate, "required access is not applicable")

    def test_artifact_path_must_exist_inside_handoff(self) -> None:
        def mutate(findings, _coverage):
            findings["evidence_sources"][0]["artifact_path"] = "evidence/missing-capture.txt"

        self.assert_invalid(mutate, "does not name a regular in-handoff evidence file")

    def test_artifact_path_cannot_escape_evidence_directory(self) -> None:
        def mutate(findings, _coverage):
            findings["evidence_sources"][0]["artifact_path"] = "evidence/../findings.json"

        self.assert_invalid(mutate, "must be a relative path inside evidence/")

    def test_verified_production_revision_requires_alignment_evidence(self) -> None:
        def mutate(findings, _coverage):
            source = next(item for item in findings["evidence_sources"] if item["id"] == "EVID-002")
            source["summary"] = "A public surface was rendered without a deployment or revision comparison."

        self.assert_invalid(mutate, "verified production revision requires")

    def test_surface_sample_method_requires_compatible_evidence(self) -> None:
        def mutate(_findings, coverage):
            coverage["surface_samples"][0]["method"] = "competitor_research"

        self.assert_invalid(mutate, "SURFACE-001 method competitor_research requires compatible evidence class")

    def test_competitor_dependent_finding_requires_competitor_evidence(self) -> None:
        def mutate(findings, _coverage):
            findings["findings"][0]["recommendation"] = "Replace the message to match a category benchmark."

        self.assert_invalid(mutate, "competitor-dependent judgment without competitor evidence")

    def test_observed_competitor_requires_sample_specific_evidence(self) -> None:
        def mutate(_findings, coverage):
            sample = coverage["competitor_samples"][0]
            sample["name"] = "Unrelated Benchmark"
            sample["locator"] = "https://unrelated-benchmark.example/"

        self.assert_invalid(mutate, "lacks sample-specific competitor evidence")

    def test_observed_competitor_rejects_different_path_on_same_host(self) -> None:
        def mutate(findings, coverage):
            source = next(item for item in findings["evidence_sources"] if item["id"] == "EVID-003")
            source["locator"] = "https://benchmark.example/other-product"
            sample = coverage["competitor_samples"][0]
            sample["name"] = "Unrelated Benchmark"
            sample["locator"] = "https://benchmark.example/target-product"

        self.assert_invalid(mutate, "lacks sample-specific competitor evidence")

    def test_observed_competitor_profiles_cannot_be_duplicated(self) -> None:
        def mutate(_findings, coverage):
            duplicate = copy.deepcopy(coverage["competitor_samples"][0])
            duplicate["id"] = "COMP-002"
            duplicate["name"] = "Concrete Benchmark Tool"
            coverage["competitor_samples"].append(duplicate)

        self.assert_invalid(mutate, "repeat an identical canonical evidence profile")

    def test_passed_check_requires_supporting_method_evidence(self) -> None:
        def mutate(_findings, coverage):
            check = coverage["surface_checks"][0]
            for link in check["method_evidence"]:
                link["role"] = "context"

        self.assert_invalid(mutate, "passed check requires method evidence that supports the result")

    def test_facet_label_variation_cannot_hide_repeated_results(self) -> None:
        def mutate(_findings, coverage):
            checks = [item for item in coverage["surface_checks"] if item["module_id"] == "business_audience"]
            for check in checks:
                check["result"] = f"The same broad result applies to {check['facet'].replace('_', ' ')}."

        self.assert_invalid(mutate, "facet-label variation over repeated boilerplate")

    def test_complete_public_audit_cannot_mark_production_not_applicable(self) -> None:
        def mutate(findings, _coverage):
            findings["audit"]["production_revision_status"] = "not_applicable"
            findings["audit"]["production_revision_evidence_ids"] = []

        self.assert_invalid(mutate, "available production website requires verified production revision")

    def test_malformed_nested_audience_object_is_rejected_cleanly(self) -> None:
        self.assert_invalid(lambda f, c: f["findings"][0].update({"affected_audiences": {}}), "affected_audiences must be an array")

    def test_unhashable_evidence_link_id_is_rejected_cleanly(self) -> None:
        self.assert_invalid(lambda f, c: f["findings"][0]["evidence_links"][0].update({"evidence_id": {}}), "evidence_id must be an evidence ID string")

    def test_malformed_priority_array_is_rejected_cleanly(self) -> None:
        self.assert_invalid(lambda f, c: f["findings"][0].update({"priority": []}), "priority must be an object")

    def test_malformed_surface_unknowns_object_is_rejected_cleanly(self) -> None:
        self.assert_invalid(lambda f, c: c["surface_checks"][0].update({"unknowns": {}}), "unknowns must be an array")

    def test_malformed_competitor_strengths_object_is_rejected_cleanly(self) -> None:
        self.assert_invalid(lambda f, c: c["competitor_samples"][0].update({"strengths": {}}), "strengths must be an array")

    def test_malformed_claim_surfaces_object_is_rejected_cleanly(self) -> None:
        self.assert_invalid(lambda f, c: f["claims"][0].update({"surfaces": {}}), "surfaces must be an array")

    def test_duplicate_finding_id_is_rejected(self) -> None:
        def mutate(findings, _coverage):
            findings["findings"][1]["id"] = findings["findings"][0]["id"]
        self.assert_invalid(mutate, "duplicate finding ID")

    def test_dependency_cycle_is_rejected(self) -> None:
        def mutate(findings, _coverage):
            findings["findings"][0]["dependencies"] = ["STR-001"]
        self.assert_invalid(mutate, "dependency cycle detected")

    def test_aesthetic_preference_cannot_be_high_severity(self) -> None:
        def mutate(findings, _coverage):
            findings["findings"][0]["judgment_basis"] = "aesthetic_preference"
            findings["findings"][0]["severity"] = "high"
        self.assert_invalid(mutate, "aesthetic preference cannot support")

    def test_blocked_finding_requires_blocker_and_action(self) -> None:
        def mutate(findings, _coverage):
            findings["findings"][0]["status"] = "blocked"
            findings["findings"][0]["blocker"] = None
        self.assert_invalid(mutate, "blocked status requires blocker text")

    def test_decision_finding_requires_precise_decision(self) -> None:
        def mutate(findings, _coverage):
            findings["findings"][0]["status"] = "decision_required"
            findings["findings"][0]["implementation"]["disposition"] = "decide"
        self.assert_invalid(mutate, "requires owner_decision text")

    def test_verified_claim_requires_evidence(self) -> None:
        self.assert_invalid(lambda f, c: f["claims"][0].update({"evidence_ids": []}), "verified claim requires evidence")

    def test_observed_competitor_requires_evidence(self) -> None:
        self.assert_invalid(lambda f, c: c["competitor_samples"][0].update({"evidence_ids": []}), "observed competitor requires evidence")

    def test_missing_required_facet_is_rejected(self) -> None:
        def mutate(_findings, coverage):
            module = next(item for item in coverage["modules"] if item["id"] == "brand_architecture")
            removed = module["check_ids"].pop()
            coverage["surface_checks"] = [item for item in coverage["surface_checks"] if item["id"] != removed]
        self.assert_invalid(mutate, "surface checks missing facets")

    def test_false_complete_with_material_blocked_access_is_rejected(self) -> None:
        def mutate(_findings, coverage):
            item = next(row for row in coverage["access"] if row["category"] == "production_website")
            item["status"] = "blocked"
            item["limitations"] = ["Production was inaccessible."]
        self.assert_invalid(mutate, "false complete status")

    def test_complete_requires_desktop_and_mobile_samples(self) -> None:
        def mutate(_findings, coverage):
            coverage["surface_samples"] = [coverage["surface_samples"][0]]
        self.assert_invalid(mutate, "requires desktop and mobile surface samples")

    def test_zero_strengths_requires_justification(self) -> None:
        def mutate(findings, coverage):
            findings["findings"] = [findings["findings"][0]]
            findings["implementation_phases"] = [findings["implementation_phases"][0]]
            for module in coverage["modules"]:
                module["finding_ids"] = [fid for fid in module["finding_ids"] if fid != "STR-001"]
            for check in coverage["surface_checks"]:
                check["finding_ids"] = [fid for fid in check["finding_ids"] if fid != "STR-001"]
            for row in coverage["narrative_reconciliation"]:
                row["finding_ids"] = [fid for fid in row["finding_ids"] if fid != "STR-001"]
                if not row["finding_ids"] and row["non_actionable_explanation"] is None:
                    row["non_actionable_explanation"] = "Context only."
        self.assert_invalid(mutate, "zero retained strengths requires")

    def test_stale_volatile_evidence_is_rejected(self) -> None:
        self.assert_invalid(lambda f, c: f["evidence_sources"][2].update({"accessed_at": "2026-06-01"}), "volatile evidence is stale")

    def test_markdown_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "brand-teardown"
            write_fixture(root)
            path = root / "09-findings-register.md"
            path.write_text(path.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
            self.assertTrue(any("disagrees with canonical JSON" in error for error in validate(root)))

    def test_malformed_input_reports_instead_of_crashing(self) -> None:
        """Renderers must survive malformed JSON so the validator can report it.

        Each case previously raised TypeError or AttributeError, which aborted the
        run before any error summary reached the user.
        """
        cases = {
            "unhashable evidence id": (
                render_findings,
                {"evidence_sources": [{"id": ["EVID-001"]}], "findings": []},
            ),
            "implementation is a list": (
                render_sequence,
                {
                    "findings": [{"id": "F-1", "implementation": []}],
                    "implementation": {"phases": [{"phase_id": "P1", "finding_ids": ["F-1"]}]},
                },
            ),
            "implementation is null": (
                render_sequence,
                {"findings": [{"id": "F-1", "implementation": None}], "implementation": {"phases": []}},
            ),
            "order is not an integer": (
                render_sequence,
                {"findings": [{"id": "F-1", "implementation": {"order": "first"}}], "implementation": {"phases": []}},
            ),
            "finding is not an object": (
                render_sequence,
                {"findings": ["not-an-object"], "implementation": {"phases": []}},
            ),
        }
        for label, (renderer, payload) in cases.items():
            with self.subTest(case=label):
                self.assertIsInstance(renderer(payload), str)

    def test_non_string_evidence_id_is_reported(self) -> None:
        self.assert_invalid(
            lambda f, c: f["evidence_sources"][0].update({"id": ["EVID-001"]}),
            "id",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
