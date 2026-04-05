---
name: ultra-writing-skills
description: Use when creating a new ultra-* skill, editing the body of an existing ultra-* skill, splitting or renaming an ultra-* skill, or when ultra-planner surfaces a phase that has no matching sub-skill yet. NOT for authoring superpowers:* skills (use superpowers:writing-skills directly) and NOT for narrative-only edits to DESIGN.md or BUILD_PLAN.md.
---

# ultra-writing-skills

## Overview

Authors and edits ultra-* skills under TDD-for-skills. Extends `superpowers:writing-skills` with orchestration-specific pressure scenarios, planner dispatch-table fit checks, and the ecosystem updates an ultra skill must land with (catalog, README, BUILD_PLAN, planner dispatch table).

**Core principle:** A new ultra-* skill is a test-driven artifact inside a coupled ecosystem. If you did not watch a subagent fail without it, you cannot know what it should teach. If you did not update the planner dispatch table, catalog, README, and BUILD_PLAN, it is orphaned.

**REQUIRED BACKGROUND:** Invoke `superpowers:writing-skills` and `superpowers:test-driven-development` via the Skill tool at session start. Reading them as reference is insufficient.

## When to Use

| Signal | Use? |
|---|---|
| Creating a new `ultra-<name>/SKILL.md` | Yes |
| Editing any existing ultra-* SKILL.md body | Yes |
| ultra-planner needs a phase-skill that doesn't exist yet | Yes |
| Splitting an ultra skill that grew past ~750 words | Yes |
| Renaming or rescoping an ultra-* skill | Yes |
| Writing a superpowers:* skill (not ultra-*) | No — use `superpowers:writing-skills` directly |
| Editing DESIGN.md / BUILD_PLAN.md narrative only (no skill change) | No |

## Procedure

Operate in order. Do not batch or skip.

**Leader-only steps:** 5, 9, 10 require dispatching subagents — only the main session can do this in Claude Code. If invoked as a subagent, describe the scenarios + expected rationalizations + verification test concretely in BUILD_PLAN.md and defer dispatch back to the leader.

1. **Load required skills.** Invoke `superpowers:writing-skills` and `superpowers:test-driven-development` via the Skill tool. Confirm both loaded.

2. **Verify naming.** Must match `ultra-<verb-ing>` (e.g. `ultra-decomposing`) or `ultra-<noun-phrase>` (e.g. `ultra-planner`). Reject vague nouns and non-ultra prefixes. Record in BUILD_PLAN.md before drafting.

3. **Verify dispatch-table fit.** Open `ultra-planner/SKILL.md`. Identify which phase the new skill serves. If none fits, either rescope or queue a planner update as a P0 interview item and stop.

4. **Design a pressure scenario.** Orchestration skill → must trigger checkpoint surfacing, multi-session resumability, or dispatch decisions. Pattern skill → force recognition under ambiguity. Reference skill → force retrieval + correct application. Document in BUILD_PLAN.md.

5. **Dispatch RED baseline subagent.** *(LEADER-ONLY)* Fresh subagent, scenario, WITHOUT the skill loaded. Never draft SKILL.md before this runs. Outputs → `/tmp/ultra-<name>-red/`.

6. **Analyze baseline.** Document rationalizations, dropped steps, and gaps verbatim in BUILD_PLAN.md. These are the tests the SKILL.md must pass.

7. **Draft minimal SKILL.md** addressing those gaps only. Match `ultra-planner`/`ultra-decomposing` style: Overview, When to Use table, numbered Procedure, Red Flags, Common Mistakes. Target 500-750 words body for orchestrators; <400 for pattern skills. No example code or templates.

8. **Verify CSO compliance.** Description states triggering conditions only — NO workflow summary. Start with "Use when…". Under ~500 chars.

9. **Dispatch GREEN verification subagent.** *(LEADER-ONLY)* Fresh subagent, same scenario, WITH the new SKILL.md loaded as a skill (not read as a file). Outputs → `/tmp/ultra-<name>-green/`.

10. **Refactor loopholes.** *(LEADER-ONLY for re-running GREEN.)* If GREEN surfaces new rationalizations, add explicit counters to Red Flags / Common Mistakes and re-run. Iterate until bulletproof.

11. **Update the ecosystem (all four, same commit):** DESIGN.md catalog row, BUILD_PLAN.md test-results table, README.md status row, and ultra-planner dispatch table if dispatchable.

## Red Flags — STOP and self-correct

- Drafting SKILL.md before RED baseline ran, or shipping because the skill "looks obviously correct" without GREEN
- Testing helper scripts the skill references instead of dispatching a subagent against SKILL.md itself
- Reading superpowers:writing-skills as reference without invoking it via the Skill tool
- Description that summarizes workflow instead of stating triggers
- Name that isn't `ultra-<verb-ing>` or `ultra-<noun-phrase>`
- No matching row in ultra-planner's dispatch table — skill is orphaned
- No update to DESIGN.md catalog, README status table, or BUILD_PLAN test results
- Example code or fill-in-the-blank templates inside the SKILL.md body
- GREEN surfaced a new rationalization and you patched Red Flags without re-running GREEN

## Common Mistakes

- **Skipped RED/GREEN:** writing straight to GREEN or shipping without GREEN because the gap is "obvious." Without the two-sided evidence you do not know which rationalizations agents reach for or whether the SKILL.md closes them.
- **Proxy testing:** verifying scripts/templates the skill references instead of the SKILL.md's teaching applied by a subagent. The SKILL.md is what is under test.
- **Orphan / dispatch mismatch:** skill lands without catalog, README, BUILD_PLAN, or planner updates — or exists with no planner phase invoking it. Rescope or update the planner; do not ship out of sync.
- **Workflow-in-description:** description becomes a shortcut and agents follow it instead of reading the body.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
