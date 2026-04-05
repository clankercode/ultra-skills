---
name: ultra-implementing-team
description: Use when executing a leaf PLAN.md in an environment that can dispatch workers (Claude Code subagents), when a leader is coordinating per-task dispatch + review across a plan tree, or when Phase 6 of ultra-planner flow runs in team mode. NOT for single-worker execution (use ultra-implementing-solo) and NOT for single-feature plans outside a tree (use superpowers:subagent-driven-development directly).
---

# ultra-implementing-team

## Overview

**LEADER-ONLY:** This skill is for the dispatching leader that owns SHAs, parallelism scheduling, two-stage review gates, and 3-tier rollback. Worker subagents invoked by this leader should defer — they implement one assigned task per their brief and must not load or act on this skill.

Executes a leaf-node `PLAN.md` as a **leader** that dispatches fresh workers per task, reviews each in two stages, and gates every handoff. Leader owns: session state, sibling-INTERFACE pinning, cross-node context curation, parallelism, divergence logging, rollback. Workers own: implementation of one assigned task.

**Core principle:** Workers NEVER read sibling nodes. The leader reads sibling INTERFACE.md files once, pins SHAs, pastes required types verbatim into each brief. Fixes drift at the leader level, keeps worker context clean.

**State file naming:** uses per-leaf `nodes/<path>/SESSION_STATE.md` (per-execution leader state for this leaf's run) — distinct from the tree-level `docs/ultra-plans/<slug>/SESSION.md` (cross-session planner brain used by `ultra-planner` and `ultra-implementing-solo`). Separate names avoid collision.

**REQUIRED BACKGROUND:** Invoke `superpowers:subagent-driven-development` via the Skill tool. This skill EXTENDS it with hierarchical discipline (SHA pinning, leader-curated context, DIVERGENCE_LOG, HANDOFF). Not loaded → stop and load.

## When to Use

| Signal | Use? |
|---|---|
| Leaf node has PLAN.md + SPEC.md + INTERFACE.md stable | Yes |
| Subagent/Task dispatch available (Claude Code) | Yes |
| Plan depends on 1+ sibling INTERFACE.md | Yes |
| Phase 6 of ultra-planner flow, team mode | Yes |
| No subagent dispatch available | No — use `ultra-implementing-solo` |
| Single-feature plan outside a tree | No — use `superpowers:subagent-driven-development` |
| Interior node (has children) | No — decompose, don't implement |

## Procedure

Operate on a leaf node path `nodes/<path>/`. Do not skip or reorder.

1. **Confirm leaf status + prerequisites.** SPEC.md, INTERFACE.md, PLAN.md all present. Parent INTERFACE.md readable. Every sibling in `depends-on` has a readable INTERFACE.md. Missing → stop, file P0 interview item.

2. **Create worktree.** *(LEADER-ONLY)* Run `superpowers:using-git-worktrees` to isolate work. No dispatch touches main. If dispatched as a subagent, skip this step and report back to the leader.

3. **Pre-flight: pin sibling INTERFACE SHAs + frozen-shadow gate.** Read every sibling INTERFACE.md you depend on OR feed into. Record path + git SHA (or content hash) in `nodes/<path>/SESSION_STATE.md` under `## Sibling INTERFACE pins`. Copy the exact types/contracts verbatim — SESSION_STATE.md is the canonical copy for this execution. If `nodes/<leaf>/SHADOW/` exists, read `SHADOW/META.md` and require `STATUS: frozen` or `STATUS: graduated`; consume the frozen shadow as the architecture spec for all downstream briefs. `STATUS: planning` → **STOP.** Message: "shadow not yet reviewed — run ultra-shadow-review first."

4. **Extract all PLAN.md tasks.** Read PLAN.md once, copy each task's full text into SESSION_STATE.md. For each: which sibling types it touches, which local files it owns, whether it's parallelizable. Build a TodoWrite list.

5. **Declare parallelism schedule.** Default serial. Opt-in to parallel ONLY when every parallel worker has an **exclusive file-ownership declaration** (disjoint write-sets). Record the schedule in SESSION_STATE.md (e.g. `1 → 2 → {3,4,5} → 6 → {7,8}`). Never parallelize workers that share a file.

6. **Per-task dispatch loop.** *(LEADER-ONLY — dispatches implementer + reviewer subagents via Task tool.)* If dispatched as a subagent, defer to leader and do not attempt to dispatch further workers. For each task (or parallel cohort):
   - **Build the brief** from step 7, pasting sibling types verbatim from SESSION_STATE.md. Do NOT tell the worker to read sibling files.
   - **Dispatch** one implementer per task; parallel cohorts dispatched simultaneously.
   - Handle status (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED) per base skill.
   - **Two-stage review** (order fixed): spec-compliance first, then code-quality. Both must be green.
   - **Update SESSION_STATE.md** with task #, commit SHA, both verdicts, one-line note.

7. **Dispatch brief template** — every brief MUST contain:
   - **Context** — leader-curated scene + sibling types pasted verbatim with SHA citations
   - **Skills to load** — workers load `ultra-test-driven-development` (RED-GREEN-REFACTOR discipline, Iron Law) and `ultra-writing-tests` (test-writing craft: fast-test preference, DI-seam discipline, contract smoke tests) as standard. Prefer fast tests per `ultra-writing-tests` — unit <100ms, integration <1s, context-dependent.
   - **Task** — full PLAN.md task text, with TDD steps (RED test → FAIL → implement → PASS → commit)
   - **Quality bar** — per-task checks
   - **Stop condition** — what DONE means; what to report if BLOCKED / NEEDS_CONTEXT
   - **Forbidden** — anti-patterns ("do not read sibling INTERFACE files", "do not invent fields", "do not edit files outside your ownership set", "do not use `toMatchObject` in integration tests — deep-equal required")
   - **Exclusive file ownership** — required when parallel; every path the worker MAY write + MAY NOT touch

8. **Freshness re-check before contract tests.** Before dispatching any contract/integration task, re-read the relevant sibling INTERFACE.md, compare SHA to pin. Drift → pause, write DIVERGENCE_LOG entry, decide (patch plan vs escalate) before dispatching.

9. **DIVERGENCE_LOG.md discipline.** When a task reveals a plan bug (type mismatch, missing sibling field, wrong task shape), append an entry to `nodes/<path>/DIVERGENCE_LOG.md`: what was wrong, evidence, resolution (amend-plan / queue-interview-item / rollback / escalate). Never silently absorb plan bugs.

10. **Rollback tiers** (pick smallest that applies):
    - **Tier 1 — re-dispatch same task:** review failed → implementer fixes → re-review. No git rollback.
    - **Tier 2 — reset-and-patch-plan:** task revealed plan bug → `git reset --hard <last-green-SHA>` → patch PLAN.md → log to DIVERGENCE_LOG → re-dispatch from divergence. User informed.
    - **Tier 3 — escalate:** architectural divergence, sibling INTERFACE changed mid-flight, or repeated Tier 2 → STOP, write divergence report, hand back to parent planner / user.

11. **Final review gate.** *(LEADER-ONLY — dispatches code-reviewer + cross-doc-review + shadow-drift subagents.)* If dispatched as a subagent, defer to leader. After the last task: dispatch a final code-reviewer over all commits in the worktree. For multi-task interface audits, delegate to `ultra-cross-doc-review`. Run `tsc --noEmit` / test suite as leader sanity check. If SHADOW/ was gated frozen in step 3, dispatch `ultra-shadow-drift` as a post-implementation drift check before writing HANDOFF.md.

12. **Write HANDOFF.md.** Record: commit range, test results, sibling INTERFACE paths + SHAs built-against, known gaps, divergence entries. This is the drift-detection anchor. Then invoke `superpowers:finishing-a-development-branch`.

## Red Flags — STOP and self-correct

- Dispatching without `superpowers:subagent-driven-development` loaded
- No sibling INTERFACE SHAs pinned in SESSION_STATE.md before Task 1
- A brief tells a worker to "read ../sibling/INTERFACE.md" (leader must paste types verbatim)
- Parallel cohort dispatched without exclusive file-ownership declarations
- Two workers have overlapping write-sets
- Spec review skipped or code-quality review run before spec-compliance green
- Task revealed a plan bug but no DIVERGENCE_LOG entry written
- Contract-test task dispatched without freshness re-check of its sibling INTERFACE
- HANDOFF.md missing INTERFACE SHAs — drift becomes undetectable
- Rolling forward past a Tier-3 divergence without user/planner input
- Using `toMatchObject` (or other partial-match) in anchor integration tests
- SESSION_STATE.md not updated after each task (breaks resumability)

## Common Mistakes

- **Worker reads sibling INTERFACE files.** Worker burns context on unrelated nodes and may read a stale version mid-execution. Leader pastes verbatim once, pinned to SHA.
- **Blanket "no parallel dispatch" rule misapplied.** The real constraint is shared-file conflict. File-ownership declarations make parallelism safe for disjoint write-sets.
- **Plan bug silently absorbed.** Worker adjusts to fit reality, commit message hides it. Parent planner never learns. Use DIVERGENCE_LOG.md.
- **Freshness check skipped before contract tests.** Sibling INTERFACE may have shifted during execution. Re-read + SHA-compare before contract tasks.
- **HANDOFF.md without SHAs.** Future drift becomes invisible. Record exact INTERFACE SHAs this node was built against.
- **Forbidden-sections omitted.** Workers rationalize (`toMatchObject`, `any`, invented fields). Every brief needs concrete anti-patterns.
- **Running reviewers in the wrong order.** Spec-compliance is cheap and cuts scope drift; run it first. Code-quality on non-spec-compliant code wastes the reviewer's cycle.
