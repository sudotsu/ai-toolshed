#!/usr/bin/env python3
"""Generate canonical human-readable views from revision.json and findings.json."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from validation_common import canonical_digest


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _pipe(values: list[str]) -> str:
    return " | ".join(values) or "None"


def render_implementation_ledger(teardown: dict[str, Any], revision: dict[str, Any]) -> str:
    originals = {
        item["id"]: item
        for item in teardown.get("findings", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    sections: list[str] = ["# Implementation ledger", ""]
    for item in revision.get("findings", []):
        finding_id = item["id"]
        original = originals[finding_id]
        acceptance = _pipe([
            f"{result['criterion']} => {result['status']} => {result['evidence']}"
            for result in item.get("acceptance_results", [])
        ])
        sections.extend([
            f"## {finding_id} — {original['title']}",
            "",
            f"- **Approval:** {item['approval']}",
            f"- **Teardown verification state:** {original.get('verification_state', 'legacy-not-recorded')}",
            f"- **Revalidation:** {item['revalidation']}",
            f"- **Disposition:** {item['disposition']}",
            f"- **Sequence:** {item['sequence']}",
            f"- **Reason:** {item['reason']}",
            f"- **Files changed:** {_pipe(item.get('files_changed', []))}",
            f"- **Acceptance results:** {acceptance}",
            f"- **Verification:** {_pipe(item.get('verification', []))}",
            f"- **Notes:** {_pipe(item.get('notes', []))}",
            f"- **Revision record digest:** {canonical_digest(item)}",
            "",
        ])
    sections.extend(["# Convergence findings", ""])
    for item in revision.get("convergence_findings", []):
        sections.extend([
            f"### {item['id']} — {item['title']}",
            "",
            f"- **Source:** {item['source']}",
            f"- **Severity:** {item['severity']}",
            f"- **Status:** {item['status']}",
            f"- **Reason:** {item['reason']}",
            f"- **Files changed:** {_pipe(item.get('files_changed', []))}",
            f"- **Verification:** {_pipe(item.get('verification', []))}",
            f"- **Convergence record digest:** {canonical_digest(item)}",
            "",
        ])
    return "\n".join(sections).rstrip() + "\n"


def render_readme(teardown: dict[str, Any], revision: dict[str, Any]) -> str:
    originals = {
        item["id"]: item
        for item in teardown.get("findings", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    findings = revision.get("findings", [])
    dispositions = Counter(item.get("disposition", "unknown") for item in findings)
    state = revision.get("final_state", {})
    delivery = state.get("delivery", {})
    attention: list[str] = []
    for item in findings:
        if item.get("approval") == "deferred" or item.get("disposition") == "blocked":
            title = originals.get(item.get("id"), {}).get("title", "Unknown finding")
            attention.append(
                f"- **{item.get('id')} — {title}:** approval `{item.get('approval')}`, "
                f"disposition `{item.get('disposition')}` — {item.get('reason')}"
            )
    summary_rows = [
        f"| `{name}` | {count} |"
        for name, count in sorted(dispositions.items())
    ] or ["| None | 0 |"]
    attention_lines = attention or ["No deferred or blocked teardown findings are recorded."]
    return f"""# Project Revision

**Project:** {revision.get('project')}  
**Teardown revision:** `{revision.get('teardown_audited_revision')}`  
**Implementation start:** `{revision.get('implementation_start_revision')}`  
**Implementation endpoint:** `{revision.get('implementation_end_revision')}`  
**Revision status:** `{revision.get('revision_status')}`  
**Review convergence:** `{state.get('review_convergence')}`  
**Merge readiness:** `{state.get('merge_readiness')}`  
**Release readiness:** `{state.get('release_readiness')}`

## Start here

1. [Decisions and scope](00-decisions-and-scope.md)
2. [Baseline and revalidation](01-baseline-and-revalidation.md)
3. [Dependency-aware execution plan](02-execution-plan.md)
4. [Generated implementation ledger](03-implementation-ledger.md)
5. [Verification and handoff](04-verification-and-handoff.md)

`revision.json` is the canonical structured record. This README and the implementation ledger are generated views; do not edit them manually.

## Finding dispositions

| Disposition | Count |
| --- | ---: |
{chr(10).join(summary_rows)}

## Owner attention and blockers

{chr(10).join(attention_lines)}

## Delivery state

| State | Value |
| --- | --- |
| Committed | `{delivery.get('committed')}` |
| Pushed | `{delivery.get('pushed')}` |
| Pull request updated | `{delivery.get('pull_request_updated')}` |
| Merged | `{delivery.get('merged')}` |

## Interpretation

Readiness is an assessment, not authorization. Consult the full verification and handoff artifact for limitations, blocked evidence, changed-path attribution, and exact delivery facts.
"""


def render_views(teardown: dict[str, Any], revision: dict[str, Any]) -> dict[str, str]:
    return {
        "README.md": render_readme(teardown, revision),
        "03-implementation-ledger.md": render_implementation_ledger(teardown, revision),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("teardown_directory", type=Path)
    parser.add_argument("revision_directory", type=Path)
    parser.add_argument("--check", action="store_true", help="fail if generated views are missing or stale")
    args = parser.parse_args()
    teardown = _load_object(args.teardown_directory / "findings.json")
    revision = _load_object(args.revision_directory / "revision.json")
    rendered = render_views(teardown, revision)
    stale: list[str] = []
    for name, content in rendered.items():
        path = args.revision_directory / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
    if stale:
        print("Generated revision views are missing or stale:", file=sys.stderr)
        for name in stale:
            print(f"- {name}", file=sys.stderr)
        return 1
    if args.check:
        print("Generated revision views are current.")
    else:
        print("Generated README.md and 03-implementation-ledger.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
