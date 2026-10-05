#!/usr/bin/env python3
"""Validate ux-ui-teardown canonical artifacts without crashing on malformed input."""

from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any

FINDING_ID = re.compile(r"^UXUI-\d{3}$")
EVID_ID = re.compile(r"^EVID-\d{3}$")
JOURNEY_ID = re.compile(r"^JOURNEY-\d{3}$")
LIMIT_ID = re.compile(r"^LIMIT-\d{3}$")

SEVERITIES = {"critical","high","medium","low","informational"}
CONFIDENCE = {"confirmed","high","medium","low"}
VERIFICATION = {"observed","partially_observed","inferred","blocked"}
KINDS = {"gap","risk","opportunity","investigation","strength","cross_domain"}
STATUSES = {"open","blocked","decision_required","retained_strength","not_applicable","resolved"}
BASIS = {"standard_requirement","observed_behavior","user_research","first_party_measurement","heuristic","design_system_convention","aesthetic_preference"}
EVIDENCE_CLASSES = {"source_inspection","rendered_observation","interaction_reproduction","standard_reference","automated_measurement","user_research","first_party_analytics","stakeholder_context","design_system_reference"}
DOMAINS = {
"ux.orientation","ux.information-architecture","ux.navigation","ux.discoverability","ux.task-flow","ux.forms","ux.feedback","ux.error-recovery","ux.cognitive-load","ux.trust","ux.conversion",
"ui.visual-hierarchy","ui.typography","ui.spacing","ui.color","ui.layout","ui.consistency","ui.responsive","ui.motion","ui.component-states",
"accessibility.semantics","accessibility.keyboard","accessibility.focus","accessibility.contrast","accessibility.target-size","accessibility.reflow","accessibility.motion",
"system.design-system","system.performance-perception"
}
MODULES = {
"orientation_comprehension","information_architecture_navigation","interaction_affordance_feedback","task_flow_forms_recovery","responsive_adaptive_layout",
"accessibility_semantics_keyboard","visual_hierarchy_legibility","trust_conversion","design_system_consistency","performance_perception"
}
ACCESS = {"source_repository","production_experience","analytics","user_research","design_system","assistive_technology"}

def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required file: {path.name}")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name} invalid JSON: {exc}")
    return None

def is_nonempty_text(v): return isinstance(v, str) and bool(v.strip())
def string_list(v): return isinstance(v, list) and all(is_nonempty_text(x) for x in v)
def obj(v): return isinstance(v, dict)

def exact_keys(d, keys, label, errors):
    if not obj(d):
        errors.append(f"{label} must be an object"); return False
    missing = sorted(set(keys)-set(d))
    extra = sorted(set(d)-set(keys))
    if missing: errors.append(f"{label} missing keys: {missing}")
    if extra: errors.append(f"{label} unexpected keys: {extra}")
    return not missing and not extra

def unique_ids(items, pattern, label, errors):
    seen=set(); out={}
    if not isinstance(items, list):
        errors.append(f"{label} must be a list"); return out
    for i,item in enumerate(items):
        if not obj(item):
            errors.append(f"{label}[{i}] must be an object"); continue
        ident=item.get("id")
        if not isinstance(ident,str) or not pattern.match(ident):
            errors.append(f"{label}[{i}].id invalid: {ident!r}"); continue
        if ident in seen: errors.append(f"{label} duplicate id: {ident}")
        seen.add(ident); out[ident]=item
    return out

def cycle_check(findings, errors):
    graph={}
    for fid,f in findings.items():
        deps=f.get("dependencies", [])
        graph[fid]=[x for x in deps if isinstance(x,str) and x in findings]
    visiting=set(); visited=set()
    def dfs(n,path):
        if n in visiting:
            errors.append("dependency cycle: " + " -> ".join(path+[n])); return
        if n in visited: return
        visiting.add(n)
        for d in graph.get(n,[]): dfs(d,path+[n])
        visiting.remove(n); visited.add(n)
    for n in graph: dfs(n,[])

def validate(root: Path) -> list[str]:
    errors=[]
    fdoc=load_json(root/"findings.json", errors)
    cdoc=load_json(root/"coverage.json", errors)
    if not obj(fdoc) or not obj(cdoc): return errors or ["canonical files must be objects"]
    exact_keys(fdoc, {"schema_version","audit","evidence_sources","journeys","findings"}, "findings.json", errors)
    exact_keys(cdoc, {"schema_version","review_status","access","modules","viewports","input_modes","state_coverage","material_limitations","validator"}, "coverage.json", errors)
    if fdoc.get("schema_version")!="ux-ui-teardown-v1": errors.append("findings schema_version must be ux-ui-teardown-v1")
    if cdoc.get("schema_version")!="ux-ui-teardown-coverage-v1": errors.append("coverage schema_version must be ux-ui-teardown-coverage-v1")

    audit=fdoc.get("audit")
    audit_keys={"project_name","project_locator","audited_revision","production_locator","production_revision_status","audit_start_date","audit_end_date","review_status","project_type","primary_user_groups","primary_goals"}
    if exact_keys(audit,audit_keys,"audit",errors):
        for k in ("project_name","project_locator","audited_revision","production_locator","project_type"):
            if not is_nonempty_text(audit.get(k)): errors.append(f"audit.{k} must be non-empty text")
        if audit.get("review_status") not in {"complete","provisional"}: errors.append("audit.review_status invalid")
        if audit.get("production_revision_status") not in {"verified","unverified","not_applicable"}: errors.append("audit.production_revision_status invalid")
        if not string_list(audit.get("primary_user_groups")): errors.append("audit.primary_user_groups must be non-empty strings")
        if not string_list(audit.get("primary_goals")): errors.append("audit.primary_goals must be non-empty strings")

    evid=unique_ids(fdoc.get("evidence_sources"),EVID_ID,"evidence_sources",errors)
    for eid,e in evid.items():
        exact_keys(e,{"id","evidence_class","title","locator","accessed_at","volatile","summary","limitations"},eid,errors)
        if e.get("evidence_class") not in EVIDENCE_CLASSES: errors.append(f"{eid}.evidence_class invalid")
        for k in ("title","locator","accessed_at","summary"):
            if not is_nonempty_text(e.get(k)): errors.append(f"{eid}.{k} must be non-empty text")
        if not isinstance(e.get("volatile"),bool): errors.append(f"{eid}.volatile must be boolean")
        if not isinstance(e.get("limitations"),list): errors.append(f"{eid}.limitations must be a list")

    journeys=unique_ids(fdoc.get("journeys"),JOURNEY_ID,"journeys",errors)
    for jid,j in journeys.items():
        keys={"id","title","user_group","trigger","intended_outcome","criticality","entry_points","steps","required_states","viewport_ids","input_modes","evidence_ids","status","limitations"}
        exact_keys(j,keys,jid,errors)
        if j.get("criticality") not in {"primary","secondary","supporting","high_risk"}: errors.append(f"{jid}.criticality invalid")
        if j.get("status") not in {"passed","failed","partial","blocked","not_tested"}: errors.append(f"{jid}.status invalid")
        for k in ("title","user_group","trigger","intended_outcome"):
            if not is_nonempty_text(j.get(k)): errors.append(f"{jid}.{k} must be non-empty text")
        for k in ("entry_points","steps","required_states","viewport_ids","input_modes","evidence_ids","limitations"):
            if not string_list(j.get(k)) and not (k=="limitations" and j.get(k)==[]): errors.append(f"{jid}.{k} must be a string list")
        for eid in j.get("evidence_ids",[]) if isinstance(j.get("evidence_ids"),list) else []:
            if eid not in evid: errors.append(f"{jid} references unknown evidence {eid}")
        if j.get("criticality") in {"primary","high_risk"} and not j.get("evidence_ids"): errors.append(f"{jid} material journey requires evidence")

    findings=unique_ids(fdoc.get("findings"),FINDING_ID,"findings",errors)
    for fid,f in findings.items():
        keys={"id","title","kind","domains","status","severity","confidence","verification_state","judgment_basis","standard_refs","journey_ids","surface_targets","evidence_ids","observed_condition","desired_condition","user_consequence","business_risk","recommendation","acceptance_criteria","verification_methods","implementation_targets","preservation_constraints","dependencies","conflicts","non_goals"}
        exact_keys(f,keys,fid,errors)
        if f.get("kind") not in KINDS: errors.append(f"{fid}.kind invalid")
        if f.get("status") not in STATUSES: errors.append(f"{fid}.status invalid")
        if f.get("severity") not in SEVERITIES: errors.append(f"{fid}.severity invalid")
        if f.get("confidence") not in CONFIDENCE: errors.append(f"{fid}.confidence invalid")
        if f.get("verification_state") not in VERIFICATION: errors.append(f"{fid}.verification_state invalid")
        if f.get("judgment_basis") not in BASIS: errors.append(f"{fid}.judgment_basis invalid")
        if not string_list(f.get("domains")) or not f.get("domains") or any(x not in DOMAINS for x in f.get("domains",[]) if isinstance(x,str)): errors.append(f"{fid}.domains invalid")
        if f.get("judgment_basis")=="aesthetic_preference" and f.get("severity") not in {"low","informational"}: errors.append(f"{fid} aesthetic_preference cannot exceed low severity")
        if f.get("judgment_basis")=="heuristic" and f.get("severity")=="critical": errors.append(f"{fid} heuristic alone cannot be critical")
        if f.get("judgment_basis")=="standard_requirement" and (not string_list(f.get("standard_refs")) or not f.get("standard_refs")): errors.append(f"{fid} standard_requirement requires standard_refs")
        if f.get("kind")=="strength":
            if f.get("severity")!="informational" or f.get("status")!="retained_strength": errors.append(f"{fid} strength must be informational retained_strength")
        for k in ("title","observed_condition","desired_condition","user_consequence","business_risk"):
            if not is_nonempty_text(f.get(k)): errors.append(f"{fid}.{k} must be non-empty text")
        for k in ("journey_ids","surface_targets","evidence_ids","acceptance_criteria","verification_methods"):
            if not string_list(f.get(k)): errors.append(f"{fid}.{k} must be non-empty string list")
        for k in ("standard_refs","implementation_targets","preservation_constraints","dependencies","conflicts","non_goals"):
            if not isinstance(f.get(k),list) or not all(is_nonempty_text(x) for x in f.get(k,[])): errors.append(f"{fid}.{k} must be a string list")
        if f.get("kind")!="strength" and f.get("status") not in {"not_applicable","resolved"} and not is_nonempty_text(f.get("recommendation")): errors.append(f"{fid}.recommendation required")
        for eid in f.get("evidence_ids",[]) if isinstance(f.get("evidence_ids"),list) else []:
            if eid not in evid: errors.append(f"{fid} references unknown evidence {eid}")
        for jid in f.get("journey_ids",[]) if isinstance(f.get("journey_ids"),list) else []:
            if jid not in journeys: errors.append(f"{fid} references unknown journey {jid}")
        for dep in f.get("dependencies",[]) if isinstance(f.get("dependencies"),list) else []:
            if not isinstance(dep,str):
                errors.append(f"{fid} dependencies must contain only finding id strings")
                continue
            if dep not in findings: errors.append(f"{fid} references unknown dependency {dep}")
            if dep==fid: errors.append(f"{fid} cannot depend on itself")
        for conflict in f.get("conflicts",[]) if isinstance(f.get("conflicts"),list) else []:
            if not isinstance(conflict,str):
                errors.append(f"{fid} conflicts must contain only finding id strings")
                continue
            if conflict not in findings: errors.append(f"{fid} references unknown conflict {conflict}")
            elif fid not in findings[conflict].get("conflicts",[]): errors.append(f"{fid} conflict with {conflict} is not symmetric")
    cycle_check(findings,errors)

    if cdoc.get("review_status") not in {"complete","provisional"}: errors.append("coverage.review_status invalid")
    if obj(audit) and cdoc.get("review_status") != audit.get("review_status"): errors.append("review_status mismatch between canonical files")

    access=cdoc.get("access")
    if not isinstance(access,list): errors.append("coverage.access must be a list"); access=[]
    cats=[]
    for i,a in enumerate(access):
        if not obj(a): errors.append(f"access[{i}] must be object"); continue
        exact_keys(a,{"category","status","material_to_comprehensive","evidence_ids","limitations","next_step"},f"access[{i}]",errors)
        cat=a.get("category"); cats.append(cat)
        if cat not in ACCESS: errors.append(f"access[{i}].category invalid")
        if a.get("status") not in {"available","partial","blocked","not_applicable"}: errors.append(f"access[{i}].status invalid")
        if not isinstance(a.get("material_to_comprehensive"),bool): errors.append(f"access[{i}].material_to_comprehensive must be bool")
        if not isinstance(a.get("evidence_ids"),list): errors.append(f"access[{i}].evidence_ids must be list")
        if not isinstance(a.get("limitations"),list): errors.append(f"access[{i}].limitations must be list")
    if set(cats)!=ACCESS or len(cats)!=len(ACCESS): errors.append("coverage.access must contain each access category exactly once")

    modules=cdoc.get("modules")
    if not isinstance(modules,list): errors.append("coverage.modules must be a list"); modules=[]
    mids=[]
    for i,m in enumerate(modules):
        if not obj(m): errors.append(f"modules[{i}] must be object"); continue
        exact_keys(m,{"id","materiality","status","finding_ids","evidence_ids","limitations"},f"modules[{i}]",errors)
        mid=m.get("id"); mids.append(mid)
        if mid not in MODULES: errors.append(f"modules[{i}].id invalid")
        if m.get("materiality") not in {"defining","high","medium","low"}: errors.append(f"{mid}.materiality invalid")
        if m.get("status") not in {"passed","failed","partial","blocked","not_tested","not_applicable"}: errors.append(f"{mid}.status invalid")
        for fid in m.get("finding_ids",[]) if isinstance(m.get("finding_ids"),list) else []:
            if fid not in findings: errors.append(f"{mid} references unknown finding {fid}")
    if set(mids)!=MODULES or len(mids)!=len(MODULES): errors.append("coverage.modules must contain each module exactly once")

    viewports=cdoc.get("viewports")
    if not isinstance(viewports,list): errors.append("coverage.viewports must be a list"); viewports=[]
    observed_classes=set()
    for i,v in enumerate(viewports):
        if not obj(v): errors.append(f"viewports[{i}] must be object"); continue
        exact_keys(v,{"id","label","width","height","class","status","journey_ids","evidence_ids","limitations"},f"viewports[{i}]",errors)
        if v.get("status")=="observed": observed_classes.add(v.get("class"))
        if not isinstance(v.get("width"),int) or isinstance(v.get("width"),bool) or v.get("width",0)<=0: errors.append(f"viewports[{i}].width invalid")
        if not isinstance(v.get("height"),int) or isinstance(v.get("height"),bool) or v.get("height",0)<=0: errors.append(f"viewports[{i}].height invalid")

    input_modes=cdoc.get("input_modes")
    if not isinstance(input_modes,list): errors.append("coverage.input_modes must be a list"); input_modes=[]
    observed_modes={m.get("mode") for m in input_modes if obj(m) and m.get("status")=="observed"}

    limits=unique_ids(cdoc.get("material_limitations"),LIMIT_ID,"material_limitations",errors)
    complete = obj(audit) and audit.get("review_status")=="complete"
    interactive_web = obj(audit) and audit.get("project_type") in {"website","web_app","saas","ecommerce","local_service","agency_professional_service"}
    if complete:
        if any(l.get("status")=="open" for l in limits.values()): errors.append("complete review cannot have open material limitations")
        for m in modules:
            if obj(m) and m.get("materiality") in {"defining","high"} and m.get("status") in {"partial","blocked","not_tested"}:
                errors.append(f"complete review has incomplete material module {m.get('id')}")
        for j in journeys.values():
            if j.get("criticality") in {"primary","high_risk"} and j.get("status") in {"partial","blocked","not_tested"}:
                errors.append(f"complete review has incomplete material journey {j.get('id')}")
        if interactive_web and not {"narrow_mobile","desktop"}.issubset(observed_classes):
            errors.append("complete interactive web review requires observed narrow_mobile and desktop")
        if interactive_web and not {"pointer_touch","keyboard"}.issubset(observed_modes):
            errors.append("complete interactive web review requires observed pointer_touch and keyboard")
        if audit.get("production_locator") and audit.get("production_revision_status")=="unverified":
            errors.append("complete public review cannot have unverified production revision")

    validator=cdoc.get("validator")
    if not obj(validator): errors.append("coverage.validator must be object")
    else:
        exact_keys(validator,{"name","status","validated_at"},"coverage.validator",errors)
        if complete and validator.get("status")!="passed": errors.append("complete review requires validator.status passed")
    return errors

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    args=parser.parse_args()
    errors=validate(args.root.resolve())
    if errors:
        print(f"UX/UI teardown validation failed with {len(errors)} error(s):")
        for e in errors[:100]: print(f"- {e}")
        return 1
    print("ux-ui-teardown validation passed")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
