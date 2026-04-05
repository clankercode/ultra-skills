---
name: ultra-cross-doc-review
description: Use when ultra-planner dispatches a tree-review checkpoint, when a plan tree has 5+ nodes with interfaces and needs cross-document coherence check, after a decomposition or refinement phase completes, or when naming drift, interface mismatches, or dependency cycles are suspected across nodes. NOT for reviewing a single node's SPEC (use inline review) and NOT for code review (use superpowers:requesting-code-review).
---

# ultra-cross-doc-review

## Overview

Cross-document review of a plan tree for architectural coherence. Walks every node, runs a fixed 8-dimension checklist, emits a dated REVIEW.md triaged BLOCKER/MAJOR/MINOR, and proposes patches (ADRs or interview items) for each BLOCKER and MAJOR. Called by `ultra-planner` at tree-review checkpoints.

**Core principle:** Findings without severity are noise; severity without patches is debt. Every BLOCKER/MAJOR must land on disk as either a `DECISIONS.md` ADR patch or an `INTERVIEW_QUEUE.md` item.

## When to Use

| Signal | Use? |
|---|---|
| ultra-planner dispatches tree-review phase | Yes |
| Plan tree has 5+ nodes with INTERFACE.md files | Yes |
| Decomposition or refinement phase just finished | Yes |
| Suspected naming drift / cycle / missing-doc | Yes |
| Reviewing one node's SPEC in isolation | No — inline |
| Reviewing implementation code | No — superpowers:requesting-code-review |

## Procedure

Operate against plan-tree root `docs/ultra-plans/<slug>/`. Do not skip or reorder.

1. **Enumerate nodes.** List every `nodes/*/` dir (plus nested `children/`). Record count N. Read `ROOT.md`, `DECISIONS.md`, and every node's `SPEC.md` and `INTERFACE.md`. Missing file → log MISSING-DOC finding, continue.

2. **Extract type/symbol inventory.** Per node collect: exposed types, exposed methods/events, consumed types, depended-on nodes. This is the evidence base for later dimensions.

3. **Walk the 8-dimension checklist.** Examine every dimension in order; do not skip because "nothing looked wrong":
   - **Naming consistency** — gather every type/identifier name; flag close-variants (`UserId` vs `user_id` vs `user_uuid`, casing, pluralization).
   - **Interface fit** — for each consumer's consumed type, verify producer exposes that exact type with matching shape. Field/optionality mismatch = MAJOR minimum.
   - **Dependency cycles** — build DAG (edge = consumer → producer from depends-on). Topological sort. Any back-edge = BLOCKER.
   - **Missing docs** — node lacking SPEC or INTERFACE, exposed symbol with no description, consumed type not defined anywhere.
   - **Type definitions** — every type referenced in any INTERFACE defined in exactly one producer. Undefined or duplicated = MAJOR.
   - **Responsibility overlap** — pairwise SPEC responsibility scan; two nodes claiming same responsibility = MAJOR.
   - **Public-surface inheritance** — every parent-exposed symbol owned by exactly one child (if decomposed). Orphan = BLOCKER.
   - **Parent-child consistency** — each child's responsibilities appear in parent's set; child cannot exceed parent scope.

4. **Triage findings.**
   - **BLOCKER** — cycle, orphaned public symbol, contradictory contract, missing node referenced as dependency.
   - **MAJOR** — naming drift on shared type, interface-fit mismatch, undefined/duplicated type, responsibility overlap, missing INTERFACE.md.
   - **MINOR** — casing drift on non-shared name, missing description, stylistic inconsistency, suspected-but-unproven overlap.

5. **Write REVIEW.md** at `nodes/REVIEWS/YYYY-MM-DD-HHMM.md` (create `REVIEWS/` if absent). Include `Reviewed N nodes: [list]` assertion at top. Group by severity; per finding: dimension tag, location (files + refs), evidence (quoted), proposed fix.

6. **Emit patches.** For each BLOCKER and MAJOR, append one of:
   - ADR entry to `DECISIONS.md` (when fix is an architectural decision).
   - `INTERVIEW_QUEUE.md` item at P0 (BLOCKER) or P1 (MAJOR) (when fix needs user input).
   Write patches same pass; cross-reference from REVIEW.md finding.

7. **Update SESSION.md and ROOT.md.** SESSION.md last/next action; ROOT.md dashboard row with review date + BLOCKER/MAJOR/MINOR counts.

## REVIEW.md Format

```
# Tree Review — YYYY-MM-DD HH:MM
Reviewed N nodes: [01-foo, 02-bar, ...]
Checklist: naming, interface-fit, cycles, missing-docs, types, overlap, public-inheritance, parent-consistency

## BLOCKER (count)
- [cycles] 02-presence ↔ 03-notification-hub: back-edge in DAG.
  Evidence: 02/INTERFACE.md depends-on: [03]; 03/INTERFACE.md depends-on: [02].
  Fix: ADR-007 (DECISIONS.md) — extract shared event bus.

## MAJOR (count)
- [naming] `UserId` (01) vs `user_id` (03) vs `user_uuid` (04).
  Fix: INTERVIEW_QUEUE.md P1 — canonical identifier type.

## MINOR (count)
- ...
```

## Red Flags — STOP and self-correct

- Findings without BLOCKER/MAJOR/MINOR triage
- Skipping a checklist dimension because "it looked clean"
- Missing `Reviewed N nodes` assertion at top of REVIEW.md
- BLOCKER/MAJOR with no DECISIONS.md or INTERVIEW_QUEUE.md patch
- Cycle detection by eye instead of explicit DAG + topo sort
- Naming drift flagged only for exact duplicates (missed close-variants)
- Findings emitted to chat instead of `nodes/REVIEWS/YYYY-MM-DD-HHMM.md`
- Node missing SPEC or INTERFACE silently skipped instead of logged

## Common Mistakes

- **Ad-hoc traversal:** opportunistic findings instead of the full 8-dimension checklist. Missed dimensions = missed issues.
- **Flat-list findings:** no severity = user can't prioritize. Triage non-optional.
- **Review-without-patch:** emitting a BLOCKER and expecting someone else to propose the fix. The review owns the patch.
- **Eyeball cycle-check:** scanning depends-on visually instead of building the graph. Cycles across 3+ hops get missed.
- **Name-drift blindness:** only flagging exact collisions. `UserId`/`user_id`/`user_uuid` is the canonical pattern.
- **Timestamp collision:** date-only filename overwrites prior reviews. Use `YYYY-MM-DD-HHMM`.
