# Sources Consulted

## Primary (named repo)
- https://github.com/adifyr/shadow-code — `adifyr/shadow-code` v0.7.4, VS Code
  extension for pseudocode-to-code transform. Primary source. README +
  CHANGELOG + src/services/ai_service.ts + assets/prompts/system.md read.
- https://github.com/adifyr/shadow-code/blob/main/CHANGELOG.md — version
  history back to 0.3.2 (initial beta, Feb 2026). Confirms `import()` →
  `context()` rename at v0.7.2, skills system added v0.7.0.

## Cursor Shadow Workspace (the pattern ultra-skills likely wants)
- https://cursor.com/blog/shadow-workspace — Arvid Lunnemark's original
  Sept 2024 design doc. Authoritative for hidden-Electron-window
  architecture, LSP isolation rationale, FUSE/kernel-proxy roadmap,
  six design goals.
- https://chauyan.dev/en/blog/cursor-shadow-workspace-en — reverse-
  engineering writeup that confirms the architecture and reports Shadow
  Workspace was quietly removed from Cursor settings.
- https://forum.cursor.com/t/what-is-shadow-workspace/4308 — community
  thread confirming Shadow Workspace was only ever for internal features,
  never exposed as a user-controllable isolation primitive.

## Live successor: worktree-per-agent
- https://code.claude.com/docs/en/common-workflows — Claude Code's
  authoritative worktree docs. `--worktree <name>`,
  `.claude/worktrees/<name>/`, branch `worktree-<name>`, `.worktreeinclude`,
  subagent `isolation: worktree` frontmatter, cleanup rules.
- https://www.digitalapplied.com/blog/multi-agent-coding-parallel-development —
  community conventions: sibling-directory naming, per-worktree port
  offsets, `contracts.md`, merge-order rules, failure modes (DB migrations,
  style drift, late integration).
- https://vibecoding.app/blog/agentmaxxing — "agentmaxxing" pattern survey.
  Defines human-to-agent (vs agent-to-agent) parallelism, decomposition
  rules, per-worktree context requirements.
- https://claudefa.st/blog/guide/development/worktree-guide — Claude Code
  worktree conventions summary (paraphrased; cross-checked against
  official docs above).

## Added 2026-04-05 for architecture-spec-layer pivot

### Pseudocode / spec / ADR lifecycle
- https://en.wikipedia.org/wiki/Software_rot — software rot definition;
  brief "active rot" reference to documentation drift.
- https://en.wikipedia.org/wiki/Literate_programming — LP overview;
  maintainability argument ("inconsistencies would be almost impossible
  to prevent" if description and program are separate sources).
- https://www-cs-faculty.stanford.edu/~knuth/lp.html — Knuth's
  canonical page on literate programming.
- https://addyosmani.com/blog/good-spec/ — Addy Osmani on spec format
  and living-document lifecycle for AI-agent workflows.
- https://www.kinde.com/learn/ai-for-software-engineering/ai-devops/spec-drift-the-hidden-problem-ai-can-help-fix/ —
  spec drift as a first-class problem in AI-assisted development.
- https://github.com/bgervin/spec-kit-sync — tooling for detecting /
  resolving drift between specs and implementation.
- https://adr.github.io/ — canonical ADR home.
- https://github.com/joelparkerhenderson/architecture-decision-record —
  ADR templates; "Deprecated by YYY / Supersedes XXX" convention.
- https://github.com/pogopaule/architecture_decision_record/blob/master/adr_lifecycle.md —
  ADR lifecycle stages.
- https://medium.com/@nolomokgosi/basics-of-architecture-decision-records-adr-e09e00c636c6 —
  ADR status enum.

### Format / token efficiency / type-as-spec
- https://arxiv.org/html/2508.13666v1 — *The Hidden Cost of Readability*:
  code formatting costs ~24.5% of input tokens on average with
  near-zero frontier-model performance impact.
- https://xiaoningdu.github.io/assets/pdf/format.pdf — PDF version of
  the same study.
- https://betterstack.com/community/guides/ai/toon-explained/ — TOON
  token-efficient data format for LLM inputs.
- https://mattrickard.com/a-token-efficient-language-for-llms — essay
  on designing token-efficient languages for LLMs.
- https://wiki.haskell.org/Type_signature — Haskell type signatures as
  documentation/design.
- https://dev.to/gcanti/functional-design-algebraic-data-types-36kf —
  ADTs as domain model / specification.
- https://www.manning.com/books/type-driven-development-with-idris —
  Edwin Brady, *Type-Driven Development with Idris*.
- https://medium.com/@n.bergsma/on-applying-type-driven-development-with-domain-driven-design-5b3a21fca6d1 —
  TDD+DDD combination writeup.
- https://medium.com/@itsayu/understanding-typescript-interfaces-your-blueprint-for-better-code-18c7b4cc7953 —
  TypeScript interfaces as self-documenting blueprints.
- https://github.com/Reviewable/Reviewable/issues/465 — evidence for
  "header-first" review convention in C/C++ (~95% preference).
- https://en.wikipedia.org/wiki/Method_stub — method stub definition.
- https://www.cs.cornell.edu/courses/cs3410/2024fa/rsrc/c/header.html —
  Cornell CS 3410 on prototypes/headers as interface contracts.

### LLM-agent spec-first workflows
- https://arxiv.org/html/2506.13905v1 — Spec2RTL-Agent: pseudocode as
  intermediate between spec and code in LLM-agent pipelines.
- https://arxiv.org/html/2405.06907v1 — CoRE: LLM as interpreter for
  natural-language and pseudocode programming of AI agents.
- https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/ —
  draft-and-review agent patterns with LoopAgent quality gates.
- https://github.com/adifyr/shadow-code — (re-visited) Pattern A
  pseudocode-to-code extension; format clues drawn from README +
  `assets/prompts/system.md`.
- https://github.com/adifyr/shadow-code/blob/main/assets/prompts/system.md —
  system prompt confirming free-form pseudocode + `context()` + "DO NOT
  output any explanation" transform contract.
