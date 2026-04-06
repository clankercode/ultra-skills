---
name: ultra-decomposing
description: Use when a plan-tree node's SPEC has multiple independent concerns, expected leaf task count exceeds ~15, a node mixes independent failure domains or lifetimes, a node's INTERFACE exposes 6+ unrelated symbols, or ultra-planner's decompose phase dispatches this skill. NOT for deciding whether to decompose (ultra-planner decides) and NOT for single-feature nodes that fit in one SPEC + PLAN.
---

# ultra-decomposing

## Overview

Splits an oversized plan-tree node into child nodes with proven coverage, proven non-overlap, interface contracts, and a topologically-ordered build sequence. Called by `ultra-planner` during the decompose phase.

**Core principle:** A decomposition is only valid if every parent responsibility has exactly one child owner, no two children share a responsibility, and the child dep graph is acyclic. These must be proven on disk, not asserted in chat.

## When to Use

| Signal | Use? |
|---|---|
| Parent SPEC lists 6+ distinct responsibilities | Yes |
| Expected leaf-plan task count > 15 | Yes |
| ultra-planner dispatches decompose phase | Yes |
| Independent failure domains / lifetimes / cadences inside one node | Yes |
| Node fits in one SPEC + one PLAN.md comfortably | No — keep as leaf |
| Deciding WHETHER to decompose at all | No — ultra-planner decides; this skill executes |

## Procedure

Operate on parent node path `nodes/<parent>/`. Produce children under `nodes/<parent>/children/<NN-slug>/`.

1. **Read parent SPEC.md and INTERFACE.md.** Extract the complete responsibility list as an enumerated set R = {r1..rN}. If R is ambiguous, append clarifying questions to INTERVIEW_QUEUE.md at P0 and stop. **Feasibility scan:** while extracting responsibilities, flag any that appear technically infeasible or physically impossible (violates known limits, requires non-existent technology, demands contradictory properties). For each flagged item, dispatch a research subagent (via `ultra-plan-research`) to investigate before proceeding. If confirmed infeasible, surface as P0 in INTERVIEW_QUEUE.md with evidence and alternative approaches — do not decompose around an impossibility.

2. **Identify split seams** before naming children. Seams come from: data ownership boundaries, failure domains, lifetime/cadence differences (persistent vs ephemeral, sync vs async, request vs background), public-API surface slices, deployment-shape differences. Write seams to `nodes/<parent>/NOTES.md`.

3. **Propose child set.** For each candidate child, record: name, owned responsibilities (subset of R), rationale (why separate, not folded).

4. **Produce coverage matrix.** Write `nodes/<parent>/CHILDREN.md` containing a table: one row per ri in R, column = owning child. Every ri MUST have exactly one owner. If a row is empty → missing child. If a row has two owners → overlap, must resolve.

5. **Produce non-overlap assertion.** In CHILDREN.md, add an explicit paragraph: "No responsibility in R is owned by more than one child" with a per-pair scan of suspicious overlaps (e.g. "collab-engine and doc-store both touch ops; boundary is: engine transforms, store persists"). Naming the overlap risk and resolving it is the assertion.

6. **Map public surface.** If parent INTERFACE.md exposes methods/types/events to outside consumers, add a second table in CHILDREN.md mapping each parent-exposed symbol → inheriting child. Consumers must not be orphaned.

7. **Scaffold child directories.** For each child create `SPEC.md` (purpose, owned responsibilities from matrix, non-responsibilities, rationale from step 3) and `INTERFACE.md` (exposes / depends-on / events).

8. **Draft cross-child contracts.** In `nodes/<parent>/INTERFACES.md` list every call, event stream, and shared type that crosses a child boundary. Each contract names producer child and consumer child(ren).

9. **Validate acyclicity.** Build dep graph from step 8 (edge = A calls/subscribes-to B). Run topological sort. If cycle detected → surface to user via INTERVIEW_QUEUE.md P0 and do NOT proceed. If DAG, write the topological order as "Implementation order" in CHILDREN.md.

10. **Surface open questions.** Any ambiguity discovered during steps 1-9 (unclear ownership, contract shape TBD, seam debated) appends to `INTERVIEW_QUEUE.md` with P0/P1/P2 priority.

11. **Update parent + ROOT.** Append to parent SPEC.md: "Decomposed into: [child list with one-line purposes]". Update `ROOT.md` tree view to show new children. Update `SESSION.md` last/next action.

## Red Flags

STOP and self-correct if any occur:

- Naming children before extracting the parent responsibility set
- Skipping the coverage matrix ("it's obvious which child owns what")
- Verbal non-overlap claim without the pairwise scan
- Child rationale living only in your response, not in SPEC.md
- Dep cycle present but proceeding anyway
- Public parent-API symbol with no child owner
- No topological order emitted
- INTERVIEW_QUEUE.md unchanged despite discovered ambiguities
- Decomposing a node whose SPEC contains a requirement that looks technically infeasible without first dispatching research to verify and then pushing back with evidence

## Common Mistakes

- **Equal-sized-slices bias:** forcing N similarly-sized children when one fat child + three thin children is the real shape.
- **Layering instead of decomposing:** producing "frontend/backend/db" layers rather than domain-owned subsystems.
- **Contract-last:** scaffolding child dirs before drafting cross-child contracts, then retrofitting interfaces.
- **Hidden cross-cutting concerns:** auth, config, lifecycle referenced by every child with no owner — either assign to one child or promote to an infra sibling.
- **Over-decomposition:** creating children that each hold <5 tasks. Merge back.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
