# AI Toolshed Project Instructions

## Quality bar

- Read and follow [`docs/quality-bar.md`](docs/quality-bar.md) before adding or materially revising a reusable skill, plugin, tool, configuration, or platform guide.
- Default standard: ship reusable work only when there is a defensible path to matching or exceeding strong current performers in its domain on the dimensions that actually matter. Do not optimize for feature count, imitate competitors, or declare success from internal validation alone.
- Validation is necessary but not sufficient. Green tests/CI prove contract and implementation correctness; they do **not** prove domain quality, judgment quality, market parity, or user value.
- Treat release readiness as separate gates: code/contract correctness, methodological coverage, evidence quality, real-world forward testing, and empirical benchmark quality when making parity/superiority claims.
- Before completion, actively search for missed opportunities, blind spots, standard practices, stronger alternatives, and domain-specific failure modes. Record important omissions or unproven claims instead of silently treating them as complete.
- Experimental/prototype work is allowed when explicitly labeled as such. Do not present it as flagship or finished until it meets the applicable quality bar.

## Runtime portability

- Read and follow [`docs/runtime-portability.md`](docs/runtime-portability.md) before adding or materially revising a reusable skill, plugin, tool, configuration, or platform guide.
- Reusable work must target both Claude Code and Codex by default and must assess the applicable Claude Desktop and ChatGPT desktop coding surfaces explicitly.
- Keep one platform-neutral core. Isolate vendor-specific metadata, installation, permissions, hooks, connectors, and invocation syntax in adapters or platform documentation.
- A platform-specific contribution is acceptable only when it depends on an exclusive capability. Document the concrete limitation and closest supported equivalent; never imply untested parity.
- Before completion, run the repository's native validation and preserve separate evidence for every runtime or desktop target whose behavior is claimed.
