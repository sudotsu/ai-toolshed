![AI Toolshed Banner](assets/ai-toolshed-best-banner.gif)

# AI Toolshed

Practical, reusable tools for working better with AI.

This monorepo collects skills, plugins, and standalone tools that make collaboration with AI systems more rigorous, useful, and repeatable. Each project is designed to solve a real workflow problem[...]

## What's inside

| Type | Project | Purpose |
| --- | --- | --- |
| Skill | [project-teardown](skills/project-teardown/) | Use a software product like a real user, inspect its implementation, benchmark it against the current market, and produce an implementation[...]

The repository is organized by artifact type:

```text
ai-toolshed/
├── skills/      # Reusable instruction and resource packages for AI agents
├── plugins/     # Bundles that may combine skills, integrations, and commands
└── tools/       # Standalone utilities and supporting software
```

Empty categories are added when the first real project for that category is ready.

## Install a skill

To install `project-teardown` for Codex, copy its complete directory into your Codex skills directory:

```bash
cp -R skills/project-teardown "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart Codex after installation so it discovers the skill. Then invoke it by name:

```text
Use $project-teardown to thoroughly evaluate this project.
```

Read each project's `SKILL.md` before adapting it to another agent or platform. Agent capabilities and packaging conventions differ.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository conventions.

## License

[MIT](LICENSE)
