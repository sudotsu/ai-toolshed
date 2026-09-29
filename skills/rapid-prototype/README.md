# rapid-prototype

Build and verify one demonstrable website/app journey quickly. This is an execution skill, not a product teardown, complete QA program or production launch approval.

Package: [SKILL.md](SKILL.md), [compact handoff](assets/handoff-template.md), [behavioral fixtures](references/behavioral-fixtures.md), `skill-manifest.json`, and optional Codex UI metadata in `agents/openai.yaml`.

## Install on the host where the coding runtime runs

| Local surface | Place the entire `rapid-prototype/` folder under | Invoke |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `/rapid-prototype` |
| Claude Desktop local Code tab | `~/.claude/skills/` | `/rapid-prototype` or skills picker |
| Codex CLI / IDE | `$HOME/.agents/skills/` | `$rapid-prototype` |
| ChatGPT desktop Codex surface | `$HOME/.agents/skills/` | `@rapid-prototype` or skills UI |

Windows, WSL, SSH and cloud sessions do not automatically share local installs. This folder does **not** independently install a skill in Claude Chat/Cowork or ChatGPT Chat/Work; those surfaces require separate supported distribution. Treat desktop discoverability and runtime behavior as unverified until separately tested.

Sample invocation: “Use rapid-prototype to build the smallest working demo of the primary user journey, verify it, give me an isolated preview and unmerged PR; leave main unchanged.”

## Structural verification (from repository root)

```bash
python3 tools/skill-validator/skill_validator.py skills/rapid-prototype
python3 -m unittest discover -s skills/rapid-prototype/scripts -p 'test_*.py' -v
```

Then execute the eight [behavioral fixtures](references/behavioral-fixtures.md) in both Claude Code and Codex; separately verify desktop discovery. Record environment, prompt and raw evidence. Static validation establishes package structure, **not** behavioral parity, real deployment or live testing.

Known limit: deadlines and missing credentials can narrow the demo, never justify false claims or unapproved production side effects.
