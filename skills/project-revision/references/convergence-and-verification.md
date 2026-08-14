# Convergence and Verification

Use this reference after implementation planning and whenever a follow-up review changes shared or risk-sensitive code.

## Contents

1. Convergence loop
2. Review-source coverage
3. Risk-triggered verification
4. Test and verification integrity
5. Readiness decisions
6. Finalization sequence

## 1. Convergence loop

Run this loop after the approved teardown findings have an initial implementation:

1. Freeze and identify the product state under review: immutable revision when available, otherwise exact working-tree inventory.
2. Review the complete product diff against the baseline, not only the latest patch.
3. Trace cross-finding interactions through shared configuration, path resolution, process execution, persistence, recovery, provider, UI, and delivery code.
4. Exercise affected user workflows end to end.
5. Collect actionable leads from every available review source.
6. Revalidate each lead against the current state and assign a `REV-<NNN>` disposition.
7. Reopen an original finding when the lead proves its acceptance criteria were not met.
8. Fix confirmed work in dependency and severity order; add focused regression and failure-path coverage.
9. Re-run focused checks, full affected workflows, and a fresh diff review.
10. Repeat after every fix that changes shared, security-sensitive, destructive, platform-specific, or recovery code.

Stop only when no confirmed critical/high/medium convergence finding remains unresolved. Green CI is evidence inside the loop, not a substitute for it.

## 2. Review-source coverage

When a pull request or review system exists, inspect:

- current head and base;
- inline threads, including resolved and outdated state;
- top-level comments and submitted reviews;
- outside-diff and collapsed findings;
- skipped-file, ignored-path, rate-limit, partial-review, and stale-head notices;
- check runs, workflow jobs, and platform matrices;
- review suggestions generated before later commits.

Revalidate rather than bulk-applying prompts. A resolved thread can still contain an incomplete fix. A suggestion can already be satisfied by a different implementation. A review can claim success while skipping files or reviewing an older head.

If external review is unavailable, rate-limited, or unauthorized:

1. Record the source as unavailable or partial.
2. Perform a manual full-diff adversarial review.
3. Do not claim the external source passed.
4. Keep merge readiness not-ready if adequate review coverage cannot otherwise be established for the risk.

## 3. Risk-triggered verification

Apply only the rows touched by the revision, but cover each applicable failure class.

| Risk surface | Required behavioral evidence |
| --- | --- |
| Destructive restore, migration, undo, or replacement | Failure before mutation, failure during replacement, rollback failure handling, retained recovery path, success path, preserved exclusions |
| Startup maintenance or background cleanup | Malformed entry, unreadable entry, disappearing entry/race, partial failure, startup still available |
| Filesystem or workspace boundary | Absolute/relative escape, symlink escape and cycle, protected paths, missing/non-regular files, oversized and binary content, high file counts |
| User-controlled parser or regex | Invalid syntax, adversarial complexity, size/depth limits, Unicode/encoding, clear errors, bounded runtime or linear-time implementation |
| Process execution | Timeout, cancellation before/during launch, descendant termination, output bounds, launch failure, no unsafe fallback, quoting and environment behavior |
| Platform-specific branch | Execute behavior on the actual supported platform or a faithful environment; compilation alone is insufficient |
| Network or provider protocol | Timeout, malformed response/stream, authentication absence, retry exhaustion, context overflow, cancellation, deterministic mock plus declared live coverage |
| Persistence and sessions | Permissions, corruption, redaction limits, retention, deletion, legacy compatibility, concurrent/racy access |
| Approval or safety UI | Exact operation preview, bounded rendering, binary/secret handling, bypass modes, catastrophic path, noninteractive behavior |
| Browser UI, responsive behavior, or accessibility | Exercise each affected entry point and primary journey in supported browsers and real devices or faithful device environments; include navigation, overlays, keyboard/focus, errors, results, submission, and narrow/wide layouts as applicable |
| PWA or installable behavior | Manifest identity and shortcuts, service-worker output and registration, install/update/uninstall, caching boundaries, offline behavior, and stale-client recovery on supported environments |
| Operational documentation, metadata, or public claims | Runtime and dependency versions, route inventories, analytics/telemetry claims, feature availability, manifests, titles/descriptions, setup instructions, and generated output must agree with current behavior |
| Packaging, CI, or release claims | Clean install, supported runtime matrix, package contents, version facts, audit, ignored/generated files, workflow credential boundaries |

Prefer deterministic fault seams over flaky timing or host-permission assumptions. When a required environment is unavailable, verify fail-safe behavior, preserve the positive check as blocked, and describe the consequence. Never turn a safe failure into positive capability evidence.

For platform matrices, distinguish:

- build evidence;
- unit evidence;
- actual branch execution;
- end-to-end user workflow evidence.

Report the strongest level achieved for each platform. Do not summarize all four as “platform tested.”


## 4. Test and verification integrity

Do not weaken assertions, remove failure-path coverage, increase timeouts without evidence, mock away the behavior under review, or narrow the supported matrix merely to make checks pass. A test change is valid only when current product requirements or a corrected test premise justify it. Record the old premise, new premise, and evidence.

For every implemented or fixed finding:

- prefer a reproducing regression test before or alongside the fix when feasible;
- verify the behavior at the lowest useful level and through the defining user workflow;
- keep deterministic fault seams for timeouts, races, I/O failures, cancellation, cleanup, and external protocol errors;
- execute platform-specific branches on the actual platform or a faithful environment;
- rerun from a clean install/build state when packaging, dependency, generated-output, or environment behavior changed;
- inspect skipped, quarantined, retried, or conditionally excluded tests as possible hidden failures.

A green suite obtained by reducing meaningful coverage is a regression, not convergence.

## 5. Readiness decisions

Assess separately:

- **Revision status:** Whether approved teardown work and required evidence are complete.
- **Merge readiness:** Whether integration is safe now, regardless of whether merging is authorized.
- **Release readiness:** Whether users should receive or depend on this state now.
- **Delivery state:** What was actually committed, pushed, reviewed, merged, deployed, or released.

A partial revision can be merge-ready when remaining evidence requires unavailable external credentials or environments, the implemented behavior fails safely, product claims are narrowed, integration does not conceal risk, and no blocking convergence defect remains.

A revision is not merge-ready when any of these apply:

- confirmed critical/high/medium convergence defect is open, deferred, or blocked;
- an original approved acceptance criterion fails in the integrated state;
- destructive or security-sensitive behavior lacks a safe failure boundary;
- required current-head review coverage is materially incomplete without an adequate manual substitute;
- baseline user work is unreconciled;
- artifact, source, CI, and PR claims materially disagree.

Release readiness normally additionally requires complete revision status, release-critical live/environment evidence, accurate public claims, and required operational authorization. Merge readiness does not imply release readiness.

## 6. Finalization sequence

Use the smallest applicable sequence.

### Uncommitted or no commit authority

1. Finish product changes and convergence.
2. Record `implementation_end_revision` as an explicit working-tree state based on the immutable baseline.
3. Set artifact relationship `working-tree`.
4. Generate and validate the artifact.
5. Report exact uncommitted inventory and do not claim commit or push.

### Authorized committed workflow

1. Finish all product changes and convergence.
2. Run product verification.
3. Commit the final product code.
4. Record that immutable commit as `implementation_end_revision`.
5. Update and validate only revision artifacts.
6. Commit the artifact-only descendant.
7. Make no product-code change after the recorded endpoint. If one is needed, return to step 1 and refresh the artifact again.
8. Run final checks and CI against the resulting head.
9. Refresh external PR description, current head, review state, CI run, test counts, readiness, and delivery facts when authorized.

Do not require a file inside a commit to contain that commit's own hash; that is self-referential and impossible. The artifact records the product-code endpoint. The externally observable final head can be stated in mutable PR metadata or a later handoff observation.

When preserving the artifact's recorded commit matters, recommend a normal merge commit rather than squash or rebase. Squash and rebase rewrite the recorded product history unless the owner explicitly accepts that loss of provenance.
