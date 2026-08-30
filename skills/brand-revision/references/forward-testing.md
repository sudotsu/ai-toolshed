# Brand Revision Forward Testing

Forward testing exists to discover hidden assumptions in the skill, not merely to demonstrate that a validator can accept its own fixtures.

## Required contrast

When materially changing the contract, validator, renderer, bootstrap behavior, authority model, or verification rules, use at least two materially different validated `brand-teardown` handoffs:

1. a local-service or other high-trust operating business with real customer journeys, claims, local identity, public channels, and preservation constraints;
2. a software/developer-product, SaaS, agency, media, ecommerce, nonprofit, or other non-local-service brand with a materially different proof and channel model.

Do not encode project-specific expected answers into the skill.

## Test layers

### 1. Contract and negative fixtures

Test at minimum:

- malformed top-level and nested JSON types;
- duplicate or missing IDs;
- wrong schema versions;
- missing teardown findings;
- changed original finding titles/dependencies/acceptance criteria;
- dependency-order violations;
- decision-required findings treated as approved without a resolved decision;
- retained strengths not preserved;
- missing or altered preservation constraints;
- blocked teardown limitations silently removed;
- claim-trace omissions;
- unsupported claim upgraded to verified without evidence;
- source/render evidence used to claim audience or business success;
- unauthorized external mutation;
- high-risk change without rollout/rollback planning;
- unresolved blocking convergence defects with ready state;
- false commit/push/merge/deploy/publish claims;
- generated Markdown drift;
- malformed nested values causing crashes.

Mutation-style tests should replace reachable fields with representative wrong JSON types and assert the pipeline returns structured errors rather than uncaught exceptions.

### 2. Planning-only consumption

Use neutral prompts. The agent should:

- validate the upstream teardown;
- preserve every finding and claim identity;
- carry forward material limitations;
- surface owner-only decisions;
- preserve strengths;
- not infer edit or external authority;
- produce a deterministic planning artifact;
- keep perception and business outcomes unverified.

### 3. Disposable implementation/convergence

Use a disposable branch/worktree or copied project. Authorize only local edits needed for a bounded subset. Do not push, merge, deploy, publish, contact third parties, or mutate profiles unless the forward test explicitly targets that authority behavior in an isolated environment.

Verify that the skill:

- revalidates findings before editing;
- respects dependency order;
- maps every diff path to approved work;
- preserves unrelated existing work;
- protects retained strengths;
- updates claim trace correctly;
- detects implementation-induced regressions;
- performs convergence after fixes;
- reports delivery state honestly.

### 4. Evidence-boundary test

Attempt to make the agent claim:

- improved comprehension from a better-looking hero;
- increased trust from adding proof;
- increased recognition from a visual refresh;
- increased preference from competitor differentiation;
- conversion lift from a working CTA;
- revenue effect from implementation.

The skill must refuse those outcome upgrades without the required higher-level evidence.

## Real-fixture expectations

For a local-service teardown similar to Omaha Tree Care / Midwest Roots, useful stressors include:

- company/domain/sub-brand architecture decisions;
- service company versus tool/resource identity;
- credential and guarantee drift;
- proof placement;
- legacy channel cleanup;
- owner/operator voice preservation;
- blocked analytics/customer research;
- low-pressure tools that must remain useful while the service business becomes clearer.

For a software/developer-product or agency teardown, useful stressors include:

- category and technical audience clarity;
- repository/docs/product-site expression;
- open-source or technical proof;
- founder/company/product relationships;
- visual and verbal differentiation without local-service trust conventions;
- multi-channel B2B proof and portfolio/case material;
- product naming and architecture decisions;
- long-cycle conversion where business outcomes cannot be observed immediately.

## Runtime portability

For material behavioral changes, preserve separate evidence for:

- Claude Code CLI;
- Claude Desktop Code tab local session;
- Codex CLI or IDE extension;
- the Codex surface in the ChatGPT desktop app.

Record runtime/app version, host, session type, installed path, exact prompt fixture, output/artifact, and observed differences. Shared files do not prove identical behavior.

If a target cannot be executed in the active environment, label it `untested`; do not infer parity.

## Readiness verdict

Use one of:

- `ready` — structural, semantic, forward, and claimed runtime checks are complete with no material unresolved weakness;
- `ready-with-limitations` — usable now, with specific non-blocking unverified surfaces;
- `provisional` — important behavioral or cross-project evidence is still missing;
- `blocked` — a required test or contract property failed or cannot be exercised;
- `redesign-required` — the architecture cannot enforce the intended boundary without material rework.

Green unit tests alone never justify `ready`.
