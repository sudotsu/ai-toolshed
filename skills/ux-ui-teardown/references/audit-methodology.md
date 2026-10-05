# UX/UI Audit Methodology

## Audit model

Use a layered model rather than a screenshot checklist:

```text
USER GOAL
  -> ENTRY / ORIENTATION
  -> INFORMATION SCENT
  -> DECISION
  -> INTERACTION
  -> SYSTEM FEEDBACK
  -> SUCCESS OR RECOVERY
```

A defect matters when it impairs one or more of those transitions, violates an applicable requirement, or creates a material risk that can be traced to evidence.

## Journey selection

Select journeys using project evidence. Prioritize:

- the product's primary value exchange;
- revenue or lead-generation flows;
- account creation/authentication when required for value;
- destructive or high-risk workflows;
- first-use/onboarding;
- common repeat tasks;
- support/recovery paths;
- mobile-critical flows.

Do not fabricate edge journeys only to increase finding count.

## State model

For each applicable interactive pattern, inspect:

| State | What to verify |
| --- | --- |
| default | discoverability, hierarchy, labels |
| focus | visible focus, order, no obscuring |
| hover | supplemental only; no hover-only requirement |
| active | feedback and accidental activation risk |
| disabled | reason/context where needed |
| loading | progress, duplicate-action protection |
| empty | next action and explanation |
| validation | field association, actionable correction |
| error | what happened, what to do next, preserved work |
| success | confirmation and next state |
| destructive | consequence, confirmation, undo/recovery |
| offline_timeout | retained state and safe retry |

The state name is only a class. Record concrete state **instances** separately when the trigger, journey step, surface, consequence, or recovery path differs. Do not use one generic `error` observation to stand in for every error state in the product. Do not use one loading observation to prove every loading transition.

A journey's `required_states` lists the classes material to that journey. The state coverage ledger proves which exact instances were exercised and under which viewport/input conditions.

## Responsive and input matrix

Use evidence, not device folklore. Record actual viewport dimensions and input method.

Minimum web sampling for every primary/high-risk journey in a complete interactive-web audit:

- one narrow mobile viewport linked to that journey;
- one desktop viewport linked to that journey;
- keyboard navigation through the journey;
- pointer/touch through the journey.

Add intermediate breakpoints when navigation, grid, form, overlay, sticky behavior, content density, or task sequencing changes.

Coverage is journey-specific. A mobile homepage observation cannot satisfy the mobile requirement for a checkout flow that was tested only on desktop. A keyboard run of global navigation cannot satisfy keyboard coverage for a form that was only exercised with a pointer.

## Severity

- `critical` — blocks a primary journey for a substantial user group with no viable workaround, creates a severe destructive-action trap, or produces an accessibility failure with equivalent catastrophic task denial.
- `high` — materially impairs a primary journey, creates repeated error/recovery cost, or excludes users from an important function.
- `medium` — meaningful friction, ambiguity, inconsistency, or accessibility/usability defect with a practical workaround.
- `low` — bounded friction or polish issue with limited task impact.
- `informational` — retained strength, observation, or non-actionable context.

Severity is impact, not certainty.

## Confidence

- `confirmed` — directly reproduced or measured with strong matching evidence.
- `high` — multiple consistent observations or strong standard/source evidence.
- `medium` — credible but partially observed or context-dependent.
- `low` — plausible lead requiring more evidence.

## Verification state

- `observed`
- `partially_observed`
- `inferred`
- `blocked`

Keep it independent from confidence.

## Design taste guardrail

Aesthetic preference may identify polish opportunities, but cannot exceed `low` severity unless a separate evidence basis demonstrates a stronger user/system consequence.

Bad:

> The hero feels dated.

Better:

> At 390px, three equally weighted actions appear before the service explanation; the primary quote path is not visually distinguishable. This is observed hierarchy/decision friction, not a claim that the aesthetic is "dated."

## Automated tooling

Automated tools may support:

- contrast checks;
- accessible-name inspection;
- DOM semantics;
- Lighthouse/Web Vitals snapshots;
- overflow/viewport checks;
- regression screenshots;
- lint/static rules.

They do not independently prove:

- a journey is understandable;
- a keyboard flow is efficient;
- screen-reader announcements are coherent;
- users trust the page;
- the correct task model was chosen;
- a conversion problem exists.

Always connect tool output to a concrete experience consequence.
