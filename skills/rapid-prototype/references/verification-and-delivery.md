# Verification and delivery: demo evidence is not release evidence

Load before declaring completion or creating a public preview. Apply only checks relevant to the promised proof, but do not omit the defining journey. This is a *selective demo checklist*, not a mandate for full production certification.

## Evidence ladder

Report checks separately; never convert one into another:

| Level | Evidence | Permitted claim |
| --- | --- | --- |
| V1 | Viewer interaction observed on actual local/device or isolated preview: entry → action → output, with relevant runtime observations | This named journey worked in this named environment at this revision |
| V2 | Actual test provider/database effect observed (and optionally repeated from another session/device when central to claim) | That specific test integration/persistence action worked |
| V3 | Automated focused test passed with the exact command and revision | Tested behavior passed under test conditions |
| V4 | Typecheck/build/lint passed | Code compiled/checked; no viewer outcome implied |
| V5 | Source/diff inspection only | Implementation is present but behavior is unverified |
| BLOCKED | Needed evidence could not be gathered | State precisely what is blocked and why |

A screenshot can establish appearance at one instant, not that controls, persistence or backend side effects work. A browser check on localhost does not prove the deployed URL works. A deploy success log does not prove the live page behaves as intended. A green PR CI check does not equal a passed runtime-agent behavioral evaluation.

## Minimal viewer-path checks

Make the proof measurable: opening path, primary action, expected result, important failure mode and observed evidence. Use synthetic, bounded, repeatable test data.

| Surface | Minimum when relevant |
| --- | --- |
| Visual website | Initial page, link/nav, primary CTA, readable hierarchy, meaningful output, narrow viewport, no broken media |
| Stateful app | Initial/empty state, selection or input, validation, loading or response feedback, changed state, reload only if persistence claimed |
| API-backed journey | Real request/response, error/timeout representation and resulting test data only if claimed |
| Integration | Sandbox or test account with inspected outcome; disclose anything still a fixture |
| Authentication/permissions | Test account/access checks if security is central; do not call hidden UI secure |
| Accessibility | Keyboard-reachable defining action, perceivable labels/focus, readable contrast and sensible error text |
| Reliability | At least one critical error/negative path without uncaught failure; no obvious console or network regressions |
| Privacy/security | Synthetic data, no secrets/PII in client bundle, output, fixtures, commits, screenshots or logs |
| Changeset | Final diff and status show only intended paths; note existing uncommitted work and unintended churn |

When a browser/device or build tool is unavailable, do what the available environment can prove, mark omitted checks as unrun, and do not manufacture screenshots or success.

## Preview environment check

A branch-named URL or provider-generated preview may still have production connections. Before a preview which can execute code or write data:

1. Confirm it is an isolated, intended destination and inspect environment scope where tools permit.
2. Check database URL, webhooks, storage, auth callbacks, secrets, cron/jobs, mail/SMS, payment mode and feature flags relevant to this build.
3. Disable outbound/live effects or use safe sandbox accounts and synthetic data.
4. Avoid accidental spend or public exposure. Verify share/access settings if a demo contains client-sensitive content.
5. Open the *actual preview URL*, run the defining path and record the deployed revision.

If separation cannot be established, do not execute the risky preview. Keep a local build or inert artifact and report the gap.

## Handoff and rollback protocol

Record:
- Baseline revision and final branch/commit/PR, and whether PR is unmerged.
- Viewer URL/path and exactly what was personally exercised and observed.
- Check commands, results and their environment; mocked elements and unverified claims.
- Preview location, mode and any external side effects: test database row, uploaded object, sent *test* notification, allocated resource, etc.
- Least destructive rollback for the *actual change*: abandon unmerged branch/PR, revert only owned commit(s) if integrated under separate approval, and separately delete/disable previews, seeded records or external resources where authorized. Never assume deleting source/closing a PR cancels an external resource.
- One concrete next owner action, only if needed.

Keep the terms apart:
- **Implemented:** source change exists at reported ref.
- **Verified demo:** named journey exercised with evidence.
- **Review ready:** isolated PR/diff ready for review, not merged.
- **Release ready:** production-specific controls and checks separately satisfied (not established by this skill alone).
- **Deployed preview:** actual URL confirmed; not equivalent to production release.
- **Production changed:** state explicitly yes/no/unknown from inspection, not by assumption.

If any required proof is blocked, say **partial/blocked**, preserve the artifact, and identify the one highest-leverage follow-up. A successful demo does not imply scalability, operational resilience, regulatory/payment readiness, secure multi-tenancy, or correctness outside the demonstrated path.
