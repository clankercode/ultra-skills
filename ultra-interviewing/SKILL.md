---
name: ultra-interviewing
description: Use when planning has accumulated 3+ open user questions that need structured queueing, prioritization, and batched surfacing at natural checkpoints (not blocking on each question individually), when ultra-planner dispatches the interview phase, or when decisions are stalling because questions pile up unasked. NOT for single clarifying questions mid-conversation — just ask inline.
---

# ultra-interviewing

## Overview

Manages the user-question backlog for a plan tree. Persists to `INTERVIEW_QUEUE.md`, triages into P0/P1/P2, attaches a default to every non-P0 item, and surfaces questions in topic-grouped, row-pickable batches at planner checkpoints. Called by `ultra-planner` when 3+ open items accumulate or at phase boundaries.

**Core principle:** Defaults-and-flag, not open questions. Every queued item above P0 ships with a default the planner is already using; the user changes a row only if they disagree. Every batch names what is NOT being asked now and which defaults are in force.

## When to Use

| Signal | Use? |
|---|---|
| INTERVIEW_QUEUE.md has 3+ open items | Yes |
| ultra-planner hits a checkpoint (phase end, tree review, 3+ P0) | Yes |
| New ambiguities appended during decompose/research/prune | Yes |
| Single inline clarification needed to continue one action | No — just ask |
| Blocking P0 that stops all progress | Ask inline AND log in queue |
| User asked "where are we?" | Dispatch ultra-planner status, then this skill |

## Procedure

1. **Read `INTERVIEW_QUEUE.md`.** If missing, create it with the format below. Load all open items.

2. **Ingest new questions.** For each question from the dispatcher (or discovered in SESSION.md / NOTES.md), check for dedup by semantic match against open items. Duplicate → update the existing row (bump `last_seen`, merge context). Novel → append with a fresh `id`.

3. **Triage each new/updated item** with written reasoning in `rationale`:
   - **P0** = blocks current phase or a structural decision (tree shape, core contract, scope boundary). Surface now.
   - **P1** = affects an upcoming phase or a reversible-but-costly choice. Surface at next phase boundary.
   - **P2** = cosmetic or easily revisited. Surface when idle or bundled.

4. **Attach a default to every P1/P2 item** (and P0 where defensible). The default is what the planner will do absent input. If no default is defensible, re-triage as P0.

5. **Group by topic.** Cluster open items by subsystem / decision-area. Within each cluster, order by priority then age.

6. **Select batch by cadence:** all P0s now; P1 at phase boundaries; P2 only when batch is small (<5) or user idle. Cap batch at ~7 items; overflow → defer list.

7. **Compose surfacing message as tables, one per cluster.** Columns: `id | question | default | change?`. User edits `change?` (or replies by id) only where they disagree. Below the tables add two mandatory sections:
   - **Deferred this round:** ids + one-line reason + priority.
   - **Defaults in force:** every default currently driving planner decisions (including ones not surfaced this round).

8. **Update queue after response.** Answered items → move to `## Resolved` with answer + DECISIONS.md ref. Unanswered → bump `last_surfaced`, keep open. Answers spawning new questions → append as children with `parent_id` set.

9. **Update SESSION.md** with batch surfaced, answers received, defaults locked in, next checkpoint.

## Queue Format

`INTERVIEW_QUEUE.md` is a single markdown file with a table per section:

```
## Open

| id | priority | phase | topic | question | default | rationale | created | last_surfaced | parent_id |
|----|----------|-------|-------|----------|---------|-----------|---------|---------------|-----------|
| Q014 | P0 | decompose | auth | SSO required at launch? | no, email+password v1 | blocks auth node shape | 2026-04-03 | 2026-04-05 | — |

## Resolved

| id | answered | answer | decision_ref |
|----|----------|--------|--------------|
| Q007 | 2026-04-04 | Postgres | DECISIONS.md#adr-003 |
```

Ids are monotonic (`Q001`, `Q002`, ...). Never reuse or renumber.

## Red Flags — STOP and self-correct

- Asking questions without reading INTERVIEW_QUEUE.md first
- Surfacing one question at a time when 3+ are open
- A P1 or P2 item without a default attached
- Surfacing batch without a "Deferred this round" section
- Surfacing batch without a "Defaults in force" section
- Same question appearing twice under different ids (missed dedup)
- Open flat list with no topic grouping when 5+ items queued
- Items aging past two checkpoints without being surfaced or re-triaged
- Answers received but queue file not updated before moving on

## Common Mistakes

- **Open-question posture:** "which database?" instead of "default: Postgres — change if you disagree." Forces user to design; defeats defaults-and-flag.
- **Hidden defaults:** planner uses defaults without listing them. User cannot challenge what they cannot see. Always emit "Defaults in force."
- **Priority inflation:** marking everything P0. P0 is reserved for items blocking the current phase.
- **Queue-dumping:** surfacing the full backlog every checkpoint. Cadence exists — respect it.
- **Orphan resolutions:** answers captured in chat but never written to INTERVIEW_QUEUE.md or DECISIONS.md.
- **Exact-string dedup:** "which DB?" and "pick a datastore" are the same item — merge semantically.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps. Red Flags and Common Mistakes are living documents.*\n'
```
