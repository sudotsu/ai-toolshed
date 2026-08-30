#!/usr/bin/env python3
from __future__ import annotations

import unittest

from bootstrap_revision import _decision_for


class ForwardRegressionTests(unittest.TestCase):
    def test_decision_category_preserves_positioning_semantics(self):
        finding = {
            "id": "FIND-001",
            "status": "decision_required",
            "module": "positioning_differentiation",
            "owner_decision": "Choose the primary audience and core offer.",
            "recommendation": "Focus the offer around the approved audience.",
            "dependencies": [],
            "priority": {"reversibility": "moderate"},
            "implementation": {"owner_or_external_actions": []},
        }
        decision = _decision_for(finding, 1)
        self.assertEqual(decision["category"], "positioning")

    def test_decision_category_preserves_brand_architecture_semantics(self):
        finding = {
            "id": "FIND-002",
            "status": "decision_required",
            "module": "brand_architecture",
            "owner_decision": "Choose the canonical brand hierarchy.",
            "recommendation": "Use one canonical hierarchy.",
            "dependencies": [],
            "priority": {"reversibility": "hard"},
            "implementation": {"owner_or_external_actions": []},
        }
        decision = _decision_for(finding, 2)
        self.assertEqual(decision["category"], "brand-architecture")

    def test_blocked_owner_action_remains_external_authority(self):
        finding = {
            "id": "FIND-003",
            "status": "blocked",
            "module": "business_audience",
            "owner_decision": None,
            "recommendation": "Run authorized customer research.",
            "dependencies": [],
            "priority": {"reversibility": "easy"},
            "implementation": {"owner_or_external_actions": ["Authorize privacy-safe read-only data access."]},
        }
        decision = _decision_for(finding, 3)
        self.assertEqual(decision["category"], "external-authority")
        self.assertEqual(decision["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
