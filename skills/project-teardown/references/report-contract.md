# Teardown Report Contract

Create the following folder. Add a specialized file only when the project warrants it; keep the numbered core files stable for the implementation handoff.

```text
project-teardown/
├── 00-executive-verdict.md
├── 01-product-and-market.md
├── 02-user-experience.md
├── 03-technical-audit.md
├── 04-security-and-reliability.md
├── 05-findings-register.md
├── 06-implementation-sequence.md
├── 07-review-coverage.md
└── evidence/
```

Keep evidence compact and safe. Store screenshots, sanitized logs, command results, benchmark notes, and other supporting artifacts in `evidence/`. Never copy secrets or sensitive user data.

## 00 — Executive verdict

Include:

- `**Review status:** complete` or `**Review status:** provisional` near the top.
- Product thesis, intended users, and maturity.
- Plain-language overall verdict.
- Current trajectory: leading, competitive, catching up, undifferentiated, outdated, or heading for a wall, with qualifications.
- Strongest qualities worth preserving.
- Critical blockers and highest-leverage opportunities.
- Best-in-class gap and realistic solo-builder ceiling.
- Decisions required from the owner.
- Review scope, environment, research date, limitations, and material assumptions.

Use `provisional` whenever a defining workflow, required platform, or evidence source remains blocked strongly enough that it could materially change the verdict. State exactly what would complete the review.

## 01 — Product and market

Include benchmarks and why they were selected, current landscape evidence, feature-value analysis, strategic classifications, contradictions, differentiation, missing capabilities, questionable or obsolete capabilities, and consequences of changing versus retaining each major direction.

## 02 — User experience

Map tested journeys and document onboarding, information architecture, interaction quality, content, visual system, responsiveness or terminal ergonomics, accessibility, feedback states, recovery, trust, and user-visible performance. Include passed checks and preserved strengths.

## 03 — Technical audit

Cover architecture, correctness, maintainability, dependencies, performance, state and data behavior, tests, build and delivery, configuration, observability, documentation, and platform-specific implementation quality. Tie conclusions to runtime evidence and source locations.

## 04 — Security and reliability

Cover threat-relevant surfaces, secret and data handling, authentication and authorization when applicable, unsafe defaults, dependency exposure, failure containment, recovery, portability, and operational risks. State whether findings are confirmed, likely, or require specialized testing. Do not imply that a teardown is a formal penetration test or compliance certification.

## 05 — Findings register

This is the authoritative inventory. Give every finding a stable ID using a category prefix and number, such as `UX-001`, `TECH-004`, `SEC-002`, or `PROD-003`.

Use one heading and one field per line. Do not combine fields. For every finding include:

- `## <ID> — <Title>`
- **Type:** defect, shortcoming, recommendation, opportunity, investigation, or strength
- **Category:** concise free-text category
- **Severity:** critical, high, medium, low, or informational
- **Confidence:** confirmed, high, medium, or low
- **Status:** open, blocked, decision-required, or accepted-risk
- **Impact:** user or business impact
- **Evidence:** evidence and reproduction
- **Expected behavior:** expected behavior, or `Not applicable — <reason>`
- **Actual behavior:** actual behavior, or `Not applicable — <reason>`
- **Root cause:** confirmed cause or explicitly labeled leading hypothesis
- **Affected components:** files, symbols, workflows, or components
- **Recommendation:** proposed response
- **If implemented:** benefits, costs, tradeoffs, and new risks
- **If unchanged:** consequences and opportunity cost
- **Dependencies:** prerequisites or `None`
- **Dependents:** downstream finding IDs or `None`
- **Conflicts:** incompatible findings or decisions, or `None`
- **Acceptance criteria:** observable completion conditions
- **Verification:** verification method
- **Estimated scope:** trivial, small, medium, large, or initiative
- **Regression risk:** low, medium, or high
- **Action:** fix, add, change, remove, investigate, decide, or retain
- **Strategic classification:** old news, contradictory, demand-misaligned, ahead of the curve, one change from ahead, heading for a wall, or `Not applicable — <reason>`

Every field is required. Use `None` or `Not applicable — <reason>` rather than omitting fields. Keep the controlled values exact so the handoff can be checked mechanically.

Severity definitions:

- **Critical:** Immediate or near-certain catastrophic harm, compromise, data loss, unusability of the core product, or a fundamental blocker to release or continued operation.
- **High:** Major user harm, core-workflow failure, serious security or reliability exposure, or a strategic issue likely to defeat the product's purpose.
- **Medium:** Meaningful degradation, recurring friction, maintainability risk, or a material missed opportunity without immediate existential impact.
- **Low:** Bounded quality, polish, consistency, or edge-case issue worth resolving.
- **Informational:** Observation, passed check, strength to preserve, or context that affects later decisions but requires no direct fix.

Do not use estimated scope as a proxy for severity.

## 06 — Implementation sequence

Create an ordered, dependency-aware plan rather than copying the severity sort. Include:

1. Decisions and investigations that unblock planning.
2. Safety, data integrity, and foundational fixes.
3. Root causes that unblock or supersede downstream findings.
4. Core workflow and high-severity improvements.
5. Product and UX changes.
6. Lower-severity refinements and cleanup.
7. Deferred initiatives and explicit accepted risks.

For each phase list finding IDs, rationale, prerequisites, parallelizable groups, conflicts, validation gates, and expected user or business outcome. Explicitly note findings superseded by another change.

End with a coverage ledger listing every open finding ID exactly once in the sequence, deferred work, or accepted risks. This prevents low-severity work from disappearing during handoff.

## 07 — Review coverage

Make review completeness explicit and auditable. Include:

- `**Review status:** complete` or `**Review status:** provisional`.
- `**Core workflows fully exercised:** yes` or `**Core workflows fully exercised:** no`.
- A surface coverage matrix with columns: surface, importance, status, evidence, limitations, and next step.
- Allowed coverage statuses: passed, failed, partial, blocked, not-tested, or not-applicable.
- Every defining workflow, supported platform, major feature, quality domain, and material research question.
- Blocked or unverified work and exactly what would unblock it.
- A narrative reconciliation table mapping every report subsection containing actionable observations to finding IDs, or explaining why its observations are passed checks, limitations, deferred, or non-actionable context.
- Counts by finding severity, status, type, and action.
- The teardown validator command and result.

The status in this file must match `00-executive-verdict.md`. If core workflows are not fully exercised, the review status must be provisional.

## Final integrity pass

Before delivery:

1. Read every narrative section again.
2. Give every actionable defect, shortcoming, recommendation, opportunity, and investigation exactly one finding ID.
3. Confirm every finding ID appears exactly once in the implementation coverage ledger.
4. Confirm no ledger ID is absent from the findings register.
5. Confirm every required finding field is present, even when its value is `None` or `Not applicable — <reason>`.
6. Confirm the coverage matrix exposes every blocked, partial, untested, and unsupported surface.
7. Confirm a blocked defining workflow produces a provisional verdict.
8. Run the bundled validator and record its successful result.
