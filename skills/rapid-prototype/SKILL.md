---
name: rapid-prototype
description: Build the fastest viable, demonstrable vertical slice of a website or app when the user needs a working prototype, MVP, preview, pitch demo or same-day result. Execute instead of returning a plan, reuse existing code, verify the visible journey, disclose demo-only behavior, preserve easy rollback and never push or merge main without explicit permission. Not for planning-only or exhaustive teardown requests.
---

# Rapid Prototype

**Produce an inspectable result, not an implementation proposal.** Optimize for the shortest path to one honest, observable user outcome. Applies to sites, PWAs, apps, dashboards, API-backed screens and new or existing repositories. A successful demo is not production readiness.

## Non-negotiable operating rules

- If asked to build or fix, **act** using available tools. Do not substitute a roadmap, prompts for another agent, long preamble or speculative audit. Reuse decisions and previous work already provided.
- Keep commentary lean. Surface only a material assumption, blocker or verified result; do not narrate routine actions.
- Prefer the existing app/site, stack, components, styles, data and deployment over a new scaffold. No unrelated redesign, sweeping refactor, dependency upgrade or new infrastructure unless required for the proof.
- Inspect current branch, working-tree status, relevant scripts and prior decisions before editing. Preserve unrelated and uncommitted work. If the tree is dirty, isolate in a new worktree/branch if safe or narrowly edit without overriding the owner. Never use a broad reset, clean, force push or unrequested stash.
- **Default delivery is a feature branch, unmerged PR and isolated preview where practical. Never push directly to or merge `main` or another protected/production branch unless the user explicitly authorizes that action for this task.**
- Permission to prototype is not permission to alter production, use live customer data, run migrations, send external emails, process real charges, buy resources, change credentials/domains or perform destructive actions. Use an isolated/test substitute and obtain separate authority for live effects.
- Clearly distinguish working behavior from mocks, fixtures, test mode, screenshots, build-only checks and unverified integrations. Never claim readiness, deployment or verification by inference.

## 1. Select the one demo proof

Infer from the request and product. Ask **one** question only if an unsafe or materially incompatible choice cannot be resolved. Otherwise state a consequential assumption briefly and proceed.

Identify: **viewer**, **one journey** from entry to visible result, **fastest usable surface**, **truth boundary** (what must actually function versus what can be visibly simulated), and **stop line** (everything nonessential). Do not turn this into a requirements workshop.

Website example: landing -> working CTA -> meaningful confirmation. App example: select -> submit -> visibly changed state. If cross-device persistence is the claim, actually persist and verify; a local fixture cannot establish it. If a provider is the core proof, verify through an authorized test environment or report that proof as blocked.

## 2. Choose the fastest safe route

Use the highest feasible option:

1. Expose or repair an already implemented journey.
2. Add the missing thin vertical slice inside the existing project.
3. Reuse available components, fixtures, routes, storage, deploy pipeline and branding.
4. Use a bounded **visibly labeled demo adapter** if an external integration is not needed to establish the requested proof.
5. Start a small new project only if no useful base exists.

Build **one complete vertical slice**, not five polished but dead-end screens. Prioritize real navigation, legibility, primary interaction and observable outcome. Keep secondary pages, animations, abstraction, analytics, backlog fixes and speculative scaling outside the short run. Include the minimum necessary empty/loading/error state and a safe defining failure path.

## 3. Execute, verify and expose

1. Record start ref and touched paths; establish an isolated task branch or disposable workspace. Keep production data/secrets separate from previews.
2. Make the defining path visible early. Implement only enough UI/backend/data behavior for that path to be honestly demonstrable.
3. Once the path works, **stop feature expansion** and use remaining effort on focused verification and delivery.
4. Run proportionate checks: applicable typecheck/build and at least one exercised end-to-end viewer journey. Add narrow tests where the change or failure mode warrants them; avoid unrelated test batteries.
5. Open it as the viewer would. Follow entry -> action -> result and inspect obvious runtime/UI failures. Compilation alone does not prove the journey. Where the demo claims data/provider behavior, inspect actual resulting state/test-provider evidence.
6. When permitted and available, deploy an **isolated non-production preview**, open the real URL, and create an **unmerged PR**. Confirm each external action actually succeeded.

Use test-mode payments or a prominently identified simulation; never accept live payment as an implicit demo shortcut. Do not fake auth/security guarantees, persistence, delivery or integration status.

## 4. Recover from blockers without going plan-only

- Missing provider credentials: continue with the safe demonstrable portion and clearly labeled test fixture, unless real integration is the point; name that unverified gate.
- Build or preview blocked: leave a working local artifact if possible, verified run instructions/screenshots, and exact blocker. Never invent a public link.
- Live/destructive step needs approval: stop **that step** and continue independent safe work.
- Deadline approaches: cut secondary features rather than falsifying results, skipping all checks or destroying rollback.
- Defining journey fails: repair it or reduce the completion claim and report the observed failure.
- If user explicitly requests only a plan/audit, do not initiate edits.

## 5. Hand off the result compactly

Fill [the compact handoff](assets/handoff-template.md) with **observed evidence**:

- Demo entry point and precisely what a viewer can do.
- Checks performed and their results (build, browser, data and provider evidence separately).
- Demo-only elements, blockers, material unverified claims.
- Starting revision, task branch/commit/PR and actual unmerged/production status.
- Least destructive rollback: close PR/discard isolated branch, revert isolated commit if needed, and separately account for external previews or data effects.
- At most one specific owner action needed next.

Never imply closing a PR removes an externally deployed preview. Do not claim the skill is installed in a runtime merely because its files exist.

For future maintenance, use [behavioral fixtures](references/behavioral-fixtures.md); static package validation cannot prove the runtime follows this workflow. See [README.md](README.md) for portable installation boundaries.
