---
name: ultra-test-driven-development
description: Use when implementing any feature or bugfix before writing production code, when executing a per-task TDD cycle inside a leaf PLAN.md, when reproducing a bug, or when `ultra-implementing-solo` / `ultra-implementing-team` dispatches a RED-GREEN-REFACTOR step. NOT for "WHAT makes a good test" (use `ultra-writing-tests` for craft concerns — fast-test discipline, test doubles, organization) and NOT for throwaway prototypes or generated code.
---

# ultra-test-driven-development

## Overview

Write the test first. Watch it fail. Write minimal code to pass. Refactor. Repeat. This is the per-task cycle that `ultra-writing-plans` structures PLAN.md tasks around, and that `ultra-implementing-solo` / `ultra-implementing-team` enforce at runtime.

**Core principle:** If you did not watch the test fail, you do not know if it tests the right thing. Violating the letter of the rule is violating the spirit of the rule.

## When to Use

| Signal | Use? |
|---|---|
| Implementing any new feature or behavior | Yes |
| Fixing a bug (write failing test that reproduces, then fix) | Yes |
| Refactoring — change behavior via tests first | Yes |
| Executing a task inside a leaf PLAN.md (solo or team) | Yes |
| Throwaway prototype you will delete | No |
| Generated code / config files | No |
| Pure documentation edits | No |

Thinking "skip TDD just this once"? That is rationalization. Return to the cycle.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? **Delete it. Start over.** Do not keep it as "reference". Do not "adapt" it while writing tests. Do not look at it. Delete means delete. Implement fresh from the test.

## RED-GREEN-REFACTOR

```
RED -> verify RED -> GREEN -> verify GREEN -> REFACTOR -> next task -> RED
         |                         |              |
         wrong failure             fails          must stay green
         -> rewrite test           -> fix code    -> no behavior change
```

### RED — write the failing test

Clear name, real code. Avoid mocks unless unavoidable. In ultra plan-tree contexts, **import real types from sibling `INTERFACE.md`** — never re-derive a shape from a task description.

**Granularity is per-case** (see Good Tests below): narrow unit logic → one behavior per test; complex flow → one flow per test, named by the journey, covering multiple causally-linked behaviors with shared setup.

Good (narrow): `test('retries failed operations 3 times', ...)` — one behavior, real code.
Good (flow): `test('new user can verify email, log in, and complete first action', ...)` — causally linked journey, named by the user path.
Bad: `test('retry works', ...)` that asserts only on a mock's call count — vague name, tests the mock not the code.

### Verify RED — watch it fail (MANDATORY)

Run the test. Confirm it **fails**, the failure message matches what you expected, and it fails because the feature is missing (not a typo or bad import).

- Passes on first run? You are testing existing behavior. Rewrite.
- Errors instead of failing? Fix and re-run until it fails cleanly.

### GREEN — minimal code

Write the simplest code that makes the test pass. No speculative options, no extra fields, no "while I'm here" refactors in other files.

### Verify GREEN — watch it pass (MANDATORY)

Run the targeted test AND the full suite. New test passes, previously-passing tests still pass, output is pristine (no new warnings, no stack traces).

- Target fails? Fix the code, not the test.
- Other tests fail? Fix now, before REFACTOR.

### REFACTOR — clean up under green

Remove duplication, improve names, extract helpers. Do not add behavior. Do not loosen assertions. Stay green on every edit.

## Fast-test preference

Default to fast tests — unit <100ms, integration <1s — so the RED→GREEN loop stays tight. **Context-dependent:** crypto, distributed-systems, and network-bound suites may legitimately run longer. When a test must exceed the budget, isolate it behind a tag (e.g. `@slow`) or a separate target, and document the reason in the test file or suite README. Slow-by-default suites corrode the discipline.

## Good Tests

Pick granularity per-case. **Don't dogmatically prefer flows, and don't dogmatically split either.** The classical "one behavior, no AND in name" rule applies to isolated unit logic; it is WRONG for flows.

| Kind | When to use | Good example | Bad example |
|---|---|---|---|
| **Narrow** (one behavior per test) | Isolated unit logic: pure functions, validators, parsers, edge-case branches | `test('rejects empty email')` | `test('test1')`; asserts on private state |
| **Flow** (one journey per test) | Complex flows with causally-linked steps and shared setup — mirrors real usage | `test('new user can verify email, log in, and complete first action')` | Five narrow tests each rebuilding the same signup fixtures |

Shared qualities for both kinds:

- **Clear name.** Describes the journey or observable behavior, not the function call. `test('test1')` / `test('works')` are always bad.
- **Shows intent.** Demonstrates the desired API from the caller's view; does not mirror the implementation or assert on private state.
- **Causally linked (for flows).** "AND" in a flow name is fine when the behaviors share a causal path and realistic setup. Split only if the behaviors are independent or the flow is masking a broken narrow unit.

Test-craft details — fixtures, helpers, doubles, flow-vs-narrow heuristics, suite organization — live in `ultra-writing-tests`. This skill owns the lifecycle (RED → verify → GREEN → verify → REFACTOR); `ultra-writing-tests` owns what goes inside each test.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests written after pass immediately — prove nothing. |
| "Tests-after achieve the same thing" | After: "what does this do?" First: "what SHOULD this do?" |
| "I already manually tested it" | Ad-hoc ≠ systematic. No record. Cannot re-run. |
| "Deleting X hours is wasteful" | Sunk cost. Untrustworthy code is the real waste. |
| "Keep as reference while I write tests" | You'll adapt it. That's tests-after. Delete means delete. |
| "Need to explore first" | Fine. Throw away the exploration. Restart with TDD. |
| "Hard to test" | Hard-to-test = hard-to-use. Simplify the interface. |
| "TDD will slow me down" | Debugging untested code is slower. |
| "This is different because…" | It is not. Back to RED. |
| "The sibling INTERFACE.md probably has that field" | Open the file. Missing? File an amendment (see `ultra-writing-plans`). Do not invent. |

## Red Flags — STOP and start over

- Code written before a test
- Test written after the implementation
- Test passes on first run
- Cannot explain why the test failed
- "I'll add tests later" / "just this once"
- "Keep as reference" / "adapt existing code"
- "TDD is dogmatic, I am being pragmatic"
- "This case is different because…"
- Mock-assertion-only test (no real behavior exercised)
- Test uses a cross-node type you re-derived from a PLAN.md description

**All of these mean: delete the code, return to RED.**

## Verification Checklist

Before marking a task complete:

- [ ] Every new function has a test.
- [ ] Each test was watched failing before implementation.
- [ ] Each test failed for the expected reason (missing feature, not typo).
- [ ] Minimal code was written to pass.
- [ ] Full suite passes; output is pristine.
- [ ] Tests use real code; mocks only where unavoidable.
- [ ] Edge cases and error paths covered.
- [ ] Cross-node types imported verbatim from sibling `INTERFACE.md` (plan-tree only).

Cannot tick all boxes? The task skipped TDD. Start over.

## When Stuck

| Problem | Solution |
|---|---|
| Don't know how to test it | Write the wished-for API first; assertion before arrange. Queue an interview item if truly ambiguous. |
| Test too complicated | Design is too complicated. Simplify the interface. |
| Have to mock everything | Code is too coupled. Introduce dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify the design. |
| Bug found mid-implementation | Write a failing test reproducing it. The test proves the fix AND prevents regression. |

Never fix a bug without a test.

## Contract smoke tests (plan-tree boundary)

`ultra-writing-plans` requires a **per-consumer contract smoke test** as the final task(s) of every leaf PLAN.md — one test per sibling consumer, feeding this node's output through a fake of that consumer's expected input signature. TDD at the boundary layer. Same cycle. Types imported verbatim from the consumer's `INTERFACE.md`.

## Final Rule

```
Production code → test exists and failed first
Otherwise → not TDD
```

No exceptions.

## References

- `ultra-writing-tests` — WHAT makes a good test (craft): fast-test discipline, doubles, suite organization. This skill is WHEN/HOW to apply the cycle.
- `ultra-implementing-solo` — per-task TDD in solo (no-dispatch) environments, with SESSION.md discipline.
- `ultra-implementing-team` — per-task TDD in leader+workers environments, under file-ownership discipline.
- `ultra-writing-plans` — emits PLAN.md tasks as RED-GREEN-REFACTOR steps; requires per-consumer contract smoke tests.
- `superpowers:test-driven-development` — parent discipline; this skill is its ultra-* port.

```!
[ -d ~/src/ultra-skills ] && printf '\n---\n*Dogfooding: patch this skill in place when you find gaps.*\n'
```
