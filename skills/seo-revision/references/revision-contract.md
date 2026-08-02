# SEO Revision Artifact Contract

`revision.json` is canonical. Generate every numbered Markdown file; never hand-edit generated registers.

```text
seo-revision/
├── 00-decisions-authority-and-scope.md
├── 01-baseline-drift-and-revalidation.md
├── 02-execution-rollout-and-measurement-plan.md
├── 03-implementation-ledger.md
├── 04-convergence-ledger.md
├── 05-production-search-and-experiment-verification.md
├── 06-readiness-and-handoff.md
├── revision.json
└── evidence/
```

Use schema version `seo-revision-v1`.

## Top-level shape

```json
{
  "schema_version": "seo-revision-v1",
  "mode": "planning-only",
  "project": {},
  "generated_at": "2026-07-30T12:00:00Z",
  "teardown": {},
  "workspace": {},
  "decisions": [],
  "authority_matrix": [],
  "findings": [],
  "coverage_trace": {},
  "changes": [],
  "evidence": [],
  "url_verifications": [],
  "experiments": [],
  "convergence_findings": [],
  "rollouts": [],
  "readiness": {}
}
```

No placeholder tokens such as `TODO`, `TBD`, `placeholder`, `lorem ipsum`, `<fill`, or `coming soon` are allowed in required evidence or completion fields.

## Project, teardown, and workspace

`project` requires:

```text
name, locator
```

`teardown` requires:

```text
path, findings_schema, coverage_schema, audited_revision, review_status,
validator_command, validator_result
```

The schemas must be `seo-teardown-v3` and `seo-teardown-coverage-v3`. The audited revision and project name must equal the canonical teardown. `validator_result` must be `passed`.

`workspace` requires:

```text
implementation_start_revision, product_endpoint, endpoint_kind,
artifact_relationship, existing_work_reconciled,
staged_paths, unstaged_paths, untracked_paths, baseline_evidence_ids
```

Controlled values:

- `endpoint_kind`: `immutable-revision|working-tree`
- `artifact_relationship`: `working-tree|artifact-only-descendant`

An artifact-only descendant requires an immutable product endpoint and verified commit delivery. A planning-only run uses a working-tree relationship and does not claim a product endpoint beyond the recorded baseline.

## Decisions

Each decision requires:

```text
id, finding_ids, status, question, options, recommendation,
owner_selection, safe_default, consequences, prerequisites, reversibility
```

- ID: `DEC-###`
- Status: `pending|resolved|blocked`
- Every option: `id`, `label`, `consequences`, `prerequisites`, `reversibility`
- `owner_selection` is null unless resolved.

Decision-required and blocked teardown findings, changed findings, accepted risks, and findings requiring an external or owner action must be covered by at least one decision.

## Authority matrix

Include exactly the fourteen IDs in `authority-and-external-actions.md`. Each row requires:

```text
id, state, scope, evidence_ids, limitations
```

State is `authorized|not-authorized|not-requested|blocked`. Authorized scope must be specific and supported by evidence or an explicit recorded owner decision. No authority implies another.

## Teardown findings

Every original teardown finding appears exactly once and uses its original title and dependency list.

Required keys:

```text
id, title, approval, revalidation, disposition, sequence, dependencies,
reason, acceptance_results, evidence_ids, change_ids, experiment_ids,
completion_gates, notes
```

Controlled values:

- `approval`: `approved|deferred|rejected|accepted-risk|not-applicable`
- `revalidation`: `confirmed|changed|stale|already-resolved|not-applicable|blocked`
- `disposition`: `planned|implemented|already-satisfied|preserved|deferred|rejected|accepted-risk|not-applicable|blocked|experiment-planned|experiment-launched|experiment-observing`

Approval/disposition compatibility:

| Approval | Allowed dispositions |
|---|---|
| approved | planned, implemented, already-satisfied, preserved, blocked, experiment-planned, experiment-launched, experiment-observing |
| deferred | deferred |
| rejected | rejected |
| accepted-risk | accepted-risk |
| not-applicable | not-applicable |

Use a unique positive sequence contiguous across all findings and preserve dependency order.

Each teardown acceptance criterion appears exactly once as:

```json
{
  "criterion": "Exact teardown criterion",
  "status": "pending",
  "evidence_ids": [],
  "observation": "Observable current result or completion gate"
}
```

Status is `pending|passed|failed|blocked|not-applicable`.

Rules:

- Planning-only approved work stays `planned` or `experiment-planned`; acceptance remains pending or blocked.
- `implemented` requires at least one mapped change and no stale/not-applicable/blocked revalidation.
- `already-satisfied` requires `already-resolved`.
- A strength finding must be `preserved` when approved.
- A complete implementation has no pending, failed, or blocked approved acceptance result.
- Every evidence, change, and experiment reference must resolve.

## Coverage trace

`coverage_trace` requires:

```text
access, surface_checks, material_limitations, deliberate_non_pursuits
```

Account for every canonical teardown item exactly once.

### Access

Each access row requires:

```text
category, source_status, disposition, completion_gate, evidence_ids
```

Disposition: `action|decision|blocker|preserve|not-applicable`.

### Surface checks

Each row requires:

```text
id, source_status, disposition, completion_gate, evidence_ids
```

Disposition: `action|decision|blocker|preserve|experiment|completion-gate|not-applicable`.

The ID and source status must equal the teardown. A blocked or partial source check needs a concrete completion gate.

### Material limitations

Each row requires:

```text
id, source_status, disposition, completion_gate, evidence_ids
```

Disposition: `open|resolved|not-applicable`. Unresolved teardown limitations cannot disappear.

### Deliberate non-pursuits

Each row requires:

```text
topic, rationale, preservation_rule, evidence_ids
```

Topic and rationale must equal the teardown. The preservation rule explains how revision work avoids recreating the rejected tactic.

## Changes

Changes record actual mutations, never planned work.

Required keys:

```text
id, scope, finding_ids, convergence_ids, targets, description,
external_authority_ids, risk_level, risk_categories, rollout_id, evidence_ids
```

- ID: `CHG-###`
- Scope: `repository|cms|content|configuration|asset|external-system`
- Risk: `low|medium|high`
- Risk categories use: `redirect-url-migration`, `canonical-noindex`, `robots-sitemap`, `structured-data`, `programmatic-template`, `dynamic-user-url`, `content-removal`, `analytics-consent`, `conversion-path`, `profile-listing`, `regulated-claim`, `javascript-rendering`, `browser-mobile-accessibility`, `other`.

Every change maps to an approved finding or fixed convergence finding. External-system changes require explicit authorized matrix rows and completed evidence. High-risk changes require a rollout.

## Evidence

Each evidence record requires:

```text
id, level, method, status, observation, artifact_path, limitations, observed_at
```

- ID: `REV-EVID-###`
- Level: `source-inspection|build-unit|local-render|preview-staging|deployed-production|search-platform-observation|business-outcome`
- Method: `source-inspection|build-unit|controlled-test|local-crawl|rendered-browser|live-fetch|platform-data|serp-observation|first-party-analysis|external-research|owner-authorization`
- Status: `completed|failed|blocked|not-applicable`

Completed evidence requires a concrete observation. Failed or blocked evidence requires a limitation and cannot support observed states.

## URL verification

Every URL verification requires:

```text
id, url, environment, method_evidence, observations, evidence_ids, limitations
```

- ID: `VERIFY-URL-###`
- Environment: `local|preview-staging|production`

Method evidence requires:

```text
method, status, observation, evidence_ids, limitations
```

Observation requires:

```text
dimension, status, value, supported_by_methods, evidence_ids, limitations
```

- Dimension: `http|canonical|render|eligibility|index|visibility|ai-citation|conversion|business-outcome`
- Status: `observed|unavailable|not-applicable`

Observed states require only completed supporting methods and completed evidence. Apply the minimum evidence rules in `verification-and-convergence.md`. Failed or blocked methods cannot support observations. Top-level evidence IDs must exactly reconcile method and observation evidence.

## Experiments

Every experiment requires:

```text
id, finding_ids, status, hypothesis, evidence_basis, segment,
affected_pages_queries, baseline, primary_metric, guardrails,
sample_requirement, expected_time_to_evidence, confounders,
stop_rollback_criteria, decision_rule, observation_owner,
next_review_at, evidence_ids
```

- ID: `EXP-###`
- Status: `planned|launched|observing|validated|rejected|blocked`

Validated or rejected experiments require completed search-platform or business-outcome evidence and application of the decision rule. Launched or observing experiments remain outcome-unverified.

## Convergence findings

Required keys:

```text
id, title, source, severity, status, reason, reopened_finding_ids,
change_ids, evidence_ids
```

- ID: `REV-###`
- Severity: `critical|high|medium|low`
- Status: `fixed|already-satisfied|invalid|open|deferred|blocked`

Fixed findings require a mapped change and completed verification evidence. Open, deferred, or blocked critical/high/medium findings prevent integration readiness.

## Rollouts

Required keys:

```text
id, change_ids, state, inventory, representative_samples,
collision_checks, rollback_plan, evidence_ids
```

- ID: `ROLLOUT-###`
- State: `not-required|planned|staged|activated|verified|blocked`

Every high-risk change has exactly one rollout. Inventory, representative samples, collision checks, and rollback plan must be concrete. `activated` or `verified` requires deployment or external evidence and matching authority.

## Readiness

Required keys:

```text
revision_status, review_convergence, integration, deployment,
publication, search_validation, experiment_status,
authorization_summary, convergence_evidence_ids, delivery,
unverified_outcomes, follow_up_actions
```

Controlled values:

- Revision status: `planned|complete|partial|blocked`
- Review convergence: `not-run|passed|blocked`
- Integration/deployment/publication: `ready|not-ready|not-applicable`
- Search validation: `not-started|eligibility-verified|index-observed|visibility-observed|outcome-observed|blocked|not-applicable`
- Experiment status: `not-applicable|planned|launched|observing|validated|rejected|blocked|mixed`
- Authorization summary: `complete|partial|blocked`
- Delivery fields: `verified|not-performed|unverified|not-applicable`

`delivery` contains exactly:

```text
committed, pushed, pull_request, merged, deployed, published,
search_platform_actions, external_profile_actions
```

Each delivery action is an object with:

```text
state, evidence_ids, observation
```

State is `verified|not-performed|unverified|not-applicable`. A verified action requires completed evidence at the level appropriate to the claim. Deployment and publication require deployed-production evidence; search-platform and external-profile actions require search-platform-observation or deployed-production evidence. Push, pull-request, merge, deployment, publication, and external changes also require their exact authority row to be authorized.

Planning-only requires planned revision status, not-run convergence, no change/convergence records, no verified delivery, and no ready integration/deployment/publication state.

Passed convergence requires completed current-state adversarial-review evidence in `convergence_evidence_ids`. Integration readiness requires reconciled existing work, passed convergence, zero blocking convergence findings, and no failed approved criterion. Deployment readiness requires integration readiness and complete high-risk rollout preparation. Publication readiness requires the applicable claim/content approval and publication authority.

Search-validation states require corresponding completed evidence. Technical completion alone leaves search validation `not-started` or `eligibility-verified`.

## Deterministic rendering and validation

Run:

```bash
python3 <skill-directory>/scripts/render_revision.py <seo-revision-directory>
python3 <skill-directory>/scripts/validate_seo_revision.py \
  <seo-teardown-directory> <seo-revision-directory>
```

The validator reruns the exact installed `seo-teardown` validator, checks the complete canonical relationship, and rejects Markdown drift.

## Final integrity review

After validator success:

1. Confirm source facts, authority, production, search, experiment, and delivery claims against current reality.
2. Confirm the teardown remains unchanged.
3. Confirm every product/external change maps to approved work.
4. Confirm all original findings, criteria, surface checks, access rows, limitations, strengths, and non-pursuits remain visible.
5. Confirm no lower evidence level is presented as higher-level success.
6. Confirm endpoint and artifact relationship are possible.
7. Refresh current-head PR, CI, deployment, production, and platform observations.
8. Confirm follow-up owner, environment, or platform actions are actionable.
