# Integration Ideas: Shadow-Code as Architecture-Spec Layer → ultra-skills

**Superseded 2026-04-05.** The previous version of this file proposed five
"parallel-isolated-state / plan-tree-worktree" ideas. That framing was wrong
for this project. This rewrite reflects the clarified vision: **shadow-code
is a cheap pseudocode architecture-spec layer that sits between PLAN.md and
real code**, inspired by Pattern A from `adifyr/shadow-code`
(https://github.com/adifyr/shadow-code) but decoupled from its VS Code
transform.

See `OVERVIEW.md` for the historical record of the name-collision analysis.

---

## The vision

A leaf node in an ultra-skills plan tree currently holds `SPEC.md +
INTERFACE.md + PLAN.md`. That PLAN.md is a TDD task list handed off to an
implementation agent. The agent writes real code, possibly discovers
architecture problems halfway through, and either papers over them or
burns expensive cycles regenerating large swaths.

**Shadow-code inserts a cheap iteration layer:**

1. **Generate shadow-code** from the stable `SPEC+INTERFACE+PLAN` trio.
   Pseudocode expresses types, signatures, control flow, error paths,
   cross-module calls. Cost: ~15-25% of real-code tokens.
2. **Review the shadow** for architecture bugs, missing error paths,
   cross-module incoherence, contract violations, type holes. Cheap because
   it is short.
3. **Iterate** shadow until it passes review.
4. **Generate real code** FROM the reviewed shadow (not from PLAN.md).
   Real-code-gen is a translation step, not a design step.
5. **Drift-check** real code against shadow; emit drift reports / fix tasks.

The payoff: architecture bugs caught at shadow-review time cost
~5x less than the same bugs caught at real-code review time, and the shadow
itself becomes a focused review target that a human or LLM reviewer can
hold in working memory all at once.

**Scope boundary:** shadow-code IS planning (architecture spec).
Real-code generation is NOT in ultra-skills — it stays with whatever
implementation skill the user picks (superpowers, direct Claude Code, etc.).
Ultra-skills stops at "plan + shadow + drift-check contract."

---

## Proposed 3-skill family

### Skill 1: `ultra-shadow-code` — shadow generation

**Host:** new skill, dispatched by `ultra-planner` in a new Phase 5.5, and
directly invocable per-leaf by the user.

**Inputs:** a leaf node's `SPEC.md`, `INTERFACE.md`, `PLAN.md`, plus parent
`INTERFACE.md` and sibling-node `INTERFACE.md` references (per the
`context()` convention, see below).

**Output:** `SHADOW/` subdirectory inside the leaf node dir. Contents:
- `MODULE.shadow` — one shadow file per planned module, using the
  default format (see `FORMAT_COMPARISON.md`; TL;DR: TypeScript-like
  with ADT bias)
- `SHADOW_INDEX.md` — catalogue of shadow files + `context()` graph
- `SHADOW_NOTES.md` — assumptions, open design questions the shadow
  surfaces (often becomes new interview items)

**Procedure:**
1. Read SPEC+INTERFACE+PLAN + parent/sibling INTERFACE contracts.
2. For each module named in PLAN.md, emit a `.shadow` file with typed
   signatures, data shapes as ADTs, function stubs with `// ...` bodies,
   explicit error-path enumeration, cross-module call sites as typed
   calls with no implementation.
3. Emit `SHADOW_INDEX.md` listing modules, their `context()` neighbours,
   and the PLAN.md tasks each module backs.
4. Emit `SHADOW_NOTES.md` capturing any architectural tension the
   shadow exposed.

**Invariants:**
- Shadow files are **non-executable**. They do not compile. Enforcing
  this keeps shadow cheap.
- Shadow files DO use real type names from INTERFACE.md.
- Token budget per leaf: target 15-25% of the projected real-code size.

### Skill 2: `ultra-shadow-review` — architecture review of shadow

**Host:** new skill, usually called by `ultra-planner` after
`ultra-shadow-code`, before handoff. Also invocable directly on an
existing `SHADOW/` dir.

**Inputs:** leaf's `SHADOW/` dir + parent `INTERFACE.md` + sibling
`INTERFACE.md` dependencies.

**Output:** `SHADOW_REVIEW.md` inside the leaf node dir, listing:
- Architecture bugs (contract violations, missing error paths, dangling
  references, circular module deps, type-shape drift from INTERFACE.md)
- Cross-module incoherence (mismatched call/return shapes across modules
  in the same leaf)
- Missing cases on ADTs
- Review verdict: `PASS` | `ITERATE` | `BLOCKED`

**Procedure:**
1. Parse `SHADOW_INDEX.md` + every `.shadow` file. Treat types and
   signatures as ground truth.
2. For every cross-module call, verify the callee's signature matches.
3. For every ADT, enumerate cases and verify every consumer handles
   all cases.
4. Compare shadow's exported shapes to parent `INTERFACE.md`. Any
   mismatch = contract violation.
5. For `ITERATE`, emit concrete fix suggestions keyed to shadow line
   numbers. For `BLOCKED`, emit questions for `ultra-interviewing`.

**Iteration loop:** `ultra-planner` re-invokes `ultra-shadow-code` with
the review attached until `PASS` or the user accepts a known-gap shadow.

### Skill 3: `ultra-shadow-drift` — post-implementation drift check

**Host:** new skill, invoked AFTER real-code generation has happened
(outside ultra-skills' normal flow — this is the post-implementation
hook). Not part of the planner's default pipeline; user or implementation
harness calls it when real code exists.

**Inputs:** leaf's `SHADOW/` dir + the real-code directory that was
generated from it.

**Output:** `SHADOW_DRIFT.md` inside the leaf node dir:
- Drift report (signatures changed, modules added/removed, ADT cases
  added/dropped, error paths elided)
- Drift verdict: `SHADOW_AUTHORITATIVE` (fix real code) |
  `CODE_AUTHORITATIVE` (regen shadow from code) | `MANUAL_REVIEW`
  (design intent changed; human decides)
- Fix tasks in the same TDD shape as PLAN.md for whichever direction
  was chosen.

**Procedure:**
1. Parse shadow files, parse real code (type signatures, module graph).
2. Align by module name + function name; diff signatures and ADT shapes.
3. For each drift: classify. Signature change without spec change =
   drift to fix. Signature change with DECISIONS.md entry justifying
   it = shadow-needs-update.
4. Emit fix tasks.

**Important:** this skill runs on a best-effort basis. It does NOT block
anything. It produces a report and leaves the call to the user.

---

## DESIGN.md addition

Add a `SHADOW/` subdirectory to the leaf-node layout:

```
nodes/some-node/
  SPEC.md
  INTERFACE.md
  PLAN.md
  SHADOW/                  <-- NEW
    SHADOW_INDEX.md
    SHADOW_NOTES.md
    <module>.shadow
    ...
  SHADOW_REVIEW.md         <-- NEW, emitted by ultra-shadow-review
  SHADOW_DRIFT.md          <-- NEW, emitted by ultra-shadow-drift (later)
```

The `SHADOW/` dir is part of the plan tree and lives in the same repo
as `nodes/`. It is NOT gitignored — the shadow IS a planning artifact
with long-term value. (This is a deliberate reversal from Pattern A's
`.shadows/` → `.gitignore` convention, because in Pattern A the shadow
is the user's scratchpad, while here the shadow is the architecture
spec.)

## ultra-planner: new Phase 5.5

Insert between current Phase 5 (leaf-node plan writing) and handoff:

```
Phase 5.5: Shadow-code architecture spec
  For each leaf node:
    - ultra-shadow-code generates SHADOW/
    - ultra-shadow-review reviews SHADOW/
    - if ITERATE: loop back to ultra-shadow-code with review
    - if BLOCKED: surface to ultra-interviewing
    - if PASS: leaf is handoff-ready
```

Gate: handoff requires `SHADOW_REVIEW.md: PASS` OR an explicit user
waiver captured in `DECISIONS.md`.

## ultra-writing-plans integration

Leaf-node PLAN.md tasks should be split into two bands:

- **Shadow-gen tasks:** "Draft `<module>.shadow` covering [responsibility]
  with types [X, Y, Z] and error cases [A, B]." These precede any
  real-code task.
- **Real-code tasks:** "Implement `<module>` from `SHADOW/<module>.shadow`,
  matching signatures exactly." These reference the reviewed shadow.

`ultra-writing-plans` emits both bands, with the shadow band first and
the real-code band explicitly citing `SHADOW/<module>.shadow` as the
source-of-truth for signatures.

## Adopted from Pattern A: `context()` convention

`adifyr/shadow-code`'s `context("path1", "path2")` header is retained for
ultra-skills shadow files. Each `.shadow` file starts with:

```
context(
  "../../INTERFACE.md",
  "../sibling-node/INTERFACE.md",
  "./OTHER_MODULE.shadow"
)
```

This lets `ultra-shadow-review` resolve cross-references deterministically
and lets downstream real-code-gen know exactly which planning artifacts
are in-scope.

---

## Summary table

| Skill | When it runs | Cost | Output |
|---|---|---|---|
| `ultra-shadow-code` | Phase 5.5, per leaf | Medium (LLM gen) | `SHADOW/` |
| `ultra-shadow-review` | After shadow-code, per leaf | Low (short input) | `SHADOW_REVIEW.md` |
| `ultra-shadow-drift` | Post-implementation, on demand | Low-Medium | `SHADOW_DRIFT.md` |

**Recommended first cut:** build `ultra-shadow-code` + `ultra-shadow-review`
together as a pair. They validate each other and produce the review-pass
gate that makes shadow-code pay for itself. `ultra-shadow-drift` can follow
after we have real shadow-reviewed outputs in the wild to calibrate against.

See also:
- `LIFECYCLE.md` — what happens to shadow over a project's lifetime.
- `FORMAT_COMPARISON.md` — which shadow format to pick + example.
