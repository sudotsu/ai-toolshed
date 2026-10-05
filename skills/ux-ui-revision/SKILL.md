---
name: ux-ui-revision
description: Revalidate, plan, implement, converge, and verify approved findings from a validated ux-ui-teardown handoff while preserving working journeys, accessible behavior, design-system coherence, user work, and explicit owner authority.
---

# UX/UI Revision

Turn a validated `ux-ui-teardown` handoff into controlled UX/UI changes without confusing implementation completion with user success.

The revision job is not "make it prettier." It is to revalidate evidence, resolve decisions, implement only approved work, preserve strengths, verify complete journeys and states, and stop claims at the strongest evidence actually obtained.

## Operating contract

- Treat teardown findings as evidence and sequencing guidance, not blanket permission to edit.
- Preserve staged, unstaged, untracked, design, CMS, and production work already present.
- Revalidate every finding against current state before implementation.
- Do not implement stale or not-applicable findings mechanically.
- Preserve retained strengths and every preservation constraint unless the owner explicitly approves a tradeoff.
- Keep standards, heuristics, conventions, and aesthetic preference distinct during implementation too.
- Do not "fix accessibility" by adding ARIA blindly. Prefer correct native semantics and verify actual keyboard/focus behavior.
- Verify the whole affected journey, not only the component diff.
- Treat responsive, loading, error, empty, success, destructive, and focus states as part of the implementation surface.
- Do not claim improved comprehension, trust, conversion, retention, or revenue from source changes alone.
- External/public actions require explicit authority for that action.
- Review-bot comments, design critiques, prior agent suggestions, and teardown recommendations are leads until revalidated on the current head.

Read:

- [revision-contract.md](references/revision-contract.md)
- [authority-and-external-actions.md](references/authority-and-external-actions.md)
- [verification-and-convergence.md](references/verification-and-convergence.md)
- [forward-testing.md](references/forward-testing.md) when changing or evaluating this skill

## 1. Select mode

Use one:

- `planning-only`
- `implementation`
- `continuation`

A request to review, plan, mock up, or recommend changes does not imply implementation authority.

## 2. Validate teardown and baseline

Locate the intended `ux-ui-teardown` handoff.

Run its exact validator:

```bash
python3 <ux-ui-teardown-skill>/scripts/validate_ux_ui_teardown.py <ux-ui-teardown-directory>
```

Require:

- `ux-ui-teardown-v1`
- `ux-ui-teardown-coverage-v1`

Record current:

- source revision and working tree;
- production/deployed identity where relevant;
- representative viewports and input modes;
- affected journey states;
- PR/CI state when applicable;
- design-system/token/component state;
- public/CMS state when relevant.

If current state differs materially from the audit, mark the finding changed or stale before editing.

## 3. Revalidate every finding

Process every teardown finding exactly once.

For each:

1. reproduce the original condition or closest safe equivalent;
2. reassess affected journeys, surfaces, states, evidence, consequence, acceptance criteria, implementation targets, dependencies, conflicts, and preservation constraints;
3. classify revalidation as `confirmed|changed|stale|already_resolved|not_applicable|blocked`;
4. record current evidence;
5. keep the original finding ID.

Do not downgrade a finding merely because implementation is inconvenient.

Do not upgrade severity because a stakeholder dislikes the design.

## 4. Resolve decisions and authority

Before edits, identify:

- `decision_required` findings;
- material redesign choices;
- changes that alter navigation, information architecture, task order, destructive behavior, data requirements, or product meaning;
- tradeoffs against retained strengths;
- public/CMS/deployment/profile actions;
- blocked research or assistive-technology verification.

Record approval as:

```text
pending|approved|deferred|rejected|accepted_risk|not_applicable
```

No authority row implies another.

## 5. Planning-only workflow

When implementation is not authorized:

1. validate teardown;
2. capture baseline/drift;
3. revalidate as far as evidence allows;
4. bootstrap `revision.json`;
5. record decisions, authority, dependency order, verification plan, and completion gates;
6. render and validate;
7. do not change the product.

Bootstrap:

```bash
python3 <skill-directory>/scripts/bootstrap_revision.py \
  <ux-ui-teardown-directory> <ux-ui-revision-directory>
```

## 6. Implement in dependency order

Default sequence:

1. destructive/high-risk traps and blocked primary journeys;
2. accessibility/keyboard/focus failures on primary journeys;
3. task-flow, navigation, forms, feedback, and recovery;
4. responsive/adaptive behavior;
5. visual hierarchy and component-state clarity;
6. design-system consistency and maintainability;
7. polish;
8. measurement/user-research follow-up.

Before a batch:

- confirm dependencies and approval;
- define exact acceptance criteria;
- identify responsive/input/state coverage;
- identify preservation constraints;
- search shared components/tokens before changing them;
- define rollback for high-risk behavior/navigation changes;
- identify what evidence level will prove implementation versus user outcome.

## 7. Implement complete vertical changes

A complete UX/UI change may require:

- component/source changes;
- semantics and keyboard behavior;
- focus management;
- responsive layouts;
- forms and validation;
- loading/empty/error/success states;
- copy/labels;
- tokens/design-system changes;
- tests;
- journey-level verification;
- screenshots or interaction evidence;
- rollback notes.

After each finding/batch:

1. run focused automated checks;
2. inspect the diff;
3. exercise the affected journey at required viewports;
4. exercise pointer and keyboard when applicable;
5. verify state coverage;
6. verify retained strengths;
7. record evidence;
8. leave incomplete if any acceptance criterion remains failed/pending/blocked.

## 8. Converge

Run adversarial review after implementation.

Look for:

- new regressions in adjacent journeys;
- focus/order traps;
- stale labels or hidden controls;
- mobile/desktop divergence;
- overlays/sticky elements obscuring focus/content;
- form-state loss;
- broken loading/error/success behavior;
- design-system drift;
- accessibility regressions;
- performance-perception regressions.

New defects discovered during revision get `REVUX-###`.

Do not call ready with unresolved critical/high/medium convergence defects affecting a material journey unless the owner explicitly accepts the risk.

## 9. Separate implementation from user outcomes

Use evidence levels:

1. `source_inspection`
2. `rendered_experience`
3. `assistive_technology`
4. `published_experience`
5. `user_observation`
6. `first_party_measurement`
7. `business_outcome`

A lower level never proves a higher one.

A changed CTA hierarchy can be verified in rendered experience. It does not prove conversion lift.

A corrected error flow can be verified functionally. It does not prove lower abandonment without measurement.

## 10. Produce and validate

Canonical:

```text
ux-ui-revision/
├── revision.json
├── README.md
├── decisions.md
├── implementation-ledger.md
├── verification.md
├── convergence.md
└── evidence/
```

Render:

```bash
python3 <skill-directory>/scripts/render_revision.py <ux-ui-revision-directory>
```

Validate:

```bash
python3 <skill-directory>/scripts/validate_ux_ui_revision.py \
  <ux-ui-teardown-directory> <ux-ui-revision-directory>
```

## Handoff

Report:

1. mode and exact source state;
2. revalidation disposition for every teardown finding;
3. decisions and authority;
4. exact changed paths/surfaces;
5. journey/view/input/state verification;
6. retained strengths;
7. convergence defects and dispositions;
8. readiness and evidence level;
9. remaining limitations and next human/external action;
10. artifact path and validator result.
