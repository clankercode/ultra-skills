---
name: ultra-implementing-solo
description: Use when executing a leaf PLAN.md in a solo environment with no subagent dispatch (Codex, OpenCode, or any harness without Task tool), when you are the sole executor of a TDD task list, or as Phase 6 of the ultra-planner flow in solo mode. NOT for environments with subagent dispatch (use `superpowers:subagent-driven-development`) and NOT for writing the plan itself (use `ultra-writing-plans`).
---

# ultra-implementing-solo

## Overview

Executes a leaf-node `PLAN.md` when YOU are the sole executor — no fresh subagents per task, no parallel review roles. Adapts `superpowers:subagent-driven-development` to single-agent reality: strict per-task RED→GREEN, sibling-contract pinning, disk-backed session state, and loud escalation when the plan is wrong.

**Core principle:** One task at a time, one RED per task, no invented cross-node types, no silent plan patches. The solo executor has no second reviewer, so the discipline must be in the procedure.

**REQUIRED BACKGROUND:** Invoke `superpowers:subagent-driven-development` and `superpowers:test-driven-development` via the Skill tool. This skill EXTENDS them for the no-dispatch case. If either is not loaded → stop and load.

## When to Use

| Signal | Use? |
|---|---|
| Executing a leaf PLAN.md in Codex / OpenCode / solo harness | Yes |
| Phase 6 of ultra-planner, subagent dispatch unavailable | Yes |
| You are the sole executor of a TDD task list | Yes |
| Claude Code with Task tool available | No — use `superpowers:subagent-driven-development` |
| Writing a new PLAN.md | No — use `ultra-writing-plans` |
| Interior (non-leaf) node | No — decompose first |

## Code Standards

**REQUIRED:** Load `ultra-code-standards` via the Skill tool. It defines LOC limits (1k soft / 2k hard), duplication rules, refactoring discipline, naming, separation of concerns, and the mechanical LOC check. Every task's GREEN and REFACTOR phases must satisfy those standards. If `ultra-code-standards` is not loaded → stop and load it.

## Procedure

Operate on leaf node path `nodes/<path>/` with PLAN.md present. Do not skip or reorder.

1. **Load background skills.** Invoke `superpowers:subagent-driven-development`, `superpowers:test-driven-development`, and `ultra-code-standards` via the Skill tool. Also load `ultra-test-driven-development` for the RED-GREEN-REFACTOR lifecycle discipline (Iron Law, rationalizations table) and `ultra-writing-tests` for test-writing craft (fast-test preference, DI-seam discipline, test-complicity guard). The Iron Law (no production code without a failing test first) is non-negotiable in solo mode.

2. **Pin sibling INTERFACE.md paths.** Read PLAN.md; enumerate every sibling INTERFACE.md from its "Cross-node references" header. For each, record path + last-modified timestamp + SHA-256 in `SESSION.md` under `Pinned siblings`. If any referenced sibling is **unreachable or missing** → **STOP. Do not invent types.** Log to `DIVERGENCE_LOG.md` and escalate to the leader. Inventing cross-node shapes is the top RED-baseline failure; it is forbidden.

3. **Freshness check.** For each pinned sibling, compare its timestamp to PLAN.md's. If any sibling is newer → write a `Freshness warning` to `DIVERGENCE_LOG.md` and verify the types you'll consume still match the plan's assumptions. Drifted → escalate.

4. **Shadow-spec gate (pre-flight).** If `nodes/<leaf>/SHADOW/` exists, read `SHADOW/META.md` and require `STATUS: frozen` or `STATUS: graduated` — consume the frozen shadow as the architecture spec BEFORE writing real code. `STATUS: planning` → **STOP.** Message: "shadow not yet reviewed — run ultra-shadow-review first." No SHADOW/ → continue. Post-implementation drift checks: dispatch `ultra-shadow-drift` after step 10.

5. **Initialise SESSION.md.** Write current task index (1), task count, pinned siblings block, next action. This file is your cross-task brain — update after every task.

6. **Per-task loop (strict TDD, one task at a time).** For each task in PLAN.md, in order:
   - **a.** Read ONE task. No peeking ahead to batch. Extract acceptance criteria.
   - **b.** Write the failing test. Use real types from pinned siblings — never re-derive a shape from a description.
   - **c.** Run and VERIFY RED. Confirm it fails for the expected reason (missing code, not typo). Passes immediately → test is wrong, rewrite.
   - **d.** Write minimal code to pass. No speculative fields, no extras.
   - **e.** Run and VERIFY GREEN. Re-run the full suite so you catch regressions. Prefer fast tests per `ultra-writing-tests` — unit <100ms, integration <1s, context-dependent.
   - **f.** REFACTOR under green. Apply Code Standards: check LOC limits on touched files, extract duplicated logic, improve names and structure in code you touched. Stay green on every edit.
   - **g.** Commit with message `task N: <task name>`.
   - **h.** Update SESSION.md: task index, commit SHA, any open plan gaps, next action.

7. **Periodic self-review (every 3 tasks or after any task touching 3+ files).** Pause implementation. Review all code written since the last self-review against:
   - **Bugs and security issues** — race conditions, injection, unvalidated input, resource leaks.
   - **Code Standards compliance** — LOC limits, duplication, separation of concerns, naming.
   - **Refactor opportunities** — patterns that emerged across tasks, abstractions waiting to be extracted.
   - **Acceptance criteria** — re-read the PLAN.md tasks completed so far; verify each acceptance criterion is met by a test.

   If issues found: fix them now (self-fix loop, max 2 iterations). Each fix must maintain GREEN on the full suite. Commit fixes as `review-fix: <summary>`. If issues persist after 2 iterations → log to DIVERGENCE_LOG.md and continue (do not block indefinitely on polish).

   Record the review in SESSION.md: `Self-review after task N: [PASS | N issues fixed | N issues deferred]`.

8. **When the plan is wrong during a task:** STOP writing code. Log the gap in `DIVERGENCE_LOG.md` as `{task, issue, route}` and pick one route:
   - **amend-plan-and-continue** — small unambiguous fix (ordering unspecified, obvious sentinel). Write the amendment into PLAN.md (or an `AMENDMENTS` section), log, continue.
   - **queue-interview-item** — user-visible decision (header copy, sort order with semantic impact). Append to `INTERVIEW_QUEUE.md` at P1, pick a default, continue with it noted.
   - **escalate-to-leader** — contract drift, missing cross-node type, contradictory acceptance criteria. Stop, log, set SESSION.md next action to "awaiting-leader", surface to user.
   **Never** silently fill plan gaps. Silent patching is the second RED-baseline failure.

9. **Before any contract smoke test task,** re-open the pinned sibling INTERFACE.md and re-compare its hash. Drifted since pinning → escalate per step 8. Write the fake consumer using types imported verbatim, not paraphrased.

10. **Finalise.** Run the full suite, type-checker, and linter (if configured). Write a final SESSION.md entry with `status: complete`, list commits, and summarise DIVERGENCE_LOG.md for the leader. **If a frozen SHADOW/ was consumed in step 4**, dispatch `ultra-shadow-drift` as a post-implementation drift check — verifies the real code hasn't drifted from the frozen architecture; emits `DRIFT_REPORT_<YYYY-MM-DD>.md` with BUG/SHADOW-UPDATE/ACCEPTABLE-EVOLUTION/FEATURE-DROPPED classifications.

## Red Flags — STOP and self-correct

- Writing code before a failing test exists for the current task
- Batching tests across multiple tasks before implementing
- A test that passes on first run (you're testing existing behavior — rewrite)
- Inventing a field, enum, or shape because the sibling INTERFACE.md "probably" has it
- Filling an ambiguous plan item silently instead of logging to DIVERGENCE_LOG.md
- Skipping SESSION.md update between tasks (loses resumability)
- No freshness check before a contract smoke test
- Treating the plan as authoritative when its references are unreachable
- Continuing past an `escalate-to-leader` classification without user input
- Skipping the periodic self-review because "the code looks fine"
- Committing a file over 2,000 lines without splitting
- Duplicated logic across 2+ files without extraction

## Common Mistakes

- **Batched RED→GREEN:** writing all tests, then implementing once. Fast but bypasses the per-task TDD pressure. Force per-task cycles even when tasks look linear.
- **Fabricated sibling types:** when `01-fetcher/INTERFACE.md` can't be opened, inventing `PRRecord` from plan field names. Largest source of contract drift at execution. STOP instead.
- **Silent plan patches:** noticing header copy or ordering is unspecified and just picking. Log it — default is fine, silence is not.
- **No session state:** treating the in-memory plan as state. Solo executors get interrupted; SESSION.md is the resume point.
- **Skipping the freshness check:** pinning siblings once but never re-verifying before contract tests. The sibling might have shipped mid-execution.
- **Subagent-language contamination:** thinking "I'll dispatch a reviewer" when you are the executor AND reviewer. The procedure's discipline replaces the missing second pair of eyes.
- **Skipped REFACTOR phase:** writing minimal GREEN code and committing without applying Code Standards. The REFACTOR phase is where LOC limits, duplication, and naming get enforced. Skipping it accumulates debt that compounds across tasks.
- **Review-fix spiral:** spending 3+ iterations polishing in self-review. Cap at 2 iterations; log remaining issues and move on. Perfect is the enemy of shipped.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
