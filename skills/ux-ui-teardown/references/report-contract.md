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

Each primary/high-risk journey must have evidence and at least one viewport and input mode.

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
- dependencies/conflicts must reference existing findings; dependencies must be acyclic; conflicts symmetric.
- `user_consequence` must distinguish observed outcome from reasoned risk in its wording when user research/measurement is absent.

## coverage.json

Schema version: `ux-ui-teardown-coverage-v1`.

Top-level:

```text
schema_version, review_status, access, modules, viewports,
input_modes, state_coverage, material_limitations, validator
```

### access

Include:

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

Material partial/blocked access forces `provisional`.

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

Each:

```text
id, label, width, height, class, status, journey_ids, evidence_ids, limitations
```

`class`: `narrow_mobile|wide_mobile|tablet|desktop|large_desktop|other`.

`status`: `observed|blocked|not_applicable`.

A complete interactive web audit requires at least one observed `narrow_mobile` and one observed `desktop` viewport.

### input_modes

Each:

```text
mode, status, journey_ids, evidence_ids, limitations
```

`mode`: `pointer_touch|keyboard|screen_reader|voice_switch|other`.

A complete interactive web audit requires observed `pointer_touch` and `keyboard` coverage unless genuinely not applicable.

### state_coverage

Each:

```text
state, status, journey_ids, evidence_ids, limitations
```

States may include `default`, `focus`, `hover`, `active`, `disabled`, `loading`, `empty`, `validation`, `error`, `success`, `destructive`, `offline_timeout`.

### material_limitations

Each:

```text
id, description, status, completion_requirement, affected_module_ids
```

ID: `LIMIT-###`. Status: `open|resolved`.

### validator

```text
name, status, validated_at
```

A generated artifact must not claim `complete` when the validator status is not `passed`.

## Completion gate

`complete` is invalid when any of the following is true:

- an open material limitation exists;
- defining/high module is `partial|blocked|not_tested`;
- a primary/high-risk journey is `partial|blocked|not_tested`;
- required mobile/desktop coverage is missing for an interactive web project;
- pointer/keyboard coverage is missing for an interactive web project;
- material public production state is part of the audit and production revision is unverified.
