---
name: ultra-plan-from-seed
description: Use when converting a single-file seed plan (Claude/Codex output, hand-written markdown, 500+ words, multi-subsystem) into an ultra-plan tree bootstrap — PRODUCT_GOALS, ROOT, node SPEC/INTERFACE stubs, DECISIONS, INTERVIEW_QUEUE, artifacts/ORIGIN.md — then hands off to ultra-planner. NOT for blank-slate planning (use ultra-planner), NOT for decomposing existing nodes (use ultra-decomposing), NOT for under-500-word or single-subsystem seeds (use superpowers:writing-plans).
---

# ultra-plan-from-seed

## Overview

Converts a prose seed plan into an ultra-plan tree bootstrap, enforcing the structural disciplines the seed's author could not (scope-tier separation, ADR fidelity, cross-node contract surfacing, interview-queue augmentation, audit trail), then hands off to `ultra-planner` mid-flow.

**Core principle:** The seed is input evidence, not ground truth. Every ambiguity surfaces as an interview row; every inferred choice is flagged as inferred; every seed section maps to a plan-tree artifact via `artifacts/ORIGIN.md`. Silent flattening of "(propose: X)" into `accepted` is a failure mode, not a shortcut.

## When to Use

| Signal | Use? |
|---|---|
| Single-file seed markdown, 500+ words, 2+ subsystems, produced by Claude/Codex/human | Yes |
| Seed has architecture section, subsystem headings, or "poncho" layout | Yes |
| Seed declares v1/v1.x/v2 scope tiers in prose | Yes — split into sub-nodes |
| User asks "turn this plan into an ultra-plan tree" | Yes |
| Blank slate, no seed, user describes idea fresh | No — `ultra-planner` Phase 0 |
| Seed already tree-shaped (nodes/, SPEC.md, INTERFACE.md on disk) | No — refuse with diff note |
| Seed under ~500 words, single subsystem, no architecture | No — `superpowers:writing-plans` |
| Seed is marketing prose with no architecture | No — synthesize PRODUCT_GOALS only, route to `ultra-planner` Phase 0 |
| Decomposing an existing node in an established tree | No — `ultra-decomposing` |

## Procedure

Operate on a seed file path provided by the user or dispatcher. Target tree root: `docs/ultra-plans/<slug>/`.

1. **Classify the seed.** Check word count, subsystem count (architecture-level headings), shape (already tree-shaped on disk?), coverage (architecture vs marketing prose). Route:
   - already tree-shaped → refuse, emit diff-style note of what a fresh bootstrap would add, stop
   - <500 words or single subsystem → recommend `superpowers:writing-plans`, stop
   - marketing prose, no architecture → synthesize PRODUCT_GOALS only, populate P0 INTERVIEW_QUEUE with architecture questions, route to `ultra-planner` Phase 0, stop
   - architecture seed, 2+ subsystems → continue

2. **Scaffold tree skeleton.** Create `docs/ultra-plans/<slug>/` with empty `ROOT.md`, `SESSION.md`, `DECISIONS.md`, `INTERVIEW_QUEUE.md`, `PRODUCT_GOALS.md`, and `artifacts/`.

3. **Write `artifacts/ORIGIN.md` early.** Copy the seed verbatim into a fenced block; start a mapping table: `seed section | captured in | verbatim/inferred/dropped | notes`. Update as later steps emit artifacts. ORIGIN.md exists before PRODUCT_GOALS is written, not after.

4. **Extract PRODUCT_GOALS.md.** Pull context, outcomes, non-goals from the seed. If the seed has a Verification/Acceptance section, copy it verbatim under a "Verification / Acceptance Criteria" heading — never drop it. Update ORIGIN.md.

5. **Extract DECISIONS.md with ADR fidelity.** For each architectural commitment, write an ADR with status, rationale, alternatives, tradeoffs. If the seed has no rationale, DO NOT fabricate — file a P1 interview item ("rationale for X not stated") and mark ADR `proposed — rationale pending`. Seed says "(propose: X)" or "tentative" → status `proposed`, never `accepted`. Update ORIGIN.md.

6. **Identify top-level nodes.** Read structural cues: poncho subsystem headings, service/app boundaries, explicit module lists. For each node, create `nodes/NN-<slug>/SPEC.md` + `INTERFACE.md` stubs. SPEC.md: owned responsibilities verbatim, non-responsibilities if stated. INTERFACE.md: exposes / depends-on / events; types not defined in seed → `TBD — see INTERVIEW_QUEUE`. Visibly less detail than siblings → write `NOTES.md` with `depth-disparity: flagged` and append P1 interview item.

7. **Scope-tier splits become sub-nodes, not annotations.** Seed declares v1/v1.x/v2 tiers for a subsystem → split into separate sub-node dirs (`nodes/NN-<slug>/01-v1/`, `02-v1.x/`, `03-v2/`) with their own SPEC.md, NOT a SPEC annotation. Scope-pruning operates on nodes; flat annotations defeat pruning.

8. **CHILDREN.md coverage matrix — mandatory for any parent with ≥2 children.** Table: one row per parent responsibility, exactly one owning child. Empty row = missing child. Two owners = overlap, file P0 item. Append an explicit non-overlap paragraph and a public-surface map if parent INTERFACE exposes symbols.

9. **Top-level `INTERFACES.md` — cross-node shared types.** Every type, event, call, or identifier crossing a node boundary goes into `INTERFACES.md` at tree root (separate from per-node `INTERFACE.md`). Each entry: producer node, consumer node(s), defined-where. Undefined → `defined-where: TBD — see INTERVIEW_QUEUE`.

10. **INTERVIEW_QUEUE.md — augment beyond seed's explicit open questions.** Copy every open question from the seed. THEN append bootstrap-inferred gaps from steps 3-9: ADRs with missing rationale, undefined cross-node types, depth-disparity flags, scope-tier ambiguities, invention candidates (struct shapes, event-name conventions, client choices, endpoint ownership, timing/lifecycle assumptions). Each new row: P0/P1/P2, topic, default, rationale. A bootstrap that produces fewer new questions than the seed listed is a red flag.

11. **Structural-coverage self-check.** Walk on disk:
    - Every seed section mapped in ORIGIN.md?
    - Every ADR has rationale + alternatives, OR is `rationale pending` with a P1 row?
    - Every cross-node type appears in top-level `INTERFACES.md`?
    - Every parent with ≥2 children has CHILDREN.md with non-overlap paragraph?
    - Every "(propose: X)" preserved as `proposed`, not flattened?
    - Seed's Verification/Acceptance captured in PRODUCT_GOALS?
    - Depth-disparity nodes flagged with interview row?
    Missing any → fix before handoff. Full cross-doc-review runs in the planner.

12. **Write handoff in SESSION.md.** Name the phase: **Phase 2 (refinement)** if the seed is clean and tree well-shaped; **Phase 3 (scope-pruning)** if seed has v1/v1.x/v2 tiers or feature count looks bloated. Record rationale. Recommend a tree-review (`ultra-cross-doc-review`) as planner's first action, then scope-pruning if tiers exist. Record interview/ADR counts. Update ROOT.md tree view.

## Red Flags — STOP and self-correct

- Guessing at an ambiguous seed item without filing an INTERVIEW_QUEUE row
- Copying seed prose as an ADR without rationale + alternatives + tradeoffs
- Flattening "(propose: X)" or "tentative" into `accepted` status
- Folding v1/v1.x/v2 scope tiers into a single SPEC as annotations instead of sub-nodes
- Skipping `artifacts/ORIGIN.md` or writing it after the other artifacts are done
- Inventing struct shapes, event-name conventions, HTTP client choices, endpoint ownership, or adapter-registration timing not present in the seed
- Dropping the seed's Verification / Acceptance Criteria section
- Not creating CHILDREN.md for any parent with ≥2 children
- Leaving depth-disparity nodes unflagged in NOTES.md with no corresponding interview row
- Interview queue shorter than or equal to the seed's original open-question list (no bootstrap-inferred gaps added)
- No top-level `INTERFACES.md` despite cross-node types crossing boundaries
- SESSION.md handoff without a named phase (2 vs 3) and rationale

## Common Mistakes

- **Silent ambiguity papering:** seed says "shared, see open question" and skill propagates the phrase into SPEC without filing an interview row. Counter: every "shared", "TBD", "see open question" becomes an INTERVIEW_QUEUE row with id and priority.
- **Ownership hand-waving:** multiple components write the same resource (DB, file, topic); skill notes it in "cross-cutting" prose without an owner. Counter: shared-resource ownership is P0 — assign to one node or file a P0 row.
- **Dep relationship unresolved:** two techs listed as deps with no relationship stated. Counter: file an interview row for the role statement.
- **"TBD" as answer:** writing `provider: TBD` in INTERFACE without an interview row. Counter: every TBD MUST point to an INTERVIEW_QUEUE id.
- **Scope-tier guessing:** assigning v1/v1.x/v2 labels where the seed does not. Counter: untiered nodes stay untiered; file a P1 row.
- **Dropping verification:** treating the seed's acceptance section as optional. Counter: acceptance criteria are load-bearing for scope-pruning; never drop.
- **Invented conventions:** naming rules (dotted event strings), struct shapes, client choices (Req/Finch), registration timing ("on app start"). Counter: if the seed doesn't state it, it's invention — flag as P1 interview or P2 ADR stub, never assert.
- **Flat-fold of fat nodes:** a ~20-file node left as a single flat SPEC. Counter: note `decomposition-pressure: high` in NOTES.md and append a P1 item recommending `ultra-decomposing` after refinement.
- **Silent ADR upgrade:** "(propose: postgres)" becomes `status: accepted`. Counter: propose stays proposed; transitions happen via interview answer or explicit ADR review.
- **Default-to-Phase-2 handoff:** routing every seed to refinement. Counter: seeds with scope tiers route to Phase 3 — prune before refining the wrong set.

## Reference

- `ultra-planner/SKILL.md` — handoff target; Phase 2 vs Phase 3 gates.
- `ultra-decomposing/SKILL.md` — runs AFTER this skill when a bootstrapped node flags decomposition pressure. Non-overlapping: decomposing splits existing nodes; this seeds from prose.
- `ultra-scope-pruning/SKILL.md` — dispatched by planner after handoff when scope tiers exist.
- `ultra-interviewing/SKILL.md` — INTERVIEW_QUEUE.md format, P0/P1/P2 triage, defaults-and-flag convention.
- `ultra-writing-plans/SKILL.md` — cross-node INTERFACE discipline; consulted later for leaf PLAN.md files.
- `ultra-cross-doc-review/SKILL.md` — full review pass; planner's first post-handoff action.
- `ultra-skills/docs/DESIGN.md` §Plan Tree Directory Model — canonical tree shape.
