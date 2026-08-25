# AI Toolshed Project Instructions

## Runtime portability

- Read and follow [`docs/runtime-portability.md`](docs/runtime-portability.md) before adding or materially revising a reusable skill, plugin, tool, configuration, or platform guide.
- Reusable work must target both Claude Code and Codex by default and must assess the applicable Claude Desktop and ChatGPT desktop coding surfaces explicitly.
- Keep one platform-neutral core. Isolate vendor-specific metadata, installation, permissions, hooks, connectors, and invocation syntax in adapters or platform documentation.
- A platform-specific contribution is acceptable only when it depends on an exclusive capability. Document the concrete limitation and closest supported equivalent; never imply untested parity.
- Before completion, run the repository's native validation and preserve separate evidence for every runtime or desktop target whose behavior is claimed.
