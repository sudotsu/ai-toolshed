#!/usr/bin/env python3
"""Bootstrap a planning-only ux-ui-revision artifact from a validated teardown."""

from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

from validation_common import run_upstream_validator

AUTHORITY = ["repository_edit","design_file_edit","cms_edit","public_content_publish","production_deploy","external_profile_change","analytics_mutation","paid_purchase","third_party_outreach","merge"]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("teardown",type=Path); ap.add_argument("revision",type=Path)
    a=ap.parse_args()
    td=a.teardown.resolve(); out=a.revision.resolve()

    ok, upstream_output = run_upstream_validator(td)
    if not ok:
        print("ux-ui-teardown upstream validation failed: " + upstream_output, file=sys.stderr)
        return 1

    if out.exists() and any(out.iterdir()):
        print("refusing to overwrite non-empty revision directory",file=sys.stderr); return 1
    findings=json.loads((td/"findings.json").read_text(encoding="utf-8"))
    coverage=json.loads((td/"coverage.json").read_text(encoding="utf-8"))
    out.mkdir(parents=True,exist_ok=True); (out/"evidence").mkdir(exist_ok=True)
    rows=[]
    for f in findings["findings"]:
        rows.append({
            "finding_id":f["id"],
            "original_status":f["status"],
            "revalidation":"blocked",
            "approval":"not_applicable" if f["kind"]=="strength" else "pending",
            "implementation_status":"preserved" if f["kind"]=="strength" else "planned",
            "current_evidence":[],
            "changed_targets":[],
            "acceptance_results":[{"criterion":c,"status":"pending","evidence":[]} for c in f["acceptance_criteria"]],
            "verification_evidence":[],
            "preservation_status":"pending",
            "notes":"Planning scaffold; revalidate before implementation."
        })
    data={
        "schema_version":"ux-ui-revision-v1",
        "mode":"planning-only",
        "source":{
            "teardown_schema_version":findings["schema_version"],
            "coverage_schema_version":coverage["schema_version"],
            "teardown_revision":findings["audit"]["audited_revision"],
            "teardown_review_status":findings["audit"]["review_status"],
            "teardown_findings_digest":digest(td/"findings.json"),
        },
        "baseline":{"current_revision":"unrecorded","working_tree_state":"unrecorded","production_revision_status":"unrecorded","captured_at":"unrecorded","material_drift":False,"drift_notes":[]},
        "authority":[{"action":x,"status":"not_authorized","scope":[],"evidence":[]} for x in AUTHORITY],
        "findings":rows,
        "decisions":[],
        "convergence":{"reviewed_revision":"unrecorded","status":"not_started","findings":[]},
        "readiness":{"implementation":"not_started","integration":"not_started","deployment":"not_performed","publication":"not_performed","user_outcome":"unverified","business_outcome":"unverified","overall":"planned","highest_evidence_level":"source_inspection","limitations":["Planning scaffold only; current-state revalidation incomplete."]}
    }
    (out/"revision.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    from render_revision import render
    for name,text in render(out).items():
        (out/name).write_text(text,encoding="utf-8",newline="\n")
    print(f"bootstrapped {len(rows)} finding row(s)")
    return 0
if __name__=="__main__": raise SystemExit(main())