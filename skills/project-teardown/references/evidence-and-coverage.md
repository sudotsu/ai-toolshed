# Evidence and Coverage Discipline

Use this reference while testing and again before assigning confidence or declaring the teardown complete.

## Contents

1. Baseline and isolation
2. Evidence classes
3. Verification states
4. Reproduction quality
5. Current and version-matched research
6. Coverage accounting
7. Completion rules
8. Sensitive evidence handling

## 1. Baseline and isolation

Before executing project commands, capture:

- repository or project identity;
- immutable revision when available;
- branch and remote;
- staged, unstaged, and untracked inventory;
- relevant runtime, package-manager, browser, OS, and tool versions;
- existing build/test status when available.

Treat source as read-only. Prefer a disposable clone, temporary worktree, copied fixture, container, VM, or sandbox for dependency installation and generated effects. If testing in the original checkout is unavoidable:

1. record the exact baseline;
2. do not run commands known to rewrite lockfiles, format source, migrate production data, or clean the tree without permission;
3. inventory all resulting changes;
4. remove only effects proven to have been created by the teardown;
5. never reset, clean, checkout over, stash, or discard pre-existing work.

A teardown is not read-only merely because the agent did not intentionally edit source.

## 2. Evidence classes

Label evidence accurately:

- `runtime`: directly observed product behavior;
- `test`: existing automated check or purpose-built non-mutating diagnostic;
- `source`: implementation inspection;
- `configuration`: manifest, deployment, workflow, or runtime configuration;
- `artifact`: package, bundle, binary, generated output, screenshot, or recording;
- `external-primary`: official documentation, standard, research paper, vendor advisory, regulation, or first-party competitor source;
- `external-secondary`: reputable independent analysis;
- `owner-provided`: owner answer, credentialed decision, business fact, or supplied evidence;
- `inference`: conclusion derived from cited evidence but not directly observed.

Do not use an inference as the sole evidence for a confirmed finding. State the leading hypothesis when root cause is not proven.

## 3. Verification states

Record what was actually verified separately from how confident the conclusion is. Use these values for schema-version-3 findings and surface coverage:

- `behaviorally-verified`: the intended workflow completed and its observable outcome was checked;
- `defect-conclusively-demonstrated`: the failure itself was directly reproduced or proven even if an adjacent external operation remains unverified;
- `operationally-unverified`: production delivery, routing, monitoring, billing, third-party receipt, or another live operation was not verified;
- `partially-verified`: a meaningful subset was exercised, but remaining states could alter the conclusion or plan;
- `source-only`: implementation was inspected without valid behavioral execution;
- `research-verified`: a current, version-matched external claim was verified using suitable primary evidence;
- `owner-provided`: the conclusion depends on an explicit owner fact or decision that was not independently verified;
- `blocked`: a concrete prerequisite prevented valid testing;
- `not-applicable`: the verification dimension does not apply, with a specific reason.

Do not downgrade a conclusive defect merely because a separate production transport remains unavailable. Register the defect and the operational evidence gap separately when they require different actions or acceptance criteria.

## 4. Reproduction quality

A reproducible finding states:

- starting state and prerequisites;
- exact path, command, input, or interaction;
- expected behavior;
- actual behavior;
- resulting state or side effect;
- environment and revision;
- whether reproduction was repeated;
- safe evidence location.

Use minimal excerpts. Preserve the full sanitized log in `evidence/` when the excerpt could omit relevant context.

## 5. Current and version-matched research

Use external research for claims that can change, including versions, vulnerabilities, standards, laws, policies, product capabilities, pricing, platform support, market conditions, and competitors.

Establish the project's actual pinned or deployed version first. Match documentation and advisories to that version. "Current official documentation" may be wrong for an older pin; old cached guidance may be wrong for a current release.

Record source, publication/update date when available, access date, and the exact claim supported. Prefer primary sources. When sources disagree, preserve the disagreement and lower confidence instead of choosing the convenient answer.

## 6. Coverage accounting

Create the surface coverage matrix before deep testing and update it during the run. Include:

- every defining workflow;
- every major feature and route or command family;
- every supported platform/runtime/provider claim;
- every relevant quality domain;
- every material market, policy, security, or legal research question;
- every destructive or high-risk boundary.

Importance values:

- `defining`: the product's central promised outcome;
- `required`: necessary to substantiate a support, safety, release, or business claim;
- `major`: meaningful product capability or high-impact quality domain;
- `supporting`: secondary behavior or lower-risk surface;
- `research`: external question needed for product or risk conclusions.

Coverage status values:

- `passed`: tested and met expectations;
- `failed`: tested and did not meet expectations;
- `partial`: only part of the surface or evidence level was exercised;
- `blocked`: a concrete prerequisite prevented the attempt;
- `not-tested`: applicable but no valid attempt was completed;
- `not-applicable`: excluded with a specific reason.

Pair each status with a verification state. In particular:

- a reproduced broken workflow should normally be `failed` plus `defect-conclusively-demonstrated`;
- an untested live transport should be `not-tested` plus `operationally-unverified`;
- a concrete access or credential gate should be `blocked` plus `blocked`;
- a source-inspected branch without runtime evidence should use `source-only`;
- a partially exercised workflow should use `partially-verified` unless the only remaining gap is specifically operational.

## 7. Completion rules

A teardown may be `complete` only when:

- every defining workflow was fully exercised;
- every defining and required coverage row is `passed` or honestly `not-applicable`;
- blocked, partial, and untested major/supporting surfaces cannot reasonably change the overall verdict or highest-priority plan;
- all actionable observations have findings;
- all material external claims are current and version-matched;
- the report and machine handoff validate.

Otherwise use `provisional`, even when the available work is extensive.

A product may have open or blocked remediation findings while the review itself is complete. Review completeness concerns evidence coverage, not whether the product is fixed.

## 8. Sensitive evidence handling

Never store secrets, private customer data, full tokens, private keys, session cookies, unredacted personal information, or production data dumps.

Sanitize evidence at collection time. Record that redaction occurred. Prefer hashes, synthetic fixtures, bounded excerpts, and metadata over copying sensitive content. Keep raw diagnostics outside the repository in a restricted temporary location and delete them after extracting safe evidence.
