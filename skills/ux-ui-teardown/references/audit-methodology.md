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

## State matrix

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
| timeout/offline | retained state and safe retry |

## Responsive and input matrix

Use evidence, not device folklore. Record actual viewport dimensions and input method.

Minimum web sampling for a complete public-site audit:

- one narrow mobile viewport;
- one desktop viewport;
- keyboard navigation through every primary journey;
- pointer/touch through every primary journey.

Add intermediate breakpoints when navigation, grid, form, overlay, or sticky behavior changes.

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

Examples:

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
