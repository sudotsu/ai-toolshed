# Compact rapid-prototype handoff

Fill with directly observed facts, omit absent optional links, and keep this short in the user-facing response. Never replace an unverified item with an implied success.

**Demo:** [actual inspected preview URL or local entry/run command; viewer access, if relevant]
**Viewer path and observed result:** [entry → action → result; what was genuinely exercised]
**Checked:** [V1 actual viewer path; V2 actual test provider/data evidence; V3 tests; V4 typecheck/build; V5 code inspection; exact command and pass/fail/unrun as applicable]
**Demo-only / unverified:** [UI-visible fixture/test-mode details; blocked integrations, security, shared state, release requirements and tests not run]
**Git / production:** [starting SHA → final task branch/commit; unmerged PR URL if real; actual preview revision; production unchanged/changed/unknown]
**External effects / cleanup owner:** [preview, seed rows, test uploads, resource cost, scheduled jobs, test messages; none only if verified]
**Rollback:** [least destructive exact steps for owned code and separately for external preview/data/resource; no broad reset/force-push]
**One next owner action, if needed:** [specific authorization or proof gate, not a vague backlog]

Use the [evidence levels and preview checks](../references/verification-and-delivery.md) and keep demo verification separate from production readiness. A passed build is not a tested viewer journey; closing a PR is not preview cleanup.
