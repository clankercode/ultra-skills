# Shadow-Code Lifecycle: What Happens After Real Code Exists

**Research question:** Once real code is generated from a reviewed shadow,
what is the shadow for? Does it stay? Does it retire? Who keeps it in
sync? When does it become stale overhead?

This document evaluates the options and recommends a default policy for
ultra-skills.

---

## The core tension

Shadow is cheap to **generate** (15-25% of real-code tokens). It is also
cheap to **regenerate** from real code, given a capable LLM. But keeping
it **manually in sync** with code is expensive and error-prone — the
classic comment-drift / doc-rot failure mode that plagues every secondary
artifact from Javadocs to design docs. (See
[Software rot (Wikipedia)](https://en.wikipedia.org/wiki/Software_rot),
which notes in its "Active rot" section that "adding new features may be
prioritized over updating documentation; without documentation, however,
it is possible for specific knowledge pertaining to parts of the program
to be lost.")

Addy Osmani's
[How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/)
frames specs as "version-controlled documentation" that must be updated
as decisions emerge — an explicitly *living* treatment. Spec-kit-sync
([bgervin/spec-kit-sync](https://github.com/bgervin/spec-kit-sync))
exists precisely because spec drift vs. implementation is considered a
hidden-but-high-cost problem once LLM workflows introduce specs. The
classical ADR world handles the same problem by marking superseded ADRs
as deprecated rather than editing them
([adr.github.io](https://adr.github.io/), and the "Deprecated by YYY /
Supersedes XXX" convention in
[joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record)).

Two opposing intuitions:

1. **Shadow-first-then-retired:** shadow is scaffolding. Once real code
   exists and passes drift-check once, the shadow has paid for itself.
   Archive and walk away.
2. **Shadow-forever-as-living-spec:** shadow is the architecture spec.
   It should outlive any particular implementation and serve as the
   canonical design artifact.

Neither extreme is right for every node. The recommendation is
**phase-based with per-node declaration**.

---

## Staleness signals

Signals that a shadow has become stale overhead rather than an asset:

1. **Every real-code change forces a manual shadow update.** If touching
   `foo.ts` reliably requires touching `foo.shadow`, the shadow is
   redundant — either merge the information into code comments or
   retire the shadow.
2. **Reviewer ignores it.** If the shadow is never opened during code
   review, it has lost its signalling value.
3. **Drift-check blocked on shadow being out of date.** If
   `ultra-shadow-drift` reports "shadow outdated" more than half the
   time without the user caring, the shadow is overhead.
4. **Two competing sources of truth.** If a contributor asks "which is
   right, the shadow or the code?" and the answer is "code," the shadow
   is no longer authoritative.
5. **Shadow regeneration from code is cheaper than maintenance.** If
   the team routinely deletes and re-derives the shadow from code when
   they want to consult it, the shadow should move to on-demand mode.

Signals that a shadow is still earning its place:

1. **New contributors read it first.** It is the fastest path to
   architectural understanding.
2. **Drift-check catches real bugs.** Code changes that violated the
   architecture were caught because the shadow called them out.
3. **Cross-module review needs it.** Reviewers use the shadow to reason
   about module-to-module contracts without loading all the code.
4. **Design discussions cite it.** DECISIONS.md entries reference
   shadow files.

---

## Lifecycle patterns

### Pattern L1: shadow-first-then-retired

Shadow exists during the planning→implementation transition. After
real code passes drift-check once, shadow is moved to
`nodes/<node>/SHADOW_ARCHIVED/` with a timestamp. Not deleted — kept as
a historical record of "what we thought we were building." Not updated.

**Pros:** zero maintenance burden. Shadow cost is bounded and front-loaded.
**Cons:** architecture intent is no longer queryable after the fact.
**Best for:** leaf nodes with stable, unsurprising responsibilities —
CRUD endpoints, thin adapters, utility libraries.

### Pattern L2: shadow-as-living-spec

Shadow is updated alongside every non-trivial real-code change. Treated
as source-of-truth for architecture; code conforms to shadow. Drift-check
runs in CI.

**Pros:** architecture stays legible, drift bugs caught early.
**Cons:** high maintenance burden. Doubles change-review cost. Dies the
first time a deadline pushes someone to skip shadow updates. This is the
classic comment-drift failure mode.
**Best for:** rarely. Only stable subsystems with infrequent, deliberate
architecture changes AND a team committed to the discipline. Even then,
a single "shadow-update-debt" sprint-end catch-up is a smell.

### Pattern L3: shadow-regenerable-on-demand (RECOMMENDED DEFAULT)

Shadow is NOT manually maintained. When someone needs the shadow view
(onboarding, refactor planning, drift-check), they regenerate it from
real code via `ultra-shadow-regen` (proposed 4th skill; see below).
The stored `SHADOW/` dir reflects the **last planning-phase shadow**,
and is never edited after Phase 5.5 gate passes. A regenerated shadow
is a new, timestamped derivation.

This treats shadow as **two distinct artifacts that share a format**:
- **Planning-shadow:** frozen at Phase 5.5 gate. Historical record of
  "what we designed." Lives in `SHADOW/`.
- **Current-shadow:** derived from code on demand. Lives in
  `.ultra-cache/shadow-regen/<timestamp>/` (gitignored).

**Pros:** zero ongoing maintenance burden. Shadow always accurate when
consulted because it is freshly derived. Planning-shadow remains as
design intent record. LLM regeneration cost is low.
**Cons:** current-shadow is never exactly equal to planning-shadow —
drift is implicit in regeneration. You can diff them to recover drift
info, but the act of consulting is no longer free.
**Best for:** most leaf nodes. The default.

### Pattern L4: shadow-graduation

At some agreed milestone (code review pass, v1.0, prod deploy), the
leaf's shadow is "graduated" to documentation-only status. It stops
being drift-checked; it becomes reference material, marked
`STATUS: graduated` at the top. Follow-up changes may or may not update
it — the team declares either way.

**Pros:** explicit transition point. Honest about the shadow's changing
role.
**Cons:** requires discipline to actually mark graduation. Another
state to track.
**Best for:** nodes that go through a clear maturity milestone (MVP →
production). Especially useful when the planning-phase shadow captures
a design that's unlikely to change much.

---

## Counter-pattern: "shadow forever is actually fine"

Claim: shadow is cheap AND LLM-regenerable, so why not keep it forever
and regenerate automatically on every commit?

This collapses to Pattern L3. "Shadow forever" is fine if "forever"
means "always freshly derivable," not "always hand-maintained."
The failure mode is specifically manual sync.

One caveat: **planning-shadow has information current-shadow cannot
recover**. Planning-shadow includes:
- Design alternatives that were considered and rejected
- Error paths that were specified but not exercised
- Cross-module intent that code cannot reveal (e.g., "this module
  exists to isolate DB logic so we can swap Postgres for SQLite later")

Regenerating shadow from code loses all of this. So **planning-shadow
should not be discarded, even if current-shadow is regenerable**.

---

## Proposed 4th skill: `ultra-shadow-regen`

If we adopt Pattern L3 as default, a 4th skill in the family is
warranted:

**`ultra-shadow-regen`** — derive a current-shadow from real code.

- Input: real code directory + (optional) planning-shadow for
  comparison.
- Output: fresh `.shadow` files in a timestamped cache dir, plus a
  `SHADOW_DIVERGENCE.md` report comparing planning-shadow to
  current-shadow. The divergence report is the "drift story" in human
  terms: what the team originally designed vs. what they actually built.
- Does NOT write into `SHADOW/` (that dir is frozen post-Phase-5.5).
- Does NOT run drift-check — that's still `ultra-shadow-drift`'s job.
  `ultra-shadow-drift` can optionally invoke `ultra-shadow-regen` as a
  subroutine.

**Verdict:** yes, propose a 4th skill. Without it, Pattern L3 has no
first-class entry point and users will either re-invoke
`ultra-shadow-code` (wrong — it writes to `SHADOW/`) or hand-craft
shadows (defeats the purpose).

---

## Recommendation for ultra-skills default policy

**Default: Pattern L3 (shadow-regenerable-on-demand) with
Pattern L4 (graduation) as the terminal state.**

Concretely:

1. `ultra-shadow-code` writes `SHADOW/` in Phase 5.5. This is the
   **planning-shadow**, frozen after review passes.
2. `SHADOW/SHADOW_INDEX.md` carries a `STATUS` field:
   - `planning` — freshly written, in Phase 5.5 iteration.
   - `frozen` — Phase 5.5 gate passed, real-code generation started.
     No further manual edits.
   - `graduated` — team declared this leaf stable; shadow is
     documentation, drift-check is informational only.
3. Post-implementation queries use `ultra-shadow-regen` for
   current-shadow, and `ultra-shadow-drift` for drift reports. Neither
   touches the frozen planning-shadow.
4. Per-leaf escape hatch: a leaf's `DECISIONS.md` may declare
   `SHADOW_POLICY: living` to opt into Pattern L2 for that leaf only.
   Reserved for genuinely architecture-stable subsystems where the
   team commits to the maintenance burden. Assume this is rare.

**Retirement milestone:** when a leaf is marked `graduated`, future
drift-checks are advisory. Shadow stays in the repo as historical
design record. No deletion, no archive dance — graduation is a status
change, not a file move.

**Maintenance burden:** near-zero by default. Real-code-edit does NOT
trigger automatic shadow regen. Regen is explicit, on demand, cheap
when invoked.

---

## Sources consulted

- [Software rot — Wikipedia](https://en.wikipedia.org/wiki/Software_rot)
- [How to write a good spec for AI agents — Addy Osmani](https://addyosmani.com/blog/good-spec/)
- [Spec drift: the hidden problem AI can help fix — Kinde](https://www.kinde.com/learn/ai-for-software-engineering/ai-devops/spec-drift-the-hidden-problem-ai-can-help-fix/)
- [bgervin/spec-kit-sync — GitHub](https://github.com/bgervin/spec-kit-sync)
- [Architectural Decision Records (adr.github.io)](https://adr.github.io/)
- [joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record)
- [ADR lifecycle — pogopaule/architecture_decision_record](https://github.com/pogopaule/architecture_decision_record/blob/master/adr_lifecycle.md)
- [Basics of ADR — Medium](https://medium.com/@nolomokgosi/basics-of-architecture-decision-records-adr-e09e00c636c6)
- [Literate Programming — Donald Knuth](https://www-cs-faculty.stanford.edu/~knuth/lp.html)
  — reviewed for the maintainability argument: "for reasons of
  maintainability it is essential that the program description defines
  the actual program text; if this were defined in a separate source
  document, then inconsistencies would be almost impossible to prevent."
  This is evidence *against* Pattern L2 as a default.
- [Literate programming — Wikipedia](https://en.wikipedia.org/wiki/Literate_programming)
