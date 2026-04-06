---
name: ultra-goal-loop
description: Use when acceptance criteria exist or can be derived but the path to satisfying them requires adaptive iteration rather than rote plan execution — especially for goals that are part of a larger project and may need to auto-advance into the next phase. NOT for executing a pre-written PLAN.md (use ultra-implementing-solo or ultra-implementing-team) or quality polishing (use self-improvement-loop).
---

# ultra-goal-loop

## Overview

Iteratively drives a codebase toward a defined goal through **assess → plan → implement → evaluate → repeat** until all acceptance criteria are satisfied. Adapts `goal-driven-loop` into the ultra-* ecosystem: plan-tree awareness, context-hygiene discipline, YAGNI lens integration, TDD grounding, and auto-advance chaining for multi-phase projects.

**Core principle:** All AC satisfied or the loop doesn't stop. The loop writes its own micro-plans in-flight and adapts — unlike `ultra-implementing-solo/team` which execute a pre-written PLAN.md. When the goal is one phase of a larger project, auto-advance chains forward without user intervention.

**Announce at start:** "I'm using the ultra-goal-loop skill to drive this to completion."

## When to Use

| Signal | Use? |
|---|---|
| Goal with AC exists, path is uncertain, adaptive iteration needed | Yes |
| Leaf-node or subsystem goal that needs driving to completion | Yes |
| Part of a larger project — goal may chain into next phase | Yes |
| Goal file with `ON_GOAL_COMPLETE_NEXT_STEPS` already present | Yes |
| Executing a pre-written PLAN.md task-by-task | No — use `ultra-implementing-solo` or `ultra-implementing-team` |
| Quality polish of already-complete code | No — use `self-improvement-loop` |
| Fixing known issues against a checklist | No — use `review-and-fix` |

## Relationship to ultra-implementing-solo / ultra-implementing-team

Those skills execute a **pre-written** leaf PLAN.md with strict per-task TDD. This skill is for when no such plan exists yet — the loop discovers what to do, writes micro-plans, implements, evaluates, and repeats. It is the skill you reach for when someone says "make X work" and X doesn't have a detailed task list yet.

If during the loop a stable PLAN.md emerges, the loop may hand off to `ultra-implementing-solo` for execution and resume its own assess/evaluate role.

## Auto-Advance (Optional)

When the current goal is part of a larger project — there is an explicit project plan, the user referenced "next steps", or context clearly indicates multi-phase work — the loop can **auto-advance** on goal completion instead of stopping.

**Activation (one of):**
1. User explicitly requests it at invocation ("keep going", "chain into next tasks", "auto-advance")
2. The goal file already contains an `ON_GOAL_COMPLETE_NEXT_STEPS` section from a prior invocation
3. The agent detects the goal is a subtask of a larger project and asks the user via the question tool whether to auto-advance on completion

**When active, on goal completion the loop does NOT exit.** Instead:
1. Microplan the next tasks based on: recent actions, the main project plan, and any `ON_GOAL_COMPLETE_NEXT_STEPS` directives
2. Create a new goal + AC list from that microplan
3. Update the persistent goal file with the new goal (preserving `ON_GOAL_COMPLETE_NEXT_STEPS`)
4. Continue the loop from Step 1

The `ON_GOAL_COMPLETE_NEXT_STEPS` directive persists across compactions and session interruptions. Once written, it stays until the user explicitly removes it or the project is complete.

## Procedure

### Before the Loop: Establish Goals

If acceptance criteria are not provided, derive them:
- Read spec documents, TODOs, README, project description, or plan-tree nodes
- Run the test suite to see what fails
- Synthesize a concrete AC list

Write the AC list explicitly before starting. If AC are ambiguous, ask the user before starting.

### Before the Loop: Create a Persistent Goal File

1. Determine the project root (`git rev-parse --show-toplevel` or cwd).
2. Create `.goal-loops/` under that root if it doesn't exist. Git-ignore it (`.git/info/exclude` preferred).
3. Create or update `.goal-loops/active-goal.md` with sections: **Primary Goal** (single sentence), **Acceptance Criteria** (bulleted), **Current Status** (iteration N, newly satisfied, remaining), **Current Plan** (micro-plan), **Blockers / Notes** (decision-relevant only), and optionally **ON_GOAL_COMPLETE_NEXT_STEPS** (auto-advance directive — see Auto-Advance section above).

This file is not optional. The loop must keep it current enough that, after compaction or interruption, any agent can resume by rereading it.

**Auto-advance check on first read:** If the file contains `ON_GOAL_COMPLETE_NEXT_STEPS`, auto-advance mode is active — no need to re-ask.

---

### Step 1: Assess

Reread `.goal-loops/active-goal.md` first. Also reread immediately after any compaction/resume.

Gather the facts about current state. Use existing results if fresh (same iteration, no code changes since). Otherwise run:

- Test suite, linters, formatters, type checkers
- Project-specific validators, evaluation scripts
- Code review (dispatch reviewer subagent if useful)

Produce a **status snapshot**: which AC are satisfied, which are not, with specific evidence. Update the goal file.

---

### Step 2: Check Exit Condition

**All AC satisfied?**

1. **Is auto-advance active?** Check goal file for `ON_GOAL_COMPLETE_NEXT_STEPS` or recall user activation.
2. **If yes — advance:** Review main project plan + recent actions, microplan next tasks, write new goal + AC into goal file (preserving `ON_GOAL_COMPLETE_NEXT_STEPS`), reset iteration counter, continue from Step 1.
3. **If no — report to user** (what was built, iteration count, remaining notes) and stop.

If auto-advance is active but no further tasks can be identified, report completion and note that auto-advance found no remaining work.

---

### Step 3: Plan

Write an explicit micro-plan (5-10 lines) before touching code: which AC this iteration addresses, concrete approach, files to change, how to verify, adjacent fixes noticed. Record it in the goal file before implementation.

---

### Step 4: Implement

Dispatch subagents to execute the micro-plan.

**If `subagent-driven-development` is available:** use it for multi-task implementation with review stages.

**Inline micro-pattern (if absent):**
1. Dispatch fresh implementer subagent — provide: micro-plan, file paths, AC list, current test output
2. Subagent implements, runs tests/verifications, commits
3. Dispatch reviewer subagent — verify micro-plan goals met, no regressions, code clean
4. If reviewer fails: dispatch fixer subagent with issues; re-review until approved

One implementer at a time (conflicts). Independent review/fix pairs can be parallel.

---

### Step 4b: Stuck Handling

If implementer reports BLOCKED or can't make progress:

1. Dispatch brainstorm subagent: what was tried, exact error/blocker, relevant code/context. Ask for 3 concrete alternative approaches with trade-offs.
2. Select best approach; re-dispatch implementer.
3. Still stuck after 2 brainstorm rounds: **escalate to user** with blocker, what was tried, and brainstorming suggestions.

---

### Step 5: Status Update

After each implementation step, post a brief status (done, eval results, AC progress X/Y, next focus) and update the goal file. Loop back to Step 1.

## Cross-Cutting Lenses (`ultra-context-hygiene`, `ultra-test-driven-development`, `ultra-writing-tests`)

Adjacent fixes are in-scope; adjacent features are not. Persist everything to the goal file, not in-memory. Each implementer follows RED-GREEN-REFACTOR.

## Exit Condition (Non-Negotiable)

**ALL acceptance criteria satisfied.** Not "mostly done." Not "one small thing left."

When all AC satisfied and auto-advance is NOT active: exit and report.
When all AC satisfied and auto-advance IS active: replace the goal with the next microplan and continue.

If 5 or more consecutive iterations produce no newly satisfied AC, escalate to user rather than looping forever. This applies globally across auto-advance phases — 5 stagnant iterations in a row regardless of goal swaps.

## Red Flags — Continue Looping

- "This is close enough"
- "Only one small AC remaining"
- "The main functionality works"

If anything is unsatisfied, loop continues.

## Red Flags — Escalate to User

- Same blocker in 3+ iterations
- Two subagents give contradictory guidance
- An AC requires a design decision you can't make
- 5+ iterations with no AC progress

## Common Mistakes

| Mistake | Fix |
|---|---|
| Exit before all AC satisfied | Binary: all pass or loop |
| Skip the micro-plan | Always plan before implementing |
| Re-use stale eval results | Re-run after code changes |
| Stuck → loop blindly | Brainstorm first, escalate second |
| AC derived wrong | Verify with user if in doubt |
| Huge implementation per iteration | Keep micro-plans small and focused |
| Dispatch parallel implementers | One at a time to avoid conflicts |
| Auto-advance without checking for next work | If no next tasks found, exit and report |
| Accumulating context in-memory across iterations | Persist to goal file, delegate heavy reads to subagents |
| Adding "while we're here" features beyond AC | Adjacent fixes yes, adjacent features no |

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
