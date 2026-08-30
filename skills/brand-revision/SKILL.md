---
name: brand-revision
description: Revalidate, plan, implement, converge, and verify approved findings from a validated brand-teardown handoff while preserving authentic identity, truthful proof, working customer journeys, and explicit owner authority. Use when the user asks to resolve brand decisions, implement approved positioning, messaging, claim, identity, trust, visual, or channel changes, continue a brand revision branch or PR, or produce an auditable brand revision and perception-verification handoff.
---

# Brand Revision

Turn a validated `brand-teardown` handoff into approved brand changes without confusing implementation with customer perception or business outcomes.

The revision job is not “make the brand better.” It is to convert a read-only evidence record into a controlled change program that preserves what is already authentic and valuable, resolves strategic decisions before they leak into execution, corrects unsupported claims, and proves only what the available evidence can actually prove.

## Operating contract

- Treat the teardown as evidence and sequencing guidance, never as blanket permission to change the project.
- Preserve all pre-existing staged, unstaged, untracked, CMS, production, profile, listing, asset, and collateral work. Never reset, discard, overwrite, or silently normalize user work.
- Revalidate every finding against current state before implementation. Do not apply stale recommendations mechanically.
- Resolve owner-only decisions before editing any dependent brand surface. Naming, brand architecture, positioning, audience narrowing, primary promise, guarantees, founder posture, major offer changes, identity replacement, consolidation, and product/sub-brand relationships remain human decisions.
- Default every external, production, profile, publication, purchase, outreach, deployment, and delivery action to not authorized unless the owner explicitly authorizes that exact action.
- Preserve retained strengths and every teardown preservation constraint. A revision that removes authentic operator voice, useful quirks, recognizable identity, verified proof, low-pressure utility, or honest limitations is a regression unless the owner explicitly approves that tradeoff.
- Keep claim correction separate from persuasion. Never invent credentials, reviews, outcomes, tenure, licensing, certifications, guarantees, prices, service areas, customer language, market demand, or proof.
- Respect adjacent disciplines. Brand work may require product, SEO, accessibility, legal, conversion, engineering, or operations changes; record those dependencies and verify their relevant constraints instead of pretending brand authority supersedes them.
- Distinguish source implementation, rendered expression, channel publication, audience observation, and business outcome evidence. A changed homepage does not prove improved comprehension, trust, recognition, preference, conversion, or revenue.
- Do not call the revision complete merely because the diff looks better or tests pass. Require current-state reconciliation and adversarial convergence.
- Keep all machine-readable artifacts structurally valid before semantic processing. Malformed nested data must fail with path-aware errors rather than crashing a renderer or validator.
- Treat review bots, PR comments, design critiques, stakeholder notes, and prior agent suggestions as leads. Revalidate them against the current head before changing anything.
- Keep secrets, private customer data, analytics payloads, and sensitive operational evidence out of artifacts and chat. Store only the minimum sanitized observation needed to support a revision claim.

## 1. Select the operating mode

Determine whether the request is:

- `planning-only` — revalidation, decision packet, rollout plan, or revision artifact without product-edit authority;
- `implementation` — owner-approved project or content changes;
- `continuation` — continue an existing brand-revision branch, worktree, PR, or convergence cycle.

Do not infer implementation authority from a request to “review,” “plan,” “revise the strategy,” or “tell me what to change.” When the owner authorizes only a document, mockup, branch, subset of findings, or repository-local change, keep the scope exactly there.

Read the bundled references before acting:

- [revision-contract.md](references/revision-contract.md)
- [authority-and-external-actions.md](references/authority-and-external-actions.md)
- [verification-and-convergence.md](references/verification-and-convergence.md)
- [forward-testing.md](references/forward-testing.md) when changing or evaluating this skill

## 2. Validate the teardown and establish the baseline

Locate the intended `brand-teardown` directory. If multiple handoffs are plausible and current evidence cannot select one safely, use the one explicitly named by the owner or report the ambiguity before edits.

Locate the installed `brand-teardown` skill by its `name: brand-teardown` frontmatter and run its exact bundled `scripts/validate_brand_teardown.py` against the handoff. Never substitute a weaker validator. Stop on validation failure and report the exact errors.

Require canonical schemas:

- `findings.json`: `brand-teardown-v1`
- `coverage.json`: `brand-teardown-coverage-v1`

Read the entire handoff, not only finding titles:

- audit metadata and review status;
- evidence sources and claim inventory;
- every finding, acceptance criterion, dependency, conflict, priority, implementation target, non-goal, owner/external action, and preservation constraint;
- implementation phases;
- access ledger, modules, surface checks, surface samples, competitor samples, material limitations, and narrative reconciliation;
- generated decision, sequence, coverage, and claim registers;
- narrative evidence that materially changes interpretation.

Record the current baseline before any edit:

- current immutable revision or explicit working-tree identity;
- branch, remote, staged, unstaged, and untracked paths;
- current production/deployed state when material and accessible;
- current CMS/profile/listing/publication state when in scope;
- current primary brand surfaces at representative desktop/mobile or format states;
- current claim state and proof location for every claim affected by approved work;
- current PR/review/CI state when working through GitHub;
- current source-to-production alignment where a public brand surface is being revised.

If the audited revision differs from current source, production diverged, public channels changed, or the teardown was provisional, mark the handoff drifted and revalidate every affected finding. Provisional limitations do not disappear because implementation is now convenient.

## 3. Revalidate every finding

Process every teardown finding exactly once in canonical implementation order. For each finding:

1. inspect the current affected brands, audiences, surfaces, channels, and claims;
2. rerun the original observation or closest safe equivalent;
3. reassess the observed condition, desired condition, consequences, dependencies, conflicts, recommendation, acceptance criteria, verification methods, implementation targets, non-goals, and preservation constraints;
4. classify revalidation as `confirmed`, `changed`, `stale`, `already-resolved`, `not-applicable`, or `blocked`;
5. record concrete current evidence and explain any divergence from the teardown.

Do not implement stale or not-applicable findings. `already-resolved` requires current evidence that every original acceptance criterion is already satisfied.

If a finding materially changes in scope, brand architecture, authority, risk, audience, offer, claim posture, or owner commitment, return it to decision before implementation. Do not smuggle a new strategy into a “clarification.”

Keep the original finding ID and exact original acceptance criteria. Create a `REV-###` convergence finding only for a genuinely new defect or regression discovered during implementation/current-head review.

## 4. Resolve decisions and authority before execution

Build one decision packet before edits that covers:

- every `decision_required` teardown finding;
- any materially changed finding;
- any proposed accepted risk;
- any tradeoff against a retained strength or preservation constraint;
- naming, brand architecture, audience, positioning, promise, guarantee, identity, founder posture, major offer, consolidation, or product/sub-brand decisions;
- every action requiring production, CMS, social, listing, publication, purchase, outreach, deployment, merge, or other external authority;
- blocked work where a human, credential, private system, customer research, or operational record is required.

For each decision, provide concrete options, recommendation, consequences, prerequisites, reversibility, and the safe default of no change.

Record every finding approval as `pending`, `approved`, `deferred`, `rejected`, `accepted-risk`, or `not-applicable`.

Retained strengths default to approved preservation after revalidation. If approved work may weaken one, surface the exact tradeoff and require explicit approval before editing.

Preserve owner decisions already supplied. Do not ask again, soften them into suggestions, or elevate an agent recommendation into owner approval.

Apply the authority model in [authority-and-external-actions.md](references/authority-and-external-actions.md). No authority row implies another. Repository-edit approval does not authorize publication. Publication approval does not authorize profile changes. PR approval does not authorize merge. Merge does not authorize deployment.

## 5. Planning-only workflow

When implementation is not authorized:

1. validate and read the teardown;
2. capture current baseline and drift safely;
3. revalidate as far as available evidence allows;
4. create or update `brand-revision/revision.json` with `mode: planning-only`;
5. trace every finding, claim, access limitation, high/defining coverage gap, and preservation constraint;
6. build decisions, authority boundaries, dependency order, rollout requirements, perception tests, and completion gates;
7. do not create product changes, claim implementation, convergence success, publication, or outcome improvement;
8. render the human-readable registers;
9. validate the artifact.

The bundled bootstrap script can create a total-coverage planning scaffold from a validated teardown:

```bash
python3 <skill-directory>/scripts/bootstrap_revision.py \
  <brand-teardown-directory> <brand-revision-directory>
```

The bootstrap output is a scaffold, not completed revalidation. Replace its pending states with current evidence before using it as an implementation plan.

## 6. Plan implementation in brand dependency order

Use the teardown dependency graph and phase model unless current evidence proves a correction is needed and the owner approves the material change.

Default sequencing:

1. owner decisions and brand architecture;
2. unsupported, contradicted, outdated, or high-risk claim correction;
3. service/product proof and trust-system changes;
4. positioning, message hierarchy, offer, and customer-journey changes;
5. visual identity or recognition-system changes;
6. channel rollout, domain/profile/listing alignment, and collateral propagation;
7. measurement and audience/perception research;
8. externally blocked work;
9. preservation verification throughout every phase.

Before each batch:

- confirm all dependencies have completed dispositions;
- identify affected claims and preservation constraints;
- search every relevant use before changing shared copy, tokens, components, assets, metadata, templates, brand names, or channel records;
- define exact success criteria and failure paths;
- identify cross-domain constraints such as accessibility, SEO, legal review, conversion routing, analytics, or engineering behavior;
- define rollback for high-risk identity, URL, navigation, claim, publication, profile, or channel changes;
- identify the evidence level required to prove implementation and the separate evidence required to observe audience or business effects.

Do not broaden a brand revision into unrelated redesign, refactoring, dependency churn, content generation, or channel expansion.

## 7. Implement complete vertical changes

Implement the smallest complete change that satisfies the approved acceptance criteria and preserves the required identity constraints.

A complete vertical brand change may include, where applicable:

- source copy and metadata;
- content models and shared configuration;
- claim correction and proof placement;
- reusable identity tokens/components;
- visual assets and provenance records;
- responsive/mobile expression;
- service/product/offering hierarchy;
- navigation and customer-journey handoff;
- tests and screenshots;
- documentation and governance notes;
- migration or rollout preparation;
- rollback instructions;
- cross-channel propagation tasks that remain explicitly blocked until separately authorized.

After each finding or coupled batch:

1. run focused checks and failure paths;
2. inspect the full batch diff against baseline;
3. verify all affected preservation constraints;
4. verify affected claims remain truthful and appropriately qualified;
5. exercise the affected rendered journey at representative states;
6. record exact changed targets and evidence;
7. leave the finding incomplete if any original acceptance criterion remains failed, pending, or blocked.

If implementation disproves the plan, stop the affected dependency branch, update revalidation, and obtain any newly required decision.

## 8. Converge the revision

Follow [verification-and-convergence.md](references/verification-and-convergence.md).

At minimum:

- freeze the exact product state under review;
- review the entire baseline-to-current diff manually;
- trace cross-finding interactions, especially identity, claims, proof, navigation, offer, and responsive changes;
- rerun defining customer journeys and primary channel expressions;
- inspect current-head PR comments, reviews, CI, static analysis, and stakeholder/design-review leads when available;
- revalidate every lead against the exact current head;
- record new regressions as `REV-###` findings;
- reopen an original finding when its original acceptance criteria fail;
- fix valid defects in dependency and severity order;
- repeat the review loop after every meaningful change until no new blocking lead appears.

Do not stop with an unresolved critical/high/medium convergence defect that affects truthful claims, identity coherence, accessibility/legibility, customer action, working conversion paths, or approved preservation constraints.

## 9. Verify expression separately from perception and outcomes

Use the evidence levels in [verification-and-convergence.md](references/verification-and-convergence.md):

1. `source-inspection`
2. `rendered-experience`
3. `published-channel`
4. `audience-observation`
5. `first-party-measurement`
6. `business-outcome`

A lower level never proves a higher level.

Implementation can prove that approved words, visuals, relationships, or proof elements are present and internally coherent. It cannot by itself prove that people understand faster, trust more, remember the brand, prefer it, convert more, or generate more revenue.

When the owner wants perception evidence, define a bounded test protocol rather than asking leading questions. Record audience segment, sample source, prompt/protocol, dimensions, baseline, result, limitations, and evidence. Label small informal tests honestly; do not inflate them into market research.

When the owner wants business-outcome evidence, use actual first-party observations with time windows and confounders. Never backfill a business result from subjective approval or implementation completion.

## 10. Reconcile the final state

Before any readiness or delivery claim:

- inventory final staged, unstaged, and untracked paths;
- map every changed product path to approved finding IDs or fixed convergence IDs;
- map every external/public mutation to an explicitly authorized authority row;
- map every affected teardown claim to its current revision action and evidence;
- confirm every retained strength and preservation constraint remains satisfied or carries an explicit owner-approved tradeoff;
- carry forward every unresolved material limitation and blocked access item;
- confirm all original acceptance criteria have current statuses and evidence;
- refresh current-head PR, review, CI, deployment, publication, and external-channel facts;
- give every remaining gap an explicit disposition and owner/environment completion gate.

Being “implemented” is not the same as integrated, deployed, published, perception-validated, or outcome-validated.

## 11. Produce and validate the artifact

`revision.json` is canonical. Follow [revision-contract.md](references/revision-contract.md).

Render the human-readable registers:

```bash
python3 <skill-directory>/scripts/render_revision.py <brand-revision-directory>
```

Validate the artifact against the exact teardown:

```bash
python3 <skill-directory>/scripts/validate_brand_revision.py \
  <brand-teardown-directory> <brand-revision-directory>
```

Fix every validation error. Validator success is necessary, not sufficient. Manually inspect factual support, decision authority, claim truthfulness, preservation, current public state, convergence, and evidence-level discipline.

When modifying or packaging the skill itself, run:

```bash
python3 <skill-directory>/scripts/validate_skill.py <skill-directory>
python3 -m unittest discover -s <skill-directory>/scripts -p 'test_*.py' -v
```

Package validation proves structural compatibility, not runtime behavioral parity. Follow [forward-testing.md](references/forward-testing.md) before claiming a material skill change is ready.

## Handoff

Report separately:

1. operating mode and exact project/revision state;
2. owner decisions and authority granted or withheld;
3. finding dispositions and preserved strengths;
4. claim corrections and proof changes;
5. exact changed paths and external/public mutations;
6. verification and convergence evidence levels;
7. implementation, integration, deployment, publication, perception-validation, and business-outcome states;
8. remaining limitations, blockers, and completion gates;
9. artifact path and validator result;
10. the exact next action requiring the owner, credentials, external system, review, merge, deployment, publication, audience research, or first-party measurement.

Never claim a commit, push, PR update, merge, deployment, publication, profile change, outreach action, audience improvement, conversion lift, or revenue effect that was not directly verified after the final relevant change.
