---
name: ultra-writing-plans
description: Use when writing a leaf-node PLAN.md inside an ultra-skills plan tree with sibling INTERFACE.md dependencies, when ultra-planner dispatches Phase 5 leaf-plan writing, or when a node has stable SPEC + INTERFACE and needs an implementation plan that respects cross-node contracts. NOT for single-feature planning (use `superpowers:writing-plans` directly) and NOT for interior nodes (decompose, don't plan).
---

# ultra-writing-plans

## Overview

Writes a leaf-node `PLAN.md` inside a hierarchical plan tree. Extends `superpowers:writing-plans` with cross-node discipline: parent-SPEC coverage, cross-node type survey, contract smoke tests per sibling consumer, and hard refusal to silently work around undefined boundary items.

**Core principle:** Prove boundary discipline on disk, not rely on orchestrator goodwill. Every cross-node type is either declared in a sibling INTERFACE.md or queued as an interview item / ADR / proposed amendment — never silently re-invented.

**REQUIRED BACKGROUND:** Invoke `superpowers:writing-plans` via the Skill tool. This skill EXTENDS it — the TDD task template, bite-sized steps, and no-placeholders rule come from there. Not loaded → stop and load.

## When to Use

| Signal | Use? |
|---|---|
| ultra-planner dispatches Phase 5 leaf-plan writing | Yes |
| Leaf node has stable SPEC.md + INTERFACE.md | Yes |
| Plan node depends on 1+ sibling INTERFACE.md | Yes |
| Interior node (has children) | No — decompose, don't plan |
| Single-feature plan outside a tree | No — `superpowers:writing-plans` |
| SPEC or INTERFACE still in flux | No — stabilise first |
| Executing an existing PLAN.md | No — `superpowers:subagent-driven-development` |

## Procedure

Operate on a leaf node path `nodes/<path>/`. Do not skip or reorder.

1. **Confirm leaf-node status.** No `children/` dir and no child rows in parent's `CHILDREN.md`. Interior node → stop; surface to ultra-planner for decomposition.

2. **Confirm prerequisites.** Stable SPEC.md and INTERFACE.md exist. Every sibling in this node's `depends-on` has a readable INTERFACE.md. Every consumer listing this node is identifiable. Missing → stop, file P0 interview items.

3. **Cross-doc-review gate.** Check `nodes/REVIEWS/` for a recent review (< 1 phase old) covering this node + its dependency/consumer siblings. Absent → invoke `ultra-cross-doc-review` (or ask ultra-planner to) before drafting. Record reviewed-at date in SESSION.md.

4. **Feasibility scan.** Before planning tasks, review the node's SPEC.md for any requirements that appear technically infeasible or impossible (violates known theoretical limits, requires non-existent technology, demands contradictory properties). For each concern, dispatch a research subagent (via `ultra-plan-research`) to investigate. If confirmed infeasible, file a P0 item in INTERVIEW_QUEUE.md with the evidence and 1-2 alternative approaches, write a `blocked — infeasible` ADR stub in DECISIONS.md, and STOP — do not write a PLAN.md that plans around an impossibility.

5. **Parent-SPEC coverage scan.** Open parent SPEC.md and parent `CHILDREN.md`. Enumerate every responsibility the parent delegates to this child. Write the list to `nodes/<path>/NOTES.md` as a coverage checklist. Each item must map to a planned task before PLAN.md ships.

6. **Cross-node type survey.** For every type, event, or identifier crossing a node boundary (imported from sibling OR exported to consumer), mark in NOTES.md: `exported-locally` | `imported-from-sibling:<path>` | `undefined-in-siblings` | `ambiguous`. Evidence base for steps 7 and 10.

7. **Resolve undefined/ambiguous boundary items.** Do NOT silently re-invent. Route each to one of:
   - **Interview item** → append to `INTERVIEW_QUEUE.md` at P1 (P0 if sibling is in flight), attach a default.
   - **DECISIONS.md ADR stub** → when the answer is a local architectural commitment.
   - **Proposed INTERFACE amendment** → append to sibling node's `NOTES.md` as a suggested addition (e.g. "PRRecord needs `title: string` for human-readable digests") and flag in PLAN header.
   Working around a missing field without filing one of these is a red flag.

8. **Invoke `superpowers:writing-plans` discipline for local task structure.** File-structure map, bite-sized 5-step tasks (failing test → FAIL → implement → PASS → commit), no-placeholders, self-review. This skill extends that; it does not re-teach it. The RED-GREEN-REFACTOR lifecycle emitted in each task follows `ultra-test-driven-development` (Iron Law, rationalizations table); workers executing these tasks should also load `ultra-writing-tests` for test-writing craft (fast-test preference, DI-seam discipline, contract smoke tests).

9. **Require contract smoke test(s).** Per distinct sibling consumer boundary, add a final task: a test feeding this node's output through a fake of the consumer's expected input signature. One per consumer. Non-optional — the last task(s) of every ultra leaf PLAN. See `ultra-writing-tests` for the contract-smoke-test pattern used here.

10. **Cite sibling INTERFACE.md paths in PLAN header.** Add a "Cross-node references" block after the Architecture line listing each sibling INTERFACE path consulted + last-modified timestamp. Stale relative to current decomposing cycle → "Freshness warning" note + P1 interview item.

11. **Update SESSION.md and ROOT.md.** SESSION.md records PLAN-written checkpoint, reviewed-at date, interview/ADR items filed. ROOT.md marks this leaf `PLAN: ready`.

## Red Flags — STOP and self-correct

- Drafting PLAN.md without `superpowers:writing-plans` loaded via the Skill tool
- Node has children but you're writing PLAN.md (interior nodes don't get plans)
- Cross-node type used that no sibling INTERFACE.md exports, with no interview/ADR/amendment filed
- Sentinel or convention assumed (e.g. `mergedAt === 0` means open) that isn't in any sibling INTERFACE.md
- Parent-SPEC coverage list missing from NOTES.md or has unchecked items
- No contract smoke test as final task(s), one per sibling consumer
- PLAN header missing "Cross-node references" block with sibling INTERFACE paths
- Skipped cross-doc-review check because "the orchestrator handles it" — verify on disk
- Sibling interface timestamp looks stale, no freshness warning filed

## Common Mistakes

- **Silent workaround:** needing a field the sibling doesn't export (`PRRecord.title`, `CIEvent.jobName`) and just not using it, instead of filing a contract amendment. Gap persists invisibly into execution.
- **Assumed sentinels:** inventing a "0 means not merged" convention without checking sibling's INTERFACE.md. Cross-node conventions belong in interfaces, not plans.
- **Parent-drift:** implementing own SPEC but missing responsibilities the parent delegated. Walk parent SPEC before finalising.
- **Contract-test-as-afterthought:** one integration test with self-chosen shapes, instead of per-consumer tests matching the consumer's exact signature.
- **No sibling citations:** referencing types without noting source INTERFACE.md — audit-hostile.
- **Extending without loading:** reading `superpowers:writing-plans` as reference instead of invoking it as a skill. The base disciplines need to be active, not summarised.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
