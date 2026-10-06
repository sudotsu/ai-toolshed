#!/usr/bin/env python3
"""Validate a UX/UI revision against its exact teardown handoff."""

from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

from validation_common import run_upstream_validator

AUTHORITY={"repository_edit","design_file_edit","cms_edit","public_content_publish","production_deploy","external_profile_change","analytics_mutation","paid_purchase","third_party_outreach","merge"}
REVALIDATION={"confirmed","changed","stale","already_resolved","not_applicable","blocked"}
APPROVAL={"pending","approved","deferred","rejected","accepted_risk","not_applicable"}
IMPLEMENTATION={"not_started","planned","in_progress","fixed","preserved","blocked","deferred","rejected","accepted_risk","not_applicable"}
PRESERVATION={"pending","preserved","regressed","approved_tradeoff","not_applicable"}
ACC={"passed","failed","pending","blocked","not_applicable"}
LEVELS=["source_inspection","rendered_experience","assistive_technology","published_experience","user_observation","first_party_measurement","business_outcome"]

def obj(x): return isinstance(x,dict)
def text(x): return isinstance(x,str) and bool(x.strip())
def slist(x): return isinstance(x,list) and all(text(y) for y in x)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def load(path,errors):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e: errors.append(f"{path.name} cannot load: {e}"); return None

def validate(teardown:Path,revision:Path,*,run_upstream:bool=True):
    errors=[]
    if run_upstream:
        ok, output = run_upstream_validator(teardown)
        if not ok:
            return ["ux-ui-teardown upstream validation failed: " + output]

    td=load(teardown/"findings.json",errors); cv=load(teardown/"coverage.json",errors); rv=load(revision/"revision.json",errors)
    if not obj(td) or not obj(cv) or not obj(rv): return errors or ["canonical documents must be objects"]
    if td.get("schema_version")!="ux-ui-teardown-v1": errors.append("upstream findings schema mismatch")
    if cv.get("schema_version")!="ux-ui-teardown-coverage-v1": errors.append("upstream coverage schema mismatch")
    if rv.get("schema_version")!="ux-ui-revision-v1": errors.append("revision schema_version must be ux-ui-revision-v1")
    mode=rv.get("mode")
    if mode not in {"planning-only","implementation","continuation"}: errors.append("revision mode invalid")
    src=rv.get("source")
    if not obj(src): errors.append("source must be object")
    else:
        if src.get("teardown_findings_digest")!=digest(teardown/"findings.json"): errors.append("source teardown digest mismatch")
        if src.get("teardown_revision")!=td.get("audit",{}).get("audited_revision"): errors.append("source teardown revision mismatch")

    auth=rv.get("authority")
    if not isinstance(auth,list): errors.append("authority must be list"); auth=[]
    actions=[]
    auth_map={}
    for i,a in enumerate(auth):
        if not obj(a): errors.append(f"authority[{i}] must be object"); continue
        action=a.get("action"); actions.append(action); auth_map[action]=a
        if action not in AUTHORITY: errors.append(f"authority[{i}].action invalid")
        if a.get("status") not in {"authorized","not_authorized","not_applicable"}: errors.append(f"authority[{i}].status invalid")
        if not isinstance(a.get("scope"),list) or not isinstance(a.get("evidence"),list): errors.append(f"authority[{i}] scope/evidence must be lists")
    if set(actions)!=AUTHORITY or len(actions)!=len(AUTHORITY): errors.append("authority must contain each action exactly once")

    source_findings={}
    for f in td.get("findings",[]) if isinstance(td.get("findings"),list) else []:
        if obj(f) and text(f.get("id")): source_findings[f["id"]]=f

    rows=rv.get("findings")
    if not isinstance(rows,list): errors.append("findings must be list"); rows=[]
    seen=set()
    for i,row in enumerate(rows):
        if not obj(row): errors.append(f"findings[{i}] must be object"); continue
        fid=row.get("finding_id")
        if fid in seen: errors.append(f"duplicate revision finding {fid}")
        seen.add(fid)
        srcf=source_findings.get(fid)
        if not srcf: errors.append(f"revision references unknown finding {fid}"); continue
        if row.get("original_status")!=srcf.get("status"): errors.append(f"{fid} original_status mismatch")
        if row.get("revalidation") not in REVALIDATION: errors.append(f"{fid}.revalidation invalid")
        if row.get("approval") not in APPROVAL: errors.append(f"{fid}.approval invalid")
        if row.get("implementation_status") not in IMPLEMENTATION: errors.append(f"{fid}.implementation_status invalid")
        if row.get("preservation_status") not in PRESERVATION: errors.append(f"{fid}.preservation_status invalid")
        for k in ("current_evidence","changed_targets","acceptance_results","verification_evidence"):
            if not isinstance(row.get(k),list): errors.append(f"{fid}.{k} must be list")
        if row.get("revalidation") in {"confirmed","changed","already_resolved"} and not row.get("current_evidence"): errors.append(f"{fid} revalidation requires current evidence")
        if row.get("revalidation") in {"stale","not_applicable"} and row.get("implementation_status")=="fixed": errors.append(f"{fid} stale/not_applicable cannot be fixed")
        if row.get("implementation_status")=="fixed":
            if row.get("approval")!="approved": errors.append(f"{fid} fixed requires approved")
            for j,r in enumerate(row.get("acceptance_results",[]) if isinstance(row.get("acceptance_results"),list) else []):
                if not obj(r) or r.get("status") not in ACC: errors.append(f"{fid}.acceptance_results[{j}] invalid")
                elif r.get("status") not in {"passed","not_applicable"}: errors.append(f"{fid} fixed has unmet acceptance criterion")
            if not row.get("verification_evidence"): errors.append(f"{fid} fixed requires verification evidence")
        if mode=="planning-only" and row.get("changed_targets"): errors.append(f"{fid} planning-only cannot record changed targets")
        if srcf.get("kind")=="strength" and row.get("implementation_status")!="preserved":
            errors.append(f"{fid} retained strength must remain preserved unless represented as an explicit owner-approved tradeoff")
        if row.get("preservation_status")=="approved_tradeoff" and row.get("approval")!="approved":
            errors.append(f"{fid} approved_tradeoff requires approved")
    if set(source_findings)!=seen: errors.append("revision must contain every teardown finding exactly once")

    conv=rv.get("convergence")
    open_material=[]
    if not obj(conv): errors.append("convergence must be object")
    else:
        if conv.get("status") not in {"not_started","in_progress","converged","blocked"}: errors.append("convergence.status invalid")
        cseen=set()
        for i,c in enumerate(conv.get("findings",[]) if isinstance(conv.get("findings"),list) else []):
            if not obj(c): errors.append(f"convergence.findings[{i}] must be object"); continue
            cid=c.get("id")
            if not isinstance(cid,str) or not re.match(r"^REVUX-\d{3}$",cid): errors.append(f"convergence.findings[{i}].id invalid")
            if cid in cseen: errors.append(f"duplicate convergence id {cid}")
            cseen.add(cid)
            if c.get("severity") not in {"critical","high","medium","low","informational"}: errors.append(f"{cid}.severity invalid")
            if c.get("status") not in {"open","fixed","accepted_risk","not_applicable"}: errors.append(f"{cid}.status invalid")
            if c.get("status")=="open" and c.get("severity") in {"critical","high","medium"}: open_material.append(cid)

    ready=rv.get("readiness")
    if not obj(ready): errors.append("readiness must be object")
    else:
        if ready.get("highest_evidence_level") not in LEVELS: errors.append("readiness.highest_evidence_level invalid")
        if ready.get("overall") not in {"planned","not_ready","ready","blocked"}: errors.append("readiness.overall invalid")
        if ready.get("deployment")=="performed" and auth_map.get("production_deploy",{}).get("status")!="authorized": errors.append("deployment performed without production_deploy authority")
        if ready.get("publication")=="performed" and auth_map.get("public_content_publish",{}).get("status")!="authorized": errors.append("publication performed without public_content_publish authority")
        if ready.get("overall")=="ready":
            if ready.get("implementation")!="ready" or ready.get("integration")!="ready": errors.append("overall ready requires implementation/integration ready")
            if open_material: errors.append(f"overall ready has open material convergence findings: {open_material}")
            for row in rows:
                if obj(row) and row.get("implementation_status") in {"not_started","planned","in_progress","blocked"}:
                    errors.append(f"overall ready has incomplete finding {row.get('finding_id')}")
                if obj(row) and row.get("preservation_status") not in {"preserved","approved_tradeoff","not_applicable"}:
                    errors.append(f"overall ready has unresolved preservation status for {row.get('finding_id')}")
    return errors

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("teardown",type=Path); ap.add_argument("revision",type=Path); a=ap.parse_args()
    errors=validate(a.teardown.resolve(),a.revision.resolve())
    if errors:
        print(f"UX/UI revision validation failed with {len(errors)} error(s):")
        for e in errors[:100]: print("-",e)
        return 1
    print("ux-ui-revision validation passed"); return 0
if __name__=="__main__": raise SystemExit(main())