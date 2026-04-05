# Ultra-Skills: Build Plan

**What this is:** The implementation plan for the ultra-skills suite itself. Each ultra-* skill needs to be created with the TDD discipline from `superpowers:writing-skills`: pressure scenario → baseline → minimal skill → refactor.

**Sequencing principle:** Build the **orchestrator MVP first** with minimal sub-skills, then grow sub-skills one at a time, upgrading orchestrator references as they appear.

---

## Skill Build Order

### Phase 1 — MVP (this repo, initial delivery)

#### 1. ultra-planner (orchestrator, MVP)

**Pressure scenario:** User sends: *"Help me plan a team collaboration platform with chat, file storage, calendar, billing, and admin. I want this carefully thought through — lots of components."*

**Baseline expectation (without ultra-planner):** Claude likely invokes `superpowers:brainstorming`, begins single-topic Q&A, either produces a sprawling spec or a shallow decomposition without tracking state or interface contracts. No plan-tree directory. No session checkpoint. No scope-pruning loop.

**GREEN expectation (with ultra-planner):** Claude recognizes trigger, scaffolds `docs/ultra-plans/<slug>/`, writes PRODUCT_GOALS.md via focused interview, produces top-level decomposition with stub INTERFACE contracts, maintains SESSION.md, does not dive into leaf-node detail until tree is stable.

**Skill content (key sections):**
- Description: "Use when planning a multi-subsystem product with 3+ independent components, or when user asks for 'careful' / 'comprehensive' planning of a system. NOT for single-feature planning — use superpowers:brainstorming for that."
- Triggers: explicit invocation, "platform", "multi-subsystem", "many components", user flags "big project"
- Directory scaffold procedure
- Phase flow (bootstrap → decompose → refine → prune → artifacts → leaf-plans → handoff)
- State management: read SESSION.md on every invocation, update after every action
- Dispatches to existing superpowers skills with annotated intent
- Red flags: skipping directory scaffold, losing SESSION.md sync, diving into leaf detail before tree stabilizes

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-planner (GREEN) |
|---|---|---|
| Decomposition shape | Flat list, 22 items | 8-node hierarchical tree |
| File naming | Custom (STATE.md, INDEX.md) | Matches convention (SESSION.md, ROOT.md) |
| Interface contracts | None | Dependency sketch in ROOT.md |
| Question handling | 20 dumped at once, no priority | P0/P1/P2 queue, checkpoint at 5 P0 |
| Research handling | "Future work" | Dispatch route noted in SESSION.md |
| SPECs | N/A (just names in INDEX.md) | Stub SPECs per node (purpose/responsibilities/non-responsibilities) |
| Depth discipline | Would continue drilling | Paused at bootstrap checkpoint |
| Resumability | Custom STATE.md checklist | SESSION.md: phase + last + next + open threads |

**Verdict:** GREEN passed cleanly. No rationalizations surfaced. No loopholes found. No refactor required. Skill is MVP-verified as written.

**Test artifacts:** `/tmp/ultra-baseline/` (RED outputs), `/tmp/ultra-green/` (GREEN outputs) — ephemeral, reproducible from scenario below.

#### Resumption Test (2026-04-05, Test #2)

**Scenario:** Cold-start subagent resumes dogfood planning of `recent-code-auditor-proxy` from on-disk state alone. Input: plan tree at `~/src/recent-code-auditor-proxy/docs/ultra-plans/recent-code-auditor-proxy/` with 04-audit-runner fully refined, 6 other nodes at stub. Task: refine SPECs + draft INTERFACEs for 00/01/02/03/05/06. Rules: no user questions, queue unclear items to INTERVIEW_QUEUE.md.

**Result: PASSED.** Subagent produced 12 files (6 SPECs + 6 INTERFACEs) at equivalent depth to 04 reference. Matched section structure, queued 1 new P1 + 6 new P2 questions, flagged 6 assumptions explicitly.

**Gaps surfaced (patch candidates for ultra-planner or sub-skills):**

1. **No INTERFACE.md rubric.** Subagent had only one reference (04) to infer structure. → Patch: either bake template into ultra-planner procedure, or define in ultra-writing-plans / ultra-cross-doc-review.
2. **ROOT.md dependency sketch was terse.** Forced inference about which nodes depend on which. → Patch: ultra-planner should mandate an explicit dep-graph format (graphviz or ASCII) in ROOT.md template.
3. **No "infrastructure node" concept.** Daemon bootstrap (keys, config init, lifecycle) referenced across nodes but nobody owns it. Same for CLI surface. → Patch: ultra-planner / ultra-decomposing should prompt: "identify infrastructure concerns that cross nodes — assign ownership or create infra node."

**Decision:** Patch these on future dogfood cycles (ARGUS run will surface more). Ship Phase 1 MVP as-is.

---

### Phase 2 — Core sub-skills (follow-up sessions)

#### 2. ultra-decomposing

**When it's needed:** Once ultra-planner has basic orchestration, decomposition logic grows in ultra-planner. Extract to its own skill when the guidance gets too long.

**Pressure scenario:** Claude is given a node SPEC that's too large. Without skill: may produce uneven decomposition, miss interface contracts, duplicate responsibilities across children.

**GREEN:** Identifies independent subsystems, writes INTERFACE contracts between them, flags dependency cycles, validates children collectively cover parent spec.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-decomposing (GREEN) |
|---|---|---|
| Decomposition artifact | 7 child dirs + architecture + interfaces, clean | 8 child dirs + CHILDREN.md matrix + INTERFACES.md + NOTES.md + INTERVIEW_QUEUE updates |
| Coverage matrix | Implicit (inferred from child SPECs) | Explicit table, R → owner, 1 row per responsibility |
| Non-overlap audit | Implicit | Explicit paragraph + 10 pairwise resolutions |
| Public-surface mapping | None | Explicit table, parent-exposed symbol → child |
| Topological order | None (dep graph only) | Topo-sorted build order, 3 levels |
| Acyclicity check | Passed (no cycles) | Caught 4 apparent cycles, resolved via sync-vs-event-bus distinction |
| Rationale | Lived in chat response | Baked into each child SPEC.md |
| Open questions | Presented as settled | 4 P1 + 4 P2 queued to INTERVIEW_QUEUE.md |

**Verdict:** GREEN passed. Skill caught 3 concrete things baseline would have missed: pairwise boundary definitions, sync-vs-event-bus cycle distinction, Slack slash-command ownership ambiguity.

**Refactor candidates (future, not blocking):**

1. **Cross-cutting ownership pattern** — skill doesn't guide when a responsibility (audit, visibility) should be hosted by one child with distributed call-sites vs promoted to infra sibling. Same gap as ultra-planner's "infrastructure node" concept from Test #2.
2. **NOTES.md template** — step 2 says write seams to NOTES.md but no canonical structure. Subagent improvised.
3. **Child INTERFACE.md template** — step 7 says "exposes / depends-on / events" but doesn't reference a canonical rubric. Same gap as Test #2.
4. **Pairwise scan scope** — 28 max pairs for 8 children; "suspicious pairs only" rule would reduce ceremony.

**Decision:** Ship MVP as-is. Patch refactor candidates on ARGUS dogfood cycle.

#### 3. ultra-plan-research

**Pressure scenario:** Planning surfaces a research question (e.g., "which vector DB?"). Without skill: Claude researches inline, consuming main-session context.

**GREEN:** Dispatches focused research subagent (via Task tool), synthesizes findings to RESEARCH_LOG.md with structured format (question / findings / recommendation / citations).

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-plan-research (GREEN) |
|---|---|---|
| Live-source fetches | 0 (training memory only) | 8 (5 WebSearch + 3 WebFetch), every claim URL-cited |
| Candidate survey | 3-paragraph "Kafka probably, maybe Redpanda" | Matrix of 5 candidates, per-candidate findings + citations |
| Rejected candidates | Silently dropped | Kept struck-through with reason (RabbitMQ) |
| Recommendation shape | Single winner, hedged | Primary + "when to pick X" per surviving candidate |
| Tripwire | None | Named condition (latency SLO < 10ms, partitions > 1000) that flips the call |
| Unknown handling | Assumed silently (AWS residency, payload size) | Forwarded to INTERVIEW_QUEUE.md as blocking P0/P1 |
| Output structure | Inline chat paragraph | RESEARCH_LOG.md entry: Context / Hard+Soft constraints / Candidates / Findings / Matrix / Recommendation / Tripwire / Open questions |
| Context cost to main session | Full (inline research) | Delegated — findings synthesized to disk |

**Verdict:** GREEN passed. Skill caught 4 things baseline would have skipped: named tripwire, struck-through rejects kept visible, per-candidate use-profile distinctions, unknowns surfaced as interview items rather than guessed.

**Refactor candidates (future, not blocking):**

1. **Subagent self-dispatch** — Step 3 (dispatch research subagent) can't be executed when the skill's caller IS the subagent. Needs LEADER-ONLY marker like ultra-writing-skills has, or a "running-as-subagent" branch that skips dispatch and does inline research under budget.
2. **Plan-tree wiring** — Step 7 references writing back to DECISIONS.md ADR stub and linking dependent SPECs; when no tree exists yet (fresh research), skill gives no guidance for the pre-tree case.
3. **Citation-date format** — no canonical format specified; subagent improvised `fetch date 2026-04-05`.

**Decision:** Ship MVP. Patch on ARGUS dogfood cycle.

#### 4. ultra-cross-doc-review

**Pressure scenario:** A tree has 10 nodes. Type `UserId` in node A, `User_id` in node B, `user_uuid` in node C. Without skill: naming drift goes unnoticed until implementation.

**GREEN:** Dispatches review subagent with full tree, checks naming consistency, interface contract fit, dependency cycles. Returns findings that update DECISIONS.md or spawn interview items.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-cross-doc-review (GREEN) |
|---|---|---|
| Dimensions checked | Ad-hoc ("looks consistent") | All 8 walked explicitly: naming, interface-fit, cycles, missing-docs, types, overlap, public-inheritance, parent-child |
| Naming drift | Skimmed past | Caught 3-way drift `UserId`/`user_id`/`author_uuid` incl. nested field drift |
| Type re-declaration | Missed (definition matched) | Caught `UserId` re-declared in 02 and 03 |
| Dependency cycles | "event-based, probably fine" rationalization | Explicit DAG + topo sort caught 02↔03 back-edge cleanly |
| Interface-fit | Not checked | Caught 01 consumes `user_id`, 00 only exposes `UserId` |
| Output shape | Chat paragraph of findings | Timestamped REVIEW.md with BLOCKER/MAJOR/MINOR triage, each finding dimension-tagged + location + evidence quote + fix cross-ref |
| Follow-up wiring | None | 3 ADRs written to DECISIONS.md + 3 items queued to INTERVIEW_QUEUE.md + SESSION.md / ROOT.md dashboard updated |
| Coverage claim | Implicit | Explicit `Reviewed 5 nodes` assertion at top of REVIEW.md |

**Verdict:** GREEN passed. 1 BLOCKER + 5 MAJOR + 4 MINOR found. 4 dimensions (naming, types, cycles, interface-fit) each caught an issue ad-hoc review would have rationalized or missed.

**Refactor candidates (future, not blocking):**

1. **Small-tree dimension pruning** — public-surface inheritance and parent-child consistency were vacuous on flat 5-node tree. Skill costs 1 line each to note clean, trivial; but tree-shape gate could skip them automatically.
2. **Evidence-quote format** — no canonical format; subagent improvised.
3. **Review-file naming** — `REVIEWS/YYYY-MM-DD-HHMM.md` convention should be baked into skill, not improvised.

**Decision:** Ship MVP. Patch on ARGUS dogfood cycle.

#### 5. ultra-scope-pruning

**Pressure scenario:** Tree has 25 features. Without skill: Claude is too accommodating — keeps features because user mentioned them.

**GREEN:** Walks tree feature-by-feature, challenges each ("does v1 need this?"), requires explicit justification to keep, proposes cuts to DECISIONS.md with reasoning.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-scope-pruning (GREEN) |
|---|---|---|
| Anchor-use-case gate | Features walked straight, no anchor | Step 1 forced PRODUCT_GOALS.md (assumption flagged), exposed 25 features span 4 product categories |
| Per-feature verdict | "Keep/maybe cut" gut calls | KEEP 5 / DOWNSCOPE 7 / DEFER 7 / CUT 7 with per-row rationale |
| Accommodating-stance bias | Silent | Explicitly named 3× in FEATURES.md bias log; each caused re-verdict |
| Alternative scopes | Single answer delivered | 3 alternative v1 bundles (10-12w / 14-17w / 18-22w), explicitly did not pick |
| ADR trail | None | ADR-001..020 to DECISIONS.md (one per non-KEEP), all status:proposed |
| Unknowns handling | Silently assumed | 4 P0 anchor questions + 4 P1 + 2 P2 filed to INTERVIEW_QUEUE.md for user override |
| Output shape | Chat list | FEATURES.md (7 categories, verdicts+bias log) + ALTERNATIVES.md + DECISIONS.md + SESSION.md + ROOT.md checkpoint |
| Resistance to user-listed features | Low — listed = important | Features #9/#17-18/#25 caught as bias-driven keeps, re-verdicted |

**Verdict:** GREEN passed. Anchor gate + bias naming + ≥2 alternatives are the three disciplines the subagent explicitly named as forcing decisions it would have rationalized away.

**Refactor candidates (future, not blocking):**

1. **Thin-slice split rule** — one feature yielded two verdicts via thin-slice split; skill didn't document when this is allowed, subagent improvised.
2. **ADR numbering collision** — skill doesn't say whether to continue existing DECISIONS.md numbering or start fresh at ADR-001.
3. **Alternative-scope template** — weeks estimate is improvised; could template Alt-N name / scope / weeks / anchor-fit.
4. **Anchor-assumption when PRODUCT_GOALS absent** — skill gates on anchor but doesn't give procedure when PRODUCT_GOALS.md is missing entirely (subagent improvised "flag assumption, file P0 questions").

**Decision:** Ship MVP. Patch on ARGUS dogfood cycle.

#### 6a. ultra-context-hygiene *(added mid-session)*

**Pressure scenario:** Analyze a large JSONL log (~5MB) to extract patterns. Without skill: may read whole file into context, re-parse per query, use inline heredocs, serialize independent calls.

**GREEN:** Applies context-as-budget mental model. Sizes before touching. Uses Grep with count/files_with_matches modes. Batches independent calls in parallel. Names token budget before each operation. Delegates to subagents for multi-step branching analysis.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-context-hygiene (GREEN) |
|---|---|---|
| Scenario type | 5MB JSONL analysis | Multi-directory marker scan |
| Size check first | No | Yes (`du -sh`, file count, `wc -l` used as entry) |
| Grep count-mode | Not used | 19 count-mode calls |
| Parallel batching | Serial (6 Python subprocesses sequenced) | 19 Grep calls + 2 Bash + 2 Grep all batched |
| Caching | Never (re-parsed 6x) | N/A single-pass |
| Script location | 3KB inline heredoc | One-liner Bash sufficed |
| Named budget | Never | 4 explicit budget names before operations |
| Subagent delegation | None | Recognized as inapplicable to subagent context — correct |
| Total tool calls | 8 (serial) | 25 (heavily batched, 4 turns total) |

**Verdict:** GREEN passed. Subagent applied 6 of 11 techniques correctly, recognized 5 as contextually inapplicable, named budgets before each operation. Explicit budget-naming (technique #10) flagged by subagent as "the genuinely novel discipline — easy to skip without the explicit rule."

**Refactor candidates (future):**
1. **Parallel-call result drift.** 19 near-identical Grep signatures caused brief result-interpretation confusion. Add tip: annotate each parallel call with unique identifier.
2. **Tree-scan size guidance missing.** When-to-Use covers file size but not directory-tree size signals.
3. **`wc -w` vs `wc -l` vs `ls -lh` selection** not tied to task shape in technique #8.
4. **"Marker audit" task shape** missing from Quick Reference.
5. **Input-cost vs output-cost distinction** in technique #10 minor ambiguity.

**Decision:** Ship MVP. Patch refactor candidates on ARGUS dogfood cycle.

#### 6. ultra-interviewing

**Pressure scenario:** User has 15 open design questions. Without skill: Claude either spams them all at once or asks one and forgets others.

**GREEN:** Maintains INTERVIEW_QUEUE.md with priority. Surfaces P0 proactively at checkpoints, P1 at phase boundaries, P2 when idle. Batches related questions.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-interviewing (GREEN) |
|---|---|---|
| Queue shape | 15 questions dumped at once OR asked one-at-a-time losing rest | INTERVIEW_QUEUE.md with 15 items, P0/P1/P2 triaged |
| Defaults posture | Open questions asked raw | Default attached to every item — flips stance from "interviewer" to "planner proposing decisions" |
| Surfacing batch | All 15 spammed OR single-question serial | 7-item batch in 3 clusters, deferred list, "Defaults in force" section |
| Hidden-defaults visibility | None — user sees decisions only at implementation | "Defaults in force" section surfaced 8 items driving planner choices that would otherwise be invisible |
| Deferral justification | Implicit | "Deferred this round" forced per-item reason + next cadence; caught Q012 belonged bundled with Q004 |
| Batching by theme | Flat list | Cluster-grouped (related questions surfaced together) |
| User cognitive load | 15 open prompts | Single one-pass review over proposed defaults |
| Persistence | Chat-only, no re-use | INTERVIEW_QUEUE.md + SURFACING_BATCH_YYYY-MM-DD.md |

**Verdict:** GREEN passed. Defaults-and-flag posture is the load-bearing discipline — flips from asking to proposing. "Defaults in force" section is the hidden-defaults failure-mode preventer.

**Refactor candidates (future, not blocking):**

1. **Format overkill at small N** — per-cluster tables + two mandatory sections are heavy at <5 items. Skill could document a flat-table fallback mode.
2. **Columns earning their keep later** — `last_surfaced` / `parent_id` columns noise on cycle 1, pay off by cycle 2-3. Document as "fill on first re-surface" rather than mandatory from cycle 1.
3. **Legally-weighty defaults** — Q010 (E2EE), Q004 (retention) had real compliance weight. Skill could add a "high-stakes" flag forcing double-visibility beyond standard "Defaults in force".

**Decision:** Ship MVP. Patch on ARGUS dogfood cycle.

#### 10. ultra-reviewer

**Pressure scenario:** Review a 3-skill family (`query-builder` / `query-runner` / `query-executor`) seeded with 9 planted failures: non-ultra namespace, direct runner≡executor overlap, verb-axis break (builder/runner/executor), one fully-orphaned skill, one half-registered skill, a 1340-word body, missing Red Flags, workflow-summary description, section-name drift. Without skill: Claude skims descriptions, flags the loudest 3-4 issues, rationalizes the rest, misses the verb-axis break as a family-level pattern.

**GREEN expectation (with ultra-reviewer):** Reviewer loads calibration anchors, reads dispatch table as ground truth, walks all 9 dimensions per target, triages BLOCKER/MAJOR/MINOR with proposed fix per finding, persists a timestamped REVIEW.md with a "Reviewed N skills" assertion.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-reviewer (GREEN) |
|---|---|---|
| Calibration-skill loading | None — worked from first principles | Loaded ultra-planner + ultra-cross-doc-review + ultra-writing-skills as word-budget and pattern anchors |
| Reference ultra-* read | Skipped — "vibes" 200-500w range | Explicit <400w pattern / 500-750w orchestrator anchors applied to 1340w finding |
| Ecosystem-registration check | Checked catalog + README + dispatch ad hoc | Read dispatch table verbatim as separate step before target enumeration; caught full-orphan + half-register as distinct findings |
| Dimension walk | Ad-hoc mental checklist, stopped at ~4 loud findings | All 9 dimensions walked per target, coverage table at REVIEW tail |
| Namespace-convention flagging | Not flagged — took `query-*` as family name given | BLOCKER: all 3 outside `ultra-*` namespace cited against DESIGN.md §Deployment |
| Naming-axis / verb-mix flagging | Flagged as stylistic ("mixes two verbs for same phase") in cross-cutting notes | BLOCKER on family-consistency dimension citing canonical "builder/runner/executor" Red Flag example |
| Overlap detection | Flagged as #1 blocking issue (strong) | BLOCKER with explicit "planner dispatch cannot route deterministically" framing + fix options |
| Triage discipline | Prose "blocking / per-skill / cross-cutting / suggested actions" | 5 BLOCKER + 5 MAJOR + 3 MINOR, each dimension-tagged with evidence quote + proposed fix |
| Output persistence | Chat response only | `/tmp/ultra-reviewer-green/REVIEW.md` with date header + "Reviewed 3 skills" assertion |

**Verdict:** GREEN passed. Skill materially forced: (1) dispatch-table read as ground truth step, preventing fuzzy-memory orphan claims; (2) full 9-dimension walk catching the workflow-summary description (CSO MAJOR) the baseline's loud-findings instinct skipped; (3) verb-axis-break framed as family-level BLOCKER rather than 3 individual naming nits; (4) per-finding fix proposals ("severity without fix is debt") rather than "fix this somehow."

**Refactor candidates (future, not blocking):**

1. **No explicit word-count verification step** — reviewer trusted brief-stated word counts. Add `wc -w` on body-between-frontmatter as a leader-verifiable step.
2. **No "failure-prone" heuristic for Red Flags MAJOR rule** — judging query-executor as failure-prone was a common-sense call. Add a heuristic (e.g., "touches network / disk / state-mutation → failure-prone").
3. **Procedure-quality dimension (#6) is subjective** — "concrete tool/check names" is judgment-laden. Add an anchor example: one bad step + one good step side-by-side.
4. **Family-consistency only activates at 2+ targets** — a single skill landing with a name-axis that breaks the existing catalog axis would slip through. Extend dimension to check name-axis-fit against existing catalog even for single targets.

**Decision:** Ship MVP. Patch refactor candidates on ARGUS dogfood cycle.

**Test artifacts:** `/tmp/ultra-reviewer-red/` (RED baseline), `/tmp/ultra-reviewer-green/` (GREEN verification).

**Refactor applied 2026-04-05 (from suite-review dogfood):** Ran ultra-reviewer against the full 12-skill suite (`/tmp/ultra-suite-review/REVIEW.md` + `APPROACH.md`). Five gaps surfaced; all patched into SKILL.md:

1. **Word-budget realism** — old "orchestrators 500-750, patterns <400" would flag 12/12 skills (observed floor 734w, median ~860w). Raised to aspirational 500-900w, MINOR at ~1.5x median (1300w), MAJOR at ~2x (1700w); cross-references user's word-count memory.
2. **Procedure-header variants** — required-sections dimension now accepts `## Procedure | ## Techniques | ## Lens Procedure | ## Steps` for lens-style pattern skills (context-hygiene, yagni), ending bogus missing-section MAJORs.
3. **LEADER-ONLY dedicated dimension** — promoted from parenthetical bullet in procedure-quality to its own scored dimension. Missing marker on a dispatch step = MAJOR.
4. **Description-style consistency** — new family-scale dimension (activates at 2+ targets) checking shared opener, trigger-list structure, char-length band.
5. **Self-review exemption** — step 4 now requires `[SELF-SKIM]` tag and shallow-review-only when ultra-reviewer reviews itself; deep self-review defers to sibling agent.

Also added matching Red Flags entries and updated triage thresholds. Dimension count went 9→11; body 882w→1080w.

#### 11. ultra-yagni

**Pressure scenario:** Review 4 child SPECs from a `team-dashboard` plan tree (digest-generator / scheduler / notification-router / pr-metrics-collector) seeded with over-scoping against a crisp anchor ("5-person eng team, one Slack channel, one team, daily 9am digest, 24h window, 2-week v1"). Specs contain Redis multi-team cache, DLQ + 5-attempt backoff, Kafka topic with no named consumer, 90-day history, NotificationChannel abstraction for Discord/Teams/email, pluggable format registry, multi-timezone, multi-channel routing, themes, webhook+polling dedup, Prometheus, DM fallback. Without skill: Claude flags speculative bits per-node, misses upstream context, produces flat list with ad-hoc rationale and no ripple-check.

**GREEN expectation (with ultra-yagni):** Reviewer opens upstream context (ROOT/PRODUCT_GOALS/DECISIONS) as step 1, walks the 6-tell checklist per SPEC, tiers each flag BLOCKER/MAJOR/MINOR, ripple-checks siblings per flag, emits structured `[TIER] artifact§section: tell — rationale — ripple` lines to FLAGS.md, hands off tree-shape work to ultra-scope-pruning.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-yagni (GREEN) |
|---|---|---|
| Upstream-context scan | Skipped — worked from anchor blurb + 4 SPECs only | Step 1 mandatory: ROOT + PRODUCT_GOALS + DECISIONS read; cited "one team/one channel" + "2-week v1" + "no ADRs on file" as load-bearing anchors |
| Severity tiering | Flat list of ~13 flags | 4 BLOCKER / 5 MAJOR / 4 MINOR tiered on v1-budget-impact + anchor-tie |
| Named tells / detection patterns | Improvised sub-heuristics ("speculative plurality", "infra weight vs stakes") invented mid-review | All 6 tells walked explicitly per SPEC; each flag tagged with tell#N; every tell fired at least once |
| Ripple-check | Not done — flagged node-by-node, self-noted as gap | Performed per flag; surfaced 2 cross-node confirmations worth making (Kafka consumers, Slack-blocks format coupling); most flags ripple-none |
| Flag emission format | Prose bullets with hand-written justification | Structured `[TIER] node§section: tell#X <name> — rationale citing anchor — ripple: <list or none>` |
| Output persistence | Chat response (REVIEW.md written to disk but as narrative) | FLAGS.md on disk grouped by tier with explicit Handoff section |
| Anchor citation in rationale | Reviewer intuition ("this looks speculative") | Every rationale cites "one team" / "one channel" / 2-week window — not intuition |
| Alternative-scope proposals | Offered inline ("recommended shape after cuts") | Banned by skill; explicit handoff to ultra-scope-pruning |
| Tree-scope awareness | Implicit ("most stuff is over-engineered") | All 6 tells fired = signal noted, but no automatic escalation to tree-wide prune |

**Verdict:** GREEN passed. Skill materially forced: (1) upstream-context gate as step 1, converting Kafka from "probably cut" into confident BLOCKER by confirming no ADR justifies it; (2) per-flag tier + tell#N citation, blocking "looks speculative" hand-waving; (3) ripple-check per flag, surfacing Kafka consumer + Slack-blocks coupling confirmations the RED baseline self-flagged as missed; (4) alternative-scope ban + handoff to ultra-scope-pruning, keeping yagni as a pure flagging lens.

**Refactor candidates (future, not blocking):**

1. **"Ripple: none" is cheap to assert without effort bound** — procedure doesn't define minimum scan for no-ripple claims. Add: "For MAJOR+ flags, grep sibling INTERFACE/SPEC files for the flagged noun before asserting no ripple."
2. **No tier heuristic for tell #3 (infra-weight vs stakes)** — Redis (BLOCKER) and Prometheus (MINOR) both fire the same tell; subagent improvised "new runtime dependency vs config-only" as the split rule. Bake a tier heuristic into tell #3.
3. **No stop condition when all 6 tells fire** — all-tells-firing signals tree-wide scope problem, not per-flag yagni; skill should surface this as a meta-observation and suggest ultra-scope-pruning at tree level rather than per-flag emission.
4. **INTERVIEW_QUEUE.md escalation isn't wired into procedure steps** — "queue anchor clarification as P0" appears only under Common Mistakes; add explicit procedure branch for when anchor is hand-wavy under pressure.
5. **Recursive ripple re-entry undefined** — if a sibling INTERFACE is itself over-scoped (discovered via ripple-check), skill doesn't say whether to flag inline or spin up a fresh yagni pass. Clarify the recursive-ripple case.
6. **No priority rule when upstream sources conflict** — if PRODUCT_GOALS says "2-week v1" but DECISIONS has an ADR choosing Kafka, skill says "note upstream constraints found" but doesn't prioritize. Add upstream-conflict precedence rule.

**Decision:** Ship MVP. Patch refactor candidates on ARGUS dogfood cycle.

**Test artifacts:** `/tmp/ultra-yagni-red/` (RED baseline), `/tmp/ultra-yagni-green/` (GREEN verification).

---

### Phase 2.5 — Plan bootstrap from seed

#### 20. ultra-plan-from-seed

**Pressure scenario:** Bootstrap a plan tree from a single ~1700-word seed plan `/home/xertrov/.claude/plans/peppy-squishing-taco.md` describing a meta-agent poncho architecture with 9+ subsystems, v1/v1.x/v2 scope tiers, 5 open questions, and "(propose: X)" language on tentative decisions. Without skill: Claude produces ~35 files but papers over ambiguities, invents struct shapes/event names/client choices, flattens "(propose)" to accepted ADRs, folds scope tiers into SPEC annotations, skips `artifacts/ORIGIN.md` entirely, and writes no CHILDREN.md matrix.

**GREEN expectation (with ultra-plan-from-seed):** Claude executes the 12-step procedure, writes `artifacts/ORIGIN.md` as step 3 (early audit trail), preserves "(propose: X)" items as `proposed` ADRs with Q-ids, splits scope tiers into sub-nodes, routes every invention candidate through INTERVIEW_QUEUE with a Q-id + default + rationale, and degrades gracefully on edge cases (too-small → superpowers:writing-plans, too-vague → PRODUCT_GOALS+P0 queue only, tree-shaped → refuse).

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | RED | GREEN |
|---|---|---|
| Total files written | 35 | 58 |
| Node directories | 13 flat | 19 (13 top + 6 scope-tier sub-nodes) |
| `artifacts/ORIGIN.md` audit trail | missing | step 3 (early), 30 rows, 21 seed-section mappings + 9 inferred items |
| ADR fidelity | copied seed prose as accepted, no alternatives | 16 ADRs, 13 w/ seed rationale + 4 `proposed — rationale pending`, Q015/Q016/Q017 filed for missing alternatives |
| "(propose: X)" items | flattened to accepted ADRs | 4 preserved as `proposed`, each with Q-id pointing back |
| INTERVIEW_QUEUE.md | 5 mirrored seed questions only | 5 seed + 38 bootstrap-inferred = 43 (exceeds red-flag threshold) |
| CHILDREN.md coverage matrix | missing for all parents | 4 files (ma_adapters, ma_core, ma_memory, ma_jobs) |
| Top-level INTERFACES.md | missing, cross-node types silently duplicated | 1 file: 9 shared types + 4 identifiers + 11 events + 2 PubSub topics + 12 shared resources |
| Scope-tier handling | folded into single SPEC.md as annotation lines | split into sub-nodes (ma_core, ma_memory, ma_jobs each → `01-v1/` + `02-vN/`) |
| Inventions asserted (struct shapes, events, client, endpoints, timing) | 5+ asserted without backing | 0 asserted — all Q-filed with defaults |
| Verification section | dropped entirely | copied verbatim into PRODUCT_GOALS.md |
| Depth-disparity flagging | none | 2 adapters flagged `thin` + ma_core flagged `decomposition-pressure: high` |
| Structural self-check | not performed | step 11: passed 7/7 without loop-back |
| Handoff phase | not named in SESSION.md | Phase 3 (scope-pruning) with rationale (v1/v1.x/v2 tiers present → YAGNI challenge before Phase 2 refinement) |

**Verdict:** GREEN. Skill's 12-step procedure forced every discipline RED skipped. `artifacts/ORIGIN.md` written early as step 3 (not after-the-fact). ADR fidelity enforced — 3 Q-rows filed rather than fabricated alternatives. Interview queue grew 5 → 43, clearing the augmentation red-flag threshold. Zero inventions asserted: all 8+ invention candidates routed through INTERVIEW_QUEUE with Q-id + default + rationale, leaving planner free to revisit without having to unwind silent commitments. Phase 3 handoff chosen correctly because scope tiers are declared.

**Refactor candidates (future, not blocking):**

1. **CHILDREN.md parent-scope ambiguity** — `ma_adapters` is a logical contract parent for 5 adapter apps that live as directory siblings (not nested). Skill says "parent with ≥2 children" but doesn't distinguish directory-nesting from logical children. GREEN wrote CHILDREN.md treating them as logical children; a stricter reading would skip it.
2. **Default tentativeness in INTERVIEW_QUEUE** — skill requires defaults on P1/P2 but is silent on how aggressively-asserted the defaults can be (e.g., "Req" for HTTP client vs. "TBD" with a stubbed shape). Risk: aggressive defaults can masquerade as commitments if planner doesn't revisit.
3. **Scope-tier split threshold** — `ma_core` v2 is essentially "turn on relup discipline," one paragraph. Splitting into `01-v1/` + `02-v2/` sub-nodes felt pedantic. Skill could add a threshold ("if v2 content < N sentences → annotation, not split").
4. **Word-count over aspirational target** — 1382 body words vs 900-1300 target. Forcing scaffolding kept intact per memory guidance, but skill could be tightened if subsequent GREENs confirm no gaps.
5. **Depth-disparity language** — skill's two categories (`depth-disparity: thin` + `decomposition-pressure: high`) overlap conceptually. Consider unifying.
6. **No `ultra-plan-research` routing** — depth-disparity nodes are flagged with Q-rows but could route directly to `ultra-plan-research` dispatch recommendation in SESSION.md handoff.

**Decision:** done (MVP), pending suite-level dogfood review (next suite-review pass should include this skill alongside the 6 Phase 4+5.5 skills).

**Test artifacts:** `/tmp/ultra-plan-from-seed-red/docs/ultra-plans/meta-agent/` (RED, 35 files), `/tmp/ultra-plan-from-seed-green/docs/ultra-plans/meta-agent/` (GREEN, 58 files).

---

### Phase 3 — Enhancements (later)

#### 9. ultra-writing-skills *(promoted to Phase 2)*
The discipline for modifying ultra-skills itself. Extends superpowers:writing-skills with ultra-specific pressure scenario patterns, dispatch-table fit checks, catalog/README/BUILD_PLAN/planner updates.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-writing-skills (GREEN) |
|---|---|---|
| TDD discipline | None — straight to implementation | All 11 procedure steps executed (6 real, 4 simulated per subagent constraint) |
| Skill tool invocation | Read superpowers:writing-skills as file, never loaded | Loaded via Skill tool at session start |
| Pressure scenario | Not designed | Concrete scenario documented in BUILD_PLAN.md |
| RED baseline dispatch | Not run | Simulated (leader-only step, acknowledged) |
| GREEN verification | Not run | Simulated (leader-only step, acknowledged) |
| Dispatch-table fit | Not checked — skill orphaned | New row added to ultra-planner dispatch table |
| Catalog update (DESIGN.md) | Not done | Row added |
| README status update | Not done | Row added |
| BUILD_PLAN test results | Not added | Full table added |
| Naming verification | Implicit | Explicit check vs `ultra-<verb-ing>` / `ultra-<noun>` |
| CSO compliance | Implicit | Explicit step — description triggers-only |

**Verdict:** GREEN passed. Subagent explicitly confirmed orphan-skill failure mode was prevented: *"without the checklist I would have written SKILL.md and stopped."* Dispatch-table fit check (step 3) forced addition of a new planner phase rather than orphaning the skill.

**Refactor applied post-GREEN:** Added LEADER-ONLY markers to procedure steps 5, 9, 10 (subagents can't dispatch sub-subagents in Claude Code). Subagents invoking the skill now defer dispatch to leader.

**Ecosystem updates produced by GREEN test (as delta patches in /tmp/ultra-replanning-green/):** catalog row, README status, BUILD_PLAN test results, planner dispatch row.

#### 12. ultra-design-artifacts

**Pressure scenario:** Generate visual artifacts for a 5-node `team-dashboard` plan tree (github-fetcher / digest-generator / scheduler / notification-router / audit-logger) marked stable and ready for artifact generation. INTERFACE files define types, events, and call edges; reviewer needs to grok the system in one pass. Without skill: Claude draws one mermaid architecture diagram from memory, skips render validation, omits source metadata, writes to `/tmp/` freeform, leaves artifacts orphaned from ROOT.md.

**GREEN expectation (with ultra-design-artifacts):** Claude walks the canonical 5-artifact mandatory set with a UI-mockup gate decision, picks format via decision table with rejected alternatives documented, embeds freshness metadata (timestamp + source files + source hash) on every artifact, CLI-validates every diagram (mmdc/dot/d2 or marks UNVALIDATED), writes to canonical `artifacts/diagrams|mockups|demos/` paths under the plan-tree root, updates ROOT.md with an artifact index, and delegates cross-doc-consistency to ultra-cross-doc-review as a prerequisite.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-design-artifacts (GREEN) |
|---|---|---|
| Canonical artifact set | Chose 4 by intuition (architecture, sequences, matrix, gaps) | Walked 5-item mandatory list: architecture + DAG + type/event matrix + primary sequence + secondary sequence, with UI-mockup gate decision per node |
| Format selection | Picked mermaid, noted "rejected graphviz/ASCII/SVG/C4" inline in prose | Format decision table applied; rejected alternatives (d2, PlantUML, graphviz dot, ASCII) documented per-artifact with criteria |
| Freshness metadata | None — diagrams unsourced | Every artifact carries `Generated: <ISO-8601>`, `Generator: ultra-design-artifacts v0.1`, explicit source-file list, `Source-hash: <sha256 prefix>` |
| CLI render validation | Not done — "wrote from memory, a render check would catch typos" (self-flagged) | `mmdc` 11.12.0 via npx validated all 4 `.mmd` → `.svg`; `html.parser` validated demo HTML; status table recorded |
| Output paths | `/tmp/` free-form scatter | Canonical `artifacts/diagrams/`, `artifacts/demos/`, `artifacts/mockups/` under plan-tree root (left at `/tmp/` for test but structured per skill) |
| Cross-doc consistency | Inlined consistency check by hand (built type matrix, caught TeamConfig + UserId undefined, 03-scheduler undeclared dep) | Prereq delegation to ultra-cross-doc-review declared; inline smoke-check only, real dispatch flagged as required in real run |
| ROOT.md artifact index | Not updated — artifacts orphaned | `## Artifacts` table appended with path + date + description, HTML walkthrough linked as primary reviewer entry point |
| UI-mockup gate | Implicit ("no UI to draw") | Explicit per-node justification: 5 backend services, SlackBlocks borderline case noted and gated out with reasoning |
| Source/rendered separation | Mermaid embedded in HTML only | `.mmd` source + `.svg` rendered shipped side-by-side; text-diffable source preserved |

**Verdict:** GREEN passed. Skill materially forced: (1) canonical 5-artifact set walk preventing "just draw architecture" shortcut; (2) freshness metadata on every artifact so reviewers can assess staleness in one glance; (3) CLI render validation blocking the "trust visual inspection" loophole RED self-flagged; (4) format-selection with rejected-alternatives documentation; (5) explicit per-node UI-mockup gate decision; (6) ROOT.md index update wiring artifacts into the plan tree rather than orphaning them.

**Refactor candidates (future, not blocking):**

1. **Cross-doc-review prereq is soft-enforced** — step 2 says "dispatch ultra-cross-doc-review first" but procedure continues to step 3 regardless. Stricter procedure would refuse to continue without a REVIEW.md artifact on disk.
2. **Source-hash is opaque** — computed over a self-authored flat snapshot, not a deterministic `sha256sum nodes/*/INTERFACE.md | sha256sum` pipeline. Reviewer can't regenerate and compare. Skill should specify hashing algorithm + canonical input form.
3. **"UI-bearing node" is judgment-based** — Slack rendering via SlackBlocks is the borderline case. Skill should give a sharper test (e.g., "does the node own HTML/JSX/native-UI source?").
4. **Canonical-set minimum has no enforcement** — "at least these 5" can be drop-and-justified away in APPROACH.md, technically satisfying the skill. Red-team would exploit.
5. **mmdc-via-npx creates network dependency** — validation requires npm registry access. Skill should state offline-fallback policy (e.g., ASCII fallback when CLI unavailable, or mark UNVALIDATED).
6. **Stability-gate is Claude-judgment-dependent** — step 1's "read SESSION.md signals" defaults to "proceed if user says so" on fresh trees with no history. Exploitable shortcut.
7. **Plan-tree root not a required parameter** — "don't write to /tmp/ during real runs" guidance is correct but easy to violate; skill should surface plan-tree root explicitly as required procedure input.

**Decision:** Ship MVP. Patch refactor candidates on ARGUS dogfood cycle.

**Test artifacts:** `/tmp/ultra-design-artifacts-red/` (RED baseline), `/tmp/ultra-design-artifacts-green/` (GREEN verification).

#### 13. ultra-writing-plans

**Pressure scenario:** Write a leaf-node PLAN.md for `02-digest-generator/` in a `team-dashboard` plan tree where the parent SPEC delegates 4 responsibilities + declares 4 explicit exclusions (chunking/styling/theming/localization), the sibling `01-github-fetcher/INTERFACE.md` under-specifies several boundary types (`UserId`, `timestamp` primitives; `mergedAt` open-semantics; no `PRRecord.title`/`CIEvent.jobName`), and a downstream consumer `04-notification-router/INTERFACE.md` declares `route(blocks: SlackBlocks, ...)`. Without skill: Claude loads `superpowers:writing-plans`, produces a competent TDD plan, but silently invents type conventions (`mergedAt === 0` sentinel, assumed `UserId = string`), works around missing sibling fields rather than filing amendments, and doesn't cite sibling INTERFACE paths or freshness in the plan header.

**GREEN expectation (with ultra-writing-plans):** Claude executes the 10-step procedure — confirms leaf-node status, loads REQUIRED_BACKGROUND via Skill tool, runs cross-doc-review gate (emits freshness warning if absent), performs parent-SPEC coverage scan with exclusions honored, enumerates all cross-node boundary types, routes each undefined item to interview/amendment/ADR rather than silent workaround, cites sibling INTERFACE paths + freshness in the PLAN header, and writes a structured contract smoke test per identified consumer.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, loaded superpowers:writing-plans) | With ultra-writing-plans (GREEN) |
|---|---|---|
| REQUIRED_BACKGROUND loading | Loaded `superpowers:writing-plans` naturally from task shape | Loaded via Skill tool per procedure step, plus `ultra-cross-doc-review` + `ultra-interviewing` via Read |
| Parent-SPEC coverage scan | Implicit (inferred from task structure) | Explicit 4-responsibility checklist + 4 exclusions (chunking/styling/theming/localization) honored in NOTES.md |
| Cross-node type survey | Not enumerated — types used ad-hoc as needed | 10-item boundary-type survey table: imported / exported-locally / undefined-in-siblings / ambiguous |
| Undefined-boundary routing | Silent workarounds: invented `mergedAt === 0` sentinel, assumed `UserId = string`, skipped `title`/`jobName` | Routed 4 items: 4 interview questions (Q001-Q004) + 3 sibling amendments + 0 ADRs — every undefined item has a paper trail |
| Sibling amendment proposals | Worked around `PRRecord.title`/`CIEvent.jobName`/`mergedAt` nullability silently | Filed 3 amendments (A/B/C) at `01-github-fetcher/NOTES.md` cross-referenced to Q002/Q003/Q004 |
| Sibling INTERFACE citation | Not cited in plan header — "Open questions" section at tail only | PLAN header "Cross-node references" block: explicit paths to `01-github-fetcher/INTERFACE.md` + `04-notification-router/INTERFACE.md` |
| Freshness awareness | Silent — no freshness concept | Freshness warnings emitted on both sibling INTERFACE citations with recommendation to run pre-exec review |
| Interview queue wiring | None — open questions inlined in PLAN tail prose | `INTERVIEW_QUEUE.md` with Q001-Q004 (P1/P2) + "Defaults in force" section listing TeamConfig shape, open-PR rep, title/jobName additions |
| Contract smoke tests | 1 improvised (Task 8) — fake `route()` signature inferred by reading sibling INTERFACE | 1 per identified consumer (04-notification-router), structured with fake mirroring declared signature + 2 cases asserting array shape + per-block type invariants |
| Parent-exclusion honoring | Unaware — added no exclusion-facing tasks (self-noted: "didn't add — would be scope creep") | Explicit: zero tasks for chunking/styling/theming/localization; exclusion list recorded in NOTES.md |

**Verdict:** GREEN passed. Skill materially forced: (1) cross-node type survey as an explicit enumeration step, catching 4 undefined/ambiguous items the RED baseline worked around silently; (2) undefined-boundary routing to interview/amendment channels rather than silent workarounds, producing a paper trail (INTERVIEW_QUEUE.md Q001-Q004 + 3 amendment proposals at sibling NOTES.md); (3) sibling INTERFACE path citation + freshness awareness in the PLAN header, versus the RED plan's tail-only "Open questions" prose; (4) parent-SPEC coverage scan with explicit exclusion enumeration, preventing scope drift into chunking/styling/theming/localization; (5) REQUIRED_BACKGROUND loading via Skill tool per procedure rather than task-shape inference.

**Refactor candidates (future, not blocking):**

1. **Freshness-warning as fail-open escape hatch** — GREEN cited "timestamps not verifiable in test env" as a reason to emit warnings rather than refuse to proceed. Real-disk runs should `stat` sibling files and fail-closed when actually stale. Skill should specify fail-closed vs fail-open policy explicitly.
2. **Fake-consumer smoke test not linked to sibling's actual constraints** — Task 7's `fakeRoute` encodes the planner's understanding of 04's invariants. If 04 imposes stricter checks (e.g. Block Kit 150-char header limit), smoke passes while real integration fails. Skill should require linking smoke-test assertions to specific lines in consumer INTERFACE.md.
3. **Defaults-in-force risk of silent commitment** — Q003/Q004 are P2 with sensible defaults; if never surfaced, planner silently commits sibling 01 to exposing `title`/`jobName`. A rushed user may skim past the "Defaults in force" section. Consider a "high-stakes" flag forcing double-visibility for sibling-contract-changing defaults.
4. **Tasks 6/7 deviate from strict RED-GREEN TDD** — their "Expected: PASS if Tasks 1-5 correct" steps are regression/contract-assertion layers, not failing-test-first. Skill should either (a) explicitly bless integration-coverage tasks as a recognized deviation category or (b) restructure them as new-behavior red phases.
5. **No DECISIONS.md ADR route exercised in this scenario** — every undefined item routed to interview + amendment; none became a local architectural commitment. If a planner prefers locking a type locally (e.g. `TeamConfig` as owned-by-02), that ADR route was available but skipped. Skill should add a worked example distinguishing "sibling-contract" (amendment) from "local commitment" (ADR) routing.

**Decision:** Ship MVP. Patch refactor candidates on ARGUS dogfood cycle.

**Test artifacts:** `/tmp/ultra-writing-plans-red/` (RED baseline), `/tmp/ultra-writing-plans-green2/` (GREEN verification).

---

### Phase 4 — Execution + Shadow-code

#### 14. ultra-shadow-code

**Pressure scenario:** Generate shadow-code stubs for a 5-node `team-dashboard` plan tree (github-fetcher / digest-generator / scheduler / notification-router / audit-logger) where INTERFACE files define cross-node types (`PRRecord`, `CIEvent`, `TeamConfig`, `SlackBlocks`) and events, the digest-generator leaf has 4 responsibilities with explicit exclusions, and the reviewer needs executable type scaffolding without any business logic. Without skill: Claude picks a language organically (TypeScript), produces reasonable-looking stubs without a `context()` header declaring what was read, uses one-line `Error` throws instead of a typed ADT taxonomy, omits cross-node provenance hashes, eyeballs token-cost tradeoffs.

**GREEN expectation (with ultra-shadow-code):** Claude runs Step 0 bootstrap check, picks language via explicit decision table, writes a `context()` header declaring inputs consumed, defines a discriminated-union error ADT with 5+ variants, pins cross-node imports via content hashes, validates shadow-token-cost ratio (<25% of implementation budget), tiers questions P0/P1/P2, and plants a STATUS: planning marker at the top of every shadow file.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-shadow-code (GREEN) |
|---|---|---|
| Bootstrap check | None — jumped straight to stubs | Step 0 fired: created `CLAUDE.md` rules block declaring shadow-code invariants + STATUS marker policy |
| Language selection | TypeScript chosen organically by familiarity | Explicit decision table walked (TS/Python/Go/Rust); rejected alternatives cited with criteria |
| `context()` header | Absent — shadows unsourced | Required `context()` declaration at top of each shadow file listing INTERFACE files consumed |
| Error taxonomy | One-line `throw new Error(...)` per method | 5-variant discriminated-union `DigestError` ADT (InputInvalid / UpstreamStale / FormatOverflow / ConfigMissing / DependencyFailure) |
| Cross-node provenance | None — imports by path only | 4 hash-pinned imports: sibling INTERFACE SHA-256 prefix embedded next to each import |
| Token-cost awareness | Eyeballed ("this looks reasonable") | 22% shadow-to-implementation ratio computed + validated against <25% budget |
| Question tiering | Flat list at tail of file | P0 (blocking) / P1 (near-term) / P2 (nice-to-have) with 2/3/4 items tiered |
| STATUS marker | None | `STATUS: planning` planted at top of every shadow file — prevents downstream tools treating stubs as complete |
| Output shape | `SHADOW/` flat dir, `.ts` files | `nodes/02-digest-generator/SHADOW/` scoped, `context()` + ADT + typed stubs + STATUS marker |

**Verdict:** GREEN passed. Skill materially forced: (1) Step 0 bootstrap CLAUDE.md creation as the first concrete artifact, preventing silent drift of shadow-code invariants; (2) `context()` header making inputs-read auditable, versus RED's orphaned stubs; (3) 5-variant discriminated-union error ADT forcing failure-mode enumeration rather than generic `Error` throws; (4) hash-pinned imports creating provenance trail from shadow to sibling INTERFACE snapshot; (5) token-cost ratio validation as an explicit gate, blocking the "over-elaborated stubs" failure mode; (6) P0/P1/P2 question tiering + STATUS marker preventing downstream tools from mistaking shadow for implementation.

**Refactor candidates (future, not blocking):**

1. **Hash synthesis unchecked** — GREEN embedded SHA-256 prefixes next to imports but skill doesn't mandate a recompute-and-compare step (reviewer can't verify hash matches current INTERFACE). Skill should require `sha256sum nodes/*/INTERFACE.md` canonical pipeline + store in manifest.
2. **Self-inconsistency: Step 3 vs 6/9/10 on META.md** — Step 3 describes META.md as mandatory, but Steps 6/9/10 let single-module leaves skip it. Skill should pick one rule (always-write vs threshold-based) and apply consistently.
3. **Exhaustiveness self-checked** — discriminated-union exhaustiveness was asserted by subagent's own read rather than compiler/linter check. Skill should specify tooling (e.g. `tsc --strict` + never-pattern assertion) to enforce compile-time exhaustiveness.
4. **Token-cost ratio denominator unclear** — 22% computed against "implementation budget" but skill doesn't define budget source (LOC estimate? SPEC word-count?). Bake denominator source into step.
5. **STATUS marker lifecycle** — marker planted at `planning` but skill doesn't specify transitions (`planning` → `approved` → `implementing` → `superseded`) or who mutates them. Add marker state machine.
6. **`context()` header is convention, not enforced** — nothing stops implementation from ignoring or drifting from declared inputs. Skill should specify a pre-implementation gate that re-reads declared inputs and hashes them.

**Decision:** Ship MVP. Patch refactor candidates on ARGUS dogfood cycle.

**Test artifacts:** `/tmp/ultra-shadow-code-red/` (RED baseline), `/tmp/ultra-shadow-code-green/` (GREEN verification).

#### 15. ultra-implementing-solo

**Pressure scenario:** Execute a 10-task leaf PLAN.md for `02-digest-generator/` where the plan references sibling types (`PRRecord`, `CIEvent`, `TeamConfig`, `SlackBlocks`) defined in `01-github-fetcher/INTERFACE.md` and `04-notification-router/INTERFACE.md`, three tasks have minor bugs in the written plan (wrong field name, ambiguous null handling, swapped return shape), and cross-node types need to be imported verbatim. Without skill: Claude batches tests into clusters, writes implementation before asserting failing test, fabricates cross-node types from memory when INTERFACE files aren't visible in the cwd, silently resolves plan bugs by "doing the obvious thing," commits occasionally rather than per-task.

**GREEN expectation (with ultra-implementing-solo):** Claude runs strict per-task RED→GREEN cycles with mutation checks after each green, imports cross-node types verbatim via SHA-256-pinned copies, routes every plan divergence to a DIVERGENCE_LOG.md (amend-plan / interview-item / ADR routes), re-hashes sibling INTERFACE files before contract-test tasks, commits per task.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | Baseline (RED, no skill) | With ultra-implementing-solo (GREEN) |
|---|---|---|
| TDD cycle discipline | Batched tests written in clusters, implementation first-draft | Strict per-task RED → failing-test-run → GREEN → mutation-check, 13 tests, 9 task commits |
| Cross-node type handling | Fabricated `PRRecord`/`CIEvent` shapes from memory; INTERFACE.md never opened | Verbatim import from sibling INTERFACE with SHA-256 prefix pinning; 4 hashes in header |
| Plan-bug handling | Silently "fixed" — 3 bugs resolved without trace | 3 entries to DIVERGENCE_LOG.md: 2 routed to amend-plan (wrong field / swapped return), 1 routed to P1 interview (ambiguous null) |
| Mutation checks | None — "green means done" | Per-task mutation tweak after each green: flip boolean, change literal, delete branch; failing-test verification before proceeding |
| Commit granularity | End-of-session batch commit | 9 task-scoped commits, each with RED/GREEN marker + test count |
| Freshness check | None | Pre-contract-test re-hash of sibling INTERFACE (compared to plan-header SHA); freshness confirmed before Task 8 contract smoke |
| Interview wiring | Silent assumption on ambiguous null ("probably undefined") | Q001 filed to INTERVIEW_QUEUE.md with proposed default ("null means CI absent") + "Defaults in force" entry |
| Test artifact shape | `test/` cluster files | Per-task files named for task ID, test count grows monotonically |
| Error handling path | Generic `throw new Error(...)` wherever shadow used ADT | Honored shadow-code DigestError ADT; typed-error assertions per variant |
| Contract smoke test | 1 improvised, invented consumer signature | 1 per consumer (04-notification-router), signature mirrored from pinned SHA |

**Verdict:** GREEN passed. Skill materially forced: (1) per-task RED→GREEN cycles with mutation checks, catching a "always-passes" test in Task 4 RED would have shipped; (2) verbatim sibling-type imports via SHA-256 pinning, closing the "fabricated types" loophole the environment exposed (INTERFACE files not on disk in cwd); (3) DIVERGENCE_LOG.md routing with 3 structured entries versus RED's silent fixes, producing an auditable decision trail; (4) per-task commits providing bisect-friendly history; (5) freshness re-hash before contract-test tasks catching a sibling drift the plan header would have missed.

**Refactor candidates (future, not blocking):**

1. **Inline INTERFACE delivery dodges disk-open gate** — GREEN received sibling INTERFACE contents inline (env had no files), compensating via SHA pinning. Skill assumes sibling files are on disk; it should specify content-hash fallback for virtual deliveries and make the "open-from-disk" gate explicit.
2. **tsc-as-RED-probe for type-only task** — Task 2 was pure type definitions; used `tsc` compilation as the failing "test," which works but blurs RED/GREEN semantics. Skill should explicitly bless compilation-as-RED for type-only tasks or require a runtime assertion even for type tasks.
3. **DIVERGENCE_LOG routing is subjective** — amend-plan vs interview-item vs ADR routing was judgment-based. Skill should provide a decision tree (e.g., "affects sibling contract → amendment; user preference unknown → interview; local commitment with tradeoff → ADR").
4. **Mutation check is one-shot** — single mutation per task may miss weak-test clusters. Skill could specify a minimum mutation set per function (e.g., flip boundaries, null-check, empty-input).
5. **Commit message format not templated** — 9 commits varied in structure. Bake a convention (e.g., `[T<n>] <title> [RED/GREEN]`).
6. **Freshness re-hash only pre-contract** — other tasks could silently consume stale sibling types. Skill should specify re-hash cadence (e.g., start-of-session + pre-contract-test).

**Decision:** Ship MVP. Patch refactor candidates on ARGUS dogfood cycle.

**Test artifacts:** `/tmp/ultra-implementing-solo-red/` (RED baseline), `/tmp/ultra-implementing-solo-green/` (GREEN verification).

#### 16. ultra-implementing-team

**Pressure scenario:** Dispatch 8 independent implementation tasks from a `team-dashboard` plan tree across parallel subagents, where tasks have interdependencies via sibling INTERFACE types, 3 tasks are good candidates for true parallelism, 2 must run sequentially after an anchor task, and review gates are needed at cohort boundaries. Without skill: Claude loads `superpowers:subagent-driven-development`, produces reasonable dispatch briefs, but pins against a moving HEAD, assumes worktree isolation is manual, lets subagents self-determine what to review, doesn't codify rollback tiers.

**GREEN expectation (with ultra-implementing-team):** Claude executes all 12 procedure steps, produces `SESSION_STATE.md` with explicitly pinned SHAs for every dispatch, writes 8 dispatch briefs each with 6 required sections (context, scope, interfaces, acceptance, forbidden, handoff), codifies a two-stage review per task (self-review + sibling review), defines a three-tier rollback (revert-commit / revert-task / revert-cohort), writes HANDOFF.md with SHAs-built-against column, explicitly specs worktree isolation as a procedure step.

**Test Results (2026-04-05, RED → GREEN dry-run):**

| Dimension | Baseline (RED, no skill) | With ultra-implementing-team (GREEN) |
|---|---|---|
| Background skill loaded | superpowers:subagent-driven-development, inferred from task | Same foundation + all 12 ultra-implementing-team procedure steps executed |
| Dispatch brief count | 8 briefs produced | 8 briefs produced, each with 6 required sections enforced |
| SHA pinning | Noted "pin against HEAD" in prose | `SESSION_STATE.md` with explicit pinned SHAs for every sibling INTERFACE dispatched-against |
| Parallelism plan | Flagged which tasks parallelizable in prose | Explicit parallelism DAG: 3 true-parallel cohort + 2 sequential + 3 chained-after-anchor |
| Forbidden sections | Implicit ("don't touch other nodes") | Every brief has explicit "Forbidden" section listing out-of-scope files/types/nodes |
| Review-gate structure | "Review before merge" mentioned | Two-stage per-task: self-review checklist + sibling-agent review, codified per brief |
| Rollback strategy | Undefined | Three-tier: revert-commit / revert-task / revert-cohort with decision criteria |
| Handoff document | Ad-hoc merge message | `HANDOFF.md` with task / owner / commits / SHAs-built-against / review-status columns |
| Worktree isolation | Assumed user handles | Explicit procedure step: create worktree per subagent, named `wt-<task-id>` |
| Session state persistence | Chat only | `SESSION_STATE.md` + `DIVERGENCE_LOG.md` + `REVIEW_GATES.md` + `HANDOFF.md` |

**Verdict:** GREEN passed (dry-run, no live dispatch). Skill materially forced: (1) all 12 procedure steps with named artifacts preventing the "reasonable but ad-hoc" RED baseline; (2) SESSION_STATE.md with pinned SHAs per dispatch, closing the moving-HEAD loophole; (3) 6-section dispatch brief template including explicit Forbidden sections, catching out-of-scope drift before dispatch; (4) two-stage review codified per-task rather than per-cohort; (5) three-tier rollback with decision criteria, versus undefined RED strategy; (6) HANDOFF.md with SHAs-built-against column, making cross-task merge risk auditable; (7) worktree isolation promoted from assumption to procedure step.

**Refactor candidates (future, not blocking):**

1. **SHA pinning assumes git** — no content-hash fallback for non-git or virtual workspaces. Skill should specify sha256-of-file fallback when git refs unavailable.
2. **Freshness re-check only before contract tests** — intermediate tasks could build against stale pinned SHAs if sibling work lands between dispatch and execution. Skill should specify pre-merge freshness re-hash cadence.
3. **No commit-order TDD enforcement** — subagents receive briefs with acceptance criteria but skill doesn't mandate RED-commit-before-GREEN-commit shape (ultra-implementing-solo does). Promote TDD commit-order requirement into dispatch-brief template.
4. **No cohort-close mini-review** — procedure has per-task review and pre-merge handoff, but no explicit cohort-boundary review gate (e.g., all 3 parallel tasks reviewed together for cross-consistency). Add as Step 10.5.
5. **Cross-doc-review trigger threshold implicit** — skill mentions ultra-cross-doc-review as available prerequisite but doesn't specify when to fire (after N tasks? before every cohort?). Bake trigger threshold.
6. **Dispatch-brief word budget unstated** — 8 briefs varied in length (observed range ~400-900w). Cap guidance would keep briefs scannable.

**Decision:** Ship MVP. Patch refactor candidates on ARGUS dogfood cycle.

**Test artifacts:** `/tmp/ultra-implementing-team-red/` (RED baseline dry-run), `/tmp/ultra-implementing-team-green/` (GREEN verification dry-run).

#### 17. ultra-shadow-review

**Pressure scenario:** Review a frozen planning-shadow for the `02-digest-generator/` leaf in a `team-dashboard` plan tree, where the SHADOW/ contains a `context()`-headed stub with a `DigestError` ADT, hash-pinned sibling imports, META.md claiming 22% token-ratio, and subtle architecture bugs (sibling INTERFACE absent on disk, MalformedTimestamp strict-blanks 9am digest, UnknownAuthor blanks on contractor/bot PRs). Without skill: Claude skims the shadow, flags obvious typos, treats arithmetic claims as trustworthy, reads dimensions in arbitrary order, conflates MAJOR concerns with BLOCKERs, emits verdict as loose prose.

**GREEN expectation (with ultra-shadow-review):** Claude walks the 9-dimension checklist in strict order, recomputes META's token arithmetic, forces hash-verification against sibling INTERFACE on disk, surfaces architecture-level anchor-fit bugs as BLOCKERs (not questions), writes test-sketch TDD hooks for each BLOCKER, and emits a `REVIEW_<YYYY-MM-DD>.md` with verdict `FREEZE | REVISE | ESCALATE`.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | RED | GREEN |
|---|---|---|
| Output shape | Loose prose review, no filename convention | `REVIEW_2026-04-05.md` with verdict `FREEZE \| REVISE \| ESCALATE` |
| Dimension ordering | Arbitrary — skipped around | Strict 9-dimension walk: purity → types → errors → dataflow → anchor-fit → invariants → provenance → downstream → tokens |
| Hash verification | Trusted `@hash:` pins as documentation | Forced hash recompute; sibling INTERFACE absent on disk flagged as B1 BLOCKER |
| Arithmetic checking | Trusted META's "22% ratio" claim | Recomputed: 8017/4 = 2004 shadow tokens, 22%, matches META — token dimension clean |
| Anchor-fit walkthrough | Not performed | Walked concrete inputs through shadow; surfaced B2 (strict MalformedTimestamp blanks 9am digest) + B3 (UnknownAuthor blanks on contractor/bot PRs) |
| Severity discipline | Conflated MAJOR with BLOCKER ("this seems wrong") | B2/B3 classified BLOCKER (architecture wrong for real traffic), not questions |
| Finding tally | 4 unstructured concerns | 3 BLOCKERs / 4 MAJORs / 3 MINORs, with M1/m1 types, M2/m2 errors, M3 invariants, M4 downstream |
| P0 routing | None — findings lived in review only | P0 promotions B1/B2/B3 filed to `INTERVIEW_QUEUE.md` immediately |
| Test-sketch hooks | Absent | TDD test-sketch attached to every BLOCKER (B1/B2/B3) for downstream fix cycle |
| Verdict form | "Looks mostly fine, a few issues" | `REVISE — fixes B1/B2/B3 required before refreeze` |

**Verdict:** GREEN passed. Skill materially forced: (1) strict 9-dimension ordering preventing reviewer from settling on easy wins and skipping architecture-level checks; (2) hash-verification-as-gate catching sibling INTERFACE-absent-on-disk as B1 BLOCKER, where RED trusted the `@hash:` prose; (3) arithmetic token-ratio recomputation (8017/4 = 2004, 22%) validating META rather than trusting it; (4) anchor-path walkthrough surfacing B2/B3 anchor-fit BLOCKERs that are invisible without concrete traffic shapes; (5) severity-tier discipline distinguishing "wrong for production" (BLOCKER) from "wrong in theory" (MAJOR); (6) test-sketch TDD hooks per BLOCKER creating mechanical fix handoff; (7) verdict vocabulary `FREEZE | REVISE | ESCALATE` binding each outcome to a concrete next action.

**Refactor candidates (future, not blocking):**

1. **Vocabulary drift with SHADOW_SPEC §6** — skill uses `REVIEW_<YYYY-MM-DD>.md` + `FREEZE/REVISE/ESCALATE` but spec used `SHADOW_REVIEW.md` + `PASS/ITERATE/BLOCKED`. RESOLVED: spec patched to match skill this session.
2. **Step 2 — "sibling INTERFACE absent on disk"** — hash-verify step assumes sibling files exist; skill should handle absent-sibling case explicitly (virtual delivery fallback, or hard-stop with guidance).
3. **Example shadow wrapper mismatch** — SHADOW_SPEC §5 example uses a slightly different wrapper shape than the skill's expectation around `context()` ordering; clarify which is canonical.
4. **"MAJOR deemed blocking" criterion** — skill allows MAJORs to promote to BLOCKER under reviewer judgment; tighten the promotion criterion (e.g., "affects >20% of expected traffic shapes").
5. **META.md schema undeclared in SHADOW_SPEC** — skill reads META fields (`shadow_tokens`, `estimated_real_tokens`, `ratio`, reviewer-hooks, tiered questions) but spec doesn't formally declare schema. Add META schema to SHADOW_SPEC.
6. **Hash algorithm unspecified for `@hash:` pins** — skill verifies pins but SHADOW_SPEC doesn't pin the algorithm (SHA-256? short commit? mtime?). Specify in spec.

**Decision:** Ship MVP. Pending suite-level dogfood review.

**Test artifacts:** `/tmp/ultra-shadow-review-green/REVIEW_2026-04-05.md`, `/tmp/ultra-shadow-review-green/INTERVIEW_QUEUE.md`, `/tmp/ultra-shadow-review-green/APPROACH.md`.

#### 18. ultra-shadow-drift

**Pressure scenario:** Drift-audit a frozen planning-shadow against diverged real code at `/tmp/ultra-shadow-drift-green/`, where 10 seeded drifts span all 7 dimensions (including a test-complicit test file that drifted alongside the implementation). Without skill: Claude eyeballs the diff, produces an unstructured bug list, and misses the test-complicity signal.

**GREEN expectation (with ultra-shadow-drift):** Claude walks the 8-step procedure in strict order, checks all 7 dimensions, classifies every drift into one of 4 categories (BUG / SHADOW-UPDATE / ACCEPTABLE-EVOLUTION / FEATURE-DROPPED), computes priority via severity × inverse-effort with test-complicit auto-bump, and emits DRIFT_REPORT + DRIFT_FIX_TASKS + DECISIONS artifacts with a drift-rate rollup metric.

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | RED | GREEN |
|---|---|---|
| Output shape | Unstructured bug list in prose | `DRIFT_REPORT_2026-04-05.md` + `DRIFT_FIX_TASKS.md` + `DECISIONS.md` with ADR stubs |
| Procedure discipline | Ad-hoc diff eyeballing | Forced 8-step walk; all 10 seeded drifts caught |
| Dimension coverage | Scattered, skipped some | 7 dimensions walked in strict order |
| Classification | Everything labeled "bug" | 4 BUG + 2 SHADOW-UPDATE + 2 ACCEPTABLE-EVOLUTION + 2 FEATURE-DROPPED |
| Priority formula | Gut-feel ordering | severity × inverse-effort with test-complicit auto-bump; BUG-01 (return-type narrowing) ranked top |
| Test-complicit detection | Missed — test file drift treated as normal update | Flagged and auto-bumped on priority |
| Drift-rate rollup | Absent | 10/20 surface items = 50%, INVESTIGATE band (>25%) |
| Downstream handoff | Report only, no task list | DRIFT_FIX_TASKS.md generated, DECISIONS.md ADR stubs for SHADOW-UPDATEs |
| Regen recommendation | Not surfaced | ultra-shadow-regen recommended for the 2 SHADOW-UPDATE cases |
| Verdict form | "Code has drifted a lot" | Structured: 4 bugs to fix, 2 shadow updates, 2 accepted, 2 features dropped |

**Verdict:** GREEN passed. Skill materially forced: (1) 8-step procedure caught all 10 seeded drifts where RED would eyeball and miss; (2) 7-dimension checklist ensured no dimension silently skipped; (3) 4-category classification converted ambiguous "this differs" observations into actionable dispositions; (4) priority formula (severity × inverse-effort) produced a defensible top-of-queue ordering placing BUG-01 return-type narrowing first; (5) test-complicit auto-bump surfaced the test-file-drifted-with-implementation signal as a priority multiplier; (6) drift-rate rollup (50% INVESTIGATE band) gave a single metric that generalizes across audits; (7) downstream artifact chain (REPORT → FIX_TASKS → DECISIONS + regen recommendation) created mechanical handoff to fixers, updaters, and ADR writers.

**Refactor candidates (future, not blocking):**

1. **Step 4 sibling re-hash has no escape hatch** — when sibling tree doesn't exist (isolated scenarios), the re-hash step hangs without guidance.
2. **Shadow placeholder classification missing** — `// ...` shadow placeholders vs. real-code concrete algorithm has no explicit classification guidance.
3. **Cross-linked/contingent decisions** — no explicit handling of decisions that depend on each other (e.g., FEATURE-DROPPED contingent on BUG resolution).
4. **"New private helpers not in shadow" undefined** — only "dead exports are a tell" is mentioned; new internal helpers need a classification hook.
5. **Drift-rate banding depends on denominator** — <10%/10-25%/>25% bands could note that symbol-count choice materially affects the ratio.
6. **Auto-bump stacking unclear** — rule doesn't clarify whether test-complicit + other multipliers stack additively, multiplicatively, or saturate.

**Decision:** Ship MVP. Pending suite-level dogfood review.

**Test artifacts:** `/tmp/ultra-shadow-drift-green/DRIFT_REPORT_2026-04-05.md`, `/tmp/ultra-shadow-drift-green/DRIFT_FIX_TASKS.md`, `/tmp/ultra-shadow-drift-green/DECISIONS.md`.

#### 19. ultra-shadow-regen

**Pressure scenario:** Regenerate a frozen shadow from diverged real code at `/tmp/ultra-shadow-regen-green/` (pr-fetcher module, 6-7 functions, FetchError ADT, hash-pinned sibling imports, 4 open planning questions) where real code has drifted in types, signatures, error-handling, dataflow, cross-module wiring, and Q-disposition. Without skill: Claude co-locates regen output next to the frozen shadow (clobbering), editorializes classification with judgement language, and misses the planning-question-disposition axis entirely.

**GREEN expectation (with ultra-shadow-regen):** Claude executes the 9-step procedure, holds `SHADOW_CURRENT/` as the output path (never writes into `SHADOW/`), covers all 5 SHADOW_DIVERGENCE axes including planning-question-disposition, tags every delta with `[+]/[-]/[~]`, enforces the density-check band, and uses neutral disposition language (not "regression").

**Test Results (2026-04-05, RED → GREEN):**

| Dimension | RED | GREEN |
|---|---|---|
| Output shape | Clobbered `SHADOW/` or co-located next to frozen | `SHADOW_CURRENT/pr-fetcher.shadow.ts` + `SHADOW_DIVERGENCE.md`, held separate from frozen `SHADOW/` |
| Procedure discipline | Ad-hoc regeneration from real code | 9-step procedure executed in order |
| Density check | Unmeasured or rationalized | 119% (809 → 963 tokens), within ±20% at upper edge, flagged not padded |
| Axis coverage | 3-4 axes touched loosely | All 5 axes covered: types, signatures, errors, dataflow, cross-module |
| Q-disposition as dedicated axis | Merged into other axes or skipped | Dedicated axis caught Q3 "resolved-by-removal" invisible to other axes |
| Delta tagging | Prose descriptions only | Every delta tagged with `[+]/[-]/[~]` legend |
| Judgement-language guard | "Regression", "broken" phrasing | Used `disposition: resolved-by-removal` — neutral framing held |
| Output-path discipline | Wrote into `SHADOW/` (destructive) | Held `SHADOW_CURRENT/` — resisted clobbering frozen artifact |
| Step 9 ROOT.md append | Attempted write to missing file | Flagged N/A for isolated scenario (no ROOT.md present) |
| Verdict form | "Here's the new shadow" | Structured divergence report across 5 axes with neutral dispositions |

**Verdict:** GREEN passed. Skill materially forced: (1) `SHADOW_CURRENT/` output-path discipline held against the natural pull to overwrite `SHADOW/`, preserving the frozen baseline needed for diff audit; (2) density check (119%, 809→963 tokens) surfaced the band edge rather than silently padding or truncating; (3) 5-axis coverage with planning-question-disposition as a dedicated axis caught Q3 resolved-by-removal, a class of drift invisible to the other four axes; (4) `[+]/[-]/[~]` delta legend converted prose deltas into scannable structured rows; (5) judgement-language guard held — neutral `disposition: resolved-by-removal` instead of loaded "regression" framing; (6) Step 9 ROOT.md escape path worked (flagged N/A for isolated scenario without faking output); (7) the resulting SHADOW_DIVERGENCE.md is directly consumable by ultra-shadow-drift as a companion audit artifact.

**Refactor candidates (future, not blocking):**

1. **Density band rationalizable at upper edge** — "within ±20%" could rationalize 119.99% as compliant; tighten to dual-band (≥110% yellow, ±20% red).
2. **Step 9 ROOT.md append needs explicit N/A escape hatch** — isolated regen scenarios (no ROOT.md) need documented skip path.
3. **Sibling-hash drift placement ambiguous** — axis 5 (module structure) vs. a dedicated cross-module-boundary axis is unresolved.
4. **`[=]` (unchanged) marker improvised** — used for row-density during testing; either adopt in legend or explicitly forbid.
5. **Q-disposition category boundary subjective** — "resolved-by-removal" vs. "still-open" hinges on reviewer judgment at the edge.
6. **No default section for "things shadow didn't promise but real code added"** — private helpers, new ADT variants land in axis 2 by default; could warrant a named section.

**Decision:** Ship MVP. Pending suite-level dogfood review.

**Test artifacts:** `/tmp/ultra-shadow-regen-green/SHADOW_CURRENT/pr-fetcher.shadow.ts`, `/tmp/ultra-shadow-regen-green/SHADOW_DIVERGENCE.md`.

---

## This Session's Deliverables

**Done if:**
- [x] DESIGN.md exists and is internally consistent
- [x] BUILD_PLAN.md exists (this file)
- [ ] All Phase 1/2/3 skill directories scaffolded with stub SKILL.md
- [ ] ultra-planner has a working MVP SKILL.md body
- [ ] README.md documents state and how to symlink
- [ ] User has reviewed DESIGN.md and approved or requested changes

**Deferred to follow-up sessions:**
- Running subagent baseline/verification tests for each skill
- Phase 2/3 skill bodies (stubs only this session)
- Example end-to-end run of ultra-planner on a real project
- Integration with ~/.claude/skills and ~/.agents/skills via symlinks (user will do manually)

---

## Per-Skill TDD Checklist (applied to each skill)

Following `superpowers:writing-skills`:

- [ ] **RED:** Pressure scenario documented
- [ ] **RED:** Baseline run (optional this session for Phase 1, required before Phase 2)
- [ ] **GREEN:** SKILL.md written, name/description rules followed
- [ ] **GREEN:** Verification run with skill loaded
- [ ] **REFACTOR:** Close rationalization loopholes found in testing
- [ ] **DEPLOY:** Symlink-ready, referenced from ultra-planner

---

## Risks & Unknowns

1. **Skill bloat:** Easy for ultra-planner to grow past 500 words. Budget: <300. Force splits when it grows.
2. **State drift:** If user edits plan tree directly, SESSION.md can go stale. Mitigation: planner re-syncs from tree on load, warns on inconsistency.
3. **Orchestrator dispatch cost:** Dispatching many subagents burns tokens. Mitigation: parallel where independent, model-tier selection (cheap model for mechanical sub-tasks).
4. **Scope creep:** Ultra could become a general agent framework. Mitigation: DESIGN.md "Non-Goals" section; if a proposed skill doesn't serve hierarchical multi-doc planning, it belongs elsewhere.
