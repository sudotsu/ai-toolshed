# Current Platform Research Protocol

Search platforms change continually. This file defines how to research them; it is not a frozen encyclopedia of ranking factors.

## Mandatory research rule

During every audit, research every material platform-sensitive claim again. Record source title, publisher, locator, update/publication date when available, access date, relevant excerpt or paraphrase, and limitations in the evidence inventory.

Prefer current primary sources:

- Google Search Central, Search Console documentation, Search status/policy documentation, Business Profile and Merchant Center documentation.
- Microsoft Bing Webmaster Tools, IndexNow, Microsoft merchant/local documentation, and official Copilot/webmaster guidance.
- OpenAI publisher, crawler, search, and referral guidance.
- Schema.org vocabulary plus the search platform's own feature documentation.
- W3C, WHATWG, HTTP, robots, accessibility, and web-platform specifications.
- Official vertical-system documentation for news, video, image, ecommerce, international, or local surfaces.

Use independent studies only when primary sources cannot answer the question. Label design, sample, date, confounders, conflicts, and whether the evidence is causal, observational, or anecdotal.

## Evidence hygiene

- Official documentation establishes documented requirements, controls, or stated behavior—not guaranteed ranking or inclusion.
- Patents describe possible inventions, not proof of current production use.
- Search quality rater guidelines describe evaluation guidance, not direct per-page ranking inputs.
- Tool scores and vendor flags are diagnostics, not defects until project-specific impact is established.
- Correlation studies do not prove causation.
- A live result is a dated, localized observation.
- A crawler user-agent rule does not prove successful indexing, retrieval, citation, or ranking.
- Platform marketing claims require qualification and should not become project performance facts.

## Crawler and control distinctions

For each material agent or control, identify its currently documented purpose before interpreting access:

- Search indexing and serving.
- Search or answer retrieval.
- Model training or improvement.
- User-triggered fetchers or browser agents.
- Preview/snippet controls.
- Removal, noindex, canonical, and robots behavior.

Do not assume one crawler's permission substitutes for another. Do not imply that blocking training necessarily blocks search retrieval, or that allowing retrieval guarantees citation.

## AI-search guardrails

Before recommending an AI-search tactic, answer:

1. Which platform and surface is affected?
2. Is the behavior officially documented, directly observed, measured in first-party data, or only inferred?
3. Is there a special control, or do ordinary search eligibility and content fundamentals apply?
4. Can the proposed change harm classic search, accessibility, conversion, legal compliance, or source clarity?
5. What metric could falsify the recommendation?

Unsupported `llms.txt`, special schema, content chunking, synthetic mentions, citation bait, or AI-targeted rewriting belongs in an experiment—not a confirmed finding.

## Staleness controls

- Mark platform-sensitive evidence with `platform_sensitive: true`.
- Access it during the audit research window recorded in `findings.json`.
- Reject discontinued result types, obsolete markup, superseded crawler guidance, and outdated feature availability.
- Review official documentation update logs when a recommendation depends on a recent or renamed feature.
- State geographic, account, language, device, and rollout limitations.
