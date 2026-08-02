---
name: project-teardown
description: Perform a comprehensive, read-only teardown of a software product by using it as a real user, inspecting its implementation, and evaluating its technical quality, UX, feature set, product coherence, and current market relevance. Use for websites, PWAs, CLIs, AI agents, developer tools, and similar projects when the user asks for a full review, teardown, deep audit, gap analysis, best-in-class comparison, product critique, or an implementation-ready inventory of everything that should be fixed, added, changed, removed, or investigated.
---

# Project Teardown

Evaluate the whole product, not merely its code. Hold it against the goal of being as good as the best relevant alternatives or better, while distinguishing what a committed solo builder can realistically achieve from advantages that require a team, capital, proprietary data, distribution, or time.

Remain independent and evidence-led. Do not grade on a curve, manufacture faults to appear thorough, or soften material conclusions. A comprehensive teardown includes meaningful strengths, passed checks, limitations, and unknowns as well as problems.

## Operating contract

- Treat the product source as read-only. Do not fix, refactor, upgrade, reformat, or remove product code.
- Permit normal local effects required to test the product, including dependency installation, builds, caches, generated artifacts, disposable accounts, and test data. Keep them isolated or reversible when possible and disclose them.
- Ask as many questions as needed when an answer could materially change the evaluation, benchmark, risk, or recommendation. Inspect available evidence first when it can answer the question.
- Never use a question to avoid reasonable investigation. State non-consequential assumptions and continue.
- Exercise the project the way a real intended user would: start with its public instructions, onboarding, primary workflows, and ordinary environment.
- Treat successful execution of the product's defining workflow as a completion gate. Installing, building, and exercising secondary commands does not substitute for using the core product.
- Test happy paths, failure paths, edge cases, recovery, and destructive or high-risk actions proportionately.
- Use current external research for market, competitor, ecosystem, security, legal, policy, or version-sensitive claims. Prefer primary sources and date the research.
- Distinguish confirmed fact, observed behavior, sourced external evidence, inference, opinion, and unresolved uncertainty.
- Do not equate popularity with quality or isolated online comments with demand.
- Never expose credentials, private data, secrets, or sensitive runtime output in the report.
- Do not perform live destructive actions, purchases, publication, production changes, or outreach without explicit authorization.

## Start by establishing the target

Infer from the project and confirm through focused questions when consequential:

1. Intended users and their core jobs.
2. Product promise, scope, maturity, and deployment context.
3. Primary workflows and what success looks like.
4. Intended differentiators and explicit non-goals.
5. Relevant constraints: solo builder, budget, timeline, platforms, compatibility, privacy, safety, and business model.
6. Named competitors or aspirational products, if any.

Do not assume the README is correct. Reconcile documentation, product behavior, code, tests, configuration, release artifacts, and the user's answers. Record contradictions.

Before deep testing, summarize the interpreted product thesis and material assumptions to the user. Ask only the questions whose answers may alter the approach; continue after receiving them.

## Execute the teardown

### 1. Establish a clean-user path

- Identify the supported environment and prerequisites.
- Follow the documented install and launch path before using repository knowledge to bypass it.
- Record every undocumented prerequisite, broken instruction, confusing choice, warning, and point of friction.
- If blocked, diagnose the blocker, try safe user-plausible recovery paths, and continue with all review surfaces that remain available.
- If a credential, account, device, supported platform, test target, or user action would unblock a defining workflow, ask the user to make it available safely. Never ask the user to paste a secret into chat; ask them to provide it through the project's normal environment or credential mechanism.
- If the defining workflow remains blocked, label the teardown **provisional**. Do not call it complete or comprehensive merely because the limitation is disclosed.

### 2. Use the complete product

- Inventory discoverable features and map the core user journeys.
- Complete each meaningful workflow from entry through outcome and recovery.
- Test empty, loading, success, partial-success, invalid-input, permission-denied, offline or disconnected, timeout, cancellation, retry, and failure states when applicable.
- For websites and PWAs, include responsive layouts, keyboard use, accessibility, browser behavior, installability, offline behavior, perceived and measured performance, forms, navigation, content quality, and visual consistency.
- For CLIs and agents, include installation, first run, help, configuration, command ergonomics, terminal output, exit behavior, interruption, non-interactive use, automation, model and tool behavior, context handling, failure recovery, packaging, upgrade, and uninstall expectations.
- Capture reproducible evidence. Use screenshots, recordings, logs, command output, timings, accessibility results, or minimal excerpts as appropriate.
- Track each planned surface as passed, failed, partially tested, blocked, not tested, or not applicable while working. Do not reconstruct coverage from memory at the end.

### 3. Inspect the implementation

Trace observed behavior into the source. Review architecture, correctness, error handling, security, privacy, dependency health, performance, state and data integrity, maintainability, tests, delivery, configuration, observability, documentation, and platform-specific requirements.

Search usages before declaring code dead or a feature unused. Run the project's existing checks. Add non-mutating diagnostics when proportionate, but do not add tests or alter project configuration.

Do not report a tool warning as a product defect without validating its relevance. Do not claim a root cause when the evidence only supports a hypothesis.

### 4. Evaluate product and landscape

Read [evaluation-framework.md](references/evaluation-framework.md) before this phase.

- Identify the strongest relevant direct competitors, substitutes, and emerging approaches.
- When recommending specialization, pivot, or entry into a niche, benchmark the strongest products, open-source projects, research systems, workflows, and evaluation standards inside that niche before issuing the recommendation.
- Compare user outcomes and defensible capabilities, not feature-count theater.
- Look for dated premises, commoditized features, internal contradictions, unmet expectations, strategic differentiation, adoption barriers, and technical or business dead ends.
- Assess every major feature against the interpreted product purpose: essential, differentiating, supporting, distracting, contradictory, obsolete, or missing.
- Identify where the product is ahead of the curve, where a specific achievable change could put it ahead, and where it is heading toward a technical, product, adoption, legal, safety, or business wall.
- Explain the consequence of changing each material item and the consequence or opportunity cost of keeping it unchanged.
- Treat claims about what the market wants as hypotheses requiring credible evidence. If evidence is insufficient, recommend validation rather than pretending certainty.

### 5. Synthesize and order the work

Read [report-contract.md](references/report-contract.md) before writing deliverables.

- Deduplicate symptoms that share a root cause without hiding their distinct user impacts.
- Separate confirmed defects, design shortcomings, strategic recommendations, opportunities, and investigations.
- Assign severity from impact and likelihood; do not inflate severity because a fix is easy or visually obvious.
- Reserve critical severity for confirmed or high-confidence conditions meeting the report contract's catastrophic-impact threshold. An architectural exposure, missing control, or plausible exploit path without demonstrated catastrophic impact is normally high, not critical.
- Build a dependency graph among findings. Order implementation by prerequisites, risk reduction, and then severity—not severity alone.
- Define `dependencies` strictly as prerequisite finding IDs that must be completed or decided before the current finding. Put reverse relationships in `dependents`. Never use reciprocal dependencies or phase membership as a dependency.
- Require an acyclic dependency graph and order the implementation ledger so every dependency appears before its dependent.
- Surface decisions and mutually exclusive paths explicitly. Do not hand the implementation skill contradictory instructions.
- Preserve low-severity findings. Comprehensive means nothing actionable silently disappears.
- Include positive findings and passed checks so future work does not regress strengths or repeat completed investigation.
- Reconcile every actionable statement in narrative sections with exactly one finding ID. If an observation is intentionally non-actionable, mark it as a passed check, limitation, explicit deferral, or contextual note in the review coverage file.
- Do not use “no material finding,” “later hardening,” or a coverage limitation to hide an actionable low-severity improvement or investigation. Register it or explicitly justify why no action is warranted.
- Use the controlled finding values and exact field labels in the report contract. Write `None` or `Not applicable — <reason>` instead of omitting a required field.

## Produce the handoff

Create a `project-teardown/` folder at the project root unless the user specifies another location. If it already exists, ask before replacing it or create a clearly dated sibling folder. Use the exact structure and field definitions in [report-contract.md](references/report-contract.md).

Do not rename, merge, omit, or substitute the required files. Do not invent a replacement schema or validator. `findings.json` is the machine-readable handoff and must mirror `05-findings-register.md`.

The handoff must let a separate implementation skill proceed without rediscovering the review. Make each actionable finding independently understandable, reproducible, scoped, and verifiable. Use repository-relative file references with line numbers or symbols when stable. Link external evidence directly and include access dates.

Before packaging or presenting the handoff, run:

```bash
python3 <skill-directory>/scripts/validate_teardown.py <project-teardown-directory>
```

Fix every validation error. Treat validator success as necessary but not sufficient: manually inspect the narrative reconciliation because a script cannot determine whether an observation deserved a finding. Report the validator result in `07-review-coverage.md`.

If the bundled validator is unavailable or cannot run, do not create a substitute validator or claim structural success. Report the exact blocker and leave the teardown provisional.

End the user-facing response with:

1. The overall verdict and product trajectory.
2. The most consequential findings and decisions.
3. What was tested, what was not, and why.
4. Whether the teardown is complete or provisional and what would complete it.
5. The path to the teardown folder.
6. A clear statement that no product fixes were implemented.

Do not collapse the full report into the chat response.
