---
name: ultra-code-standards
description: Use when writing or reviewing production code in any context — implementation tasks, reviews, refactoring, or ad-hoc coding. Defines LOC limits, duplication rules, naming, separation of concerns, and quality bar. Load this skill whenever code quality standards should be enforced.
---

# ultra-code-standards

## Overview

Non-negotiable code quality standards for all production code. These apply during implementation (GREEN and REFACTOR phases), during reviews, and when fixing review findings. Every agent writing or reviewing code should load this skill.

**Core principle:** Concrete, checkable rules — not vague aspirations. "No file over 1,000 LOC" not "keep files small."

## Standards

### LOC Limits

- **Soft limit: 1,000 lines** per file. Breach → refactor before committing (extract module, split file).
- **Hard limit: 2,000 lines** per file. Breach → STOP, refactor is mandatory before proceeding. Review FAILS on hard-limit breach, no exceptions.
- **Measurement:** production code lines excluding imports/comments. Use `wc -l` as a fast proxy; if borderline, count manually.

### No Duplicated Code

- If you write logic that already exists elsewhere in the codebase, extract to a shared module.
- Second occurrence of similar logic → extract immediately. Don't wait for a third.
- Reviewers: check for cross-task and cross-file duplication that the implementer may not see.

### Proactive Refactoring

- When a task touches messy code (unclear names, tangled responsibilities, missing abstractions), improve it in the REFACTOR phase.
- Do not leave code worse than you found it.
- Do not refactor files you are not touching for the current task — scope discipline applies.
- When refactoring, stay green on every edit. Never refactor under red.

### Clean Separation of Concerns

- One module, one responsibility.
- If a file handles parsing AND validation AND persistence, split it.
- Each file should have a well-defined interface — other modules interact through that interface, not through internals.

### Meaningful Names

- Variables, functions, types, files — all should describe what they represent, not how they work.
- No single-letter names outside loop indices.
- No abbreviations that require domain knowledge to decode.

### Best Practices

- Consistent error handling patterns within a codebase. No swallowed exceptions.
- No magic numbers — extract named constants.
- No hardcoded secrets or credentials.
- No TODO without an issue reference.
- Follow existing patterns in the codebase. Improve code you're touching; don't restructure code outside your task.

## LOC Check (mechanical)

After every GREEN phase, before committing:

1. Check the line count of every file you modified or created.
2. If any exceeds 1,000 lines → refactor in the REFACTOR phase (extract module, split responsibilities).
3. If any exceeds 2,000 lines → mandatory split before commit. Do not proceed.

## For Reviewers

When reviewing code against these standards, check:

- [ ] No file exceeds 2,000 LOC (hard fail)
- [ ] Files over 1,000 LOC are flagged for extraction
- [ ] No duplicated logic across files
- [ ] Each file has one clear responsibility
- [ ] Names are meaningful and consistent
- [ ] Error handling follows codebase patterns
- [ ] No magic numbers, hardcoded secrets, or bare TODOs

Report violations with file:line references and severity (Critical for hard-limit breach or security; Important for soft-limit breach, duplication, naming; Minor for style).

## When to Use

| Signal | Use? |
|---|---|
| Writing production code (any context) | Yes |
| Reviewing code (spec-compliance or quality) | Yes |
| Refactoring existing code | Yes |
| Worker subagent implementing a task | Yes — load this skill |
| Writing tests only (no production code) | No — test files are exempt from LOC limits |
| Planning / spec / design work | No |

## Integration

- **`ultra-implementing-solo`** — references this skill; solo agents self-enforce during REFACTOR and self-review.
- **`ultra-implementing-team`** — leader includes this skill in worker briefs; reviewers check against it.
- **`superpowers:subagent-driven-development`** — code-quality reviewer should load this skill.
- **Ad-hoc use** — any agent can load this skill when writing or reviewing code outside the ultra-planner flow.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
