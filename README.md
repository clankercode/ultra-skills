# ultra-skills

A skill suite for **hierarchical, multi-document planning** of systems too large for a single spec or plan. Extends (does not replace) the `superpowers` skill set.

**Problem it solves:** `superpowers:brainstorming` and `superpowers:writing-plans` are single-topic, single-doc skills. They explicitly punt on decomposition ("break this into sub-projects") but give you no machinery for managing the resulting tree. ultra-skills *is* that machinery.

## Status

**Phase 1 (MVP):** `ultra-planner` only, as a thin orchestrator that calls into superpowers fallbacks where ultra-* sub-skills don't yet exist.

**Phase 2/3:** Sub-skills stubbed. They document intent + pressure scenarios but have no body yet.

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

## Key Docs

- `docs/DESIGN.md` — architecture, plan-tree model, review cadence, rationale
- `docs/BUILD_PLAN.md` — skill build order, per-skill TDD pressure scenarios
- `docs/SHADOW_SPEC.md` — canonical shadow-code format + lifecycle spec (link from project rules files)

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

## Installing (Symlinking into Agent Harnesses)

Each skill directory is symlink-ready. Run the installer for your harness — they are idempotent (safe to re-run) and will update stale symlinks in place:

```bash
./install-symlinks-claude.py     # -> ~/.claude/skills
./install-symlinks-codex.py      # -> ~/.agents/skills
./install-symlinks-opencode.py   # -> ~/.config/opencode/skills
```

Each script creates the target directory if needed, symlinks every `ultra-*/` subdir, leaves existing correct symlinks alone, updates stale ones, and refuses to touch real directories (prints a suggested-fix instead). Prints a summary and exits 0 on success, 1 on any error.

Skills are invoked by bare name (e.g., `ultra-planner`), not with a plugin prefix.

<details>
<summary>Manual fallback (if you can't run the scripts)</summary>

```bash
# Claude Code
ln -s $(pwd)/ultra-planner ~/.claude/skills/ultra-planner

# Generic agent harness (~/.agents/skills)
ln -s $(pwd)/ultra-planner ~/.agents/skills/ultra-planner
```

Or link all ultra-* skills at once:

```bash
for d in ultra-*/; do
  name="${d%/}"
  ln -s "$(pwd)/$name" "$HOME/.claude/skills/$name"
  ln -s "$(pwd)/$name" "$HOME/.agents/skills/$name"
done
```
</details>

## TDD-for-Skills Status

Per `superpowers:writing-skills`, each skill requires a pressure scenario + baseline subagent run + verification run. Current state:

- Pressure scenarios: **documented** in `docs/BUILD_PLAN.md` for all 9 skills.
- **ultra-planner: RED + GREEN passed.** Baseline (no skill) produced a flat 22-item list with custom file conventions. GREEN (with skill) produced an 8-node hierarchical tree with interface sketch, P0/P1/P2 interview queue, proper SESSION.md state, and checkpoint discipline. No rationalizations surfaced; no refactor required. Full findings in `docs/BUILD_PLAN.md` (pending write-up).
- Phase 2 skills: **not yet tested**. Run baselines when bodies are written.

**When ultra-planner is actually used on a real planning task, treat that usage itself as a live test and record findings against the pressure scenario.**

## Contributing New Ultra Skills

1. Follow `ultra-writing-skills` discipline (falls back to `superpowers:writing-skills` if ultra-writing-skills isn't installed).
2. Name the skill `ultra-<verb-ing>` (e.g., `ultra-decomposing`) or `ultra-<noun>` (e.g., `ultra-planner`).
3. Document its pressure scenario in `docs/BUILD_PLAN.md` before writing the body.
4. Update the status table above.
5. Run the baseline-then-verification cycle.

## Non-Goals

- Not a Claude plugin (standalone skills).
- Not a replacement for superpowers — a layer above it.
- Not an execution framework. Hand off to `superpowers:subagent-driven-development` or `superpowers:executing-plans` at the end of planning.
