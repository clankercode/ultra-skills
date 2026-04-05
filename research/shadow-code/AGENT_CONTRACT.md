# Agent Contract: Operating Inside a Shadow-Style Isolation Pattern

Operating manual for subagents when a shadow-workspace / worktree-style
isolation pattern is active. Organized by pattern because the contracts
differ materially.

---

## Contract A: `adifyr/shadow-code` (Pseudocode-Transform)

**When a subagent would operate inside this:** Only if a worker is asked
to author or modify `.shadow` pseudocode files, or a `.shadows/.skills/<LANG>.md`
skills file on the user's behalf. This is rare — the pseudocode is
normally the user's artifact.

### What the subagent needs to know
1. **Shadow files live at `.shadows/` mirroring the source tree.** A source
   file at `src/components/chat_message.tsx` has its shadow at
   `.shadows/src/components/chat_message.tsx.shadow`.
2. **`context("path1", "path2", ...)` at top of a shadow file** is the
   *only* reserved syntax. It's the context selector for the transform.
   Do NOT add arbitrary imports; the transform will misinterpret them.
3. **Do not include `package.json` / `pubspec.yaml` in `context()`** — the
   extension auto-picks those up.
4. **Skills files are SHOUT-CASE**: `.shadows/.skills/PYTHON.md`,
   `DART.md`, `GO.md`. One per language.
5. **`.shadows/` belongs in `.gitignore`** in shared workspaces.
6. **The transform is a one-shot edit that overwrites the source file.**
   There is no staging, no review gate. If authoring a shadow file, the
   worker should assume its pseudocode will be executed verbatim.

### Handoff
- No handoff protocol. User triggers transform manually in VS Code.
- Workers writing shadow files should emit a crisp, fully-contextualized
  `.shadow` file and stop. Do not attempt to invoke the transform from CLI.

---

## Contract B: Shadow Workspace / Worktree Isolation (the live pattern)

**When a subagent operates inside this:** Whenever the user's environment
uses worktree-per-agent isolation (Claude Code `--worktree`, Cursor 2.0
parallel agents, custom git-worktree harnesses).

### Surface area the subagent must understand

#### 1. Where work lands
- **Working directory is an isolated worktree**, typically at
  `<repo>/.claude/worktrees/<name>/` (Claude Code) or
  `<repo>/../<project>-<feature>/` (sibling-directory community pattern).
- **Branch is pre-created**: Claude Code uses `worktree-<name>`. Do not
  create a new branch unless explicitly asked.
- **`.git` is shared** with the main checkout. History is visible; other
  worktrees' uncommitted work is NOT.
- **Untracked files from main are NOT present** unless `.worktreeinclude`
  copied them. If you expect `.env`, verify it exists before use.

#### 2. Invariants the subagent MUST preserve
- **Never `cd` out of the worktree** to edit files. Edits to the user's
  canonical checkout break isolation.
- **Never `git checkout` a different branch** in the worktree. Worktrees
  are pinned 1:1 to their branch.
- **Never `git worktree remove`** unless explicitly asked. The harness
  manages lifecycle.
- **Never push without explicit instruction.** The worktree's branch may
  be ephemeral.

#### 3. State files to be aware of
- `.claude/worktrees/` (should be gitignored). Workers should not read/write
  across sibling worktrees.
- `.worktreeinclude` at repo root — gitignore syntax, declares files to
  auto-copy on worktree creation. Workers modifying ignored config files
  may need to update this so future worktrees inherit them.
- `.cursor/worktrees.json` (community convention) — setup script per
  worktree (install deps, migrate DB, assign port).
- `contracts.md` / `interfaces.ts` (community convention) — **authoritative
  cross-worktree contract**. A subagent MUST read this before writing any
  code that touches a shared boundary.

#### 4. Coexistence with user edits
- **The user can edit files inside the worktree concurrently.** Workers
  should stat-before-write and re-read after any long operation.
- **The user edits the main checkout freely.** Rebase/merge concerns are
  for a later integration step, not the worker's problem.
- **No shared mutable state (DB, caches) is safe.** Assume any DB writes
  may collide with sibling worktrees if DB is shared.

#### 5. Review gate / handoff protocol
- **Exit signal:** the worker finishes its task and writes its artifacts
  to disk. The harness detects changes.
- **Claude Code exit behavior:** no changes → worktree + branch deleted;
  changes → user prompted to keep/discard. Workers should commit locally
  when their task is done so the harness reliably detects "changes."
- **Integration is NOT the worker's job.** Merge order, conflict
  resolution, and CI verification happen above the worker.
- **No cross-worktree handoff.** If worker A needs output from worker B,
  the orchestration layer must serialize them. Parallel workers cannot
  import each other's uncommitted work.

#### 6. Linting / LSP caveats
- **Inside a Cursor worktree: LSP is not available** (documented
  limitation). Workers should not rely on IDE-level diagnostics.
- **Inside Claude Code worktrees: LSP works** (standard LS runs per
  checkout). But some language servers misbehave with ephemeral branches.
- If running tests, expect a fresh dependency install may be required
  (worktree ≠ node_modules mirror).

### Failure modes the subagent must handle
| Failure | Cause | Worker mitigation |
|---|---|---|
| "File not found: .env" | `.worktreeinclude` missing entry | Flag to leader; don't fabricate |
| Dependency install needed | Fresh checkout with no `node_modules` | Run install script from `.cursor/worktrees.json` if present; otherwise flag |
| Tests hit port conflict | Sibling worktree holds the port | Read per-worktree `.env.local` for offset; don't hardcode |
| Schema migration collision | Parallel DB migrations | ABORT task; flag to leader — this should not have been parallelized |
| Contract drift | Missed `contracts.md` / `INTERFACE.md` | Always read contracts before touching boundaries |
| Stale `origin/HEAD` | Worktree branched from wrong base | Flag to leader; do not `git remote set-head` without permission |
| Worker's edits not detected | Work left uncommitted and crash | Commit locally on significant milestones |

### Minimum invocation-time disclosure a leader must give a worker
When dispatching a worker into a worktree-isolated context, the leader
should include in the worker's brief:
1. The worktree's **absolute path** (not relative).
2. The worktree's **branch name**.
3. The **base branch** the worktree was cut from (so the worker can diff
   meaningfully).
4. The path(s) of the **cross-worktree contract files** the worker must
   honor.
5. Whether the worker is allowed to **commit** (usually yes) and whether
   it may **push** (usually no).
6. Any **per-worktree config** (port offsets, DB schema namespace).
7. **Sibling worktree names** (so the worker knows what's parallel but
   out-of-bounds).

### What the subagent reports back on exit
- Files changed (paths relative to worktree root).
- Whether work was committed (and commit SHA if so).
- Any contract violations or contract ambiguities discovered.
- Any out-of-worktree needs surfaced (dependency adds, schema changes,
  contract revisions) — these cannot be resolved inside the worktree.
