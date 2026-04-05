# Shadow-Code: Overview

**NOTE 2026-04-05:** This document is retained as **historical context**
from the initial name-collision research. The project has since pivoted
to a different, clearer vision: shadow-code as a **cheap pseudocode
architecture-spec layer** between PLAN.md and real code (Pattern A's
spirit, decoupled from its VS Code transform).

For the current design, see:
- `INTEGRATION_IDEAS.md` (rewritten) — 3-skill family proposal
- `LIFECYCLE.md` — what happens to shadow over a project's lifetime
- `FORMAT_COMPARISON.md` — format evaluation + recommended default

The Pattern B / B' (Shadow Workspace / worktree-per-agent) analysis
below is no longer driving integration plans, though it remains the
right reference if the team ever revisits worktree isolation.

---

## Name collision — two distinct patterns under similar names

The project at **https://github.com/adifyr/shadow-code** is **NOT** the
"parallel-view / isolated-state" pattern the ultra-skills suite is looking
for. It is a VS Code extension for pseudocode-to-code transformation.

The pattern the ultra-skills user description gestures at ("agents operate
on a parallel/isolated view of state while the user's canonical state stays
untouched") is **Shadow Workspace**, originally from Cursor. This document
covers both, clearly labeled.

---

## Pattern A: `adifyr/shadow-code` — Pseudocode-to-Code Transform

**Source:** https://github.com/adifyr/shadow-code (v0.7.4, GPL-3.0, TypeScript VS Code extension, 70 stars)

**Tagline from repo:** `"Developers think in code, not paragraphs."`

### What it is
A VS Code / Cursor extension that transforms human-written pseudocode into
production code in a target language. The user writes in `.shadow` files,
invokes a transform, and the AI emits real code back into the original
source file.

### Problem it solves
Vibe-coding from natural language is imprecise. The claim is that
pseudocode is closer in form to the target output, so the model produces
"more consistent and deterministic" code, faster, with fewer tokens, using
cheaper models. Quote from README: *"the input that the AI receives is much
closer in nature to the intended output."*

### Mechanics
1. Open "Shadow Mode" (Ctrl+Alt+S) on a source file. A split-view opens
   with a parallel `.shadow` file.
2. Shadow files live in `.shadows/` at workspace root, mirroring the
   source-file tree. README recommends adding `.shadows/` to `.gitignore`.
3. User writes pseudocode. A reserved `context()` function (previously
   `import()`) at the top of the shadow file declares which real files the
   model should see: `context("src/components/chat_message.tsx", "assets/styles/message.css");`
4. Press Ctrl+Alt+Enter to transform. The extension bundles a system
   prompt (`assets/prompts/system.md`), user prompt, config file content
   (`package.json` / `pubspec.yaml` / etc.), and optional language skills
   from `.shadows/.skills/<LANGUAGE>.md` (e.g. `DART.md`), and sends to the
   user's selected VS Code Language Model provider.
5. The model's output overwrites the original source file. Missing
   dependencies (detected from generated code vs config) are auto-installed
   for "1st-class" languages (JS, TS, Java, Dart, Python, Rust, Go).

### Key artifacts / conventions
- `.shadows/` — mirror tree of `.shadow` pseudocode files
- `.shadows/.skills/<LANGUAGE>.md` — per-language user-authored instruction
  files (filename is SHOUT-CASE, e.g. `DART.md`, `PYTHON.md`)
- `context(...)` — the only reserved syntax in a shadow file
- System prompt: transform pseudocode-diff + existing code + config +
  skills → final code (see `assets/prompts/system.md`).

### Handoff
- Handoff is fully automated: the extension writes directly to the source
  file as a single edit (undo-able with Ctrl+Z as of v0.5.5).
- No branch, no worktree, no staging. The user's canonical file is
  replaced in place.

### Why this is probably not what ultra-skills wants
The "shadow" here is the pseudocode file that shadows a source file — the
pseudocode is the user's intent artifact, transformed to code. It is **not**
an isolation mechanism for agent iteration. There is no parallel workspace,
no hidden runtime, no review gate. The user IS the gate (by writing the
pseudocode).

---

## Pattern B: Cursor "Shadow Workspace" — Hidden Parallel Environment

**Primary source:** https://cursor.com/blog/shadow-workspace (Arvid Lunnemark, Sept 2024)
**Reverse-engineering writeup:** https://chauyan.dev/en/blog/cursor-shadow-workspace-en
**Forum context:** https://forum.cursor.com/t/what-is-shadow-workspace/4308

### What it is
A hidden Electron window running the same workspace as the user's active
editor, used so AI agents can **iterate on code with full LSP and
runnability feedback** without mutating the user's visible state.

### Problem it solves
From Lunnemark's blog: *"naively letting AIs run loose in your folder
results in chaos: imagine writing out a reasoning-intense function only for
an AI to overwrite it, or trying to run your program only for an AI to
insert code that doesn't compile."* Design pursues six goals: LSP-usability,
runnability, independence from user, privacy (local-only), concurrency,
speed.

### Mechanics
- Spawn a hidden Electron window (`show: false`) for the workspace.
- AI edits flow: main-window renderer → main-window extension host → IPC
  (gRPC/buf) → shadow-window extension host → shadow-window renderer.
- Shadow window returns lints/diagnostics/errors via the same path.
- A separate language-server instance runs in the shadow window, which
  prevents the user's LSP from being contaminated by duplicate
  declarations, extra go-to-references hits, etc.
- Trade-off: ~2x memory. Mitigated by opt-in, extension-limiting, and
  15-min-idle auto-kill.

### Filesystem isolation (roadmap)
The hidden window handles **linting** but not **runnability** (executing
generated code). For runnability they explored a kernel-level folder proxy:
- Shadow folder A′ appears identical to user folder A for all FS-API
  readers, except for a small in-memory override table of AI-written files.
- Reads fall through to A; writes are captured in memory.
- Linux: FUSE. macOS/Windows: blocked by OS sandboxing ("walled gardens");
  macFUSE is unshippable. Apple's unreleased `FSKit` framework flagged as
  potential future path.
- `cp -r`, hardlink, symlink, and `cp -c` clonefile all rejected as too
  slow or too fragile (clonefile: "a `cp -c` clonefile takes 45 seconds ...
  too slow to be run before every shadow workspace request").

### Current status
Per community reverse-engineering, Shadow Workspace was **removed** from
Cursor's settings UI quietly. The speculated reason is the memory cost vs.
low opt-in rate, and a pivot toward git-worktree-based parallel agents
instead (Cursor 2.0 agents window).

---

## Pattern B' (live descendant): Git-Worktree Parallel Agents

The practical successor to Shadow Workspace is **one isolated git worktree
per agent**. This is what Cursor 2.0, Claude Code, and the "agentmaxxing"
community converged on.

### Mechanics (Claude Code, authoritative)
Source: https://code.claude.com/docs/en/common-workflows

- `claude --worktree <name>` (`-w <name>`) creates
  `<repo>/.claude/worktrees/<name>/` on a new branch `worktree-<name>`
  branched from `origin/HEAD`.
- Omitting the name auto-generates e.g. `bright-running-fox`.
- Subagents: `isolation: worktree` in agent frontmatter gives each its
  own worktree, auto-cleaned on exit if no changes.
- `.worktreeinclude` (gitignore syntax) copies `.env`-style files that
  tracked checkouts wouldn't carry.
- Recommend adding `.claude/worktrees/` to `.gitignore`.
- Exit: no changes → worktree + branch deleted. Changes exist → user
  prompted to keep or remove.
- Orphaned subagent worktrees swept at startup past `cleanupPeriodDays`,
  *only* if no tracked modifications and no unpushed commits.

### Community convention (digitalapplied.com, vibecoding.app)
- Directory naming: `<projectname>-<featurename>` (sibling dirs, not nested)
- Per-worktree port offsets (3001, 3002, 3003) via `.env.local`
- `.cursor/worktrees.json` describes per-worktree setup (npm install,
  migrations, env config) run on creation
- A shared `contracts.md` / `interfaces.ts` **before** fanout to prevent
  style drift
- Merge dependency order first (auth before payments), integrate daily,
  not at end-of-project

### Failure modes documented
- Parallel DB schema migrations create unresolvable conflicts — don't
  parallelize migrations
- Tightly-coupled features should not fan out
- Tasks <2h have a bad coordination-to-work ratio
- LSP/lint support is NOT currently available inside Cursor worktrees

---

## Ambiguity notes

- The `adifyr/shadow-code` repo and Cursor's "Shadow Workspace" share the
  word "shadow" but are unrelated. If the ultra-skills team specifically
  wants the `adifyr` repo's ideas, see Pattern A's "shadow syntax" and
  "selective context" (`context()`) as the reusable ideas.
- The ultra-skills task description ("agents operate on a parallel/isolated
  view of state while the user's canonical state stays untouched") matches
  Pattern B / B' much better than Pattern A.
- Shadow Workspace (Pattern B) was **removed from Cursor**; the live
  successor is worktree-based (Pattern B'). Any integration should
  probably target B' unless the team specifically wants the hidden-window
  architecture.

---

## Cited URLs
- https://github.com/adifyr/shadow-code
- https://cursor.com/blog/shadow-workspace
- https://chauyan.dev/en/blog/cursor-shadow-workspace-en
- https://forum.cursor.com/t/what-is-shadow-workspace/4308
- https://code.claude.com/docs/en/common-workflows
- https://www.digitalapplied.com/blog/multi-agent-coding-parallel-development
- https://vibecoding.app/blog/agentmaxxing
- https://claudefa.st/blog/guide/development/worktree-guide
