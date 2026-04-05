---
name: ultra-scope-pruning
description: Use when a plan tree has accumulated features and scope feels bloated, when a v1 feature list exceeds what one small team can ship, when ultra-planner's prune phase dispatches this skill, or when the user asks "what should we cut?" NOT for deciding initial scope from scratch (use superpowers:brainstorming) and NOT for cutting tasks inside a single leaf plan.
---

# ultra-scope-pruning

## Overview

Walks an accumulated feature set and forces a YAGNI pass. Every feature must justify itself against a named anchor use case or get cut. Called by `ultra-planner` during the prune phase.

**Core principle:** No pruning without an anchor. A v1 feature list with no ICP and no core job is not a scope problem — it is a product problem, and it must be resolved before any KEEP/CUT verdict has meaning.

## When to Use

| Signal | Use? |
|---|---|
| Plan tree lists 15+ candidate features for a single release | Yes |
| User says "this feels bloated" / "help me cut scope" | Yes |
| ultra-planner dispatches prune phase | Yes |
| Feature list exists but no named ICP / core job | Yes — start by eliciting the anchor |
| Choosing initial scope with no features drafted yet | No — use superpowers:brainstorming |
| Cutting tasks inside one leaf PLAN.md | No — handle inline in that plan |

## Procedure

Operate on the plan tree root. Do not skip or reorder steps 1-2.

1. **Elicit/verify anchor use case.** Open `PRODUCT_GOALS.md`. The anchor must name: (a) the ICP (who specifically, not "teams" or "users"), (b) the core job they hire this product for, (c) the one workflow that must feel magical in v1. If any of the three is missing or hand-wavy, append P0 questions to `INTERVIEW_QUEUE.md` and STOP. Do not proceed to pruning.

2. **Group features by category.** Read every node's SPEC.md. Produce a flat list of candidate v1 features, then group them into 4-8 categories (e.g. docs / chat / calls / tasks / admin / infra). Write the grouped list to `nodes/_prune/FEATURES.md` (create the `_prune` working dir if absent). Grouping first prevents one-by-one anchoring on whichever feature you read most recently.

3. **Walk each feature. Demand KEEP justification.** For every feature, write one line tying it (or failing to tie it) to the anchor from step 1. The default verdict is CUT. A KEEP verdict requires an explicit sentence: "This is required for [anchor job] because [mechanism]." If you cannot write that sentence, the verdict is not KEEP.

4. **Emit a verdict per feature.** One of: **KEEP** (required for anchor job), **DOWNSCOPE** (anchor needs a thin version, not the full thing — name the thin version), **DEFER** (useful but not for v1 — name the trigger that would revive it), **CUT** (not aligned with anchor). Each verdict carries a one-sentence rationale. Write verdicts into `FEATURES.md` next to each feature.

5. **Name the accommodating-stance bias when you catch it.** If you find yourself wanting to KEEP a feature because "the user listed it" or "it would be sad to cut" or "it might be useful later" — stop and write `BIAS: accommodating stance` next to that row. The user's original list is not a justification. Past effort spent discussing a feature is not a justification. Convert to CUT or DEFER unless a real anchor tie exists.

6. **Offer >=2 alternative v1 scopes.** From the KEEP + DOWNSCOPE set, build at least two coherent alternative v1 bundles (e.g. "docs-anchored v1" vs "tasks-anchored v1" vs "thin-slice-across-all v1"). For each alternative, give a rough build-time estimate (weeks) and name what it gives up. The user picks; you do not pick for them.

7. **Append cuts to DECISIONS.md as ADRs.** For every CUT, DEFER, and DOWNSCOPE verdict, append a row/entry to `DECISIONS.md` so the reasoning survives. Minimal ADR shape:

   ```
   ## ADR-NNN: Cut <feature> from v1
   Date: YYYY-MM-DD  Status: proposed  Verdict: CUT
   Anchor: <ICP + core job>
   Rationale: <one sentence: why not aligned>
   Revive-if: <trigger that would reopen this>
   ```

8. **Surface residual open questions to INTERVIEW_QUEUE.md.** Anything that blocked a verdict — ICP ambiguity, pricing model unclear, competitive positioning, team size constraints, which alternative scope to pick — goes into the queue with P0/P1/P2 priority. Do not silently assume.

9. **Update SESSION.md and ROOT.md.** Record last action, next planned action, and surface the alternative-scope choice to the user at the next checkpoint.

## Red Flags — STOP and self-correct

- Starting to walk features before the anchor use case is named and written
- Emitting verdicts without per-feature rationale, or with rationale only for CUTs
- Keeping a feature because "the user mentioned it" or "we already discussed it" (accommodating-stance bias — name it, then re-verdict)
- Picking one alternative v1 scope on the user's behalf instead of offering >=2
- CUTs not appended to DECISIONS.md (reasoning will evaporate)
- "We can keep everything if we prioritize well" — this is not a prune pass, restart
- Walking features in original-list order instead of grouping by category first
- Open ambiguities silently resolved instead of queued to INTERVIEW_QUEUE.md

## Common Mistakes

- **Skipping the anchor:** pruning a feature list whose ICP is "teams" and whose core job is "productivity" produces noise. Force specificity first, even at the cost of stopping the prune.
- **KEEP-by-default:** treating the user's list as the baseline and looking for reasons to cut. Invert: CUT is the default, KEEP requires an explicit anchor tie.
- **One-scope answer:** delivering a single recommended v1 instead of >=2 alternatives. Pruning is a decision aid, not a decision.
- **Verdict without rationale:** CUT/KEEP tags with no sentence. A future reader will reverse the call.
- **DEFER as a hiding place:** marking everything DEFER to avoid conflict. DEFER needs a named revive trigger; without one, it is CUT.
- **No ADR trail:** cuts discussed in chat but not written to DECISIONS.md. Next session, the same features re-accumulate.
