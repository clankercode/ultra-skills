---
name: ultra-shadow-drift
description: Use when real code exists for a leaf and you need to check drift against the frozen planning-shadow, before merging a PR touching a shadow-fronted module, or as periodic post-implementation audit. Emits a dated drift report classifying each delta BUG / SHADOW-UPDATE / ACCEPTABLE-EVOLUTION / FEATURE-DROPPED and prioritized for fix. NOT for planning-status shadows (use ultra-shadow-review), NOT for fresh current-shadow derivation (use ultra-shadow-regen).
---

# ultra-shadow-drift

## Overview

Compares a leaf's real code against its **frozen planning-shadow** and emits a classified, prioritized drift report. Every delta is tagged BUG (real code must change), SHADOW-UPDATE (real code wins, shadow catches up), ACCEPTABLE-EVOLUTION (harmless refinement), or FEATURE-DROPPED (scoped-out intentionally). BUGs become task candidates; SHADOW-UPDATEs suggest `ultra-shadow-regen`; ACCEPTABLE-EVOLUTION and FEATURE-DROPPED become ADR stubs in `DECISIONS.md`.

**Core principle:** Drift without classification is noise; classification without priority is debt. Walk a named checklist in fixed order, compute rollup metrics, and surface test-complicity (tests that pass *because* they fail to assert missing behavior) as a first-class risk tier.

## When to Use

| Signal | Use? |
|---|---|
| Real code landed for a leaf with `STATUS: frozen` shadow | Yes |
| About to merge a PR touching a shadow-fronted module | Yes |
| Periodic audit of architecture drift post-implementation | Yes |
| Shadow is still `STATUS: planning` (not yet frozen) | No — `ultra-shadow-review` |
| Need a fresh shadow derived from current real code | No — `ultra-shadow-regen` |
| No real code yet | No — premature |
| Leaf is `STATUS: graduated` (shadow is advisory) | Yes, but findings are advisory only |

## Procedure

Operate on a leaf node at `nodes/<leaf>/` with a `SHADOW/` dir and real code in the project tree. Do not skip or reorder.

1. **Load both artifacts + verify frozen.** Open `SHADOW/META.md`. Assert `STATUS: frozen` (or `graduated`). If `planning`, **STOP** — wrong skill; route to `ultra-shadow-review`. List every `<module>.shadow.ts`, resolve the real-code tree (`src/<leaf>/` or as META.md notes), read every shadow file, every real-code source, every test. Record counts atop the report.

2. **Build symbol inventory — both sides.** Shadow: exported types, error-enum variants, function signatures, cross-node imports (with pinned `// @hash:`). Real code: same list. Keep side-by-side — this is the evidence base for dimensions below.

3. **Walk the 7-dimension drift checklist in order.** Do not skip a dimension because "nothing obvious":
   - **Types** — every shadow type present in real code with matching shape (fields, optionality, union members exact).
   - **Signatures** — params + return types match (`Result<T, E>` vs bare `T`).
   - **Error-paths** — every ADT variant is *actually raised*. Enum declared but never constructed = silent drop.
   - **Dataflow** — control-flow steps in shadow bodies (one per line) present in real code. A step like `// filter p.state==="merged" && inWindow(p.mergedAt, window)` requires BOTH filters.
   - **Cross-module boundaries** — real-code cross-node imports resolve to *current* sibling INTERFACE shape (see Step 4).
   - **Features-dropped** — shadow-declared helpers, fields, or exports absent from real code. Dead exports on either side are a tell.
   - **Test-coverage-complicity** — for each BUG candidate, check tests. A test that passes *despite* the bug (e.g. doesn't assert zero-count rows when shadow required them) is complicit.

4. **Sibling INTERFACE re-hash cross-check.** For every cross-node type real code imports from a sibling, open the current sibling INTERFACE.md, recompute its hash, and compare to the shadow's pinned `// @hash:`. If the sibling drifted since freeze, log as its own drift entry (BUG if real code now depends on a shape the sibling no longer emits; SHADOW-UPDATE if benign).

5. **Classify each delta.** Four categories with explicit criteria:
   - **BUG** — real code violates a still-right shadow decision (missing filter, unhandled error, dropped invariant, silent throw, broken anchor use case).
   - **SHADOW-UPDATE** — real code made a defensible different call (simpler shape, cleaner naming, cut unnecessary field). Shadow catches up.
   - **ACCEPTABLE-EVOLUTION** — superset refinement (extra fields from producer, enriched type contracts, non-breaking additions).
   - **FEATURE-DROPPED** — deliberate scope cut after freeze. Distinguished from BUG by *intent* — if traceable and deliberate, FEATURE-DROPPED.

6. **Prioritize BUGs: severity × effort-to-fix-now.** Severity: breaks anchor use case (HIGH) / degrades correctness (MED) / cosmetic (LOW). Effort: one-line ripple-free (LOW) / several files (MED) / cross-node renegotiation (HIGH). Priority = severity × inverse-effort; HIGH-sev + LOW-effort tops the list. Test-complicit BUGs jump one tier (tests are lying, risk is hidden).

7. **Compute rollup metrics.** At top of report: total drifts, per-category counts, drift rate = drifts ÷ planned-surface-items (exported symbols + error variants + signature params counted from shadow). Bands: under 10% clean, 10-25% expected, over 25% investigate.

8. **Emit report + downstream artifacts.** Write `nodes/<leaf>/DRIFT_REPORT_<YYYY-MM-DD>.md`. Group by category; each entry has shadow ref (file:line), real-code ref, quoted evidence, classification rationale, priority (BUGs only), test-complicity tag. BUGs → task candidates in `DRIFT_FIX_TASKS.md`. SHADOW-UPDATEs → recommend `ultra-shadow-regen`. ACCEPTABLE-EVOLUTION + FEATURE-DROPPED → ADR stubs in this leaf's `DECISIONS.md`, one per entry, dated, with rationale.

## Red Flags — STOP and self-correct

- Running against `STATUS: planning` (wrong skill — use `ultra-shadow-review`)
- Eyeballing without the Step-2 symbol inventory
- Skipping a checklist dimension because "nothing obvious"
- Findings without 4-way classification
- BUGs without severity × effort priority
- Report missing rollup metrics (total drifts, per-category counts, drift rate)
- Skipping sibling INTERFACE re-hash — misses upstream drift
- Test-complicity not checked per BUG
- Writing report to chat, not `nodes/<leaf>/DRIFT_REPORT_<YYYY-MM-DD>.md`
- Editing the frozen shadow to "fix drift" — frozen is terminal; use `ultra-shadow-regen`, never mutate the planning-shadow
- Reclassifying a BUG as SHADOW-UPDATE because "real code looks fine" without naming an anchor or contract criterion

## Common Mistakes

- **Ad-hoc diff:** walking files top-to-bottom noting oddities. Misses whole categories (features-dropped, sibling drift, test-complicity). Use the 7-dimension checklist.
- **Missing rollup metrics:** per-drift detail without "X total, Y BUGs, Z SHADOW-UPDATEs, drift rate R%". User can't triage.
- **Test-complicity blindness:** green suite + missing behavior = tests are complicit, not code "working." Surface as its own tier.
- **Sibling-blindness:** comparing only shadow ↔ real code, forgetting real-code imports may have drifted from sibling INTERFACE since freeze. Re-hashing siblings is mandatory.
- **Single-bucket thinking:** everything tagged "BUG" or everything "looks fine." Four-way classification forces honest triage.
- **Priority by gut:** BUGs ordered by "whichever felt worst." Use severity × effort-to-fix-now; test-complicit BUGs auto-bump one tier.
- **No fix-task artifact:** ten BUGs in the report, no `DRIFT_FIX_TASKS.md`. BUGs that aren't tasks don't get fixed.
- **ADR amnesia:** ACCEPTABLE-EVOLUTION and FEATURE-DROPPED findings discarded. They record *why* code diverged — belong in `DECISIONS.md`.

## Reference

- `ultra-skills/docs/SHADOW_SPEC.md` — canonical format + lifecycle spec (required read).
- `ultra-skills/ultra-shadow-code/SKILL.md` — sibling that produced the frozen shadow being diffed.
- `ultra-skills/ultra-shadow-review/SKILL.md` — pre-freeze review; structural template for severity triage.
- `ultra-skills/ultra-implementing-solo/SKILL.md` and `ultra-skills/ultra-implementing-team/SKILL.md` — upstream executors that produce the real code this skill checks; both dispatch `ultra-shadow-drift` post-implementation when they consumed a frozen SHADOW/.
- `ultra-skills/ultra-cross-doc-review/SKILL.md` — BLOCKER/MAJOR/MINOR triage pattern this skill adapts.
- `ultra-skills/research/shadow-code/LIFECYCLE.md` — L3 regen vs L4 graduation rationale; why frozen shadows are terminal.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
