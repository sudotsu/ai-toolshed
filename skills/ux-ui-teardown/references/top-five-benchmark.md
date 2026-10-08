# UX/UI pair — top-five current-performer benchmark

Benchmark date: **2026-10-07**.

This document applies the repository quality bar to `ux-ui-teardown` and `ux-ui-revision`.

## Domain being benchmarked

The relevant domain is **UX/UI evaluation and evidence-to-improvement tooling for digital product interfaces**: systems that help a team identify usability/interface problems, ground judgments in evidence, prioritize improvements, and verify whether the experience got better.

This is intentionally narrower than "design software" and broader than "AI screenshot critic." The Toolshed pair audits rendered product experience, can consume behavioral/user evidence, calibrates against competitors, produces a structured implementation handoff, and verifies revisions. A benchmark that considered only screenshot graders would ignore much of the actual job; a benchmark against general design generators would compare a different job.

The five below are **not an arbitrary convenience set and are not ranked 1–5**. They were selected from current attributable evidence using multiple signals relevant to this domain: research rigor or observed-user evidence, independent/verified market evidence, adoption/usage scale, breadth of applicable UX evaluation capability, and category leadership. No single metric determined inclusion.

## The five current reference leaders

### 1. Baymard Institute / UX-Ray

Why it belongs in the set:

- Baymard documents 200,000+ hours of UX research, 4,400+ moderated participant/site sessions, 54 rounds of manual benchmarking, 344 top-grossing sites, 810 UX guidelines in its methodology dataset, 175,000+ implementation examples, and 275,000+ weighted UX performance scores.
- UX-Ray is a direct automated UX-analysis peer: Baymard reports 95% accuracy versus its human UX experts and documents the comparison method across 79 websites.
- It combines heuristic evaluation, evidence traceability, competitor scanning, prioritization, and research-backed recommendations.

Current evidence:

- https://baymard.com/research/methodology
- https://baymard.com/blog/ux-ray-progress-2026
- https://baymard.com/research-articles/ai-heuristic-evaluations
- https://baymard.com/product/ux-ray

### 2. UserTesting

Why it belongs in the set:

- UserTesting is a Leader in G2's Fall 2026 Enterprise Grid for User Research.
- G2's leader placement uses verified customer reviews plus market presence rather than vendor self-ranking.
- It is a major reference for the part an automated audit cannot manufacture: direct human observation, qualitative evidence, task comprehension, trust, preference, and post-change validation.

Current evidence:

- https://www.usertesting.com/blog/g2-user-research-leaders-fall-2026
- https://www.usertesting.com/resources/reports/g2-enterprise-report-fall-2026
- https://www.g2.com/categories/user-research/themes/usability-testing

### 3. Contentsquare / Hotjar

Why it belongs in the set:

- Contentsquare's current G2 seller profile reports 2,084 reviews, a 4.4/5 average, Grid Leader status, and #1 placement in three categories.
- The product family covers customer-journey analytics, digital analytics, heatmaps, session replay, feedback, and user research—the behavior-evidence side of serious UX diagnosis.
- This makes it a strong bar for finding friction from actual usage rather than inferring user behavior from source code or screenshots.

Current evidence:

- https://www.g2.com/sellers/contentsquare
- https://www.g2.com/products/hotjar-by-contentsquare/reviews

### 4. Maze

Why it belongs in the set:

- Maze's current G2 profile reports a 4.5/5 rating from 111 reviews and describes an all-in-one research workflow spanning recruiting, testing, and analysis.
- Maze reports 60,000 brands, 325,000 live studies, and 6.2 million user responses.
- It is a strong reference for rapid prototype/live-product testing, task/path evidence, quantitative-plus-qualitative research, and design-decision validation.

Current evidence:

- https://www.g2.com/products/maze-maze/reviews
- https://maze.co/customers/

### 5. Dscout

Why it belongs in the set:

- Dscout's current G2 profile reports 4.5/5 across 191 reviews and broad multi-method user-research capability.
- G2 identifies usability testing, interviews, field/diary studies, surveys, intercepts, card sorting, and participant recruitment among its capabilities.
- Dscout reports access to more than 3 million additional participants through partner panels and publishes substantial enterprise customer evidence.
- It is a strong bar for in-context qualitative evidence and for preventing a UX audit from substituting model inference for real human behavior.

Current evidence:

- https://www.g2.com/products/dscout/reviews
- https://www.dscout.com/platform/find-participants
- https://www.dscout.com/customers

## What the Toolshed pair must match or beat

For the parts of the job that apply to a portable agent skill, `ux-ui-teardown` + `ux-ui-revision` should not be considered flagship-finished unless they cover these capabilities at a top-tier level:

1. **Evidence provenance and claim discipline.** A finding must say what evidence supports it, distinguish observation from inference, and refuse to turn source inspection into a rendered/behavioral claim.
2. **Real journey and task reasoning.** Evaluate end-to-end user work, not isolated screenshots or generic heuristic counts.
3. **UI craft judgment.** Evaluate composition, hierarchy, spacing, typography, color systems, imagery, responsive recomposition, interaction polish, perceived performance, coherence, and accidental/template-like design.
4. **Context-sensitive UX judgment.** Do not mechanically optimize for fewer clicks, more engagement, more conversion, or a universal pattern. Judge effort by whether it produces feedback, progress, relevance, or payoff for this product and audience.
5. **Behavioral and user evidence escalation.** Consume analytics, session/behavior evidence, and user research when available; require new post-change evidence when improvement claims depend on behavior or user response.
6. **Measured competitive calibration.** Select competitors from current attributable evidence, observe equivalent surfaces, compare without cloning, and preserve areas where the audited product is already stronger.
7. **Accessibility and inclusive usability.** Catch material readability, contrast, input, focus, semantics, reflow, target, motion, and assistive-technology issues in proportion to actual risk.
8. **Actionability.** Findings need prioritized recommendations, acceptance criteria, verification methods, affected targets, dependencies, non-goals, and preservation constraints—not vague critique.
9. **Strength preservation and tradeoffs.** Record what is already good and prevent revision from normalizing distinctive or effective qualities away.
10. **Implementation coupling.** Carry validated findings into an implementation ledger without losing provenance, criteria, owner decisions, or authority boundaries.
11. **Verification and convergence.** A visual/behavioral finding is not fixed because code changed. Verify the affected experience at the evidence level required by the original claim, then perform convergence review before readiness.
12. **Safe mutation boundaries.** Separate planning, editing, publishing, deploying, outreach, purchases, and merging; do not infer authority from access.
13. **Reproducibility and malformed-input safety.** Deterministic artifacts, explicit schemas, bounded validation failure, and regression coverage are part of the product, not optional engineering hygiene.

## Where the market leaders remain stronger

The Toolshed pair does **not** natively reproduce several capabilities of these platforms:

- participant recruitment/panels;
- hosted moderated or unmoderated research infrastructure;
- session-replay and heatmap data collection;
- product analytics/event collection;
- enterprise research repositories and dashboards;
- Baymard's proprietary 200,000+ hour research corpus and manually scored benchmark database.

Those are not silently ignored. For this project's actual use case, reproducing those SaaS/data-collection infrastructures inside a portable agent skill is **not necessary** and would add enormous complexity without improving the skill's core job. The requirement instead is:

- use those evidence sources when they are available through connected tools, files, analytics, or supplied research;
- never fabricate the evidence they provide;
- keep claims provisional when the needed evidence is unavailable;
- recommend/escalate to real user or behavioral research when the question cannot be answered reliably from direct inspection.

This is the explicit use-case exception permitted by the repository quality bar.

## Where the Toolshed pair should be stronger or meaningfully differentiated

The pair is designed to exceed typical standalone audit/research products on several applicable workflow dimensions:

- one evidence chain from teardown finding to approved implementation to post-change verification;
- deterministic, validator-backed handoff artifacts rather than an unstructured report;
- exact acceptance-criterion accounting before a finding can be closed;
- explicit owner/context decisions and approved-tradeoff handling;
- explicit preservation of strengths, not only defect discovery;
- typed mutation authority and separation of edit/deploy/publish/merge permissions;
- code/repository awareness when source is available while still refusing to infer rendered outcomes from source;
- context-sensitive UX reasoning that can reach opposite conclusions for superficially similar patterns;
- measured competitor selection plus actual competitor-surface observation;
- regression/convergence gates that challenge whether the revision introduced new UX defects.

These are design targets. They are not, by themselves, proof of market superiority.

## Evidence required before claiming top-five parity or superiority

Green CI, detailed contracts, and two successful forward tests are not enough to claim that this pair is empirically better than the five references above.

A parity/superiority claim requires a diversified blind or independently checked benchmark that measures, at minimum:

- material-finding precision and false-positive rate;
- material-finding recall / missed-opportunity rate;
- severity/prioritization agreement with qualified independent review or trusted reference findings;
- correct use of behavioral/user evidence versus unsupported inference;
- recommendation quality and harmful-intervention rate;
- strength-preservation rate;
- acceptance/verification correctness after revision;
- regression rate after implementation;
- context sensitivity across materially different product archetypes;
- competitor-calibration quality and non-copying behavior.

The current V2 forward tests on OmahaTreeCare and TipJar establish **workflow viability and context sensitivity**, not top-five empirical parity. Until the broader benchmark exists, the accurate claim is:

> The UX/UI pair is intentionally designed and release-gated against five evidence-selected current leaders on the capabilities that apply to a portable agent workflow; market-leading judgment quality remains an empirical benchmark question, not something inferred from CI or architecture.
