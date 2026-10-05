from __future__ import annotations
import copy, tempfile, unittest
from pathlib import Path
from test_validator import fixture, write_fixture
from validate_ux_ui_teardown import validate

class MalformedInputTests(unittest.TestCase):
    def test_wrong_top_level_types_do_not_crash(self):
        variants=[None, [], "bad", 3, True]
        for value in variants:
            with self.subTest(value=value):
                f,c=fixture()
                f["findings"]=value
                with tempfile.TemporaryDirectory() as t:
                    p=Path(t); write_fixture(p,f,c)
                    self.assertTrue(validate(p))

    def test_wrong_finding_shapes_do_not_crash(self):
        for value in [None, [], "bad", 5, {"x":"y"}]:
            with self.subTest(value=value):
                f,c=fixture()
                f["findings"][0]["domains"]=value
                with tempfile.TemporaryDirectory() as t:
                    p=Path(t); write_fixture(p,f,c)
                    self.assertTrue(validate(p))
if __name__=="__main__":
    unittest.main()
