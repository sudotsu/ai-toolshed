import json,tempfile,unittest
from pathlib import Path
from test_validator import write_fixture
from validate_ux_ui_teardown import validate
class Malformed(unittest.TestCase):
    def test_bad_conflict_and_lists_are_bounded(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t); write_fixture(r); d=json.loads((r/'findings.json').read_text()); d['findings'][0]['conflicts']=5; d['experience_assessments'][0]['competitor_ids']={'bad':1}; (r/'findings.json').write_text(json.dumps(d)); self.assertTrue(validate(r))
if __name__=='__main__': unittest.main()
