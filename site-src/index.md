# ultra-skills

A skill suite for **hierarchical, multi-document planning** of systems too large for a single spec or plan. Extends (does not replace) the `superpowers` skill set.

## Why ultra-skills?

`superpowers:brainstorming` and `superpowers:writing-plans` are single-topic, single-doc skills. They intentionally exclude decomposition ("break this into sub-projects") but give you no machinery for managing the resulting tree. **ultra-skills *is* that machinery.**

## Skills

| Skill | What it does |
|---|---|
| `ultra-planner` | Hierarchical plan tree for large multi-subsystem projects |
| `ultra-plan-from-seed` | Convert a seed doc into an ultra plan tree bootstrap |
| `ultra-decomposing` | Split a plan-tree node into independent sub-nodes |
| `ultra-plan-research` | Research tech/library questions without burning main context |
| `ultra-cross-doc-review` | Cross-document coherence check across a plan tree |
| `ultra-scope-pruning` | Cut bloated scope down to a shippable v1 |
| `ultra-interviewing` | Queue and batch user questions at natural checkpoints |
| `ultra-design-artifacts` | Generate visual architecture artifacts from INTERFACE.md files |
| `ultra-writing-plans` | Write a leaf-node PLAN.md respecting cross-node contracts |
| `ultra-writing-skills` | Author or edit ultra-* skill files |
| `ultra-reviewer` | Review and audit ultra-* skills for quality and consistency |
| `ultra-yagni` | Prune speculative scope from drafts and plans |
| `ultra-index` | Symptom-to-skill routing guide for the ultra-* suite |
| `ultra-implementing-solo` | Execute a leaf PLAN.md without subagent dispatch |
| `ultra-implementing-team` | Execute a leaf PLAN.md with coordinated subagent workers |
| `ultra-test-driven-development` | RED→GREEN→REFACTOR TDD cycle for implementation tasks |
| `ultra-writing-tests` | Test-craft guidance for writing good test code |
| `ultra-code-standards` | LOC limits, naming, and quality bar for production code |
| `ultra-context-hygiene` | Manage context when processing large files or datasets |
| `ultra-shadow-code` | Generate typed pseudocode shadow before writing real code |
| `ultra-shadow-review` | Review a shadow artifact before freezing for real-code handoff |
| `ultra-shadow-drift` | Audit drift between frozen shadow and real code |
| `ultra-shadow-regen` | Derive a fresh current-shadow from existing real code |
| `ultra-goal-loop` | Adaptively iterate toward acceptance criteria |
| `ultra-batch-review` | Multi-scope parallel review campaign for large codebases |

## Getting Started

New to ultra-skills? Here's the typical flow:

1. Run `ultra-planner` to scaffold a hierarchical plan tree for your project.
2. Use `ultra-decomposing` to split large interior nodes into independent sub-nodes with interface contracts.
3. Run `ultra-scope-pruning` and `ultra-cross-doc-review` to tighten the tree before writing leaf plans.
4. Write each leaf node's PLAN.md with `ultra-writing-plans`.
5. Implement solo with `ultra-implementing-solo` (no subagents) or with workers via `ultra-implementing-team`.
6. Use `ultra-index` at any point if you're unsure which skill to reach for.

## Directory Convention

Each skill is a directory named `ultra-<slug>/` containing at minimum `SKILL.md`. Extra supporting files (scripts, templates, reference docs) live alongside.

```
ultra-skills/
├── README.md
├── docs/
│   ├── DESIGN.md
│   └── BUILD_PLAN.md
└── ultra-<name>/
    ├── SKILL.md
    └── templates/     ← supporting files live here
```

## Installing

Each skill directory is symlink-ready. Run the installer for your harness:

```bash
./install-symlinks-claude.py     # -> ~/.claude/skills
./install-symlinks-codex.py      # -> ~/.agents/skills
./install-symlinks-opencode.py   # -> ~/.config/opencode/skills
```

Each script is idempotent (safe to re-run) and will update stale symlinks in place.

## Contributing

1. Follow `ultra-writing-skills` discipline.
2. Name the skill `ultra-<verb-ing>` or `ultra-<noun>`.
3. Document its pressure scenario in `docs/BUILD_PLAN.md` before writing the body.
4. Update the skills table in README and site-src/index.md.
5. Run the baseline-then-verification cycle.

## Non-Goals

- Not a Claude plugin (standalone skills).
- Not a replacement for superpowers — a layer above it.
- Deliberately stops at planning handoff — use `superpowers:executing-plans` for execution.
