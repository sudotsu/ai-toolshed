#!/usr/bin/env python3
"""Validate ux-ui-teardown v2 canonical artifacts without crashing on malformed input."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from typing import Any

PATTERNS={
 'evidence':re.compile(r'^EVID-\d{3}$'),'competitor':re.compile(r'^COMP-\d{3}$'),
 'journey':re.compile(r'^JOURNEY-\d{3}$'),'experience':re.compile(r'^EXP-\d{3}$'),
 'finding':re.compile(r'^UXUI-\d{3}$'),'viewport':re.compile(r'^VIEW-\d{3}$'),
 'state':re.compile(r'^STATE-\d{3}$'),'limit':re.compile(r'^LIMIT-\d{3}$')}
EVIDENCE_CLASSES={'source_inspection','rendered_observation','interaction_reproduction','standard_reference','automated_measurement','user_research','user_sentiment','first_party_analytics','stakeholder_context','design_system_reference','competitor_measurement','competitor_observation'}
AUDIENCE={'local','regional','national','global','mixed','internal'}
CRITICALITY={'primary','high_risk','secondary','supporting'}
EFFORT={'low','moderate','high','contextual'}
JOURNEY_STATUS={'passed','failed','partial','blocked','not_tested'}
AXES={'visual_craft','color_system','typography','composition','visual_coherence','audience_fit','orientation_clarity','journey_logic','friction','engagement_quality','effort_payoff','feedback_progress','relevance_personalization','trust','recovery','responsive_consistency','perceived_performance','accessibility_readability'}
CONFIDENCE={'confirmed','high','medium','low'}
KINDS={'gap','risk','opportunity','investigation','strength','comparative'}
FINDING_STATUS={'open','blocked','decision_required','retained_strength','not_applicable','resolved'}
SEVERITY={'critical','high','medium','low','informational'}
VERIFICATION={'observed','partially_observed','inferred','blocked'}
BASIS={'standard_requirement','observed_behavior','visual_craft','measured_comparison','user_research','user_sentiment','first_party_measurement','heuristic','design_system_convention','owner_context','aesthetic_preference'}
ACCESS={'source_repository','production_experience','competitor_measurement','user_sentiment','design_system','assistive_technology'}
PASSES={'ui_craft','ux_experience','competitive_calibration','accessibility_readability'}
PASS_STATUS={'passed','failed','partial','blocked','not_tested','not_applicable'}
VIEW_CLASSES={'narrow_mobile','wide_mobile','tablet','desktop','large_desktop','other'}
COVERAGE_STATUS={'observed','blocked','not_applicable'}
INPUT_MODES={'pointer_touch','keyboard','screen_reader','other'}
STATE_CLASSES={'default','focus','hover','active','disabled','loading','empty','validation','error','success','destructive','offline_timeout'}
DOMAINS={'ui.visual-craft','ui.color','ui.typography','ui.composition','ui.coherence','ui.responsive','ui.component-states','ux.orientation','ux.navigation','ux.journey','ux.friction','ux.engagement','ux.feedback','ux.progress','ux.relevance','ux.trust','ux.recovery','ux.performance-perception','ux.audience-fit','accessibility.readability','accessibility.keyboard','accessibility.semantics','competitive.calibration'}

def obj(v): return isinstance(v,dict)
def text(v): return isinstance(v,str) and bool(v.strip())
def slist(v): return [x for x in v if isinstance(x,str) and x.strip()] if isinstance(v,list) else []
def load(p,errors):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'{p.name} cannot load: {e}'); return None

def ids(rows,pattern,label,errors):
    out={}
    if not isinstance(rows,list): errors.append(f'{label} must be list'); return out
    for i,row in enumerate(rows):
        if not obj(row): errors.append(f'{label}[{i}] must be object'); continue
        ident=row.get('id')
        if not isinstance(ident,str) or not pattern.match(ident): errors.append(f'{label}[{i}].id invalid'); continue
        if ident in out: errors.append(f'duplicate {label} id {ident}')
        out[ident]=row
    return out

def refs(value,known,label,errors,nonempty=False):
    vals=slist(value)
    if not isinstance(value,list) or len(vals)!=len(value) or (nonempty and not vals): errors.append(f'{label} must be {"non-empty " if nonempty else ""}string list')
    for x in vals:
        if x not in known: errors.append(f'{label} references unknown id {x}')
    return vals

def validate(root:Path):
    errors=[]; f=load(root/'findings.json',errors); c=load(root/'coverage.json',errors)
    if not obj(f) or not obj(c): return errors or ['canonical files must be objects']
    if f.get('schema_version')!='ux-ui-teardown-v2': errors.append('findings schema_version must be ux-ui-teardown-v2')
    if c.get('schema_version')!='ux-ui-teardown-coverage-v2': errors.append('coverage schema_version must be ux-ui-teardown-coverage-v2')
    audit=f.get('audit') if obj(f.get('audit')) else {}; 
    if not audit: errors.append('audit must be object')
    required_audit=['project_name','project_locator','audited_revision','production_locator','production_revision_status','audit_start_date','audit_end_date','review_status','project_type','audience_scope','primary_user_groups','primary_goals','owner_context','competitor_benchmark_required','competitor_benchmark_reason']
    for k in required_audit:
        if k not in audit: errors.append(f'audit missing {k}')
    for k in ['project_name','project_locator','audited_revision','project_type','competitor_benchmark_reason']:
        if k in audit and not text(audit.get(k)): errors.append(f'audit.{k} must be non-empty text')
    if audit.get('review_status') not in {'complete','provisional'}: errors.append('audit.review_status invalid')
    if audit.get('production_revision_status') not in {'verified','unverified','not_applicable'}: errors.append('audit.production_revision_status invalid')
    if audit.get('audience_scope') not in AUDIENCE: errors.append('audit.audience_scope invalid')
    if not isinstance(audit.get('primary_user_groups'),list) or not slist(audit.get('primary_user_groups')): errors.append('audit.primary_user_groups must be non-empty string list')
    if not isinstance(audit.get('primary_goals'),list) or not slist(audit.get('primary_goals')): errors.append('audit.primary_goals must be non-empty string list')
    if not isinstance(audit.get('owner_context'),list) or len(slist(audit.get('owner_context')))!=len(audit.get('owner_context',[]) if isinstance(audit.get('owner_context'),list) else []): errors.append('audit.owner_context must be string list')
    if not isinstance(audit.get('competitor_benchmark_required'),bool): errors.append('audit.competitor_benchmark_required must be bool')

    evid=ids(f.get('evidence_sources'),PATTERNS['evidence'],'evidence_sources',errors)
    for eid,row in evid.items():
        if row.get('evidence_class') not in EVIDENCE_CLASSES: errors.append(f'{eid}.evidence_class invalid')
        for k in ['title','locator','accessed_at','summary']:
            if not text(row.get(k)): errors.append(f'{eid}.{k} must be non-empty text')
        if not isinstance(row.get('limitations'),list) or len(slist(row.get('limitations')))!=len(row.get('limitations',[]) if isinstance(row.get('limitations'),list) else []): errors.append(f'{eid}.limitations must be string list')

    comps=ids(f.get('competitor_set'),PATTERNS['competitor'],'competitor_set',errors)
    for cid,row in comps.items():
        if row.get('selection_status') not in {'measured','owner_supplied','reference_only'}: errors.append(f'{cid}.selection_status invalid')
        for k in ['name','locator','relevance_reason']:
            if not text(row.get(k)): errors.append(f'{cid}.{k} must be non-empty text')
        sel=refs(row.get('selection_evidence_ids'),set(evid),f'{cid}.selection_evidence_ids',errors,nonempty=row.get('selection_status')=='measured')
        refs(row.get('comparison_evidence_ids'),set(evid),f'{cid}.comparison_evidence_ids',errors)
        if not slist(row.get('surfaces_compared')): errors.append(f'{cid}.surfaces_compared must be non-empty string list')
        if row.get('selection_status')=='measured' and not any(evid.get(x,{}).get('evidence_class')=='competitor_measurement' for x in sel): errors.append(f'{cid} measured competitor requires competitor_measurement evidence')

    journeys=ids(f.get('journeys'),PATTERNS['journey'],'journeys',errors)
    for jid,row in journeys.items():
        if row.get('criticality') not in CRITICALITY: errors.append(f'{jid}.criticality invalid')
        if row.get('effort_budget') not in EFFORT: errors.append(f'{jid}.effort_budget invalid')
        if row.get('status') not in JOURNEY_STATUS: errors.append(f'{jid}.status invalid')
        for k in ['title','user_group','trigger','intended_outcome','engagement_intent','expected_payoff','context_notes']:
            if not text(row.get(k)): errors.append(f'{jid}.{k} must be non-empty text')
        if not slist(row.get('steps')): errors.append(f'{jid}.steps must be non-empty string list')
        refs(row.get('evidence_ids'),set(evid),f'{jid}.evidence_ids',errors,nonempty=True)
        for k in ['viewport_ids','input_modes','state_ids','limitations']:
            if not isinstance(row.get(k),list) or len(slist(row.get(k)))!=len(row.get(k,[]) if isinstance(row.get(k),list) else []): errors.append(f'{jid}.{k} must be string list')

    exps=ids(f.get('experience_assessments'),PATTERNS['experience'],'experience_assessments',errors)
    exps_by_journey={j:set() for j in journeys}; axes_seen=set(); comparative_refs=[]
    for xid,row in exps.items():
        if row.get('axis') not in AXES: errors.append(f'{xid}.axis invalid')
        axes_seen.add(row.get('axis'))
        if row.get('confidence') not in CONFIDENCE: errors.append(f'{xid}.confidence invalid')
        for k in ['surface_target','verdict','observation','reasoning','desired_direction']:
            if not text(row.get(k)): errors.append(f'{xid}.{k} must be non-empty text')
        jids=refs(row.get('journey_ids'),set(journeys),f'{xid}.journey_ids',errors)
        refs(row.get('evidence_ids'),set(evid),f'{xid}.evidence_ids',errors,nonempty=True)
        cids=refs(row.get('competitor_ids'),set(comps),f'{xid}.competitor_ids',errors)
        if cids: comparative_refs.append(set(cids))
        for j in jids: exps_by_journey.setdefault(j,set()).add(row.get('axis'))

    findings=ids(f.get('findings'),PATTERNS['finding'],'findings',errors)
    for fid,row in findings.items():
        if row.get('kind') not in KINDS: errors.append(f'{fid}.kind invalid')
        if row.get('status') not in FINDING_STATUS: errors.append(f'{fid}.status invalid')
        if row.get('severity') not in SEVERITY: errors.append(f'{fid}.severity invalid')
        if row.get('confidence') not in CONFIDENCE: errors.append(f'{fid}.confidence invalid')
        if row.get('verification_state') not in VERIFICATION: errors.append(f'{fid}.verification_state invalid')
        if row.get('judgment_basis') not in BASIS: errors.append(f'{fid}.judgment_basis invalid')
        dom=slist(row.get('domains'))
        if not dom or len(dom)!=len(row.get('domains',[]) if isinstance(row.get('domains'),list) else []) or any(x not in DOMAINS for x in dom): errors.append(f'{fid}.domains invalid')
        if row.get('judgment_basis')=='aesthetic_preference' and row.get('severity') not in {'low','informational'}: errors.append(f'{fid} aesthetic_preference cannot exceed low severity')
        if row.get('judgment_basis')=='visual_craft' and row.get('severity')=='critical': errors.append(f'{fid} visual_craft alone cannot be critical')
        cids=refs(row.get('competitor_ids'),set(comps),f'{fid}.competitor_ids',errors)
        if row.get('judgment_basis')=='measured_comparison' and not cids: errors.append(f'{fid} measured_comparison requires competitor_ids')
        if row.get('kind')=='strength' and (row.get('severity')!='informational' or row.get('status')!='retained_strength'): errors.append(f'{fid} strength must be informational retained_strength')
        for k in ['title','observed_condition','desired_condition','user_consequence','business_risk']:
            if not text(row.get(k)): errors.append(f'{fid}.{k} must be non-empty text')
        for k in ['surface_targets','acceptance_criteria','verification_methods']:
            if not slist(row.get(k)): errors.append(f'{fid}.{k} must be non-empty string list')
        refs(row.get('journey_ids'),set(journeys),f'{fid}.journey_ids',errors)
        refs(row.get('evidence_ids'),set(evid),f'{fid}.evidence_ids',errors,nonempty=True)
        for k in ['standard_refs','implementation_targets','preservation_constraints','dependencies','conflicts','non_goals']:
            if not isinstance(row.get(k),list) or len(slist(row.get(k)))!=len(row.get(k,[]) if isinstance(row.get(k),list) else []): errors.append(f'{fid}.{k} must be string list')
        if row.get('kind')!='strength' and row.get('status') not in {'not_applicable','resolved'} and not text(row.get('recommendation')): errors.append(f'{fid}.recommendation required')
        for dep in slist(row.get('dependencies')):
            if dep not in findings: errors.append(f'{fid} unknown dependency {dep}')
        for conf in slist(row.get('conflicts')):
            if conf not in findings: errors.append(f'{fid} unknown conflict {conf}')
            elif fid not in slist(findings[conf].get('conflicts')): errors.append(f'{fid} conflict with {conf} not symmetric')

    if c.get('review_status') not in {'complete','provisional'}: errors.append('coverage.review_status invalid')
    if c.get('review_status')!=audit.get('review_status'): errors.append('review_status mismatch')
    access=c.get('access') if isinstance(c.get('access'),list) else []
    if not isinstance(c.get('access'),list): errors.append('coverage.access must be list')
    cats=[]
    for i,row in enumerate(access):
        if not obj(row): errors.append(f'access[{i}] must be object'); continue
        cat=row.get('category'); cats.append(cat)
        if cat not in ACCESS: errors.append(f'access[{i}].category invalid')
        if row.get('status') not in {'available','partial','blocked','not_applicable'}: errors.append(f'access[{i}].status invalid')
        if not isinstance(row.get('material_to_complete'),bool): errors.append(f'access[{i}].material_to_complete must be bool')
        refs(row.get('evidence_ids'),set(evid),f'access[{i}].evidence_ids',errors)
    if set(cats)!=ACCESS or len(cats)!=len(ACCESS): errors.append('coverage.access must contain each category exactly once')

    passes=c.get('passes') if isinstance(c.get('passes'),list) else []
    if not isinstance(c.get('passes'),list): errors.append('coverage.passes must be list')
    pmap={}
    for i,row in enumerate(passes):
        if not obj(row): errors.append(f'passes[{i}] must be object'); continue
        pid=row.get('id')
        if pid in pmap: errors.append(f'duplicate pass {pid}')
        pmap[pid]=row
        if pid not in PASSES: errors.append(f'passes[{i}].id invalid')
        if row.get('materiality') not in {'defining','high','supporting'}: errors.append(f'{pid}.materiality invalid')
        if row.get('status') not in PASS_STATUS: errors.append(f'{pid}.status invalid')
        refs(row.get('finding_ids'),set(findings),f'{pid}.finding_ids',errors)
        refs(row.get('evidence_ids'),set(evid),f'{pid}.evidence_ids',errors)
    if set(pmap)!=PASSES: errors.append('coverage.passes must contain all four passes exactly once')

    viewports=ids(c.get('viewports'),PATTERNS['viewport'],'viewports',errors)
    observed_views={j:set() for j in journeys}
    for vid,row in viewports.items():
        if row.get('class') not in VIEW_CLASSES: errors.append(f'{vid}.class invalid')
        if row.get('status') not in COVERAGE_STATUS: errors.append(f'{vid}.status invalid')
        jids=refs(row.get('journey_ids'),set(journeys),f'{vid}.journey_ids',errors)
        ev=refs(row.get('evidence_ids'),set(evid),f'{vid}.evidence_ids',errors,nonempty=row.get('status')=='observed')
        if row.get('status')=='observed':
            for j in jids: observed_views.setdefault(j,set()).add(row.get('class'))

    input_rows=c.get('input_modes') if isinstance(c.get('input_modes'),list) else []
    if not isinstance(c.get('input_modes'),list): errors.append('coverage.input_modes must be list')
    observed_modes={j:set() for j in journeys}; seen_modes=set()
    for i,row in enumerate(input_rows):
        if not obj(row): errors.append(f'input_modes[{i}] must be object'); continue
        mode=row.get('mode')
        if mode not in INPUT_MODES: errors.append(f'input_modes[{i}].mode invalid')
        if mode in seen_modes: errors.append(f'duplicate input mode {mode}')
        seen_modes.add(mode)
        if row.get('status') not in COVERAGE_STATUS: errors.append(f'input_modes[{i}].status invalid')
        jids=refs(row.get('journey_ids'),set(journeys),f'input_modes[{i}].journey_ids',errors)
        refs(row.get('evidence_ids'),set(evid),f'input_modes[{i}].evidence_ids',errors,nonempty=row.get('status')=='observed')
        if row.get('status')=='observed':
            for j in jids: observed_modes.setdefault(j,set()).add(mode)

    states=ids(c.get('state_coverage'),PATTERNS['state'],'state_coverage',errors)
    for sid,row in states.items():
        if row.get('state') not in STATE_CLASSES: errors.append(f'{sid}.state invalid')
        jid=row.get('journey_id')
        if jid not in journeys: errors.append(f'{sid}.journey_id invalid')
        if row.get('status') not in COVERAGE_STATUS: errors.append(f'{sid}.status invalid')
        refs(row.get('viewport_ids'),set(viewports),f'{sid}.viewport_ids',errors,nonempty=row.get('status')=='observed')
        refs(row.get('evidence_ids'),set(evid),f'{sid}.evidence_ids',errors,nonempty=row.get('status')=='observed')
        modes=slist(row.get('input_modes'))
        if not isinstance(row.get('input_modes'),list) or any(x not in INPUT_MODES for x in modes): errors.append(f'{sid}.input_modes invalid')
        refs(row.get('finding_ids'),set(findings),f'{sid}.finding_ids',errors)

    limits=ids(c.get('material_limitations'),PATTERNS['limit'],'material_limitations',errors)
    for lid,row in limits.items():
        if row.get('status') not in {'open','resolved'}: errors.append(f'{lid}.status invalid')
        if not text(row.get('description')) or not text(row.get('completion_requirement')): errors.append(f'{lid} description/completion_requirement required')

    complete=audit.get('review_status')=='complete'
    interactive=audit.get('project_type') in {'website','web_app','saas','ecommerce','local_service','agency_professional_service'}
    benchmark_required=audit.get('competitor_benchmark_required') is True
    if complete:
        if any(obj(r) and r.get('material_to_complete') is True and r.get('status') in {'partial','blocked'} for r in access): errors.append('complete review has material access partial/blocked')
        if any(r.get('status')=='open' for r in limits.values()): errors.append('complete review cannot have open material limitations')
        for pid in ['ui_craft','ux_experience']:
            if pmap.get(pid,{}).get('status') not in {'passed','failed'}: errors.append(f'complete review requires completed {pid} pass')
        if benchmark_required:
            if pmap.get('competitive_calibration',{}).get('status') not in {'passed','failed'}: errors.append('complete review requires competitive calibration pass')
            measured=[x for x in comps.values() if x.get('selection_status')=='measured']
            if len(measured)<2: errors.append('complete benchmark-required review requires at least two measured competitors')
            if not any(len(x)>=2 for x in comparative_refs): errors.append('complete benchmark-required review requires a comparative assessment referencing at least two competitors')
        for axis in ['visual_craft','color_system','audience_fit']:
            if axis not in axes_seen: errors.append(f'complete review missing {axis} assessment')
        material=[(jid,j) for jid,j in journeys.items() if j.get('criticality') in {'primary','high_risk'}]
        for jid,j in material:
            if j.get('status') in {'partial','blocked','not_tested'}: errors.append(f'complete review has incomplete material journey {jid}')
            if not exps_by_journey.get(jid): errors.append(f'complete material journey {jid} has no experience assessment')
            if interactive:
                missing={'narrow_mobile','desktop'}-observed_views.get(jid,set())
                if missing: errors.append(f'complete material journey {jid} missing viewports: {sorted(missing)}')
                if 'pointer_touch' not in observed_modes.get(jid,set()): errors.append(f'complete material journey {jid} missing pointer/touch coverage')
        if interactive and not any(obj(r) and r.get('mode')=='keyboard' and r.get('status')=='observed' for r in input_rows): errors.append('complete interactive review requires representative keyboard coverage')
        if audit.get('production_locator') and audit.get('production_revision_status')=='unverified': errors.append('complete public review cannot have unverified production revision')
        if not any(row.get('evidence_class')=='rendered_observation' for row in evid.values()): errors.append('complete review requires rendered observation evidence')
    validator=c.get('validator')
    if not obj(validator) or validator.get('status') not in {'passed','pending'} or not text(validator.get('name')) or not text(validator.get('validated_at')): errors.append('coverage.validator invalid')
    return errors

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('root',type=Path); a=ap.parse_args(); errors=validate(a.root.resolve())
    if errors:
        print(f'UX/UI teardown validation failed with {len(errors)} error(s):')
        for e in errors[:150]: print('-',e)
        return 1
    print('ux-ui-teardown validation passed'); return 0
if __name__=='__main__': raise SystemExit(main())
