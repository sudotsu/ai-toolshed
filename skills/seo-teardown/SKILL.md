---
name: seo-teardown
description: Perform a comprehensive, read-only, evidence-led teardown of a public website or web product's organic-search visibility, local discovery, AI-mediated discovery, indexation, content and authority, measurement, and qualified-conversion opportunity. Use when the user asks for a deep SEO audit, technical SEO teardown, local SEO investigation, AI Overview/AI Mode/Copilot/ChatGPT search audit, organic growth diagnosis, search visibility gap analysis, or an implementation-ready SEO findings handoff for a repository, deployed site, or both.
---

# SEO Teardown

Investigate whether the project can earn qualified organic discovery and conversions across the search surfaces that materially affect its business. Do not produce an SEO score, generic checklist, keyword-density advice, or a vendor-tool dump.

## Operating contract

- Treat source code, production configuration, search-platform settings, profiles, feeds, listings, outreach, and publication as read-only.
- Normal isolated crawling, rendering, HTTP inspection, exports, local builds, disposable diagnostics, and controlled tests are allowed. Disclose their scope and side effects.
- Adapt the audit to the business model. Do not activate irrelevant modules merely to appear exhaustive.
- Separate traffic opportunity from qualified-business opportunity.
- Distinguish official documentation, first-party data, controlled tests, direct observation, strong inference, industry correlation, and unverified theory.
- Never present folklore, patents, vendor claims, isolated case studies, or correlation studies as confirmed ranking-system facts.
- Never invent demand, volume, rankings, impressions, conversions, citations, competitors, or local visibility.
- Use fresh web research during every audit for platform-sensitive claims. Prefer current primary platform documentation and record access dates.
- Preserve strengths, passed checks, explicit non-goals, and deliberate exclusions.
- A generic best practice is not a finding. Require a project-specific consequence, documented eligibility requirement, credible evidence-supported opportunity, or clearly labeled experiment.
- Call the teardown **provisional** whenever missing production evidence, first-party data, live crawl/index evidence, location-specific SERP testing, or another material limitation could change the verdict.

## Start with the search and business model

Infer from available evidence, then ask only questions whose answers would materially alter scope, severity, opportunity, or prioritization:

1. Intended customers, geography, funnel, commercial value, seasonality, brand constraints, and primary conversions.
2. Business model and applicable search systems: local service, publisher, SaaS, ecommerce, marketplace, tool, international, news, image/video, or another vertical.
3. Repository, production, platform, and first-party-data access.
4. Brand versus non-brand demand, conversion quality, and defensible differentiation.
5. Known constraints, prohibited tactics, owner decisions, and explicit non-goals.

Before deep work, briefly state the interpreted search thesis, activated modules, material assumptions, and likely blockers.

## Execute the audit

Read [audit-methodology.md](references/audit-methodology.md) before investigation.

1. Inventory evidence and access before drawing conclusions.
2. Build a representative query and journey sample tied to business value.
3. Observe current search results and record concrete winning domains, URLs, or named entities with location, device, personalization, and date limitations. When reliable winners were not captured, record an evidenced unavailable state instead of a category label or guess.
4. Compare theoretical eligibility with production crawling, rendering, indexing, and performance evidence; reconcile the deployed output to the audited source revision.
5. Trace discoverability, internal authority, content usefulness, entity clarity, reputation, structured facts, and conversion paths.
6. Activate AI-discovery, local, ecommerce, international, news, image, video, or other vertical modules only when material.
7. Separate documented controls from transferable fundamentals and unsupported surface-specific tactics.
8. Establish measurement gaps and experiments with hypotheses, guardrails, confounders, time-to-evidence, and decision rules.
9. Record every activated module through its required facet-level surface checks, plus explicit SERP and URL samples. Surface checks must be facet-specific, and URL observations must identify which completed, failed, or blocked method produced the evidence. Missing first-party access never excuses unfinished public/source work.
10. Reconcile every actionable narrative statement to exactly one finding ID; classify non-actionable material as a strength, passed check, limitation, assumption, deliberate non-pursuit, or explicit deferral.

For volatile platform behavior, read [platform-research.md](references/platform-research.md) and conduct current primary-source research. Do not rely on the reference as a frozen ranking-factor encyclopedia.

## Synthesize findings and strategy

Read [report-contract.md](references/report-contract.md) before writing the handoff.

- Keep severity, confidence, evidence quality, expected value, effort, and speculation separate.
- Experiments and unverified theories cannot become high-severity defects.
- Deduplicate shared root causes without erasing distinct query, page, platform, or conversion consequences.
- Identify what to fix, add, change, consolidate, remove, preserve, investigate, test, decide, or deliberately leave alone.
- Order work by decisions and evidence gates, safety/policy and technical eligibility, root-cause dependencies, qualified-business value, time-to-evidence, and reversibility—not by severity alone.
- Record conflicts and mutually exclusive paths. Do not hand a future revision skill contradictory instructions.
- For every finding, separate technical eligibility from observed performance, tie the consequence to a qualified conversion, identify exact implementation targets and non-goals, state evidence roles, and define the verification environment.
- Review the current project head before delivery. Record newly discovered convergence findings rather than silently expanding unrelated scope.

## Produce the handoff

Create `seo-teardown/` at the project root unless the user specifies another location. If it exists, use a dated sibling unless replacement is explicitly authorized.

Use the exact contract in [report-contract.md](references/report-contract.md). `findings.json` and `coverage.json` are canonical. Generate the deterministic Markdown registers with:

```bash
python3 <skill-directory>/scripts/render_handoff.py <seo-teardown-directory>
```

Then validate:

```bash
python3 <skill-directory>/scripts/validate_seo_teardown.py <seo-teardown-directory>
```

Fix every validation error. Validator success is necessary, not sufficient: manually review factual support, live-search limitations, narrative reconciliation, and whether any recommendation exists merely because a checklist item was absent.

End the user-facing delivery with the verdict, highest-consequence findings and decisions, tested and blocked evidence, complete versus provisional status, handoff path, validator result, and a clear statement that no fixes or external mutations were performed.
