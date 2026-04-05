---
name: ultra-design-artifacts
description: Use when a plan tree's INTERFACE.md files have stabilized and need visual representation for reviewer or stakeholder walkthrough, when ultra-planner dispatches its artifact-generation phase (Phase 4), or when architecture/dependency/sequence views are needed to validate the tree before leaf-plan writing. NOT for ad-hoc one-off diagrams (draw inline) and NOT for per-node clarification sketches (add to the node's NOTES.md instead).
---

# ultra-design-artifacts

## Overview

Generates a canonical artifact set — architecture diagram, dependency DAG, type/event matrix, sequence diagrams for top happy-paths, optional UI mockups — from a plan tree's stabilized INTERFACE.md files. Writes to canonical paths under `artifacts/` and updates `ROOT.md` with an index. Delegates cross-document consistency checks to `ultra-cross-doc-review` rather than re-implementing the 8-dimension checklist. Called by `ultra-planner` at the artifact-generation phase (Phase 4).

**Core principle:** Artifacts are derived views, not primary sources. Every artifact cites its source files and carries freshness metadata so a reviewer can tell at a glance whether it is stale. If the underlying contracts are inconsistent, diagram the inconsistency — do not paper over it.

## When to Use

| Signal | Use? |
|---|---|
| ultra-planner dispatches Phase 4 (artifacts) | Yes |
| INTERFACE.md files across the tree are stable (not churning) | Yes |
| Tree is being handed to a reviewer or stakeholder for walkthrough | Yes |
| UI-bearing nodes need a mockup or HTML demo for design validation | Yes |
| Single ad-hoc diagram for inline explanation | No — draw inline in chat |
| Per-node clarifying sketch | No — add to that node's NOTES.md |
| Contracts still changing every session | No — wait for stability, or diagram a snapshot and mark STALE |

## Procedure

Operate against a plan-tree root `docs/ultra-plans/<slug>/`. Do not skip or reorder.

1. **Check stability gate.** Read `SESSION.md` and every targeted node's `INTERFACE.md`. If INTERFACE.md files are marked draft, have changed in the last session, or the session log says contracts are still churning, STOP. Note in SESSION.md that artifact generation is deferred pending interface stability. Proceed only when interfaces are stable or user explicitly requests a snapshot.

2. **Delegate consistency check first.** Dispatch `ultra-cross-doc-review` against the plan tree (or the specific subtree being diagrammed). Wait for its REVIEW.md. Do NOT re-implement the 8-dimension checklist here. If the review emits BLOCKERs, either resolve them first (update SPEC/INTERFACE per the ADR patches) or diagram the tree with each BLOCKER called out as an explicit annotation on the affected edge/node. MAJORs get inline footnote annotations. MINORs can be ignored in the artifacts.

3. **Select format via decision table.** Pick per artifact type; record the choice and reasoning in an `APPROACH.md` alongside the artifacts:

   | Need | Preferred format | Criteria |
   |---|---|---|
   | Architecture + dep graph + sequence | mermaid | Renders in GitHub/IDEs; text-diffable; CLI validatable via `mmdc` |
   | Complex layered system / C4 | d2 or PlantUML | Better layout control; CLI validatable |
   | Cyclic graphs with custom layout | graphviz dot | Mature layout; ubiquitous CLI (`dot`) |
   | UI mockup | static HTML + CSS or SVG | Renders in any browser; no build step |
   | Fallback only | ASCII | When no renderer is available; lossy |

   Default to mermaid unless a criterion forces otherwise. State the chosen format and rejected alternatives in APPROACH.md.

4. **Produce the canonical artifact set.** At minimum, generate all five:
   - **Architecture diagram** — all nodes + external dependencies + edge types (call / event / data).
   - **Dependency DAG** — pure depends-on edges, topo-sorted, for cycle inspection at a glance.
   - **Type/event matrix** — table: row per type or event, columns for producer and consumers.
   - **Sequence diagrams** — one per top happy-path identified from SPEC.md goals (at least the primary flow; add secondary flows if distinct actors or branches).
   - **UI mockups** — for each node whose SPEC.md describes a user-facing surface, produce a static HTML or SVG mockup. Skip for pure backend nodes; note the skip in APPROACH.md.

5. **Embed freshness metadata in every artifact.** Header comment or footer containing: generation timestamp (ISO-8601), generating skill name + version, source-file list (relative paths from plan-tree root), and source git rev or a content hash of the source files. A reviewer must be able to answer "is this stale?" without reading the tree.

6. **Validate rendering before shipping.** Run the format's CLI validator against each file: `mmdc -i X.mmd -o X.svg` for mermaid, `dot -Tsvg X.dot -o X.svg` for graphviz, `d2 X.d2 X.svg` for d2. For HTML mockups, open in a headless browser or confirm it parses. If the validator is unavailable in the environment, note that in APPROACH.md and mark the artifact as UNVALIDATED. Syntax errors block shipping.

7. **Write to canonical paths.** Under `docs/ultra-plans/<slug>/artifacts/`: diagrams to `diagrams/`, UI mockups to `mockups/`, interactive HTML demos (e.g., an index page rendering all diagrams) to `demos/`. Do not write to `/tmp/` or task-dirs for real runs — only during RED/GREEN skill-testing.

8. **Update ROOT.md with the artifact index.** Append (or update) an `## Artifacts` section listing each artifact with its path, generation date, and one-line description. Reviewers land on ROOT.md first; they must find artifacts from there. Link the `demos/index.html` (or equivalent) as the primary entry point.

9. **Update SESSION.md.** Record last action (artifacts generated for nodes [list]), next planned action, and any BLOCKERs carried forward from the cross-doc-review that were diagrammed-as-annotated rather than resolved.

## Red Flags — STOP and self-correct

- Generating artifacts while INTERFACE.md files are still churning (stability gate skipped)
- Re-implementing a consistency checklist instead of dispatching `ultra-cross-doc-review`
- Picking mermaid (or any format) without stating criteria and rejected alternatives
- Shipping an artifact with no freshness metadata or no source-file citation
- Skipping CLI validation because "the syntax looks right"
- Writing artifacts to `/tmp/` or task-dirs during a real planner run
- ROOT.md not updated — reviewers cannot find the artifacts you produced
- Silently dropping a canonical artifact (e.g., no type matrix) without noting why in APPROACH.md
- Producing a UI mockup for a pure-backend node, or skipping mockups for a UI-bearing node without a stated reason
- Papering over a BLOCKER by redrawing edges to hide it instead of annotating the contradiction

## Common Mistakes

- **Artifact-as-source drift:** editing the diagram to patch a contract mismatch instead of fixing the INTERFACE.md. Artifacts are derived; sources are canonical.
- **Checklist duplication:** running a naming/cycle/interface-fit scan inline instead of delegating to `ultra-cross-doc-review`. The delegation is the discipline.
- **Format-by-reflex:** defaulting to mermaid without considering d2 / graphviz / PlantUML fit. State criteria, then pick.
- **No-metadata artifacts:** timestamp + source-list + source-rev is the minimum. Without it, reviewers cannot trust the artifact.
- **Validation-skipped:** shipping unrendered syntax. A typo invalidates the entire walkthrough.
- **Orphaned artifacts:** writing files under `artifacts/` without linking from ROOT.md. Reviewers will not find them.
- **Everything-in-one-diagram:** cramming architecture + sequences + types into one mermaid. Canonical set exists because each view answers a different reviewer question.
- **UI-mockup gate ignored:** producing mockups for every node, or none. The gate is "does SPEC describe a user-facing surface?"
