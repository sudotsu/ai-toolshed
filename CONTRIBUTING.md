# Contributing

Contributions should make AI-assisted workflows more dependable, understandable, or effective.

## Before opening a pull request

- Put the project under the matching top-level category: `docs/`, `skills/`, `plugins/`, or `tools/`.
- Keep each project self-contained and include only files it needs to work.
- Document prerequisites, installation, usage, and known limitations at the closest appropriate public documentation level.
- Never commit credentials, private data, generated caches, or machine-specific configuration.
- Run the project's own validation and tests, and include the results in the pull request.
- Keep unrelated changes in separate pull requests.

## Runtime portability

Reusable contributions target Claude Code and Codex by default. They must also assess the Claude Desktop Code tab and the Codex surface in the ChatGPT desktop app whenever those surfaces support the artifact type. Follow the [runtime portability contract](docs/runtime-portability.md): keep one platform-neutral core, isolate vendor adapters, document exact installation and invocation differences, and validate every claimed target independently.

A contribution may be platform-specific only when it depends on an exclusive capability. State the concrete limitation and the closest supported equivalent; do not omit the other runtime silently. “Untested” must remain labeled unverified.

For skills, preserve the standard `SKILL.md` frontmatter and bundle reusable scripts, references, and assets inside the skill directory. Validate scripts by running them, not only by reading them.

For documentation sets, provide an index from `docs/`, link the set from the repository README when it introduces a first-class concept, keep each canonical configuration in one location, and verify every relative link. Documentation that defines behavioral tests must include an execution and comparison method rather than presenting the cases as examples only.

By contributing, you agree that your contribution is licensed under the repository's MIT License.
