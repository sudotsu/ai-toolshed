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

Revalidation:

```text
confirmed|changed|stale|already_resolved|not_applicable|blocked
```

### acceptance and verification evidence

`acceptance_results` preserves every source acceptance criterion exactly once:

```json
{
  "criterion": "the affected flow remains coherent at mobile and desktop sizes",
  "status": "passed",
  "evidence": ["VERIFY-001"]
}
```

`verification_evidence` is a typed evidence ledger. Its `ref` values are what `acceptance_results[].evidence` cites:

```json
{
  "ref": "VERIFY-001",
  "level": "rendered_experience",
  "locator": "optional browser, screenshot, artifact, test, or observation locator"
}
```

Allowed evidence levels, weakest to strongest for this contract:

```text
source_inspection
rendered_experience
assistive_technology
published_experience
user_observation
first_party_measurement
business_outcome
```

Rules:

- fixed requires `approval: approved`;
- `accepted_risk` implementation requires `approval: accepted_risk`;
- each source acceptance criterion must appear exactly once in `acceptance_results`;
- a `passed` acceptance result requires evidence refs that resolve to `verification_evidence` rows;
- fixed requires every applicable criterion `passed|not_applicable`, terminal current-state revalidation, and verification evidence;
- a fixed visual, interaction, accessibility, or competitive UX/UI finding requires at least one acceptance-linked evidence row at `rendered_experience` or higher;
- `source_inspection` can support implementation correctness but does not by itself prove a visual or interaction outcome is fixed;
- retained strengths stay `preserved`, unless `preservation_status: approved_tradeoff` with explicit `approval: approved`;
- planning-only authorizes no mutation action, records no changed targets, and cannot claim `in_progress|fixed` implementation;
- planning-only cannot claim deployment or publication was performed;
- overall ready requires terminal preservation and terminal disposition for material open/decision-required findings;
- overall ready cannot contain findings whose current-state revalidation remains `blocked|stale`.

This contract does not make screen-reader testing a universal readiness requirement. Assistive-technology evidence is used when the finding or product context makes it material; representative keyboard/readability/accessibility checks remain governed by the teardown and affected-journey verification requirements.

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

`highest_evidence_level` uses the same evidence ladder documented above.
