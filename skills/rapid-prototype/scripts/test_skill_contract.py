"""Static rapid-prototype package contracts; agent behavior requires separate runtime evaluations."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "claude-code", "codex", "claude-desktop-code", "chatgpt-desktop-codex"
}
REFERENCE_PATHS = (
    "references/decision-playbook.md",
    "references/verification-and-delivery.md",
    "references/behavioral-fixtures.md",
    "references/runtime-validation.md",
    "assets/handoff-template.md",
)


class RapidPrototypeContract(unittest.TestCase):
    """Validate consistent portable metadata, supporting files and eval specifications."""

    def test_manifest_files_targets_and_statuses(self):
        """A declared packaging target must also have an explicit independent evidence status."""
        manifest = json.loads((ROOT / "skill-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "rapid-prototype")
        self.assertEqual(set(manifest["targets"]), TARGETS)
        self.assertEqual(set(manifest["target_verification"]), TARGETS)
        self.assertTrue(all(
            manifest["target_verification"][target] in {"unverified", "verified"}
            for target in TARGETS
        ))
        self.assertEqual(manifest["target_verification_register"], "references/runtime-validation.md")
        for path in manifest["required_files"]:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), path)

    def test_activation_and_negative_trigger(self):
        """The discovery description must select urgent builds without overruling planning-only work."""
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---\n", content, flags=re.DOTALL)
        self.assertIsNotNone(frontmatter)
        description = frontmatter.group(1).lower()
        for term in ("website", "app", "demonstrable", "plan", "main"):
            with self.subTest(term=term):
                self.assertIn(term, description)
        self.assertIn("planning-only", description)

    def test_core_authority_and_truth_rules(self):
        """Keep source preservation, main protection, honest proof and side-effect gates visible."""
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        for term in (
            "feature branch", "unmerged", "main", "rollback", "production",
            "synthetic", "viewer", "verified", "simulation", "separate",
            "untrusted", "dirty", "test mode", "partial", "narrow-screen",
        ):
            with self.subTest(term=term):
                self.assertIn(term, content)

    def test_progressive_reference_files_are_linked(self):
        """All required details must be locatable from the short canonical skill file."""
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for path in REFERENCE_PATHS:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), path)
                self.assertIn(f"]({path})", skill)

    def test_evidence_handoff_and_external_cleanup(self):
        """The compact user handoff must distinguish checked outcomes from external cleanup."""
        content = (ROOT / "assets/handoff-template.md").read_text(encoding="utf-8")
        for term in (
            "**Demo:**", "**Viewer path and observed result:**", "**Checked:**",
            "**Demo-only / unverified:**", "**Git / production:**",
            "**External effects / cleanup owner:**", "**Rollback:**",
            "V1", "V2", "V3", "V4", "V5",
        ):
            with self.subTest(term=term):
                self.assertIn(term, content)

    def test_sixteen_behavioral_cases_are_executable_specs(self):
        """Each distinct eval needs setup, exact prompt and independently inspectable pass/fail cues."""
        content = (ROOT / "references/behavioral-fixtures.md").read_text(encoding="utf-8")
        sections = re.split(r"(?=^## \d{2}\. )", content, flags=re.MULTILINE)
        scenarios = [section for section in sections if re.match(r"^## \d{2}\. ", section)]
        ids = [re.match(r"^## (\d{2})\. ", section).group(1) for section in scenarios]
        self.assertEqual(ids, [f"{number:02d}" for number in range(1, 17)])
        for ident, section in zip(ids, scenarios):
            for marker in ("**Setup:**", "**Prompt:**", "**Pass:**", "**Fail:**"):
                with self.subTest(case=ident, field=marker):
                    self.assertIn(marker, section)
        for term in (
            "dirty", "main", "preview", "persistence", "planning", "production",
            "interrupted", "untrusted", "remote-only", "visual", "authentication",
            "baseline", "critical",
        ):
            with self.subTest(term=term):
                self.assertIn(term, content.lower())

    def test_runtime_claims_remain_unverified_without_real_evals(self):
        """Static compatibility cannot silently turn into verified CLI/desktop behavior."""
        register = (ROOT / "references/runtime-validation.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        for name in ("Claude Code CLI", "Codex CLI/IDE", "Claude Desktop", "ChatGPT desktop"):
            with self.subTest(name=name):
                self.assertIn(name, register)
        self.assertGreaterEqual(register.count("**UNVERIFIED**"), 4)
        self.assertIn("unverified", readme)
        self.assertIn("sixteen", readme)
        self.assertIn("structural", readme)

    def test_platform_adapter_is_optional_and_scoped(self):
        """Vendor-specific presentation metadata must not be required to understand core behavior."""
        content = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("display_name:", content)
        self.assertIn("default_prompt:", content)
        self.assertIn("main", content.lower())
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("agents/openai.yaml", skill)


if __name__ == "__main__":
    unittest.main()
