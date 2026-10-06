from __future__ import annotations
import json,tempfile,unittest,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
TD_SCRIPTS=HERE.parents[1]/"ux-ui-teardown"/"scripts"
sys.path.insert(0,str(TD_SCRIPTS))
import importlib.util
spec=importlib.util.spec_from_file_location("uxui_teardown_test_fixture", TD_SCRIPTS/"test_validator.py")
td_fixture=importlib.util.module_from_spec(spec)
spec.loader.exec_module(td_fixture)
write_fixture=td_fixture.write_fixture
sys.path.insert(0,str(HERE))
import bootstrap_revision, render_revision
from validate_ux_ui_revision import validate

def run_bootstrap(td:Path,rv:Path):
    old=sys.argv[:]
    sys.argv=["bootstrap_revision.py",str(td),str(rv)]
    try:
        return bootstrap_revision.main()
    finally:
        sys.argv=old

def setup_pair(base:Path):
    td=base/"td"; rv=base/"rv"; td.mkdir()
    write_fixture(td)
    rc=run_bootstrap(td,rv)
    assert rc==0
    return td,rv

class RevisionTests(unittest.TestCase):
    def test_bootstrap_valid_planning(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            self.assertEqual(validate(td,rv),[])

    def test_bootstrap_rejects_invalid_upstream_teardown(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t); td=base/"td"; rv=base/"rv"; td.mkdir(); write_fixture(td)
            c=json.loads((td/"coverage.json").read_text()); c["review_status"]="bogus"
            (td/"coverage.json").write_text(json.dumps(c))
            self.assertEqual(run_bootstrap(td,rv),1)
            self.assertFalse((rv/"revision.json").exists())

    def test_revision_validator_rejects_invalid_upstream_teardown(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            c=json.loads((td/"coverage.json").read_text()); c["review_status"]="bogus"
            (td/"coverage.json").write_text(json.dumps(c))
            errors=validate(td,rv)
            self.assertTrue(any("upstream validation failed" in e for e in errors))

    def test_planning_cannot_claim_changed_targets(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            d=json.loads((rv/"revision.json").read_text()); d["findings"][0]["changed_targets"]=["x.tsx"]
            (rv/"revision.json").write_text(json.dumps(d))
            self.assertTrue(any("planning-only" in e for e in validate(td,rv)))

    def test_invalid_preservation_status_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            d=json.loads((rv/"revision.json").read_text()); d["findings"][0]["preservation_status"]="looks-good"
            (rv/"revision.json").write_text(json.dumps(d))
            self.assertTrue(any("preservation_status invalid" in e for e in validate(td,rv)))

    def test_approved_tradeoff_requires_approval(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            d=json.loads((rv/"revision.json").read_text()); row=d["findings"][0]
            row["preservation_status"]="approved_tradeoff"; row["approval"]="pending"
            (rv/"revision.json").write_text(json.dumps(d))
            self.assertTrue(any("approved_tradeoff requires approved" in e for e in validate(td,rv)))

    def test_fixed_requires_approval(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            d=json.loads((rv/"revision.json").read_text()); r=d["findings"][0]
            r["revalidation"]="confirmed"; r["current_evidence"]=["observed current state"]; r["implementation_status"]="fixed"; r["approval"]="pending"; r["verification_evidence"]=["journey rerun"]
            for x in r["acceptance_results"]: x["status"]="passed"; x["evidence"]=["rerun"]
            d["mode"]="implementation"
            (rv/"revision.json").write_text(json.dumps(d))
            self.assertTrue(any("fixed requires approved" in e for e in validate(td,rv)))

    def test_fixed_requires_acceptance_pass(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            d=json.loads((rv/"revision.json").read_text()); r=d["findings"][0]
            r.update({"revalidation":"confirmed","current_evidence":["current"],"implementation_status":"fixed","approval":"approved","verification_evidence":["rendered"]})
            d["mode"]="implementation"
            (rv/"revision.json").write_text(json.dumps(d))
            self.assertTrue(any("unmet acceptance" in e for e in validate(td,rv)))

    def test_deploy_requires_authority(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            d=json.loads((rv/"revision.json").read_text()); d["readiness"]["deployment"]="performed"
            (rv/"revision.json").write_text(json.dumps(d))
            self.assertTrue(any("deployment performed" in e for e in validate(td,rv)))

    def test_ready_requires_resolved_preservation(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            d=json.loads((rv/"revision.json").read_text())
            d["mode"]="implementation"; d["readiness"]["implementation"]="ready"; d["readiness"]["integration"]="ready"; d["readiness"]["overall"]="ready"
            for r in d["findings"]:
                r["revalidation"]="not_applicable"; r["implementation_status"]="not_applicable"; r["approval"]="not_applicable"
            (rv/"revision.json").write_text(json.dumps(d))
            self.assertTrue(any("unresolved preservation status" in e for e in validate(td,rv)))

    def test_digest_detects_wrong_teardown(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t))
            f=json.loads((td/"findings.json").read_text()); f["audit"]["project_name"]="changed"
            (td/"findings.json").write_text(json.dumps(f))
            self.assertTrue(any("digest mismatch" in e for e in validate(td,rv)))

    def test_renderer_deterministic(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=setup_pair(Path(t)); self.assertEqual(render_revision.render(rv),render_revision.render(rv))
if __name__=="__main__": unittest.main()