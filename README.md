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

Read each skill's `SKILL.md` before adapting it to another agent or platform. Agent capabilities, authority boundaries, and packaging conventions differ.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository conventions.

## License

[MIT](LICENSE)
