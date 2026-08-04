# Contributing

Contributions should make AI-assisted workflows more dependable, understandable, or effective.

## Before opening a pull request

- Put the project under the matching top-level category: `skills/`, `plugins/`, or `tools/`.
- Keep each project self-contained and include only files it needs to work.
- Document prerequisites, installation, usage, and known limitations at the closest appropriate public documentation level.
- Never commit credentials, private data, generated caches, or machine-specific configuration.
- Run the project's own validation and tests, and include the results in the pull request.
- Keep unrelated changes in separate pull requests.

For skills, preserve the standard `SKILL.md` frontmatter and bundle reusable scripts, references, and assets inside the skill directory. Validate scripts by running them, not only by reading them.

Claude Code skills under `.claude/skills/` declare their package contract in a `skill-manifest.json` and are checked by the shared [`tools/skill-validator`](tools/skill-validator/). When you add or change one of those skills, update its manifest and run `python3 tools/skill-validator/skill_validator.py`; include the result in the pull request.

By contributing, you agree that your contribution is licensed under the repository's MIT License.
