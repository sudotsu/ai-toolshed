# Evidence and Standards Hierarchy

Use the strongest applicable source, and label what kind of authority it has.

## Tier 1 — normative requirements

Use for requirements the product is expected to satisfy.

Primary web baseline:

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) — W3C Recommendation.
- HTML/platform specifications when semantics or native behavior are material.

Do not claim legal compliance/non-compliance unless the task explicitly includes the relevant jurisdiction and legal standard. A WCAG failure is an accessibility finding, not automatically a legal conclusion.

## Tier 2 — authoritative implementation guidance

- [WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/) for ARIA patterns, accessible names, keyboard interaction, focus, and widget semantics.

APG is implementation guidance. Prefer native HTML when it provides the required semantics/behavior. "No ARIA is better than bad ARIA" is an operating principle of APG.

## Tier 3 — empirical and established usability heuristics

- [Nielsen Norman Group: 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).

NN/g explicitly describes these as broad rules of thumb rather than specific usability requirements. Use `judgment_basis: heuristic`, not `standard_requirement`.

Useful heuristic families:

- visibility of system status;
- match between system and real world;
- user control/freedom;
- consistency/standards;
- error prevention;
- recognition over recall;
- flexibility/efficiency;
- minimalist relevance;
- error recognition/recovery;
- help/documentation.

## Tier 4 — mature design-system and platform conventions

Use contextually:

- [GOV.UK Design System](https://design-system.service.gov.uk/) for service patterns, focus treatment, forms, error recovery, and task-oriented content.
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) for Apple-platform conventions.
- Material Design and other platform systems when the product actually targets that environment.
- The project's own established design system.

A convention can be strong evidence of inconsistency or learnability cost. It is not automatically universal.

## Tier 5 — aesthetic preference

Taste can be recorded, but must be labeled `aesthetic_preference`.

It cannot independently justify:

- critical/high/medium severity;
- accessibility claims;
- user-confusion claims;
- conversion claims;
- redesigning a coherent existing visual system.

## Evidence classes

Use:

- `source_inspection`
- `rendered_observation`
- `interaction_reproduction`
- `standard_reference`
- `automated_measurement`
- `user_research`
- `first_party_analytics`
- `stakeholder_context`
- `design_system_reference`

When evidence is volatile, record access date and environment.

## Claim discipline

Distinguish:

- **observed**: directly reproduced or measured;
- **supported risk**: consequence follows from a standard/heuristic and observed condition;
- **hypothesis**: plausible but needs user or first-party evidence;
- **preference**: subjective aesthetic judgment.

Never rewrite a hypothesis as an observed user outcome.
