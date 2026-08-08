---
name: brand-teardown
description: Perform a rigorous, read-only, evidence-led audit of how a project is understood, trusted, remembered, preferred, and acted on across positioning, audience fit, brand architecture, messaging, offers, proof, claims, voice, visual identity, customer experience, competitors, and channel expression. Use when Codex is asked for a brand teardown, brand audit, positioning or messaging diagnosis, identity consistency review, trust or differentiation analysis, multi-brand architecture review, brand-risk assessment, or an implementation-ready brand findings handoff for a business, product, service, creator, nonprofit, or multi-brand organization.
---

# Brand Teardown

Answer one central question: does the project have a clear, trustworthy, differentiated, memorable, and consistently expressed identity that causes the right audience to understand it, prefer it, and act?

Audit the operating brand, not merely its logo or prose. Treat positioning, proof, offers, experience, voice, visuals, and channel behavior as one system while preserving authentic founder, operator, or community material that makes the identity credible and recognizable.

## Operating contract

- Treat the audited project, production surfaces, profiles, listings, collateral, and external systems as read-only.
- Permit isolated browsing, rendering, captures, repository inspection, public research, and controlled calls-to-action that do not submit deceptive leads, publish content, contact third parties, buy anything, or alter live state.
- Never change the audited project. Put the handoff in a separate requested location or a disposable audit directory.
- Distinguish brand review from adjacent disciplines. Record product, SEO, accessibility, conversion, legal, engineering, or operational dependencies without pretending this audit replaces those disciplines.
- Adapt modules to the project type. Mark irrelevant work not applicable with a project-specific reason; do not manufacture checklist findings.
- Separate stakeholder intent, observable expression, audience perception, and business outcomes. Implementation evidence does not prove recall, preference, trust, conversion, or revenue.
- Never invent audiences, competitors, reviews, credentials, certifications, licensing, prices, guarantees, results, customer language, market demand, or visual provenance.
- Treat stakeholder claims as hypotheses until reconciled with the actual product, messages, proof, and customer journey.
- Use current public research for competitor and time-sensitive claims. Date the evidence and mark incomplete competitive work provisional.
- Preserve strengths, deliberate quirks, honest limitations, useful educational material, and channel-specific variation.
- Use critical or high severity only for demonstrated consequences. Aesthetic preference alone cannot support critical or high severity.
- Call the audit `provisional` whenever inaccessible material surfaces could materially change the verdict. A homepage-only review is never complete for a multi-surface brand.

## Establish the brand and business model

Infer available facts first. Ask only questions whose answers would materially change scope, severity, or strategy:

1. What is sold, to whom, in which markets, through which offers and conversion paths.
2. Buyer, user, influencer, and blocker roles; trigger problems; desired outcomes; perceived risks; objections; and proof needs.
3. Parent, operating, product, service, resource, campaign, founder, domain, and social identities.
4. Intended position, differentiators, personality, non-goals, and identity elements that must be preserved.
5. Available repository, production, social, review, collateral, customer-research, analytics, and stakeholder evidence.

Briefly state the interpreted brand thesis, activated conditional modules, consequential assumptions, and likely blockers before deep investigation.

## Execute the audit

Read [audit-methodology.md](references/audit-methodology.md) before collecting evidence. Read [evidence-and-claims.md](references/evidence-and-claims.md) before evaluating proof, competitors, or subjective visual material.

1. Inventory access, brands, audiences, offers, channels, artifacts, evidence age, and production/source alignment.
2. Exercise primary customer journeys at representative desktop and mobile states when a website is material. Observe approximately 5-second, 30-second, and several-minute comprehension.
3. Build a claim inventory covering promises, proof, credentials, guarantees, availability, pricing, outcomes, identity, and authority.
4. Review brand architecture, positioning, message hierarchy, offers, proof, voice, visuals, and channel expression as connected systems.
5. Capture multimodal evidence when available: screenshots, logos, photography, video frames, advertisements, flyers, estimates, invoices, packaging, signage, uniforms, vehicles, repository pages, and documentation.
6. Research concrete competitors and substitutes. Capture dated evidence for category language, trust conventions, offers, visual patterns, strengths, and strategic consequences.
7. Record facet-level work in `coverage.json` while investigating. State what was established, what remains unknown, and why.
8. Register every actionable observation exactly once. Classify non-actionable material as a retained strength, passed check, limitation, context, or not applicable.

## Synthesize findings

Read [report-contract.md](references/report-contract.md) before writing the handoff.

- Keep severity, confidence, evidence quality, claim state, judgment basis, and outcome evidence separate.
- Tie every finding to affected brands, audiences, surfaces, and channels.
- Explain the brand, business, trust, differentiation, and recognition consequences; use `Not applicable — <reason>` only when a dimension genuinely does not apply.
- Separate owner decisions from operational corrections. A recommendation never authorizes renaming, repositioning, consolidation, offer changes, guarantee changes, or identity replacement.
- Require project-specific evidence. Generic advice without an observed condition is not a finding.
- Deduplicate shared causes without erasing distinct audience or channel consequences.
- Keep dependencies acyclic and order every prerequisite before its dependent.
- Put foundational positioning and architecture decisions before claims, messaging, visuals, rollout, measurement, and externally blocked work.
- Give retained strengths explicit preservation constraints. If no retained strength exists, require a specific justification.

## Produce the handoff

Create `brand-teardown/` outside the audited source tree unless the user explicitly selects a safe in-repository documentation location. If the target exists, use a dated sibling unless replacement is authorized.

Use the exact artifact and canonical schemas in [report-contract.md](references/report-contract.md). `findings.json` and `coverage.json` are authoritative. Never hand-edit the five generated registers.

Render and validate:

```bash
python3 <skill-directory>/scripts/render_handoff.py <brand-teardown-directory>
python3 <skill-directory>/scripts/validate_brand_teardown.py <brand-teardown-directory>
```

Fix every error. Validator success is necessary, not sufficient. Manually reconcile evidence truthfulness, narrative actions, competitor conclusions, visual judgment, blocked surfaces, claim status, owner decisions, and implementation-versus-outcome evidence.

## Forward testing and changes to this skill

When modifying the contract or validator, follow [forward-testing.md](references/forward-testing.md). Use materially different local-service and software/developer-product projects, keep both projects read-only, validate both complete disposable handoffs, and harden only systemic weaknesses.

## Boundary and handoff

This skill audits and recommends. It does not implement a brand revision, rewrite copy, replace visual identity, publish content, change profiles, or prove improved perception or revenue.

A future `brand-revision` skill may consume approved findings. It must preserve authentic voice, recognizable identity, verified proof, working conversion paths, accessibility, SEO, and project constraints. Implementation alone never proves recall, preference, trust, or business outcomes.

Report the verdict, most consequential findings and owner decisions, tested and blocked evidence, complete or provisional status, artifact path, validator result, and a clear statement that no audited project or external system was modified.
