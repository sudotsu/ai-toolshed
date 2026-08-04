---
name: project-revision
description: Plan, implement, and converge an approved, validated project-teardown handoff against the current revision of a software project. Use when Claude must translate a teardown into an exhaustive owner decision or revision plan, resolve decisions, revalidate findings against changed code, implement approved work in dependency order, preserve existing work, review implementation-induced regressions and PR feedback, verify risk-sensitive behavior across relevant environments, and produce a current auditable implementation and readiness ledger.
---

# Project Revision

Turn a validated `project-teardown` handoff into verified project changes. Treat the teardown as evidence and a plan, not as permission to apply stale recommendations blindly. Implementation is not finished when the first test suite passes; it is finished only after an adversarial convergence pass and an honest final-state reconciliation.

## Operating contract

- Preserve all pre-existing user work. Never reset, clean, checkout over, stash, discard, or silently reformat it. Do not assume an uncommitted change belongs to this run.
- Implement only findings the owner approves. Approval covers in-repository implementation, not unrelated redesigns, destructive data operations, purchases, publication, production changes, credential changes, or external outreach.
- Verify every finding against the current project state before changing it. Do not force a fix whose premise, affected code, or recommendation is stale.
- Follow the teardown dependency graph. Do not implement a dependent while its prerequisite is unresolved unless the owner approves a corrected graph.
- Search usages before changing shared code. Prefer the smallest complete change that satisfies acceptance criteria and preserves documented strengths.
- Continue until every approved finding is implemented, already satisfied, retained, or explicitly blocked. A blocker makes the revision partial or blocked, never complete.
- Treat review bots and reviewer prompts as leads, not proof. Revalidate them against the current head and record their dispositions.
- Never call a revision merge-ready while a confirmed critical, high, or medium implementation or convergence defect remains unresolved.
- Distinguish implementation status, merge readiness, release readiness, and authorization. None implies another.
- Distinguish teardown facts, implementation recommendations, owner decisions, and newly discovered findings. A recommendation is never implicit approval.
- Preserve every provisional limitation, blocked investigation, unexercised workflow, and required external or real-environment check as an explicit blocker or completion gate. Do not let planning prose collapse them into vague future testing.
- Keep secrets and sensitive output out of artifacts, diffs, logs, and chat.

## 1. Establish inputs and baseline

Locate the project root and intended teardown folder. If multiple reports are plausible, ask the owner to select one. Read repository instructions before acting.

Read both bundled references:

- `references/revision-contract.md` for artifact structure and validation.
- `references/convergence-and-verification.md` for the adversarial review loop, risk-triggered testing, readiness rules, and commit sequencing.

Locate the installed `project-teardown` skill by `name` frontmatter and run its bundled `scripts/validate_teardown.py` against the handoff. Do not substitute another validator. Stop and report exact errors if validation fails.

Read the complete handoff, including `findings.json`, every numbered report, `07-review-coverage.md`, and all evidence relevant to decisions, acceptance criteria, reproduction, named product surfaces, or known limitations. Confirm Markdown, JSON, and evidence describe the same report, not merely that the validator passed. Supporting evidence can contain required subconditions that the one-line finding summary omits.

Capture before product edits:

- current immutable revision, branch, or equivalent workspace identity;
- staged, unstaged, and untracked paths;
- the diff or content snapshot needed to distinguish existing work;
- relevant toolchain versions and baseline check results;
- existing pull request, review, CI, issue, or delivery state when in scope and accessible.

Keep raw diagnostics in a restricted temporary location, not the repository artifact. Before editing a path with existing user changes, preserve its exact bytes and file mode for reconciliation. If approved work cannot safely combine with existing changes, stop and ask.

If the audited revision differs from the current revision, either state includes working-tree changes, or an existing implementation branch has advanced, mark the handoff drifted and fully revalidate it.

If the teardown is provisional, surface unresolved coverage before approval. Do not imply known fixes cover unreviewed surfaces; block any finding whose acceptance cannot be established because of the same limitation.

Create `project-revision/`, or a clearly dated sibling when one already exists. Never overwrite an existing revision record without permission. New and migrated artifacts must follow schema version 2 in the revision contract.

## 2. Revalidate findings and resolve decisions

Process findings in coverage-ledger order. For each finding:

1. Inspect the current workflow and all relevant usages.
2. Re-run the reproduction or closest safe equivalent.
3. Reassess root cause, impact, recommendation, dependencies, conflicts, acceptance criteria, and verification.
4. Classify it as `confirmed`, `changed`, `stale`, `already-resolved`, `not-applicable`, or `blocked`.
5. Cite current evidence and explain divergence from the teardown.

Do not edit stale or not-applicable findings. Treat already-resolved work as satisfied only after its acceptance criteria pass. If a changed finding requires materially different behavior, scope, or risk, return it to owner decision. Apply a small implementation adjustment without another question only when it preserves the approved outcome and risk profile; record it.

Build one owner decision packet before product edits. Include decision-required findings, conflicts, accepted risks, missing prerequisites, materially changed findings, and work requiring authority beyond repository edits. For each, provide concrete options, recommendation, consequences, dependencies, and default of no change.

Record an approval matrix covering every finding: `approved`, `deferred`, `rejected`, `accepted-risk`, or `not-applicable`. Strengths and retain actions still need explicit preservation approval. Do not start product edits while a pending decision can change the executable graph.

### Planning-only and decision-packet requests

When the owner requests analysis, revalidation, or a revision plan without authorizing product edits, stop after producing the requested planning artifact. Do not create an implementation ledger, claim convergence, or imply that planning exercised the skill's implementation behavior.

Before delivering the plan, build a handoff-to-plan traceability check. Account for:

- every finding ID, exact disposition, dependency, acceptance criterion, and preservation action;
- every decision, prerequisite, blocked investigation, unverified claim, provisional limitation, and unexercised core workflow from the executive verdict, coverage ledger, sequence, and evidence;
- every affected runtime, configuration, manifest, metadata, operational-documentation, delivery, and user-facing surface named by the evidence;
- every required live-provider, external-system, real-device, browser, platform, accessibility, security, failure-path, or production check.

Put each item in the plan as an implementation action, owner decision, explicit blocker, or observable completion gate. Use specific workflows and environments; phrases such as "test mobile," "check accessibility," or "update documentation" are insufficient when the handoff identifies concrete surfaces.

Include a delta statement that separates:

1. teardown-derived facts and recommendations translated into the plan;
2. new implementation or sequencing recommendations from the revision pass;
3. genuinely new findings discovered during current-state revalidation.

Label agent recommendations as recommendations until the owner approves them. Preserve the teardown's provisional/final status and exact finding counts and dispositions. If no new findings exist, say so directly. A cleaner reorganization of existing evidence is not a new finding.

## 3. Plan and implement in dependency order

Order approved work by prerequisites, then risk reduction, then severity. Group only independent findings. Before each batch:

- confirm prerequisites have completed dispositions;
- identify overlap with baseline work;
- choose an edit strategy that preserves both intents;
- define focused checks, regression risks, fault cases, and a rollback approach that does not discard user work.

Implement complete vertical changes, including tests, documentation, configuration, migrations, error handling, and cleanup required by acceptance criteria. Do not broaden scope into opportunistic refactors.

When work touches destructive recovery, startup maintenance, trust boundaries, user-controlled parsing, processes, platform-specific behavior, provider protocols, or resource limits, apply the relevant fault-injection and behavioral checks from `references/convergence-and-verification.md`. A build on another platform is not behavioral platform evidence.

After each finding or coupled batch:

1. Run focused verification, including failure paths.
2. Inspect the diff and inventory against baseline.
3. Confirm existing work remains semantically intact.
4. Record changed files, acceptance results, evidence, and disposition.
5. Do not mark work implemented while any required criterion fails.

If implementation disproves the plan, stop that dependency branch, diagnose, update the ledger, and request a decision only when the changed outcome is consequential.

## 4. Converge the implementation

After approved implementation, run the convergence workflow from `references/convergence-and-verification.md`.

At minimum:

1. Perform a fresh adversarial review of the complete product diff, emphasizing cross-finding interactions and newly shared code.
2. Re-run affected end-to-end workflows as a user, not only unit tests.
3. If a pull request exists and access is available, inspect current-head inline threads, top-level comments, reviews, outside-diff findings, skipped-file notices, and rate-limit or partial-review warnings.
4. Revalidate every actionable lead. Record it in `convergence_findings` as fixed, already satisfied, invalid, open, deferred, or blocked.
5. If a lead proves an original finding's acceptance criteria failed, reopen that original finding as well; do not hide it only in the convergence ledger.
6. Fix confirmed in-scope defects in severity and dependency order, add regression tests, then review the resulting diff again.
7. Repeat until no confirmed critical, high, or medium convergence defect remains unresolved.

Do not equate resolved review threads with fixed code, green CI with reviewed behavior, or bot silence with a clean review. If external review is unavailable or rate-limited, record that limitation and complete a manual full-diff review; never claim the unavailable source passed.

Low-severity findings may remain only with a recorded reason and consequence. Owner approval is required when deferral changes promised behavior or accepted risk.

## 5. Verify and finalize

Run existing project checks plus the end-to-end and risk-specific workflows needed to cover cross-finding interactions. Re-run security, performance, accessibility, packaging, and platform checks whenever touched. Verify preserved strengths and accepted-risk boundaries.

Reconcile the final product tree against baseline:

- every new product change maps to an approved finding or confirmed convergence defect;
- all pre-existing staged, unstaged, and untracked work remains accounted for;
- unrelated paths remain unchanged;
- generated files and dependency changes are intentional;
- affected operational documentation, manifests, public metadata, configuration claims, and version facts agree with the implemented product;
- no secret or sensitive diagnostic entered the diff.

When version control cannot distinguish baseline work, compare captured snapshots and state uncertainty. Never claim preservation without evidence.

Finalize using the sequencing rules in `references/convergence-and-verification.md`. In particular, a committed artifact cannot contain its own commit hash. Record the last immutable product-code revision as `implementation_end_revision`, then place only artifact maintenance after it. If commit or push authority is absent, use an explicit working-tree state instead of inventing a revision.

Complete schema-version-2 `revision.json`, then run:

```bash
python3 <skill-directory>/scripts/validate_revision.py <project-teardown-directory> <project-revision-directory>
```

Fix every structural error and record the command and result. Validator success is necessary, not sufficient: manually reconcile decisions, evidence, diffs, acceptance criteria, convergence findings, review state, readiness, delivery facts, and the original findings register.

Use these status boundaries:

- `complete`: every approved finding is implemented, already satisfied, or retained; required evidence passes; existing work is reconciled.
- `partial`: useful approved work completed, but an approved finding or required verification remains blocked or failed.
- `blocked`: no approved implementation could safely complete.

Merge-ready may be true for an honestly partial revision only when remaining limitations are non-blocking for integration, fail safely, are documented, and no blocking convergence defect remains. Release-ready normally requires a complete revision and all release-critical environment evidence. Readiness never authorizes merging or releasing.

## Handoff

End with:

1. Revision status and immutable product-code endpoint or explicit working-tree state.
2. Artifact relationship to that endpoint.
3. Implemented, satisfied, retained, deferred, rejected, accepted-risk, stale, and blocked findings.
4. Convergence findings and the sources reviewed.
5. Checks, results, fault coverage, and unverified claims.
6. Merge readiness, release readiness, and consequences of remaining limitations.
7. Exact delivery facts: commit, push, pull-request update, merge, deployment, and release state.
8. Preservation evidence and remaining uncertainty.
9. Path to the revision artifact.

Do not claim a commit, push, PR update, merge, deployment, migration, publication, or production change unless explicitly authorized and verified. Do not describe a PR as current without refreshing its head, reviews, and CI state.
