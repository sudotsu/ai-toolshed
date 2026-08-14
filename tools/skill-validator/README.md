# skill-validator

A single, reusable package validator for the skills in this repository. It
replaces the per-skill `validate_skill.py` scripts, which each re-implemented
the same integrity checks and had drifted apart. The validation *logic* now
lives here once; each skill declares its own package contract as data in a
`skill-manifest.json` file.

This is a maintenance / CI tool. It validates a skill's **package** (structure,
frontmatter, links, scripts, tests) from the repository source. It is not part
of a skill's runtime contract and is not bundled inside individual skills — the
skills' own runtime validators (`validate_teardown.py`, `validate_seo_teardown.py`,
and so on) remain bundled and self-contained.

## Usage

```bash
# Validate every bundled skill (defaults to ../../.claude/skills)
python3 tools/skill-validator/skill_validator.py

# Validate specific skills
python3 tools/skill-validator/skill_validator.py .claude/skills/seo-teardown

# Validate every skill under a root directory
python3 tools/skill-validator/skill_validator.py .claude/skills

# Skip the (slower) declared regression tests
python3 tools/skill-validator/skill_validator.py --no-tests
```

Exit status is `0` when every validated skill passes, `1` when any skill fails
validation, and `2` for a usage problem (a path that does not exist, or a path
with no manifest at or under it).

Run the validator's own regression suite with:

```bash
cd tools/skill-validator && python3 -m unittest test_skill_validator.py
```

The tool depends only on the Python standard library.

## What it checks

For each skill, in order:

1. **Manifest** — `skill-manifest.json` exists and is structurally valid.
2. **Directory name** — matches the manifest `name`.
3. **Required / forbidden files** — every `required_files` entry exists as a
   file; no `forbidden_files` entry is present.
4. **Frontmatter** — `SKILL.md` opens with a well-formed YAML frontmatter fence;
   `name` and `description` are present; `name` matches the manifest, is
   kebab-case, and is at most 64 characters; `description` meets the manifest's
   minimum length, is at most 1024 characters, and contains no angle brackets;
   the top-level keys satisfy the manifest's key policy.
5. **Local links** — every relative Markdown link in any `*.md` file resolves to
   an existing file inside the skill (no broken links, no links escaping the
   skill directory).
6. **Scripts** — every `scripts/*.py` file byte-compiles.
7. **Declared tests** — each command in the manifest `tests` list runs to a
   zero exit status (skipped with `--no-tests`, and skipped automatically when
   an earlier structural check already failed).

## Manifest schema (`skill-manifest.json`)

```jsonc
{
  "schema_version": 1,                 // required, must be 1
  "name": "seo-teardown",              // required; must match SKILL.md and dir name
  "runtime": "claude-code",            // optional, informational
  "required_files": [                  // required, non-empty; each must exist
    "SKILL.md",
    "references/audit-methodology.md",
    "scripts/validate_seo_teardown.py"
  ],
  "forbidden_files": [                 // optional; each must NOT exist
    "agents/openai.yaml"
  ],
  "frontmatter": {                     // optional
    "keys": "name-description-only",   // "name-description-only" | "claude-standard"
    "description_min_length": 80       // optional, default 40
  },
  "tests": [                           // optional
    {
      "command": ["python3", "-m", "unittest", "test_validator.py"],
      "cwd": "scripts",                // optional, default "."
      "timeout_seconds": 180           // optional, default 180
    }
  ]
}
```

### Frontmatter key policies

- `name-description-only` — the frontmatter may contain *only* `name` and
  `description`. This is the strictest policy and what the bundled teardown and
  revision skills use.
- `claude-standard` — the frontmatter may use any subset of this allowlist:
  `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`.
  Use this when a skill legitimately needs one of the optional keys.

In both policies `name` and `description` are required, and the length,
kebab-case, and angle-bracket rules always apply.

The `claude-standard` allowlist deliberately mirrors the `ALLOWED_PROPERTIES`
set enforced by Anthropic's own skill packager (`skill-creator/scripts/quick_validate.py`)
— it is the *Skill* frontmatter contract, not the slash-command or subagent
frontmatter set (which adds fields such as `argument-hint`, `disable-model-invocation`,
`user-invocable`, and `disallowed-tools`). It is intentionally a restrictive
repository policy: a skill whose frontmatter needs a field outside this set
should widen the allowlist here on purpose rather than have it accepted silently.

### Frontmatter parsing

Frontmatter is parsed with a small, dependency-free reader (standard library
only — no PyYAML). It supports the flat `key: value` form these skills use:
top-level keys are read from column-zero `key:` lines, and nested mapping keys
(indented under `metadata`) are ignored for the key-policy check. It does not
implement the full YAML grammar — quoted keys, block scalars, and flow
collections in frontmatter are out of scope. Keep skill frontmatter to plain
`key: value` lines so the reader and the Claude Code loader agree.

## Why data-driven manifests

Declaring each skill's contract as data (rather than as a central registry, or
as copied-and-edited validator code) keeps the logic single-source while letting
each skill own its own contract. It also gives every skill a small, inspectable
description of what it is made of — a natural substrate for the roadmap's planned
cross-runtime `skill-portability` work, and the reason the same validator can
later cover Codex-packaged skills unchanged (their manifest would simply require
`agents/openai.yaml` instead of forbidding it).
