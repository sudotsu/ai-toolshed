# Runtime Portability

Reusable AI Toolshed work targets **Claude Code and Codex by default**. The corresponding local coding surfaces in the Claude Desktop and ChatGPT desktop apps are also required targets whenever they support the artifact type. Platform-specific packaging may differ; silently treating one runtime's configuration as universal is not portability.

This policy was verified against official OpenAI and Anthropic documentation on **2026-08-25**. Recheck the sources below before relying on exact paths, inheritance, invocation syntax, or desktop availability.

## The portability contract

Every new or materially revised skill, plugin, tool, or configuration must:

1. keep its canonical workflow and behavioral rules platform-neutral;
2. support both Claude Code and Codex, unless the artifact is inherently tied to a platform capability and the contribution states that limitation before implementation;
3. assess Claude Desktop and the ChatGPT desktop app explicitly, using the exact surface names below;
4. isolate vendor metadata, permissions, hooks, connectors, and installation logic in adapters rather than leaking them into the portable core;
5. document installation, invocation, known differences, and unverified behavior per target; and
6. validate every claimed target independently instead of inferring parity from one successful runtime.

“Not applicable” is valid only when the surface cannot consume that artifact type. It requires a concrete platform reason. “Untested” means unverified, not supported.

## Exact skill surfaces

The shared `SKILL.md` directory format is the portable source. Installation and invocation differ:

| Target | Personal skill location | Project skill location | Explicit invocation | What the local copy reaches |
| --- | --- | --- | --- | --- |
| Claude Code | `~/.claude/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `/<name>` | Claude Code CLI sessions on that host |
| Claude Desktop — Code tab | Same paths as Claude Code for local sessions | Same paths as Claude Code | `/<name>` or the Skills picker | Local Code-tab sessions; SSH sessions read the remote host's personal path |
| Codex CLI / IDE extension | `$HOME/.agents/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | `$<name>` | Codex sessions running on that host |
| ChatGPT desktop app — Codex | Same local Agent Skills source used by Codex | Same repository source used by Codex | `$<name>` or the Skills UI | The Codex coding surface in the desktop app |

Host boundaries matter. A skill installed inside WSL is not automatically installed for a Windows desktop runtime, and a Windows-host copy is not automatically present inside WSL, SSH, or a cloud session.

Local installation does **not** publish the skill to every conversational surface:

- Claude Desktop's local **Code** tab shares Claude Code configuration and skills. Claude **Chat**, **Cowork**, and cloud sessions use account-enabled or synced skills and have different execution limits.
- Standalone Agent Skills are available to the **Codex** surface in the ChatGPT desktop app. ChatGPT **Chat** and **Work** across web, desktop, and mobile receive reusable skills through plugin distribution rather than a copied local folder.

Do not claim those non-local surfaces until the account-sync or plugin package has been built and tested there.

## Instruction and configuration surfaces

Instruction files follow the coding runtime, including inside the local desktop coding surface:

| Concern | Claude Code and Claude Desktop Code | Codex and ChatGPT desktop Codex |
| --- | --- | --- |
| Global instructions | `~/.claude/CLAUDE.md` | First non-empty `~/.codex/AGENTS.override.md`, then `~/.codex/AGENTS.md` |
| Project instructions | `CLAUDE.md`, `.claude/CLAUDE.md`, and `CLAUDE.local.md` according to Claude's discovery rules | First non-empty `AGENTS.override.md`, then `AGENTS.md`, then configured fallbacks in each directory |
| Personal skills | `~/.claude/skills/` | `$HOME/.agents/skills/` |
| Project skills | `.claude/skills/` | `.agents/skills/` |
| Vendor adapter | Claude plugin metadata, hooks, settings, and MCP configuration | `agents/openai.yaml`, OpenAI plugin metadata, connectors, and Codex configuration |

Claude Desktop's Code tab and the Claude Code CLI read the same `CLAUDE.md`, settings, hooks, and local skills for local sessions. The standalone Claude Code CLI does not read `claude_desktop_config.json`; that file is a Desktop-specific MCP source.

ChatGPT Custom Instructions, Memory, and Project Instructions belong to ChatGPT Chat/Work. They are not substitutes for the `AGENTS.md` instruction chain used by the Codex coding surface. See [Persistent & Enforced Context](persistent-enforced-context/platform-implementations.md) for the behavioral-layer mapping.

This repository keeps its minimal portability kernel in the root [`AGENTS.md`](../AGENTS.md). Root [`CLAUDE.md`](../CLAUDE.md) imports that same kernel, so Codex and Claude Code receive one canonical set of project invariants without maintaining two drifting copies.

## Portable core and adapters

Keep the common package consumable by both runtimes:

```text
skill-name/
├── SKILL.md                 # portable workflow and shared frontmatter
├── scripts/                 # runtime-neutral scripts where practical
├── references/              # shared evidence and guidance
├── assets/                  # shared templates and resources
└── agents/
    └── openai.yaml          # optional OpenAI-only UI/tool adapter
```

Platform-specific files are allowed when they add a real capability. They must be optional from the other runtime's perspective and must not become an undeclared dependency of `SKILL.md`.

Use platform-neutral trigger language in the shared description. Say “when the user asks” or “when the agent must,” not “when Codex must” or “when Claude must.” Put `$skill-name`, `/skill-name`, tool identifiers, vendor-only frontmatter, and connector configuration in the relevant adapter or installation documentation.

## Validation gate

For every published skill:

- the internal `skill-manifest.json` must declare all four local targets;
- the generic validator must pass the shared package, frontmatter, links, scripts, and declared tests;
- runtime-specific metadata must validate independently and remain optional to the other runtime;
- trigger, refusal/authority, artifact, and failure-path prompts must be run separately in Claude Code and Codex after material behavioral changes;
- desktop discoverability must be checked separately from CLI discoverability when desktop support is claimed; and
- results must identify the exact runtime, version, host, session type, installed path, prompt fixture, and raw evidence.

Static package validation proves structural compatibility, not behavioral parity. A passing Claude Code run does not prove Codex behavior, and a passing CLI run does not prove desktop discovery.

## Official sources

OpenAI:

- [Build skills](https://developers.openai.com/codex/skills)
- [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [ChatGPT desktop app](https://developers.openai.com/codex/app)

Anthropic:

- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Claude Code on desktop](https://code.claude.com/docs/en/desktop)
- [Create plugins](https://code.claude.com/docs/en/plugins)
