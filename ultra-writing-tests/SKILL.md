---
name: ultra-writing-tests
description: Use when writing test code during a leaf PLAN.md task, when ultra-implementing-solo/team dispatches a RED test, when adding contract smoke tests per sibling consumer, or when extending an existing test file. Covers test-craft (fast-test preference, test doubles, determinism, helper extraction, organization). NOT for WHEN to write tests (use ultra-test-driven-development) and NOT for running/dispatching tests (use ultra-implementing-solo/team).
---

# ultra-writing-tests

## Overview

Test-craft discipline for workers writing test code under ultra plan-tree execution. Assumes `ultra-test-driven-development` enforces the RED-GREEN cycle; this skill covers WHAT makes the test itself correct, fast, and honest: behavior-not-mocks, deterministic time, real sibling types, contract smoke tests, tiering, helper discipline.

**Core principle:** A test is a claim about observable behavior, pinned to a real contract. If it asserts on call counts, wall-clocks, or locally-redefined types, the claim is about the harness — not the code.

## When to Use

| Signal | Use? |
|---|---|
| Worker dispatched to write the RED test for a PLAN.md task | Yes |
| Adding a contract smoke test per sibling consumer | Yes |
| Extending an existing test file past 2 similar cases (helper extraction) | Yes |
| Reviewing test drift during `ultra-shadow-drift` test-complicity dimension | Yes |
| Deciding WHEN to write a test | No — `ultra-test-driven-development` |
| Running tests / orchestrating the suite | No — `ultra-implementing-solo` / `ultra-implementing-team` |
| Cutting scope from a test list | No — `ultra-scope-pruning` / `ultra-yagni` |

## Techniques

1. **No testability-only parameters in production.** `octokit?`, `clock?`, `fetch?` as a trailing optional arg "for tests" is a leaky seam. DI belongs at module construction (factory, constructor, closure) — not every caller's API.

2. **Assert on observable output, not mocks.** Avoid `toHaveBeenCalledTimes(N)` / `toHaveBeenCalledWith(...)` except for side-effect-only code (logging, metrics, fire-and-forget). Tests read like the caller: "given input X, output is Y." Call-shape assertions break on innocent refactors.

3. **Import cross-node types verbatim from sibling INTERFACE.md.** Never re-declare `PRRecord`, `FetchError`, etc. locally. Redefined types make contract drift invisible. SUT-local redefinition is a drift report, not a shortcut.

4. **Fake the clock for time-sensitive logic.** Rate-limit resets, timeouts, retries, debounces, TTLs — use fake timers (`vi.useFakeTimers()` / equivalent). Never assert on `Date.now()` deltas.

5. **Behavior-named; scope per case.** `test('returns empty array for empty repo')` beats `test('test_fetchPRs_1')`. Name by behavior / journey, never by method signature. For scope (one behavior vs flow), see "Flow-covering vs narrow-unit" — dogmatic one-behavior-per-test is wrong for flows.

6. **Extract helpers at the second duplication.** Copy-paste a fixture or context-builder (auth'd user, test DB, fake clock, seeded repo) twice → extract to `test-helpers.ts` / `fixtures/`. Third copy is a red flag. Tests are code — refactor with production-code taste.

7. **Cover boundary, null, and state-derived cases.** Off-by-one at page boundaries (exactly `PER_PAGE` → next page empty). Null/missing fields (`user: null`). State-derived fields (`merged` = `state === "closed" && merged_at !== null`). Where real bugs hide; where naive suites skip.

8. **Tight, measured timing assertions.** Code runs in <50ms → assert `< 100ms`, not `< 5000ms`. Measure once, set to ~2x. Per-test timeouts (`{ timeout: 200 }`) on time-sensitive tests.

9. **Tier tests: unit / integration / e2e as separate targets or tags.** Unit by default; integration + e2e behind `@integration` / `@slow` tags or separate scripts (`test:unit`, `test:integration`). Flag-gate by default.

## Fast-test preference

> **Default to fast tests — unit <100ms, integration <1s — so the RED→GREEN loop stays tight. Context-dependent: crypto, distributed-systems, network-bound, and chaos suites may legitimately run longer. When a test must exceed the budget, isolate it behind a tag (e.g. `@slow`, `@integration`) or a separate target, and document the reason in the test file or suite README. Slow-by-default suites corrode the discipline.**

Targets are aspirational but firm: a unit suite that creeps to 5s per test normalizes non-response, and workers stop running it mid-task. If a specific domain (crypto key derivation, distributed-consensus fixture, chaos injection) cannot hit the budget, tag and isolate — don't slow everything down to accommodate it.

## Flow-covering vs narrow-unit — choose per case

Classical TDD's "one behavior per test, no AND in the name" is correct for isolated unit logic (parsers, pure functions, validators). It is **wrong** for complex flows. For flows, prefer ONE well-named flow test that exercises multiple behaviors on one causal path — it mirrors real usage, avoids rebuilding shared setup, and surfaces integration bugs that narrow-unit slices miss.

| Situation | Prefer |
|---|---|
| Pure function, single branch, isolated validator | Narrow unit — one behavior per test |
| Multi-step user journey (signup → verify → first-action) | Flow test — one well-named test covering the path |
| Causally-linked steps (create → read → update → list) | Flow test — splitting hides the causal chain |
| Parametric edge cases over one unit | Narrow unit, parameterized |
| End-to-end integration across 2+ modules | Flow test, tag-gated |

**Flow tests depend on strong fixtures.** Setup (auth'd user, test DB, fake clock, seeded repo) lives in reusable helpers / named fixtures, not copy-pasted. Flow tests without fixtures degenerate into giant setup blocks; narrow tests with inline setup degenerate into copy-paste sprawl. Helpers are non-optional in both modes.

**Rule of thumb:** choose per case. Narrow for narrow logic, flow for flows. Name by the journey / observable behavior: `"new user can complete first-action after signup"`, not `"test_createUser_AND_verifyEmail_AND_postTask"`.

## Contract smoke tests

Every leaf PLAN.md requires **one contract smoke test per distinct sibling consumer**, as the final task(s) of the plan (see `ultra-writing-plans`). Craft rules:

- **Import types verbatim** from the consumer's `INTERFACE.md`-cited source path. Stale or unreachable → escalate per `ultra-implementing-solo`/`ultra-implementing-team`; do not invent.
- **Fake the consumer, feed real SUT output.** Minimal fake matching the consumer's expected input signature; pipe this node's actual output in; assert the fake received well-formed data under the consumer's type.
- **Assert shape AND values.** Pure type-check (`satisfies Consumer.Input`) is not enough — add at least one value assertion proving semantic correctness.
- **One smoke test per consumer.** Distinct consumers catch distinct drift.

## Test-complicity guard

A test that passes *because* it fails to assert on missing behavior is **complicit drift** — see `ultra-shadow-drift` Dimension 7. Self-check before commit:

- Does this test assert on every field the SPEC names?
- If I delete the assertion body, does RED still fire? If not, the assertion is load-bearing for nothing.
- Does the test still pass if I mutate the SUT to return stubbed data? Green = complicit.

Complicit tests auto-bump one severity tier in `ultra-shadow-drift` drift reports. Avoid writing them.

## Red Flags — STOP and fix

- Added `foo?: Foo` parameter to production signature purely for test injection
- `toHaveBeenCalledTimes(N)` / `toHaveBeenCalledWith(...)` on non-side-effect code
- Imported `PRRecord` / `FetchError` / any cross-node type from the SUT's own file instead of the sibling `INTERFACE.md`-cited path
- Asserted on `Date.now()`, wall-clock delta, or real elapsed time
- Missing fake timers on rate-limit / retry / timeout / debounce logic
- Timing assertion set to `< 5000ms` when the code runs in <50ms
- No per-test timeout on time-sensitive tests
- Flat `describe` with 10+ tests, no nesting, no helpers extracted
- Test name describes the method signature instead of the journey / observable behavior (e.g. `test_fetchPRs_1`, `test('calls_octokit_pulls_list')`)
- Splitting causally-linked behaviors into separate tests when one flow test would mirror real usage (e.g. `createUser` / `verifyEmail` / `firstAction` as three isolated tests instead of one "new user completes first-action after signup")
- Inline setup (auth'd user, test DB, fake clock, seeded repo) duplicated across 3+ tests without extraction to a helper or named fixture
- Integration test runs by default (not tag-gated, not in separate target)
- Locally redefined cross-node type instead of importing it
- Contract smoke test asserts only types, no values

## Common Mistakes

- **Testability parameter creep:** `fetchPRs(repo, since, octokit?)` leaks a test seam into every caller. Use factory/constructor injection; keep per-call signatures caller-focused.
- **Mock-behavior tests:** `expect(octokit.pulls.list).toHaveBeenCalledTimes(3)` tests the mock, not the code. Assert on the returned `PRRecord[]` — pagination bugs show up in output.
- **Wall-clock flakiness:** `expect(Date.now() - start).toBeLessThan(1000)` is the flakiest assertion in software. Fake timers, advance by known amounts.
- **Duplicate-type drift:** SUT re-declares `PRRecord` locally, test imports from SUT, sibling `INTERFACE.md` silently drifts. Import from the `INTERFACE.md`-cited path; SUT redefinitions are drift reports, not shortcuts.
- **Loose timing budgets:** `< 5000ms` passes even when code is 50x slower. Measure once; set to ~2x measured.
- **Flat test files + inline setup sprawl:** 11 tests under one `describe`, fixtures copy-pasted. Extract at second duplication; nest `describe` by behavior family. Tests are code — refactor with the same taste as production.
- **Narrow-slicing flows:** `createUser` / `verifyEmail` / `firstAction` split into three isolated tests with duplicated setup, instead of one `"new user completes first-action after signup"` flow test with a shared fixture.
- **Missing boundary cases:** page-returns-exactly-PER_PAGE, `user: null`, state-derived fields like `merged` from `state + merged_at`. Where real bugs hide; where naive suites skip.
- **Contract test as afterthought:** one integration test at the end with self-chosen shapes, instead of per-consumer tests matching each consumer's exact `INTERFACE.md` signature.
- **Complicit green:** test passes because it never asserted on the missing field. Mutate the SUT to stub data — does the test catch it?

## Reference

- `ultra-test-driven-development` — WHEN/HOW to apply the RED-GREEN-REFACTOR cycle; this skill is WHAT makes the test itself good.
- `ultra-writing-plans` — emits PLAN.md tasks requiring per-consumer contract smoke tests as final tasks; this skill tells you how to craft them.
- `ultra-shadow-drift` — Dimension 7 test-complicity; complicit tests auto-bump one severity tier in drift reports.
- `ultra-implementing-solo` — solo executor that dispatches RED tests per task; load this skill at test-writing time.
- `ultra-implementing-team` — leader + workers; workers should load this skill when their brief is to write a test.
- `superpowers:test-driven-development` — parent discipline; `testing-anti-patterns.md` (in that skill's dir) covers mock-behavior anti-patterns in more depth.
