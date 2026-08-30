# Brand Revision Artifact Contract

`revision.json` is canonical. The renderer owns every Markdown file in the revision directory except evidence artifacts.

```text
brand-revision/
├── README.md
├── 00-decisions-authority-and-scope.md
├── 01-baseline-and-revalidation.md
├── 02-strategy-execution-and-rollout-plan.md
├── 03-implementation-ledger.md
├── 04-claims-and-preservation-ledger.md
├── 05-convergence-and-perception-verification.md
├── 06-readiness-and-handoff.md
├── revision.json
└── evidence/
```

Use schema version `brand-revision-v1`.

## Top-level shape

```json
{
  "schema_version": "brand-revision-v1",
  "mode": "planning-only",
  "project": {},
  "generated_at": "2026-08-29T00:00:00Z",
  "teardown": {},
  "workspace": {},
  "decisions": [],
  "authority_matrix": [],
  "findings": [],
  "claim_trace": [],
  "coverage_trace": {},
  "changes": [],
  "evidence": [],
  "perception_tests": [],
  "convergence_findings": [],
  "rollouts": [],
  "readiness": {}
}
```

No placeholder tokens such as `TODO`, `TBD`, `placeholder`, `lorem ipsum`, `<fill`, or `coming soon` are allowed in required completed fields. Controlled pending states are allowed only where this contract explicitly permits them.

## Project and teardown

`project` requires:

```text
name, locator, production_locator
```

`teardown` requires:

```text
path, findings_schema, coverage_schema, audited_revision, review_status,
validator_command, validator_result
```

The canonical schemas must be `brand-teardown-v1` and `brand-teardown-coverage-v1`. Project name, locator, audited revision, and teardown review status must equal the canonical teardown. `validator_result` must be `passed` for an artifact that claims upstream validation.

## Workspace

Required keys:

```text
implementation_start_revision, product_endpoint, endpoint_kind,
artifact_relationship, existing_work_reconciled,
staged_paths, unstaged_paths, untracked_paths, baseline_evidence_ids
```

Controlled values:

- `endpoint_kind`: `immutable-revision|working-tree`
- `artifact_relationship`: `working-tree|artifact-only-descendant`

Planning-only normally uses `working-tree`. `artifact-only-descendant` requires an immutable product endpoint and verified commit delivery.

## Decisions

Each decision requires:

```text
id, finding_ids, category, status, question, options, recommendation,
owner_selection, safe_default, consequences, prerequisites, reversibility,
evidence_ids
```

- ID: `DEC-###`
- category: `brand-architecture|positioning|audience|promise|offer|guarantee|founder-posture|visual-identity|claim-posture|channel-migration|accepted-risk|external-authority|other`
- status: `pending|resolved|blocked`
- `owner_selection` is null unless resolved.
- Every option requires `id`, `label`, `consequences`, `prerequisites`, and `reversibility`.

Every teardown `decision_required` finding must map to at least one decision. A finding cannot have approval `approved` while its required decision remains pending or blocked.

## Authority matrix

Include exactly the fifteen IDs in `authority-and-external-actions.md`.

Each row requires:

```text
id, state, scope, evidence_ids, limitations
```

State: `authorized|not-authorized|not-requested|blocked`.

Every actual mutation in `changes` must map to the exact authority required for its scope. Every verified delivery action must also have the required authority.

## Findings

Every teardown finding appears exactly once. Required keys:

```text
id, title, source_status, approval, revalidation, disposition, sequence,
dependencies, reason, acceptance_results, evidence_ids, change_ids,
perception_test_ids, preservation_constraints, preservation_status,
completion_gates, notes
```

Controlled values:

- `approval`: `pending|approved|deferred|rejected|accepted-risk|not-applicable`
- `revalidation`: `pending|confirmed|changed|stale|already-resolved|not-applicable|blocked`
- `disposition`: `planned|implemented|already-satisfied|preserved|deferred|rejected|accepted-risk|not-applicable|blocked|investigating`
- `preservation_status`: `pending|preserved|owner-approved-tradeoff|not-applicable|failed`

Rules:

- `title`, `source_status`, `dependencies`, and `preservation_constraints` must exactly equal the teardown finding.
- Sequence must exactly preserve canonical teardown implementation order.
- Dependencies must exist and be earlier in sequence.
- Every original acceptance criterion appears exactly once as:

```json
{
  "criterion": "Exact teardown criterion",
  "status": "pending",
  "evidence_ids": [],
  "observation": "Concrete current observation or completion gate"
}
```

Acceptance status: `pending|passed|failed|blocked|not-applicable`.

- Planning-only work may remain `pending` and `planned`.
- `implemented` requires approval `approved`, revalidation `confirmed|changed`, at least one mapped change, no failed acceptance criterion, and every passed criterion supported by completed evidence.
- `already-satisfied` requires `already-resolved` and all applicable criteria passed.
- A teardown `retained_strength` must use disposition `preserved` unless the owner explicitly approved a tradeoff and the artifact records it.
- `preservation_status: preserved` requires current completed evidence.
- `preservation_status: owner-approved-tradeoff` requires a resolved decision covering the finding.
- A complete implementation has no pending/failed/blocked acceptance result for approved implemented work and no failed preservation status.

## Claim trace

Every canonical teardown claim appears exactly once.

Required keys:

```text
id, claim, brand, source_state, action, target_state, finding_ids,
change_ids, evidence_ids, verification_status, notes
```

- `id`, `claim`, `brand`, and `source_state` must equal the teardown claim.
- `action`: `pending|preserve|correct|qualify|remove|verify|not-applicable|unchanged`
- `target_state`: `verified|plausible_unverified|unsupported|contradicted|outdated|not_applicable`
- `verification_status`: `pending|verified|unverified|blocked|not-applicable`

Rules:

- `verification_status: verified` requires completed claim-verification evidence. An upstream claim may retain `target_state: verified` during planning while current revision verification remains `pending`; source state is not fresh revision proof.
- Corrected, qualified, or removed public claims require mapped changes when implementation has occurred.
- Unsupported/contradicted/outdated source claims cannot silently become verified.
- Planning-only may use `action: pending`.

## Coverage trace

`coverage_trace` requires:

```text
access, modules, surface_checks, material_limitations
```

Every canonical teardown item in those four collections appears exactly once.

### Access rows

```text
category, source_status, disposition, completion_gate, evidence_ids
```

Disposition: `pending|action|decision|blocker|preserve|not-applicable|resolved`.

### Module rows

```text
id, source_status, disposition, completion_gate, evidence_ids
```

Disposition: `pending|action|decision|blocker|preserve|completion-gate|not-applicable|resolved`.

### Surface-check rows

```text
id, source_status, disposition, completion_gate, evidence_ids
```

Disposition: `pending|action|decision|blocker|preserve|perception-test|completion-gate|not-applicable|resolved`.

### Material limitations

```text
id, description, source_status, disposition, completion_gate, evidence_ids
```

Disposition: `open|resolved|not-applicable`.

An open teardown limitation cannot disappear. A complete revision may retain open limitations if they concern unobserved perception/business outcomes, but readiness must not claim those outcomes.

## Changes

Changes record actual mutations only.

Required keys:

```text
id, scope, finding_ids, convergence_ids, targets, description,
authority_ids, risk_level, risk_categories, rollout_id, evidence_ids
```

- ID: `CHG-###`
- scope: `repository|content|asset|configuration|cms|external-profile|business-listing|published-channel|other`
- risk: `low|medium|high`
- risk categories: `brand-architecture|claim|credential|guarantee|offer|identity-recognition|domain-channel-migration|proof-publication|customer-journey|accessibility-legibility|seo-discoverability|analytics-measurement|other`

Every change maps to approved findings or fixed convergence findings. High-risk changes require exactly one rollout record.

## Evidence

Each evidence record requires:

```text
id, level, method, status, observation, artifact_path, limitations, observed_at
```

- ID: `REV-EVID-###`
- level: one of the six levels in `verification-and-convergence.md`
- method: one allowed method in that reference
- status: `completed|failed|blocked|not-applicable`

Completed evidence requires a non-empty concrete observation. Failed/blocked evidence requires limitations and cannot support passed criteria, verified claims, completed perception tests, or verified delivery actions.

## Perception tests

Each record requires:

```text
id, finding_ids, dimensions, status, audience_segment, sample_source,
protocol, baseline, result, limitations, evidence_ids
```

- ID: `PERCEPT-###`
- dimensions: `comprehension|trust|differentiation|recognition|preference|action-clarity`
- status: `planned|completed|blocked|not-applicable`

Completed tests require completed `audience-observation` evidence. Planning-only tests may remain planned without result evidence.

## Convergence findings

Required keys:

```text
id, title, source, severity, status, reason, reopened_finding_ids,
change_ids, evidence_ids
```

- ID: `REV-###`
- severity: `critical|high|medium|low`
- status: `fixed|already-satisfied|invalid|open|deferred|blocked`

Fixed findings require a mapped change and completed evidence. Open/deferred/blocked critical/high/medium findings prevent convergence from passing.

## Rollouts

Required keys:

```text
id, change_ids, state, inventory, representative_samples,
collision_checks, rollback_plan, authority_ids, evidence_ids
```

- ID: `ROLLOUT-###`
- state: `planned|staged|activated|verified|blocked|not-required`

Every high-risk change must map to exactly one rollout. Activation/verification of public or external rollouts requires matching authority and evidence at `published-channel` or higher when public state is claimed.

## Readiness

Required keys:

```text
revision_status, review_convergence, integration, deployment, publication,
perception_validation, business_outcome, authorization_summary,
convergence_evidence_ids, delivery, unverified_outcomes, follow_up_actions
```

Controlled values:

- `revision_status`: `planned|complete|partial|blocked`
- `review_convergence`: `not-run|passed|blocked`
- integration/deployment/publication: `ready|not-ready|not-applicable`
- `perception_validation`: `not-started|observed|partially-observed|blocked|not-applicable`
- `business_outcome`: `unverified|observed|blocked|not-applicable`
- `authorization_summary`: `complete|partial|blocked`

`delivery` contains exactly:

```text
committed, pushed, pull_request, merged, deployed, published,
social_profile_changes, business_listing_changes, outreach
```

Each delivery row:

```text
state, evidence_ids, observation
```

State: `verified|not-performed|unverified|not-applicable`.

Planning-only requires:

- revision status `planned|blocked`;
- convergence `not-run|blocked`;
- no `changes` or `convergence_findings` that claim implementation;
- no ready integration/deployment/publication;
- no verified delivery mutation;
- perception/business outcomes unverified, blocked, or not applicable.

Passed convergence requires completed current-head convergence evidence and zero blocking convergence findings. Integration readiness requires reconciled existing work, passed convergence, no failed approved criterion, and preservation success. Deployment readiness requires integration readiness and complete high-risk rollout preparation. Publication readiness additionally requires publication authority and claim/proof readiness.

Perception `observed|partially-observed` requires completed audience-observation evidence. Business outcome `observed` requires completed business-outcome evidence.

## Deterministic rendering and validation

Run:

```bash
python3 <skill-directory>/scripts/render_revision.py <brand-revision-directory>
python3 <skill-directory>/scripts/validate_brand_revision.py \
  <brand-teardown-directory> <brand-revision-directory>
```

The validator reruns the exact installed `brand-teardown` validator unless explicitly skipped for isolated validator tests, verifies the full canonical relationship, and rejects generated Markdown drift.
