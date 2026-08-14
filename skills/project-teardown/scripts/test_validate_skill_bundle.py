#!/usr/bin/env python3
"""Regression tests for validate_skill_bundle.py."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from validate_skill_bundle import validate


class SkillBundleValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "demo-skill"
        (self.root / "agents").mkdir(parents=True)
        (self.root / "scripts").mkdir()
        (self.root / "references").mkdir()
        self.write_valid()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_valid(self) -> None:
        (self.root / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: This skill performs a complete evidence-led demonstration workflow for validation.\n---\n\n# Demo Skill\n\nRead [reference](references/example.md).\n",
            encoding="utf-8",
        )
        (self.root / "references" / "example.md").write_text("# Reference\n", encoding="utf-8")
        (self.root / "agents" / "openai.yaml").write_text(
            'interface:\n  display_name: "Demo Skill"\n  short_description: "Run a complete demonstration workflow"\n  default_prompt: "Use $demo-skill to run the demonstration workflow."\n',
            encoding="utf-8",
        )
        for name in ("validate_demo.py", "test_demo.py"):
            path = self.root / "scripts" / name
            path.write_text("#!/usr/bin/env python3\nprint('ok')\n", encoding="utf-8")
            path.chmod(0o755)

    def test_valid_bundle_passes(self):
        self.assertEqual([], validate(self.root))

    def test_folder_name_must_match(self):
        text = (self.root / "SKILL.md").read_text().replace("name: demo-skill", "name: wrong-name")
        (self.root / "SKILL.md").write_text(text)
        self.assertTrue(any("does not match" in error for error in validate(self.root)))

    def test_broken_link_fails(self):
        (self.root / "references" / "example.md").unlink()
        self.assertTrue(any("broken relative link" in error for error in validate(self.root)))

    def test_unquoted_openai_value_fails(self):
        text = (self.root / "agents" / "openai.yaml").read_text().replace('display_name: "Demo Skill"', 'display_name: Demo Skill')
        (self.root / "agents" / "openai.yaml").write_text(text)
        self.assertTrue(any("invalid or unquoted" in error for error in validate(self.root)))

    def test_prompt_must_name_skill(self):
        text = (self.root / "agents" / "openai.yaml").read_text().replace("$demo-skill", "$other")
        (self.root / "agents" / "openai.yaml").write_text(text)
        self.assertTrue(any("must mention $demo-skill" in error for error in validate(self.root)))

    def test_python_cache_is_ignored_for_installed_skill(self):
        cache = self.root / "scripts" / "__pycache__"
        cache.mkdir()
        (cache / "x.pyc").write_bytes(b"cache")
        self.assertEqual(validate(self.root, mode="installed"), [])

    def test_python_cache_fails_package_validation(self):
        cache = self.root / "scripts" / "__pycache__"
        cache.mkdir()
        (cache / "x.pyc").write_bytes(b"cache")
        self.assertTrue(any("skill package contains generated Python cache" in error for error in validate(self.root, mode="package")))

    def test_missing_tests_fails(self):
        (self.root / "scripts" / "test_demo.py").unlink()
        self.assertTrue(any("regression suite" in error for error in validate(self.root)))

    @unittest.skipIf(os.name == "nt", "executable bits are not portable on Windows")
    def test_validator_must_be_executable(self):
        (self.root / "scripts" / "validate_demo.py").chmod(0o644)
        self.assertTrue(any("must be executable" in error for error in validate(self.root)))


if __name__ == "__main__":
    unittest.main()
