# UX/UI Revision Contract

Canonical artifact: `revision.json`.

Schema version: `ux-ui-revision-v1`.

Top-level:

```text
schema_version, mode, source, baseline, authority, findings,
decisions, convergence, readiness
```

Before bootstrap or validation, run the exact `ux-ui-teardown` validator against the source handoff. Schema names and digests do not substitute for upstream semantic validation.

## mode

`planning-only|implementation|continuation`.

## source

```text
teardown_schema_version
coverage_schema_version
teardown_revision
teardown_review_status
teardown_findings_digest
```

## baseline

```text
current_revision
working_tree_state
production_revision_status
captured_at
material_drift
drift_notes
```

## authority

Include exactly:

```text
repository_edit
design_file_edit
cms_edit
public_content_publish
production_deploy
external_profile_change
analytics_mutation
paid_purchase
third_party_outreach
merge
```

Each row:

```text
action, status, scope, evidence
```

Status: `authorized|not_authorized|not_applicable`.

Authorization must be explicit and action-specific.

## findings

Every teardown finding appears exactly once.

Each row:

```text
finding_id, original_status, revalidation, approval,
implementation_status, current_evidence, changed_targets,
acceptance_results, verification_evidence, preservation_status,
notes
```

`revalidation`:

```text
confirmed|changed|stale|already_resolved|not_applicable|blocked
```

`approval`:

```text
pending|approved|deferred|rejected|accepted_risk|not_applicable
```

`implementation_status`:

```text
not_started|planned|in_progress|fixed|preserved|blocked|deferred|rejected|accepted_risk|not_applicable
```

`preservation_status`:

```text
pending|preserved|regressed|approved_tradeoff|not_applicable
```

Use `pending` until current-state evidence has checked the applicable preservation constraints. `approved_tradeoff` requires explicit approval. A planning scaffold may therefore show `implementation_status: preserved` for a retained-strength row while leaving `preservation_status: pending` until revalidation proves the current state still preserves it.

Each `acceptance_results` row:

```text
criterion, status, evidence
```

Status: `passed|failed|pending|blocked|not_applicable`.

Rules:

- stale/not-applicable teardown findings cannot be marked fixed;
- fixed requires `approval: approved`;
- fixed requires every applicable acceptance criterion passed;
- retained-strength findings use `preserved` unless an explicit approved tradeoff exists;
- `approved_tradeoff` preservation requires `approval: approved`;
- `changed_targets` must be empty in planning-only mode;
- current evidence is required for confirmed/changed/already-resolved;
- accepted risk requires `approval: accepted_risk`;
- implementation cannot imply external publication/deployment without matching authority;
- `overall: ready` requires every finding's preservation status to be terminal: `preserved|approved_tradeoff|not_applicable`.

## decisions

Each:

```text
id, finding_ids, question, options, recommendation, status, owner_evidence
```

Status: `pending|resolved|deferred`.

## convergence

```text
reviewed_revision
status
findings
```

Status: `not_started|in_progress|converged|blocked`.

Each convergence finding:

```text
id, severity, title, affected_journeys, status, evidence, resolution
```

ID: `REVUX-###`.

Status: `open|fixed|accepted_risk|not_applicable`.

## readiness

```text
implementation
integration
deployment
publication
user_outcome
business_outcome
overall
highest_evidence_level
limitations
```

Implementation/integration: `not_started|in_progress|ready|blocked`.

Deployment/publication: `not_performed|performed|blocked|not_applicable`.

User/business outcome: `unverified|partial|verified|not_applicable`.

Overall: `planned|not_ready|ready|blocked`.

Evidence level:

```text
source_inspection
rendered_experience
assistive_technology
published_experience
user_observation
first_party_measurement
business_outcome
```

`overall: ready` requires:

- implementation and integration `ready`;
- no unresolved critical/high/medium convergence defect unless accepted risk;
- every open/decision-required material teardown finding has a terminal approved disposition;
- every retained strength preserved or explicitly traded off;
- every finding has terminal preservation status (`preserved|approved_tradeoff|not_applicable`);
- no false publication/deployment claim;
- limitations do not contradict readiness.

Readiness does not require user/business outcomes to be verified unless the owner explicitly defined those as the completion gate.