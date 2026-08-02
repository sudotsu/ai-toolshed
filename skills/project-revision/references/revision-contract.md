# Revision Artifact Contract

Create a durable execution and convergence record beside the teardown without modifying the teardown itself.

```text
project-revision/
├── 00-decisions-and-scope.md
├── 01-baseline-and-revalidation.md
├── 02-execution-plan.md
├── 03-implementation-ledger.md
├── 04-verification-and-handoff.md
├── revision.json
└── evidence/
```

If `project-revision/` exists, ask before replacing it or create a dated sibling. Migrate an approved existing artifact to schema version 2 when continuing its implementation. Keep evidence sanitized and compact.

## 00 — Decisions and scope

Record the teardown path and audited revision, owner approval matrix, exact answers to required decisions, accepted risks, substitutions, exclusions, and authority boundaries. Cover every teardown finding exactly once. Distinguish owner decisions from agent recommendations.

## 01 — Baseline and revalidation

Record implementation-start revision, branch or workspace identity, dirty state, sanitized staged/unstaged/untracked inventories, baseline checks, toolchain versions, delivery state, and drift from the audited revision.

For every teardown finding, record current classification, reproduction or inspection, current evidence, changes from the premise, and whether the original recommendation and dependencies remain valid.

## 02 — Execution plan

Give the dependency-aware order, batches, prerequisites, conflicts, overlap with existing work, focused verification, fault cases, regression risks, and stop conditions. Identify deviations from `06-implementation-sequence.md`. Every dependency must resolve before its dependent.

Include a convergence plan: full-diff review method, relevant end-to-end workflows, available external review sources, risk-triggered checks, and criteria for repeating review after fixes.

## 03 — Implementation and convergence ledger

Give every teardown finding exactly one `## <ID> — <Title>` section using its original ID and title. Record approval, revalidation, disposition, sequence, edits or preserved behavior, files changed, acceptance results, verification, blockers, and notes. Do not hide deferred, rejected, stale, informational, or accepted-risk findings.

After the teardown findings, add `# Convergence findings`. Give every actionable implementation-review lead a `### REV-<NNN> — <Title>` section. Record source, severity, current-head revalidation, status, relationship to any original finding, changed files, verification, and reason. Include inline, top-level, outside-diff, manual-review, static-analysis, fault-injection, and CI leads when applicable. A stale or invalid lead still needs a disposition if it was actionable.

If a convergence lead proves an original finding's acceptance criteria failed, update the original finding's ledger entry too.

## 04 — Verification and handoff

Start with these exact markers, matching `revision.json`:

```text
**Revision status:** complete
**Implementation endpoint:** immutable product-code revision or explicit working-tree state
**Artifact relationship:** artifact-only-descendant
**Review convergence:** passed
**Blocking convergence findings:** 0
**Merge readiness:** ready
**Release readiness:** ready
**Committed:** verified
**Pushed:** verified
**Pull request updated:** verified
**Merged:** not-performed
```

Allowed artifact relationships are `working-tree` and `artifact-only-descendant`. Use `artifact-only-descendant` only when `implementation_end_revision` is the last product-code commit and every later change is artifact-only. A committed artifact cannot identify its own commit hash from inside itself. Use `working-tree` when changes remain uncommitted or no immutable revision exists.

Also include:

- focused, full-suite, end-to-end, platform, and fault-injection checks with commands or methods and results;
- review sources inspected, current-head coverage, partial/rate-limited sources, and dispositions;
- failures, limitations, blocked environments, and unverified claims;
- sanitized final working-tree inventory;
- baseline-to-final reconciliation and preservation evidence;
- mapping from changed product paths to approved findings or convergence IDs;
- mapping from artifact paths to artifact maintenance;
- revision validator command and result;
- consequences of merging or releasing with remaining limitations;
- exact deployment, migration, publication, and production state.

## revision.json — schema version 2

Use this top-level shape:

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

`implementation_end_revision` identifies product code, not a self-referential artifact commit. If an artifact-only descendant is used, make no product-code change after that endpoint. Record the externally observable final head in the handoff or PR description after the artifact commit when authorized and verifiable.

### Teardown findings

Give every teardown finding these keys:

```text
id, approval, revalidation, disposition, sequence, reason,
files_changed, acceptance_results, verification, notes
```

Controlled values:

- `approval`: `approved`, `deferred`, `rejected`, `accepted-risk`, or `not-applicable`
- `revalidation`: `confirmed`, `changed`, `stale`, `already-resolved`, `not-applicable`, or `blocked`
- `disposition`: `implemented`, `already-satisfied`, `retained`, `deferred`, `rejected`, `accepted-risk`, `not-applicable`, or `blocked`
- acceptance-result `status`: `passed`, `failed`, `not-applicable`, or `blocked`

Use a unique positive `sequence` contiguous across teardown findings. Preserve dependency order. Store `files_changed`, `verification`, and `notes` as arrays of strings. Use an empty `files_changed` array for findings resolved without edits. `reason` must be non-empty.

Store acceptance results as objects with exactly:

```json
{
  "criterion": "observable criterion from the teardown",
  "status": "passed",
  "evidence": "current verification evidence"
}
```

Disposition rules:

| Approval | Allowed disposition |
| --- | --- |
| approved | implemented, already-satisfied, retained, blocked |
| deferred | deferred |
| rejected | rejected |
| accepted-risk | accepted-risk |
| not-applicable | not-applicable |

An implemented finding must list a changed file. An already-satisfied finding requires revalidation `already-resolved`. A retained finding is for an approved strength or retain action and has no changed file. A blocked approved finding forces revision status `partial` or `blocked`.

Every approved finding needs at least one acceptance result. `complete` requires every approved finding to be implemented, already satisfied, or retained; all approved acceptance results passed or genuinely not applicable; and existing work reconciled.

### Convergence findings

Give every convergence finding these keys:

```text
id, title, source, severity, status, reason, files_changed, verification
```

Controlled values:

- `id`: unique `REV-<NNN>` identifier
- `severity`: `critical`, `high`, `medium`, or `low`
- `status`: `fixed`, `already-satisfied`, `invalid`, `open`, `deferred`, or `blocked`

Use `invalid` only after current-head revalidation disproves the lead. Use `already-satisfied` when current code and verification already meet it. A fixed finding must list changed files and verification. An open, deferred, or blocked critical/high/medium finding is blocking and prevents merge readiness. A remaining low finding needs an explicit consequence.

The JSON convergence IDs and Markdown `### REV-<NNN>` headings must match exactly once.

### Final state

Controlled values:

- `artifact_relationship`: `working-tree` or `artifact-only-descendant`
- `review_convergence`: `passed` or `blocked`
- readiness: `ready`, `not-ready`, or `not-applicable`
- delivery values: `verified`, `not-performed`, `unverified`, or `not-applicable`

`blocking_convergence_findings` must equal the computed number of critical/high/medium convergence findings with status open, deferred, or blocked.

Review convergence may be `passed` only when that count is zero and a manual adversarial pass ran. Merge readiness may be `ready` only when review convergence passed, the count is zero, and revision status is not blocked. Release readiness may be `ready` only when merge readiness is ready and revision status is complete.

Readiness is an assessment, not authorization. Delivery fields record verified facts, not intended next actions.

## Final integrity pass

1. Confirm the original teardown still validates and remains unchanged.
2. Confirm decisions, Markdown ledger, and JSON cover identical teardown IDs.
3. Confirm all actionable review leads have convergence dispositions.
4. Confirm every required owner decision has an exact answer.
5. Confirm every finding was revalidated against the implementation-start state.
6. Confirm prerequisites resolve earlier than dependents.
7. Confirm product changes map to approved findings or fixed convergence findings.
8. Confirm approved acceptance criteria have current evidence.
9. Confirm risk-triggered, full-suite, end-to-end, and platform checks are reported accurately.
10. Confirm baseline work remains and unrelated paths are unchanged.
11. Confirm implementation endpoint and artifact relationship are possible and current.
12. Refresh any PR head, review, CI, and delivery claims after the last product change.
13. Confirm readiness and delivery markers match JSON and evidence.
14. Run the bundled revision validator and record success.
15. Confirm every provisional coverage limitation, blocked investigation, unexercised workflow, and required external or real-environment check remains visible as a blocker, limitation, or completion gate.
16. Confirm affected operational documentation, manifests, metadata, configuration claims, route inventories, analytics claims, and version facts agree with the final product.
