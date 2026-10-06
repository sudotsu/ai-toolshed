from __future__ import annotations
import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
TD=HERE.parents[1]/'ux-ui-teardown'/'scripts';sys.path.insert(0,str(TD))
spec=importlib.util.spec_from_file_location('td_fixture',TD/'test_validator.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);write_fixture=m.write_fixture
sys.path.insert(0,str(HERE))
import bootstrap_revision,render_revision
from validate_ux_ui_revision import validate

def bootstrap(td,rv):
    old=sys.argv[:];sys.argv=['bootstrap_revision.py',str(td),str(rv)]
    try:return bootstrap_revision.main()
    finally:sys.argv=old

def pair(base):
    td=base/'td';rv=base/'rv';td.mkdir();write_fixture(td);assert bootstrap(td,rv)==0;return td,rv
class Tests(unittest.TestCase):
    def test_bootstrap_valid(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));self.assertEqual(validate(td,rv),[])
    def test_invalid_upstream_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));c=json.loads((td/'coverage.json').read_text());c['review_status']='bogus';(td/'coverage.json').write_text(json.dumps(c));self.assertTrue(any('upstream validation failed' in x for x in validate(td,rv)))
    def test_fixed_requires_every_acceptance_criterion(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));d=json.loads((rv/'revision.json').read_text());r=d['findings'][0];r.update({'revalidation':'confirmed','current_evidence':['current'],'implementation_status':'fixed','approval':'approved','verification_evidence':['rendered']});r['acceptance_results']=[];d['mode']='implementation';(rv/'revision.json').write_text(json.dumps(d));self.assertTrue(any('exactly once' in x for x in validate(td,rv)))
    def test_accepted_risk_requires_matching_approval(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));d=json.loads((rv/'revision.json').read_text());r=d['findings'][0];r['implementation_status']='accepted_risk';r['approval']='pending';(rv/'revision.json').write_text(json.dumps(d));self.assertTrue(any('accepted_risk requires' in x for x in validate(td,rv)))
    def test_strength_approved_tradeoff_is_allowed(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));d=json.loads((rv/'revision.json').read_text());r=d['findings'][0];r['implementation_status']='planned';r['preservation_status']='approved_tradeoff';r['approval']='approved';(rv/'revision.json').write_text(json.dumps(d));errors=validate(td,rv);self.assertFalse(any('retained strength' in x for x in errors))
    def test_decision_required_needs_linked_decision(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));f=json.loads((td/'findings.json').read_text());f['findings'][0]['kind']='gap';f['findings'][0]['status']='decision_required';f['findings'][0]['severity']='medium';f['findings'][0]['recommendation']='choose';(td/'findings.json').write_text(json.dumps(f));# rebootstrap because digest/source status
            import shutil;shutil.rmtree(rv);self.assertEqual(bootstrap(td,rv),0);self.assertTrue(any('needs linked decision' in x for x in validate(td,rv)))
    def test_resolved_decision_requires_owner_evidence(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));d=json.loads((rv/'revision.json').read_text());d['decisions']=[{'id':'DEC-001','finding_ids':['UXUI-001'],'question':'Choose?','options':['a','b'],'recommendation':'a','status':'resolved','owner_evidence':[]}];(rv/'revision.json').write_text(json.dumps(d));self.assertTrue(any('resolved requires owner evidence' in x for x in validate(td,rv)))
    def test_ready_material_pending_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));f=json.loads((td/'findings.json').read_text());x=f['findings'][0];x.update({'kind':'gap','status':'open','severity':'medium','recommendation':'fix'});(td/'findings.json').write_text(json.dumps(f));import shutil;shutil.rmtree(rv);bootstrap(td,rv);d=json.loads((rv/'revision.json').read_text());r=d['findings'][0];r['revalidation']='confirmed';r['current_evidence']=['x'];r['implementation_status']='rejected';r['preservation_status']='not_applicable';d['mode']='implementation';d['readiness']['implementation']='ready';d['readiness']['integration']='ready';d['readiness']['overall']='ready';(rv/'revision.json').write_text(json.dumps(d));self.assertTrue(any('terminal disposition' in x for x in validate(td,rv)))
    def test_deploy_requires_authority(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));d=json.loads((rv/'revision.json').read_text());d['readiness']['deployment']='performed';(rv/'revision.json').write_text(json.dumps(d));self.assertTrue(any('deployment performed' in x for x in validate(td,rv)))
    def test_digest_mismatch(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));f=json.loads((td/'findings.json').read_text());f['audit']['project_name']='changed';(td/'findings.json').write_text(json.dumps(f));self.assertTrue(any('digest mismatch' in x for x in validate(td,rv,run_upstream=False)))
    def test_renderer_deterministic(self):
        with tempfile.TemporaryDirectory() as t:
            td,rv=pair(Path(t));self.assertEqual(render_revision.render(rv),render_revision.render(rv))
if __name__=='__main__':unittest.main()
