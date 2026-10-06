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
9. record strengths worth preserving.

## Experience judgment

Prefer concrete explanations over scores.

Useful:

> The four-choice service step asks for one small decision, immediately narrows the next question, shows progress, and prevents the user from reading irrelevant service copy later. The extra interaction is justified by the reduction in downstream complexity.

Not useful:

> Engagement score: 8.2/10.

A score can hide reasoning and create false precision.

## Evidence hierarchy

Strongest evidence depends on the claim:

- observed rendered behavior for what the interface actually did;
- user research/sentiment for what people actually report feeling;
- first-party measurement for completion, abandonment, errors, or conversion behavior;
- measured competitor evidence for market calibration;
- source inspection for implementation facts;
- standards for requirements;
- heuristics for probable usability risk;
- visual-craft analysis for quality/coherence judgments;
- aesthetic preference only for explicitly subjective polish.

No single hierarchy applies to every question. Match evidence to claim.
