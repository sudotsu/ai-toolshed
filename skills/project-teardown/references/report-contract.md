# Teardown Report Contract

## Contents

1. Required folder and source-of-truth rules
2. Executive verdict
3. Product and market
4. User experience
5. Technical audit
6. Security and reliability
7. Canonical findings and generated register
8. Implementation sequence
9. Review coverage
10. Claims inventory
11. Final integrity pass

## 1. Required folder and source-of-truth rules

Create this structure. Additional evidence or domain-specific artifacts may be added, but these files are mandatory for new schema-version-3 reports.

```text
project-teardown/
├── README.md
├── 00-executive-verdict.md
├── 01-product-and-market.md
├── 02-user-experience.md
├── 03-technical-audit.md
├── 04-security-and-reliability.md
├── 05-findings-register.md
├── 06-implementation-sequence.md
├── 07-review-coverage.md
├── 08-claims-inventory.md
├── findings.json
└── evidence/
```

`findings.json` is the canonical findings source. Do not manually maintain duplicate finding records. Generate `05-findings-register.md` and `README.md` after the final JSON edit:

```bash
python3 <skill-directory>/scripts/render_findings.py <project-teardown-directory>
python3 <skill-directory>/scripts/render_readme.py <project-teardown-directory>
```

The validator requires exact generated output for schema version 3. This preserves the full implementation contract while removing redundant manual authoring and hand-calculated digests.

Keep evidence compact and safe. Store screenshots, sanitized logs, command results, benchmark notes, network summaries, and other supporting artifacts in `evidence/`. Never copy secrets, unredacted private data, session cookies, or production dumps.

New reports use `findings.json` schema version 3. The validator continues to read legacy schema versions 1 and 2 so previously validated teardowns can still feed `project-revision`.

## 2. `00-executive-verdict.md`

Include:

- `**Review status:** complete` or `**Review status:** provisional` near the top;
- product thesis, intended users, maturity, and audited revision;
- plain-language overall verdict;
- current trajectory: leading, competitive, catching up, undifferentiated, outdated, or heading for a wall, with qualifications;
- strongest qualities worth preserving;
- critical blockers and highest-leverage opportunities;
- best-in-class gap and realistic owner/team ceiling;
- owner decisions required;
- review scope, environment, research date, limitations, and material assumptions.

Use `provisional` whenever a defining workflow or required evidence source remains blocked, partial, or untested strongly enough to change the verdict or plan. State exactly what would complete the review.

A confirmed defect may remain conclusive even when an adjacent production transport or third-party operation is unverified. Do not blur those facts. Use the finding and coverage verification states to distinguish them.

## 3. `01-product-and-market.md`

Include benchmark selection and rationale, current landscape evidence, product thesis, feature-value analysis, strategic classifications, contradictions, differentiation, missing capabilities, questionable or obsolete capabilities, business/adoption constraints, and consequences of changing versus retaining each major direction.

Separate sourced market evidence from inference. Date version-sensitive research.

## 4. `02-user-experience.md`

Map tested journeys and document onboarding, information architecture, interaction quality, content, visual system, responsiveness or terminal ergonomics, accessibility, feedback states, recovery, trust, user-visible performance, and conversion or completion paths. Include passed checks and preserved strengths.

Distinguish behaviorally tested surfaces from screenshots, source-only inspection, or assumptions.

## 5. `03-technical-audit.md`

Cover architecture, correctness, maintainability, dependencies, performance, resource limits, state and data behavior, concurrency, tests, build and delivery, configuration, observability, documentation, packaging, and platform-specific implementation quality. Tie conclusions to runtime evidence and source locations.

## 6. `04-security-and-reliability.md`

Cover threat-relevant surfaces, secret and data handling, authentication and authorization when applicable, unsafe defaults, trust boundaries, scope and egress, dependency exposure, failure containment, recovery, portability, destructive behavior, and operational risks.

State whether each conclusion is confirmed, likely, inferred, or requires specialized testing. Do not imply that a product teardown is a formal penetration test, legal opinion, safety certification, or compliance audit.

## 7. Canonical findings and generated register

### `findings.json`

New reports use this exact top-level shape:

```json
{
  "schema_version": 3,
  "project": "owner/project or project name",
  "audited_revision": "immutable revision or explicit working-tree state",
  "review_status": "complete",
  "core_workflows_fully_exercised": true,
  "generated_at": "ISO-8601 timestamp",
  "findings": []
}
```

Give every finding exactly these keys:

```text
id, title, type, category, severity, confidence, verification_state, status,
impact, evidence, expected_behavior, actual_behavior, root_cause,
affected_components, recommendation, if_implemented, if_unchanged,
dependencies, dependents, conflicts, acceptance_criteria, verification,
estimated_scope, regression_risk, action, strategic_classification
```

Controlled values:

- `type`: `defect`, `shortcoming`, `recommendation`, `opportunity`, `investigation`, `strength`
- `severity`: `critical`, `high`, `medium`, `low`, `informational`
- `confidence`: `confirmed`, `high`, `medium`, `low`
- `verification_state`: `behaviorally-verified`, `defect-conclusively-demonstrated`, `operationally-unverified`, `partially-verified`, `source-only`, `research-verified`, `owner-provided`, `blocked`, `not-applicable`
- `status`: `open`, `blocked`, `decision-required`, `accepted-risk`, `retained`
- `estimated_scope`: `trivial`, `small`, `medium`, `large`, `initiative`
- `regression_risk`: `low`, `medium`, `high`
- `action`: `fix`, `add`, `change`, `remove`, `investigate`, `decide`, `retain`

The two evidence dimensions are intentionally separate:

- `confidence` states how strongly the finding itself is supported.
- `verification_state` states what kind of verification was actually achieved.

Examples:

- A fake success screen reproduced in a browser can be `confirmed` and `defect-conclusively-demonstrated`, while production email routing remains a separate `operationally-unverified` or `blocked` investigation.
- A source-inspected platform branch can be high confidence but `source-only`.
- A successful real-user workflow can be `behaviorally-verified`.

Requirements:

- Store `evidence` as an array of objects with exactly `kind`, `source`, `location`, and `claim` non-empty strings.
- Store `affected_components`, `dependencies`, `dependents`, `conflicts`, `acceptance_criteria`, and `strategic_classification` as arrays of unique non-empty strings. Use an empty array when none apply.
- Use only registered finding IDs in relationship arrays.
- `dependencies` are prerequisites of the current finding; `dependents` are exact reverse links.
- Keep dependency/dependent links exact, conflicts symmetric, and the dependency graph acyclic.
- A decision may be a dependency; phase membership is not.
- A `strength` uses informational severity, retained status, and retain action.
- Status `decision-required` and action `decide` must occur together.
- A confirmed finding requires at least one evidence item.
- Critical severity requires confirmed or high confidence, non-empty evidence, catastrophic impact, and a realistic trigger.

Severity definitions:

- **Critical:** Immediate or near-certain catastrophic harm, compromise, data loss, unusability of the core product, or a fundamental blocker to release or continued operation.
- **High:** Major user harm, core-workflow failure, serious security or reliability exposure, or a strategic issue likely to defeat the product's purpose.
- **Medium:** Meaningful degradation, recurring friction, maintainability risk, or a material missed opportunity without immediate existential impact.
- **Low:** Bounded quality, polish, consistency, or edge-case issue worth resolving.
- **Informational:** Passed check, retained strength, or context that affects later decisions but requires no direct fix.

Do not use estimated scope as a proxy for severity.

The bundled `references/schemas/findings.schema.json` is an editor/interoperability schema. The Python validator remains normative because it enforces graph, coverage, claims, generated-view, and cross-file rules.

### `05-findings-register.md`

This is the generated human-readable view of `findings.json`, not a second manually authored source of truth.

Generate it with `scripts/render_findings.py`. The renderer includes every field, complete evidence summaries, and the SHA-256 digest of each canonical finding object. Manual edits are rejected because they would reintroduce drift.

### `README.md`

This is the generated entry point. It identifies the project, revision, review status, finding counts, highest-priority findings, reading order, and validation commands. Generate it with `scripts/render_readme.py`.

## 8. `06-implementation-sequence.md`

Create an ordered, dependency-aware plan rather than copying severity order. Include:

1. decisions and investigations that unblock planning;
2. safety, data integrity, and foundational fixes;
3. root causes that unblock or supersede downstream findings;
4. core workflow and high-severity improvements;
5. product and UX changes;
6. lower-severity refinements and cleanup;
7. deferred initiatives, retained strengths, and explicit accepted risks.

For each phase list finding IDs, rationale, prerequisites, parallelizable groups, conflicts, validation gates, and expected user/business outcome. Explicitly note findings superseded by another change.

End with this exact section and table:

```markdown
## Coverage ledger

| Sequence | Finding ID | Planned disposition | Prerequisites | Rationale |
| --- | --- | --- | --- | --- |
| 1 | PROD-001 | decide | None | ... |
```

List every finding exactly once in executable order, whether scheduled, deferred, retained, or accepted. Every dependency must occur earlier than its dependent.

## 9. `07-review-coverage.md`

Start with:

```text
**Review status:** complete
**Core workflows fully exercised:** yes
**Validator status:** passed
```

### `## Surface coverage`

Use this exact schema-version-3 table header:

```markdown
| Surface | Importance | Status | Verification class | Evidence level | Evidence | Limitations | Next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

Importance values: `defining`, `required`, `major`, `supporting`, `research`.

Status values: `passed`, `failed`, `partial`, `blocked`, `not-tested`, `not-applicable`.

Verification classes: `behaviorally-verified`, `defect-conclusively-demonstrated`, `operationally-unverified`, `partially-verified`, `source-only`, `research-verified`, `owner-provided`, `blocked`, `not-applicable`.

Evidence levels: `behavioral`, `test`, `build-only`, `source-only`, `research`, `owner-provided`, `mixed`, `none`.

Use the status and verification class together. A surface can be `failed` and `defect-conclusively-demonstrated`; a different operational surface can remain `not-tested` and `operationally-unverified`. Do not collapse both into a vague partial statement.

Include every defining workflow, supported platform/runtime/provider, major feature, quality domain, destructive boundary, and material research question. State exactly what would unblock blocked or unverified work.

A complete review requires every defining and required row to be `passed` or specifically justified `not-applicable`.

### `## Narrative reconciliation`

Use this table header:

```markdown
| Report section | Classification | Finding IDs | Rationale |
| --- | --- | --- | --- |
```

Include at least one row for each numbered narrative file `01` through `04`. Classification values: `actionable`, `passed-check`, `limitation`, `deferred`, `context`, or `mixed`.

Every actionable row must contain registered finding IDs. Non-actionable rows must explain why no finding is required.

### `## Finding counts`

Include `**Total findings:** <integer>` plus counts by severity, status, type, and action. The total must match `findings.json`.

### `## Validator result`

Record the exact command, timestamp, and successful output. The exact `**Validator status:** passed` marker may appear only after the project-report validator succeeds.

The review status must match the executive verdict and JSON. `Core workflows fully exercised: yes` must match `core_workflows_fully_exercised: true`.

## 10. `08-claims-inventory.md`

Inventory every material external claim, including credentials, licensing, insurance, safety, diagnosis, expertise, guarantees, response times, pricing, performance, statistics, privacy, data handling, and product capability.

Use this exact table:

```markdown
## Claims

| Claim ID | Claim text | Location | Category | Required evidence | Evidence found | Verification state | Disposition | Related finding IDs | Required action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

Claim IDs use `CLAIM-001`, `CLAIM-002`, and so on. Category values:

`credential`, `licensing`, `insurance`, `safety`, `diagnosis`, `expertise`, `guarantee`, `pricing`, `performance`, `statistics`, `privacy`, `capability`, `other`.

Verification states:

`verified`, `unsupported`, `contradicted`, `partially-verified`, `blocked`, `not-applicable`.

Dispositions:

`retain`, `qualify`, `remove`, `replace`, `investigate`, `owner-decision`, `not-applicable`.

Every unsupported, contradicted, partially verified, or blocked claim must map to at least one finding. A claim can be retained only when verified. If the project genuinely makes no material external claims, include one explicit `CLAIM-000` not-applicable row rather than omitting the artifact.

## 11. Final integrity pass

Before delivery:

1. Re-read every narrative section.
2. Give every actionable defect, shortcoming, recommendation, opportunity, investigation, and unresolved material claim exactly one finding ID.
3. Confirm every finding appears exactly once in the implementation coverage ledger.
4. Confirm dependencies, reverse dependents, conflicts, and sequence order are valid and acyclic.
5. Confirm each finding's confidence and verification state describe different dimensions accurately.
6. Confirm the coverage matrix distinguishes conclusive defect evidence from unverified operations.
7. Confirm the claims inventory includes all material claims and maps every unresolved claim to findings.
8. Confirm narrative reconciliation covers `01` through `04` and maps all actionable statements.
9. Confirm blocked or unexercised defining/required surfaces produce a provisional verdict.
10. Recheck every critical rating against the critical definition.
11. Confirm no low-severity UX, accessibility, onboarding, delivery, reliability, or polish item disappeared merely because it was low severity.
12. Generate `05-findings-register.md` and `README.md` from the final JSON.
13. Run the project-report validator and record success.
14. Manually verify substantive completeness after structural validation.
15. Confirm no product source or pre-existing user work was modified by the teardown.
