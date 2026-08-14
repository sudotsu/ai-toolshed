# Implementation ledger

## <ID> — <Original title>

- **Approval:** <approved|deferred|rejected|accepted-risk|not-applicable>
- **Revalidation:** <confirmed|changed|stale|already-resolved|not-applicable|blocked>
- **Disposition:** <implemented|already-satisfied|retained|deferred|rejected|accepted-risk|not-applicable|blocked>
- **Sequence:** <positive integer>
- **Reason:** <current evidence and decision>
- **Files changed:** <safe relative paths joined by ` | ` or None>
- **Acceptance results:** <criterion => status => evidence entries joined by ` | ` or None>
- **Verification:** <checks joined by ` | ` or None>
- **Notes:** <notes joined by ` | ` or None>
- **Revision record digest:** sha256:<canonical revision finding digest>

<Repeat exactly once for every teardown finding.>

# Convergence findings

### REV-001 — <Title>

- **Source:** <manual review, PR comment, CI, fault injection, platform check, etc.>
- **Severity:** <critical|high|medium|low>
- **Status:** <fixed|already-satisfied|invalid|open|deferred|blocked>
- **Reason:** <current evidence>
- **Files changed:** <safe relative paths joined by ` | ` or None>
- **Verification:** <checks joined by ` | `>
- **Convergence record digest:** sha256:<canonical convergence record digest>

<Remove the example section when there are no convergence findings; keep the `# Convergence findings` heading.>
