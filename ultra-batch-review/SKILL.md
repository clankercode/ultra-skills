---
name: ultra-batch-review
description: Use when a codebase or plan tree needs a comprehensive multi-scope review campaign. Heavyweight - requires user consent before dispatch. NOT for single-pass inline review, reviewing one ultra-* SKILL.md (use ultra-reviewer), cross-doc plan-tree coherence (use ultra-cross-doc-review), or shadow-code review (use ultra-shadow-review).
---

# ultra-batch-review

## Overview

Orchestrates a batched, multi-scope review campaign against a codebase or plan tree. Creates a hierarchical review tree under reviews/batchN/, dispatches parallel review subagents per scope, synthesizes cross-scope interaction findings bottom-up, aggregates findings into a deduplicated fix register, plans fix rounds via conflict-graph coloring, and iterates fix-dispatch + verification until clean.

**Core principle:** A review that doesn't check interactions between components misses the bugs that actually ship. Each parent scope gets two reviews: REVIEW.md (own files) and SYNTHESIS.md (cross-child interactions - contract mismatches, duplicated logic, cascading errors). Neither alone is sufficient.

**Weight warning:** This skill is heavyweight. It creates many subagents, writes extensive state files, and consumes significant wall-clock time. It is NOT a replacement for lightweight inline reviews or the focused review skills (ultra-reviewer, ultra-cross-doc-review, ultra-shadow-review). Use it when the target is large enough to warrant a full campaign and the user has explicitly consented to the cost.

**REQUIRED BACKGROUND:** Load ultra-context-hygiene and ultra-code-standards via the Skill tool. This skill dispatches many subagents and processes large amounts of review output - context hygiene is load-bearing.

## When to Use

| Signal | Use? |
|---|---|
| Codebase needs comprehensive review (components + flows + system) | Yes |
| Multiple reviewers should work in parallel on different scopes | Yes |
| Need iterative fix rounds with deduplication and state tracking | Yes |
| Review target has hierarchical structure (modules to submodules) | Yes |
| Quick inline review of one file or small module | No - review inline |
| Reviewing one or more ultra-* SKILL.md files | No - ultra-reviewer |
| Cross-doc plan-tree coherence check | No - ultra-cross-doc-review |
| Shadow-code artifact review before freeze | No - ultra-shadow-review |
| Routine post-implementation sanity check | No - use lighter review |

## Directory Structure

reviews/batchN/ contains: scopes.md (scope registry), fixes.md (fix register), SUMMARY.md (final verdict), and scopes/ (per-scope directories). Each scope directory contains SCOPE.md and REVIEW.md. Parent scopes additionally contain SYNTHESIS.md.

Scope IDs use the format rv-NN (e.g., rv-01, rv-02). Directories are scopes/rv-01/, scopes/rv-02/, etc. SCOPE.md headers include a Label field for human readability (e.g., "Label: auth") but the directory and cross-references use the short rv-NN form.

Leaf scopes have no SYNTHESIS.md - their REVIEW.md is complete. Parent scopes produce both REVIEW.md (own files) and SYNTHESIS.md (cross-child interactions). Complete review for any node = REVIEW.md + SYNTHESIS.md (if present).

Example: a codebase with auth, api, and db modules might produce scopes rv-01 (auth), rv-02 (api), rv-03 (db) as leaves, rv-04 (dataflow api-to-db, children: rv-02, rv-03), rv-05 (conceptual error-handling, children: rv-01, rv-02, rv-03), rv-06 (system, children: rv-01 through rv-05).

## Procedure

Operate against target root. Each invocation advances one phase. State files carry a Phase: header so re-invocation picks up where the last session left off. Do not skip or reorder phases.

### Phase 1 - Scope Planning

1. **Walk the target codebase.** Identify review scopes at four levels:
   - **Component scopes** - one per module/directory with independent responsibility
   - **Data-flow scopes** - one per significant data path (A to B to C)
   - **Conceptual-group scopes** - cross-cutting concerns (error handling, auth patterns, config, logging)
   - **System scope** - whole-system integration (entry points, config bootstrap, deployment, cross-module wiring)

2. **Build scope hierarchy.** Group child scopes under parent conceptual scopes. A data-flow scope that spans two component scopes is a child of both. The system scope is always the root. Record dependencies: which scopes must be reviewed before others (leaf components first, flows that depend on them next, system last).

3. **Write state files.** Create reviews/batchN/ (increment N if prior batch exists). Write scopes.md with every scope as a table row: id, type, paths, parent, deps, status (planned), review-output. Write per-scope directory scopes/rv-NN/ with SCOPE.md containing: paths covered, entry points, dependency scopes, and a tailored review prompt.

4. **Get user consent.** *(LEADER-ONLY)* Present the scope plan: number of scopes, estimated subagent count, expected wall-clock time. Wait for explicit approval before dispatching reviews. Do not auto-proceed - this is a heavyweight operation.

### Phase 2 - Review Dispatch

5. **Dispatch leaf review subagents.** *(LEADER-ONLY)* For each leaf scope with status: planned, spawn a review subagent. Each subagent gets: its SCOPE.md, relevant source file paths, and instruction to write REVIEW.md with BLOCKER/MAJOR/MINOR triage, file:line citations, and proposed fixes. Output path: reviews/batchN/scopes/rv-NN/REVIEW.md.

6. **Collect leaf reviews.** Read every completed REVIEW.md. Update scopes.md status to reviewed per scope. If any subagent failed or produced empty output, log as finding, mark scope incomplete, continue.

### Phase 3 - Bottom-Up Synthesis

7. **Walk the scope tree bottom-up.** For each parent scope (flows before conceptual, conceptual before system):
   - **a.** Write REVIEW.md covering the parent's own files not covered by children (integration glue, config wiring, shared utilities).
   - **b.** Read all children's REVIEW.md and SYNTHESIS.md files. Write SYNTHESIS.md identifying:
     - Contract mismatches between sibling scopes (type A exported here, type B consumed there)
     - Duplicated logic or patterns across siblings
     - Cascading error patterns (child A's bug surfaces as child B's symptom)
     - Missing cross-scope invariants (fields that must agree, ordering guarantees)
   - **c.** Complete review for this node = REVIEW.md + SYNTHESIS.md.

8. **Update scopes.md.** Mark parent scopes reviewed. Record both output files.

### Phase 4 - Aggregation and Fix Register

9. **Aggregate all findings.** Read every REVIEW.md and SYNTHESIS.md across the tree. Merge into fixes.md:
   - **Deduplication:** same file:line + same symptom = merge, keep the finding from the most specific scope as canonical
   - **Cross-cutting:** same conceptual issue surfaced in multiple scopes = single finding marked with all scope IDs
   - **Per finding:** id, severity (BLOCKER/MAJOR/MINOR), scope(s), location (file:line), description, proposed fix, status (open), fix-round (null)

10. **Record aggregation stats.** Write fixes.md header: Phase: fix-planning, Open findings count, BLOCKER/MAJOR/MINOR counts.

### Phase 5 - Fix Round Planning

11. **Build conflict graph.** Nodes = open findings. Edge between two findings if they touch:
    - The same file, OR
    - Files in the same import chain (fixing A might break B's fix), OR
    - The same conceptual module (semantic conflict risk)

12. **Graph-color the conflict graph.** Each color class = one fix round. Round 1 gets the largest possible set of BLOCKERs that don't conflict. Update fixes.md with fix-round assignments. Record round plan: N rounds, findings per round, files touched per round.

### Phase 6 - Fix Dispatch and Verification (iterative)

13. **Dispatch fix subagents for round N.** *(LEADER-ONLY)* Group findings by non-overlapping file sets (guaranteed by graph coloring). Spawn one fix subagent per group. Each subagent gets: findings to fix, source files, and the relevant SCOPE.md + REVIEW.md/SYNTHESIS.md for review context (so the fix agent understands why the reviewer flagged it, not just what was flagged).

14. **Verify fixes.** *(LEADER-ONLY)* Dispatch micro-review subagents on touched files only. Each micro-reviewer checks: did the fix address the finding? Did it introduce regressions? Update fixes.md per finding: verified (resolved), reopened (new finding appended with new ID), or partial (some sub-issues remain).

15. **Iterate or converge.** If reopened or partial findings exist, rebuild conflict graph for remaining findings, plan next round (back to step 11). If all findings verified or only MINORs remain, proceed to Phase 7.

### Phase 7 - Summary

16. **Write SUMMARY.md.** Include: total scopes reviewed, findings by severity (before/after fix rounds), fix rounds executed, remaining open issues, and verdict. Verdict options:
    - CLEAN - zero open findings
    - ACCEPTABLE - only MINORs remain, none safety-critical
    - NEEDS-ATTENTION - MAJOR+ findings remain unresolved

17. **Update state files.** Final scopes.md and fixes.md with all statuses set.

## State File Formats

**scopes.md** header lines: Phase, Generated date, Target. Table columns: id, type, paths, parent, deps, status, review-output. The review-output column lists REVIEW.md (+ SYNTHESIS.md for parent scopes). Example rows:

    rv-01 | component | src/auth/ | - | - | reviewed | scopes/rv-01/REVIEW.md
    rv-04 | dataflow | src/api/, src/db/ | - | rv-02, rv-03 | reviewed | scopes/rv-04/REVIEW.md + SYNTHESIS.md

**fixes.md** header lines: Phase, Last completed round, Next round, Open/BLOCKER/MAJOR/MINOR counts. Table columns: id, severity, scope(s), location, description, proposed fix, status, fix-round. Status values: open, fixing, verified, reopened, partial. Example rows:

    fx-001 | BLOCKER | rv-02 | src/api/handler.ts:42 | Unvalidated user input | Add zod schema | open | 1
    fx-002 | MAJOR | rv-02, rv-04 | auth/types.ts:12, api/types.ts:8 | UserSession vs Session mismatch | Unify to UserSession | open | 1

**SCOPE.md** header lines: Scope (rv-NN), Type (component/dataflow/conceptual/system), Label (human-readable name), Paths (file list), Entry points (function/method names), Depends on (scope IDs), Review prompt (tailored instructions).

**SYNTHESIS.md** header lines: Synthesis (rv-NN), Label, Synthesized from children (scope IDs), Generated date. Body sections: Contract Mismatches, Duplicated Logic, Cascading Patterns, Missing Cross-Scope Invariants. Each item cross-references finding IDs where applicable.

## Red Flags - STOP and self-correct

- Dispatching review subagents before writing SCOPE.md per scope
- Skipping SYNTHESIS.md for parent scopes - interaction bugs are the ones that ship
- Proceeding without user consent after scope planning
- Findings without BLOCKER/MAJOR/MINOR triage
- Fix round with overlapping file sets (conflict graph prevents this - build it, respect it)
- Skipping verification after fix rounds
- Emitting findings to chat instead of disk-backed fixes.md
- Reviewing a scope from memory without opening the actual source files
- Emitting CLEAN verdict with open BLOCKER or MAJOR findings
- Re-running the full campaign instead of resuming from the Phase: header in state files
- Marking a finding verified without dispatching a micro-review subagent

## Common Mistakes

- **Flat review instinct:** doing one pass over the whole codebase. Component-level and system-level reviews catch different bug classes; both are needed. SYNTHESIS.md catches what neither catches alone.
- **Skipping synthesis:** reviewing each module in isolation and calling it done. Contract mismatches, duplicated logic, and cascading failures live in the seams between modules. SYNTHESIS.md is where those bugs are caught.
- **Fix-round collisions:** dispatching two fix agents that touch the same file. The conflict graph prevents this. If you skip graph coloring, you will create race conditions.
- **Verification skip:** assuming fixes work because the fix agent said so. Micro-review of touched files catches regressions and incomplete fixes that the fix agent's "looks good" misses.
- **State amnesia:** not updating scopes.md and fixes.md after each phase. These files are the resume point. A session crash mid-campaign should lose zero state.
- **Heavyweight overuse:** running a full campaign for a 3-file module. This skill is for codebases large enough to warrant parallel review. Use inline review for small targets.
- **Context-free fix agents:** passing fix agents only the finding row without the SCOPE.md and REVIEW.md context. Fix agents that understand why the reviewer flagged something write better fixes than agents that see only what was flagged.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
