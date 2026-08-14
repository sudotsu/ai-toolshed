---
name: project-teardown
description: Perform a comprehensive, evidence-led, read-only teardown of a software product by executing it as a real user, inspecting its implementation, testing relevant platforms and failure paths, researching the current landscape, and producing a validated implementation-ready findings handoff. Use for websites, PWAs, CLIs, AI agents, APIs, desktop/mobile apps, libraries, and developer tools when the user asks for a full review, teardown, deep audit, product critique, gap analysis, best-in-class comparison, release-readiness assessment, or exhaustive inventory of what should be fixed, added, changed, removed, retained, decided, or investigated. Do not use for implementing fixes.
---

# Project Teardown

Evaluate the whole product, not merely its code. Hold it against the strongest relevant alternatives and the product's own promises while distinguishing improvements a committed solo builder can execute from advantages that require a team, capital, proprietary data, distribution, credentials, or time.

Remain independent and evidence-led. Do not grade on a curve, manufacture faults to appear thorough, or soften material conclusions. Include meaningful strengths, passed checks, limitations, unknowns, and preservation requirements as well as defects.

## Operating contract

- Treat product source and pre-existing user work as read-only. Do not fix, refactor, upgrade, format, migrate, or remove product code.
- Prefer a disposable clone, temporary worktree, copied fixture, container, VM, or sandbox for installs, builds, generated files, test data, and destructive-path testing. Read [evidence-and-coverage.md](references/evidence-and-coverage.md) before running project commands.
- Never use reset, clean, checkout, stash, broad formatter, or deletion to restore the tree. Remove only effects proven to have been created by this teardown.
- Exercise the product as an intended user: start with public instructions, onboarding, ordinary configuration, primary workflows, and the claimed environment.
- Treat successful execution of every defining workflow as a completion gate. Building, linting, or exercising secondary commands does not substitute for using the core product.
- Test happy paths, failure paths, edge cases, interruption, recovery, and high-risk actions proportionately. Use safe substitutes for live destructive actions.
- Ask focused questions when an answer could materially change the benchmark, risk, scope, or recommendation. Inspect available evidence first and do not use questions to avoid reasonable investigation.
- Use current external research for version-sensitive, market, competitor, ecosystem, security, legal, policy, pricing, or platform claims. Match guidance to the project's actual pinned or deployed version and date the research.
- Distinguish runtime observation, automated test, source inspection, configuration evidence, artifact evidence, external source, owner-provided fact, inference, opinion, and unresolved uncertainty. Record finding confidence separately from verification state so a conclusively demonstrated defect is not blurred with an unverified production operation.
- Do not equate popularity with quality, a successful demo with reliability, or isolated online comments with demand.
- Treat a constraint as real only when the owner stated it or an objective external fact establishes it. Never infer a quality-limiting constraint from task difficulty, elapsed effort, or inconvenience, and never use one to justify a lower benchmark. Record the provenance of every constraint that caps achievable quality alongside the dimension it caps.
- Never expose credentials, secrets, private data, or sensitive runtime output in reports or evidence.
- Do not perform purchases, publication, production changes, credential changes, external outreach, or live destructive operations without explicit authorization.

## 1. Establish the target and baseline

Infer from the project and confirm only when consequential:

1. intended users and core jobs;
2. product promise, scope, maturity, and deployment context;
3. defining workflows and observable success;
4. intended differentiators and explicit non-goals;
5. constraints: solo builder, budget, timeline, platforms, compatibility, privacy, safety, credentials, business model, and release intent;
6. named competitors, substitutes, aspirational products, or standards.

Do not assume the README is correct. Reconcile documentation, runtime behavior, code, tests, configuration, release artifacts, deployment state, analytics/operational evidence, and owner answers. Record contradictions.

Capture the immutable revision or explicit working-tree state, branch, dirty inventory, relevant tool versions, and existing checks before testing. Summarize the interpreted product thesis, defining workflows, benchmarks, and material assumptions before deep testing.

## 2. Build the coverage plan

Read:

- [testing-matrix.md](references/testing-matrix.md) for product-type and risk-specific checks;
- [evidence-and-coverage.md](references/evidence-and-coverage.md) for evidence levels, isolation, and completion rules.

Create the surface coverage matrix before deep testing. Include every defining workflow, major feature, supported platform/runtime/provider claim, applicable quality domain, destructive boundary, and material research question. Track status while working; do not reconstruct coverage from memory at the end.

## 3. Establish a clean-user path

- Follow the documented install and launch path before using repository knowledge to bypass it.
- Record undocumented prerequisites, broken instructions, confusing choices, warnings, and friction.
- If blocked, diagnose the blocker, try safe user-plausible recovery paths, and continue every review surface that remains available.
- When credentials, devices, platforms, accounts, test targets, or owner action would unblock a defining workflow, request them through the project's normal secure mechanism. Never ask for a secret in chat.
- If any defining or required surface remains materially blocked, partial, or untested, keep the teardown `provisional` unless the evidence-and-coverage completion rules are still satisfied.

## 4. Use the complete product

- Inventory discoverable features and map core journeys from entry through outcome, persistence, and recovery.
- Execute every meaningful workflow and applicable state in the testing matrix.
- Verify user-visible and system-visible results: output, exit state, files, records, requests, logs, notifications, delivery, persistence, and cleanup.
- For cross-platform claims, distinguish behavioral, build-only, source-only, blocked, and not-tested evidence. A build on a platform is not behavioral platform verification.
- Capture reproducible, sanitized evidence in `project-teardown/evidence/` when it improves independent verification.

## 5. Inspect the implementation

Trace observed behavior into source and configuration. Review architecture, correctness, error handling, trust boundaries, security, privacy, dependency health, performance, resource limits, state/data integrity, concurrency, maintainability, tests, delivery, configuration, observability, documentation, and platform-specific branches.

Search usages before declaring code dead or a feature unused. Run existing checks in an isolated or baseline-safe environment. Add only non-mutating diagnostics. Do not add tests or alter project configuration.

Do not report a tool warning as a defect without validating relevance. Do not claim a root cause when evidence supports only a hypothesis. Do not treat absence of proof as proof of absence.

## 6. Evaluate product and landscape

Read [evaluation-framework.md](references/evaluation-framework.md).

- Select the strongest relevant direct competitors, substitutes, open-source projects, research systems, workflows, and standards.
- When recommending a niche, pivot, or specialization, benchmark the strongest systems inside that niche before recommending it.
- Compare user outcomes, reliability, defensible capability, adoption friction, and business constraints—not feature-count theater.
- Identify dated premises, commoditized features, internal contradictions, unmet expectations, technical/business dead ends, and realistic differentiation.
- Classify every major feature as essential, differentiating, supporting, distracting, contradictory, obsolete, or missing.
- Identify what is ahead of the curve, one achievable change from ahead, and heading toward a technical, product, adoption, legal, safety, or business wall.
- Explain consequences and tradeoffs of changing and retaining each material direction.
- Treat market-demand claims as hypotheses unless supported by credible evidence. Recommend validation where evidence is insufficient.
- Support every parity, superiority, or shortfall judgment with a concrete artifact: a competitor capability actually inspected, a measured output, a test or command result, or a dated external source. Reasoning about why the product seems strong is not evidence of parity.

## 7. Synthesize the findings

Read [report-contract.md](references/report-contract.md) before writing artifacts.

- Deduplicate shared root causes without hiding distinct user impacts.
- Separate defects, shortcomings, recommendations, opportunities, investigations, strengths, and owner decisions.
- Assign severity from impact, likelihood, reach, and reversibility. Do not inflate severity because a fix is easy or visible.
- Reserve critical for confirmed or high-confidence catastrophic impact with a realistic trigger.
- Build an acyclic dependency graph. `dependencies` are prerequisites of the current finding; `dependents` are exact reverse links. Phase membership is not a dependency.
- Order work by decisions and prerequisites, then risk reduction, then severity and leverage.
- Surface conflicts and mutually exclusive paths. Do not hand the revision skill contradictory instructions.
- Preserve low-severity work and strengths. Nothing actionable or worth retaining may silently disappear.
- Build the dedicated claims inventory for credentials, licensing, insurance, safety, diagnosis, expertise, guarantees, pricing, performance, statistics, privacy, data handling, and capability claims. Every unresolved material claim must map to a finding.
- Give every actionable narrative observation exactly one finding ID. Mark non-actionable material as a passed check, limitation, explicit deferral, or contextual note in review coverage.
- Keep recommendation, owner decision, accepted risk, and evidence gap distinct. A recommendation is not approval.

## 8. Produce and validate the handoff

Create `project-teardown/` at the project root unless the user specifies another location. If it already exists, do not overwrite it; obtain permission or create a clearly dated sibling.

Use the exact core structure and fields in [report-contract.md](references/report-contract.md). Copy the starter files from `assets/report-template/` when useful, then replace every placeholder. Do not rename, merge, omit, or substitute required files. `findings.json` is the sole canonical findings source. Generate `05-findings-register.md` and `README.md` from it; do not manually duplicate the findings or calculate digests.

The handoff must let a separate revision run proceed without rediscovering the audit. Every actionable finding must be independently understandable, reproducible, scoped, dependency-aware, and verifiable. Use repository-relative paths with line numbers or symbols when stable. Link and date external evidence.

Generate the derived views, then validate the project report:

```bash
python3 <skill-directory>/scripts/render_findings.py <project-teardown-directory>
python3 <skill-directory>/scripts/render_readme.py <project-teardown-directory>
python3 <skill-directory>/scripts/validate_teardown.py <project-teardown-directory>
```

Fix every project-report validation error. Rerun both renderers after every final `findings.json` edit. Use `validate_teardown.py --verbose` only when the bounded default error summary is insufficient.

Skill-package validation and validator regression tests are maintenance tasks, not project teardown gates. Run them only when installing, packaging, or modifying the skill itself:

```bash
python3 <skill-directory>/scripts/validate_skill_bundle.py <skill-directory> --mode installed
python3 <skill-directory>/scripts/validate_skill_bundle.py <skill-directory> --mode package
python3 -m unittest discover -s <skill-directory>/scripts -p 'test_*.py' -v
```

Validator success is necessary, not sufficient. Manually re-read all narrative sections, coverage rows, evidence limitations, and finding classifications. A script cannot determine whether an observation deserved a finding or whether testing was substantively adequate.

If the bundled validator cannot run, do not invent a substitute or claim structural success. Report the exact blocker and leave the teardown provisional.

## User-facing handoff

End with:

1. overall verdict and trajectory;
2. most consequential findings, strengths, and decisions;
3. what was behaviorally tested, what was only inspected or built, and what remains blocked;
4. complete or provisional status and exactly what would complete it;
5. path to the teardown folder;
6. explicit statement that no product fixes were implemented.

Do not collapse the full report into chat.
