# SEO Teardown Report Contract

Create this deterministic handoff:

```text
seo-teardown/
├── README.md
├── 00-executive-verdict.md
├── 01-search-business-model.md
├── 02-evidence-and-access.md
├── 03-live-search-and-competitors.md
├── 04-technical-discovery-indexation.md
├── 05-content-entity-authority.md
├── 06-platform-and-vertical-modules.md
├── 07-measurement-and-experiments.md
├── 08-owner-decisions-and-blockers.md
├── 09-implementation-sequence.md       # generated
├── 10-review-coverage.md               # generated
├── 11-findings-register.md             # generated
├── findings.json                       # canonical
├── coverage.json                       # canonical
└── evidence/
```

Keep evidence compact, sanitized, reproducible, and read-only. `findings.json` and `coverage.json` are authoritative. Never hand-edit generated files.

## Narrative files

### README.md

State the audited project, revision, production locator, read-only boundary, canonical files, renderer, validator command, and provisional/complete status.

### 00 — Executive verdict

Include an exact `**Review status:** complete|provisional` line, the search/business thesis, qualified-conversion target, production-revision status, overall verdict, strengths, primary blockers/opportunities, owner decisions, scope, research dates, and what would complete a provisional audit.

### 01 — Search/business model

Record customers, geography, funnel, commercial value, brand/non-brand jobs, search journeys, defensible differentiation, applicable verticals, assumptions, and explicit non-goals. Separate traffic from qualified-business value.

### 02 — Evidence and access

Inventory repositories, production, platform accounts, analytics, logs, profiles, feeds, rank/conversion records, test methods, access dates, limitations, and requested read-only access. Explain production/source reconciliation.

### 03 — Live search and competitors

Summarize the canonical SERP samples from `coverage.json`: query, surface, date, location/device, result features, actual winners, target observation, and limitations. Never turn a snapshot into rank history.

### 04 — Technical discovery/indexation

Cover HTTP behavior, robots, crawler-purpose distinctions, sitemaps, canonicals, redirects, rendering, source/DOM/user-visible parity, parameters, dynamic URLs, discoverability, mobile parity, production revision, theoretical eligibility, and observed index evidence separately.

### 05 — Content, entity, and authority

Cover intent satisfaction, originality, claims, sources, authorship/review, templates, scale, entity consistency, reputation, reviews, mentions/links, local evidence, conversion paths, preserved strengths, and deliberate non-pursuits.

### 06 — Platform and vertical modules

Cover AI-mediated discovery, structured data, local, performance/accessibility, ecommerce, international, news, image/video, marketplace/tool/SaaS, regulated-content, or other applicable systems. Record non-applicable systems rather than forcing findings.

### 07 — Measurement and experiments

Record stack, baselines, qualified conversions, attribution limits, zero-click/AI observability, experiments, hypotheses, metrics, guardrails, confounders, rollback, and decision rules.

### 08 — Owner decisions and blockers

List every `blocked` or `decision_required` finding ID, the exact missing access/decision, safe method of provision, consequence, and downstream work it blocks. Write `None` when absent.

## Canonical `findings.json`

Use schema version `seo-teardown-v3`. This version is paired with `seo-teardown-coverage-v3`; do not mix v2 and v3 canonical files.

### Audit object

Required fields:

- `project_name`
- `project_locator`
- `audited_revision`
- `production_locator`
- `audit_start_date`
- `audit_end_date`
- `research_window_days` — integer 1–30
- `review_status` — `complete|provisional`
- `business_model`
- `primary_geographies` — non-empty list
- `production_revision_status` — `verified|unverified|not_applicable`
- `production_revision_evidence_ids` — list

A public production audit cannot be `complete` while its deployed revision is materially unverified.

### Evidence source

Every source requires:

- `id` — `EVID-###`
- `evidence_class` — `official_documentation|first_party_data|controlled_test|direct_observation|strong_inference|industry_correlation|unverified_theory`
- `title`
- `publisher_or_owner`
- `locator`
- `accessed_at`
- `platform_sensitive` — boolean
- `summary`
- `limitations`
- `artifact_path` — path or null

Platform-sensitive evidence must fall inside the audit research window.

### Finding object

Each finding requires:

- Identity: `id`, `title`, `kind`, `domain`, `status`, `severity`, `confidence`
- Claim calibration: `evidence_quality`, `claim_basis`, `likelihood`
- Response: `action`, `recommendation`, `if_implemented`, `if_unchanged`
- Consequence: `business_impact`, `search_consequence`
- Scope: `affected_queries`, `affected_urls_or_entities`, `platforms`
- Proof: `evidence_ids`, `evidence_links`, `reproduction`, `root_cause`
- Completion: `acceptance_criteria`, `verification`
- Coordination: `dependencies`, `conflicts`, `blocker`, `owner_decision`
- Calibration objects: `priority`, `measurement`, `implementation`
- Revision-ready objects: `search_state`, `conversion_linkage`, `implementation_scope`, `verification_context`

Controlled values retain the validator’s exact spellings.

#### Evidence links

`evidence_links` must account for every `evidence_id` exactly once:

```json
{
  "evidence_id": "EVID-001",
  "role": "supports|contradicts|context",
  "claim": "The exact bounded proposition this source supports or contextualizes."
}
```

At least one link must `support` the finding. A source’s existence does not prove every sentence in the finding.

#### Search state

```json
{
  "technical_eligibility": "eligible|ineligible|partial|unknown|not_applicable",
  "observed_performance": "present|absent_in_sample|mixed|unknown|not_applicable",
  "consequence_type": "eligibility|observed_visibility|conversion|policy|trust|quality|measurement|none"
}
```

Never infer observed performance from source-only evidence. `absent_in_sample` means only the recorded sample.

#### Qualified-conversion linkage

```json
{
  "conversion_target": "Project-specific qualified outcome",
  "funnel_stage": "discovery|comparison|decision|conversion|retention|post_purchase|not_applicable",
  "qualifiedness": "qualified|proxy|unknown|not_applicable",
  "measurement_status": "measured|partial|blocked|not_applicable"
}
```

A search recommendation must explain how it supports, protects, measures, or deliberately does not affect a qualified conversion.

#### Implementation scope

```json
{
  "targets": ["Exact routes, templates, entities, settings, records, or processes"],
  "non_goals": ["Explicit exclusions and anti-scope-creep boundaries"],
  "owner_or_external_actions": ["Required access, profile, legal, platform, or owner action"]
}
```

Targets and non-goals are mandatory. Blocked findings require an owner or external action.

#### Verification context

```json
{
  "mode": "source|rendered|live|platform_data|controlled_test|mixed",
  "environment": "Where and how the verification must occur",
  "limitations": ["Remaining constraints"]
}
```

#### Priority

Required fields: `expected_business_value`, `effort`, `reversibility`, `time_to_evidence`, `downside`.

#### Measurement

Required fields: `baseline`, `primary_metric`, `guardrail_metrics`, `time_horizon`, `confounders`, `rollback_criteria`, `decision_rule`. Opportunities, investigations, and experiments require real metrics and decision rules.

#### Implementation

Required fields: `phase_id`, positive unique `order`, `disposition`, `rationale`, `validation_gate`.

### Implementation phases

Every finding appears exactly once in one phase, ordered consistently with dependencies. Dependencies must exist, be acyclic, and occur earlier. Conflicts must be symmetric.

## Canonical `coverage.json`

Use schema version `seo-teardown-coverage-v3`. This is incompatible with v2 because SERP winners, URL methods, and surface limitations are now structured evidence contracts.

Required top-level fields:

- `review_status`
- `access`
- `modules`
- `surface_checks`
- `serp_samples`
- `url_samples`
- `deliberate_non_pursuits`
- `material_limitations`
- `narrative_reconciliation`
- `validator`

### Access categories

Include exactly: `source_repository`, `production_website`, `google_search_console`, `bing_webmaster_tools`, `analytics`, `crawl_logs`, `google_business_profile`, `merchant_feeds`, `rank_tracking`, `conversion_records`, and `location_serp_testing`.

Each records status, coverage window, materiality, evidence, limitations, and next step. Material partial/blocked access forces a provisional audit.

### Modules

Include exactly the fourteen module IDs defined by the validator. Each module records applicability, materiality, status, `check_ids`, findings, evidence, limitations, and next step.

A module summary is not proof of work. Every applicable module must have one check for every required facet in `MODULE_FACETS`. A non-applicable module has exactly one `module_scope` check with status `not_applicable`.

### Surface checks

Each `CHECK-###` requires:

- `module_id`
- required `facet`
- `method` — source inspection, live fetch, rendered browser, controlled test, platform data, SERP observation, first-party analysis, or external research
- `status` — passed, failed, partial, blocked, or not applicable
- `evidence_ids`
- `finding_ids`
- `result` — the facet-specific conclusion established by the completed work
- `unknowns` — facet-specific facts that remain unknown; required for partial and blocked checks
- `limitations` — check-specific method or interpretation constraints, not shared access boilerplate
- `limitation_refs` — reusable references to `LIMIT-###` records or `access:<category>` records
- `available_work_completed` — must be `true` for delivery

A blocked platform check does not excuse unfinished source, live, or public research. `available_work_completed` means all work possible without the missing access was completed. Each partial or blocked check must still state what was established for its exact facet and what specifically remains unknown. Repeated generic coverage sentences are invalid. Shared blockers belong in canonical access or material-limitation records and may be referenced repeatedly through `limitation_refs`.

### SERP samples

Every `SERP-###` records query, engine/surface, location, device, observed date, features, target observation, evidence, limitations, and a structured `winner_observation`. An applicable live-search module requires at least one sample.

`winner_observation` requires:

```json
{
  "status": "observed|unavailable|not_applicable",
  "results": [
    {"kind": "domain|url|named_entity", "value": "Concrete observed winner", "position": "Observed result position or surface"}
  ],
  "reason": null,
  "evidence_ids": ["EVID-001"]
}
```

An `observed` state requires at least one concrete domain, URL, or named entity. Category labels such as “local competitors,” “strategy publishers,” “wheel tools,” or “cost publishers” are invalid. When the evidence did not preserve reliable winners, use `unavailable`, an empty `results` list, a specific reason, and evidence IDs. Never reconstruct or invent winners after the fact.

### URL samples

Every `URL-###` records URL, role, source-revision alignment, findings, reconciled evidence, limitations, `method_evidence`, and five structured observations: HTTP, eligibility, index, canonical, and render. Available production access requires samples.

Each claimed method requires:

```json
{
  "method": "source_inspection|live_fetch|rendered_browser|controlled_test|platform_data|serp_observation|first_party_analysis|external_research",
  "status": "completed|failed|blocked|not_applicable",
  "observation": "What this exact method produced or failed to produce",
  "evidence_ids": ["EVID-001"],
  "limitations": []
}
```

Each URL observation requires `status`, `value`, `supported_by_methods`, `evidence_ids`, and `limitations`. Observed HTTP requires a completed live fetch or controlled test. Observed rendering requires a completed rendered-browser method. Observed index state requires completed SERP or platform evidence. Failed or blocked methods cannot support observed values. An unavailable observation uses a null value, identifies the attempted or relevant methods, cites evidence, and explains the limitation. Top-level URL evidence IDs must exactly reconcile all method and observation evidence.

### Deliberate non-pursuits

Record tactics deliberately rejected and why, with evidence where applicable. Include generic false-positive defenses such as unsupported GEO tactics, fake authority, arbitrary content quotas, or expansion without distinct value when relevant.

### Material limitations and review status

Unresolved material limitations, defining/high blocked or partial modules, material blocked access, incomplete available work, or unverified production revision prevent a `complete` verdict.

### Narrative reconciliation

Every narrative file must have a reconciliation row mapping actionable statements to findings or explaining why the material is context, a passed check, limitation, assumption, or deliberate non-pursuit.

## Generated files and integrity

Run:

```bash
python3 <skill-directory>/scripts/render_handoff.py <seo-teardown-directory>
python3 <skill-directory>/scripts/validate_seo_teardown.py <seo-teardown-directory>
```

The validator rejects missing files, malformed values, stale research, evidence-role drift, evidence-quality inflation, unsupported theory, experiment severity inflation, eligibility/performance conflation detectable from verification mode, generic category-only SERP winners, unsupported URL observations, failed methods represented as completed, unreconciled method evidence, repeated surface-coverage boilerplate, missing conversion linkage, vague implementation scope, missing facets, unfinished available work, missing samples, false complete status, dependency errors, Markdown/JSON disagreement, and incomplete owner/blocker handoff.
