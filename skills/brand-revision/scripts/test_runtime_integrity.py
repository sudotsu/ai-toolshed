#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bootstrap_revision import _write_scaffold_atomically
from render_revision import GENERATED_FILES
from test_validator import teardown_docs
from validation_common import unique_strings


class RuntimeIntegrityTests(unittest.TestCase):
    def test_unique_strings_requires_nonempty_unique_values(self):
        self.assertFalse(unique_strings([]))
        self.assertFalse(unique_strings(["one", "one"]))
        self.assertFalse(unique_strings(["one", ""]))
        self.assertTrue(unique_strings(["one", "two"]))

    def test_validator_cli_accepts_only_production_validation_arguments(self):
        script = Path(__file__).with_name("validate_brand_revision.py")
        for flag in ("--skip-upstream-validation", "--skip-markdown-check"):
            with self.subTest(flag=flag):
                proc = subprocess.run(
                    [sys.executable, str(script), "teardown", "revision", flag],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
                self.assertIn("unrecognized arguments", proc.stderr)

    def test_atomic_bootstrap_does_not_publish_partial_render(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            teardown = root / "brand-teardown"
            revision = root / "brand-revision"
            teardown.mkdir()
            findings, coverage = teardown_docs()

            def fail_after_partial_write(staging: Path) -> None:
                (staging / "README.md").write_text("partial\n", encoding="utf-8")
                raise RuntimeError("simulated renderer failure")

            with patch("bootstrap_revision.render_to_disk", side_effect=fail_after_partial_write):
                with self.assertRaisesRegex(ValueError, "could not build brand-revision scaffold"):
                    _write_scaffold_atomically(
                        teardown,
                        revision,
                        findings,
                        coverage,
                        validator_result="passed",
                    )

            self.assertFalse(revision.exists())
            self.assertEqual(list(root.glob(".brand-revision.tmp-*")), [])

    def test_atomic_bootstrap_publishes_complete_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            teardown = root / "brand-teardown"
            revision = root / "brand-revision"
            teardown.mkdir()
            findings, coverage = teardown_docs()

            _write_scaffold_atomically(
                teardown,
                revision,
                findings,
                coverage,
                validator_result="passed",
            )

            self.assertTrue((revision / "revision.json").is_file())
            self.assertTrue((revision / "evidence").is_dir())
            for name in GENERATED_FILES:
                self.assertTrue((revision / name).is_file(), name)
            self.assertEqual(list(root.glob(".brand-revision.tmp-*")), [])


if __name__ == "__main__":
    unittest.main()
