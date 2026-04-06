---
name: ultra-plan-research
description: Use when planning surfaces a technology comparison, library/framework selection, API exploration, pattern lookup, or constraint-satisfaction question that would burn main-session context if answered inline, or when ultra-planner's research phase dispatches this skill. NOT for factual recall the leader already holds with high confidence and NOT for questions where the answer is already in the plan tree's DECISIONS.md.
---

# ultra-plan-research

## Overview

Answers a bounded research question with cited findings, a candidate evaluation matrix, and a "when to pick X" recommendation, written as a structured entry in `RESEARCH_LOG.md`. Called by `ultra-planner` during the research phase; keeps main-session context clean by dispatching a subagent with fresh WebSearch/WebFetch calls rather than relying on training memory.

**Core principle:** Answering from training knowledge is a red flag, not a shortcut. Every candidate claim needs a dated citation. Tools, versions, maintenance status, and known issues all drift; a research entry without fetched sources is a guess dressed as a finding.

## When to Use

| Signal | Use? |
|---|---|
| Tech/library/service comparison with 2+ candidates | Yes |
| Constraint-satisfaction question ("which X supports Y at Z scale?") | Yes |
| API/protocol/pattern exploration outside leader's confident knowledge | Yes |
| ultra-planner dispatches research phase | Yes |
| Answer already recorded in DECISIONS.md or RESEARCH_LOG.md | No — cite existing entry |
| Trivial factual recall leader is sure of | No — note inline, move on |
| Question blocks on user preference, not facts | No — route to ultra-interviewing |
| Feasibility concern — requirement looks impossible or technically infeasible | Yes — investigate with evidence before concluding |

## Procedure

Operate on plan tree root `docs/ultra-plans/<project>/`. Append to `RESEARCH_LOG.md`.

**Leader-only steps:** 3 requires dispatching a subagent — only the main session can do this. If invoked as a subagent, complete steps 1-2 and 5-7 using your own WebSearch/WebFetch, then return. If scope is truly too small for delegation (1 candidate, 1 claim), state that and proceed inline.

1. **Extract the research question + hard constraints.** From planning context, write a single-sentence question and an enumerated constraint list (throughput, latency, ordering, retention, licensing, ops burden, runtime, language, budget). Separate **hard** constraints (must satisfy) from **soft** (preferred). If constraints are vague, append a P0 item to `INTERVIEW_QUEUE.md` and stop.

2. **Identify the candidate set.** List every plausible candidate (3-7 typical). Include at least one incumbent/default and one outlier. Drop candidates that fail a hard constraint on face value; record the drop reason.

3. **Dispatch research subagent.** *(LEADER-ONLY)* Brief the subagent with: the question, the hard + soft constraint list, the candidate set, and the output contract (step 4). Subagent MUST use WebSearch or WebFetch for each candidate — no answering from training memory. Outputs land under `/tmp/ultra-research-<slug>/` and are summarized into the log entry.

4. **Research subagent brief (output contract).** For each candidate, fetch and record: current stable version + release date, maintenance signal (last release, active maintainers, CVEs), 1-2 production users at target scale, known issues/footguns, licensing, and per-constraint verdict (meets / partial / fails / unknown). Every claim carries an inline citation (URL + fetch date). No bare assertions.

5. **Synthesize the matrix.** Rows = candidates, columns = hard constraints + 2-3 soft. Cells = verdict + one-line evidence. Candidates failing any hard constraint are struck through, not deleted — the reader needs to see they were considered.

6. **Recommend with "when to pick X" framing.** For each surviving candidate, write one paragraph: what it optimizes for, which constraint profile it wins, what it costs. End with a primary recommendation tied to THIS plan's constraint weighting, and name the tripwire that would flip the recommendation.

7. **Write the RESEARCH_LOG.md entry and link it.** Append the entry (format below). Add a back-link from the SPEC.md of every node whose decision depends on this finding. If the recommendation implies an architectural commitment, append a draft ADR stub to `DECISIONS.md`. Surface open questions from step 4's "unknown" cells into `INTERVIEW_QUEUE.md`.

## RESEARCH_LOG.md Entry Format

```
## RQ-NN: <one-line question>  (YYYY-MM-DD)

**Context:** <node(s) this informs>
**Hard constraints:** <bulleted list>
**Soft constraints:** <bulleted list>
**Candidates considered:** <list, with dropped + reason>

**Findings:**
- <candidate>: <version, date> — <per-constraint verdict> [src: <url>, fetched YYYY-MM-DD]
- ...

**Matrix:** <inline table: candidates x constraints>

**Recommendation:** <pick> — when to pick each alt: <short "when to pick X" lines>
**Tripwire:** <what flips the recommendation>
**Open questions:** <forwarded to INTERVIEW_QUEUE.md items QQ-N>
```

## Red Flags — STOP and self-correct

- Writing findings without any WebSearch/WebFetch calls in this session
- "From my training" or undated claims about versions, maintainers, or scale
- Candidate claims with no URL citation
- Skipping constraint extraction and jumping to candidates
- Recommendation without per-candidate "when to pick X" framing
- RESEARCH_LOG.md entry written but no back-link from dependent SPEC.md
- Hard-constraint failures hidden instead of struck through in the matrix
- Leader ran the research inline when scope clearly warranted a subagent

## Common Mistakes

- **Training-memory research:** producing a polished comparison with zero tool calls. Looks authoritative, ages like milk. Always fetch.
- **Candidate-first, constraint-later:** listing tools you already know, then retrofitting constraints. Extract constraints first, then let them narrow the field.
- **Winner-only writeup:** describing only the recommended option. The log needs to show what was rejected and why, so later readers can re-evaluate when constraints change.
- **Citation theater:** linking a vendor homepage as "source" for a scale claim. Cite the specific doc page, changelog, or post-mortem that carries the claim.
- **Orphan entry:** RESEARCH_LOG.md grows but no SPEC.md or DECISIONS.md links back — the finding is invisible to the nodes that need it.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
