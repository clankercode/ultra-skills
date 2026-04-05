---
name: ultra-yagni
description: Use when reviewing an in-progress SPEC/PLAN/research/skill draft for speculative scope, when noticing plurality/abstraction/future-proofing language ("multi-X", "pluggable", "future-proofs for") in drafts, when invoked as a quality gate during decomposing / plan-research / writing-plans / cross-doc-review, or when an artifact's infra weight feels out of proportion to its stakes. NOT for generating alternative v1 scopes (use ultra-scope-pruning) and NOT for cutting tasks inside a single leaf plan.
---

# ultra-yagni

## Overview

Cross-cutting LENS for flagging speculative scope inside in-progress planning artifacts. Pairs with `ultra-context-hygiene` as a fellow pattern-skill. Invoked from inside other phases — does NOT run standalone and does NOT propose alternative scopes.

**Core principle:** Default verdict is "speculative." An item stays only if tied to a named anchor (PRODUCT_GOALS / SPEC) or to a hidden upstream requirement. Sequence: check upstream → walk tells → tier → ripple.

## When to Use (vs ultra-scope-pruning)

| You have... | Use |
|---|---|
| In-progress artifact (SPEC / PLAN / research / skill draft) to review | **ultra-yagni** (reactive lens) |
| Plurality / abstraction / future-proofing language in a draft | **ultra-yagni** |
| Infra-weight vs stakes mismatch (Kafka for a 5-person cron) | **ultra-yagni** |
| Bag of features needing ≥2 alternative v1 scopes | **ultra-scope-pruning** (forward procedure) |
| User asks "what should we cut?" across the whole tree | **ultra-scope-pruning** |
| Initial scope from scratch, no features drafted | superpowers:brainstorming |
| Tasks inside one leaf PLAN.md | handle inline |

**scope-pruning generates alternatives; yagni only flags.** Run yagni first; feed flags into scope-pruning if tree-wide reshape is still needed.

## The Tells (detection checklist)

Walk these against every artifact. A match is a candidate flag — it triggers the lens procedure.

1. **Speculative plurality.** "multi-X", "per-Y", "tenants", "targets" — pluralized nouns whose anchor is singular (SPEC says "one channel" → "channel targets" is a tell).
2. **Abstraction with a single concrete case.** `FooRegistry`, `NotificationChannel` interface, pluggable adapters, strategy patterns — with exactly one implementation.
3. **Infra weight vs stakes mismatch.** Redis / Kafka / DLQ / Prometheus / 5-attempt backoff on a low-stakes low-volume path. Heavy infra for a daily cron.
4. **Self-admitting future-proofing language.** "future-proofs for…", "to support later analytics", "so we can add Teams later" — the SPEC confessing.
5. **Storage / history without a named consumer.** 90-day retention, event logs, audit tables with no current query or user story touching them.
6. **Edge-case handling for scenarios the anchor excludes.** DM fallback for archived channel on a 5-person team; multi-timezone on a one-team one-TZ deployment.

## Lens Procedure

1. **Upstream-context gate (do not skip).** Open `ROOT.md`, `PRODUCT_GOALS.md`, `DECISIONS.md`. Scan for hidden requirements that would retroactively justify a "speculative" feature (e.g. "org rollout Q3", "tenant isolation is P0", an ADR already deciding on Kafka). Note upstream constraints found. If a file is absent, say so — do not assume.
2. **Walk the tells.** For each artifact section, match against the 6 tells. Each match → candidate flag with the tell named.
3. **Tier each flag.** **BLOCKER** (breaks budget / timeline / stated v1 constraint), **MAJOR** (whole subsystem or infra dependency with no anchor tie), **MINOR** (small future-proofing, cheap to remove later). Flat lists diffuse reader attention — always tier.
4. **Ripple-check per flag.** Name which OTHER nodes / INTERFACE files touch this item. If cutting it orphans a sibling (cut Kafka in node A but node B's INTERFACE consumes a Kafka topic), record the ripple. Unresolved ripples either justify the item or become their own flag.
5. **Emit flags, grouped by tier.** One line each: `[TIER] <artifact>§<section>: <tell> — <rationale citing anchor> — ripple: <list or none>`. Do NOT propose alternative scopes; hand off to `ultra-scope-pruning` for tree-wide reshape.

## Red Flags — STOP and self-correct

- Flagging before reading ROOT / PRODUCT_GOALS / DECISIONS — you will flag load-bearing features
- Flat flag list with no BLOCKER / MAJOR / MINOR tiers
- Flags with no ripple-check — cuts silently orphan siblings
- Proposing replacement features or alternative v1 scopes (that's ultra-scope-pruning)
- "Looks speculative, cut it" without naming which of the 6 tells matched
- Rationale not citing the anchor or an upstream constraint
- Treating the user's chat message as the anchor — the anchor lives in PRODUCT_GOALS / SPEC
- Running as a standalone phase — ultra-yagni is invoked from inside another phase

## Common Mistakes

- **Skipping the upstream-context gate.** Flagging "multi-tenant caching" without checking if PRODUCT_GOALS names org rollout. Upstream first, always.
- **Flat severity.** Treating a `NotificationChannel` interface and Prometheus metrics as equal weight.
- **Node-local review.** Flagging per-artifact without ripple-check. Cuts cascade.
- **Scope-pruning drift.** Drafting alternative v1 bundles — stop, that is `ultra-scope-pruning`.
- **Anchor amnesia.** Rationalizing by reviewer intuition ("feels over-built") instead of the stated anchor. If the anchor is hand-wavy, that itself is the flag — queue to INTERVIEW_QUEUE.md as P0.

## Call-me-from

Invoke ultra-yagni as a lens pass from:
- `ultra-decomposing` — after drafting a new child SPEC
- `ultra-plan-research` — on research synthesis before writing to RESEARCH_LOG.md
- `ultra-writing-plans` — on draft PLAN.md before finalizing tasks
- `ultra-cross-doc-review` — as one review dimension across the tree
- `ultra-writing-skills` — on SKILL.md drafts that list capabilities/options
