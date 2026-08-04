![AI Toolshed Banner](assets/ai-toolshed-best-banner.gif)

# AI Toolshed

Practical, reusable tools for working better with AI.

This monorepo collects skills, plugins, and standalone tools that make collaboration with AI systems more rigorous, useful, and repeatable. Each project is designed around a real workflow, explicit evidence, and verifiable outputs rather than a generic prompt.

## What's inside

| Type | Project | Purpose |
| --- | --- | --- |
| Skill | [project-teardown](skills/project-teardown/) | Use a software product like a real user, inspect its implementation, judge its product and market position, and produce a severity-ordered, implementation-ready teardown. |
| Skill | [project-revision](skills/project-revision/) | Revalidate an approved project teardown, resolve owner decisions, implement findings in dependency order, and converge the result into an auditable readiness handoff. |
| Skill | [seo-teardown](skills/seo-teardown/) | Investigate technical SEO, content, authority, local and AI-mediated discovery, measurement, and qualified-conversion opportunity without changing the site. |
| Skill | [seo-revision](skills/seo-revision/) | Revalidate and implement approved SEO findings, respect repository and external-action boundaries, verify search eligibility, and produce a durable revision and experiment record. |

The skills form two complementary workflows:

```text
project-teardown  -> project-revision
seo-teardown      -> seo-revision
```

The teardown skills are comprehensive and read-only. The revision skills consume validated handoffs, request decisions where needed, implement only approved work, and verify the resulting state without claiming unproven outcomes.

The repository is organized by artifact type:

```text
ai-toolshed/
├── assets/
└── skills/
    ├── project-teardown/
    ├── project-revision/
    ├── seo-teardown/
    └── seo-revision/
```

Each skill is self-contained and includes its instructions plus any validators, renderers, references, tests, or interface metadata it needs.

## Install for Codex CLI or the IDE extension

Codex discovers user-level skills under `$HOME/.agents/skills`. Install skills on the same host where the Codex runtime runs: a skill copied inside WSL is not visible to a Windows IDE extension, and vice versa.

The commands below replace each destination completely so removed repository files cannot remain as stale installed files. Back up local edits inside an installed skill first; replacement deletes them.

From WSL or another POSIX shell:

```bash
mkdir -p "$HOME/.agents/skills"
for skill in project-teardown project-revision seo-teardown seo-revision; do
  rm -rf -- "$HOME/.agents/skills/$skill"
  cp -R "skills/$skill" "$HOME/.agents/skills/$skill"
done
```

From Windows PowerShell:

```powershell
$skillRoot = Join-Path $HOME ".agents\skills"
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
foreach ($skill in "project-teardown", "project-revision", "seo-teardown", "seo-revision") {
  $destination = Join-Path $skillRoot $skill
  if (Test-Path -LiteralPath $destination) {
    Remove-Item -LiteralPath $destination -Recurse -Force
  }
  Copy-Item -LiteralPath (Join-Path "skills" $skill) -Destination $destination -Recurse
}
```

Codex normally detects skill changes automatically. List available skills with `/skills`, or invoke one explicitly with `$`:

```text
Use $project-teardown to comprehensively evaluate this project.
Use $project-revision to implement the approved teardown findings.
Use $seo-teardown to investigate this site's organic-search opportunity.
Use $seo-revision to implement the approved SEO teardown findings.
```

This installation is for Codex only. Cloning or copying this repository does not add these skills to a ChatGPT account.

## Install for Claude Code

Claude Code discovers skills under `.claude/skills/`. This repository already ships Claude-native packages of all four skills at [`.claude/skills/`](.claude/skills/), so any Claude Code session opened in this repository picks them up automatically — no install step is required to use them here.

These are separate copies from the Codex `skills/` catalog, adapted to Claude Code conventions: the Codex `agents/openai.yaml` interface file is removed, `SKILL.md` frontmatter is limited to `name` and `description`, and the `seo-revision` validator resolves its upstream `seo-teardown` package from Claude skill locations. The two trees are kept independent so each runtime gets packaging that matches it.

To make the skills available in every Claude Code session on your machine, copy them into your user-level skills directory.

From a POSIX shell:

```bash
mkdir -p "$HOME/.claude/skills"
for skill in project-teardown project-revision seo-teardown seo-revision; do
  rm -rf -- "$HOME/.claude/skills/$skill"
  cp -R ".claude/skills/$skill" "$HOME/.claude/skills/$skill"
done
```

From Windows PowerShell:

```powershell
$skillRoot = Join-Path $HOME ".claude\skills"
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
foreach ($skill in "project-teardown", "project-revision", "seo-teardown", "seo-revision") {
  $destination = Join-Path $skillRoot $skill
  if (Test-Path -LiteralPath $destination) {
    Remove-Item -LiteralPath $destination -Recurse -Force
  }
  Copy-Item -LiteralPath (Join-Path ".claude\skills" $skill) -Destination $destination -Recurse
}
```

Claude surfaces a skill automatically when your request matches its `description`; you can also ask for one by name:

```text
Use project-teardown to comprehensively evaluate this project.
Use project-revision to implement the approved teardown findings.
Use seo-teardown to investigate this site's organic-search opportunity.
Use seo-revision to implement the approved SEO teardown findings.
```

Each Claude package carries its own validators. Run a skill's `scripts/validate_skill.py` (where present) to check the package, and its output validator (`validate_teardown.py`, `validate_revision.py`, `validate_seo_teardown.py`, `validate_seo_revision.py`) against the artifact it produces.

Read each skill's `SKILL.md` before adapting it to another agent or platform. Agent capabilities, authority boundaries, and packaging conventions differ.

## What's coming next

The next additions are being selected from working skill packages already used across Claude Code, Codex, and Gemini environments. This is a roadmap, not a promise to publish local folders unchanged: every candidate must be generalized, hardened, documented, and tested to the same standard as the teardown and revision skills before it lands here.

The strongest pipeline currently looks like this:

```text
lead-architect
├── backend-expert
├── frontend-expert
├── devops-sre
└── qa-testing

digital-product-launcher
skill-portability
```

| Planned skill | What it will add | Why it made the cut | Required before publication |
| --- | --- | --- | --- |
| `lead-architect` | Spec-driven decomposition, specialist coordination, handoff contracts, and separate compliance and quality reviews for complex builds. | It already has an explicit operating law, staged workflow, failure escalation, model-selection guidance, and adversarial evals. | Remove runtime-specific assumptions, define durable handoff schemas, and add validator-backed completion gates. |
| `backend-expert` | Secure API and data-system design with transaction, idempotency, concurrency, authorization, and query-performance checks. | It already combines a concrete workflow with architecture and security references plus pressure, refactoring, and adversarial evals. | Generalize beyond one stack, replace absolute rules with evidence-aware policy, and validate generated implementation specs. |
| `frontend-expert` | Accessible, resilient, performance-aware frontend planning and implementation with explicit server/client and async-state boundaries. | It already carries accessibility, performance, and resilience references plus three behavior-focused evals. | Make framework rules version-aware, support non-React projects, and add measurable accessibility and performance verification. |
| `devops-sre` | Environment fingerprinting, change impact analysis, secret-safe infrastructure work, dry runs, rollback planning, and reliability verification. | It already includes a host fingerprint tool, a security/reliability contract, and adversarial infrastructure evals. | Make fingerprinting cross-platform, formalize destructive-action approvals, and test rollback and secret-handling guarantees. |
| `qa-testing` | Behavior-first test strategy, deterministic async testing, integration boundaries, adversarial coverage review, and regression handoffs. | It already has a testing-strategy reference and evals for flaky, over-mocked, and superficially complete suites. | Relax dogmatic test rules where the evidence calls for it, define bounded test budgets, and validate the resulting coverage record. |
| `digital-product-launcher` | Live-market research, monetization-model selection, pricing, payment constraints, launch sequencing, landing-page copy, and email funnels. | It already routes through seven substantial reference guides instead of producing generic launch advice. | Remove project- and vertical-specific assumptions, add evidence citation and freshness rules, and separate planning from authorized external actions. |
| `skill-portability` | Package one workflow for Claude Code, Codex, and Gemini while preserving metadata, tool permissions, MCP configuration, references, and install behavior. | Cross-runtime skill drift is a real recurring problem, and the local tooling demonstrates a viable analyze-transform-validate workflow. | Use a provenance-safe implementation, document each runtime's supported contract, and add round-trip fixtures that detect lossy conversion. |

### Publication gate

A roadmap candidate ships only when it is:

- reusable outside the project that created it;
- explicit about scope, authority, destructive actions, and external side effects;
- organized around a concrete workflow and durable output contract;
- bundled with the references, scripts, templates, or assets required to work independently;
- covered by realistic evals or regression tests, with validators where deterministic artifacts are part of the contract;
- portable across the hosts and runtimes it claims to support; and
- clear on provenance, licensing, current-documentation requirements, and known limitations.

Prompt-only personas, project-private operating instructions, copied vendor bundles, and unverified experiments do not enter the catalog just because they happen to live in a skills directory.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository conventions.

## License

[MIT](LICENSE)
