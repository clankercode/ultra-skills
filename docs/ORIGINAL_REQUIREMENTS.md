# ultra-skills: Original Requirements (verbatim from user)

Captured 2026-04-05 to preserve pre-build context across potential conversation compaction.

## How this started

User asked whether existing planning skills could handle a project that would need 10-30 planning documents. They then described what they needed, verbatim:

> "i'm looking for something that works heirarchically/recursively, makes good use of agent teams and subagnets, performs competent research, does review rounds to ensure the plan is consistent and the architecture is good and meets product goals, integrates all reasonable manner of testing optimized for speed and correctness, proactively refactors things to simplify architecture and program logic, quesitons if we need certian features to cut fat and simplify the design, handles complex multi iteration planning sessions, activley interviews the user about all manner of things they might want input on, can produce nice specs, diagrams, demo sites, svgs, etc to iterate with the user on the design before implementation, proactively researches things in the bg and suggests new ideas that surface, and so on."
>
> "Is it possible we might need to write a new skill to handle projects of this size with this level of planning?"

## Decomposed feature list (from the above)

1. **Hierarchical / recursive** structure for plans
2. **Agent teams / subagents** for parallelism and context isolation
3. **Competent research** (not ad-hoc)
4. **Review rounds** for consistency, architecture, product-goal alignment
5. **Testing integrated** into planning, optimized for speed + correctness
6. **Proactive refactoring / simplification** of architecture & program logic
7. **Active YAGNI** — question each feature, cut fat
8. **Multi-iteration / multi-session** planning support
9. **Active user interviewing** — surface all inputs user should weigh in on
10. **Design artifacts** — specs, diagrams, demo sites, SVGs for user iteration
11. **Background research** with proactive idea-surfacing

## Gap analysis agreed upon

- `superpowers:brainstorming` = single-topic Q&A, one spec output
- `superpowers:writing-plans` = flat, single-doc, single-subsystem plans
- Neither handles hierarchical multi-doc trees, cross-doc consistency, or multi-session state

Conclusion: new skill suite needed. User approved the sketch ("that sounds good").

## Tracked mapping to planned skills

| Feature from wishlist | Skill handling it |
|---|---|
| Hierarchical / recursive | `ultra-planner` + `ultra-decomposing` |
| Agent teams / subagents | `ultra-plan-research`, `ultra-cross-doc-review` (dispatched work) |
| Competent research | `ultra-plan-research` |
| Review rounds | `ultra-cross-doc-review` |
| Testing integrated | (deferred — part of leaf plans via `ultra-writing-plans`) |
| Proactive refactoring | `ultra-scope-pruning` + tree review |
| Active YAGNI | `ultra-scope-pruning` |
| Multi-iteration / multi-session | `ultra-planner` session state discipline |
| Active user interviewing | `ultra-interviewing` |
| Design artifacts | `ultra-design-artifacts` |
| Background research | `ultra-plan-research` (background dispatch) |

## Project pipeline stated by user

Projects queued to get the ultra-planner treatment BEFORE user begins implementation:

1. **recent-code-auditor-proxy** (`~/src/recent-code-auditor-proxy/`) — smaller, tactical tool. Used as first dogfood target (this session).
2. **ARGUS** (codename for `~/src/agentic-peer-review-repo/` — see `TEST_PLAN_FOR_SKILL_TESTING_1.md`) — the big decentralized code-audit platform.
3. **meta-agent** (`~/src/meta-agent/`) — early stage, "not sure how much is there yet."

User stated: *"argus and meta-agent are both going to get the ultra-planner treatment before I move to implementation (once we're completely done with skills design)."*

recent-code-auditor-proxy was chosen as the first dogfood because meta-agent is too early-stage, and recent-code-auditor-proxy naturally becomes a first-party review agent for the eventual ARGUS network.
