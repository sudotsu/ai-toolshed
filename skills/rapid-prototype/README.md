# rapid-prototype

**Execution skill:** implement and verify the smallest honest, inspectable website or app journey with minimal narration and a straightforward rollback. Optimized for demonstrable progress, not exhaustive planning or production launch certification.

The core [SKILL.md](SKILL.md) deliberately stays compact. Detailed cases are linked only when needed:

| Resource | Why it exists |
| --- | --- |
| [Decision playbook](references/decision-playbook.md) | Fastest viable route, existing/remote/dirty workspace, scope trade-offs and action-specific authority |
| [Verification and delivery](references/verification-and-delivery.md) | Evidence ladder, functional and visual quality floor, safe preview, release/rollback distinction |
| [Handoff template](assets/handoff-template.md) | Concise, evidence-backed result rather than a lengthy status report |
| [Behavioral fixtures](references/behavioral-fixtures.md) | Sixteen executable agent regression scenarios, comparison method and critical-failure conditions |
| [Runtime verification register](references/runtime-validation.md) | Explicit status and evidence gate per CLI/desktop surface |
| [Manifest](skill-manifest.json) and [tests](scripts/test_skill_contract.py) | Static package contract and portable tooling |
| [Codex interface adapter](agents/openai.yaml) | Optional UI metadata; the core requires no proprietary tools |

## When to invoke

Use when the user says “demo this today,” “make it actually work,” “fastest viable build,” “fix the main flow and give me a preview,” or explicitly selects the skill. Do *not* use it to override “planning only,” to run an exhaustive teardown, or to imply readiness for a production launch. Works for websites, PWAs, dashboards, API-backed apps, both new and existing projects; no framework, hosting provider, payment system or repo is mandatory.

Sample: “Use rapid-prototype. Build the smallest working demo of the primary user journey now, verify the viewer path, deliver an isolated preview and unmerged PR if available, and leave main unchanged.”

## Install on the host where the coding runtime executes

| Intended local surface | Entire folder destination | Explicit invocation |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/rapid-prototype/` | `/rapid-prototype` |
| Claude Desktop local Code tab | Local Claude skill source on that desktop/remote host | `/rapid-prototype` or skills picker |
| Codex CLI / IDE | `$HOME/.agents/skills/rapid-prototype/` | `$rapid-prototype` |
| ChatGPT desktop Codex surface | Local Codex Agent Skills source | `@rapid-prototype` / skills UI where available |

Copy **the entire folder**; don't copy only SKILL.md, since its references and tests are part of the package. Windows, WSL, SSH and remote sessions do not automatically share local installs. Local copies do **not** automatically install into ChatGPT Chat/Work or Claude Chat/Cowork. These require separate supported distribution and testing.

The table above identifies *packaging targets*, not demonstrated runtime behavior. See [runtime verification](references/runtime-validation.md): discovery, execution in Claude Code and Codex, and both desktop coding surfaces remain **unverified until their individual evidence exists**. Static CI success does not prove otherwise.

## Structural verification (from repository root)

```bash
python3 tools/skill-validator/skill_validator.py skills/rapid-prototype
python3 -m unittest discover -s skills/rapid-prototype/scripts -p 'test_*.py' -v
```

For behavior, execute all applicable sixteen [fixtures](references/behavioral-fixtures.md) on disposable copies separately in Claude Code and Codex; verify desktop discovery/execution independently. Record host, runtime version, model, exact invocation, prompt, actions/diff, external effects and observed result in the register or linked run evidence. Use matched no-skill runs if comparing effectiveness. A fixture that is blocked or unrun is **not** a pass.

## Scope and limits

A prototype may use synthetic data and test-mode integration **when clearly disclosed** and when doing so does not invalidate the central proof. Production data, live payment/messaging, deployment promotion, destructive migrations, DNS/credential changes and direct main/merge actions require separately applicable authority. A preview URL is not proof of isolation or functional verification. Feature speed never authorizes invented success.

This package is maintained independently of any one client, repository, framework, deployment platform or external account.
