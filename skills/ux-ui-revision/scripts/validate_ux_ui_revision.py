#!/usr/bin/env python3
"""Validate ux-ui-revision v2 against its exact validated teardown."""
from __future__ import annotations
import argparse,hashlib,json,re
from collections import Counter
from pathlib import Path
from validation_common import run_upstream_validator
AUTH={'repository_edit','design_file_edit','cms_edit','public_content_publish','production_deploy','external_profile_change','analytics_mutation','paid_purchase','third_party_outreach','merge'}
REVAL={'confirmed','changed','stale','already_resolved','not_applicable','blocked'}
APP={'pending','approved','deferred','rejected','accepted_risk','not_applicable'}
IMPL={'not_started','planned','in_progress','fixed','preserved','blocked','deferred','rejected','accepted_risk','not_applicable'}
PRES={'pending','preserved','regressed','approved_tradeoff','not_applicable'}
ACC={'passed','failed','pending','blocked','not_applicable'}
LEVELS={'source_inspection','rendered_experience','assistive_technology','published_experience','user_observation','first_party_measurement','business_outcome'}
def obj(v): return isinstance(v,dict)
def text(v): return isinstance(v,str) and bool(v.strip())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,e):
    try:return json.loads(p.read_text())
    except Exception as x:e.append(f'{p.name} cannot load: {x}'); return None

def validate(td:Path,rvdir:Path,*,run_upstream=True):
    e=[]
    if run_upstream:
        ok,msg=run_upstream_validator(td)
        if not ok:return ['ux-ui-teardown upstream validation failed: '+msg]
    src=load(td/'findings.json',e); rv=load(rvdir/'revision.json',e)
    if not obj(src) or not obj(rv): return e or ['canonical documents must be objects']
    if src.get('schema_version')!='ux-ui-teardown-v2': e.append('upstream findings schema mismatch')
    if rv.get('schema_version')!='ux-ui-revision-v2': e.append('revision schema_version must be ux-ui-revision-v2')
    if rv.get('mode') not in {'planning-only','implementation','continuation'}: e.append('revision mode invalid')
    s=rv.get('source') if obj(rv.get('source')) else {}
    if not s:e.append('source must be object')
    else:
        if s.get('teardown_findings_digest')!=digest(td/'findings.json'): e.append('source teardown digest mismatch')
        if s.get('teardown_revision')!=src.get('audit',{}).get('audited_revision'): e.append('source teardown revision mismatch')
    auth=rv.get('authority') if isinstance(rv.get('authority'),list) else []
    if not isinstance(rv.get('authority'),list):e.append('authority must be list')
    amap={}; actions=[]
    for i,a in enumerate(auth):
        if not obj(a):e.append(f'authority[{i}] must be object');continue
        actions.append(a.get('action'));amap[a.get('action')]=a
        if a.get('action') not in AUTH:e.append(f'authority[{i}].action invalid')
        if a.get('status') not in {'authorized','not_authorized','not_applicable'}:e.append(f'authority[{i}].status invalid')
        if not isinstance(a.get('scope'),list) or not isinstance(a.get('evidence'),list):e.append(f'authority[{i}] scope/evidence must be lists')
    if set(actions)!=AUTH or len(actions)!=len(AUTH):e.append('authority must contain each action exactly once')
    sf={x['id']:x for x in src.get('findings',[]) if obj(x) and text(x.get('id'))}
    rows=rv.get('findings') if isinstance(rv.get('findings'),list) else []
    if not isinstance(rv.get('findings'),list):e.append('findings must be list')
    rmap={}
    for i,r in enumerate(rows):
        if not obj(r):e.append(f'findings[{i}] must be object');continue
        fid=r.get('finding_id')
        if fid in rmap:e.append(f'duplicate revision finding {fid}')
        rmap[fid]=r; source=sf.get(fid)
        if not source:e.append(f'unknown finding {fid}');continue
        if r.get('original_status')!=source.get('status'):e.append(f'{fid} original_status mismatch')
        if r.get('revalidation') not in REVAL:e.append(f'{fid}.revalidation invalid')
        if r.get('approval') not in APP:e.append(f'{fid}.approval invalid')
        if r.get('implementation_status') not in IMPL:e.append(f'{fid}.implementation_status invalid')
        if r.get('preservation_status') not in PRES:e.append(f'{fid}.preservation_status invalid')
        for k in ['current_evidence','changed_targets','acceptance_results','verification_evidence']:
            if not isinstance(r.get(k),list):e.append(f'{fid}.{k} must be list')
        if r.get('revalidation') in {'confirmed','changed','already_resolved'} and not r.get('current_evidence'):e.append(f'{fid} revalidation requires current evidence')
        if r.get('revalidation') in {'stale','not_applicable'} and r.get('implementation_status')=='fixed':e.append(f'{fid} stale/not_applicable cannot be fixed')
        results=r.get('acceptance_results') if isinstance(r.get('acceptance_results'),list) else []
        criteria=[x.get('criterion') for x in results if obj(x) and text(x.get('criterion'))]
        source_criteria=source.get('acceptance_criteria') if isinstance(source.get('acceptance_criteria'),list) else []
        if Counter(criteria)!=Counter(source_criteria) or len(criteria)!=len(results): e.append(f'{fid} acceptance_results must cover every source criterion exactly once')
        for j,x in enumerate(results):
            if not obj(x) or x.get('status') not in ACC or not isinstance(x.get('evidence'),list):e.append(f'{fid}.acceptance_results[{j}] invalid')
        if r.get('implementation_status')=='fixed':
            if r.get('approval')!='approved':e.append(f'{fid} fixed requires approved')
            if any(not obj(x) or x.get('status') not in {'passed','not_applicable'} for x in results):e.append(f'{fid} fixed has unmet acceptance criterion')
            if not r.get('verification_evidence'):e.append(f'{fid} fixed requires verification evidence')
        if r.get('implementation_status')=='accepted_risk' and r.get('approval')!='accepted_risk':e.append(f'{fid} accepted_risk requires accepted_risk approval')
        if rv.get('mode')=='planning-only' and r.get('changed_targets'):e.append(f'{fid} planning-only cannot record changed targets')
        if source.get('kind')=='strength':
            ok_strength=r.get('implementation_status')=='preserved' or (r.get('preservation_status')=='approved_tradeoff' and r.get('approval')=='approved')
            if not ok_strength:e.append(f'{fid} retained strength must stay preserved or have approved tradeoff')
        if r.get('preservation_status')=='approved_tradeoff' and r.get('approval')!='approved':e.append(f'{fid} approved_tradeoff requires approved')
    if set(rmap)!=set(sf):e.append('revision must contain every teardown finding exactly once')

    decisions=rv.get('decisions') if isinstance(rv.get('decisions'),list) else []
    if not isinstance(rv.get('decisions'),list):e.append('decisions must be list')
    dmap={}; decision_links={fid:[] for fid in sf}
    for i,d in enumerate(decisions):
        if not obj(d):e.append(f'decisions[{i}] must be object');continue
        did=d.get('id')
        if not isinstance(did,str) or not re.match(r'^DEC-\d{3}$',did):e.append(f'decisions[{i}].id invalid');continue
        if did in dmap:e.append(f'duplicate decision {did}')
        dmap[did]=d
        fids=d.get('finding_ids') if isinstance(d.get('finding_ids'),list) else []
        if not fids or not all(isinstance(x,str) and x in sf for x in fids):e.append(f'{did}.finding_ids invalid')
        for fid in fids:
            if fid in decision_links:decision_links[fid].append(d)
        if not text(d.get('question')) or not isinstance(d.get('options'),list) or not d.get('options') or not all(text(x) for x in d.get('options',[])):e.append(f'{did} question/options invalid')
        if not text(d.get('recommendation')):e.append(f'{did}.recommendation required')
        if d.get('status') not in {'pending','resolved','deferred'}:e.append(f'{did}.status invalid')
        if not isinstance(d.get('owner_evidence'),list):e.append(f'{did}.owner_evidence must be list')
        if d.get('status')=='resolved' and not d.get('owner_evidence'):e.append(f'{did} resolved requires owner evidence')
    for fid,source in sf.items():
        if source.get('status')=='decision_required':
            links=decision_links.get(fid,[])
            if not links:e.append(f'{fid} decision_required finding needs linked decision')
            row=rmap.get(fid,{})
            if row.get('implementation_status')=='fixed' and not any(d.get('status')=='resolved' and d.get('owner_evidence') for d in links):e.append(f'{fid} fixed decision_required finding needs resolved owner decision')

    conv=rv.get('convergence') if obj(rv.get('convergence')) else {}; open_material=[]
    if not conv:e.append('convergence must be object')
    else:
        if conv.get('status') not in {'not_started','in_progress','converged','blocked'}:e.append('convergence.status invalid')
        seen=set()
        items=conv.get('findings') if isinstance(conv.get('findings'),list) else []
        for i,x in enumerate(items):
            if not obj(x):e.append(f'convergence.findings[{i}] must be object');continue
            cid=x.get('id')
            if not isinstance(cid,str) or not re.match(r'^REVUX-\d{3}$',cid):e.append(f'convergence.findings[{i}].id invalid')
            if cid in seen:e.append(f'duplicate convergence {cid}')
            seen.add(cid)
            if x.get('severity') not in {'critical','high','medium','low','informational'}:e.append(f'{cid}.severity invalid')
            if x.get('status') not in {'open','fixed','accepted_risk','not_applicable'}:e.append(f'{cid}.status invalid')
            if x.get('status')=='open' and x.get('severity') in {'critical','high','medium'}:open_material.append(cid)
    ready=rv.get('readiness') if obj(rv.get('readiness')) else {}
    if not ready:e.append('readiness must be object')
    else:
        if ready.get('highest_evidence_level') not in LEVELS:e.append('readiness.highest_evidence_level invalid')
        if ready.get('overall') not in {'planned','not_ready','ready','blocked'}:e.append('readiness.overall invalid')
        if ready.get('deployment')=='performed' and amap.get('production_deploy',{}).get('status')!='authorized':e.append('deployment performed without production_deploy authority')
        if ready.get('publication')=='performed' and amap.get('public_content_publish',{}).get('status')!='authorized':e.append('publication performed without public_content_publish authority')
        if ready.get('overall')=='ready':
            if ready.get('implementation')!='ready' or ready.get('integration')!='ready':e.append('overall ready requires implementation/integration ready')
            if open_material:e.append(f'overall ready has open material convergence findings: {open_material}')
            for fid,r in rmap.items():
                source=sf[fid]
                if r.get('implementation_status') in {'not_started','planned','in_progress','blocked'}:e.append(f'overall ready has incomplete finding {fid}')
                if r.get('preservation_status') not in {'preserved','approved_tradeoff','not_applicable'}:e.append(f'overall ready has unresolved preservation status for {fid}')
                if source.get('status') in {'open','decision_required'} and source.get('severity') in {'critical','high','medium'} and r.get('approval') not in {'approved','deferred','rejected','accepted_risk'}:e.append(f'overall ready has no terminal disposition for material finding {fid}')
                if source.get('status')=='decision_required' and r.get('implementation_status') not in {'deferred','rejected','accepted_risk','not_applicable'} and not any(d.get('status')=='resolved' for d in decision_links.get(fid,[])):e.append(f'overall ready has unresolved owner decision for {fid}')
    return e

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('teardown',type=Path); ap.add_argument('revision',type=Path); a=ap.parse_args(); e=validate(a.teardown.resolve(),a.revision.resolve())
    if e:
        print(f'UX/UI revision validation failed with {len(e)} error(s):')
        for x in e[:150]:print('-',x)
        return 1
    print('ux-ui-revision validation passed'); return 0
if __name__=='__main__': raise SystemExit(main())
