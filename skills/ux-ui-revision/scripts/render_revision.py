#!/usr/bin/env python3
"""Render deterministic UX/UI revision Markdown views from revision.json."""

from __future__ import annotations
import json,sys
from pathlib import Path

def render(root:Path):
    d=json.loads((root/"revision.json").read_text(encoding="utf-8"))
    readme=f"""# UX/UI Revision

- **Mode:** {d['mode']}
- **Source revision:** {d['source']['teardown_revision']}
- **Overall readiness:** {d['readiness']['overall']}
- **Highest evidence level:** {d['readiness']['highest_evidence_level']}

## Validation

```bash
python3 <skill-directory>/scripts/validate_ux_ui_revision.py <ux-ui-teardown-directory> <ux-ui-revision-directory>
```
"""
    decisions=["# Decisions",""]
    for x in d["decisions"]:
        decisions += [f"## {x['id']}",f"- **Question:** {x['question']}",f"- **Status:** {x['status']}",""]
    ledger=["# Implementation Ledger","","| Finding | Revalidation | Approval | Implementation | Preservation |","| --- | --- | --- | --- | --- |"]
    for f in d["findings"]:
        ledger.append(f"| {f['finding_id']} | {f['revalidation']} | {f['approval']} | {f['implementation_status']} | {f['preservation_status']} |")
    verification=["# Verification","",f"**Highest evidence level:** {d['readiness']['highest_evidence_level']}",""]
    for f in d["findings"]:
        verification += [f"## {f['finding_id']}",f"- Evidence: {', '.join(f['verification_evidence']) if f['verification_evidence'] else 'None recorded'}",""]
    convergence=["# Convergence","",f"**Status:** {d['convergence']['status']}",""]
    for f in d["convergence"]["findings"]:
        convergence += [f"- `{f['id']}` {f['severity']} / {f['status']} — {f['title']}"]
    return {
        "README.md":readme,
        "decisions.md":"\n".join(decisions).rstrip()+"\n",
        "implementation-ledger.md":"\n".join(ledger).rstrip()+"\n",
        "verification.md":"\n".join(verification).rstrip()+"\n",
        "convergence.md":"\n".join(convergence).rstrip()+"\n",
    }

def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
    for n,t in render(root).items(): (root/n).write_text(t,encoding="utf-8",newline="\n")
    print("rendered 5 UX/UI revision view(s)"); return 0
if __name__=="__main__": raise SystemExit(main())
