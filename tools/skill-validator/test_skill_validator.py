#!/usr/bin/env python3
"""Regression tests for the reusable skill validator.

Each test builds a minimal but valid fixture skill in a temporary directory,
then mutates exactly one thing and asserts the validator reports it.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import skill_validator

VALID_SKILL_MD = """\
---
name: fixture-skill
description: A fixture skill exercising the reusable AI Toolshed skill validator across many cases.
---

# Fixture Skill

See [the guide](references/guide.md) for details.
"""

VALID_MANIFEST = {
    "schema_version": 1,
    "name": "fixture-skill",
    "runtime": "claude-code",
    "required_files": [
        "SKILL.md",
        "references/guide.md",
        "scripts/tool.py",
        "scripts/test_ok.py",
    ],
    "forbidden_files": ["agents/openai.yaml"],
    "frontmatter": {"keys": "name-description-only", "description_min_length": 40},
    "tests": [
        {
            "command": ["python3", "-m", "unittest", "test_ok.py"],
            "cwd": "scripts",
            "timeout_seconds": 60,
        }
    ],
}

PASSING_TEST = """\
import unittest


class Ok(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
"""

FAILING_TEST = """\
import unittest


class Bad(unittest.TestCase):
    def test_bad(self):
        self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
"""


def build_fixture(base: Path) -> Path:
    root = base / "fixture-skill"
    (root / "references").mkdir(parents=True)
    (root / "scripts").mkdir(parents=True)
    (root / "SKILL.md").write_text(VALID_SKILL_MD, encoding="utf-8")
    (root / "references" / "guide.md").write_text("# Guide\n\nContent.\n", encoding="utf-8")
    (root / "scripts" / "tool.py").write_text("def run():\n    return True\n", encoding="utf-8")
    (root / "scripts" / "test_ok.py").write_text(PASSING_TEST, encoding="utf-8")
    write_manifest(root, VALID_MANIFEST)
    return root


def write_manifest(root: Path, manifest) -> None:
    text = manifest if isinstance(manifest, str) else json.dumps(manifest, indent=2)
    (root / skill_validator.MANIFEST_NAME).write_text(text, encoding="utf-8")


def has(errors, needle: str) -> bool:
    return any(needle in error for error in errors)


class SkillValidatorTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.root = build_fixture(self.base)

    def tearDown(self):
        self._tmp.cleanup()

    def test_valid_skill_passes_including_declared_tests(self):
        self.assertEqual(skill_validator.validate(self.root, run_tests=True), [])

    def test_missing_required_file(self):
        (self.root / "references" / "guide.md").unlink()
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "missing required file: references/guide.md"))

    def test_forbidden_file_present(self):
        (self.root / "agents").mkdir()
        (self.root / "agents" / "openai.yaml").write_text("x: y\n", encoding="utf-8")
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "forbidden file present: agents/openai.yaml"))

    def test_directory_name_mismatch(self):
        renamed = self.root.parent / "renamed-skill"
        self.root.rename(renamed)
        errors = skill_validator.validate(renamed, run_tests=False)
        self.assertTrue(has(errors, "does not match manifest name"))

    def test_missing_manifest(self):
        (self.root / skill_validator.MANIFEST_NAME).unlink()
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertEqual(errors, ["missing skill-manifest.json"])

    def test_manifest_invalid_json(self):
        write_manifest(self.root, "{ not json")
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "not valid JSON"))

    def test_manifest_bad_schema_version(self):
        manifest = dict(VALID_MANIFEST, schema_version=2)
        write_manifest(self.root, manifest)
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "schema_version must be 1"))

    def test_manifest_empty_required_files(self):
        manifest = dict(VALID_MANIFEST, required_files=[])
        write_manifest(self.root, manifest)
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "required_files must be a non-empty list"))

    def test_no_frontmatter(self):
        (self.root / "SKILL.md").write_text("# No frontmatter here\n", encoding="utf-8")
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "must start with YAML frontmatter"))

    def test_name_mismatch_between_skill_and_manifest(self):
        (self.root / "SKILL.md").write_text(
            VALID_SKILL_MD.replace("name: fixture-skill", "name: other-name"),
            encoding="utf-8",
        )
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "does not match manifest name"))

    def test_non_kebab_name(self):
        (self.root / "SKILL.md").write_text(
            VALID_SKILL_MD.replace("name: fixture-skill", "name: Fixture_Skill"),
            encoding="utf-8",
        )
        manifest = dict(VALID_MANIFEST, name="Fixture_Skill")
        # Also rename dir so the directory-name check is not what fires.
        renamed = self.root.parent / "Fixture_Skill"
        self.root.rename(renamed)
        write_manifest(renamed, manifest)
        errors = skill_validator.validate(renamed, run_tests=False)
        self.assertTrue(has(errors, "must be kebab-case"))

    def test_description_too_short(self):
        manifest = dict(VALID_MANIFEST)
        manifest["frontmatter"] = {"keys": "name-description-only", "description_min_length": 400}
        write_manifest(self.root, manifest)
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "description is too short"))

    def test_description_too_long(self):
        long_desc = "description: " + ("word " * 300)
        (self.root / "SKILL.md").write_text(
            VALID_SKILL_MD.replace(
                "description: A fixture skill exercising the reusable AI Toolshed skill validator across many cases.",
                long_desc.rstrip(),
            ),
            encoding="utf-8",
        )
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "description is too long"))

    def test_description_angle_brackets(self):
        (self.root / "SKILL.md").write_text(
            VALID_SKILL_MD.replace(
                "across many cases.", "across many cases like <this>."
            ),
            encoding="utf-8",
        )
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "angle brackets"))

    def test_extra_key_rejected_under_name_description_only(self):
        (self.root / "SKILL.md").write_text(
            VALID_SKILL_MD.replace(
                "---\n\n# Fixture Skill", "license: MIT\n---\n\n# Fixture Skill"
            ),
            encoding="utf-8",
        )
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "only name and description"))

    def test_claude_standard_allows_license_but_rejects_unknown(self):
        # license is allowed under claude-standard...
        manifest = dict(VALID_MANIFEST)
        manifest["frontmatter"] = {"keys": "claude-standard", "description_min_length": 40}
        write_manifest(self.root, manifest)
        (self.root / "SKILL.md").write_text(
            VALID_SKILL_MD.replace(
                "---\n\n# Fixture Skill", "license: MIT\n---\n\n# Fixture Skill"
            ),
            encoding="utf-8",
        )
        self.assertEqual(skill_validator.validate(self.root, run_tests=False), [])
        # ...but an unknown key is not.
        (self.root / "SKILL.md").write_text(
            VALID_SKILL_MD.replace(
                "---\n\n# Fixture Skill", "bogus: nope\n---\n\n# Fixture Skill"
            ),
            encoding="utf-8",
        )
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "unexpected key"))

    def test_link_escapes_skill(self):
        (self.root / "SKILL.md").write_text(
            VALID_SKILL_MD + "\n[escape](../secrets.md)\n", encoding="utf-8"
        )
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "links outside the skill"))

    def test_broken_local_link(self):
        (self.root / "SKILL.md").write_text(
            VALID_SKILL_MD + "\n[missing](references/nope.md)\n", encoding="utf-8"
        )
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "broken local link"))

    def test_non_compiling_script(self):
        (self.root / "scripts" / "broken.py").write_text("def (:\n", encoding="utf-8")
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "Python compile failed for scripts/broken.py"))

    def test_failing_declared_test_is_caught(self):
        (self.root / "scripts" / "test_ok.py").write_text(FAILING_TEST, encoding="utf-8")
        errors = skill_validator.validate(self.root, run_tests=True)
        self.assertTrue(has(errors, "tests[0] failed"))

    def test_no_tests_flag_skips_declared_tests(self):
        (self.root / "scripts" / "test_ok.py").write_text(FAILING_TEST, encoding="utf-8")
        # With run_tests disabled the failing suite must not be executed.
        self.assertEqual(skill_validator.validate(self.root, run_tests=False), [])

    def test_declared_tests_skipped_when_structurally_broken(self):
        # A structural error should short-circuit before the declared tests run.
        # Make the declared test fail, so if it *were* run the error would appear.
        (self.root / "scripts" / "test_ok.py").write_text(FAILING_TEST, encoding="utf-8")
        (self.root / "references" / "guide.md").unlink()
        errors = skill_validator.validate(self.root, run_tests=True)
        self.assertTrue(has(errors, "missing required file"))
        self.assertFalse(has(errors, "tests[0] failed"))

    def test_required_file_path_traversal_rejected(self):
        manifest = dict(VALID_MANIFEST, required_files=VALID_MANIFEST["required_files"] + ["../escape.md"])
        write_manifest(self.root, manifest)
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "required_files entry escapes the skill directory"))

    def test_absolute_manifest_path_rejected(self):
        manifest = dict(VALID_MANIFEST, forbidden_files=["/etc/passwd"])
        write_manifest(self.root, manifest)
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "forbidden_files entry escapes the skill directory"))

    def test_test_cwd_traversal_rejected(self):
        manifest = dict(VALID_MANIFEST)
        manifest["tests"] = [{"command": ["python3", "-c", "pass"], "cwd": "../.."}]
        write_manifest(self.root, manifest)
        errors = skill_validator.validate(self.root, run_tests=False)
        self.assertTrue(has(errors, "tests[0].cwd escapes the skill directory"))

    def test_discover_surfaces_skill_missing_manifest(self):
        # A sibling skill dir with SKILL.md but no manifest must be discovered
        # (and then reported as missing its manifest), not silently skipped.
        orphan = self.base / "orphan-skill"
        orphan.mkdir()
        (orphan / "SKILL.md").write_text("---\nname: orphan-skill\n---\n", encoding="utf-8")
        found = {p.name for p in skill_validator.discover_skills(self.base)}
        self.assertIn("orphan-skill", found)
        self.assertEqual(skill_validator.validate(orphan, run_tests=False), ["missing skill-manifest.json"])


if __name__ == "__main__":
    unittest.main()
