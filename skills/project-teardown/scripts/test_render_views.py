#!/usr/bin/env python3
"""Regression tests for deterministic teardown report views."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from finding_model import canonical_finding_digest, render_findings_register, render_readme


class RenderViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project-teardown"
        self.root.mkdir()
        self.finding = {
            "id": "CONV-001",
            "title": "Reject false success",
            "type": "defect",
            "category": "conversion",
            "severity": "high",
            "confidence": "confirmed",
            "verification_state": "defect-conclusively-demonstrated",
            "status": "open",
            "impact": "A visitor is told a lead exists when no lead was created.",
            "evidence": [{
                "kind": "runtime",
                "source": "browser walkthrough",
                "location": "evidence/fast-quote.txt",
                "claim": "The success page appeared without contact capture or delivery.",
            }],
            "expected_behavior": "Success appears only after durable acknowledgement.",
            "actual_behavior": "Navigation alone displays success.",
            "root_cause": "The quote widget routes directly to a receipt page.",
            "affected_components": ["src/FastQuote.tsx", "quote workflow"],
            "recommendation": "Remove the false receipt immediately and connect a durable lead boundary.",
            "if_implemented": "Visitors receive truthful state and recoverable lead handling.",
            "if_unchanged": "Leads are silently lost.",
            "dependencies": [],
            "dependents": [],
            "conflicts": [],
            "acceptance_criteria": ["No success state appears before durable acknowledgement."],
            "verification": "Exercise success, failure, timeout, and duplicate submission paths.",
            "estimated_scope": "medium",
            "regression_risk": "medium",
            "action": "fix",
            "strategic_classification": ["heading for a wall"],
        }
        self.payload = {
            "schema_version": 3,
            "project": "owner/project",
            "audited_revision": "abc123",
            "review_status": "provisional",
            "core_workflows_fully_exercised": False,
            "generated_at": "2026-07-17T12:00:00-05:00",
            "findings": [self.finding],
        }
        (self.root / "findings.json").write_text(json.dumps(self.payload, indent=2) + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_register_is_deterministic_and_complete(self) -> None:
        first = render_findings_register(self.payload)
        second = render_findings_register(self.payload)
        self.assertEqual(first, second)
        self.assertIn("[runtime] The success page appeared", first)
        self.assertIn("browser walkthrough", first)
        self.assertIn("evidence/fast-quote.txt", first)
        self.assertIn(canonical_finding_digest(self.finding), first)

    def test_readme_is_deterministic_and_indexes_claims(self) -> None:
        first = render_readme(self.payload)
        self.assertEqual(first, render_readme(self.payload))
        self.assertIn("08-claims-inventory.md", first)
        self.assertIn("CONV-001 — Reject false success", first)
        self.assertIn("defect-conclusively-demonstrated", first)

    def test_render_findings_cli_write_and_check(self) -> None:
        script = Path(__file__).with_name("render_findings.py")
        write = subprocess.run([sys.executable, str(script), str(self.root)], capture_output=True, text=True)
        self.assertEqual(write.returncode, 0, write.stderr)
        check = subprocess.run([sys.executable, str(script), str(self.root), "--check"], capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)

    def test_render_findings_check_rejects_manual_edit(self) -> None:
        script = Path(__file__).with_name("render_findings.py")
        subprocess.run([sys.executable, str(script), str(self.root)], check=True, capture_output=True, text=True)
        target = self.root / "05-findings-register.md"
        target.write_text(target.read_text(encoding="utf-8") + "manual edit\n", encoding="utf-8")
        check = subprocess.run([sys.executable, str(script), str(self.root), "--check"], capture_output=True, text=True)
        self.assertNotEqual(check.returncode, 0)
        self.assertIn("stale", check.stderr)

    def test_render_readme_cli_write_and_check(self) -> None:
        script = Path(__file__).with_name("render_readme.py")
        write = subprocess.run([sys.executable, str(script), str(self.root)], capture_output=True, text=True)
        self.assertEqual(write.returncode, 0, write.stderr)
        check = subprocess.run([sys.executable, str(script), str(self.root), "--check"], capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)


if __name__ == "__main__":
    unittest.main()
