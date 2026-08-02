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

Codex discovers user-level skills under `$HOME/.agents/skills`. From WSL or another POSIX shell, copy whichever complete skill directories you want:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R skills/project-teardown "$HOME/.agents/skills/"
cp -R skills/project-revision "$HOME/.agents/skills/"
cp -R skills/seo-teardown "$HOME/.agents/skills/"
cp -R skills/seo-revision "$HOME/.agents/skills/"
```

Codex normally detects skill changes automatically. List available skills with `/skills`, or invoke one explicitly with `$`:

```text
Use $project-teardown to comprehensively evaluate this project.
Use $project-revision to implement the approved teardown findings.
Use $seo-teardown to investigate this site's organic-search opportunity.
Use $seo-revision to implement the approved SEO teardown findings.
```

In ChatGPT Work, invoke an installed skill with `@` instead. Cloning this repository does not automatically add its skills to your ChatGPT account.

Read each skill's `SKILL.md` before adapting it to another agent or platform. Agent capabilities, authority boundaries, and packaging conventions differ.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository conventions.

## License

[MIT](LICENSE)
