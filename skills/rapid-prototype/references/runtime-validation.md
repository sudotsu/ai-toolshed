# Runtime verification register

**This file records actual evidence, not aspirational compatibility.** The four manifest targets identify intended local packaging/discovery targets under the repository portability contract. They do not assert successful agent behavior or desktop discovery. Do not mark a runtime verified merely because it accepts the SKILL.md format or the Python package validator passes.

| Surface | Packaging target | Behavioral fixtures | Discovery | Status |
| --- | --- | --- | --- | --- |
| Claude Code CLI | `~/.claude/skills/rapid-prototype/` | Not run | Not checked on target host | **UNVERIFIED** |
| Codex CLI/IDE | `$HOME/.agents/skills/rapid-prototype/` | Not run | Not checked on target host | **UNVERIFIED** |
| Claude Desktop local Code tab | Claude local skill source | Not run | Not checked on target desktop | **UNVERIFIED** |
| ChatGPT desktop Codex surface | Codex local skill source | Not run | Not checked on target desktop | **UNVERIFIED** |

Static structural tests and GitHub CI: see the current PR check run rather than copying historical statuses here. They are a **different evidence category** from the matrix above.

## What makes a runtime verified

1. Install the exact branch/commit bundle on the host where that runtime executes. Record version/model, OS, tool permissions and invocation.
2. Confirm explicit skill invocation loads the intended version. Check automatic selection using clear positive trigger and planning-only negative trigger.
3. Execute applicable [behavioral fixtures](behavioral-fixtures.md) in disposable environments, retain prompt/action trace/diff/actual outcome, and inspect any external effects.
4. Fail on any critical-gate violation (unapproved main/production action, destroyed owner work, fake integration proof, fabricated test/deployment or leaked secret). A blocked/unrun fixture is not verified.
5. Independently test desktop discovery and its actual execution surface. CLI behavior does not prove it.
6. Add dated, reviewer-checkable evidence links or artifact paths and update the status cell. Re-run affected cases whenever the skill's behavioral contract changes.

Do not claim this skill is installed in ChatGPT Chat/Work or Claude Chat/Cowork just because local folders exist. Distributable plugin/account installation is a separate project with its own verification.

## Current release gate

The skill package can be reviewed and its static CI can pass while runtime portability remains **unverified**. Keep this distinction explicit in PR and user-facing communication; do not treat this register as waived testing.
