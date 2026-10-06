#!/usr/bin/env python3
"""Render deterministic Markdown views from ux-ui-revision v2 JSON."""
from __future__ import annotations
import argparse,json
from pathlib import Path
def render(root:Path):
    d=json.loads((root/'revision.json').read_text())
    read=f"# UX/UI revision\n\nMode: **{d['mode']}**  \nOverall: **{d['readiness']['overall']}**  \nSource revision: `{d['source']['teardown_revision']}`\n"
    dec=['# Decisions','']
    for x in d['decisions']:dec += [f"## {x['id']}",x['question'],'',f"Status: **{x['status']}**",'']
    led=['# Implementation ledger','']
    for x in d['findings']:led += [f"## {x['finding_id']}",f"Revalidation: **{x['revalidation']}** · Approval: **{x['approval']}** · Implementation: **{x['implementation_status']}** · Preservation: **{x['preservation_status']}**",'']
    ver=['# Verification','']
    for x in d['findings']:
        ver += [f"## {x['finding_id']}"]+[f"- {r.get('criterion')}: **{r.get('status')}**" for r in x.get('acceptance_results',[])]+['']
    conv=['# Convergence','',f"Status: **{d['convergence']['status']}**",'']
    for x in d['convergence']['findings']:conv += [f"- **{x['id']}** {x.get('severity')}: {x.get('title','')} — {x.get('status')}"]
    return {'README.md':read,'decisions.md':'\n'.join(dec)+'\n','implementation-ledger.md':'\n'.join(led)+'\n','verification.md':'\n'.join(ver)+'\n','convergence.md':'\n'.join(conv)+'\n'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);a=ap.parse_args();out=render(a.root.resolve())
    for n,t in out.items():(a.root/n).write_text(t,encoding='utf-8',newline='\n')
    print(f'rendered {len(out)} markdown file(s)');return 0
if __name__=='__main__':raise SystemExit(main())
