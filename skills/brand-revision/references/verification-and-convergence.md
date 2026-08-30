# Brand Verification and Convergence

Brand revision has two separate proof problems:

1. Did the approved expression change correctly without regressions?
2. Did the changed expression alter real audience perception or business outcomes?

The first can often be verified during implementation. The second usually requires audience or first-party evidence after publication. Never collapse them.

## Evidence levels

Use exactly these levels in `revision.json`:

1. `source-inspection` — current source/configuration/content inspection.
2. `rendered-experience` — current local/preview rendered page, asset, document, or journey observation.
3. `published-channel` — current public website, profile, listing, collateral, or production-channel observation.
4. `audience-observation` — bounded evidence from representative or explicitly limited audience testing.
5. `first-party-measurement` — analytics, CRM, survey, lead, conversion, or other first-party measurement with defined window and scope.
6. `business-outcome` — completed jobs, revenue, retention, qualified pipeline, preference/share data, or other business outcome tied to a defined observation method.

A lower evidence level cannot prove a higher one.

## Evidence methods

Allowed methods:

```text
source-inspection
build-unit
rendered-browser
visual-inspection
claim-verification
published-fetch
profile-observation
collateral-observation
audience-test
customer-research
first-party-analysis
business-record-analysis
owner-authorization
external-research
```

Completed evidence requires a concrete observation. Failed or blocked evidence requires a specific limitation and cannot support a completed claim.

## Brand-native verification dimensions

### Identity and architecture

Verify:

- canonical company/product/service/sub-brand names;
- ownership/endorsement relationships;
- domain and metadata identity;
- shared configuration and channel propagation;
- absence of unintended legacy collisions;
- owner-approved architecture matches the implementation.

### Positioning and message comprehension

Implementation verification can establish that the approved hierarchy is present and legible. It cannot prove a visitor understands it faster.

For audience observation, test without leading participants toward the intended answer. Useful dimensions include:

- category recognition;
- target-audience recognition;
- primary offer comprehension;
- what happens next;
- perceived reason to choose;
- proof remembered;
- identity remembered.

### Trust, proof, and claims

For every materially affected claim:

- trace the teardown claim ID;
- preserve the original claim state;
- record the revision action;
- record the resulting claim state;
- support changed verified claims with appropriate evidence;
- do not turn absence of contradiction into verification.

Proof placement must be inspected at the actual decision surface. A proof element buried elsewhere does not satisfy an acceptance criterion that requires it near the decision.

### Voice and verbal identity

Review the complete changed copy, not isolated sentences. Confirm:

- authentic operator/founder language remains recognizable where preservation requires it;
- generic corporate/AI phrasing was not introduced as collateral damage;
- unsupported authority language was removed without erasing useful personality;
- channel-specific variation remains intentional.

### Visual identity and recognition

Verify at representative sizes/formats:

- logo/wordmark treatment;
- color and type hierarchy;
- contrast and legibility;
- asset cropping/responsiveness;
- image/video/proof provenance where material;
- category distinctiveness and recognition constraints;
- absence of accidental lookalike or inconsistent variants.

Visual preference alone is not evidence of audience improvement.

### Customer journey and conversion

Exercise every affected primary action path without fabricating harmful leads. Confirm:

- CTA destination and context;
- service/product/tool handoff;
- phone/form fallback where applicable;
- content/claim consistency at the next step;
- no broken accessibility, SEO, routing, analytics, or form behavior caused by brand changes.

Use adjacent-domain verification where a brand edit touched those systems.

## Perception tests

Each `perception_test` records:

```text
id, finding_ids, dimensions, status, audience_segment, sample_source,
protocol, baseline, result, limitations, evidence_ids
```

Dimensions:

```text
comprehension
trust
differentiation
recognition
preference
action-clarity
```

Status:

```text
planned
completed
blocked
not-applicable
```

Rules:

- Completed tests require `audience-observation` evidence.
- Informal owner or agent opinion is not an audience test.
- A tiny convenience sample must be labeled as such in `limitations`.
- Do not use leading prompts that name the intended positioning before asking what the participant perceived.
- Do not aggregate unlike audiences into one conclusion without preserving segment differences.
- One observed dimension does not prove another.

## Convergence loop

After implementation:

1. Freeze the exact state under review.
2. Review the complete baseline-to-current diff.
3. Trace each changed path to approved findings or fixed `REV-###` findings.
4. Re-run affected source, render, public-channel, and journey checks.
5. Re-check every affected claim and preservation constraint.
6. Inspect current-head PR comments, reviews, CI, static analysis, and stakeholder/design-review leads when available.
7. Revalidate every lead against the exact head.
8. Record new defects as convergence findings.
9. Reopen original findings when original acceptance criteria fail.
10. Fix valid defects and repeat after every meaningful change.

Do not call convergence passed while an unresolved critical/high/medium convergence finding can materially affect truthfulness, identity coherence, comprehension, trust, recognition, accessibility/legibility, or a working conversion path.

## Common implementation-induced regressions

Look specifically for:

- owner-approved brand architecture implemented inconsistently across metadata, navigation, footer, structured data, profiles, and collateral;
- claim correction on one surface while stale stronger claims remain elsewhere;
- service proof added but pushed below the decision point on mobile;
- stronger homepage category clarity that destroys a useful low-pressure tool/resource identity;
- “professionalized” copy that erases authentic founder/operator voice;
- identity cleanup that breaks SEO titles, URLs, schema, analytics, or conversion routing;
- visual refresh that reduces contrast, mobile legibility, or recognition;
- new testimonials/proof published without permission or provenance;
- generic competitor mimicry replacing a supportable differentiator;
- audience-testing claims based only on internal stakeholder approval;
- business-outcome claims based on too-short or confounded measurement windows.

## Readiness discipline

Keep separate states for:

- implementation completeness;
- convergence;
- integration;
- deployment;
- publication;
- perception validation;
- business outcome observation;
- delivery actions.

A revision can be technically complete and publication-ready while perception and business outcomes remain unverified. That is an honest successful state, not a failure.
