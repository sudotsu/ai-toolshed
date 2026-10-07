#!/usr/bin/env python3
"""Render deterministic Markdown views from ux-ui-revision v2 JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(root: Path):
    data = json.loads((root / "revision.json").read_text(encoding="utf-8"))
    readme = (
        "# UX/UI revision\n\n"
        f"Mode: **{data['mode']}**  \n"
        f"Overall: **{data['readiness']['overall']}**  \n"
        f"Source revision: `{data['source']['teardown_revision']}`\n"
    )

    decisions = ["# Decisions", ""]
    for decision in data["decisions"]:
        decisions += [
            f"## {decision['id']}",
            decision["question"],
            "",
            f"Status: **{decision['status']}**",
            "",
        ]

    ledger = ["# Implementation ledger", ""]
    for finding in data["findings"]:
        ledger += [
            f"## {finding['finding_id']}",
            (
                f"Revalidation: **{finding['revalidation']}** · "
                f"Approval: **{finding['approval']}** · "
                f"Implementation: **{finding['implementation_status']}** · "
                f"Preservation: **{finding['preservation_status']}**"
            ),
            "",
        ]

    verification = ["# Verification", ""]
    for finding in data["findings"]:
        verification.append(f"## {finding['finding_id']}")
        for result in finding.get("acceptance_results", []):
            evidence_refs = result.get("evidence", []) if isinstance(result, dict) else []
            evidence_text = f" — evidence: {', '.join(f'`{ref}`' for ref in evidence_refs)}" if evidence_refs else ""
            verification.append(f"- {result.get('criterion')}: **{result.get('status')}**{evidence_text}")
        evidence_rows = finding.get("verification_evidence", [])
        if evidence_rows:
            verification += ["", "Evidence levels:"]
            for evidence in evidence_rows:
                if not isinstance(evidence, dict):
                    continue
                locator = f" — {evidence.get('locator')}" if evidence.get("locator") else ""
                verification.append(f"- `{evidence.get('ref')}`: **{evidence.get('level')}**{locator}")
        verification.append("")

    convergence = ["# Convergence", "", f"Status: **{data['convergence']['status']}**", ""]
    for finding in data["convergence"]["findings"]:
        convergence.append(
            f"- **{finding['id']}** {finding.get('severity')}: {finding.get('title', '')} — {finding.get('status')}"
        )

    return {
        "README.md": readme,
        "decisions.md": "\n".join(decisions) + "\n",
        "implementation-ledger.md": "\n".join(ledger) + "\n",
        "verification.md": "\n".join(verification) + "\n",
        "convergence.md": "\n".join(convergence) + "\n",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    output = render(args.root.resolve())
    for name, rendered in output.items():
        (args.root / name).write_text(rendered, encoding="utf-8", newline="\n")
    print(f"rendered {len(output)} markdown file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
