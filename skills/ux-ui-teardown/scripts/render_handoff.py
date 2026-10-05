#!/usr/bin/env python3
"""Render deterministic Markdown views from ux-ui-teardown canonical JSON."""

from __future__ import annotations
import json, sys
from pathlib import Path

GENERATED = ("README.md", "findings.md", "journey-map.md", "coverage.md")

def load(root: Path):
    return (
        json.loads((root / "findings.json").read_text(encoding="utf-8")),
        json.loads((root / "coverage.json").read_text(encoding="utf-8")),
    )

def md_list(items):
    return "\n".join(f"- {x}" for x in items) if items else "- None recorded"

def render(root: Path) -> dict[str, str]:
    findings, coverage = load(root)
    audit = findings["audit"]
    rows = []
    for f in findings["findings"]:
        rows.append(
            f"| {f['id']} | {f['severity']} | {f['status']} | "
            f"{', '.join(f['domains'])} | {f['title']} |"
        )
    readme = f"""# UX/UI Teardown — {audit['project_name']}

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
    finding_md = "# Findings\n\n| ID | Severity | Status | Domains | Finding |\n| --- | --- | --- | --- | --- |\n" + "\n".join(rows) + "\n"
    journey_lines = ["# Journey Map", ""]
    for j in findings["journeys"]:
        journey_lines += [
            f"## {j['id']} — {j['title']}",
            f"- **User group:** {j['user_group']}",
            f"- **Criticality:** {j['criticality']}",
            f"- **Status:** {j['status']}",
            f"- **Trigger:** {j['trigger']}",
            f"- **Intended outcome:** {j['intended_outcome']}",
            "",
            "### Steps",
            md_list(j["steps"]),
            "",
        ]
    cov_lines = ["# Coverage", "", f"**Review status:** {coverage['review_status']}", "", "## Modules", ""]
    for m in coverage["modules"]:
        cov_lines.append(f"- `{m['id']}` — {m['status']} ({m['materiality']})")
    cov_lines += ["", "## Material limitations", ""]
    for lim in coverage["material_limitations"]:
        cov_lines.append(f"- `{lim['id']}` — {lim['status']}: {lim['description']}")
    if not coverage["material_limitations"]:
        cov_lines.append("- None")
    return {
        "README.md": readme,
        "findings.md": finding_md,
        "journey-map.md": "\n".join(journey_lines).rstrip() + "\n",
        "coverage.md": "\n".join(cov_lines).rstrip() + "\n",
    }

def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    outputs = render(root)
    for name, text in outputs.items():
        (root / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"rendered {len(outputs)} UX/UI teardown view(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
