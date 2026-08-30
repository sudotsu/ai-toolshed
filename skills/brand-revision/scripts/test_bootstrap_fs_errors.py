#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_validator import teardown_docs


class BootstrapFilesystemErrorTests(unittest.TestCase):
    def test_regular_file_parent_returns_controlled_exit_code(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            teardown = root / "brand-teardown"
            teardown.mkdir()
            findings, coverage = teardown_docs()
            (teardown / "findings.json").write_text(json.dumps(findings), encoding="utf-8")
            (teardown / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")

            blocked_parent = root / "not-a-directory"
            blocked_parent.write_text("regular file\n", encoding="utf-8")
            revision = blocked_parent / "brand-revision"

            proc = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("bootstrap_revision.py")),
                    str(teardown),
                    str(revision),
                    "--skip-upstream-validation",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            output = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 2, output)
            self.assertIn("could not build brand-revision scaffold", output)
            self.assertNotIn("Traceback", output)


if __name__ == "__main__":
    unittest.main()
