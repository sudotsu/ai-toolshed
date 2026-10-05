# UX/UI Teardown Report Contract

Create:

```text
ux-ui-teardown/
├── README.md
├── findings.json
├── coverage.json
├── findings.md
├── journey-map.md
├── coverage.md
└── evidence/
```

`findings.json` and `coverage.json` are canonical. Generated Markdown must be reproducible from them.

## findings.json

Schema version: `ux-ui-teardown-v1`.

Top-level keys:

```text
schema_version, audit, evidence_sources, journeys, findings
```

### audit

Required:

```text
project_name, project_locator, audited_revision, production_locator,
production_revision_status, audit_start_date, audit_end_date,
review_status, project_type, primary_user_groups, primary_goals
```

`review_status`: `complete|provisional`.

`production_revision_status`: `verified|unverified|not_applicable`.

### evidence_sources

Each source:

```text
id, evidence_class, title, locator, accessed_at, volatile, summary, limitations
```

IDs: `EVID-###`.

`evidence_class`:

```text
source_inspection
rendered_observation
interaction_reproduction
standard_reference
automated_measurement
user_research
first_party_analytics
stakeholder_context
design_system_reference
```

### journeys

Each journey:

```text
id, title, user_group, trigger, intended_outcome, criticality,
entry_points, steps, required_states, viewport_ids, input_modes,
evidence_ids, status, limitations
```

IDs: `JOURNEY-###`.

`criticality`: `primary|secondary|supporting|high_risk`.

`status`: `passed|failed|partial|blocked|not_tested`.

`required_states` contains state classes from the canonical state taxonomy below. It describes the states the journey materially requires; `coverage.json.state_coverage` records the concrete instances that were actually exercised.

Each primary/high-risk journey must have evidence and at least one viewport and input mode. A complete interactive-web audit has stricter per-journey coverage requirements in the completion gate below.

### findings

Each finding:

```text
id, title, kind, domains, status, severity, confidence,
verification_state, judgment_basis, standard_refs, journey_ids,
surface_targets, evidence_ids, observed_condition, desired_condition,
user_consequence, business_risk, recommendation, acceptance_criteria,
verification_methods, implementation_targets, preservation_constraints,
dependencies, conflicts, non_goals
```

IDs: `UXUI-###`.

`kind`: `gap|risk|opportunity|investigation|strength|cross_domain`.

`status`: `open|blocked|decision_required|retained_strength|not_applicable|resolved`.

`severity`: `critical|high|medium|low|informational`.

`confidence`: `confirmed|high|medium|low`.

`verification_state`: `observed|partially_observed|inferred|blocked`.

`judgment_basis`:

```text
standard_requirement
observed_behavior
user_research
first_party_measurement
heuristic
design_system_convention
aesthetic_preference
```

`domains` use one or more:

```text
ux.orientation
ux.information-architecture
ux.navigation
ux.discoverability
ux.task-flow
ux.forms
ux.feedback
ux.error-recovery
ux.cognitive-load
ux.trust
ux.conversion
ui.visual-hierarchy
ui.typography
ui.spacing
ui.color
ui.layout
ui.consistency
ui.responsive
ui.motion
ui.component-states
accessibility.semantics
accessibility.keyboard
accessibility.focus
accessibility.contrast
accessibility.target-size
accessibility.reflow
accessibility.motion
system.design-system
system.performance-perception
```

Rules:

- `aesthetic_preference` cannot exceed `low`.
- `heuristic` alone cannot justify `critical`; critical needs direct observed behavior, user research/measurement, or an applicable standard with a catastrophic task consequence.
- `standard_requirement` requires non-empty `standard_refs`.
- `strength` requires informational severity and `retained_strength`.
- every non-strength actionable finding requires a non-empty recommendation, acceptance criteria, and verification methods;
- every finding must trace to at least one evidence source and one journey;
- dependencies/conflicts must reference existing findings; dependencies must be acyclic; conflicts symmetric;
- `user_consequence` must distinguish observed outcome from reasoned risk when user research/measurement is absent.

## coverage.json

Schema version: `ux-ui-teardown-coverage-v1`.

Top-level:

```text
schema_version, review_status, access, modules, viewports,
input_modes, state_coverage, material_limitations, validator
```

### access

Include exactly:

```text
source_repository
production_experience
analytics
user_research
design_system
assistive_technology
```

Each:

```text
category, status, material_to_comprehensive, evidence_ids, limitations, next_step
```

Status: `available|partial|blocked|not_applicable`.

Material partial/blocked access forces `provisional` when that access is required for a comprehensive conclusion.

### modules

Include exactly:

```text
orientation_comprehension
information_architecture_navigation
interaction_affordance_feedback
task_flow_forms_recovery
responsive_adaptive_layout
accessibility_semantics_keyboard
visual_hierarchy_legibility
trust_conversion
design_system_consistency
performance_perception
```

Each:

```text
id, materiality, status, finding_ids, evidence_ids, limitations
```

`materiality`: `defining|high|medium|low`.

`status`: `passed|failed|partial|blocked|not_tested|not_applicable`.

### viewports

Each viewport is one concrete sampled size:

```text
id, label, width, height, class, status, journey_ids, evidence_ids, limitations
```

IDs: `VIEW-###`.

`class`: `narrow_mobile|wide_mobile|tablet|desktop|large_desktop|other`.

`status`: `observed|blocked|not_applicable`.

An observed viewport must reference evidence and every journey actually exercised at that size. Journey and viewport references must be reciprocal.

### input_modes

Each input-mode row:

```text
mode, status, journey_ids, evidence_ids, limitations
```

`mode`: `pointer_touch|keyboard|screen_reader|voice_switch|other`.

`status`: `observed|blocked|not_applicable`.

Use one row per mode. An observed row must reference evidence and every journey actually exercised with that mode.

### state_coverage

`required_states` on a journey is a taxonomy. `state_coverage` is an **instance ledger**. Never collapse materially different instances merely because they share the same state class. For example, a stale-roster checkout error and a payment-verification error are separate `STATE-###` rows even though both use `state: error`.

Each state instance:

```text
id, state, label, journey_id, step, surface_target, trigger, status,
viewport_ids, input_modes, evidence_ids, finding_ids, limitations
```

IDs: `STATE-###`.

`state`:

```text
default
focus
hover
active
disabled
loading
empty
validation
error
success
destructive
offline_timeout
```

`status`: `observed|blocked|not_applicable`.

For observed state instances:

- `label`, `step`, `surface_target`, and `trigger` identify the exact state variant;
- `viewport_ids`, `input_modes`, and `evidence_ids` are non-empty;
- every referenced viewport and input mode must itself be observed for the same journey;
- `finding_ids` may be empty, but when present must reference findings caused by or materially expressed in that state.

Multiple observed instances of the same state class are valid and expected when they represent different steps, surfaces, triggers, or outcomes.

### material_limitations

Each limitation:

```text
id, description, status, completion_requirement, affected_module_ids
```

ID: `LIMIT-###`. Status: `open|resolved`.

### validator

```text
name, status, validated_at
```

A generated artifact must not claim `complete` when validator status is not `passed`.

## Completion gate

`complete` is invalid when any of the following is true:

- an open material limitation exists;
- a defining/high module is `partial|blocked|not_tested`;
- a primary/high-risk journey is `partial|blocked|not_tested`;
- any declared `required_states` class for a primary/high-risk journey lacks at least one observed `STATE-###` instance tied to that journey;
- for an interactive web project, any primary/high-risk journey lacks an observed `narrow_mobile` viewport **for that journey**;
- for an interactive web project, any primary/high-risk journey lacks an observed `desktop` viewport **for that journey**;
- for an interactive web project, any primary/high-risk journey lacks observed `pointer_touch` **for that journey**;
- for an interactive web project, any primary/high-risk journey lacks observed `keyboard` **for that journey**;
- a journey declares a viewport/input mode that has no reciprocal coverage row;
- an observed state references a viewport/input mode that was not observed for the same journey;
- material public production state is part of the audit and production revision is unverified.

Global coverage elsewhere in the product never satisfies a material journey's completion gate. If the primary checkout journey was tested only on desktop, a separate mobile observation of the homepage does not make checkout responsive coverage complete.
