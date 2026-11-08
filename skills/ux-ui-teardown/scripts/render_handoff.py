#!/usr/bin/env python3
"""Render deterministic Markdown views from ux-ui-teardown v2 JSON."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def load(root,name): return json.loads((root/name).read_text(encoding='utf-8'))
def bullets(items): return '\n'.join(f'- {x}' for x in items) if items else '- None recorded'
def render(root:Path):
    f=load(root,'findings.json'); c=load(root,'coverage.json'); audit=f['audit']
    overview=f"# UX/UI teardown — {audit['project_name']}\n\nStatus: **{audit['review_status']}**  \nAudience: **{audit['audience_scope']}**  \nRevision: `{audit['audited_revision']}`\n\n## Primary goals\n{bullets(audit['primary_goals'])}\n"
    findings=['# Findings','']
    for x in sorted(f['findings'],key=lambda r:(['critical','high','medium','low','informational'].index(r['severity']),r['id'])):
        findings += [f"## {x['id']} — {x['title']}",f"**{x['severity']} · {x['judgment_basis']} · {x['status']}**",'',x['observed_condition'],'',f"**Why it matters:** {x['user_consequence']}",'',f"**Recommendation:** {x.get('recommendation') or 'Preserve current strength.'}",'']
    journeys=['# Journey map','']
    for j in f['journeys']:
        journeys += [f"## {j['id']} — {j['title']}",f"Criticality: **{j['criticality']}** · Effort budget: **{j['effort_budget']}**",'',f"Trigger: {j['trigger']}",f"Outcome: {j['intended_outcome']}",'',bullets(j['steps']),'']
    exp=['# Experience assessment','']
    for x in f['experience_assessments']:
        exp += [f"## {x['id']} — {x['axis']}",f"Surface: **{x['surface_target']}** · Confidence: **{x['confidence']}**",'',x['observation'],'',x['reasoning'],'',f"Direction: {x['desired_direction']}",'']
    bench=['# Competitive calibration','',f"Required: **{audit['competitor_benchmark_required']}**",'']
    for x in f['competitor_set']:
        bench += [f"## {x['id']} — {x['name']}",f"Selection: **{x['selection_status']}**",'',x['relevance_reason'],'',f"Surfaces: {', '.join(x['surfaces_compared'])}",'']
    cov=['# Coverage','',f"Review status: **{c['review_status']}**",'','## Passes']
    for p in c['passes']: cov.append(f"- **{p['id']}** — {p['status']} ({p['materiality']})")
    cov += ['','## Access']
    for a in c['access']: cov.append(f"- **{a['category']}** — {a['status']} · material={a['material_to_complete']}")
    return {'README.md':overview,'findings.md':'\n'.join(findings)+'\n','journey-map.md':'\n'.join(journeys)+'\n','experience.md':'\n'.join(exp)+'\n','benchmark.md':'\n'.join(bench)+'\n','coverage.md':'\n'.join(cov)+'\n'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); a=ap.parse_args(); out=render(a.root.resolve())
    for name,text in out.items(): (a.root/name).write_text(text,encoding='utf-8',newline='\n')
    print(f'rendered {len(out)} markdown file(s)'); return 0
if __name__=='__main__': raise SystemExit(main())
