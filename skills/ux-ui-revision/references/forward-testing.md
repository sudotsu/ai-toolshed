# Forward testing

Forward-test revision against the same contrasting project types used for teardown.

The test is not merely "does revision.json validate?" It must show that revision:

- refuses invalid upstream teardown;
- preserves owner/context-sensitive decisions instead of silently choosing;
- accounts for every acceptance criterion;
- fixes visual/experience problems without flattening authentic strengths;
- uses competitor evidence as calibration rather than cloning;
- verifies rendered experience after code changes;
- when a source finding depends on behavioral or user evidence, preserves pre-change analytics/user-study evidence as the baseline and obtains new post-change behavioral or user evidence for the affected finding or criterion before claiming improvement; prior evidence cannot serve as proof that the revision caused the intended change;
- does not over-apply guided engagement to low-friction tasks;
- does not optimize a business metric by introducing deceptive/coercive friction;
- checks interaction/motion/perceived-performance consequences when affected;
- keeps accessibility proportional and non-regressed;
- converges without unresolved material findings.

Every generic failure found in a forward test becomes a regression test.

## Smoke tests are not implementation-quality proof

A few successful real-project revisions and green validators prove workflow viability, not that the revision skill consistently chooses the best intervention or preserves the right things.

Do not claim market-leading revision quality from CI, self-review, or a small hand-selected set of projects.

## Peer comparison before flagship release

Before treating the revision skill as flagship-finished, review and apply [`top-five-benchmark.md`](top-five-benchmark.md). The same provisional peer cohort governs both halves, but teardown and revision outcomes must be evaluated separately. A named cohort is not a top-five result.

Refresh the peer cohort from current attributable evidence when the domain changes or the comparison becomes stale. Do not silently substitute model memory or a convenient comparison set.

## Flagship implementation benchmark

For a strong expert-equivalent or top-market claim, evaluate the revision skill across a diversified benchmark of validated teardowns with independently supported desired outcomes.

Include different product archetypes and change types: visual craft, interaction flow, responsive behavior, accessibility-sensitive UI, low-friction transaction, high-consideration journey, global/localized presentation, and at least some findings grounded in first-party behavior or user research.

Track at minimum:

- **acceptance correctness** — every source criterion is actually satisfied, not merely marked passed;
- **regression rate** — new journey/state/responsive/accessibility defects introduced by the change;
- **strength-preservation rate** — important existing qualities remain intact unless an explicit approved tradeoff exists;
- **harmful-intervention rate** — changes that make the user experience worse, add unjustified effort, or optimize the business at the user's expense;
- **verification sufficiency** — evidence strength matches the claim being closed;
- **behavioral-outcome agreement** — when analytics/user-study evidence exists, whether new post-change evidence shows the revised outcome actually moved the relevant behavior/understanding in the intended direction relative to the pre-change baseline;
- **competitive distinctiveness** — whether useful benchmark principles are adopted without cloning or genericizing the product;
- **context sensitivity** — whether revision avoids applying the same interaction recipe to materially different tasks;
- **convergence quality** — whether independent review of the revised product still finds unresolved material defects.

Keep failed interventions and regressions in the benchmark corpus. A second run by the same evaluator/model is useful challenge testing, but it is not independent validation.

A strong market-quality claim should be based on this empirical benchmark, not on how detailed the workflow contract is.
