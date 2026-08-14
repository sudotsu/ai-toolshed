#!/usr/bin/env python3
"""Regression tests for canonical revision view rendering."""

from __future__ import annotations

import copy
import unittest

from render_revision_views import render_implementation_ledger, render_readme, render_views
from test_validate_revision import build_revision, build_teardown


class RevisionViewRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.teardown = build_teardown()
        self.revision = build_revision(self.teardown)

    def test_rendering_is_deterministic(self) -> None:
        self.assertEqual(render_views(self.teardown, self.revision), render_views(self.teardown, self.revision))

    def test_ledger_contains_every_teardown_and_convergence_id(self) -> None:
        ledger = render_implementation_ledger(self.teardown, self.revision)
        for item in self.teardown["findings"]:
            self.assertIn(f"## {item['id']} — {item['title']}", ledger)
        for item in self.revision["convergence_findings"]:
            self.assertIn(f"## {item['id']} — {item['title']}", ledger)

    def test_readme_surfaces_status_and_deferred_or_blocked_work(self) -> None:
        readme = render_readme(self.teardown, self.revision)
        self.assertIn("**Revision status:** `partial`", readme)
        self.assertIn("PROD-001", readme)
        self.assertIn("REL-001", readme)
        self.assertIn("`revision.json` is the canonical structured record", readme)

    def test_changed_revision_changes_generated_views(self) -> None:
        changed = copy.deepcopy(self.revision)
        changed["findings"][0]["notes"] = ["Clarified measurable verification without changing the criterion."]
        self.assertNotEqual(render_implementation_ledger(self.teardown, self.revision), render_implementation_ledger(self.teardown, changed))


if __name__ == "__main__":
    unittest.main()
