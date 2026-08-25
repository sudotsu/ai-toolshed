![AI Toolshed Banner](assets/ai-toolshed-best-banner.gif)

# AI Toolshed

Practical, reusable tools for working better with AI.

This monorepo collects skills, plugins, and standalone tools that make collaboration with AI systems more rigorous, useful, and repeatable. Each project is designed around a real workflow, explicit evidence, and verifiable outputs rather than a generic prompt.

## What's inside

| Type | Project | Purpose |
| --- | --- | --- |
| Guide | [Persistent & Enforced Context](docs/persistent-enforced-context/) | Design durable AI instructions, memory, project context, and behavioral regression tests without collapsing them into one oversized prompt. |
| Skill | [project-teardown](skills/project-teardown/) | Use a software product like a real user, inspect its implementation, judge its product and market position, and produce a severity-ordered, implementation-ready teardown. |
| Skill | [project-revision](skills/project-revision/) | Revalidate an approved project teardown, resolve owner decisions, implement findings in dependency order, and converge the result into an auditable readiness handoff. |
| Skill | [seo-teardown](skills/seo-teardown/) | Investigate technical SEO, content, authority, local and AI-mediated discovery, measurement, and qualified-conversion opportunity without changing the site. |
| Skill | [seo-revision](skills/seo-revision/) | Revalidate and implement approved SEO findings, respect repository and external-action boundaries, verify search eligibility, and produce a durable revision and experiment record. |
| Skill | [brand-teardown](skills/brand-teardown/) | Audit positioning, differentiation, architecture, messaging, trust, identity, claims, channel expression, and competitive context without changing the audited project. |

The skills include two implemented teardown/revision workflows and one standalone teardown:

```text
project-teardown  -> project-revision
seo-teardown      -> seo-revision
brand-teardown    -> validated implementation handoff
```

The teardown skills are comprehensive and read-only. The revision skills consume validated handoffs, request decisions where needed, implement only approved work, and verify the resulting state without claiming unproven outcomes.
No `brand-revision` skill is implemented yet; `brand-teardown` defines the evidence and authority boundary a future revision workflow must preserve.

The repository is organized by artifact type:

```text
ai-toolshed/
├── AGENTS.md
├── CLAUDE.md
├── assets/
├── docs/
│   ├── persistent-enforced-context/
│   └── runtime-portability.md
├── skills/
│   ├── project-teardown/
│   ├── project-revision/
│   ├── seo-teardown/
│   ├── seo-revision/
│   └── brand-teardown/
└── tools/
```

Each skill is self-contained and includes its instructions plus any validators, renderers, references, tests, or interface metadata it needs.

The documentation guides preserve reusable architecture, configuration, and validation knowledge that should not be packaged as a runtime skill. Start with the [documentation index](docs/). Reusable additions follow the [runtime portability contract](docs/runtime-portability.md): Claude Code and Codex are required targets, and the applicable Claude Desktop and ChatGPT desktop surfaces must be assessed explicitly.

## Install the skills

The canonical skill packages target both Claude Code and Codex. Their local desktop coding surfaces use the same runtime-specific skill sources:

| Runtime surface | Personal installation root | Explicit invocation |
| --- | --- | --- |
| Claude Code and Claude Desktop Code tab | `$HOME/.claude/skills` | `/skill-name` |
| Codex CLI, IDE extension, and the Codex surface in the ChatGPT desktop app | `$HOME/.agents/skills` | `$skill-name` |

Install on the same host where the runtime executes. A skill copied inside WSL is not visible to a Windows-host desktop session, and vice versa.

The commands below replace each destination completely so removed repository files cannot remain as stale installed files. Back up local edits inside an installed skill first; replacement deletes them.

From WSL or another POSIX shell:

```bash
for target_root in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  mkdir -p "$target_root"
  for skill in project-teardown project-revision seo-teardown seo-revision brand-teardown; do
    destination="$target_root/$skill"
    rm -rf -- "$destination"
    cp -R "skills/$skill" "$destination"
  done
done
```

From Windows PowerShell:

```powershell
$skillRoots = @(
  (Join-Path $HOME ".claude\skills"),
  (Join-Path $HOME ".agents\skills")
)
foreach ($skillRoot in $skillRoots) {
  New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
  foreach ($skill in "project-teardown", "project-revision", "seo-teardown", "seo-revision", "brand-teardown") {
    $destination = Join-Path $skillRoot $skill
    if (Test-Path -LiteralPath $destination) {
      Remove-Item -LiteralPath $destination -Recurse -Force
    }
    Copy-Item -LiteralPath (Join-Path "skills" $skill) -Destination $destination -Recurse
  }
}
```

Both runtimes detect skill changes automatically in ordinary local sessions; restart if a new top-level skill directory does not appear. Invoke the installed workflows with the runtime's syntax:

```text
Claude Code / Claude Desktop Code:
/project-teardown comprehensively evaluate this project.
/project-revision implement the approved teardown findings.

Codex / ChatGPT desktop Codex:
Use $project-teardown to comprehensively evaluate this project.
Use $project-revision to implement the approved teardown findings.
```

Local copies reach the local coding surfaces listed above. They do not automatically install into Claude Chat/Cowork, cloud sessions, or ChatGPT Chat/Work. Those surfaces use account sync or plugin distribution and must be packaged and tested separately. See [Runtime Portability](docs/runtime-portability.md) for the exact boundary and current official sources.

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
| `skill-portability` | Automate analysis, conversion, and packaging beyond the repository's enforced Claude Code/Codex baseline, including Gemini and distributable plugins. | Cross-runtime adapter drift remains a real problem even after the shared skill contract is enforced. | Use a provenance-safe implementation and add round-trip fixtures that detect lossy metadata, permission, MCP, reference, and install conversion. |

### Publication gate

A roadmap candidate ships only when it is:

- reusable outside the project that created it;
- explicit about scope, authority, destructive actions, and external side effects;
- organized around a concrete workflow and durable output contract;
- bundled with the references, scripts, templates, or assets required to work independently;
- covered by realistic evals or regression tests, with validators where deterministic artifacts are part of the contract;
- supported by both Claude Code and Codex, with applicable Claude Desktop and ChatGPT desktop surfaces assessed under the [runtime portability contract](docs/runtime-portability.md); and
- clear on provenance, licensing, current-documentation requirements, and known limitations.

Prompt-only personas, project-private operating instructions, copied vendor bundles, and unverified experiments do not enter the catalog just because they happen to live in a skills directory.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository conventions.

## License

[MIT](LICENSE)
