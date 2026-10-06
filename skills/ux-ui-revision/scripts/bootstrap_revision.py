#!/usr/bin/env python3
"""Bootstrap a planning-only ux-ui-revision v2 artifact from validated teardown."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from validation_common import run_upstream_validator
AUTH=['repository_edit','design_file_edit','cms_edit','public_content_publish','production_deploy','external_profile_change','analytics_mutation','paid_purchase','third_party_outreach','merge']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('teardown',type=Path); ap.add_argument('revision',type=Path); a=ap.parse_args(); td=a.teardown.resolve(); out=a.revision.resolve()
    ok,msg=run_upstream_validator(td)
    if not ok: print('ux-ui-teardown upstream validation failed: '+msg,file=sys.stderr); return 1
    if out.exists() and any(out.iterdir()): print('refusing to overwrite non-empty revision directory',file=sys.stderr); return 1
    f=json.loads((td/'findings.json').read_text()); out.mkdir(parents=True,exist_ok=True); (out/'evidence').mkdir(exist_ok=True)
    rows=[]
    for x in f['findings']:
        rows.append({'finding_id':x['id'],'original_status':x['status'],'revalidation':'blocked','approval':'not_applicable' if x['kind']=='strength' else 'pending','implementation_status':'preserved' if x['kind']=='strength' else 'planned','current_evidence':[],'changed_targets':[],'acceptance_results':[{'criterion':c,'status':'pending','evidence':[]} for c in x['acceptance_criteria']],'verification_evidence':[],'preservation_status':'pending','notes':'Planning scaffold; revalidate before implementation.'})
    data={'schema_version':'ux-ui-revision-v2','mode':'planning-only','source':{'teardown_schema_version':f['schema_version'],'teardown_revision':f['audit']['audited_revision'],'teardown_review_status':f['audit']['review_status'],'teardown_findings_digest':digest(td/'findings.json')},'baseline':{'current_revision':'unrecorded','working_tree_state':'unrecorded','production_revision_status':'unrecorded','captured_at':'unrecorded','material_drift':False,'drift_notes':[]},'authority':[{'action':x,'status':'not_authorized','scope':[],'evidence':[]} for x in AUTH],'findings':rows,'decisions':[],'convergence':{'reviewed_revision':'unrecorded','status':'not_started','findings':[]},'readiness':{'implementation':'not_started','integration':'not_started','deployment':'not_performed','publication':'not_performed','user_outcome':'unverified','business_outcome':'unverified','overall':'planned','highest_evidence_level':'source_inspection','limitations':['Planning scaffold only; current-state revalidation incomplete.']}}
    (out/'revision.json').write_text(json.dumps(data,indent=2)+'\n')
    from render_revision import render
    for name,text in render(out).items(): (out/name).write_text(text,encoding='utf-8',newline='\n')
    print(f'bootstrapped {len(rows)} finding row(s)'); return 0
if __name__=='__main__': raise SystemExit(main())
