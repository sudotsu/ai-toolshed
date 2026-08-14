# Revision Artifact Contract

Use this contract only for implementation or continuation mode. Planning-only work follows [planning-contract.md](planning-contract.md).

## Contents

1. Required folder and generated entry point
2. Decisions and scope
3. Baseline and revalidation
4. Execution plan
5. Generated implementation and convergence ledger
6. Verification and handoff
7. `revision.json` schema version 2
8. Teardown finding rules
9. Convergence finding rules
10. Final-state rules
11. Final integrity pass

## 1. Required folder and generated entry point

```text
project-revision/
├── README.md
├── 00-decisions-and-scope.md
├── 01-baseline-and-revalidation.md
├── 02-execution-plan.md
├── 03-implementation-ledger.md
├── 04-verification-and-handoff.md
└── revision.json
```

All listed files are mandatory. `revision.json` is the canonical structured finding and convergence record. Generate `README.md` and `03-implementation-ledger.md` with:

```bash
python3 <skill-directory>/scripts/render_revision_views.py <project-teardown-directory> <project-revision-directory>
```

Do not manually maintain those generated views. The README is the concise human entry point and must link to the full artifacts; it does not replace them. Add safe evidence files only when they materially improve independent verification. Do not copy secrets, private data, or raw production dumps.

## 2. `00-decisions-and-scope.md`

Include these exact sections:

- `## Owner decisions and approval matrix`
- `## Constraints and preserved strengths`
- `## Blocked evidence and authority boundaries`

Record:

- project and teardown identity;
- operating mode and implementation authority;
- owner priorities and constraints;
- exact approval matrix covering every finding;
- unresolved decisions and defaults;
- accepted risks;
- exclusions and authority boundaries;
- strengths and behaviors that must be preserved; retained strengths default to preservation without a separate owner answer unless planned work threatens a tradeoff;
- provisional limitations and blocked evidence carried from the teardown.

Distinguish owner decisions from agent recommendations. Cover every teardown finding exactly once. A narrowly approved subset is allowed, but every untouched finding must retain an explicit deferred, rejected, accepted-risk, retained, not-applicable, or blocked disposition.

## 3. `01-baseline-and-revalidation.md`

Include these exact sections:

- `## Baseline state`
- `## Preservation inventory`
- `## Current-state revalidation`

Record:

- implementation-start revision, branch, remote, and workspace identity;
- sanitized staged, unstaged, and untracked inventories;
- pre-existing changed-path hashes or equivalent preservation evidence;
- baseline checks and toolchain versions;
- current PR, review, CI, issue, and delivery state when in scope;
- drift from the audited teardown revision.

For every teardown finding, record current classification, reproduction/inspection, current evidence, changed premise, original-record digest, and whether the recommendation, dependencies, acceptance criteria, and verification remain valid.

## 4. `02-execution-plan.md`

Include these exact sections:

- `## Dependency-aware execution plan`
- `## Verification plan`
- `## Convergence plan`
- `## Stop conditions`

Give the dependency-aware order, batches, prerequisites, conflicts, overlap with existing work, focused verification, fault cases, environment requirements, regression risks, safe rollback, and stop conditions.

Identify every deviation from the teardown implementation sequence and explain it. Every dependency must resolve before its dependent.

Include a convergence plan covering:

- full baseline-to-current diff review;
- defining and end-to-end workflows;
- current-head review sources;
- risk-triggered platform, fault-injection, package, security, accessibility, and external-system checks;
- criteria for repeating review after product-code fixes;
- readiness gates and delivery sequencing.

## 5. Generated `03-implementation-ledger.md`

This file is generated from `revision.json` and the teardown. Do not edit it manually.

### Teardown findings

The renderer gives every teardown finding exactly one section using the original ID and title:

```markdown
## TECH-001 — Repair behavior

- **Approval:** approved
- **Teardown verification state:** defect-conclusively-demonstrated
- **Revalidation:** confirmed
- **Disposition:** implemented
- **Sequence:** 1
- **Reason:** Current evidence and owner approval.
- **Files changed:** src/example.ts | src/example.test.ts
- **Acceptance results:** criterion one => passed => focused test passed | criterion two => passed => failure-path test passed
- **Verification:** unit test passed | defining workflow passed
- **Notes:** None
- **Revision record digest:** sha256:<digest of the revision finding record>
```

Requirements:

- Use exact JSON values for approval, revalidation, disposition, sequence, and reason.
- Render arrays with ` | ` separators; use `None` for empty arrays.
- Render each acceptance result as `<criterion> => <status> => <evidence>` and separate results with ` | `.
- Preserve original titles.
- Record deferred, rejected, stale, already-resolved, not-applicable, informational, accepted-risk, retained, and blocked findings; do not hide them.
- The digest is SHA-256 of the canonical revision finding object (`sort_keys=True`, compact separators, UTF-8).

### Convergence findings

After all teardown findings, add the exact heading:

```markdown
# Convergence findings
```

Give every actionable implementation-review lead one section:

```markdown
### REV-001 — Follow-up regression

- **Source:** manual full-diff review
- **Severity:** medium
- **Status:** fixed
- **Reason:** The implementation introduced an edge-case failure.
- **Files changed:** src/example.ts | src/example.test.ts
- **Verification:** failure-path regression passed
- **Convergence record digest:** sha256:<digest of the convergence record>
```

Include inline, top-level, outside-diff, manual-review, static-analysis, fault-injection, platform, package, CI, and external-review leads when applicable. A stale or invalid lead still needs a disposition if it was actionable.

If a convergence lead proves an original finding's acceptance criteria failed, update the original finding's ledger entry and `revision.json` too.

## 6. `04-verification-and-handoff.md`

Start with these exact labels, matching `revision.json`:

```text
**Revision status:** complete
**Implementation endpoint:** immutable product-code revision or explicit working-tree state
**Artifact relationship:** artifact-only-descendant
**Review convergence:** passed
**Manual adversarial review:** completed
**Current-head review after final product change:** completed
**Existing work reconciled:** yes
**Blocking convergence findings:** 0
**Merge readiness:** ready
**Release readiness:** ready
**Committed:** verified
**Pushed:** verified
**Pull request updated:** verified
**Merged:** not-performed
**Revision validator status:** passed
```

Allowed values:

- manual/current-head review: `completed` or `blocked`;
- existing work reconciled: `yes` or `no`;
- other values are defined by `revision.json` below.

Use `artifact-only-descendant` only when `implementation_end_revision` is the final product-code commit and every later change is artifact-only. A committed artifact cannot identify its own containing commit hash from inside itself. Use `working-tree` when changes remain uncommitted or no immutable product endpoint exists.

Include these exact sections:

- `## Verification results`
- `## Review-source coverage`
- `## Baseline reconciliation`
- `## Changed-path attribution`
- `## Limitations and blocked evidence`
- `## Delivery state`
- `## Validator result`

Under `## Changed-path attribution`, use this exact table shape:

```markdown
| Path | Classification | Finding IDs | Baseline relationship | Rationale |
| --- | --- | --- | --- | --- |
| src/example.ts | approved-finding | TECH-001 REV-002 | New project-revision change | Implements TECH-001 and fixes REV-002 |
```

Allowed classifications are `approved-finding`, `convergence-fix`, `preserved-existing-work`, `revision-artifact`, and `generated-ignored`. Every path in a finding or convergence `files_changed` array must appear and include the responsible ID.

Also include:

- focused, full-suite, end-to-end, platform, accessibility, security, package, and fault-injection checks with commands/methods and results;
- review sources inspected, exact current head, partial/rate-limited sources, and dispositions;
- failures, limitations, blocked environments, and unverified claims;
- sanitized final working-tree inventory;
- baseline-to-final preservation reconciliation;
- mapping from every changed product path to approved finding IDs, fixed convergence IDs, or preserved pre-existing work;
- mapping from artifact paths to artifact maintenance;
- revision validator command and result;
- consequences of merging or releasing with remaining limitations;
- exact commit, push, PR, merge, deployment, migration, publication, release, and production state.

## 7. `revision.json` — schema version 2

Use this exact top-level shape:

```json
{
  "schema_version": 2,
  "project": "owner/project or project name",
  "teardown_path": "project-teardown",
  "teardown_audited_revision": "immutable revision or explicit working-tree state",
  "implementation_start_revision": "immutable revision or explicit working-tree state",
  "implementation_end_revision": "last product-code revision or explicit working-tree state",
  "revision_status": "complete",
  "generated_at": "ISO-8601 timestamp",
  "existing_work_reconciled": true,
  "findings": [],
  "convergence_findings": [],
  "final_state": {
    "artifact_relationship": "artifact-only-descendant",
    "review_convergence": "passed",
    "blocking_convergence_findings": 0,
    "merge_readiness": "ready",
    "release_readiness": "ready",
    "delivery": {
      "committed": "verified",
      "pushed": "verified",
      "pull_request_updated": "verified",
      "merged": "not-performed"
    }
  }
}
```

`implementation_end_revision` identifies product code, not a self-referential artifact commit. If using an artifact-only descendant, make no product-code change after that endpoint and record the externally observable final repository head in the handoff or PR description.

The bundled `references/schemas/revision.schema.json` is an editor/interoperability schema. The Python validator is normative because it also enforces teardown correspondence, dependency order, acceptance-criterion coverage, Markdown digests, readiness, and handoff markers.

## 8. Teardown finding rules

Give every teardown finding exactly these keys:

```text
id, approval, revalidation, disposition, sequence, reason,
files_changed, acceptance_results, verification, notes
```

Controlled values:

- `approval`: `approved`, `deferred`, `rejected`, `accepted-risk`, `not-applicable`
- `revalidation`: `confirmed`, `changed`, `stale`, `already-resolved`, `not-applicable`, `blocked`
- `disposition`: `implemented`, `already-satisfied`, `retained`, `deferred`, `rejected`, `accepted-risk`, `not-applicable`, `blocked`
- acceptance-result `status`: `passed`, `failed`, `not-applicable`, `blocked`

Use a unique positive `sequence` contiguous across all teardown findings and preserve dependency order.

Store `files_changed`, `verification`, and `notes` as unique arrays of non-empty strings. Paths must be safe relative project paths, not absolute and not containing `..`.

Store acceptance results as objects with exactly:

```json
{
  "criterion": "observable criterion from the teardown",
  "status": "passed",
  "evidence": "current verification evidence"
}
```

For every approved finding, the acceptance-result criteria must match the original teardown acceptance criteria exactly once. Do not summarize, omit, split, or replace them. Use a blocked result when a criterion cannot be established.

When revalidation reveals that a criterion is vague, preserve its exact text and add a non-material clarification through current verification evidence or `notes`. A clarification may make the same approved outcome measurable; it may not change behavior, scope, authority, risk, or owner commitment. Any such material change returns to owner decision.

Disposition rules:

| Approval | Allowed disposition |
| --- | --- |
| approved | implemented, already-satisfied, retained, blocked |
| deferred | deferred |
| rejected | rejected |
| accepted-risk | accepted-risk |
| not-applicable | not-applicable |

Additional rules:

- `implemented` requires changed files, non-empty verification, and all acceptance results passed or genuinely not applicable.
- `already-satisfied` requires revalidation `already-resolved`, no changed files, non-empty verification, and passing criteria.
- `retained` is valid only for a teardown strength or retain action, defaults to approved preservation after revalidation, has no changed files, and requires preservation verification. A threatened tradeoff requires explicit owner approval.
- `blocked` requires revalidation `blocked`, no changed files, and at least one blocked acceptance result with specific evidence.
- Deferred, rejected, accepted-risk, and not-applicable findings must not list changed files.
- Approval `not-applicable` requires revalidation `not-applicable`.
- Revalidation `stale` or `not-applicable` requires **both** approval `not-applicable` **and**
  disposition `not-applicable`. A finding the teardown can no longer substantiate is not
  deferred or rejected — it is out of scope, and all three fields must say so.
- Revalidation `already-resolved` requires disposition `already-satisfied`, and disposition
  `already-satisfied` requires revalidation `already-resolved`. This pairing is bidirectional:
  neither value is valid without the other.
- A complete revision requires every approved finding implemented, already satisfied, or retained; every approved criterion passed or genuinely not applicable; and existing work reconciled.

## 9. Convergence finding rules

Give every convergence finding exactly these keys:

```text
id, title, source, severity, status, reason, files_changed, verification
```

Controlled values:

- `id`: unique `REV-<NNN>`
- `severity`: `critical`, `high`, `medium`, `low`
- `status`: `fixed`, `already-satisfied`, `invalid`, `open`, `deferred`, `blocked`

Rules:

- `fixed` requires changed files and non-empty verification.
- `already-satisfied` and `invalid` require non-empty current-head verification and no changed files.
- `invalid` is used only when current-head evidence disproves the lead.
- Critical/high/medium open, deferred, or blocked findings are blocking and prevent convergence and readiness.
- A remaining low finding needs an explicit consequence and blocks release readiness when it violates a required acceptance criterion.
- Markdown and JSON IDs, titles, values, and digests must match exactly.

## 10. Final-state rules

Controlled values:

- `artifact_relationship`: `working-tree` or `artifact-only-descendant`
- `review_convergence`: `passed` or `blocked`
- readiness: `ready`, `not-ready`, or `not-applicable`
- delivery values: `verified`, `not-performed`, `unverified`, or `not-applicable`

`blocking_convergence_findings` equals the computed number of critical/high/medium convergence findings with status open, deferred, or blocked.

Review convergence may be `passed` only when:

- the blocking count is zero;
- the manual adversarial review marker is `completed`;
- current-head review after the final product change is `completed`.

Merge readiness may be `ready` only when:

- revision status is not `blocked`;
- review convergence passed;
- blocking count is zero;
- existing work is reconciled;
- no approved acceptance criterion failed;
- any remaining blocked approved criterion depends on genuinely external evidence, the implemented behavior fails safely, and the limitation is explicit;
- required merge-gate checks are satisfied;
- delivery facts do not contradict the claimed artifact relationship.

A partial revision may therefore be merge-ready in the narrow external-evidence case above, but it cannot be release-ready.

Release readiness may be `ready` only when merge readiness is ready, revision status is complete, and all required release/environment gates are satisfied.

Readiness is an assessment, not authorization. Delivery fields record verified facts, not intentions.

Delivery consistency:

- verified push requires verified commit;
- verified PR update requires verified push and a current PR read;
- verified merge requires verified commit and push, plus current merged state;
- artifact-only descendant requires a verified committed product endpoint;
- no delivery field may be inferred from another.

## 11. Final integrity pass

1. Confirm the original teardown still validates and remains unchanged.
2. Confirm decisions, revalidation, Markdown ledger, and JSON cover identical teardown IDs.
3. Confirm every approved finding preserves all original acceptance criteria.
4. Confirm all actionable review leads have convergence dispositions.
5. Confirm every required owner decision has an exact answer or remains an explicit blocker.
6. Confirm every finding was revalidated against the implementation-start state.
7. Confirm prerequisites resolve earlier than dependents.
8. Confirm product changes map to approved findings, fixed convergence findings, or preserved pre-existing work.
9. Confirm approved acceptance criteria have current evidence.
10. Confirm risk-triggered, full-suite, end-to-end, accessibility, security, package, platform, and external-system checks are reported accurately.
11. Confirm baseline work remains and unrelated paths are unchanged.
12. Confirm implementation endpoint and artifact relationship are possible and current.
13. Refresh PR head, review, CI, remote, merge, release, and delivery claims after the last relevant change.
14. Confirm readiness and delivery markers match JSON and evidence.
15. Confirm every provisional limitation, blocked investigation, unexercised workflow, and required real-environment check remains visible.
16. Confirm operational docs, manifests, metadata, configuration claims, route inventories, analytics claims, and version facts agree with the final product.
17. Regenerate `README.md` and `03-implementation-ledger.md` from `revision.json`; do not hand-edit digests.
18. Run the bundled revision validator and record success. Skill-bundle validation is maintenance-only and is not a project completion gate.
