# SEO Audit Methodology

Use this as a conditional investigation map, not a checklist that manufactures findings. Every activated area must end as passed, failed, partial, blocked, not-tested, or not-applicable in `coverage.json`.

## Evidence classes

Use these exact classes and keep them separate from confidence and severity:

1. `official_documentation` — current first-party platform, standards, policy, or product documentation.
2. `first_party_data` — Search Console, Bing Webmaster Tools, analytics, logs, Business Profile, merchant feeds, rank tracking, conversion or revenue records.
3. `controlled_test` — reproducible crawl, render, HTTP, structured-data, browser, log, experiment, or other isolated test.
4. `direct_observation` — live SERP, production page, profile, result feature, referral, interface, or user-visible behavior observed during the audit.
5. `strong_inference` — conclusion supported by multiple direct facts but not directly measured.
6. `industry_correlation` — repeated independent correlation or observational research that does not establish platform causation.
7. `unverified_theory` — plausible but unsupported or weakly supported idea. It may only support an investigation or experiment.

A source can support what a platform documents, what was observed, or what a dataset contains. It does not automatically prove a project-specific ranking cause.

## 1. Business and search model

Document:

- Customer, geography, funnel, lifetime or transaction value where available, seasonality, brand constraints, conversions, and lead/revenue quality.
- Primary organic jobs across discovery, comparison, decision, local, navigational, transactional, support, and post-purchase journeys.
- Brand/non-brand demand and the distinction between traffic and qualified opportunity.
- Real differentiation: source-worthy data, tools, direct experience, original media, unique inventory, trusted service, or another defensible reason to be selected.
- Applicable vertical modules and explicit non-goals.

Do not invent search volume. When no first-party or credible external demand evidence exists, record demand as unknown and define the cheapest useful validation.

## 2. Live search reality

Build a query sample from user journeys and commercial value rather than keyword permutations. Include representative head, long-tail, local, comparison, problem, brand, and conversion-adjacent queries when applicable.

For each observation record:

- Query, date/time, country or location, language, device class, signed-in/personalization state when known, and search surface.
- Visible result features and actual domains/entities winning.
- The audited project's presence or absence without extrapolating to an invented rank history.
- AI Overview/AI Mode, local pack/map, image, video, forum, shopping, news, answer, or other features when they actually appear.
- Temporal, localization, and personalization limitations.

Use Search Console, Bing Webmaster Tools, rank tracking, or logs when available. A single manually observed SERP is a snapshot, not a stable ranking fact.

## 3. Crawling, rendering, and indexation

Conditionally inspect:

- Robots directives and crawler-specific rules.
- XML, image, video, news, or other sitemaps.
- HTTP status, redirect chains, canonicalization, soft 404s, duplicate and parameter URLs, faceting, pagination, and URL normalization.
- Source HTML, rendered DOM, accessibility tree, and user-visible content where rendering could change discovery or meaning.
- JavaScript execution, hydration, delayed or interaction-gated content, mobile parity, internal discovery, click paths, orphaning, and crawl depth.
- Index eligibility versus production index evidence. A theoretically indexable URL is not proven indexed.
- CDN, WAF, authentication, geoblocking, rate controls, bot verification, and server behavior that may alter crawler access.

Distinguish agents by documented purpose. Do not collapse search indexing, training, user-triggered retrieval, and other crawler roles into “AI bots.”

## 4. Information architecture and internal authority

Evaluate taxonomy, navigation, URL design, hubs, breadcrumbs, contextual links, anchor context, click depth, orphan pages, template effects, canonical clusters, competing pages, consolidation opportunities, and crawl prioritization.

Map pages and tools to journeys, entities, services, locations, and conversion intent. Do not manufacture doorway pages or near-duplicate geography pages.

## 5. Content and evidence quality

Evaluate only against the job the page must perform:

- Intent satisfaction and useful next steps.
- Originality, information gain, direct experience, local or domain specificity, factual support, claim accuracy, source quality, and update/review process.
- Authorship and organizational responsibility without treating credential theater as a substitute for accuracy.
- Media usefulness, source-worthy facts, tools, data, explanations, or demonstrations.
- Templating, duplication, cannibalization, thinness, decay, and scaled-content risk.
- Whether programmatic pages provide distinct user value and reliable data rather than search-targeted permutations.

Word count, keyword density, FAQ count, and arbitrary content length are non-goals unless project evidence makes them relevant.

## 6. AI-mediated discovery and citation

Investigate Google AI features, Bing/Copilot, ChatGPT search, and other surfaces only when material and researchable.

Separate:

- Core crawl/index eligibility and snippet controls.
- Surface-specific documented controls.
- Retrieval and citation observations.
- Source clarity, passage support, factual consistency, entity disambiguation, and attribution.
- Referral and citation observability.
- Query fan-out implications as a research model, not a guarantee that subtopic coverage creates citations.

Do not assume `llms.txt`, special AI schema, artificial “chunking,” AI-oriented prose, or manufactured mentions help. Unsupported ideas belong in experiments with falsifiable metrics.

## 7. Structured data and machine-readable facts

Validate syntax, rendered presence, content parity, applicability, entity identifiers, graph consistency, required/recommended properties, and current search-feature eligibility.

Separate schema.org vocabulary validity from platform feature support. Detect invisible, unsupported, misleading, obsolete, duplicated, or self-serving markup. Include feeds, Business Profile, Merchant Center, or other structured sources when applicable.

## 8. Entity, brand, reputation, and off-site evidence

Conditionally inspect business/entity consistency, organization-person relationships, names, addresses, phones, service areas, profiles, citations, reviews, owner responses, earned mentions, backlinks, link quality, link gaps, spam exposure, source credibility, and realistic digital-PR opportunities.

Separate citation cleanup, genuine authority building, and manipulative acquisition. Never recommend fake reviews, manufactured mentions, parasite SEO, doorway pages, or link schemes.

## 9. Local SEO

When local intent is material, inspect Business Profile alignment, categories, services, areas, hours, photos, review patterns, responses, landing-page alignment, local-pack competitors, proximity limitations, NAP consistency, local citations/links, location-page quality, and map conversion paths.

Treat local organic and local-pack visibility as related but distinct. Record unsupported location claims and templated doorway strategies.

## 10. Performance, experience, and accessibility

Separate:

- Documented eligibility or search-feature consequences.
- Field Core Web Vitals versus lab diagnostics.
- Probable user behavior and conversion consequences.
- General quality or accessibility concerns.

Inspect mobile usability, intrusive UI, navigation, readability, media loading, layout stability, interaction performance, keyboard/accessibility barriers, and conversion friction. Do not label every UX defect a ranking factor.

## 11. Vertical systems

Activate only applicable modules:

- Ecommerce: product data, Merchant Center, variants, availability, price/currency, reviews, shipping/returns, duplication, faceting, and policy.
- International: locale architecture, hreflang, language/country targeting, currency, translation quality, canonical conflicts, and regional duplication.
- News: eligibility, publisher policy, dates, corrections, authorship, freshness, feeds, and article structure.
- Image/video: rights, originals, discoverability, metadata, transcripts/captions, thumbnails, embeds, loading, and dedicated result surfaces.
- Marketplaces/tools/SaaS/publishers: inventory/data uniqueness, free-versus-gated content, UGC governance, templates, documentation/support journeys, and product-led conversion.

## 12. Search policy and risk

Investigate confirmed violations, active exposure, and theoretical risk separately. Cover spam policies, manual actions, security issues, hacked content, reputation abuse, expired-domain abuse, scaled content abuse, cloaking, hidden text, structured-data policy, review markup, regulated or legal constraints, and risky legacy tactics.

Do not imply a manual action or policy violation without evidence.

## 13. Measurement and experimentation

Inventory the current stack and gaps. Establish baselines where possible by query, page, intent, geography, device, brand/non-brand, result type, conversion, qualified lead/revenue, and observable AI referral or citation data.

For experiments define:

- Hypothesis and evidence basis.
- Primary metric and guardrails.
- Segment and sample.
- Time horizon and expected time-to-evidence.
- Confounders and external events.
- Rollback criteria.
- Decision rule.

Account for attribution limits and zero-click discovery. Never promise uplift or infer causation from an uncontrolled before/after change.

## 14. Strategy and prioritization

Separate technical blockers, demand gaps, content opportunities, authority gaps, conversion problems, defensive work, owner decisions, and speculative experiments.

Compare business value, confidence, evidence quality, cost, dependencies, reversibility, time-to-evidence, and downside. Preserve strengths and reject work whose only purpose is making the audit look exhaustive.

## 15. Prove investigation depth

Do not summarize an activated module as “reviewed” without recording its facet-level work in `coverage.json`.

- Create one `surface_check` for every required facet in `MODULE_FACETS`.
- Record the method, result, supporting evidence, findings, limitations, and whether all work possible without unavailable access was completed.
- Build explicit `serp_samples` and `url_samples`; do not hide sampling inside prose.
- Reconcile production output to the audited source revision. Treat an unverified deployment as material when it could change findings.
- For every finding, separately record technical eligibility, observed performance, consequence type, qualified-conversion linkage, implementation targets/non-goals, evidence roles, and verification environment.
- Record deliberate non-pursuits so a later revision agent does not “fix” rejected folklore or recreate false positives.

Blocked first-party evidence narrows the conclusion; it does not permit abbreviated crawling, rendering, source inspection, public research, or conversion-journey testing.
