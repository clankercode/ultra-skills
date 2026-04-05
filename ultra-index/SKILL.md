---
name: ultra-index
description: Use when uncertain which ultra-* skill applies to a planning situation, when you need a symptom-to-skill routing guide, when onboarding a new agent or human reviewer to the ultra-skills suite, when surveying the available skills before starting a planning session, or when a planner dispatch has no obvious match and you want the full menu. NOT a replacement for ultra-planner's dispatch table (which is phase-driven) and NOT a procedure — this is a lookup aid.
---

# ultra-index

## Overview

Symptom-to-skill routing guide for the ultra-skills suite. When an agent or reviewer feels a planning pain point but is uncertain which ultra-* skill addresses it, this index maps the situation to the right skill. It is the inverse of `ultra-planner`'s dispatch table: that table maps planner phases to skills; this one maps symptoms, triggers, and artifacts-in-hand to skills. Read it, find the matching row, then invoke the skill via the Skill tool.

**Core principle:** The suite is large enough that ad-hoc recall misses skills. A structured lookup beats "what was that one skill about pruning?" every time.

## How to use this index

1. Scan the quick-route table first — most situations match one row directly.
2. If no row matches, skim the catalog grouped by phase.
3. If you are layering discipline onto an in-progress phase, check cross-cutting lenses.
4. If modifying the suite itself, check meta skills.
5. For multi-step flows, see common chains.

## Quick-route table

| Symptom / Situation | Skill | Phase |
|---|---|---|
| Starting a multi-subsystem / platform / product plan from scratch | `ultra-planner` | Bootstrap |
| Seeding a plan tree from an existing single-file markdown plan (Claude/Codex output, hand-written architecture doc) | `ultra-plan-from-seed` | Bootstrap |
| Need to break an oversized node into child nodes with contracts | `ultra-decomposing` | Decompose |
| Parent SPEC has 6+ responsibilities or expected >15 leaf tasks | `ultra-decomposing` | Decompose |
| Need to compare 2+ tech/library/service candidates with citations | `ultra-plan-research` | Research |
| Research question would burn main-session context if answered inline | `ultra-plan-research` | Research |
| Plan tree has 5+ nodes, need cross-doc coherence check | `ultra-cross-doc-review` | Review |
| INTERFACE drift / naming drift / suspected cycle across nodes | `ultra-cross-doc-review` | Review |
| 15+ candidate features for v1, need to cut scope with anchor discipline | `ultra-scope-pruning` | Prune |
| User says "this feels bloated" / "help me cut scope" | `ultra-scope-pruning` | Prune |
| Speculative plurality, single-case abstraction, or future-proofing language in a draft | `ultra-yagni` | Cross-cutting lens |
| Infra weight feels out of proportion to stakes (Kafka for a cron) | `ultra-yagni` | Cross-cutting lens |
| About to implement a feature / bugfix; need the RED-GREEN-REFACTOR cycle and Iron Law | `ultra-test-driven-development` | Cross-cutting lens |
| Tempted to write code before the test, or a test passed on first run | `ultra-test-driven-development` | Cross-cutting lens |
| 3+ open user questions piling up, need batched surfacing | `ultra-interviewing` | Interview |
| Need to queue an ambiguity instead of asking inline | `ultra-interviewing` | Interview |
| INTERFACE.md files stable, need diagrams / mockups / demos | `ultra-design-artifacts` | Artifacts |
| Writing a leaf-node PLAN.md with sibling contract dependencies | `ultra-writing-plans` | Plan |
| Writing a RED test / contract smoke test / extending a test file — behavior-not-mocks, deterministic time, flow-vs-narrow, helper extraction, tiering | `ultra-writing-tests` | Craft / cross-cutting lens |
| Test passes but doesn't assert on SPEC behavior (test-complicity) / mock-call-count assertions / timing budgets 100x too loose | `ultra-writing-tests` | Craft / cross-cutting lens |
| File >1MB, same dataset queried 2+ times, or 3+ data-passing steps | `ultra-context-hygiene` | Cross-cutting lens |
| Creating or editing an ultra-* SKILL.md | `ultra-writing-skills` | Meta |
| Reviewing a new or shipped ultra-* skill against the 11-dimension checklist | `ultra-reviewer` | Meta |
| Uncertain which skill to use / onboarding to the suite | `ultra-index` | Reference |

## Skill catalog (by phase)

**Bootstrap / Orchestration**
- `ultra-planner` — Entry point for multi-subsystem plans. Maintains the plan tree, SESSION.md, phase dispatching.
- `ultra-plan-from-seed` — Alternative entry point. Converts a single-file seed plan into a tree bootstrap (PRODUCT_GOALS, node SPEC/INTERFACE stubs, DECISIONS, INTERVIEW_QUEUE, artifacts/ORIGIN.md), then hands off to ultra-planner at Phase 2 (refinement) or Phase 3 (scope-pruning).

**Decompose**
- `ultra-decomposing` — Splits oversized nodes into children with coverage matrix, non-overlap assertion, and DAG validation.

**Research**
- `ultra-plan-research` — Dispatches a research subagent with citations; writes to RESEARCH_LOG.md; recommends with "when to pick X" framing.

**Review**
- `ultra-cross-doc-review` — 8-dimension checklist across the plan tree; emits BLOCKER/MAJOR/MINOR findings + patches.

**Prune**
- `ultra-scope-pruning` — Anchor-driven YAGNI pass across the feature set; produces ≥2 alternative v1 scopes; ADRs for cuts.

**Interview**
- `ultra-interviewing` — Queue management, triage, default-attached batched surfacing at checkpoints.

**Artifacts**
- `ultra-design-artifacts` — Architecture diagram, dependency DAG, type matrix, sequence diagrams, UI mockups from stable INTERFACE.md.

**Plan**
- `ultra-writing-plans` — Leaf-node PLAN.md writer with parent-coverage scan, cross-node type survey, contract smoke tests per consumer.

**Meta (suite self-modification)**
- `ultra-writing-skills` — TDD-for-skills authoring, orchestration pressure scenarios, ecosystem registration.
- `ultra-reviewer` — 11-dimension review of ultra-* skill(s) with BLOCKER/MAJOR/MINOR triage.
- `ultra-index` — This skill. Symptom-to-skill routing guide.

**Cross-cutting lenses (layered onto other phases)**
- `ultra-context-hygiene` — Context-as-budget; delegate branching work; use narrow tools; persist to disk.
- `ultra-yagni` — Reactive speculative-scope flagger with 6 tells + BLOCKER/MAJOR/MINOR tiering + ripple-check.
- `ultra-test-driven-development` — RED-GREEN-REFACTOR discipline, Iron Law, rationalizations table, fast-test preference. Grounds `ultra-implementing-solo` / `ultra-implementing-team` and the task structure `ultra-writing-plans` emits.
- `ultra-writing-tests` — Test-craft companion to `ultra-test-driven-development`: WHAT makes a good test (behavior-not-mocks, deterministic time, flow-vs-narrow, contract smoke tests, helper extraction, tiering, test-complicity guard). Loaded by workers at RED-test-writing time.

## Cross-cutting lenses: when and how

**ultra-context-hygiene** — layer on when ANY phase involves: reading files you haven't sized, running 3+ data-passing steps inline, re-parsing the same file, or reaching for Bash+pipe when Grep's `count`/`head_limit` would do. Invoke proactively at the start of dispatching phases (research, review) and before any big-file read.

**ultra-yagni** — layer on INSIDE decomposing, plan-research, writing-plans, cross-doc-review, and writing-skills after a draft exists but before it ships. It does not run standalone. Its output is flags, not alternative scopes — hand flags to `ultra-scope-pruning` if tree-wide reshape follows.

**ultra-writing-tests** — load at RED-test-writing time under `ultra-implementing-solo` / `ultra-implementing-team` (per-task TDD execution), or when adding a contract smoke test per sibling consumer (per `ultra-writing-plans`). Covers test-craft that `ultra-test-driven-development` deliberately punts on: fast-test targets + context-dependent caveats, behavior-not-mocks, flow-vs-narrow, fake timers, helper extraction, tiering, test-complicity guard. Pair with `ultra-test-driven-development` (WHEN/HOW) for full coverage.

## Meta skills: when the suite modifies itself

**ultra-writing-skills** — any new or edited `ultra-<name>/SKILL.md`. Invoke before drafting; it carries the RED/GREEN discipline and ecosystem-update checklist.

**ultra-reviewer** — before shipping a new ultra-* skill, when a family of 2+ skills lands together, or for periodic audit. It loads calibration skills and walks a fixed 11-dimension checklist. Pairs with `ultra-cross-doc-review` (which reviews plan trees rather than skills).

## Common chains

1. **plan-from-seed → cross-doc-review → scope-prune (if scope-tiered) → decompose** — bootstrap a tree from prose, check coherence, prune tiers, decompose fat nodes.
2. **decompose → cross-doc-review → scope-prune → interview** — grow the tree, check coherence, cut scope, queue residual ambiguities.
3. **plan-research → cross-doc-review → writing-plans** — research commits a tech choice, review confirms contracts still fit, leaf plan cites the INTERFACE paths.
4. **writing-skills → reviewer → ecosystem updates** — draft with RED/GREEN, review against 11 dimensions, update DESIGN.md + README + planner dispatch table in the same commit.
5. **decompose → yagni lens → cross-doc-review** — flag speculative plurality and infra weight in new SPEC/INTERFACE before the tree-review pass runs.

## Reference

- `ultra-skills/docs/DESIGN.md` — full architecture, plan-tree model, phase flow, review cadence.
- `ultra-planner/SKILL.md` — dispatch table (phase → skill), the forward-direction counterpart to this index.
- `ultra-skills/README.md` — status table for each skill (MVP / pending GREEN / done).

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps. Red Flags and Common Mistakes are living documents.*\n'
```
