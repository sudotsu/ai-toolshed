# Platform Implementations

Platform behavior changes. The mappings below were verified against official product documentation on **2026-08-25**. Recheck the linked sources before relying on exact paths, limits, inheritance, or availability.

## Cross-platform map

| Concern | ChatGPT | Claude Code | Codex |
| --- | --- | --- | --- |
| Global behavioral contract | Custom Instructions = CORE | `~/.claude/CLAUDE.md` = CORE + personal CODING | `~/.codex/AGENTS.md` = compressed CORE + CODING |
| Persistent user context | Memory / Memory Summary = USER CONTEXT | Auto memory or deliberately maintained user context | Memory features where available; keep behavioral rules in `AGENTS.md` |
| Project behavior | Project Instructions = PROJECT KERNEL + local rules | Project `CLAUDE.md` / `.claude/CLAUDE.md` = local rules; global files also load | Project and nested `AGENTS.md` = local rules in an ordered chain |
| Long reference material | Project Sources | Repository docs, skills, or imported references | Repository docs, skills, or files read on demand |
| Historical evidence | Chat history, project chats, search, or external episodic retrieval | Session history and retrieval tooling; auto memory is a synthesis, not the transcript | Session history and retrieval tooling; memory is not a provenance-complete archive |

No platform collapses all of these concerns safely into one file.

## ChatGPT

There is no single first-class `CHATGPT.md` equivalent. The practical mapping is:

```text
Normal chat
    Custom Instructions = CORE
    Memory = USER CONTEXT
    Current conversation = task state

Project chat
    Project Instructions = PROJECT KERNEL + local behavior
    Project Sources = specifications, evidence, examples, long rationale
    Project chats / memory = continuing project context
```

OpenAI describes Custom Instructions as direct guidance about what ChatGPT should consider in its responses. Memory is a continually updated synthesis of useful context and its summary may not expose everything remembered. Those are different maintenance and reliability models, so Memory should reinforce a behavioral rule rather than being its only source of truth.

Current OpenAI documentation also states that project instructions apply only inside their project and override global Custom Instructions. That platform-specific override is why a small repeated [Project Kernel](project-kernel.md) is warranted in ChatGPT even though indiscriminate duplication is harmful elsewhere.

Use:

- [Ready-to-use ChatGPT configuration](chatgpt-configuration.md) for the global Custom Instructions and Memory Summary;
- [PROJECT KERNEL](project-kernel.md) at the beginning of project instructions; and
- project sources for specifications, reports, examples, and this longer rationale.

Official sources:

- [ChatGPT Custom Instructions](https://help.openai.com/en/articles/8096356-chat-preferences-for-chatgpt)
- [Memory FAQ](https://help.openai.com/en/articles/8590148-memory-and-projects)
- [Projects in ChatGPT](https://help.openai.com/en/articles/10169521)

## Claude Code

Claude Code uses additive instruction discovery rather than ChatGPT's project-instruction override model. Current Anthropic documentation distinguishes user instructions at `~/.claude/CLAUDE.md`, shared project instructions at `./CLAUDE.md` or `./.claude/CLAUDE.md`, local project preferences at `./CLAUDE.local.md`, and auto memory stored per repository. Discovered `CLAUDE.md` files are concatenated into context, with more specific files later in the sequence.

That produces this composition:

```text
~/.claude/CLAUDE.md
    = CORE + durable personal CODING policy

project CLAUDE.md
    = commands, architecture, project-only constraints, and traps

CLAUDE.local.md
    = private project-specific preferences or local endpoints

auto memory
    = learned preferences, corrections, and project context
```

Do not duplicate the entire global contract in every project file. Both copies load, consume context, and can drift. Restate a global invariant only when it is easy to miss and expensive to violate in that project, and state the project-specific consequence briefly.

Claude Code's official guidance currently targets fewer than 200 lines per `CLAUDE.md` and warns that longer files consume more context and reduce adherence. Moving text into `@` imports may improve organization, but imported content still loads at launch; it does not solve instruction dilution. Use path-scoped rules or skills when guidance should load only for a subset of work.

Auto memory is not the same thing as `CLAUDE.md`: Claude writes and updates it as learned context, while the user writes `CLAUDE.md` to guide behavior. Anthropic explicitly describes both as context rather than hard enforcement. Use permissions, managed settings, hooks, or other deterministic controls when an action must be blocked regardless of model judgment.

Official source:

- [How Claude remembers your project](https://code.claude.com/docs/en/memory)

## Codex

Codex's native instruction file is `AGENTS.md`. Current OpenAI documentation describes an ordered chain:

1. Codex reads `AGENTS.override.md` or `AGENTS.md` from the Codex home directory for global guidance.
2. From the project root toward the working directory, it reads at most one instruction file per directory.
3. Files closer to the working directory appear later and can override earlier guidance.

Use this composition:

```text
~/.codex/AGENTS.md
    = CORE + CODING, aggressively compressed

repository AGENTS.md
    = project commands, constraints, authority boundaries, and verification

nested AGENTS.md
    = rules genuinely specific to that subtree
```

Keep general conversation preferences out of project files unless they are necessary to the project's work. Keep machine state out of the global behavioral contract when the runtime can discover it or when it belongs in local context. Search for existing `AGENTS.md` files before adding another so a new file does not accidentally alter instruction precedence.

Official source:

- [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

## Project sources and historical retrieval

Sources and history solve different problems:

- A **project source** is selected reference material: requirements, reports, examples, evidence, or long rationale.
- **Historical or episodic retrieval** searches prior conversations or session records when the current summary is insufficient.
- **Memory** is a compact, evolving context layer.
- **Instructions** tell the system how to behave.

Do not assume a model will retrieve a source on every turn merely because the source exists. Put the minimum behavioral invariant in the instruction surface, keep the full reasoning in a source, and retrieve the original history when provenance or exact wording matters.
