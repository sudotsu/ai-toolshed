# Forward testing

Do not call this skill ready because fixtures validate.

Use at least two real projects with materially different UX:

1. a high-consideration public/service journey where guided questions can genuinely tailor the result;
2. a low-friction transactional/app journey where unnecessary steps should be penalized.

For each project, evaluate whether the skill:

- finds visual-craft problems, including color and "off-looking" inconsistencies;
- distinguishes justified participation from pointless friction;
- catches broken/dead-ended/nonsensical journeys;
- selects benchmark competitors from current evidence rather than memory;
- compares without copying;
- adapts to local/global audience context without preferring one;
- records real strengths;
- stays provisional when required evidence cannot be exercised;
- uses analytics/user research when the conclusion materially depends on behavior or reported experience and that evidence is available;
- recognizes manipulative/deceptive engagement as a UX defect rather than treating more engagement as automatically good;
- inspects motion, interaction feedback, perceived performance, and locale-sensitive behavior when material;
- produces a handoff revision can consume without reconstructing the audit.

Regression-test every generic contract defect exposed by a real run.

When changing completion logic, malformed input must return bounded validation errors rather than tracebacks.

## Smoke tests are not an accuracy benchmark

The two contrasting real-project runs above are a minimum forward smoke test. They show that the workflow can make materially different context-sensitive judgments. They do **not** prove that the skill finds most important UX problems, avoids false positives, ranks severity correctly, or matches/exceeds expert market tools.

Do not claim top-tier, top-five, expert-equivalent, or best-in-market quality from green CI, schema validation, self-review, or a small hand-selected set of projects.

## Required top-five reference benchmark

Before treating the skill as flagship-finished, review and apply [`../../../docs/ux-ui-top-five-benchmark.md`](../../../docs/ux-ui-top-five-benchmark.md). That artifact records the current evidence-selected five, the capabilities this portable agent workflow must match or beat, the explicit use-case exception for SaaS/data-collection infrastructure, and the evidence boundary for any market-parity or superiority claim.

If the benchmark becomes stale or the domain changes materially, refresh the five from current attributable multi-signal evidence before relying on it. Do not silently substitute model memory or a convenient competitor set.

## Market-quality / flagship benchmark

Before making a strong market-parity or superiority claim, run a diversified benchmark whose reference findings are established independently of the skill under test.

The benchmark should include multiple product archetypes and journey types, for example:

- local/high-consideration service;
- ecommerce/checkout;
- SaaS onboarding/core task;
- low-friction transaction;
- content/information/navigation-heavy experience;
- mobile-dominant flow;
- globally/localized experience when relevant;
- at least one product with useful analytics or user-research evidence.

Avoid cherry-picked cases the skill was designed around. Keep misses and failed cases in the benchmark corpus.

Reference evidence can come from expert audits, high-quality published research/benchmarks, real user-task studies, first-party behavioral data, or another genuinely independent evaluator. A second run by the same model/evaluator is not independent ground truth.

Predeclare and record, at minimum:

- **precision / false-positive rate** — how many material findings are actually supported;
- **recall / false-negative rate** — which important reference issues the skill missed;
- **severity agreement** — whether impact is materially over- or under-ranked;
- **unsupported-claim rate** — conclusions presented more strongly than their evidence supports;
- **harmful-recommendation rate** — recommendations that would make the real experience worse or optimize the business at the user's expense;
- **strength-preservation rate** — whether the audit identifies and protects important existing strengths;
- **contextual-judgment quality** — whether the same pattern is judged differently when task stakes/payoff genuinely differ;
- **competitive-calibration quality** — whether selected competitors are defensible and comparisons use equivalent surfaces without copying;
- **evidence-escalation quality** — whether the skill knows when heuristics/rendered inspection are insufficient and asks for or uses behavioral/user evidence instead of inventing certainty.

Track disagreements, not just a single aggregate score. Inspect failure modes by archetype and evidence class.

A market-quality claim should be based on this empirical benchmark, not on the sophistication of the prompt or the amount of validation code.