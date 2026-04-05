---
name: ultra-shadow-code
description: Use when a leaf node in an ultra-skills plan tree has stable SPEC+INTERFACE+PLAN and is entering Phase 5.5 shadow generation, when about to write real code but want a cheap architecture review first, or when a team-dashboard-style multi-module leaf needs a cheap architecture spec before real-code gen. NOT for single-function utilities (overhead > payoff) and NOT for regenerating shadows from existing real code (use ultra-shadow-regen).
---

# ultra-shadow-code

## Overview

Generates a **planning-shadow** — a TypeScript-like pseudocode architecture spec with ADT error enums — for one leaf node. Costs ~15-25% of projected real-code tokens, surfaces architecture bugs (missing error paths, cross-module incoherence, type holes, contract drift) before any real code exists. Output lands at `nodes/<leaf>/SHADOW/` for `ultra-shadow-review`, then freezes, then real-code-gen reads the frozen shadow as design input.

**Core principle:** Shadow is a typed architecture artifact, not prose. Every fallible path names its error variant; every cross-node type cites source + hash; every open question carries a severity tier tied to a shadow line. The format does load-bearing work — ADTs catch missing-case bugs at write time. See `ultra-skills/docs/SHADOW_SPEC.md` for canonical format rules.

## When to Use

| Signal | Use? |
|---|---|
| Leaf node has stable SPEC+INTERFACE+PLAN, entering Phase 5.5 | Yes |
| Multi-module leaf with cross-node type imports | Yes |
| About to write real code but want architecture review first | Yes |
| Leaf is a one-function utility with obvious signature | No — overhead > payoff |
| Thin CRUD adapter, no architecture decisions to surface | No |
| SPEC or INTERFACE still in flux | No — stabilise first |
| Real code already exists, want a current view | No — `ultra-shadow-regen` |
| Shadow already frozen, want drift check | No — `ultra-shadow-drift` |

## Procedure

Operate on a leaf node path `nodes/<path>/`. Do not skip or reorder.

0. **Bootstrap check — project rules file.** Look for `CLAUDE.md`, `AGENTS.md`, `.cursor-rules`, or `.cursorrules` at repo root. Grep for `SHADOW_SPEC.md`. If absent, **STOP** and instruct the user to paste the "Shadow-code rules" block from `ultra-skills/docs/SHADOW_SPEC.md` §4 into the rules file. Idempotent — re-running is free when the marker is present.

1. **Prerequisite gates.** `SPEC.md` + `INTERFACE.md` stable (no `DRAFT` marker, no open P0 tied to this node), `PLAN.md` drafted, ideally `ultra-cross-doc-review` passed for this cohort. Any gate open → stop, surface to ultra-planner.

2. **Read inputs.** This node's SPEC+INTERFACE+PLAN, parent INTERFACE.md, every sibling INTERFACE.md in `depends-on`, and any consumer INTERFACE.md. Capture each sibling INTERFACE path + last-modified hash — cited inline in shadow.

3. **Enumerate modules from PLAN.md.** PLAN.md's file-structure map names modules. 1 module → single `<module>.shadow.ts`; 2+ → one file per module plus `META.md`.

4. **Draft shadow per module.** For each module emit `<module>.shadow.ts` under `SHADOW/` containing:
   - **`context()` header** declaring `imports from`, `touches`, `exports` — required, first declaration. See SHADOW_SPEC.md §2.
   - **Type declarations** using real names from INTERFACE.md.
   - **Error enum** — discriminated union `type <Module>Error = { kind: ...; ... } | ...`. Every fallible function returns `Result<T, <Module>Error>`. No silent throws, no improvised accumulators.
   - **Function signatures** with typed params + `Result<T, E>` returns.
   - **Function bodies as comments only.** One control-flow step per line. Prefix `// !Err:` before error paths, `// =>` before happy-path output. Bodies contain no executable statements.
   - **Cross-module calls** written as real TS calls: `UserRepo.lookup(input.userId)`.

5. **Cross-node provenance citations.** Every type imported from a sibling INTERFACE.md carries source path + pinned hash: `import type { PRRecord } from "../01-github-fetcher/INTERFACE.md" // @hash:a3f2c9`. Commit short-hash or mtime-derived; must match Step 2. Missing/drifted → stop, P0.

6. **Write `SHADOW/META.md`.** Contains:
   - `STATUS: planning`
   - Module list + one-line purpose each.
   - `context()` graph (which modules import which sibling interfaces).
   - **Token-budget estimate** (Step 9) + target-range flag.
   - **Tiered open questions** (Step 10).
   - **Reviewer hooks** — 2-4 specific concerns to look at (e.g. "cross-module call at digest.shadow.ts:47 vs user-store INTERFACE").
   - `SHADOW_POLICY` note (Step 11) if applicable.

7. **Exhaustiveness pass on ADTs.** For each discriminated union, verify every consumer function handles every variant. Missing case → add it, or file as P1 with variant name.

8. **Self-scan red flags.** Run Red Flags list below against the draft. Fix any hit before META.md.

9. **Token-budget estimation.** Shadow tokens (chars / 4). Estimate real-impl tokens from PLAN.md task count × ~300 tokens/task + test scaffolding. Record in META.md as `shadow_tokens: N / estimated_real_tokens: M / ratio: R%`. Target 15-25%. If < 15% flag "under-specified"; if > 30% flag "over-specified".

10. **Tier open questions.** Each question gets severity + shadow line reference:
    - **P0** — blocks real-code gen. Unresolved type shape, unknown error policy, missing contract.
    - **P1** — should resolve before gen. Ambiguous naming, dedupe policy, undefined edge case.
    - **P2** — document and continue. Stylistic, deferred, nice-to-have.
    File P0 items to tree-level `INTERVIEW_QUEUE.md` immediately.

11. **Status + escape hatch.** Default `STATUS: planning`. If leaf's `DECISIONS.md` has `SHADOW_POLICY: living`, note `POLICY: living (skip-freeze)` in META.md. Otherwise `STATUS` transitions to `frozen` at Phase 5.5 gate by `ultra-shadow-review` / planner, not here.

## Red Flags — STOP and self-correct

- Running this skill in a project with no `SHADOW_SPEC.md` reference in rules file → Step 0 failure, stop
- Drafting shadow without reading parent INTERFACE.md or sibling INTERFACE.md dependencies
- Shadow file missing `context()` header as its first declaration
- Fallible function returns `T` directly instead of `Result<T, E>` — silent throws
- Error paths written as inline comments/`warnings[]` accumulators instead of named discriminated-union variants
- Cross-node type imported without source path + pinned hash comment
- Executable statement in a function body (bodies are comments-only)
- Open questions emitted as flat list with no P0/P1/P2 tier or no shadow line reference
- META.md missing `STATUS`, token-budget ratio, or reviewer-hooks
- Writing shadow for an interior node (decompose first)
- Overwriting an existing `STATUS: frozen` shadow — frozen is terminal, use `ultra-shadow-regen` for fresh views
- Token ratio outside 15-25% with no flag written in META.md

## Common Mistakes

- **Prose-shadow:** writing English pseudocode instead of typed TS+ADT. Loses the bug-catching power — the format IS the spec.
- **Improvised error accumulator:** declaring `warnings: string[]` inline and stuffing problems into it. Makes review impossible to mechanize. Use a named `<Module>Error` discriminated union, every variant payload-typed.
- **Sibling-type re-invention:** referring to `PRRecord` without importing it from the sibling INTERFACE with hash. Future drift becomes invisible.
- **Flat open-questions list:** all questions at the bottom with no tier and no line reference. Reviewer can't triage; real-code-gen can't gate on P0s.
- **Token-eyeballing:** "looks about right" ratio instead of computing shadow/real estimate. Target range exists to catch over- and under-specified shadows.
- **Skipping Step 0:** assuming the project "probably" has shadow rules. Bootstrap check is cheap, idempotent, and prevents orphaned shadow artifacts that downstream agents don't know to respect.
- **Editing frozen shadows:** once `STATUS: frozen`, the planning-shadow is a historical design record. For fresh views, dispatch `ultra-shadow-regen`; for drift fixes, `ultra-shadow-drift`.

## Reference

- `ultra-skills/docs/SHADOW_SPEC.md` — canonical format + lifecycle spec (required read).
- `ultra-skills/research/shadow-code/FORMAT_COMPARISON.md` — format matrix + worked example.
- `ultra-skills/research/shadow-code/LIFECYCLE.md` — L3+L4 policy rationale.
- `ultra-skills/research/shadow-code/INTEGRATION_IDEAS.md` — 4-skill family context.
