# Ultra-Skills: Design

**Purpose:** A skill suite for **hierarchical, multi-document planning** of systems too large for a single spec or plan. Extends (not replaces) the `superpowers` skill set.

**Core insight:** `superpowers:brainstorming` and `superpowers:writing-plans` are single-topic, single-doc skills. They explicitly punt on "break this into sub-projects" — but give you no machinery for managing the resulting tree. Ultra-skills is that machinery.

---

## Scope

**Ultra-skills handles:**
- Projects that need 10-30+ planning documents
- Recursive decomposition with interface contracts between nodes
- Cross-document consistency (naming, types, interfaces) at scale
- Multi-session planning with checkpointed state
- Background research loops feeding into the plan
- Aggressive YAGNI / scope-pruning as a recurring discipline
- Accumulated user-interview queue (not one question at a time)
- Design artifacts: diagrams, SVGs, mockups, demos

**Ultra-skills does NOT handle:**
- Single-feature planning (use `superpowers:brainstorming` + `superpowers:writing-plans`)
- Execution (use `superpowers:subagent-driven-development` or `executing-plans`)
- Code review (use `superpowers:requesting-code-review`)

**Relationship to superpowers:** Ultra-skills is a LAYER ABOVE superpowers. It composes and dispatches into superpowers skills for leaf-node work. It does NOT fork superpowers.

---

## Deployment Model

Each skill lives at `ultra-skills/ultra-<name>/SKILL.md`, with optional supporting files in the same directory.

Users symlink individual skills into their agent harness:

```bash
ln -s $(pwd)/ultra-skills/ultra-planner ~/.claude/skills/ultra-planner
ln -s $(pwd)/ultra-skills/ultra-planner ~/.agents/skills/ultra-planner
```

The repo is not itself a Claude plugin; skills are standalone. Invocation is by bare name: `ultra-planner`, not `ultra:ultra-planner`.

---

## Plan Tree: Directory Model

When the user runs ultra-planner on a project, it creates:

```
docs/ultra-plans/<project-slug>/
├── ROOT.md                  # tree structure + status dashboard
├── SESSION.md               # current session state, last/next action
├── INTERVIEW_QUEUE.md       # open questions for the user, priority-ranked
├── RESEARCH_LOG.md          # background research findings, chronological
├── DECISIONS.md             # architectural decision log (ADR-style)
├── PRODUCT_GOALS.md         # why we are building this; success criteria
├── nodes/
│   ├── 01-auth/
│   │   ├── SPEC.md          # what this component does, user-facing
│   │   ├── INTERFACE.md     # contracts: what it exposes, what it depends on
│   │   ├── PLAN.md          # implementation plan (leaf nodes only)
│   │   ├── NOTES.md         # working notes, scratch
│   │   └── 01-session/      # child node
│   │       ├── SPEC.md
│   │       ├── INTERFACE.md
│   │       └── PLAN.md
│   └── 02-ingest/
│       └── ...
└── artifacts/
    ├── diagrams/
    ├── mockups/
    └── demos/
```

**Node IDs** are hierarchical slashed paths: `01-auth`, `01-auth/01-session`. Numeric prefixes give stable ordering; slugs give human readability.

**Leaf vs. interior nodes:**
- Interior nodes (have children): SPEC + INTERFACE + NOTES. No PLAN.
- Leaf nodes (terminal): SPEC + INTERFACE + PLAN + NOTES.

**Rule:** If a node gets too big for a single PLAN.md (>~15 tasks, or multiple clearly-separate concerns), decompose it. Decomposition is a first-class operation, not a last resort.

---

## Session State Model

`SESSION.md` is the cross-session brain:

```markdown
# Session State

**Project:** <slug>
**Current phase:** decomposition | research | review | interview | pruning | handoff
**Last action:** YYYY-MM-DD HH:MM — <what happened>
**Next planned action:** <what comes next>

## Open threads
- Research: <topic> (subagent dispatched YYYY-MM-DD)
- Review: tree-consistency pass scheduled after node 02-ingest complete
- Interview: 4 questions queued (see INTERVIEW_QUEUE.md)

## Recent checkpoints
- YYYY-MM-DD: Tree v3 — added node 03-billing, pruned 01-auth/03-sso
- YYYY-MM-DD: Tree v2 — ...
```

The ultra-planner reads SESSION.md on every invocation. It's the "where were we?" file.

---

## Interview Queue Model

Traditional brainstorming asks one question at a time. Ultra asks **many questions, accumulates them, and surfaces batches at natural checkpoints**.

`INTERVIEW_QUEUE.md`:
```markdown
# Interview Queue

## P0 (blocks current work)
- [ ] Auth: Do we need SSO in v1? (Affects 01-auth tree size)

## P1 (needed soon)
- [ ] Ingest: Max expected throughput? (sizes 02-ingest architecture)
- [ ] Billing: Do we bill usage-based or seat-based?

## P2 (can defer)
- [ ] UI: Light/dark mode priority?

## Answered (archive)
- [x] 2026-04-05 — Language: Python 3.12. Reason: team familiarity.
```

Ultra-planner surfaces P0 questions proactively. P1 at phase boundaries. P2 when idle.

---

## Review Cadence

Three review types, triggered at different moments:

### Node review
**When:** A node's SPEC or PLAN is newly written/updated.
**Checks:** Completeness, no placeholders, internal consistency, aligns with parent.
**Who:** Single subagent, fast.

### Interface review
**When:** Two or more sibling nodes have INTERFACE.md. When a shared contract changes.
**Checks:** Do the interfaces fit? Name drift? Type mismatches? Dependency cycles?
**Who:** Single subagent, given the sibling INTERFACEs as input.

### Tree review
**When:** Major milestones. Before user review. On demand. After scope-pruning passes.
**Checks:** Does the tree as a whole satisfy PRODUCT_GOALS.md? Redundancy to prune? Missing coverage? Architectural coherence?
**Who:** Subagent with read access to full tree, returns structured findings.

Reviews write findings to `REVIEW_<YYYY-MM-DD>_<type>.md` at the tree level, not inline. Findings become interview queue items or decomposition tasks.

---

## Skill Catalog

| Skill | Role | Status |
|---|---|---|
| `ultra-planner` | Orchestrator. Entry point. Manages tree & session state. | MVP target |
| `ultra-plan-from-seed` | Bootstraps a plan tree from a single-file seed plan (Claude/Codex output, hand-written markdown); hands off to ultra-planner at Phase 2 or Phase 3. | done (MVP) pending GREEN |
| `ultra-decomposing` | Recursive breakdown with interface contracts. | done (MVP) |
| `ultra-plan-research` | Parallel research dispatch + synthesis into RESEARCH_LOG. | done (MVP) |
| `ultra-cross-doc-review` | Consistency/architecture passes across tree. | done (MVP) |
| `ultra-scope-pruning` | YAGNI loop — challenges every feature, requires justification. | done (MVP) |
| `ultra-interviewing` | Queue management + surfacing protocol. | done (MVP) |
| `ultra-design-artifacts` | Diagrams, SVGs, mockups, demos for iteration. | done (MVP) pending GREEN |
| `ultra-writing-plans` | Hierarchical-aware plan writer (leaf-node PLAN.md). | done (MVP) pending GREEN |
| `ultra-writing-skills` | Ultra's own skill-authoring discipline (for suite self-modification). | done (MVP) |
| `ultra-reviewer` | Meta: reviews ultra-* skills (individually or as a family) against an 11-dimension checklist, triages BLOCKER/MAJOR/MINOR. | done (MVP) pending GREEN |
| `ultra-context-hygiene` | Cross-cutting: context-as-budget discipline referenced by every dispatching skill. | done (MVP) |
| `ultra-yagni` | Cross-cutting: reactive YAGNI lens for flagging speculative scope in in-progress artifacts (tells + tiering + ripple-check). | done (MVP) pending GREEN |
| `ultra-index` | Reference: symptom-to-skill routing guide for the ultra-* suite (inverse of ultra-planner's dispatch table). | done (MVP) pending GREEN |

### Phase 4 — Execution

| Skill | Role | Status |
|---|---|---|
| `ultra-implementing-solo` | Leaf-PLAN.md executor for solo (no-dispatch) environments — Codex, OpenCode. Strict per-task TDD, sibling-contract pinning, disk-backed session state. | done (MVP) pending GREEN |
| `ultra-implementing-team` | Leaf-PLAN.md executor for leader environments with worker dispatch (Claude Code). Leader owns sibling-INTERFACE SHA pinning, cross-node context curation, DIVERGENCE_LOG, 3-tier rollback; workers own single-task implementation under file-ownership discipline. | done (MVP) pending GREEN |

### Shadow-code family (Phase 5.5)

**NOTE:** Shadow-code is a cheap pseudocode architecture spec between PLAN.md and real code. Canonical spec: `ultra-skills/docs/SHADOW_SPEC.md`. TODO (leader): add a `SHADOW/` subdirectory row to the plan-tree directory-model diagram above, reflecting the new leaf-node layout from SHADOW_SPEC.md §1.

| Skill | Role | Status |
|---|---|---|
| `ultra-shadow-code` | Generates planning-shadow for a leaf node (TypeScript-like + ADT). | done (MVP) pending GREEN |
| `ultra-shadow-review` | Architecture review of SHADOW/; emits FREEZE/REVISE/ESCALATE. | done (MVP) pending GREEN |
| `ultra-shadow-drift` | Post-implementation drift check: real code vs. frozen shadow. | done (MVP) pending GREEN |
| `ultra-shadow-regen` | Derives current-shadow from real code on demand; emits SHADOW_DIVERGENCE.md (raw 5-axis deltas, no classification). | done (MVP) pending GREEN |

**Phase 1 (MVP, this repo):** ultra-planner only. Callable as a thin orchestrator that:
1. Recognizes when it applies (user describes a large multi-component system)
2. Sets up the plan tree directory
3. Dispatches to superpowers skills where ultra sub-skills don't exist yet
4. Manages session state

**Phase 2:** Core sub-skills — decomposing, research, cross-doc-review, scope-pruning, interviewing. ultra-planner upgrades to call these instead of superpowers equivalents.

**Phase 3:** Enhancements — artifacts, hierarchical-plan-writer, self-modification discipline.

---

## How the Orchestrator Flows

```
User: "I want to build X" (X = multi-subsystem product)
          ↓
ultra-planner triggers (size heuristics: "multiple subsystems", "platform",
"many components", or user explicit invocation)
          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 0: Bootstrap                                      │
│  • Create docs/ultra-plans/<slug>/                      │
│  • Write PRODUCT_GOALS.md (via interview)               │
│  • Seed SESSION.md, INTERVIEW_QUEUE.md                  │
└─────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Top-level decomposition                        │
│  • Identify top-level subsystems                        │
│  • Create nodes/NN-<slug>/ for each                     │
│  • Write rough SPEC + INTERFACE for each                │
│  • Tree review                                          │
└─────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 2: Per-node refinement (iterative, possibly       │
│ parallel for independent nodes)                         │
│  • Tighten SPEC via interviewing                        │
│  • Research open questions (background dispatch)        │
│  • Recursively decompose if too large                   │
│  • Node review + interface review with siblings         │
└─────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 3: Scope pruning                                  │
│  • Walk tree, challenge each feature                    │
│  • Propose cuts; require justification to keep          │
│  • Tree review                                          │
└─────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Artifact generation                            │
│  • Architecture diagram from INTERFACE files            │
│  • Component diagrams                                   │
│  • Demo/mockup for UI-bearing nodes                     │
└─────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 5: Leaf-node plan writing                         │
│  • For each leaf: write PLAN.md (TDD tasks)             │
│  • Plans hand off to superpowers:subagent-driven-       │
│    development for execution                            │
└─────────────────────────────────────────────────────────┘
          ↓
Handoff: user reviews tree, chooses execution approach.
Implementation is OUT OF SCOPE for ultra-skills.
```

Phases are **not strictly sequential** — the orchestrator revisits earlier phases as new information arrives. Session state tracks where we are.

---

## TDD for Skills (required by writing-skills)

Every ultra skill needs a pressure scenario + baseline test BEFORE the skill is written. See `ultra-skills/docs/BUILD_PLAN.md` for per-skill scenarios.

The suite-level baseline scenario for ultra-planner:

> **Scenario:** Give Claude a prompt like *"I want to build a team collaboration platform with chat, file storage, calendar, billing, and admin dashboards. Help me plan it."* without ultra-planner loaded.
>
> **Expected baseline (failing) behavior:** Claude invokes `superpowers:brainstorming`, asks one question at a time, eventually either (a) produces a single sprawling spec, or (b) decomposes and then loses cross-cutting consistency, or (c) gets stuck in the brainstorming loop asking questions about each subsystem without structural progress.
>
> **Expected GREEN behavior with ultra-planner:** Claude creates `docs/ultra-plans/team-platform/`, writes PRODUCT_GOALS.md, decomposes into 4-5 top-level nodes with INTERFACE contracts, maintains SESSION.md, defers specific sub-system design to iterative refinement with checkpoints.

---

## Open Questions (will become interview items as we build)

1. **Subagent dispatch mechanism:** Claude Code Task tool vs. the superpowers subagent-via-bash approach. Likely: Task tool when available, bash fallback documented.
2. **Token budget:** Orchestrator skills can balloon. Target <300 words for each ultra SKILL.md.
3. **Multi-agent support:** Do we care about Gemini CLI / Codex compatibility Day 1, or Claude Code only?
4. **Self-improvement loop:** Should ultra-planner track its own failure modes and suggest skill updates?

---

## Non-Goals

- Not a replacement for project management tools (Linear, Jira)
- Not a runtime state manager for running systems
- Not a codegen pipeline
- Not a general "agent framework"

It is: **a filesystem-backed planning discipline, surfaced as composable skills.**
