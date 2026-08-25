---
name: project-revision
description: Revalidate, plan, implement, and converge an approved project-teardown handoff against the current state of a software project while preserving existing user work and producing an auditable decision, implementation, verification, and readiness record. Use when the user asks the agent to create an exhaustive planning-only revision document, resolve owner decisions, implement approved teardown findings in dependency order, continue an existing revision branch or PR, address reviewer feedback, verify risk-sensitive behavior across relevant environments, or prove that every teardown finding and newly discovered regression has a current disposition. Do not use without a project-teardown handoff or as permission to apply stale recommendations blindly.
---

# Project Revision

Turn a validated `project-teardown` handoff into either:

1. a fully traceable planning-only artifact; or
2. verified project changes that converge after adversarial review.

Treat the teardown as evidence and a proposed plan, not as permission to apply stale recommendations. Implementation is not finished when the first test suite passes. It is finished only when approved work satisfies current acceptance criteria, pre-existing work is reconciled, the entire final diff survives convergence review, and readiness claims match verifiable facts.

## Operating contract

- Preserve all pre-existing user work. Never reset, clean, checkout over, stash, discard, overwrite, or silently reformat it.
- Implement only findings the owner approves. A recommendation is not approval.
- Revalidate every finding against the current project state before changing it.
- Follow the teardown dependency graph unless current evidence proves it wrong and the owner approves the corrected graph.
- Search usages before changing shared code. Prefer the smallest complete vertical change, not the fewest lines.
- Include tests, documentation, configuration, migrations, error handling, cleanup, and cross-platform behavior required by acceptance criteria. Do not use "minimal" as an excuse for incomplete work.
- Continue until every approved finding is implemented, already satisfied, retained, or explicitly blocked. A blocker makes the run partial or blocked, never complete.
- Treat review bots, inline comments, PR prompts, static-analysis warnings, and prior agent suggestions as leads. Revalidate every actionable lead against the current head.
- Distinguish implementation status, convergence, merge readiness, release readiness, delivery state, and owner authorization. None implies another.
- Preserve every provisional limitation, blocked investigation, unexercised workflow, and required real-environment check as an explicit blocker or completion gate.
- Keep secrets, private data, and sensitive runtime output out of artifacts, diffs, logs, and chat.
- Treat a constraint as real only when the owner stated it or an objective external fact establishes it. Never infer a quality-limiting constraint from task difficulty, elapsed effort, or inconvenience. A constraint may reduce approved scope; it does not lower execution quality for work that remains in scope.
- Support every readiness, parity, or completion judgment with a concrete artifact: a measured output, a test or command result, an inspected competitor capability, or a produced file. Reasoning about why the work seems strong is not evidence.

## 1. Select the operating mode

Determine whether the request is:

- `planning-only`: analysis, revalidation, decision packet, or revision plan without product-edit authorization;
- `implementation`: owner-approved product changes;
- `continuation`: continue an existing revision branch, worktree, PR, or review cycle.

Do not infer implementation authority from a request for a plan. When the user explicitly limits edits to one document, modify only that document.

Read the relevant contracts before acting:

- [planning-contract.md](references/planning-contract.md) for planning-only work;
- [revision-contract.md](references/revision-contract.md) for implementation artifacts;
- [preservation-and-delivery.md](references/preservation-and-delivery.md) before product edits or delivery claims;
- [convergence-and-verification.md](references/convergence-and-verification.md) before defining verification and convergence.

## 2. Establish inputs and baseline

Locate the project root and intended teardown folder. If multiple handoffs are plausible and evidence cannot select one safely, ask the owner to choose.

Locate the installed `project-teardown` skill by `name` frontmatter and run its bundled validator against the handoff. Do not substitute another validator. Stop and report exact errors if validation fails.

Read the entire handoff:

- `README.md` when present, as the entry index rather than a substitute for the full handoff;
- `findings.json`, including schema-version-3 confidence and verification-state distinctions;
- every numbered report;
- the complete implementation sequence and coverage ledger;
- `07-review-coverage.md`;
- `08-claims-inventory.md` when present, preserving every unresolved claim and related finding;
- all evidence relevant to decisions, acceptance criteria, reproduction, named surfaces, claims, or limitations.

Do not rely on one-line finding summaries. Supporting evidence and coverage files may contain required subconditions, platform checks, owner decisions, or blocked environments.

Capture the baseline using [preservation-and-delivery.md](references/preservation-and-delivery.md): immutable revision, branch, remote, staged/unstaged/untracked paths, relevant file bytes/modes, toolchain versions, baseline checks, and current PR/review/CI/delivery state.

If the audited revision differs from the current revision, either state contains working-tree changes, or the implementation branch advanced, mark the teardown drifted and revalidate every finding.

If the teardown is provisional, surface the unresolved coverage before approval. Do not imply known fixes cover unreviewed surfaces. Block acceptance that depends on the same missing evidence.

## 3. Revalidate every teardown finding

Process findings in coverage-ledger order. For each:

1. inspect the current workflow and all relevant usages;
2. rerun the reproduction or closest safe equivalent;
3. reassess root cause, impact, recommendation, dependencies, conflicts, acceptance criteria, verification, and preservation requirements;
4. classify as `confirmed`, `changed`, `stale`, `already-resolved`, `not-applicable`, or `blocked`;
5. cite current evidence and explain divergence from the teardown.

Do not edit stale or not-applicable findings. Treat already-resolved work as satisfied only after all original acceptance criteria pass. Preserve each original acceptance criterion verbatim. A non-material clarification may add a measurable verification method or evidence detail in `verification`, `notes`, or planning prose when it preserves the approved outcome, scope, authority, and risk profile. A material change to behavior, scope, authority, risk, or owner commitment returns to owner decision.

Preserve the original teardown finding identity and record digest in planning and implementation artifacts. Create a new `REV-<NNN>` convergence finding only for a genuinely new defect or review lead discovered during implementation/current-head review, not for clearer wording or sequencing.

## 4. Resolve owner decisions

Build one decision packet before product edits. Include:

- every decision-required finding;
- conflicts and mutually exclusive paths;
- accepted-risk proposals;
- missing prerequisites or authority;
- materially changed findings;
- work requiring destructive data operations, purchases, credentials, publication, deployment, production changes, or external outreach.

For each decision provide concrete options, recommendation, consequences, dependencies, and default of no change.

Record an approval matrix covering every finding: `approved`, `deferred`, `rejected`, `accepted-risk`, or `not-applicable`. Retained strengths default to preservation and do not require a separate owner answer; record them as approved/retained after revalidation. If approved work could weaken, remove, or trade off a retained strength, elevate that specific tradeoff for explicit owner approval before editing. Do not start product edits while an unanswered decision can change the executable graph.

Preserve owner decisions already supplied. Do not ask again, soften them into suggestions, or upgrade agent recommendations into owner-approved decisions.

A narrowly approved subset is valid. Still revalidate and record every teardown finding exactly once; mark untouched findings deferred, rejected, accepted-risk, retained, not applicable, or blocked as appropriate. Subset scope reduces implementation work, not coverage, preservation, or convergence obligations for the resulting diff.

## 5. Planning-only workflow

When product edits are not authorized:

1. revalidate current state safely;
2. create or update only the requested planning artifact;
3. follow [planning-contract.md](references/planning-contract.md);
4. trace every teardown finding and every coverage/evidence condition;
5. distinguish teardown-derived content, new implementation recommendations, and genuinely new findings;
6. carry forward exact counts, statuses, dependencies, acceptance criteria, verification, affected surfaces, blockers, and owner decisions;
7. state clearly that no product edits or convergence testing occurred;
8. run `scripts/validate_revision_plan.py`.

Do not create `project-revision/revision.json` or an implementation ledger for a planning-only request unless the owner explicitly asks for a separate implementation artifact.

## 6. Plan implementation in dependency order

For implementation or continuation mode, create `project-revision/` or a clearly dated sibling. Never overwrite an existing revision record without permission.

Order approved work by prerequisites, then risk reduction, then severity and leverage. Group only truly independent findings.

Before each batch:

- confirm prerequisites have completed dispositions;
- identify overlap with baseline work;
- choose an edit strategy that preserves both intents;
- define focused success checks, failure-path checks, regression risks, environment requirements, and safe rollback;
- identify documentation, manifests, metadata, configuration, delivery, and user-facing claims that must change with the code.

Do not broaden the batch into opportunistic refactors, formatting, dependency churn, or unrelated cleanup.

## 7. Implement complete vertical changes

Implement all behavior required by the approved acceptance criteria. Include tests, docs, configuration, migrations, packaging, error handling, recovery, and removal of superseded paths where required.

When work touches destructive recovery, startup maintenance, trust boundaries, user-controlled parsing, processes, shell execution, provider protocols, platform-specific behavior, resource limits, persistence, or data egress, apply the relevant checks from [convergence-and-verification.md](references/convergence-and-verification.md).

After each finding or coupled batch:

1. run focused verification, including failure paths;
2. inspect the full batch diff against baseline;
3. confirm pre-existing work remains semantically intact;
4. record changed files, original acceptance criteria, current evidence, verification, and disposition;
5. do not mark work implemented while any required criterion fails or remains unverified.

If implementation disproves the plan, stop the affected dependency branch, update revalidation, and obtain any newly required decision before continuing.

## 8. Converge the implementation

Read [convergence-and-verification.md](references/convergence-and-verification.md) and execute the full convergence loop.

At minimum:

- review the entire baseline-to-current diff manually;
- rerun defining workflows and relevant end-to-end paths;
- run focused and full project checks;
- exercise risk-triggered failure, platform, fault-injection, packaging, and external-system checks;
- inspect current-head PR comments, reviews, CI, static analysis, and outside-diff leads when available;
- revalidate every actionable lead against the exact current head;
- record valid, stale, invalid, fixed, blocked, deferred, and open convergence findings;
- repeat review after every product-code fix until no new blocking lead appears.

A passing test suite does not prove convergence. A build on another platform does not prove platform behavior. A stale review comment does not justify a change.

## 9. Reconcile the final state

Before any readiness or delivery claim:

- inventory final staged, unstaged, and untracked paths;
- map every product path to approved finding IDs, fixed convergence IDs, or preserved pre-existing work;
- map every artifact path to revision-record maintenance;
- investigate unexpected files, deletions, mode changes, generated output, and lockfile churn;
- confirm all original acceptance criteria have current evidence;
- confirm all provisional limitations and required real-environment gates remain visible;
- refresh current-head PR, review, CI, remote, merge, release, and deployment facts;
- give every remaining gap an explicit disposition — being fixed in this run, awaiting an owner decision, or blocked by a named cause — and carry the disposition into the artifact and the user-facing handoff. An enumerated gap list with no dispositions is a disclaimer, not a reconciliation, and does not support a completion claim.

Use [preservation-and-delivery.md](references/preservation-and-delivery.md) for honest working-tree versus artifact-only-descendant sequencing.

## 10. Produce and validate the implementation artifact

Follow [revision-contract.md](references/revision-contract.md). Copy starter files from `assets/revision-template/` when useful, then replace every placeholder.

For implementation mode, treat `revision.json` as the canonical finding and convergence record. Generate the human entry point and implementation ledger before validation:

```bash
python3 <skill-directory>/scripts/render_revision_views.py <project-teardown-directory> <project-revision-directory>
```

Do not manually maintain `README.md` or `03-implementation-ledger.md`; regenerate them after every `revision.json` change.

Validate the requested artifact:

```bash
# Implementation mode
python3 <skill-directory>/scripts/validate_revision.py <project-teardown-directory> <project-revision-directory>

# Planning-only mode
python3 <skill-directory>/scripts/validate_revision_plan.py <project-teardown-directory> <planning-document>
```

Fix every artifact validation error. Skill-package validation and validator regression tests are maintenance tasks, never project-revision completion gates. Run them only when installing, packaging, or modifying the skill itself:

```bash
python3 <skill-directory>/scripts/validate_skill_bundle.py <skill-directory> --mode installed
python3 <skill-directory>/scripts/validate_skill_bundle.py <skill-directory> --mode package
python3 -m unittest discover -s <skill-directory>/scripts -p 'test_*.py' -v
```

Validator success is necessary, not sufficient. Manually inspect substantive correctness, current evidence, preservation, and convergence. A script cannot prove that a code change is correct, that an environment was genuinely exercised, or that an owner decision was understood.

If a bundled validator cannot run, do not invent a substitute or claim structural success. Report the exact blocker.

## User-facing handoff

State:

1. operating mode and exact project/revision state;
2. owner decisions and approved scope;
3. what was implemented, already satisfied, retained, deferred, rejected, accepted-risk, not applicable, or blocked;
4. verification and convergence evidence, including environment limits;
5. preservation and changed-path reconciliation;
6. implementation status, merge readiness, release readiness, and delivery state separately;
7. the generated implementation `README.md` entry point and paths to the full planning or implementation artifacts;
8. exact next action requiring the owner, external environment, credentials, review, merge, release, or deployment.

Never claim a commit, push, PR update, merge, release, deployment, migration, publication, or production verification that was not directly confirmed after the final relevant change.

## Forward testing

When changing the revision contract, the planning contract, the validators, or the
generated views, follow [forward-testing.md](references/forward-testing.md).
Passing unit tests are not evidence that the skill can carry a real teardown to
convergence.
