# Shadow-Code Format Comparison

**Research question:** What shadow-code format is most efficient for an
LLM to generate AND review, and then translate faithfully to typed real
code?

Six candidates evaluated against six criteria, then a recommendation and
a worked example.

---

## Candidates

### C1: TypeScript-like (types + signatures + `// ...` stubs)

```ts
type DigestInput = { messages: Message[]; since: Date; userId: UserId };
type DigestError = "NoMessages" | "UserNotFound" | "RateLimited";
type DigestResult = { summary: string; tokensUsed: number };

function generateDigest(input: DigestInput): Result<DigestResult, DigestError> {
  // validate input.userId against UserRepo
  // fetch messages since input.since
  // if empty → Err("NoMessages")
  // call LLM summarizer with message batch
  // return Ok({ summary, tokensUsed })
}
```

Familiar, ADT-ish via unions, portable signatures.

### C2: Haskell-like (type signatures + equations + ADTs)

```haskell
data DigestError = NoMessages | UserNotFound | RateLimited
data DigestInput = DigestInput { messages :: [Message], since :: UTCTime, userId :: UserId }
data DigestResult = DigestResult { summary :: Text, tokensUsed :: Int }

generateDigest :: DigestInput -> IO (Either DigestError DigestResult)
generateDigest input = do
  -- validate userId
  -- fetch messages since `since`
  -- empty ==> Left NoMessages
  -- summarize ==> Right DigestResult {..}
```

Densest. ADTs first-class. Most foreign to target-language translation.

### C3: Python type hints + stub bodies

```python
DigestError = Literal["NoMessages", "UserNotFound", "RateLimited"]

class DigestInput(TypedDict):
    messages: list[Message]; since: datetime; userId: UserId

def generate_digest(input: DigestInput) -> Result[DigestResult, DigestError]:
    ...  # validate userId
    ...  # fetch messages since input.since
    ...  # empty -> Err("NoMessages")
    ...  # summarize -> Ok(DigestResult(...))
```

Familiar, but `TypedDict`/`Literal`/`Result` ceremony is noisy.

### C4: Idris/Agda-style dependently-typed signatures

```idris
generateDigest : (input : DigestInput)
              -> { auto userExists : UserExists input.userId }
              -> IO (Either DigestError DigestResult)
```

Maximum rigor, maximum foreignness. LLM training data is thin.

### C5: Custom minimal DSL (exports + signatures + dataflow)

```
module DigestGen
exports: generateDigest
types:
  DigestInput    = { messages: [Message], since: Date, userId: UserId }
  DigestError    = NoMessages | UserNotFound | RateLimited
  DigestResult   = { summary: String, tokensUsed: Int }
fn generateDigest(input: DigestInput) -> Result<DigestResult, DigestError>
  flow:
    input.userId -> UserRepo.lookup -> ?UserNotFound
    input.since  -> MessageRepo.since -> messages
    messages == [] -> !NoMessages
    messages -> LLMSummarizer.summarize -> (summary, tokens)
    -> Ok { summary, tokensUsed: tokens }
```

Token-efficient, editable. But: invented syntax, no LLM training prior.

### C6: Module-diagram notation (Alloy / PlantUML / D2)

```
DigestGen --> UserRepo : lookup(userId)
DigestGen --> MessageRepo : since(date)
DigestGen --> LLMSummarizer : summarize(messages)
```

Best at visual module graphs. Worst at capturing types and control flow
inside a function.

---

## Evaluation matrix

Scoring 1-5 (5 best). Reasoning in the footnotes.

| Criterion                    | C1 TS | C2 Haskell | C3 Python | C4 Idris | C5 DSL | C6 Diagram |
|---|---|---|---|---|---|---|
| Token density [¹]            | 4     | 5          | 3         | 5        | 5      | 3          |
| Human reviewability [²]      | 5     | 3          | 5         | 2        | 4      | 3          |
| LLM reviewability [³]        | 5     | 4          | 4         | 3        | 3      | 2          |
| Typed-target fidelity [⁴]    | 5     | 4          | 4         | 3        | 3      | 2          |
| Untyped-target fidelity [⁵]  | 5     | 3          | 5         | 2        | 4      | 3          |
| Bug-catching at format level [⁶] | 4 | 5          | 3         | 5        | 3      | 2          |
| LLM training density [⁷]     | 5     | 4          | 5         | 2        | 1      | 3          |
| **Weighted score**           | **33**| **28**     | **29**    | **22**   | **23** | **18**     |

Footnotes:
- [¹] Bytes/tokens per unit-of-architecture captured. Haskell and Idris
  win on type density; diagrams waste tokens on graph syntax.
- [²] Does an average reviewer parse this fast? TS/Python win via
  ubiquity. Haskell/Idris lose on audience fit.
- [³] Can an LLM reviewer extract the architecture reliably? TS wins on
  training-data density. DSLs and diagrams lose.
- [⁴] Mapping shadow shapes → TypeScript/Rust/Go/Java signatures.
  TS-shaped shadow has nearly 1:1 translation to TS/Java/Go/Rust,
  modulo the Result/union mapping.
- [⁵] Mapping shadow shapes → JS/Ruby. TS and Python are closest to
  common dynamic-target idioms. Haskell is furthest.
- [⁶] Does the format itself surface architecture bugs? Typed ADTs
  catch missing-case / mismatched-shape bugs at format-write time.
  Haskell/Idris win; stubs without ADTs lose.
- [⁷] How much training data does the LLM have in this format?
  TS/Python saturate. Idris is rare. Invented DSLs are absent.

---

## Supporting evidence from external research

- **LLMs tolerate compact/unformatted code well.** The arxiv study
  *The Hidden Cost of Readability* ([2508.13666](https://arxiv.org/html/2508.13666v1))
  finds input-token reductions of 24.5% average (up to 34.9% for Java)
  by stripping formatting, with near-zero performance drop for
  frontier models. Implication: we do not need to worry about dense
  Haskell-like shadow being unreadable by the LLM. Human review is the
  bottleneck, not LLM comprehension.
- **Types-as-design is a live tradition.** Type-driven-development
  literature (Edwin Brady's
  [*Type-Driven Development with Idris*](https://www.manning.com/books/type-driven-development-with-idris),
  the
  [HaskellWiki on type signatures](https://wiki.haskell.org/Type_signature),
  Gabriel Canti's
  [Functional design: ADTs](https://dev.to/gcanti/functional-design-algebraic-data-types-36kf))
  consistently argues that typed signatures + ADTs act as
  specifications that catch architecture bugs before code is written.
  Implication: shadow format should prioritize typed ADTs over
  untyped stubs.
- **Header-first convention.** C/C++ reviewers read headers before
  implementation ~95% of the time
  ([Reviewable issue #465](https://github.com/Reviewable/Reviewable/issues/465)).
  Implication: a shadow that reads like a header file is a known-
  familiar reviewer affordance.
- **TypeScript interfaces as "blueprint."** Interfaces "make your code
  self-documenting" with compiler-enforced accuracy
  ([ayush kumar tiwari on Medium](https://medium.com/@itsayu/understanding-typescript-interfaces-your-blueprint-for-better-code-18c7b4cc7953)).
  Implication: TS is culturally positioned as a spec format.
- **adifyr/shadow-code's own format choice** is intentionally free-form
  pseudocode with only `context()` reserved. The README encourages
  users to invent their own "shadow syntax" ("your own personal coding
  language"). Implication: there is no established shadow-pseudocode
  format to inherit — we are free to pick.

---

## Recommendation: **TypeScript-like with strong ADT bias** (C1+)

Use TypeScript-as-shadow-language as the default format, deliberately
leaning into ADT/union patterns. Specifically:

1. **Types and signatures in TypeScript syntax.** Discriminated unions
   for error enums and state machines. Type aliases for domain concepts.
2. **Function bodies as `// ...` comments describing control flow,**
   one control-flow step per line. Prefix error paths with `// !Err:`
   and happy-path outputs with `// =>`.
3. **`context(...)` header at the top** of each `.shadow` file citing
   dependencies (inherited from Pattern A).
4. **Cross-module calls as real TypeScript calls** using imports of
   the types defined in sibling shadows: `UserRepo.lookup(userId)`.
5. **No real executable bodies.** Bodies are always stubbed. Enforce
   with a lint that fails if any shadow file has a non-comment
   function body.

This scored highest on the weighted matrix, has the strongest LLM
training-data prior, reads well for humans, translates cleanly to TS,
Go, Rust, Java, Python, Ruby, and JS, and gets most of Haskell's
bug-catching power via discriminated unions + exhaustive `switch`
narrowing.

### When to use alternates

- **Use C2 (Haskell-like)** when the leaf is heavy on algebraic
  transformations, typeclass-style polymorphism, or has a reviewer
  who is a Haskeller and will catch more bugs in that form. Rare.
- **Use C3 (Python type hints)** when the target language is Python
  AND the reviewing audience is Python-first. The TS→Python
  translation step is tiny, so sticking with TS is usually fine.
- **Use C6 (diagram notation)** as a *companion* to the TS shadow
  when module count at a leaf exceeds 6-8 and the architecture
  diagram itself is the review target. Do NOT use diagrams alone;
  they cannot carry types and control flow.

---

## Worked example: team-dashboard digest-generator leaf

File: `nodes/digest-generator/SHADOW/digest.shadow`

```ts
context(
  "../../INTERFACE.md",
  "../user-store/INTERFACE.md",
  "../message-store/INTERFACE.md",
  "../llm-summarizer/INTERFACE.md"
)

import type { UserId } from "../user-store/INTERFACE.md"
import type { Message } from "../message-store/INTERFACE.md"

export type DigestInput = {
  userId: UserId
  since: Date
  maxMessages: number
}

export type DigestError =
  | { kind: "UserNotFound"; userId: UserId }
  | { kind: "NoMessages"; since: Date }
  | { kind: "RateLimited"; retryAfterMs: number }
  | { kind: "SummarizerFailed"; reason: string }

export type DigestResult = {
  summary: string
  messageCount: number
  tokensUsed: number
  generatedAt: Date
}

export async function generateDigest(
  input: DigestInput
): Promise<Result<DigestResult, DigestError>> {
  // UserRepo.lookup(input.userId)
  // !Err: UserNotFound when lookup returns null
  // MessageRepo.since(input.userId, input.since, limit=input.maxMessages)
  // !Err: NoMessages when messages is empty
  // LLMSummarizer.summarize(messages, { style: "digest" })
  // !Err: RateLimited pass-through from summarizer
  // !Err: SummarizerFailed wrap any other summarizer error
  // => Ok { summary, messageCount: messages.length, tokensUsed, generatedAt: now() }
}
```

What this 20ish lines already catches at review time:
- Every error case is named with its payload — reviewer can ask "what
  does the caller do with `retryAfterMs`?"
- `maxMessages` surfaced as input, not buried; reviewer can ask "who
  sets this?"
- Cross-module calls are named (UserRepo, MessageRepo, LLMSummarizer),
  with their INTERFACE.md files in `context()`, so shadow-review can
  verify signatures line up.
- Control flow is one-step-per-line, so missing error paths (e.g.
  forgot to handle rate-limiting) are visible at a glance.

This is the review affordance the shadow format is for.
