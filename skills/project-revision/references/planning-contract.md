# Planning-Only Revision Contract

Use this contract when the owner requests revalidation, a decision packet, an implementation plan, or a plain-language revision document without authorizing product edits.

## Contents

1. Planning boundary
2. Required markers
3. Required sections
4. Traceability ledger
5. Delta from the original teardown
6. Owner decisions
7. Completion gates and blocked evidence
8. Validation

## 1. Planning boundary

Planning-only work may inspect the current project, rerun safe checks, and create or update the requested planning document. It must not:

- edit product code, tests, configuration, manifests, deployment files, or operational content;
- create an implementation or convergence ledger that implies work was performed;
- mark findings implemented or fixed;
- claim convergence, merge readiness, release readiness, deployment, publication, or production verification;
- silently convert an agent recommendation into an owner decision.

When the user says to update only one named document, modify only that document. Do not add a sidecar artifact unless the owner requests one.

## 2. Required markers

Place these near the top of the planning document using exact labels:

```text
**Artifact mode:** planning-only
**Product edits performed:** no
**Convergence testing performed:** no
**Teardown review status:** complete
**Teardown finding count:** 23
**Current revision checked:** <immutable revision or explicit working-tree state>
```

`Teardown review status` and `Teardown finding count` must match `findings.json`.

## 3. Required sections

Include:

- `## Purpose and boundary`
- `## Current-state revalidation`
- `## Delta from the original teardown`
- `## Owner decisions required`
- `## Proposed implementation sequence`
- `## Traceability ledger`
- `## Blockers and completion gates`
- `## What was not done`

The document may use additional audience-specific sections, but these exact sections must remain.

## 4. Traceability ledger

Give every teardown finding exactly one section using its original ID and title:

```markdown
### TECH-001 — Repair behavior

- **Teardown status:** open
- **Teardown verification state:** defect-conclusively-demonstrated
- **Revalidation:** confirmed
- **Plan treatment:** implement
- **Dependencies:** None
- **Owner decision:** None
- **Blocker or completion gate:** None
- **Acceptance criteria carried forward:** criterion one | criterion two
- **Verification carried forward:** exact verification from the teardown
- **Affected surfaces carried forward:** src/example.ts | CLI failure path | Windows runner
- **Plan action:** concrete current implementation action
- **Notes:** None
- **Teardown record digest:** sha256:<digest of the original teardown finding>
```

Allowed `Plan treatment` values:

- `implement`
- `owner-decision`
- `investigate`
- `blocker`
- `defer`
- `accepted-risk`
- `retain`
- `no-action`

Allowed `Revalidation` values:

- `confirmed`
- `changed`
- `stale`
- `already-resolved`
- `not-applicable`
- `blocked`

Requirements:

- Preserve the exact teardown status, dependencies, acceptance criteria, verification, affected components, and record digest.
- When an original criterion is vague, keep it verbatim and place any non-material measurable clarification in `Plan action` or `Notes`. If scope, behavior, authority, risk, or owner commitment changes, use `owner-decision`.
- Use `owner-decision` when implementation behavior, risk, scope, conflict, or authority still requires an owner choice.
- Use `blocker` when evidence or environment prevents a valid implementation commitment.
- Use `retain` for strengths and retain actions.
- Use `no-action` only for stale, already-resolved, or not-applicable findings and explain why.
- A changed finding must explain the changed premise and whether it creates a genuinely new finding.
- Specific affected runtime, configuration, manifest, metadata, operational-documentation, delivery, user-facing, platform, browser, provider, device, accessibility, security, and failure-path surfaces from the handoff must remain visible.

The bundled validator verifies ID coverage, status, dependencies, acceptance criteria, verification, affected components, and digest. It cannot determine whether the prose plan action is substantively good; manually review that.

## 5. Delta from the original teardown

Use these exact subsections:

```markdown
### Teardown recommendations translated or reorganized

### New implementation or sequencing recommendations

### Genuinely new findings from current-state revalidation
```

Rules:

- A clearer explanation, grouping, dependency order, or implementation suggestion is not a new finding.
- New implementation recommendations must remain recommendations until approved.
- A genuinely new finding requires current evidence, impact, scope, and a new stable ID outside the original teardown ID set.
- If no new findings were discovered, state `No genuinely new findings were discovered.` exactly.

## 6. Owner decisions

For each unresolved owner decision, provide:

- exact question;
- concrete options;
- recommendation;
- consequences and tradeoffs;
- affected finding IDs;
- dependencies;
- default of no change when unanswered.

Preserve owner decisions already provided. Do not ask again or relabel them as recommendations. Retained strengths default to preservation and do not require a separate owner answer unless a proposed change threatens or trades off that strength. A plan may cover a narrowly approved subset, but every untouched finding must remain explicitly traced and deferred or otherwise disposed.

## 7. Completion gates and blocked evidence

Carry forward every:

- provisional limitation;
- blocked investigation;
- unexercised defining workflow;
- required live-provider or external-system check;
- real-device, browser, operating-system, platform, accessibility, security, production, delivery, migration, or failure-path check;
- credential, account, evidence, or authority prerequisite.

Each must appear as a specific blocker or observable completion gate. Generic phrases such as “test mobile,” “check accessibility,” or “update documentation” are insufficient when the teardown names concrete surfaces.

## 8. Validation

The `## What was not done` section must include these exact statements:

```text
No product code, tests, configuration, manifests, deployment files, or operational content were edited.
No implementation convergence testing was performed.
```

Run:

```bash
python3 <skill-directory>/scripts/validate_revision_plan.py <project-teardown-directory> <planning-document.md>
```

Fix all structural and traceability errors. Validator success does not authorize implementation and does not prove convergence. Skill-bundle validation and regression tests are maintenance-only, not planning completion gates.
