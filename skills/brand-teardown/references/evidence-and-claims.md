# Brand Evidence and Claim Discipline

## Evidence classes

Use these exact classes:

1. `first_party_artifact` — current repository content, owned site, collateral, product, profile, invoice, estimate, policy, or other controlled brand artifact.
2. `controlled_observation` — reproducible reviewer journey, comprehension pass, render, comparison, or safe CTA test.
3. `live_observation` — dated public site, channel, profile, review, listing, advertisement, or user-visible behavior.
4. `stakeholder_statement` — owner, founder, operator, team, or supplied brief. It establishes intent or asserted facts, not audience perception or independent proof.
5. `customer_or_audience_evidence` — interviews, surveys, usability sessions, review text, customer language, or properly scoped behavioral research.
6. `competitor_evidence` — dated first-party competitor artifact or direct competitor-surface observation.
7. `independent_source` — authoritative registry, accreditation body, media source, research, or other independent evidence.
8. `strong_inference` — conclusion supported by multiple direct facts but not directly measured.

Keep evidence class separate from confidence, claim state, and outcome evidence.

## Evidence scope

Every evidence source declares what it can support:

- `artifact_state` — what a brand currently says or shows.
- `stakeholder_intent` — intended identity, audience, or strategy.
- `audience_perception` — what an identified audience understood, trusted, recalled, or preferred.
- `business_outcome` — measured behavior or commercial outcome.
- `competitor_state` — what a concrete competitor or alternative expressed at a date.
- `independent_verification` — credentials, licensing, accreditation, awards, ownership, or other independently verified fact.

Do not use artifact state to claim audience perception. Do not use audience opinion alone to claim revenue. Do not use stakeholder intent as independent verification.

## Finding evidence links

Each finding must link every evidence ID exactly once with:

```json
{
  "evidence_id": "EVID-001",
  "role": "supports",
  "claim": "The bounded proposition this source supports."
}
```

Allowed roles are `supports`, `contradicts`, and `context`. At least one source must support the observed condition. A contradictory source must be reconciled in the finding, not silently ignored.

## Claim inventory

Inventory material public or decision-relevant claims, including identity, category, audience, product/service scope, credentials, licensing, certifications, safety, years in business, pricing, availability, service area, guarantees, outcomes, reviews, technical capability, open-source status, privacy, and authority.

Use claim states:

- `verified` — evidence supports the exact claim at the audited date.
- `plausible_unverified` — plausible but not independently or directly verified.
- `unsupported` — expressed as fact without evidence adequate for its consequence.
- `contradicted` — current evidence conflicts with the claim.
- `outdated` — the claim or proof is stale relative to current facts.
- `not_applicable` — retained only to document why a candidate claim does not apply.

Do not treat absence from the repository as proof that a credential is false. Use `plausible_unverified` or `unsupported` according to how the public claim is framed and the available evidence.

Every claim records exact surfaces, affected audiences, evidence, risk, owner, required action, and verification method. A verified claim requires supporting evidence. A contradicted or outdated claim requires evidence of the conflict or date mismatch.

## Competitor evidence

Competitor conclusions require a canonical `competitor_samples` record with a concrete name or alternative, locator, observed date, evidence IDs, and a strategic consequence. Record category language, trust conventions, offer conventions, visual patterns, and strengths only when observed.

Use `unavailable` when public evidence could not be captured. State the exact reason and keep the competitive module partial or blocked when the missing evidence could change positioning conclusions.

## Visual and multimodal judgment

Every finding declares a judgment basis:

- `observed_behavior`
- `audience_evidence`
- `category_evidence`
- `accessibility_or_legibility`
- `claim_or_provenance_evidence`
- `aesthetic_preference`
- `not_applicable`

`aesthetic_preference` can support only low or informational severity. High-impact visual findings need a demonstrated comprehension, trust, accessibility, recognition, provenance, or conversion consequence.

Record surface samples for the actual artifact, brand, audience, channel, viewport or format, method, state, evidence, date, and limitations. For generated or supplied imagery, state provenance only when verified; otherwise record it as unknown.

## Staleness and contradiction

- Mark volatile sources such as prices, availability, staffing, service area, profiles, competitor offers, and current channel state with `volatile: true`.
- Access volatile evidence within the declared research window.
- A later source may supersede an earlier source only when the relationship is documented.
- If active evidence sources make materially conflicting factual claims and no finding or claim record captures the contradiction, the handoff is invalid.
- Archive screenshots and supplied artifacts may establish historical state; they do not prove current expression.

## Implementation and outcome evidence

Each finding records `outcome_evidence_status`: `measured`, `partial`, `blocked`, or `not_applicable`.

- A code, copy, design, or channel change can satisfy implementation acceptance criteria.
- It cannot by itself prove improved comprehension, trust, recognition, preference, conversion, or revenue.
- When the recommendation predicts audience or business effects, define the future research or measurement needed and leave outcome evidence partial or blocked until observed.
- A finding may be structurally resolved only when the audited condition is no longer present in current evidence. Outcome claims remain separately calibrated.
