#!/usr/bin/env python3
"""Render deterministic Markdown views from ux-ui-teardown canonical JSON."""
from __future__ import annotations
import json, sys
from pathlib import Path

GENERATED=("README.md","findings.md","journey-map.md","coverage.md")

def load(root: Path):
    return json.loads((root/"findings.json").read_text(encoding="utf-8")), json.loads((root/"coverage.json").read_text(encoding="utf-8"))

def md_list(items): return "\n".join(f"- {x}" for x in items) if items else "- None recorded"

def render(root: Path) -> dict[str,str]:
    findings,coverage=load(root); audit=findings["audit"]
    rows=[f"| {f['id']} | {f['severity']} | {f['status']} | {', '.join(f['domains'])} | {f['title']} |" for f in findings["findings"]]
    readme=f"""# UX/UI Teardown — {audit['project_name']}

- **Audited revision:** {audit['audited_revision']}
- **Production locator:** {audit['production_locator']}
- **Production revision status:** {audit['production_revision_status']}
- **Audit dates:** {audit['audit_start_date']} → {audit['audit_end_date']}
- **Review status:** {audit['review_status']}
- **Canonical files:** `findings.json`, `coverage.json`

## Primary goals

{md_list(audit['primary_goals'])}

## Validation

```bash
python3 <skill-directory>/scripts/render_handoff.py <ux-ui-teardown-directory>
python3 <skill-directory>/scripts/validate_ux_ui_teardown.py <ux-ui-teardown-directory>
```
"""
    finding_md="# Findings\n\n| ID | Severity | Status | Domains | Finding |\n| --- | --- | --- | --- | --- |\n"+"\n".join(rows)+"\n"
    journey_lines=["# Journey Map",""]
    for j in findings["journeys"]:
        journey_lines += [f"## {j['id']} — {j['title']}",f"- **User group:** {j['user_group']}",f"- **Criticality:** {j['criticality']}",f"- **Status:** {j['status']}",f"- **Trigger:** {j['trigger']}",f"- **Intended outcome:** {j['intended_outcome']}",f"- **Required states:** {', '.join(j['required_states'])}",f"- **Viewports:** {', '.join(j['viewport_ids'])}",f"- **Input modes:** {', '.join(j['input_modes'])}","","### Steps",md_list(j["steps"]),""]
    cov=["# Coverage","",f"**Review status:** {coverage['review_status']}","","## Modules",""]
    cov += [f"- `{m['id']}` — {m['status']} ({m['materiality']})" for m in coverage["modules"]]
    cov += ["","## Viewports","", "| ID | Class | Size | Status | Journeys |", "| --- | --- | --- | --- | --- |"]
    cov += [f"| {v['id']} | {v['class']} | {v['width']}×{v['height']} | {v['status']} | {', '.join(v['journey_ids'])} |" for v in coverage["viewports"]]
    cov += ["","## Input modes",""]
    cov += [f"- `{m['mode']}` — {m['status']}; journeys: {', '.join(m['journey_ids'])}" for m in coverage["input_modes"]]
    cov += ["","## State instances","", "| ID | State | Label | Journey | Step | Surface | Status |", "| --- | --- | --- | --- | --- | --- | --- |"]
    cov += [f"| {s['id']} | {s['state']} | {s['label']} | {s['journey_id']} | {s['step']} | {s['surface_target']} | {s['status']} |" for s in coverage["state_coverage"]]
    cov += ["","## Material limitations",""]
    cov += [f"- `{lim['id']}` — {lim['status']}: {lim['description']}" for lim in coverage["material_limitations"]] or ["- None"]
    return {"README.md":readme,"findings.md":finding_md,"journey-map.md":"\n".join(journey_lines).rstrip()+"\n","coverage.md":"\n".join(cov).rstrip()+"\n"}

def main()->int:
    root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve(); outputs=render(root)
    for name,text in outputs.items(): (root/name).write_text(text,encoding="utf-8",newline="\n")
    print(f"rendered {len(outputs)} UX/UI teardown view(s)"); return 0
if __name__=="__main__": raise SystemExit(main())
