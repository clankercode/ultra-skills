---
name: ultra-context-hygiene
description: Use when processing files >1MB or logs >10k lines, when the same dataset will be queried 2+ times, when 2+ independent scans are queued, when a task branches across parse/filter/correlate steps, when dispatching subagents for multi-step work, or when the main session is accumulating raw data, repeated parses, or inline heredoc scripts. NOT for single reads of known-small files or when the user asks to inspect raw content.
---

# ultra-context-hygiene

## Overview

Teaches main-session agents to treat context as a finite budget and push work outward — to subprocesses, subagents, and disk — so the model reviews summaries, not raw data. Referenced by `ultra-planner`, `ultra-plan-research`, `ultra-cross-doc-review`, and any dispatching orchestrator.

**Core principle:** Context = budget. Every raw byte loaded is spent. Push work to subprocess, subagent, or disk; review the summary.

## When to Use

| Signal | Use? |
|---|---|
| File > 1MB, log > 10k lines, dataset that won't fit comfortably | Yes |
| Same data queried 2+ times | Yes |
| 2+ independent scans/counts/greps queued | Yes |
| Multi-step branching analysis (parse → filter → correlate) | Yes |
| Fetching web content for extraction | Yes |
| Single read of a known-small file | No — just Read it |
| User asks to inspect raw content | No — show it |

## Mental Model

Three places work can happen, ranked by context cost:

1. **Subagent** — fresh window, returns a summary. Cheapest for the leader.
2. **Subprocess / disk** — Bash, script, Grep counts. Results land as short strings.
3. **Main session** — most expensive. Reserve for decisions, not data.

Default: push one level outward from where you instinctively reached.

## Techniques

1. **Delegate multi-step processing to subagents.** Branching logic (parse → filter → correlate → decide) is a clean delegation. Leader reads the report, not intermediates. 3+ data-passing steps → dispatch.

2. **Dedicated tools over Bash one-offs.** Reach for `Grep` (`output_mode: count`/`files_with_matches`, `head_limit`), `Glob`, and `Read` (`offset`/`limit`) BEFORE Bash+pipe chains. Count-mode Grep returns a scalar; `cat | grep | head` returns lines you scroll past.

3. **Batch independent tool calls.** No shared state → one turn, parallel tool uses. Serial independents burn turns and tokens.

4. **Cache and persist state to disk.** Parse once, serialize (JSON, `.cache/`), reuse. Plan trees, NOTES.md, intermediate reports, queues belong on disk, not in context. Re-parsing the same file for query 2 is a stop signal.

5. **Scripts to files, not inline heredocs.** Python past ~15 lines or referenced twice belongs in `scripts/foo.py`. Heredocs bloat every turn they appear in.

6. **Size before you touch, then Read with offset/limit.** `wc -l`/`ls -lh` first — size changes strategy. When the region is known (line from prior Grep), Read with `offset`/`limit`.

7. **Markdown fetchers over raw-HTML.** Raw HTML is 5-20x the token cost.

8. **Name the budget.** Before a big operation state: "this scan stays under 5k tokens." Naming makes it checkable.

9. **Skill loading: tool over @-link.** `@skills/foo/SKILL.md` force-loads every turn. Prefer the Skill tool.

## Quick Reference: task shape → tactic

| Task shape | Tactic |
|---|---|
| "How many X in file?" | Grep `output_mode: count` |
| "Which files contain X?" | Grep `files_with_matches` + `head_limit` |
| Same dataset, 3 queries | Parse once → cache → reuse |
| Parse → filter → join → summarize | Dispatch subagent, review report |
| Known line range in big file | Read with `offset`/`limit` |
| 40-line Python one-off | Write `scripts/foo.py`, invoke by path |

## Red Flags — STOP and self-correct

- Reading a file whose size you haven't checked, or loading raw data "to have a look"
- Inline Python heredocs past ~15 lines, or one growing turn-over-turn
- Re-parsing the same file for query 2 without caching
- N independent tool calls across N turns instead of one parallel batch
- `cat | grep | head` when Grep tool fits
- Multi-step intermediate state held in conversation instead of on disk
- Fetching raw HTML when a markdown fetcher is available
- No budget named before a large operation
- @-linking skills that rarely fire

## Common Mistakes

- **Leader-does-everything:** keeping multi-step processing in-session because "it's only a few steps." Delegate at 3+ data-passing steps.
- **Reflexive Bash:** Bash feels fast but often returns more bytes than Grep/Glob with `count`/`head_limit`. Pick the narrower tool.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps. Red Flags and Common Mistakes are living documents.*\n'
```
