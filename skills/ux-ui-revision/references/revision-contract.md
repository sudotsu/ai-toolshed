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
changed_target_actions
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

### changed targets and edit authority

`changed_targets` records concrete product/design/CMS targets changed by this revision.

`changed_target_actions` binds each changed target to the exact mutation authority that permitted it:

```json
{
  "src/components/Flow.tsx": "repository_edit",
  "Figma/Checkout": "design_file_edit",
  "cms:homepage.hero": "cms_edit"
}
```

Rules:

- when `changed_targets` is non-empty, `changed_target_actions` must map every changed target exactly once and may not contain extra targets;
- values must be one of `repository_edit|design_file_edit|cms_edit`;
- each mapped authority must itself be `authorized`;
- an authorized action needs a non-empty text scope and evidence of that authorization;
- an `in_progress|fixed` implementation claim with no concrete changed target still requires at least one authorized edit action unless the finding was `already_resolved` before this revision run;
- access to a repository/design/CMS does not imply mutation authority.

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
  "timing": "post_change",
  "locator": "optional browser, screenshot, artifact, test, or observation locator"
}
```

Allowed evidence types (listed in the order used for the readiness summary, not as substitutes for one another):

```text
source_inspection
rendered_experience
assistive_technology
published_experience
user_observation
first_party_measurement
business_outcome
```

Optional `timing` values are `pre_change|post_change`. For behavior/user-dependent fixed findings, acceptance-linked proof of improvement must explicitly be `post_change`.

Rules:

- fixed requires `approval: approved`;
- `accepted_risk` implementation requires `approval: accepted_risk`;
- each source acceptance criterion must appear exactly once in `acceptance_results`;
- a `passed` acceptance result requires evidence refs that resolve to `verification_evidence` rows;
- fixed requires every applicable criterion `passed|not_applicable`, terminal current-state revalidation, and verification evidence;
- a fixed visual, interaction, accessibility, or competitive UX/UI finding requires at least one acceptance-linked `rendered_experience` or `published_experience` evidence row; behavioral or business evidence alone cannot substitute for inspection of the affected interface;
- when the source finding's `judgment_basis` is `first_party_measurement`, `user_research`, or `user_sentiment`, fixed requires new acceptance-linked `post_change` evidence at `user_observation`, `first_party_measurement`, or `business_outcome`; pre-change analytics/research remain baseline evidence and cannot prove the revision worked;
- `source_inspection` can support implementation correctness but does not by itself prove a visual, interaction, or behavioral outcome is fixed;
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

`convergence.status: converged` requires a concrete `convergence.reviewed_revision`; `unrecorded` is not evidence of convergence.

## readiness

Implementation/integration: `not_started|in_progress|ready|blocked`.

Deployment/publication: `not_performed|performed|blocked|not_applicable`.

Overall: `planned|not_ready|ready|blocked`.

`highest_evidence_level` uses the same enumeration documented above as a summary field. Its position in that list does not establish that all other evidence types are present or that a particular criterion was verified.

`readiness.overall: ready` additionally requires:

- `convergence.status: converged`;
- concrete `baseline.current_revision` and `convergence.reviewed_revision` values;
- the convergence review to match the current baseline revision rather than a stale revision;
- no open material convergence finding;
- no incomplete/unrevalidated finding or unresolved material owner decision.
