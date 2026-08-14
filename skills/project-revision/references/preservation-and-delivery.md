# Preservation, Git, and Delivery Discipline

Use this reference before product edits and before any commit, push, pull-request, merge, release, or deployment claim.

## Contents

1. Baseline capture
2. Existing work preservation
3. Safe edit strategy
4. Attribution and changed-path reconciliation
5. Commit and artifact sequencing
6. Push, PR, CI, merge, and release claims

## 1. Baseline capture

Capture:

- repository root, remote, branch, and immutable head;
- staged, unstaged, and untracked paths;
- submodule and worktree state when applicable;
- file modes and exact bytes for pre-existing changed paths that approved work may touch;
- relevant toolchain versions and baseline check results;
- existing PR, review, CI, issue, and release state when in scope.

Store raw baseline data outside the repository artifact in a restricted temporary location. Put only sanitized summaries and hashes in `project-revision/`.

## 2. Existing work preservation

Never reset, clean, checkout over, stash, discard, or broadly reformat pre-existing work. Do not assume an uncommitted path belongs to this run.

Before editing a pre-existing changed path:

1. understand the user's current intent from the diff and surrounding code;
2. preserve exact bytes and mode;
3. design a semantic merge of both intents;
4. stop when safe reconciliation is not possible without owner input.

After editing, compare baseline intent and final behavior—not only textual presence. Tests passing does not prove unrelated work was preserved.

## 3. Safe edit strategy

Prefer small, reviewable vertical changes. Search all usages before shared-code edits. Avoid opportunistic refactors, broad formatting, generated-file churn, dependency upgrades unrelated to acceptance criteria, and cleanup that obscures attribution.

Define a rollback approach before risky batches. Rollback must remove only changes attributable to the batch; it must not discard user work.

## 4. Attribution and changed-path reconciliation

Every final product path must map to:

- one or more approved teardown finding IDs;
- one or more fixed convergence finding IDs; or
- preserved pre-existing user work.

Every artifact-only path must map to revision-record maintenance. Unmapped product changes are scope drift and block completion.

Compare final staged, unstaged, and untracked inventories with the baseline. Investigate every unexpected path, mode change, generated artifact, lockfile change, and deletion.

## 5. Commit and artifact sequencing

A revision artifact cannot reliably name the hash of the commit that contains itself.

Use one of two honest states:

### Working-tree state

Use when product or artifact changes remain uncommitted. Record the implementation endpoint as an explicit working-tree state and mark commit/push/PR facts accurately.

### Artifact-only descendant

Use when:

1. product changes are committed and verified at immutable product endpoint `P`;
2. no product code changes after `P`;
3. the revision artifact is updated in a later artifact-only commit `A`;
4. the handoff records `P` as `implementation_end_revision` and externally records `A` as the final repository head.

Re-run current-head review after any product-code change. An artifact-only edit does not require re-running product behavior unless it changes executable content.

## 6. Push, PR, CI, merge, and release claims

Record facts only after direct verification:

- `committed: verified` requires the expected commit to exist locally;
- `pushed: verified` requires the expected remote ref to contain it;
- `pull_request_updated: verified` requires reading the current PR head/body/state after the final push;
- `merged: verified` requires current merged state and resulting target-branch head;
- CI claims require the current head and named jobs, not an earlier commit;
- release readiness is not deployment or publication;
- merge readiness is not merge authorization;
- a local build is not a release, deployment, migration, or production verification.

Refresh remote and delivery evidence after the last product or artifact commit. Do not repeat stale PR head, CI, or review claims from an earlier revision.
