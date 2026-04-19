---
name: ultra-tui-iteration
description: Use when implementing or modifying a TUI (terminal user interface — Bubble Tea, Ratatui, Textual, Rich, Ink, tcell/tview) under TDD discipline, particularly when the worker is an AI agent that cannot see a real terminal, when rendering output is the surface being changed, or when an agent-readable feedback loop for visual regressions is required. NOT for non-TUI CLIs, NOT the TDD lifecycle itself (use ultra-test-driven-development), NOT general test-craft (use ultra-writing-tests).
---

# ultra-tui-iteration

## Overview

Domain reference for TUI work under ultra plan-tree execution. The agent cannot see the terminal, so every rendering claim must be exercised through a headless harness and asserted on a captured frame. This skill is loaded by `ultra-implementing-solo` / `ultra-implementing-team` / `ultra-writing-tests` only when the SUT is a TUI; otherwise inert.

**Core principle:** *Render is a pure function of state.* If `View(state)` is pure, you can drive it headlessly, capture the frame as a string, and assert on it like any other return value. If it isn't, fix the architecture before fixing the test.

## When to Use

| Signal | Use? |
|---|---|
| SUT is a TUI (Bubble Tea, Ratatui, Textual, Ink, tview, Rich) | Yes |
| Adding/changing rendering or input handling | Yes |
| Existing TUI has no rendering tests, only logic tests | Yes |
| Re-architecting hidden render-side state into the model | Yes |
| Plain CLI / non-TUI program | No — `ultra-writing-tests` |
| Bug is in the framework (e.g. Bubble Tea internals) | No — escalate |
| Discipline question (Iron Law, RED-verify) | No — `ultra-test-driven-development` |

## The architectural precondition

Before any TUI test will repay the effort, confirm the model conforms to the Elm Architecture (TEA): `Init() Cmd`, `Update(Msg) (Model, Cmd)`, `View() string`. **No I/O in `View`. No hidden state in the framework.** Ratatui's `StatefulWidget`, Textual's reactive properties, Ink's React state, and tcell's `SimulationScreen` all assume this. If the SUT renders inside `Update` or reads global state from `View`, refactor first — testing around impure render is testing the harness, not the code.

## Headless harness — by framework

Pick one. Do not roll a custom string-driver when the framework ships a harness.

| Framework | Harness | Drive input | Capture frame |
|---|---|---|---|
| Bubble Tea (Go) | `teatest.NewTestModel(t, m)` | `tm.Type("…")`, `tm.Send(Msg)`, `tm.WaitFor(...)` | `teatest.RequireEqualOutput(t, tm.Output())` (golden file via `-update`) |
| tview / tcell (Go) | `tcell.NewSimulationScreen("UTF-8")` | `screen.InjectEvent(NewEventKey(...))` | `cells, w, h := screen.GetContents()` |
| Ratatui (Rust) | `Terminal::new(TestBackend::new(80, 24))` | message into `Update` directly; or `ratatui-testlib` PTY harness | `terminal.backend().buffer()` + `insta::assert_snapshot!` |
| Textual (Python) | `async with app.run_test() as pilot:` | `await pilot.press("…")`, `pilot.click("#id")` | `app.save_screenshot()` (SVG) + `pytest-textual-snapshot.snap_compare` |
| Rich (Python) | `Console(record=True, force_terminal=True)` | n/a (render-only) | `console.export_text(styles=True)` / `export_html()` |
| Ink (TypeScript) | `render(<C/>)` from `ink-testing-library` | `stdin.write(...)`; `rerender(<C/>)` | `lastFrame()`; `expect(lastFrame()).toMatchInlineSnapshot()` |

Force a deterministic colour profile in CI (`tcell.Ascii` for tcell; SVG-only for Textual; TestBackend doesn't render colour). Otherwise golden files diff across environments.

## Default to snapshot/golden assertions

The cheap-feeling shortcut is `strings.Contains(view, "Search:")`. It cannot detect format drift, alignment regressions, off-by-one cursor placement, or accidental trailing whitespace — exactly the bugs an agent cannot eyeball. Snapshot/golden tests catch all of these in one assertion and update on intent (`go test -update`, `cargo insta review`, `pytest --snapshot-update`, `jest -u`). "Tedious to type the expected string" is rationalisation for skipping the strongest assertion the framework provides; the harness types it for you on first run.

**Inline snapshots are tier-1 equivalent.** When `-update` is impractical (sandboxed agent without toolchain access, CI-only pipeline, single-shot worker that cannot iterate the run-and-accept loop), inline string-literal snapshots (`expect(lastFrame()).toMatchInlineSnapshot(\`…\`)`, hand-built Go string-literal `t.Fatalf("--- want ---\n%s\n--- got ---\n%s")`) carry the same semantic strength as golden files and are colocated with the assertion. Prefer golden-file snapshots when you can run `-update`; reach for inline snapshots otherwise. Do not downgrade to substring assertions just because `-update` isn't reachable.

Mix strategies per case: snapshot for layout/format, structured assertion for one-line behaviour (cursor index, query text), state assertion for invariants (`m.cursor < len(m.filtered())`).

**When the test runner itself is unreachable** (sandboxed agent without toolchain, no `go`/`cargo`/`pytest`/`npm` available), do not skip RED-verify — substitute a **static RED-verify**: walk each test and confirm the failure mode would be a *compile-time* or *import-time* error against the unmodified SUT (e.g. references to fields/methods that don't yet exist on the model). For statically-typed frameworks (Bubble Tea, Ratatui, Ink+TS), the type checker is the test runner for the RED check; the failure is unambiguous "feature missing" rather than "typo." Document the substitution in your trace so a reviewer can audit. For dynamically-typed frameworks (Textual, Rich), static-RED is weaker — prefer arranging toolchain access over substituting.

## The cheapest agent-readable feedback move

Before any sophisticated tooling: dump `View(state)` (or one captured frame) to a file inside `/tmp` and `Read` it. This costs one line and gives you a sanity-check on shape — you'll spot empty-render, double-newline, missing status line in seconds. Do this once per major UI change, regardless of the test suite.

## When to reach for heavier tools

In order of cost; only escalate when text-level assertions plateau.

1. **Cell-level diff** between golden frames — when snapshots churn but you want to know *what changed*. Ratatui's buffer diff, `ansi-diff` (Node.js), or hand-rolled per cell.
2. **ANSI → image** (`termshot`, `termframe`, `svg-term`) — when colour/style is the surface and the harness can't assert on it. Use to seed a vision-API review pass.
3. **Vision-API review on the rendered image** — only after design has stabilised. Batch every 3–5 iterations, not every cycle. Tokens are ~10× a text assert.
4. **PTY automation (`agent-tui`, `MCP TUI Test`, `pyte`, `vt10x`, `@xterm/headless`)** — when you do **not** control the SUT (third-party CLI). Spawn under PTY, parse the cell grid, send keystrokes via JSON commands.

If you are reaching for #3 or #4 to test code you own, the architecture is wrong (impure View) or the snapshot suite is missing — fix that first.

## UX ambiguities → interview queue, not silent choice

Spec says "status line" and the position is unclear? Do not pick a side and write a test that passes either way. Log the question to `INTERVIEW_QUEUE.md` (or, in solo mode, to `SESSION.md`) under P1, default-attached. Snapshot-locking an arbitrary choice ossifies a decision the user never made.

## Stacking with other ultra-* skills

Test-craft rules from `ultra-writing-tests` still apply — fast-test budget (<100 ms per render assertion), behavior-not-mocks, no wall-clock assertions, helper extraction at second duplication, contract smoke tests for sibling consumers. This skill adds the TUI-specific harness, golden-file default, pure-View precondition, and tool-cost ladder. RED-verify (`ultra-test-driven-development`) is mandatory: run the new test against the unmodified TUI and confirm it fails for the right reason — "I assumed it would fail because the feature isn't there" is the canonical rationalisation this skill exists to prevent.

## Red Flags — STOP and fix

- Ran the TUI under a real terminal to "see" it instead of capturing a frame headlessly
- Wrote a custom string-parser helper to inspect `View()` output instead of using the framework's snapshot harness
- Skipped RED-verify on a render test because "the feature obviously doesn't exist yet"
- `View` reads from global state, time, or files — not pure
- `Update` performs I/O instead of returning a `Cmd`
- Snapshot golden file committed without reading it once
- Substring assertion (`Contains("Search:")`) covering a layout-sensitive change — drift will pass
- Untested rendering code shipped because "it's purely UX, a human will eyeball it" (no human is in the loop)
- Reaching for vision API before the snapshot suite is complete
- Picking one side of a UX ambiguity and writing a test that passes either way, instead of escalating
- Re-implementing a headless harness the framework already ships (custom `sendKey`/`visibleItems` helpers when `teatest`/Pilot/`ink-testing-library` exists)

## Common Mistakes

- **"Trust the framework, test only Update":** `Update` and `View` are both pure functions and both can break independently. Render bugs hide in `View`; only frame-capture catches them.
- **Substring-only assertions:** `strings.Contains(v, "Search:")` passes on `"SEARCH:"`, leading whitespace drift, status-line moved to the wrong section, and "Search:" appearing twice. Snapshot the section.
- **Custom heuristic parser of `View()`:** invents fragility (false positives, false negatives) that the framework's harness was built to avoid. Use the harness.
- **Eyeballed UX hint untested:** `(filter: X)` hint added "because it's nicer" with no test. If it isn't worth a test, it isn't worth shipping.
- **Single-frame snapshot for a flow:** capture frames at each step (`teatest.WaitFor` / `frames` array in ink / sequential `pilot.press` + `save_screenshot`) — flow tests need flow snapshots.
- **Ignoring colour profile / terminal size:** golden files diff between local and CI. Pin both in test setup.
- **Render-side state not in the model:** if a test cannot reproduce a visible bug by replaying the same `Msg` sequence, the bug-bearing state is hidden in the framework. Pull it into the model.
- **Vision-API as the primary loop:** burns tokens, batches poorly, hides regressions in summarisation. Snapshot first; vision only after stabilisation.

## References

- Elm Architecture / TEA — universal across frameworks; precondition for headless testing.
- `ultra-test-driven-development` — RED-GREEN-REFACTOR lifecycle, Iron Law, RED-verify mandate.
- `ultra-writing-tests` — test-craft (helper extraction, behavior-not-mocks, fast-test preference, contract smoke tests).
- `ultra-implementing-solo` / `ultra-implementing-team` — load this skill at task-start when the SUT is a TUI.
- `ultra-context-hygiene` — when the rendered frame or snapshot file is large, read narrowly; do not dump multi-MB ANSI logs into the main session.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
