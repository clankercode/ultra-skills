# ultra-skills

A skill suite for **hierarchical, multi-document planning** of systems too large for a single spec or plan. Extends (does not replace) the `superpowers` skill set.

## Why ultra-skills?

`superpowers:brainstorming` and `superpowers:writing-plans` are single-topic, single-doc skills. They explicitly punt on decomposition ("break this into sub-projects") but give you no machinery for managing the resulting tree. **ultra-skills *is* that machinery.**

## Skill Status

| Skill | Status |
|---|---|
| `ultra-planner` | **MVP verified via TDD baseline (RED → GREEN passed)** |
| `ultra-plan-from-seed` | done (MVP) pending GREEN |
| `ultra-decomposing` | done (MVP) |
| `ultra-plan-research` | done (MVP) |
| `ultra-cross-doc-review` | done (MVP) |
| `ultra-scope-pruning` | done (MVP) |
| `ultra-interviewing` | done (MVP) |
| `ultra-design-artifacts` | done (MVP) pending GREEN |
| `ultra-writing-plans` | done (MVP) pending GREEN |
| `ultra-writing-skills` | done (MVP) |
| `ultra-reviewer` | done (MVP) pending GREEN |
| `ultra-context-hygiene` | done (MVP) |
| `ultra-yagni` | done (MVP) pending GREEN |
| `ultra-test-driven-development` | done (MVP) pending GREEN |
| `ultra-writing-tests` | done (MVP) pending GREEN |
| `ultra-index` | done (MVP) pending GREEN |
| `ultra-implementing-solo` | done (MVP) pending GREEN |
| `ultra-implementing-team` | done (MVP) pending GREEN |
| `ultra-shadow-code` | done (MVP) pending GREEN |
| `ultra-shadow-review` | done (MVP) pending GREEN |
| `ultra-shadow-drift` | done (MVP) pending GREEN |
| `ultra-shadow-regen` | done (MVP) pending GREEN |
| `ultra-goal-loop` | done (MVP) pending GREEN |
| `ultra-batch-review` | done (MVP) pending GREEN |

## Directory Convention

Each skill is a directory named `ultra-<slug>/` containing at minimum `SKILL.md`. Extra supporting files (scripts, templates, reference docs) live alongside.

```
ultra-skills/
├── README.md
├── docs/
│   ├── DESIGN.md
│   └── BUILD_PLAN.md
└── ultra-<name>/
    └── SKILL.md
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
4. Update the status table in README.
5. Run the baseline-then-verification cycle.

## Non-Goals

- Not a Claude plugin (standalone skills).
- Not a replacement for superpowers — a layer above it.
- Not an execution framework. Hand off to `superpowers:subagent-driven-development` or `superpowers:executing-plans` at the end of planning.
