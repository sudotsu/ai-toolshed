# Forward-Testing Protocol

Use this protocol when changing the skill contract, the report contract, the
validator, or the generated views. Unit tests prove the validator accepts and
rejects synthetic shapes; only a forward test proves the skill produces a useful
teardown of a real project.

## What counts as a forward test

Distinguish three evidence levels and never present a weaker one as a stronger one:

| Level | What it proves | Acceptable as release evidence |
| --- | --- | --- |
| **Schema fixture** | The validator accepts or rejects a synthetic payload | No, on its own |
| **Canonical artifact replay** | A previously produced real teardown still validates and its generated views still render byte-identically | Yes, for contract or renderer changes |
| **Full behavioral forward test** | A fresh agent, given only a project locator, produced a teardown that validates and is materially useful | Required before declaring the skill improved |

## Test selection

Use at least two materially different project shapes, for example:

- A small application with a single defining workflow, a real user, and limited
  test coverage — the case where a teardown must avoid manufacturing findings.
- A larger codebase with multiple runtimes, external services, or platform
  claims — the case where coverage accounting and provisional status matter.

A repository plus a running instance is preferred. Representative artifacts are
acceptable when access is limited; record the limitation. **Never modify the test
project.** The teardown must leave it byte-identical.

## Prompt discipline

Give the agent only the project locator, the allowed access, the read-only
boundary, and the request to use `project-teardown`. Do not reveal expected
findings, known defects, severity expectations, or scoring criteria inside the
prompt. A forward test that names the answer measures instruction-following, not
audit quality.

## Evaluation rubric

Judge each output on:

- Whether every defining workflow was actually exercised, not merely inspected.
- Separation of runtime observation, test evidence, source inspection, external
  research, owner-provided fact, and inference.
- Correct use of `confidence` versus `verification_state` as independent axes.
- Useful findings versus manufactured or restated ones.
- Honest `provisional` status when a defining or required surface is untested.
- Finding specificity: reproduction, consequence, acceptance criteria, verification.
- Dependency graph correctness and an executable implementation sequence.
- Agreement between `findings.json` and every generated Markdown view.
- Preservation: strengths retained, nothing actionable silently dropped.

## Failure-driven improvement

When a forward test exposes a weakness, fix the **skill**, not the test project
and not the rubric. Add a regression test that fails against the previous
behavior. Never encode a specific project's expected findings into a validator or
into a reusable test — the validators must stay project-agnostic.

## Recording evidence

Every forward test recorded as release evidence must state:

- the skill revision under test (commit SHA);
- the audited project and its exact revision;
- the exact commands run, including validator and renderer invocations;
- the validator result verbatim;
- SHA-256 of each canonical artifact (`findings.json`) produced;
- the disposition of any independent review of the output;
- which evidence level above was achieved, and what remained untested.

Store the record under `evidence/` in the teardown handoff, sanitized. Never copy
secrets, credentials, private data, or production dumps. A forward test whose
evidence cannot be independently re-derived from that record is not release
evidence.
