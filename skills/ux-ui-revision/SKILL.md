---
name: ux-ui-revision
description: Revalidate a UX/UI teardown and implement approved improvements to visual craft and real user experience while preserving strengths, respecting context and authority, and verifying the affected journeys against the exact validated handoff.
---

# UX/UI Revision

Use a validated `ux-ui-teardown-v2` handoff to improve the product people actually see and use.

The goal is not to make the artifact look resolved. The goal is to make the product materially better while preserving what already works.

## Priorities

1. Revalidate every finding against the current product.
2. Resolve context-sensitive owner decisions before changing flows whose "best" answer depends on business/user context.
3. Fix broken/nonsensical journeys and visual-craft defects.
4. Improve effort, feedback, progress, relevance, recovery, and payoff where the teardown supports it.
5. Use competitor findings as calibration, never as copying instructions.
6. Preserve distinctive/authentic strengths and any areas where the product already beats the benchmarks.
7. Verify the affected rendered experience at relevant viewports/states.
8. Keep accessibility/readability proportional but do not regress it.

Read:

- [revision-contract.md](references/revision-contract.md)
- [authority-and-external-actions.md](references/authority-and-external-actions.md)
- [verification-and-convergence.md](references/verification-and-convergence.md)
- [forward-testing.md](references/forward-testing.md) when changing the skill

## 1. Validate the exact teardown

Before planning or implementation:

- run the exact sibling/installed `ux-ui-teardown` semantic validator;
- verify the teardown digest and audited revision;
- refuse to build on an invalid or drifted handoff.

## 2. Revalidate in current state

For each finding determine:

```text
confirmed|changed|stale|already_resolved|not_applicable|blocked
```

Do not implement a stale conclusion merely because it was once valid.

## 3. Resolve owner decisions

Some UX choices cannot be determined by generic heuristics alone.

Examples:

- whether a guided intake is justified by real downstream tailoring;
- whether a local/human presentation or globally standardized presentation better fits the product;
- whether a deliberate visual quirk is identity or accidental inconsistency;
- whether a requested interaction cost is acceptable for the task's stakes.

A teardown finding with `status: decision_required` must have a linked decision record. Do not silently choose on the owner's behalf.

## 4. Plan by journey and surface

Group work so a journey is fixed coherently rather than as isolated CSS/components.

For each change record:

- exact targets;
- acceptance criteria inherited from teardown;
- preserved strengths;
- comparative principle, if any;
- what must be rerun after implementation.

## 5. Implement without cloning competitors

Competitor evidence can justify principles such as clearer hierarchy, faster orientation, better progress feedback, or stronger mobile composition.

It does **not** authorize copying competitor copy, branding, layout, imagery, or distinctive interaction sequence.

Prefer an implementation that fits this project's audience, identity, and constraints.

## 6. Verify actual experience

For every fixed material finding:

- account for every source acceptance criterion exactly once;
- rerun the affected journey/state;
- inspect rendered UI at relevant widths;
- confirm visual coherence, color, hierarchy, and responsive behavior where touched;
- verify effort/feedback/progress/payoff when the change alters interaction;
- confirm retained strengths remain intact;
- verify representative keyboard/readability behavior when the change touches interactive/accessibility-sensitive UI.

Source inspection alone does not prove a visual or experiential fix.

## 7. Converge

Run an adversarial pass looking for:

- new dead ends/404s;
- shifted or lost state;
- visual regressions;
- mobile-only problems;
- over-engineered interaction that increased work without payoff;
- genericization or loss of authenticity;
- competitor imitation;
- accessibility/readability regressions;
- owner decisions accidentally bypassed.

No material open convergence issue can coexist with `overall: ready` unless explicitly accepted as risk.

## 8. Authority

Repository editing is not merge authority. Merge is not deployment authority. Deployment is not permission to mutate CMS, profiles, analytics, purchases, or outreach.

Planning mode authorizes no product mutation.

## 9. Handoff

Canonical artifact:

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

Validate/render:

```bash
python3 <skill-directory>/scripts/validate_ux_ui_revision.py <teardown-dir> <revision-dir>
python3 <skill-directory>/scripts/render_revision.py <revision-dir>
```
