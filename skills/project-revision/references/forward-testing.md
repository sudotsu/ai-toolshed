# Forward-Testing Protocol

Use this protocol when changing the revision contract, the planning contract, the
validators, or the generated views. Unit tests prove the validators accept and
reject synthetic shapes; only a forward test proves the skill can carry a real
teardown through to a converged, auditable implementation.

## What counts as a forward test

Distinguish three evidence levels and never present a weaker one as a stronger one:

| Level | What it proves | Acceptable as release evidence |
| --- | --- | --- |
| **Schema fixture** | The validator accepts or rejects a synthetic payload | No, on its own |
| **Canonical artifact replay** | A previously produced real revision still validates against its teardown, and generated views still render byte-identically | Yes, for contract or renderer changes |
| **Full behavioral forward test** | A fresh agent, given a real teardown and owner decisions, implemented approved findings and converged without weakening a rule | Required before declaring the skill improved |

## Test selection

Use at least two materially different teardown shapes, for example:

- A teardown with a genuine owner decision, at least one blocked finding, and a
  retained strength — the case where approval and preservation rules bind.
- A teardown whose findings have real dependencies and at least one finding that
  revalidation proves stale — the case where sequencing and revalidation bind.

Prefer a teardown produced by `project-teardown` on a real project, plus that
project's repository. **Preserve pre-existing uncommitted work**; a revision run
that silently discards it has failed regardless of validator output.

## Prompt discipline

Give the agent the teardown path, the project, the owner approval matrix, and the
operating mode. Do not reveal which findings you expect to be implemented,
deferred, or found stale. Do not hint at convergence findings. A forward test that
supplies the answers measures instruction-following, not revision quality.

## Evaluation rubric

Judge each output on:

- Every teardown finding covered exactly once with an explicit disposition.
- Revalidation performed against current head, not restated from the teardown.
- Approval, revalidation, and disposition combinations that satisfy the contract
  without any rule being relaxed to make validation pass.
- Changed-path attribution complete, with pre-existing work provably intact.
- Convergence findings raised from real review, with honest blocking counts.
- Provisional or blocked status used honestly rather than forced to complete.
- Generated views byte-identical to a fresh render from `revision.json`.
- Acceptance criteria genuinely evaluated, not marked passed by assertion.

## Failure-driven improvement

When a forward test exposes a weakness, fix the **skill**, not the test project,
not the teardown, and not the rubric. Add a regression test that fails against the
previous behavior. Never encode a specific project's expected findings into a
validator or a reusable test — the validators must stay project-agnostic.

## Recording evidence

Every forward test recorded as release evidence must state:

- the skill revision under test (commit SHA);
- the source teardown, its audited revision, and its `findings.json` SHA-256;
- the implementation start and end revisions of the target project;
- the exact commands run, including both validators and the renderer;
- the validator result verbatim;
- SHA-256 of `revision.json` produced;
- the disposition of any independent review, including rejected leads;
- which evidence level above was achieved, and what remained untested.

Store the record under `evidence/` in the revision handoff, sanitized. Never copy
secrets, credentials, private data, or production dumps. A forward test whose
evidence cannot be independently re-derived from that record is not release
evidence.
