---
name: ultra-planner
description: Use when planning a multi-subsystem system (3+ independent components), a "platform" or "product" with many moving parts, or any project the user flags as big, comprehensive, careful, or "lots of components". Produces a hierarchical plan tree on disk across multiple sessions. NOT for single-feature planning — use superpowers:brainstorming for that.
---

# ultra-planner

## Overview

Orchestrates hierarchical, multi-document planning for systems too large for a single spec. Maintains a filesystem plan tree with per-node specs, interface contracts, research log, decision log, and session state. Dispatches to sub-skills for decomposition, research, review, and scope-pruning.

**Core principle:** Plan-as-filesystem. Every decision is a file. Every file is resumable across sessions. Session state lives in `SESSION.md`; you MUST read it on invocation and update it after every significant action.

## When to Use

| Signal | Use? |
|---|---|
| "Build a platform / product / system with components A, B, C, D" | Yes |
| "Help me carefully plan X" (X is non-trivial) | Yes |
| "Lots of components / subsystems / moving parts" | Yes |
| Single feature, single file, single function | No — use superpowers:brainstorming |
| Fixing a bug | No — use superpowers:systematic-debugging |
| Executing an existing plan | No — use superpowers:subagent-driven-development |

## Plan Tree Directory Layout

Create under `docs/ultra-plans/<project-slug>/`:

```
ROOT.md                 # tree structure + status dashboard
SESSION.md              # current phase, last/next action, open threads
INTERVIEW_QUEUE.md      # prioritized open questions for user
RESEARCH_LOG.md         # findings from research subagents
DECISIONS.md            # ADR-style architectural decisions
PRODUCT_GOALS.md        # success criteria, non-goals
nodes/NN-<slug>/        # one dir per subsystem
  SPEC.md               # what this component does
  INTERFACE.md          # what it exposes / depends on
  PLAN.md               # leaf nodes only — TDD task list
  NOTES.md              # working notes
artifacts/              # diagrams, mockups, demos
```

Full spec: `ultra-skills/docs/DESIGN.md`.

## Procedure (every invocation)

1. Read `SESSION.md`. Missing → bootstrap (create tree dir + PRODUCT_GOALS via interview).
2. Identify current phase and next planned action from SESSION.md.
3. Execute one phase step (dispatch per table below, unless user requests batching).
4. Update SESSION.md (`Last action`, `Next planned action`).
5. At a checkpoint → surface status + top interview queue items to user.

**Phases:** bootstrap → decompose → refine → prune → artifacts → leaf-plans → handoff. Revisit earlier phases when new info arrives.

## Feasibility Gate (cross-cutting)

Before accepting any requirement, feature, or architectural commitment into the plan tree, apply a feasibility check. If something appears impossible or technically infeasible — physically impossible, violates known theoretical limits, requires non-existent technology, or demands contradictory properties — do NOT silently plan around it or accept it at face value.

**Procedure when a feasibility concern arises:**

1. **Flag it.** Note the concern in the relevant node's `NOTES.md` with tag `feasibility-concern`.
2. **Research first.** Dispatch a subagent (via `ultra-plan-research` or a targeted research subagent) to investigate whether the requirement is actually infeasible or whether there are creative approaches that could satisfy it. Do not conclude infeasibility from intuition alone.
3. **Push back with evidence.** If research confirms infeasibility (or extreme impracticality), surface this to the user as a P0 item in `INTERVIEW_QUEUE.md` with: the requirement, why it's infeasible (with citations/evidence from research), and 1-2 alternative approaches that achieve the user's underlying goal. Write a draft ADR in `DECISIONS.md` with status `blocked — infeasible` and the evidence.
4. **Do not proceed past the concern.** An infeasible requirement in a SPEC poisons every downstream artifact. Block leaf-plan writing for affected nodes until resolved.

This gate applies during every phase — bootstrap, decompose, research, prune, and leaf-plan writing. Planning around an impossibility is worse than stopping to surface it.

## Dispatch Table

For each phase, dispatch to a skill. Ultra-* sub-skills are preferred; fall back to superpowers:

| Phase | Ultra skill (preferred) | Fallback |
|---|---|---|
| Bootstrap from a single-file seed plan (Claude/Codex output, hand-written markdown) — produces tree skeleton, ORIGIN.md audit trail, augmented INTERVIEW_QUEUE, then hands back at Phase 2 or 3 | `ultra-plan-from-seed` | Inline prose-to-tree conversion (loses ORIGIN.md audit, ADR fidelity check, scope-tier splitting, interview-queue augmentation, CHILDREN.md coverage matrix) |
| Decompose node | `ultra-decomposing` | Inline reasoning + superpowers:brainstorming for node SPEC |
| Research | `ultra-plan-research` | superpowers:dispatching-parallel-agents |
| Tree review | `ultra-cross-doc-review` | superpowers:requesting-code-review pattern |
| Prune scope | `ultra-scope-pruning` | Inline YAGNI challenge |
| Interview user | `ultra-interviewing` | Inline one-question-at-a-time |
| Leaf-node plan writing (Phase 5) | `ultra-writing-plans` | superpowers:writing-plans |
| Phase 5.5 — Shadow generation | `ultra-shadow-code` | Skip; proceed directly to implementation (loses architecture-review gate) |
| Phase 5.5b — Shadow review | `ultra-shadow-review` | Skip-then-freeze (loses cheap-layer bug catch); or inline ad-hoc review |
| Post-implementation drift check — real code vs. frozen shadow, classified + prioritized | `ultra-shadow-drift` | Ad-hoc diff + eyeballed drift notes (loses classification, rollup metrics, test-complicity flag) |
| Shadow regeneration (L3) — derive current-shadow from real code + emit SHADOW_DIVERGENCE.md | `ultra-shadow-regen` | Manual re-derivation of shadow from code; hand-written divergence notes |
| Leaf implementation (solo mode, no subagent dispatch) | `ultra-implementing-solo` | superpowers:test-driven-development inline |
| Leaf implementation (team mode, leader + dispatched workers) | `ultra-implementing-team` | superpowers:subagent-driven-development |
| Goal-driven loop (adaptive iteration toward a goal without pre-written plan, auto-advance for multi-phase) | `ultra-goal-loop` | `goal-driven-loop` (personal skill, loses plan-tree awareness, context-hygiene, YAGNI lens, ultra-TDD grounding) |
| Artifact generation (Phase 4) | `ultra-design-artifacts` | Inline graphviz/mermaid |

**Cross-cutting (invoked by every dispatching phase):**

| Concern | Ultra skill | Fallback |
|---|---|---|
| Context budget / delegation discipline | `ultra-context-hygiene` | Inline reminders to cap token spend |
| YAGNI lens pass on in-progress artifacts (call from `ultra-decomposing`, `ultra-plan-research`, `ultra-writing-plans`, `ultra-cross-doc-review`, `ultra-writing-skills`) | `ultra-yagni` | Inline "is this speculative?" check against anchor |
| TDD discipline (RED-GREEN-REFACTOR cycle, Iron Law) grounding `ultra-implementing-solo` / `ultra-implementing-team` per-task execution and `ultra-writing-plans` task structure | `ultra-test-driven-development` | `superpowers:test-driven-development` |
| Test-craft (WHAT makes a good test) — fast-test preference, behavior-not-mocks, deterministic time, flow-vs-narrow, contract smoke tests, helper extraction, tiering, test-complicity guard. Loaded by workers at RED-test-writing time under `ultra-implementing-solo` / `ultra-implementing-team` | `ultra-writing-tests` | Inline "testing the mock?" self-check + superpowers:test-driven-development `testing-anti-patterns.md` |

**Meta (suite self-modification):**

| Phase | Ultra skill | Fallback |
|---|---|---|
| Create/modify an ultra-* skill | `ultra-writing-skills` | superpowers:writing-skills |
| Review ultra-* skill(s) before shipping | `ultra-reviewer` | superpowers:requesting-code-review pattern |
| Skill routing (symptom → which ultra-* skill) — **lookup aid, not dispatched** | `ultra-index` | Inline recall of suite |

Check if the ultra sub-skill is loaded (listed in skills catalog). If not, use fallback and note in SESSION.md.

## Session State Discipline

- If user message contradicts SESSION.md's next action, trust user, update SESSION.md.
- Never hold critical state in your own context — write it to disk.
- **Checkpoint triggers:** end of phase, 3+ P0 questions accumulated, tree review finds issues, user asks "where are we?".

## Red Flags

STOP and self-correct if any of these occur:

- Diving into leaf-node detail before the tree has a stable top-level shape
- Writing a PLAN.md before the parent INTERFACE.md exists
- Skipping SESSION.md read/update (breaks resumability)
- Letting INTERVIEW_QUEUE.md grow unbounded without surfacing to user
- Asking user one question at a time when many are queued — batch at checkpoints
- Producing a flat list of tasks instead of a hierarchical tree when project is multi-subsystem
- Running research inline (burns main-session context) instead of dispatching
- Accepting a requirement that looks physically impossible or technically infeasible without dispatching a research subagent to investigate and then pushing back with evidence

## Common Mistakes

- **Scope drift up:** growing into a general agent framework. Non-goal.
- **Scope drift down:** using this for a single-feature ask. Use superpowers:brainstorming.
- **Over-decomposition:** splitting nodes that fit comfortably in one SPEC + PLAN. Only decompose when >15 tasks expected or multiple independent concerns.
- **State-free operation:** skipping SESSION.md read/update.
- **Single-session thinking:** large plans span sessions. Write everything to disk.

## Reference

See `ultra-skills/docs/DESIGN.md` for full architecture, plan-tree model, review cadence, and rationale.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
