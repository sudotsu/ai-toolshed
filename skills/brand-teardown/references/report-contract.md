# Brand Teardown Report Contract

Create this deterministic, read-only handoff:

```text
brand-teardown/
├── README.md
├── 00-executive-verdict.md
├── 01-brand-and-business-model.md
├── 02-positioning-and-differentiation.md
├── 03-brand-architecture.md
├── 04-message-offer-and-customer-journey.md
├── 05-trust-proof-and-claims.md
├── 06-voice-and-verbal-identity.md
├── 07-visual-and-channel-system.md
├── 08-competitive-brand-landscape.md
├── 09-findings-register.md                 # generated
├── 10-owner-decisions.md                   # generated
├── 11-implementation-sequence.md            # generated
├── 12-review-coverage-and-limitations.md    # generated
├── 13-brand-claim-inventory.md              # generated
├── findings.json                            # canonical
├── coverage.json                            # canonical
└── evidence/
```

Keep evidence compact, sanitized, reproducible, and outside the audited project. `findings.json` and `coverage.json` are authoritative. Never hand-edit generated files.

## Narrative responsibilities

### README.md

State project and revision, production locator, audit dates, read-only boundary, canonical files, renderer and validator commands, review status, and evidence limitations. Use non-empty metadata lines labeled exactly `Project`, `Audited revision`, `Production locator`, `Audit dates`, `Review status`, `Boundary`, `Canonical files`, and `Evidence limitations`.

Use portable commands with placeholders exactly as shown under Generated files and validation. Never embed a machine-specific absolute skill path in the delivered handoff.

### 00 — Executive verdict

Include an exact `**Review status:** complete|provisional` line, brand thesis, audiences, overall verdict, strongest retained qualities, primary gaps and risks, owner decisions, best-established standard used for comparison, remaining gap to that standard, scope, dates, assumptions, and completion requirements.

### 01 — Brand and business model

Record what is sold, what customers receive, project type, audiences and roles, triggers, outcomes, risks, objections, alternatives including inaction, proof needs, customer journey, and inconsistencies between stakeholder intent and actual expression.

### 02 — Positioning and differentiation

Record category, target customer, problem/outcome, purpose, reasons to choose, supportable differentiators, generic category language, experience alignment, crowded positions, and credible open territory.

### 03 — Brand architecture

Record every material brand, company, product, service, tool, resource, campaign, founder identity, domain, and social identity; ownership and endorsement relationships; naming or domain collisions; dilution; and decisions that only the owner can make.

### 04 — Message, offer, and customer journey

Record 5-second, 30-second, and deep comprehension; promise and support hierarchy; audience cues; proof placement; objections; offer inventory; deliverables; process; calls to action; next steps; readiness fit; pricing, guarantee, availability, or scope claims; mobile behavior; and competing offers.

### 05 — Trust, proof, and claims

Summarize the canonical claim inventory and proof system: reviews, testimonials, cases, before/after evidence, work samples, credentials, licensing, insurance, certifications, tenure, owner/team/local presence, process, safety, outcomes, media, awards, accreditation, technical proof, repositories, guarantees, and policies. Separate verified, plausible but unverified, unsupported, contradicted, outdated, buried, and weak proxy proof.

### 06 — Voice and verbal identity

Record authenticity, recognizability, audience and situation fit, confidence and humility, cross-channel behavior, generic or AI-like language, fear or urgency, technical accessibility, useful personality, and exact verbal strengths to preserve.

### 07 — Visual and channel system

Record logo/wordmark, color, typography, hierarchy, spacing, iconography, illustration, photography, video, social graphics, legibility, contrast, mobile behavior, category distinctiveness, offer/tone alignment, provenance, and channel-specific expression across applicable digital and physical surfaces. Separate brand consequences from accessibility or legal conclusions.

### 08 — Competitive brand landscape

Summarize canonical competitor samples: selection rationale, dated evidence, category language, visual and trust conventions, offers, strengths, crowded positions, open territory, limitations, and strategic consequences. Do not invent competitor state when evidence is unavailable.

Use the exact `##` section headings enforced by `validate_brand_teardown.py` for every narrative. Each section must contain substantive project-specific analysis, not a label, placeholder, one-line summary, or repeated substantive paragraph. The headings are the deterministic completeness boundary; content remains evidence-led prose rather than generated boilerplate.

## Canonical `findings.json`

Use schema version `brand-teardown-v1`.

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
- `project_type` — `local_service|software_developer_product|saas|agency_professional_service|ecommerce|creator_media|nonprofit|multi_brand|other`
- `brands` — non-empty list of canonical brand names
- `primary_audiences` — non-empty list
- `production_revision_status` — `verified|unverified|not_applicable`
- `production_revision_evidence_ids` — list
- `zero_strengths_justification` — null or specific explanation
- `established_standard` — concrete relevant benchmark or standard used for final comparison
- `remaining_standard_gaps` — list; empty only when evidence supports no material remaining gap

A material public audit cannot be complete while the deployed revision is unverified. `established_standard` must name the relevant comparison basis, not merely say “best practice.”

### Evidence source

Every source requires exactly:

```text
id, evidence_class, evidence_scope, title, publisher_or_owner, locator,
accessed_at, volatile, summary, limitations, artifact_path, supersedes
```

- `id`: `EVID-###`
- `evidence_class`: one value from `evidence-and-claims.md`
- `evidence_scope`: `artifact_state|stakeholder_intent|audience_perception|business_outcome|competitor_state|independent_verification`
- `accessed_at`: `YYYY-MM-DD`
- `volatile`: boolean
- `artifact_path`: string or null
- `supersedes`: list of evidence IDs

Volatile evidence must fall inside the audit research window. Supersession references must exist and may not cycle.

When `artifact_path` is present, it must be a regular, non-symlinked relative file under `evidence/` and contain substantive evidence or a reproducible manifest for bundled captures. Do not point at an adjacent temporary file or use a one-line assertion as the artifact.

`production_revision_status: verified` requires referenced controlled, live, or independent alignment evidence that names the audited revision and the alignment method, such as a deployment identifier or current default-branch commit. A source review plus an unrelated public render is not revision alignment.

### Finding object

Every finding requires exactly:

```text
id, title, kind, module, status, severity, confidence, evidence_quality,
claim_state, judgment_basis, outcome_evidence_status, affected_brands,
affected_audiences, affected_surfaces, affected_channels, evidence_ids,
evidence_links, observed_condition, desired_condition, brand_consequence,
business_consequence, trust_consequence, differentiation_consequence,
recognition_consequence, proof_or_claim_gap, dependencies, conflicts,
blocker, owner_decision, recommendation, acceptance_criteria,
verification_methods, preservation_constraints, implementation_notes,
responsible_discipline, priority, implementation
```

Controlled values:

- `kind`: `gap|risk|opportunity|investigation|strength|cross_domain`
- `module`: one of the twelve module IDs defined below
- `status`: `open|blocked|decision_required|retained_strength|not_applicable|resolved`
- `severity`: `critical|high|medium|low|informational`
- `confidence`: `confirmed|high|medium|low`
- `evidence_quality`: one evidence class
- `claim_state`: `verified|plausible_unverified|unsupported|contradicted|not_applicable`
- `judgment_basis`: `observed_behavior|audience_evidence|category_evidence|accessibility_or_legibility|claim_or_provenance_evidence|aesthetic_preference|not_applicable`
- `outcome_evidence_status`: `measured|partial|blocked|not_applicable`
- `responsible_discipline`: `brand|product|seo|accessibility|legal|conversion|engineering|operations|mixed`

All affected brand, audience, surface, and channel fields are non-empty arrays. `evidence_ids`, `acceptance_criteria`, and `verification_methods` are non-empty arrays. Relationship and preservation arrays contain only strings. Every finding needs at least one supporting evidence link.

Use `Not applicable — <reason>` for consequence dimensions that genuinely do not apply. Do not leave them empty. `strength` requires informational severity, `retained_strength` status, and `preserve` disposition. `not_applicable` findings are normally represented through coverage rather than manufactured findings.

Blocked findings require `blocker`, an owner or external action in `implementation.owner_or_external_actions`, and a provisional audit when material. Decision-required findings require a precise `owner_decision`. Other findings use null for those fields.

Visual findings based only on `aesthetic_preference` cannot exceed low severity. Critical severity requires confirmed or high confidence, demonstrated catastrophic or existential brand/business consequence, and evidence stronger than inference.

#### Evidence links

Each link requires exactly:

```json
{
  "evidence_id": "EVID-001",
  "role": "supports",
  "claim": "The exact bounded proposition supported by this source."
}
```

Allowed roles are `supports`, `contradicts`, and `context`. Links must account for each `evidence_id` exactly once.

#### Priority

Required fields:

```text
brand_impact, business_impact, effort, reversibility
```

Controlled values:

- impact: `very_high|high|medium|low|unknown`
- effort: `trivial|small|medium|large|initiative|unknown`
- reversibility: `easy|moderate|hard|unknown`

#### Implementation handoff

Required fields:

```text
phase_id, order, disposition, rationale, validation_gate, targets,
non_goals, owner_or_external_actions
```

- `order`: unique positive integer across all findings, forming a **contiguous** range from
  `1` through the total finding count. Every finding is ordered exactly once and no number is
  skipped, so `1, 2, 3` is valid and `1, 5, 9` is rejected.
- `disposition`: `implement|investigate|decide|preserve|accept_risk|defer|leave_alone`
- `targets` and `non_goals`: non-empty string arrays
- `owner_or_external_actions`: string array

### Claim inventory

`claims` is a non-empty list for any public-facing project. Every claim requires exactly:

```text
id, claim, brand, surfaces, audiences, claim_type, state, risk_level,
evidence_ids, owner, required_action, verification_method
```

- `id`: `CLAIM-###`
- `claim_type`: `identity|category|audience|offer|credential|licensing|certification|safety|tenure|pricing|availability|service_area|guarantee|outcome|review|technical_capability|open_source|privacy|authority|other`
- `state`: `verified|plausible_unverified|unsupported|contradicted|outdated|not_applicable`
- `risk_level`: `high|medium|low|informational`

Verified claims require evidence. Contradicted and outdated claims require evidence supporting the conflict or age. Surfaces and audiences are non-empty lists.

### Implementation phases

Every finding appears exactly once in one phase. Every phase requires:

```text
id, title, phase_type, rationale, finding_ids, validation_gate, expected_outcome
```

`phase_type` is `foundation_decision|trust_claim_correction|message_offer|visual_system|channel_rollout|measurement_research|externally_blocked|preservation`.

Dependencies must exist, be acyclic, and occur earlier. Conflicts must be symmetric. Recommended ordering is foundation decisions, trust/claim corrections, messages/offers, visuals, channels, measurement/research, and blocked work, while preserving strengths throughout.

## Canonical `coverage.json`

Use schema version `brand-teardown-coverage-v1`.

Required top-level fields:

```text
schema_version, review_status, access, modules, surface_checks,
surface_samples, competitor_samples, material_limitations,
narrative_reconciliation, validator
```

### Access categories

Include exactly:

```text
source_repository, production_website, stakeholder_context,
customer_research, analytics_conversion_data, social_channels,
review_profiles, sales_operational_collateral, visual_assets,
competitor_public_evidence
```

Each row requires `category`, `status`, `material_to_comprehensive`, `coverage_window`, `evidence_ids`, `limitations`, and `next_step`.

Status is `available|partial|blocked|not_applicable`. Material partial or blocked access forces a provisional audit.

### Modules

Include exactly:

```text
business_audience, positioning_differentiation, brand_architecture,
message_comprehension, offer_customer_journey, trust_proof_claims,
voice_verbal_identity, visual_identity_recognition, channel_expression,
competitive_landscape, brand_risk_claim_discipline, strategic_preservation
```

Each module requires `id`, `applicable`, `materiality`, `status`, `check_ids`, `finding_ids`, `evidence_ids`, `limitations`, and `next_step`.

Status is `passed|failed|partial|blocked|not_tested|not_applicable`; materiality is `defining|high|medium|low`. Every applicable module has one surface check for every facet in the validator. A non-applicable module has exactly one `module_scope` check.

### Surface checks

Every check requires exactly:

```text
id, module_id, facet, method, status, evidence_ids, finding_ids,
method_evidence, result, unknowns, limitations, limitation_refs,
available_work_completed
```

- ID: `CHECK-###`
- method: `source_inspection|live_site_review|rendered_browser|controlled_comprehension|stakeholder_evidence|customer_research|analytics_analysis|social_profile_review|collateral_review|competitor_research|independent_verification`
- status: `passed|failed|partial|blocked|not_applicable`

Partial and blocked checks require facet-specific unknowns plus a limitation or canonical limitation reference. `available_work_completed` must be true before delivery. Repeated generic result or limitation boilerplate is invalid, including prose that differs only by inserting the current facet label.

`method_evidence` accounts for every `evidence_id` exactly once. Each entry has exactly `evidence_id`, `role`, and `observation`; role is `supports_result|context|limitation`. Passed and failed checks require at least one `supports_result` entry whose evidence class is compatible with the declared method. Context evidence cannot make a method pass. A facet cannot pass when the access ledger says its required surface is blocked or not applicable.

### Surface samples

Each sampled brand artifact requires exactly:

```text
id, surface, locator, brand, audience, channel, viewport_or_format,
method, status, observed_at, evidence_ids, finding_ids, observations, limitations
```

- ID: `SURFACE-###`
- status: `observed|unavailable|not_applicable`

Observed samples require evidence and at least one concrete observation. Unavailable samples require evidence of the attempt or access boundary plus a specific limitation. A material available production website requires desktop and mobile samples unless the project is genuinely non-web.

### Competitor samples

Each record requires exactly:

```text
id, name, locator, relationship, observed_at, status, category_language,
trust_conventions, offer_conventions, visual_patterns, strengths,
strategic_consequence, evidence_ids, limitations
```

- ID: `COMP-###`
- relationship: `direct_competitor|substitute|inaction|category_benchmark`
- status: `observed|unavailable|not_applicable`

Observed records require a concrete named entity, dated evidence, and a strategic consequence. An applicable competitive module requires at least one observed competitor or an evidenced unavailable record that keeps the module partial or blocked.

Every observed named competitor except inaction must reference at least one `competitor_evidence` source that identifies the exact sample by name or locator in its metadata or captured artifact. Bundled evidence must use a referenced manifest that explicitly maps every competitor to its capture. Each observed sample must contain a source-specific canonical evidence profile; exact duplicate observation profiles across different named competitors are invalid because they erase which entity demonstrated which strength.

### Material limitations

Each limitation requires `id`, `description`, `status`, `completion_requirement`, and `affected_module_ids`. ID is `LIMIT-###`; status is `open|resolved`.

Open material limitations, material blocked/partial access, defining or high blocked/partial/not-tested modules, unfinished available work, or unverified material production revision prevent a complete verdict.

### Narrative reconciliation

Every narrative file from `00` through `08` requires at least one reconciliation row with `location`, `finding_ids`, and `non_actionable_explanation`. Rows with findings use null or `None` explanation. Rows without findings require a concrete passed-check, context, assumption, limitation, or not-applicable explanation. Narrative prose containing a recommendation or implementation direction must reconcile to at least one canonical finding; a generic “non-actionable” explanation cannot hide an action.

For narratives `01` through `08`, list only findings materially addressed in that file and include each mapped finding ID literally in the narrative. The executive verdict may summarize the complete register. Blanket mappings that attach every finding to every narrative are not traceability.

## Generated files and validation

Render and validate:

```bash
python3 <skill-directory>/scripts/render_handoff.py <brand-teardown-directory>
python3 <skill-directory>/scripts/validate_brand_teardown.py <brand-teardown-directory>
```

The validator rejects missing files; wrong schemas; invalid or malformed nested fields; duplicate IDs; stale volatile evidence; unreconciled evidence, claims, modules, samples, and narratives; unsupported factual claims; competitor conclusions without evidence; false complete states; missing retained strengths; generic findings; dependency and phase errors; subjective severity inflation; contradictory evidence without a finding or claim record; implementation/outcome conflation; and generated Markdown drift.

## Future revision boundary

The handoff is implementation-ready but grants no approval. A future `brand-revision` skill may:

- implement only owner-approved findings and resolved strategic decisions;
- preserve authentic voice, recognizable identity, verified proof, working conversion paths, accessibility, SEO, and project constraints;
- revalidate every finding and current claim before editing;
- keep implementation evidence separate from audience and business outcomes;
- never claim improved recall, trust, preference, conversion, or revenue from implementation alone.
