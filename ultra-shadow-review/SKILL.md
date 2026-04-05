---
name: ultra-shadow-review
description: Use when a shadow-code artifact was just generated and awaits review before freeze, at the Phase 5.5b gate between ultra-shadow-code and real-code handoff, or about to freeze a SHADOW/ dir for real-code gen. Cheap architecture review of typed pseudocode before real code embeds the bugs. NOT for frozen shadows, NOT for real code (use superpowers:requesting-code-review), NOT for cross-tree INTERFACE review (use ultra-cross-doc-review).
---

# ultra-shadow-review

## Overview

Reviews a leaf node's `SHADOW/` artifacts — the typed pseudocode produced by `ultra-shadow-code` — BEFORE real-code generation. Walks a fixed dimension checklist, triages findings BLOCKER/MAJOR/MINOR, proposes concrete fixes + test sketches for BLOCKERs, promotes P0 findings to `INTERVIEW_QUEUE.md`, and emits a freeze verdict: FREEZE / REVISE / ESCALATE. Only FREEZE allows the shadow to transition to `STATUS: frozen` and hand off to real-code gen.

**Core principle:** Catch architecture bugs at the shadow layer where iteration is cheap (~5× cheaper than post-real-code review). Every finding must name a shadow line, carry a severity, propose a concrete fix — and every BLOCKER must carry a one-line test sketch that would catch the bug if it slipped into real code. Freeze is a gate, not a rubber stamp.

**Checklist scope:** walks a 9-dimension shadow-review checklist (distinct from `ultra-reviewer`'s 11-dimension suite checklist — different target, different dimensions).

## When to Use

| Signal | Use? |
|---|---|
| `ultra-shadow-code` just emitted `SHADOW/` with `STATUS: planning` | Yes |
| Phase 5.5b gate: about to freeze shadow for real-code handoff | Yes |
| Shadow revised after a prior REVISE verdict | Yes (re-review) |
| Shadow has `STATUS: frozen` already | No — frozen is terminal |
| Real code exists, want drift check | No — `ultra-shadow-drift` |
| Review INTERFACE.md coherence across whole tree | No — `ultra-cross-doc-review` |
| Review real code | No — `superpowers:requesting-code-review` |

## Procedure

Operate against a leaf node's `SHADOW/` dir at `nodes/<leaf>/SHADOW/`. Do not skip or reorder.

1. **Load target inputs.** Read every file in `SHADOW/` (each `<module>.shadow.ts` + `META.md`), plus this leaf's `SPEC.md`, `INTERFACE.md`, `PLAN.md`. Count modules from `META.md` module list; assert count matches files on disk. Missing file → log as finding, continue.

2. **Load sibling context.** For every `context()` import (parent INTERFACE.md, each sibling INTERFACE.md in depends-on, each consumer INTERFACE.md), **open and read the actual file**. Record its current hash. Do not review cross-module calls from memory — cite the opened file.

3. **Walk the 9-dimension checklist in order.** Do not skip a dimension because "nothing looked wrong":
   - **Purity / side-effect discipline** — do functions claiming purity inject their clocks/IDs/randomness? Any hidden `Date.now()`, `Math.random()`, I/O?
   - **Type contracts** — does every exported type match the shape promised in this leaf's INTERFACE.md? Field names, optionality, enum members exact?
   - **Error taxonomy completeness** — every fallible path emits a named ADT variant? Discriminated union exhaustive at every consumer? No silent throws, no `warnings: string[]` improvisation.
   - **Cross-module data-flow** — is each `context()` header accurate (imports/touches/exports list matches actual file contents)?
   - **Anchor-use-case fit** — walk the SPEC.md anchor scenario through the shadow end-to-end. Does the happy path produce the anchor output?
   - **Cross-field invariants** — fields that constrain each other (e.g. `state==="merged"` vs `mergedAt!==null`). Are precedence and violation handling specified?
   - **Provenance verification** — every `// @hash:<sha>` comment matches the sibling INTERFACE.md's **current** hash recorded in Step 2. Drift → BLOCKER.
   - **Downstream-consumer shape** — the shadow's output type matches what the downstream sibling's INTERFACE.md says it accepts (e.g. `SlackBlocks` vs bare `SlackBlock[]`).
   - **Token-budget ratio** — `META.md`'s declared `ratio: R%` in 15-25% range. Compute actual shadow token count (chars/4); flag if META's number is stale or out of range.

4. **Triage findings.**
   - **BLOCKER** — real-code-gen would embed this bug. Purity violation, type-shape mismatch with INTERFACE.md, unhandled ADT variant, provenance-hash drift, cross-module signature mismatch, missing case on anchor path.
   - **MAJOR** — significant architecture issue. Undefined policy (dedupe, sort stability, empty-state), cross-field invariant not specified, token ratio outside range, downstream shape unverified.
   - **MINOR** — cosmetic or doc-only. Naming nit, ambiguous JSDoc, stylistic inconsistency, label-vs-data concern split.

5. **Write concrete fix proposals.** Each finding ends with a one-line fix recommendation naming the specific signature change, policy decision, or file edit. Not "fix it" — the diff-level action.

6. **Attach test sketches to BLOCKERs.** Every BLOCKER gets a one-line test case that would fail against the bug if it shipped. Example: `test: generateDigest({...input, now: undefined}) should fail to type-check`. This becomes input to real-code TDD.

7. **Promote P0 items.** Every BLOCKER and every P0 open-question surfaced by the review gets appended to tree-level `INTERVIEW_QUEUE.md` at P0. Cross-reference the REVIEW.md finding ID.

8. **Emit verdict.** At the end of REVIEW.md, a single line:
   - `VERDICT: FREEZE` — zero BLOCKERs, MAJORs acceptable. Shadow may transition to `STATUS: frozen`.
   - `VERDICT: REVISE` — 1+ BLOCKERs OR MAJORs deemed blocking by reviewer. Shadow cycles back to `ultra-shadow-code` with this review attached.
   - `VERDICT: ESCALATE` — review surfaces questions the reviewer can't answer (missing SPEC decisions, absent sibling INTERFACE, contradictory user intent). Surface to ultra-interviewing / user.

9. **Persist REVIEW.md.** Write to `nodes/<leaf>/SHADOW/REVIEW_<YYYY-MM-DD>.md`. If a prior review exists same day, suffix `-HHMM`. Include at top: `Reviewed N files: [list]` + `Checklist: purity, types, errors, dataflow, anchor-fit, invariants, provenance, downstream, tokens` + counts `BLOCKER: X / MAJOR: Y / MINOR: Z`.

## Red Flags — STOP and self-correct

- Reviewing a cross-module call from memory without opening the sibling INTERFACE.md
- Reviewing only one shadow file when `SHADOW/` contains multiple modules
- Skipping a checklist dimension because "it looked clean"
- Findings emitted without a BLOCKER/MAJOR/MINOR triage tag
- BLOCKER without a one-line test-sketch proposal
- Finding without a concrete fix proposal (just "looks wrong" / "consider X")
- Skipping provenance hash verification — treating `// @hash:abc123` as decorative
- Emitting REVIEW.md without a `VERDICT:` line
- FREEZE verdict with any open BLOCKER
- P0 findings not promoted to `INTERVIEW_QUEUE.md`
- Token-ratio check skipped because "META.md said it was fine"
- Reviewing a `STATUS: frozen` shadow (frozen is terminal — use `ultra-shadow-drift`)

## Common Mistakes

- **Memory-reviewing sibling types:** assuming you remember what `PRRecord` looks like from earlier context instead of opening `01-github-fetcher/INTERFACE.md`. Cross-reference unverified = provenance drift invisible.
- **Single-file tunnel-vision:** reviewing `digest.shadow.ts` while ignoring `dedupe.shadow.ts` and `META.md` in the same `SHADOW/`. Multi-module shadows break at the seams — review all files.
- **Organic checklist:** improvising dimensions based on what catches your eye. Misses entire classes (token-budget, downstream shape, provenance) every time. Walk the named 9-dimension list in order.
- **Fix-less findings:** "M3: cross-field invariant not enforced" with no proposed fix. Author can't act — review is debt, not value. Every finding owns its fix.
- **BLOCKER without test sketch:** "this is a BLOCKER" without the one-line test that would catch it. Downstream real-code TDD loses the hook.
- **Rubber-stamp FREEZE:** emitting FREEZE because "no obvious bugs" instead of walking every dimension. Freeze is a gate — the verdict is load-bearing for the real-code handoff.
- **Triage inflation:** promoting MINORs to MAJOR because they felt important. Severity discipline exists so the author knows what must block vs what can polish later.

## Reference

- `ultra-skills/docs/SHADOW_SPEC.md` — canonical format + lifecycle spec (required read).
- `ultra-skills/ultra-shadow-code/SKILL.md` — sibling skill that writes the shadow being reviewed.
- `ultra-skills/ultra-cross-doc-review/SKILL.md` — structural reference for severity triage + patch discipline.
- `ultra-skills/research/shadow-code/LIFECYCLE.md` — why FREEZE matters (STATUS transitions).
- `ultra-skills/research/shadow-code/INTEGRATION_IDEAS.md` — 4-skill family context.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
