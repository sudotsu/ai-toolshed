# UX/UI teardown v2 report contract

Canonical files are `findings.json` and `coverage.json`.

`scripts/bootstrap_teardown.py` creates a minimal provisional scaffold with an open limitation. Its valid JSON is a starting point, not an audit result. Fill actual evidence, journeys, assessments, findings and coverage, then validate and render the completed handoff.

## findings.json

Schema: `ux-ui-teardown-v2`.

Top-level fields:

```text
schema_version
audit
evidence_sources
competitor_set
journeys
experience_assessments
findings
```

### audit

Required fields:

```text
project_name
project_locator
audited_revision
production_locator
production_revision_status
audit_start_date
audit_end_date
review_status
project_type
audience_scope
primary_user_groups
primary_goals
owner_context
competitor_benchmark_required
competitor_benchmark_reason
```

`review_status`: `complete|provisional`.

`audience_scope`: `local|regional|national|global|mixed|internal`.

### evidence_sources

IDs: `EVID-###`.

Evidence classes:

```text
source_inspection
rendered_observation
interaction_reproduction
standard_reference
automated_measurement
user_research
user_sentiment
first_party_analytics
stakeholder_context
design_system_reference
competitor_measurement
competitor_observation
```

### competitor_set

IDs: `COMP-###`.

Each row:

```text
id
name
locator
selection_status
selection_evidence_ids
comparison_evidence_ids
relevance_reason
surfaces_compared
limitations
```

`selection_status`: `measured|owner_supplied|reference_only`.

`measured` requires at least one `competitor_measurement` evidence source.

### journeys

IDs: `JOURNEY-###`.

Each journey records:

```text
id
title
user_group
trigger
intended_outcome
criticality
steps
effort_budget
engagement_intent
expected_payoff
context_notes
viewport_ids
input_modes
state_ids
evidence_ids
status
limitations
```

`criticality`: `primary|high_risk|secondary|supporting`.

`effort_budget`: `low|moderate|high|contextual`.

### experience_assessments

IDs: `EXP-###`.

Axes:

```text
visual_craft
color_system
typography
composition
visual_coherence
audience_fit
orientation_clarity
journey_logic
friction
engagement_quality
effort_payoff
feedback_progress
relevance_personalization
trust
recovery
responsive_consistency
perceived_performance
accessibility_readability
```

Each row includes `journey_ids`, `surface_target`, `axis`, `verdict`, `confidence`, `evidence_ids`, `competitor_ids`, `observation`, `reasoning`, and `desired_direction`.

### findings

IDs: `UXUI-###`.

Kinds:

```text
gap|risk|opportunity|investigation|strength|comparative
```

Statuses:

```text
open|blocked|decision_required|retained_strength|not_applicable|resolved
```

Judgment bases:

```text
standard_requirement
observed_behavior
visual_craft
measured_comparison
user_research
user_sentiment
first_party_measurement
heuristic
design_system_convention
owner_context
aesthetic_preference
```

Aesthetic preference cannot exceed low severity. `visual_craft` alone cannot be critical. `measured_comparison` requires competitor references.

## coverage.json

Schema: `ux-ui-teardown-coverage-v2`.

Top-level fields:

```text
schema_version
review_status
access
passes
viewports
input_modes
state_coverage
material_limitations
validator
```

### access categories

```text
source_repository
production_experience
competitor_measurement
user_sentiment
design_system
assistive_technology
```

Each row has `status`, `material_to_complete`, evidence, limitations, and next step.

### passes

Exactly four:

```text
ui_craft
ux_experience
competitive_calibration
accessibility_readability
```

UI craft and UX experience are defining. Competitive calibration is high when benchmarking is required. Accessibility/readability is supporting unless the owner/product context elevates it.

### completion

A complete interactive web audit requires:

- UI craft and UX experience completed;
- measured competitive calibration when required;
- every primary/high-risk journey actually exercised;
- desktop and narrow-mobile observations linked to each primary/high-risk journey;
- pointer/touch coverage for each primary/high-risk journey;
- representative keyboard coverage somewhere meaningful in the interactive experience;
- at least one `visual_craft`, `color_system`, and `audience_fit` assessment;
- at least one experience assessment for every primary/high-risk journey;
- no open material limitation;
- no access row marked material to completion that remains partial/blocked;
- verified production revision when a public production verdict is made.

Screen-reader coverage is not a default completion requirement.
