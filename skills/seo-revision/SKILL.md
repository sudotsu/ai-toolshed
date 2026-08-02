---
name: seo-revision
description: Plan, implement, converge, and verify approved findings from a validated seo-teardown v3 handoff. Use when Codex must revalidate SEO findings against current source and production, resolve owner decisions and authority boundaries, make repository or explicitly authorized external SEO changes, preserve limitations and strengths, verify deployment and search eligibility without inflating rankings or outcomes, run adversarial convergence, or produce a durable SEO revision and experiment handoff.
---

# SEO Revision

Turn a validated `seo-teardown` v3 handoff into approved, evidence-backed changes and an honest readiness record. Treat the teardown as evidence and sequencing guidance, not permission to apply stale recommendations or mutate external systems.

## Operating contract

- Preserve all pre-existing staged, unstaged, untracked, CMS, production, and external-system state. Never discard or overwrite user work.
- Default to no external or production mutation. Repository-edit approval does not authorize commit, push, merge, deployment, publication, search-platform, analytics, profile, listing, outreach, purchase, or regulated-content actions.
- Never request credentials in chat. Use configured secure connections or leave the action blocked.
- Revalidate every finding against current source, deployed production, and current primary platform documentation where material.
- Separate technical implementation, deployment, search eligibility, observed indexing, visibility, AI citation/referral, engagement, conversion, qualified outcome, and revenue.
- Never invent demand, rankings, competitors, reviews, business facts, credentials, prices, guarantees, authorship, expert review, measurement, citations, or results.
- Preserve teardown limitations, blocked evidence, strengths, explicit non-goals, and deliberate non-pursuits.
- Treat unsupported SEO or GEO tactics only as labeled experiments with falsifiable decision rules.
- Do not call implementation complete because code checks pass. Require adversarial convergence and current-state reconciliation.

## 1. Validate the input and establish the baseline

Read all bundled references:

- [revision-contract.md](references/revision-contract.md)
- [authority-and-external-actions.md](references/authority-and-external-actions.md)
- [verification-and-convergence.md](references/verification-and-convergence.md)
- [forward-testing.md](references/forward-testing.md) when testing or changing this skill

Locate the installed `seo-teardown` skill by the `name: seo-teardown` frontmatter and run its exact bundled `scripts/validate_seo_teardown.py`. Never substitute a custom validator. Stop on failure.

Require matching canonical schemas:

- `findings.json`: `seo-teardown-v3`
- `coverage.json`: `seo-teardown-coverage-v3`

Read the complete teardown, generated registers, evidence, owner decisions, SERP and URL samples, method evidence, surface checks, access ledger, strengths, material limitations, and deliberate non-pursuits. Do not reduce it to finding titles.

Before product edits, record:

- immutable source revision or explicit working-tree identity;
- staged, unstaged, and untracked paths plus byte-preservation for overlapping files;
- toolchain, build, test, crawl, render, content, conversion, and production baselines;
- current branch, pull request, review, CI, deployment, CMS, publication, and external state when accessible and in scope;
- audited-source versus current-source drift;
- current-source versus deployed-production alignment;
- stale platform-sensitive evidence and refreshed primary documentation.

Create `seo-revision/` beside the project unless the user specifies another path. Use a dated sibling when one exists unless replacement is explicitly authorized.

## 2. Revalidate, decide, and authorize

Classify every teardown finding exactly once as:

`confirmed`, `changed`, `stale`, `already-resolved`, `not-applicable`, or `blocked`.

Do not implement stale or not-applicable findings. Return materially changed behavior, scope, risk, claims, or external actions to owner decision.

Produce one owner decision packet before edits. Cover every decision-required or blocked finding, changed finding, accepted risk, mutually exclusive strategy, claim or credential boundary, URL migration, local-profile change, measurement definition, experiment, and authority beyond local edits. Give concrete options, a recommendation, consequences, prerequisites, reversibility, and the safe default of no change.

Record every finding approval as:

`approved`, `deferred`, `rejected`, `accepted-risk`, or `not-applicable`.

Do not begin edits while a pending decision can change the executable dependency graph. Apply the authority matrix in [authority-and-external-actions.md](references/authority-and-external-actions.md).

### Planning-only execution

When asked only for revalidation, decisions, or a plan:

- do not edit the product or external systems;
- keep mode `planning-only` and revision status `planned`;
- do not create change records, implementation claims, convergence claims, or ready states;
- trace every finding, criterion, dependency, surface check, access constraint, material limitation, strength, and deliberate non-pursuit into an action, decision, blocker, preservation rule, experiment, or observable completion gate;
- distinguish teardown-derived work, new sequencing recommendations, and genuinely new findings;
- state that planning did not exercise implementation behavior.

## 3. Implement approved work

Work in valid dependency order:

1. Safety, policy, legal, regulated-content, and destructive search-control risks.
2. Crawl, render, canonical, indexing, URL, and entity foundations.
3. Shared template and data-model root causes.
4. Claim accuracy, usefulness, authority, and trust.
5. Qualified-conversion paths and measurement.
6. Content and discoverability opportunities.
7. Reversible experiments and longer-term authority work.

Search every relevant use before editing shared routing, templates, metadata, structured data, content models, analytics, or entity records. Implement the smallest complete change that satisfies approved acceptance criteria, including tests, configuration, migration, documentation, monitoring, and rollback preparation.

Apply the SEO-native rules in [verification-and-convergence.md](references/verification-and-convergence.md). Treat redirects, canonicals, robots, noindex, sitemap removals, URL migrations, programmatic pages, content deletion, analytics, consent, profiles, and regulated claims as high risk.

After each finding or coupled batch:

1. Run focused checks and failure paths.
2. Reproduce the original state or opportunity.
3. Inspect the complete diff against baseline.
4. Verify strengths and deliberate non-pursuits remain intact.
5. Record exact changed targets and evidence levels.
6. Leave the finding incomplete when any required criterion is failed or blocked.

## 4. Converge and verify

Run the adversarial loop in [verification-and-convergence.md](references/verification-and-convergence.md):

1. Freeze the exact product state.
2. Review the complete baseline-to-current diff.
3. Trace cross-finding interactions.
4. Exercise affected user and crawler journeys end to end.
5. Inspect every available current-head review source and its skipped, partial, stale, outside-diff, or rate-limited state.
6. Revalidate each lead and record it as `REV-###`.
7. Reopen an original finding when its acceptance criteria failed.
8. Fix confirmed defects in dependency and severity order and add regression coverage.
9. Repeat after every meaningful fix.

Do not stop with a confirmed critical, high, or medium convergence defect unresolved.

Use these evidence levels without inflation:

1. `source-inspection`
2. `build-unit`
3. `local-render`
4. `preview-staging`
5. `deployed-production`
6. `search-platform-observation`
7. `business-outcome`

A lower level never proves a higher level.

## 5. Produce and validate the artifact

Follow [revision-contract.md](references/revision-contract.md). `revision.json` is canonical. Generate all numbered Markdown registers:

```bash
python3 <skill-directory>/scripts/render_revision.py <seo-revision-directory>
```

Validate with the exact upstream teardown validator and this skill's validator:

```bash
python3 <skill-directory>/scripts/validate_seo_revision.py \
  <seo-teardown-directory> <seo-revision-directory>
```

Fix every error. Validator success is necessary, not sufficient: manually reconcile factual support, authority, diffs, deployment, current production, search observations, experiments, readiness, delivery facts, and preserved limitations.

A committed artifact cannot contain its own commit hash. Record the last product-code commit, then make only artifact changes in an artifact-only descendant. If uncommitted, record an explicit working-tree relationship.

## Handoff

Report:

1. Revision status and product endpoint.
2. Artifact relationship.
3. Finding and convergence dispositions.
4. Evidence levels achieved and blocked.
5. Integration, deployment, publication, search-validation, and experiment states.
6. Exact commit, push, PR, merge, deployment, publication, platform, and external-action facts.
7. Preserved work, strengths, limitations, and non-pursuits.
8. Follow-up owners and review points.
9. Artifact path and validator result.

Never imply that readiness grants authorization or that technical completion proves search or business success.
