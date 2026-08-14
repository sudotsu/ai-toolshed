# Product Testing Matrix

Use this reference after inventorying the product. Apply every relevant section and record each applicable row in `07-review-coverage.md`. A category is not complete because one happy path passed.

## Contents

1. Universal workflow checks
2. Web applications and PWAs
3. CLIs and coding agents
4. APIs and backend services
5. Desktop and mobile applications
6. Libraries, SDKs, and packages
7. AI-enabled behavior
8. Cross-platform and environment claims
9. Destructive and high-risk behavior

## 1. Universal workflow checks

For each defining and major workflow, test or explicitly block:

- clean installation or first access;
- first-run onboarding and configuration;
- ordinary successful completion;
- empty state and first-use state;
- invalid, malformed, oversized, and boundary input;
- permission denial and missing prerequisites;
- partial success and partial persistence;
- cancellation, interruption, timeout, retry, and resume;
- network loss or unavailable dependency;
- duplicate submission or repeated execution;
- stale state, concurrent state, and recovery after restart;
- undo, rollback, deletion, export, and account removal when applicable;
- help, diagnostics, support, upgrade, and uninstall paths.

Record actual outputs, exit states, persistence effects, and recovery behavior. Do not replace behavioral evidence with source inspection when execution is possible.

## 2. Web applications and PWAs

Cover:

- supported browsers and at least one non-default engine when claimed;
- responsive layouts at narrow phone, large phone, tablet, laptop, and wide desktop widths;
- keyboard-only navigation, visible focus, focus order, focus trapping, and escape behavior;
- landmarks, headings, labels, names, descriptions, errors, live regions, contrast, zoom, and reduced motion;
- route entry, refresh, deep linking, back/forward behavior, redirects, canonical URLs, and not-found handling;
- forms: validation, autofill, duplicate submission, failure recovery, spam/abuse controls, delivery, and durable receipt;
- loading, skeleton, empty, success, warning, partial, and error states;
- authentication, authorization, session expiry, password/reset, and account deletion when present;
- cache behavior, service workers, installability, offline claims, update behavior, and stale assets;
- performance on first load and repeat load, including image/font/script weight and interaction latency;
- metadata, structured data, sitemap/robots behavior, social previews, and analytics claims;
- privacy notice, consent behavior, data retention, third-party requests, and sensitive data exposure.

A generated Lighthouse score is supporting evidence, not a substitute for keyboard use, real workflow execution, or network inspection.

## 3. CLIs and coding agents

Cover:

- install from the documented distribution path and from a clean packed artifact when release claims exist;
- first run with no configuration, valid configuration, malformed configuration, and conflicting configuration sources;
- help, version, examples, exit codes, stdout/stderr separation, non-interactive use, piping, redirection, and automation;
- terminal widths, non-TTY input, EOF, SIGINT/SIGTERM, cancellation, timeout, and child-process cleanup;
- shell quoting and argument preservation on every claimed platform;
- path handling, symlinks, traversal, protected paths, large trees, binary files, unusual filenames, and permission failures;
- tool approval, preview, denial, retry, rollback, and recovery after partial writes;
- session save/load, schema drift, corruption, permissions, redaction, context pruning, token limits, and provider errors;
- package contents, ignored/generated files, upgrade behavior, compatibility ranges, and uninstall expectations;
- unsafe or bypass modes, sandbox availability, fail-closed behavior, scope boundaries, egress, and audit evidence.

A Linux build does not validate native Windows command behavior. WSL does not substitute for native Windows when the product claims both.

## 4. APIs and backend services

Cover:

- documented startup, migrations, seed data, health checks, and shutdown;
- authentication and authorization at object, route, and action boundaries;
- schema validation, content types, pagination, filtering, sorting, idempotency, and versioning;
- rate limits, abuse controls, replay, duplicate requests, and concurrency;
- transaction boundaries, partial failure, retries, queues, dead letters, and recovery;
- timeouts, backpressure, resource exhaustion, dependency outage, and degraded mode;
- logging, metrics, tracing, secret redaction, audit events, and actionable diagnostics;
- backup, restore, migration rollback, retention, deletion, and data export;
- deployment configuration, environment separation, CORS, headers, TLS assumptions, and supply-chain controls.

## 5. Desktop and mobile applications

Cover:

- clean installation, permissions, first launch, update, downgrade, and uninstall;
- window sizes, scaling, orientation, keyboard, pointer, touch, screen reader, and system appearance;
- backgrounding, suspension, resume, low memory, low storage, offline behavior, and interrupted updates;
- file associations, deep links, notifications, clipboard, local storage, and OS integration;
- platform-specific signing, packaging, permissions, sandboxing, and distribution claims.

Use real devices or supported platform runners for behavior that emulation cannot establish. Record when only an emulator or source inspection was available.

## 6. Libraries, SDKs, and packages

Cover:

- clean consumer installation using supported package managers and runtime versions;
- documented imports, module formats, types, tree shaking, side effects, and generated artifacts;
- public API behavior, error contracts, backwards compatibility, and deprecation paths;
- minimal examples compiled and executed outside the source repository;
- package metadata, license, provenance, source maps, declaration files, and release automation;
- unsupported runtime and peer dependency behavior.

## 7. AI-enabled behavior

Cover:

- deterministic harnesses before expensive or credentialed live runs;
- every claimed provider/model profile, or an explicit blocked matrix;
- streaming, malformed chunks, partial tool calls, retries, rate limits, context overflow, and provider-specific errors;
- prompt injection, untrusted retrieved content, tool authority, data egress, secret handling, and scope enforcement;
- hallucinated tool arguments, invalid schemas, repeated actions, loops, cancellation, and recovery;
- session/context persistence, summarization drift, truncation, token accounting, and reproducibility;
- representative task suites with stored inputs, outputs, versions, success criteria, costs, turns, failures, and human intervention;
- factual claims about model/provider capability matched to the exact version tested.

A single successful demo is not evidence of reliable agent behavior.

## 8. Cross-platform and environment claims

Create a claim-to-evidence matrix for every supported runtime, browser, operating system, architecture, provider, deployment target, and package format.

Use these evidence levels:

- `behavioral`: workflow executed in the claimed environment;
- `build-only`: compiled or packaged there but behavior not exercised;
- `source-only`: inspected platform branch or configuration;
- `blocked`: environment unavailable or failed before the target behavior;
- `not-tested`: no attempt made.

Never describe build-only or source-only evidence as platform support verification.

## 9. Destructive and high-risk behavior

Use disposable data, repositories, accounts, devices, sandboxes, or snapshots. Test:

- explicit scope and authorization boundaries;
- confirmation quality and preview accuracy;
- cancellation before and during execution;
- partial failure and recovery;
- rollback integrity and preservation of unrelated work;
- audit trail, provenance, and evidence export;
- fail-closed behavior when containment, credentials, or prerequisites are unavailable.

Do not execute a live destructive action merely to improve coverage. Record the safe substitute and remaining uncertainty.
