---
name: ultra-reviewer
description: Use when an ultra-* skill is about to ship, when a family of ultra-* skills lands together and needs consistency check, when periodically auditing the existing suite for drift, or when onboarding a fresh perspective to the catalog. NOT for reviewing plan trees (use ultra-cross-doc-review) and NOT for reviewing implementation code (use superpowers:requesting-code-review).
---

# ultra-reviewer

## Overview

Reviews one or more ultra-* SKILL.md files against a fixed 11-dimension checklist, emits a REVIEW.md triaged BLOCKER/MAJOR/MINOR, and proposes concrete fixes per finding. Meta-counterpart to `ultra-cross-doc-review`: that skill reviews plan trees, this one reviews the skill suite itself.

**Core principle:** You cannot judge a skill you have not calibrated against. Load the style-setting skills and read at least one shipped ultra-* skill before touching the target. Findings without severity are noise; severity without a proposed fix is debt.

## When to Use

| Signal | Use? |
|---|---|
| A new ultra-* SKILL.md is about to ship | Yes |
| A family of 2+ ultra-* skills landed together | Yes |
| Periodic audit of existing ultra-* suite | Yes |
| Onboarding a fresh reviewer to the catalog | Yes |
| Reviewing a plan tree / INTERFACE.md set | No — use ultra-cross-doc-review |
| Reviewing code | No — use superpowers:requesting-code-review |
| Single typo fix in a shipped SKILL.md | No — inline edit |

## Procedure

Operate in order. Do not skip calibration or the dimension walk.

1. **Load calibration skills via the Skill tool.** Invoke `ultra-writing-skills` (style + TDD-for-skills discipline) and `ultra-cross-doc-review` (triage pattern). Reading them as files is insufficient. Confirm both loaded before drafting anything.

2. **Read a reference ultra-* SKILL.md** from the shipped suite as a calibration anchor. `ultra-planner` for orchestrators, `ultra-decomposing` or `ultra-cross-doc-review` for pattern skills. Note: word count, section names, description style, procedure length. These are your budget anchors.

3. **Read the dispatch table.** Open `ultra-planner/SKILL.md` and record every phase + cross-cutting + meta row verbatim. This is the ecosystem-registration ground truth for step 5, dimension 3 and 8.

4. **Enumerate targets.** List every SKILL.md path under review. Record N. Read each target's full body + frontmatter. **Self-review exemption:** if `ultra-reviewer/SKILL.md` is in the target list, self-skim only (format + ecosystem-registration + naming) and tag its entries `[SELF-SKIM]` in REVIEW.md. Deep review of ultra-reviewer defers to a sibling agent.

5. **Walk the 11-dimension checklist per target.** Examine every dimension in order; do not skip because "it looked clean":

   - **CSO compliance** — description triggers-only, starts with "Use when…", includes NOT-for clauses where applicable, under ~500 chars, no workflow summary.
   - **Naming convention** — matches `ultra-<verb-ing>` or `ultra-<noun-phrase>`. Flag vague nouns or non-ultra prefixes.
   - **Ecosystem registration** — rows exist in DESIGN.md catalog, README status table, and ultra-planner dispatch table (if dispatchable). Half-registered = MAJOR; dispatchable + fully unregistered = BLOCKER.
   - **Word budget** — aspirational 500-900w body, orchestrators and patterns alike. Targets are aspirational per user's word-count memory, not hard cuts. Flag MINOR only at ~1.5x suite median (~1300w), MAJOR only at ~2x median (~1700w). Do NOT flag 600-1100w as over-budget.
   - **Required sections** — Overview, When to Use, one of {`## Procedure` | `## Techniques` | `## Lens Procedure` | `## Steps`}, Red Flags, Common Mistakes. Procedure-equivalent headers accepted for lens/technique-style skills. Missing Red Flags on a failure-prone skill = MAJOR.
   - **Procedure quality** — numbered, actionable, concrete tool/check names (not "validate X" with no how).
   - **LEADER-ONLY markers** — if the skill dispatches subagents or uses leader-only tools (Task, multi-agent Skill invocation), each such step must be tagged `LEADER-ONLY` with subagent-alternative guidance ("if subagent, describe scenario and defer"). Missing marker on a dispatch step = MAJOR.
   - **Overlap with existing ultra-* skills** — two skills claiming the same phase/responsibility = BLOCKER.
   - **Dispatch-table fit** — if dispatchable, a phase row must invoke it. Orphaned dispatchable = BLOCKER.
   - **Family consistency** (2+ targets) — naming axis (no verb-mixing like builder/runner/executor), consistent section names.
   - **Description-style consistency** (2+ targets) — shared "Use when…" opener, trigger-list structure, char-length within ~150-char band. Flag outliers or style drift (imperative vs descriptive, trigger-list vs narrative). MINOR unless it breaks CSO for one skill.

6. **Triage findings.**
   - **BLOCKER** — orphaned dispatchable skill, direct responsibility overlap, non-ultra namespace, missing required section (no Procedure-equivalent at all) on failure-prone skill, naming axis break in a family.
   - **MAJOR** — half-registered, ~2x median word-bloat (~1700w+), missing Red Flags, CSO violation (workflow-in-description), procedure step with no concrete how, missing LEADER-ONLY marker on a dispatch step.
   - **MINOR** — ~1.5x median budget overrun, stylistic drift, description-style outlier, section-name variance within tolerance, thin Common Mistakes.

7. **Write REVIEW.md** to the review output path (default `REVIEW.md` in cwd; leader may specify). Top line: `Reviewed N skills: [list]`. Group findings by severity. Per finding: dimension tag, skill + location, evidence (quoted), proposed fix (concrete edit or ecosystem update).

8. **Summary verdict.** At the end of REVIEW.md: ship / fix-then-ship / do-not-ship, with the 2-3 load-bearing reasons. Leader will act on this.

## Red Flags — STOP and self-correct

- Drafting REVIEW.md before loading `ultra-writing-skills` and `ultra-cross-doc-review` via the Skill tool
- Judging word budget by vibes without reading a shipped ultra-* SKILL.md
- Flagging skills at 600-1100w as over-budget — word targets are aspirational; only flag 1.5x/2x median deviations
- Flagging `## Techniques` or `## Lens Procedure` as a missing-Procedure failure when the skill is a lens-style pattern
- Checking only the target's directory — ecosystem registration requires DESIGN.md + README + ultra-planner
- Findings emitted to chat instead of REVIEW.md on disk
- Severity-free findings, or BLOCKER/MAJOR with no proposed fix
- Skipping a checklist dimension because "nothing looked wrong"
- Missing `Reviewed N skills` assertion at top of REVIEW.md
- Flagging naming drift only for exact duplicates (missing verb-axis breaks like builder/runner/executor)
- Deep-reviewing `ultra-reviewer` from within `ultra-reviewer` — self-skim only, tag `[SELF-SKIM]`, defer to sibling

## Common Mistakes

- **Uncalibrated review:** asserting word budgets and section conventions from first principles. Numbers from vibes get both directions wrong — read a shipped skill first.
- **Ad-hoc dimension walk:** reviewing by "what jumps out." Naming-axis breaks and namespace violations are structural and easy to skim past.
- **Ecosystem blindness:** reading only the SKILL.md body. A skill can look perfect in isolation and still be orphaned from the planner dispatch table.
- **Fix-free findings:** the review owns the proposed fix, not the author.
- **In-chat review:** REVIEW.md on disk is the artifact; without it there is nothing to diff against.
