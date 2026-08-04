# SEO Verification and Convergence

## Contents

1. SEO-native implementation rules
2. Evidence levels
3. URL and production verification
4. Experiments and delayed outcomes
5. Adversarial convergence
6. Readiness and finalization

## 1. SEO-native implementation rules

### Technical discovery and indexation

Conditionally verify HTTP status, redirects, canonicals, robots, `noindex`, snippet and removal controls, sitemaps, parameters, facets, pagination, dynamic URLs, JavaScript rendering, source/render parity, internal discovery, mobile parity, structured data, hreflang, media discovery, production/source alignment, and CDN/WAF/authentication crawler behavior.

Technical eligibility is not observed indexing. Indexing is not ranking. Ranking or citation is not traffic. Traffic is not a qualified conversion.

### Content, claims, and authority

Every content change must serve an identified user/search job and preserve claim accuracy, current evidence, business identity, owner-approved service and credential boundaries, review responsibility, regulated-content limits, distinct value, conversion paths, and existing strengths.

Never create keyword permutations, doorway pages, synthetic expertise, fake reviews, unsupported local facts, or programmatic pages without distinct value and reliable data.

Content consolidation or removal must cover redirects, internal links, canonicals, sitemaps, analytics, publication authority, and rollback.

### Local and external entities

Keep local organic, local-pack visibility, Business Profile, citations, listings, reviews, and on-site entity consistency distinct. Verify canonical name, phone, address or service area, hours, categories, services, domain, and owner facts before any authorized change.

### AI-mediated discovery

Use fresh primary documentation and current observations. Prefer transferable fundamentals: eligibility, clear entities, accurate claims, source attribution, passage usefulness, original evidence, consistent facts, and observable referrals or citations.

Do not automatically add `llms.txt`, special AI schema, arbitrary chunking, citation bait, synthetic mentions, or “AI-optimized” prose. Treat unsupported tactics as experiments only.

### Measurement and conversions

Tie work to the teardown's qualified-conversion definition. Analytics, consent, privacy, call tracking, lead storage, attribution, and conversion definitions must match actual behavior and approved policy.

## 2. Evidence levels

Use exactly:

| Level | Proves |
|---|---|
| `source-inspection` | Current source/configuration/content state |
| `build-unit` | Build, static, unit, or isolated behavior |
| `local-render` | Local browser, render, crawl, or journey behavior |
| `preview-staging` | Deployed preview or staging behavior |
| `deployed-production` | Current production response or user behavior |
| `search-platform-observation` | Search-platform, SERP, index, citation, or referral observation |
| `business-outcome` | Qualified lead, activation, sale, revenue, or owner-defined business result |

Evidence status is `completed`, `failed`, `blocked`, or `not-applicable`. Failed or blocked evidence cannot support an observed state.

Never use source inspection to claim deployment, indexing, visibility, AI citation, traffic, conversion, or revenue. Never use search-platform observation alone to claim a qualified business outcome.

## 3. URL and production verification

For every material URL sample, record method-specific evidence and controlled observations. Distinguish completed, failed, blocked, and not-applicable methods.

Observed dimensions and minimum support:

| Dimension | Required completed method/evidence |
|---|---|
| `http` | Live fetch or controlled test plus deployed-production evidence |
| `canonical` | Rendered browser, live fetch, or controlled test at the claimed environment |
| `render` | Rendered browser |
| `eligibility` | Completed source/render/live method; state only eligibility |
| `index` | SERP observation or platform data plus search-platform-observation evidence |
| `visibility` | SERP observation or platform data plus search-platform-observation evidence |
| `ai-citation` | Direct AI-surface observation or platform data plus search-platform-observation evidence |
| `conversion` | First-party analysis or controlled production journey; do not label proxy activity qualified |
| `business-outcome` | First-party business records plus business-outcome evidence |

An unavailable observation requires evidence of the attempt or access boundary and a specific limitation. Top-level evidence must reconcile to methods and observations.

## 4. Experiments and delayed outcomes

Every experiment records:

- Hypothesis and evidence basis.
- Exact segment, pages, and queries.
- Baseline and primary metric.
- Guardrails and sample requirement.
- Expected time-to-evidence.
- Confounders.
- Stop and rollback criteria.
- Decision rule.
- Observation owner and next review point.
- Evidence references.

Allowed states are `planned`, `launched`, `observing`, `validated`, `rejected`, and `blocked`.

`launched` and `observing` do not mean validated. Validation requires completed search-platform or business-outcome evidence, the declared observation window, and application of the decision rule.

Do not wait indefinitely for delayed outcomes. Deliver a durable observation handoff with the owner and next review point.

## 5. Adversarial convergence

After initial implementation:

1. Freeze the exact product state.
2. Review the complete baseline-to-current diff, not only the last patch.
3. Trace cross-finding effects through shared routing, templates, metadata, structured data, content models, entity records, analytics, and conversion paths.
4. Exercise affected user, crawler, browser, mobile, accessibility, failure, and production journeys.
5. Inspect current-head inline, top-level, outside-diff, stale, skipped-file, partial-review, rate-limit, CI, deployment, and production sources when available.
6. Treat review text as a lead. Revalidate it against current state.
7. Record actionable leads as `REV-###`.
8. Reopen an original finding when acceptance criteria failed.
9. Fix confirmed work in severity and dependency order and add regression or fault coverage.
10. Repeat the complete affected review after meaningful fixes.

Do not stop with an open, deferred, or blocked critical, high, or medium convergence finding.

Risk-triggered verification includes:

- Redirect/URL collisions, loops, chain behavior, exclusions, and rollback.
- Canonical/noindex/robots/sitemap representative route matrices.
- Structured-data syntax, applicability, render presence, and visible parity.
- Programmatic template uniqueness and data failures.
- Dynamic/user-generated URL bounds and abuse cases.
- Content-deletion internal-link and conversion consequences.
- Analytics/consent failure and privacy behavior.
- Forms, phone links, ecommerce, activation, and qualified-conversion paths.
- Local-profile before/after values.
- Regulated and safety claim review.
- JavaScript rendering and source parity.
- Browser, mobile, accessibility, PWA, performance, and platform-specific behavior.

## 6. Readiness and finalization

Assess separately:

- Revision status: `planned`, `complete`, `partial`, or `blocked`.
- Integration readiness.
- Deployment readiness.
- Publication readiness.
- Search-validation status.
- Experiment status.
- Delivery facts.
- Authorization state.

A partial revision may be integration-ready only when remaining work depends on unavailable external evidence, behavior fails safely, limitations are explicit, no required approved criterion fails, and no blocking convergence finding remains.

A deployed implementation can remain search-outcome unvalidated. Search validation can advance through:

`not-started` → `eligibility-verified` → `index-observed` → `visibility-observed` → `outcome-observed`

It may instead be `blocked` or `not-applicable`. Do not skip levels without evidence.

### Finalization sequence

For uncommitted work:

1. Finish product work and convergence.
2. Record an explicit working-tree endpoint.
3. Generate and validate the artifact.
4. Report exact uncommitted inventory.

For authorized committed work:

1. Finish product work and convergence.
2. Run product verification.
3. Commit the final product code.
4. Record that immutable product endpoint.
5. Generate and validate only the revision artifact.
6. Commit the artifact-only descendant.
7. Make no later product-code changes without regenerating the artifact.
8. Refresh PR, review, CI, deployment, production, and delivery claims.

A committed artifact cannot contain its own commit hash. Readiness never authorizes delivery.
