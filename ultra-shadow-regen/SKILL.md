---
name: ultra-shadow-regen
description: Use when a leaf has a frozen planning-shadow AND real code and you need a fresh current-shadow derived from code plus a raw divergence report. Entry point for Pattern L3 regen-on-demand — onboarding, refactor planning, architecture queries post-implementation, or the derive-step feeding ultra-shadow-drift's classification. NOT for first-time shadow generation (use ultra-shadow-code); NOT for judging deltas as bugs/updates/acceptable (use ultra-shadow-drift).
---

# ultra-shadow-regen

## Overview

Derives a **current-shadow** from real code in the same TypeScript+ADT format the planning-shadow uses, then emits a raw `SHADOW_DIVERGENCE.md` comparing frozen planning vs current. Produces **structured deltas, not judgements** — downstream `ultra-shadow-drift` classifies each delta as bug / update / acceptable.

**Core principle:** Regen is derivation, not editorial. It reads code, matches the planning-shadow's density and format, and emits divergences across five orthogonal axes with a `[+]` / `[-]` / `[~]` legend. Frozen planning-shadow is read-only input; output lands in `SHADOW_CURRENT/` beside `SHADOW/`, never inside it. See `ultra-skills/docs/SHADOW_SPEC.md` §3 and `research/shadow-code/LIFECYCLE.md` for L3 rationale.

## When to Use

| Signal | Use? |
|---|---|
| Leaf has `SHADOW/META.md` with `STATUS: frozen` + real code exists | Yes |
| Onboarding contributor wants fresh architecture view | Yes |
| Refactor planning — need to see current shape before changing it | Yes |
| About to run `ultra-shadow-drift` — regen derives what drift classifies | Yes |
| Leaf's `SHADOW_POLICY: living` is set | Yes — but regen is informational-only, warn user |
| No planning-shadow exists yet | No — use `ultra-shadow-code` |
| `SHADOW/META.md` shows `STATUS: planning` (not yet frozen) | Warn — regen-on-non-frozen is informational only |
| You want judgement on which deltas are bugs | No — regen derives; `ultra-shadow-drift` classifies |
| Real code doesn't exist yet | No — nothing to derive from |

## Procedure

Operate on a leaf node path `nodes/<leaf>/`. Do not skip or reorder.

1. **Verify frozen-shadow input.** Read `nodes/<leaf>/SHADOW/META.md`. Check `STATUS: frozen`. If `planning` → warn "regen on non-frozen shadow is informational only." If `graduated` → proceed, note in report header. If no META.md or no `SHADOW/` → STOP, redirect to `ultra-shadow-code`.

2. **Read the real-code tree.** Enumerate files from `PLAN.md`'s file-structure map. Read every module plus companion `types.ts` / `index.ts`. Prefer AST extraction (`ts-morph`, `tsc --noEmit`) where available; otherwise parse manually. Read tests too — they reveal output contracts the source embeds implicitly.

3. **Read each planning-shadow module.** From `SHADOW/`, note `context()` headers, error-enum variants, function signatures, cross-node hashes, and open-questions from `META.md`. This is your diff baseline.

4. **Derive current-shadow per module.** Emit `<module>.shadow.ts` into `nodes/<leaf>/SHADOW_CURRENT/` (create if missing — **NEVER write into `SHADOW/`**). Match planning-shadow format: `context()` header with real imports/touches/exports; type decls with real names; error enum as discriminated union if code uses `Result<T,E>`, else name thrown types and flag `// !! planning had ADT, current uses throws`; function bodies as comments with `// !Err:` / `// =>` prefixes, one step per line. **Preserve planning-shadow's section scaffolding** (e.g. `// ── Types ──`) with `// !! removed entirely` stubs where sections collapse — keeps visual diff legible.

5. **Density match.** Compute current-shadow tokens (chars / 4). Target within ±20% of planning-shadow. Outside → flag in report header as "density drift: current is N% of planned." Do NOT pad or trim to hit target — flag it.

6. **Compute divergence across 5 axes:**
   - **Types** — per interface/alias: field adds/removes/renames, union-arm changes, wrapper shape
   - **Signatures** — per function: param list, return type, nullable/result-wrapping
   - **Dataflow** — per pipeline step: filtering, sorting, grouping, windowing, composition
   - **Error-paths** — per condition: planned handling vs current handling
   - **Planning-question disposition** — each P0/P1/P2 from planning `META.md`: resolved-by-decision / resolved-by-removal / still-open / answered-against-plan

7. **Emit `nodes/<leaf>/SHADOW_DIVERGENCE.md`** with canonical sections in order:
   ```
   # Shadow Divergence Report
   **Module:** <leaf-id>
   **Planning-shadow:** <path> (STATUS: frozen|planning|graduated)
   **Current-shadow:** <path> (derived YYYY-MM-DD)
   **Real code:** <path>
   **Density:** planned=N tok / current=M tok / ratio=R%

   Legend: [+] in current NOT in planned · [-] in planned NOT in current · [~] in both but changed

   ## 1. Headline metrics
   ## 2. By type
   ## 3. By signature
   ## 4. By dataflow
   ## 5. By error-path
   ## 6. By module/file structure
   ## 7. Planning-question disposition
   ## 8. Net-shape summary
   ```

8. **Tag every divergence** with `[+]` / `[-]` / `[~]`. Sections 2, 3, 7 use markers on every line. Sections 4–5 may omit markers in row bodies where side-by-side table columns make direction obvious; legend at report top always declares them.

9. **Link from ROOT.md.** Append under this leaf's status entry: `- SHADOW_DIVERGENCE.md: <date> (N type deltas, M signature deltas)`. Surfaces regen output at tree level.

## Red Flags — STOP and self-correct

- Writing current-shadow into `SHADOW/` instead of `SHADOW_CURRENT/` — frozen shadow is read-only, terminal
- Running regen without checking `STATUS: frozen` marker first
- Emitting judgement language ("this is a bug", "this is wrong", "regression") — regen is descriptive only; classification is `ultra-shadow-drift`'s job
- Current-shadow density outside ±20% with no flag in divergence report header
- Divergence report missing any of the 8 canonical sections
- `[+]` / `[-]` / `[~]` legend absent or markers missing from type/signature/question sections
- Planning-question disposition section collapsed into prose instead of per-question row mapping
- Skipping open-questions axis because "they're already answered in the code" — that IS the disposition finding
- Overwriting a prior `SHADOW_CURRENT/` without timestamping or noting regen date in header
- Re-invoking `ultra-shadow-code` when regen is what's needed (writes to wrong directory)

## Common Mistakes

- **Classifying-while-deriving:** adding "bug" / "acceptable" / "update" labels inline. Regen stays descriptive; downstream drift classifies. Mixing the two loses the clean handoff.
- **Skipping the density check:** producing a 3-line current-shadow against a 160-line planning-shadow and calling it done. Density mismatch is itself a finding — flag it, don't hide it.
- **Textual line-diff thinking:** treating this as `diff SHADOW/ SHADOW_CURRENT/`. Shadow-to-shadow line diffs are noise when formats evolve; the 5-axis structural diff is what earns its keep.
- **Forgetting planning-question disposition:** it's the highest-signal axis — "all 5 planning Q's were resolved by REMOVAL not decision" is the kind of architectural insight that only surfaces here. Dedicated section, not afterthought.
- **Preserving planning-shadow scaffolding half-heartedly:** either keep all its section headers (with `// !! removed` stubs for collapsed sections) or derive fresh structure from code. Half-measures make visual diffing harder, not easier.
- **Ignoring tests:** the test file reveals output contracts (e.g. exact block shapes, trailing-divider rules) that the source may embed implicitly. Read tests alongside source.
- **Re-running on a non-frozen shadow without the warning:** planning-shadow mid-iteration will diverge from code by construction — regen output is low-signal until freeze.

## Reference

- `ultra-skills/docs/SHADOW_SPEC.md` — canonical format rules you must match when deriving.
- `ultra-skills/research/shadow-code/LIFECYCLE.md` — L3 regen-on-demand policy rationale.
- `ultra-skills/ultra-shadow-code/SKILL.md` — produces the planning-shadow you diff against.
- `ultra-skills/ultra-shadow-drift/SKILL.md` — classifies the deltas you derive (downstream consumer).
