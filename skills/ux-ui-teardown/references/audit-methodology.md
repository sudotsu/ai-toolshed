# Audit methodology

## Purpose

The audit should answer one practical question: **what about this experience makes the intended user want to continue, stop, trust it, doubt it, enjoy it, tolerate it, or get lost?**

Do not flatten UI/UX into generic best practices. Context controls the meaning of friction.

## Context before heuristics

Record the task's stakes, urgency, frequency, user knowledge, and expected payoff before judging effort.

Examples:

- A guided five-step intake can be appropriate when the purchase is expensive, risky, or highly variable because the answers genuinely tailor what happens next.
- The same five-step intake can be absurd for a one-action gratuity flow where the user's goal is to finish quickly.
- A local service can benefit from visible human/local specificity; a global product can require globally coherent patterns, localization, and consistency. Neither is inherently more authentic.

When the owner supplies project-specific intent that changes a generic heuristic, record it as `owner_context` evidence rather than silently overriding the audit.

## Match method to question

Do not use one method for every UX question.

- **Rendered inspection / cognitive walkthrough**: What does the product show? Can a plausible user understand and complete the task? Where are likely breakdowns?
- **First-party behavioral analytics**: What are real users doing at scale? Where do they abandon, detour, retry, misclick, error, or behave differently by device/segment?
- **Task-based user research**: Why are people behaving that way? What do they understand, expect, trust, prefer, or misunderstand while performing the task?
- **User sentiment**: What recurring qualitative themes exist in reviews, interviews, support records, surveys, or other attributable user feedback?
- **Automated measurement**: What measurable accessibility, performance, visual-stability, or attention signal supports the observation?
- **Competitive calibration**: How does the audited experience differ from legitimately selected market alternatives on equivalent tasks/surfaces?
- **Source inspection**: What implementation fact explains or constrains the observed behavior?

A heuristic is not a substitute for observed behavior. Analytics is not a substitute for why. User comments are not a substitute for task behavior. A predictive heatmap is not proof of comprehension. Choose the method whose evidence can actually support the claim.

If the available method cannot answer a material question, lower confidence, keep the audit provisional where appropriate, or create an `investigation` finding with the evidence needed next.

## Journey method

For each primary/high-risk journey:

1. start from a realistic entry point;
2. state what the user already knows and wants;
3. follow the real path, including branches;
4. inspect material states and recovery;
5. record desktop and narrow-mobile behavior for web products;
6. verify links/destinations and obvious 404/dead-end risk;
7. identify where the product asks the user to think or act;
8. judge whether that effort produces useful feedback, progress, relevance, or payoff;
9. compare the expected path with real path/funnel/session evidence when available;
10. record strengths worth preserving.

When behavioral evidence exists, inspect at least the material journey's task success/completion signal, abandonment/drop-off, unexpected paths, repeated/retry interactions, errors, and relevant device/segment differences. Use click maps, heatmaps, session replay, funnels, or path analysis when available, but do not infer a user's motive from a cursor path alone.

## Experience judgment

Prefer concrete explanations over scores.

Useful:

> The four-choice service step asks for one small decision, immediately narrows the next question, shows progress, and prevents the user from reading irrelevant service copy later. The extra interaction is justified by the reduction in downstream complexity.

Not useful:

> Engagement score: 8.2/10.

A score can hide reasoning and create false precision.

## Autonomy and deceptive friction

Treat user autonomy as part of UX quality. Inspect material journeys for patterns such as:

- business-favorable options preselected without a user-centered reason;
- acceptance easier than refusal, cancellation, unsubscribe, or reversal;
- disguised choices or unclear consequences;
- artificial urgency/scarcity/countdowns not supported by reality;
- confirm-shaming or coercive wording;
- repeated interruption designed to wear down refusal;
- forced data collection unrelated to the requested outcome;
- confusing defaults, bait-and-switch, or obstruction that increases business metrics by making the user's task harder.

Do not call a pattern successful merely because it increases clicks, time-on-task, opt-ins, or conversion. Distinguish beneficial engagement from manipulation.

## Performance and perceived responsiveness

Performance belongs in UX when the user can feel it.

When measurements exist, use relevant loading, interaction-responsiveness, and visual-stability evidence rather than describing a site as "fast" from one subjective run. For web products, field data is stronger than a single lab run when available. Keep deep performance/root-cause engineering in the appropriate engineering skill; this audit owns the user-visible consequence and whether delay/shift breaks momentum, trust, or control.

## Global and locale-sensitive experiences

For global or mixed audiences, conditionally inspect:

- text expansion/truncation and translation clarity;
- date, number, currency, time-zone, address, and phone assumptions;
- RTL/layout resilience where relevant;
- locale-dependent imagery, terminology, legal/consent presentation, and content order;
- whether global consistency has erased necessary local relevance, or local assumptions make the product confusing elsewhere.

Do not run a localization checklist on a product whose scope makes it irrelevant.

## Evidence hierarchy

Strongest evidence depends on the claim:

- observed rendered behavior for what the interface actually did;
- user research/sentiment for what people actually report feeling or understanding;
- first-party measurement for completion, abandonment, errors, path behavior, or conversion behavior;
- measured competitor evidence for market calibration;
- source inspection for implementation facts;
- standards for requirements;
- heuristics for probable usability risk;
- visual-craft analysis for quality/coherence judgments;
- aesthetic preference only for explicitly subjective polish.

No single hierarchy applies to every question. Match evidence to claim.

## Challenge and evaluator blindness

A broad heuristic audit by one evaluator can miss issues. Before finalizing, perform a deliberate challenge pass that tries to disprove important findings and surface missed paths, strengths, or contradictory evidence.

For broad/high-stakes audits, use an independent second evaluator/reviewer when practical. Compare overlap, unique findings, false positives, and severity disagreements before convergence. Do not label a second pass by the same model/evaluator as independent review.
