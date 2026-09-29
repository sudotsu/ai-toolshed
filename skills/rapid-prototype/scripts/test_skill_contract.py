"""Static package/contract tests; behavioral tests require real agent sessions."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RapidPrototypeContract(unittest.TestCase):
    def test_manifest_targets_and_required_files(self):
        manifest = json.loads((ROOT / "skill-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "rapid-prototype")
        self.assertEqual(set(manifest["targets"]), {
            "claude-code", "codex", "claude-desktop-code", "chatgpt-desktop-codex"
        })
        for path in manifest["required_files"]:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())

    def test_authority_truth_and_rollback_rules(self):
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        for term in ("feature branch", "unmerged pr", "main", "rollback",
                     "production", "simulated", "viewer", "verified"):
            with self.subTest(term=term):
                self.assertIn(term, content)

    def test_handoff_has_verified_and_unverified_fields(self):
        content = (ROOT / "assets/handoff-template.md").read_text(encoding="utf-8")
        for term in ("**Demo:**", "**What works:**", "**Checked:**",
                     "**Demo-only / unverified:**", "**Git/production:**", "**Rollback:**"):
            with self.subTest(term=term):
                self.assertIn(term, content)

    def test_all_eight_behavioral_prompts_exist(self):
        content = (ROOT / "references/behavioral-fixtures.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^## [1-8]\\. ", content, flags=re.MULTILINE)), 8)
        for term in ("Dirty tree", "Plan-only", "Deployment fails", "Core proof cannot be faked"):
            self.assertIn(term, content)


if __name__ == "__main__":
    unittest.main()
