# UX/UI revision v2 contract

Schema: `ux-ui-revision-v2`.

Top-level:

```text
schema_version
mode
source
baseline
authority
findings
decisions
convergence
readiness
```

Modes: `planning-only|implementation|continuation`.

## finding rows

Every teardown finding appears exactly once.

```text
finding_id
original_status
revalidation
approval
implementation_status
current_evidence
changed_targets
acceptance_results
verification_evidence
preservation_status
notes
```

Approval:

```text
pending|approved|deferred|rejected|accepted_risk|not_applicable
```

Implementation:

```text
not_started|planned|in_progress|fixed|preserved|blocked|deferred|rejected|accepted_risk|not_applicable
```

Preservation:

```text
pending|preserved|regressed|approved_tradeoff|not_applicable
```

Rules:

- fixed requires `approval: approved`;
- `accepted_risk` implementation requires `approval: accepted_risk`;
- each source acceptance criterion must appear exactly once in `acceptance_results`;
- fixed requires every applicable criterion `passed|not_applicable` and verification evidence;
- retained strengths stay `preserved`, unless `preservation_status: approved_tradeoff` with explicit `approval: approved`;
- planning-only cannot record changed targets;
- overall ready requires terminal preservation and terminal disposition for material open/decision-required findings.

## decisions

IDs: `DEC-###`.

```text
id
finding_ids
question
options
recommendation
status
owner_evidence
```

Status: `pending|resolved|deferred`.

A source finding with `status: decision_required` must have a linked decision. A fixed/approved implementation of that finding requires the decision to be resolved with owner evidence.

## convergence

IDs: `REVUX-###`.

Statuses: `open|fixed|accepted_risk|not_applicable`.

Material open convergence findings block readiness.

## readiness

Implementation/integration: `not_started|in_progress|ready|blocked`.

Deployment/publication: `not_performed|performed|blocked|not_applicable`.

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
