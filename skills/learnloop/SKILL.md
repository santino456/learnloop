---
name: learnloop
description: Work with LearnLoop local-first adaptive learning courses. Use when creating or updating LearnLoop course source, generating trustworthy AI-assisted tutorials, choosing Tutorial/Reference/Practice/Perspective content forms, validating course claims and sources, answering saved learner questions from questions.jsonl, or improving modules based on learner confusion.
---

# LearnLoop

LearnLoop turns raw material into a local, verifiable learning loop:

```text
sources + learner goal -> Markdown/YAML course -> local HTML -> questions -> agent context -> improved source
```

Your first job is **epistemic control**, not fast drafting. A fluent lesson is not good enough unless the learner goal, sources, evidence, content forms, and validation state are clear.

## Task Router

- **Answer learner question**: read `references/answering-loop.md`, run `learnloop context`, write an answer artifact, and update course source only if the answer should be reused.
- **Small course edit**: inspect the target module, preserve section ids, make the narrow edit, then run `learnloop validate` and `learnloop build`.
- **New or substantial course generation**: follow the stage gates below before writing `modules/*.md`.
- **Publication or reusable course**: also read `docs/content-forms.md`, `docs/evidence-and-sources.md`, `docs/course-quality.md`, and `references/content-verification.md`; run `learnloop audit`.

## Stage Gates

Before drafting a new or substantial course, produce these notes. For quick personal work they may stay in the response; for reusable technical courses persist them in `.learnloop/`.

1. **Intent**: learner goal, background, desired outcome, exclusions.
2. **Research**: sources used or needed; reliability tier; missing sources.
3. **Evidence**: supported facts, useful examples, weak/conflicting points.
4. **Design**: module plan and why each content form is justified.
5. **Draft**: write only content supported by the design and evidence.
6. **Review**: check unsupported claims, fake Reference, weak Practice, empty Perspective, private examples, and section id stability.
7. **Build**: run validate/build/audit as appropriate.

Do not write a long module before Intent, Research, Evidence, and Design exist.

## Content Form Rules

- **Tutorial** explains concepts and mental models.
- **Reference** is only for dense reusable lookup facts: APIs, fields, commands, formulas, comparison tables, edge cases, failure modes, or source locations.
- **Practice** trains a checkable action, calculation, debugging move, implementation step, or decision. Include answer, feedback, or expected reasoning.
- **Perspective** extracts judgment, taste, tradeoffs, quality signals, bad smells, or AI-use criteria. State the basis: verified claims, practice observations, author experience, or `needs-human-review`.

If a form is not justified, omit it. Do not mirror sample modules just because they exist.

## Source And Claim Rules

- Prefer official docs, source code, runnable output, papers, or user-provided current context.
- Important technical facts should enter `.learnloop/claims.jsonl` when the course is reusable.
- `verified` requires `source_id` or `source`.
- `agent-inference` is never a final verified fact.
- Conflicts go to `.learnloop/conflicts.jsonl`; do not silently choose the convenient version.
- Use fictitious public examples unless the user explicitly asks for private context.

## Subagents

Subagents are optional speedups, not the method itself. Use them only for bounded work:

- Researcher: return sources, evidence, uncertainties, citations. Do not draft.
- Architect: propose module boundaries and content-form decisions. Do not write modules.
- Reviewer: find unsupported claims, fake Reference, weak Practice, empty Perspective, duplication, and private examples.
- Verifier: check whether sources actually support claims; downgrade unsupported claims.

Subagents do not edit `modules/*.md`, `course.yaml`, or `dist/`. The main agent owns final merges and truth status.

## Commands

```bash
learnloop validate <course-dir>
learnloop audit <course-dir>
learnloop build <course-dir>
learnloop context <course-dir> --question-id <id>
learnloop start courses --port 8787
```

Use `python3 -m learnloop ...` only when the package is not installed.

## References

- Read `references/course-format.md` before creating or restructuring course files.
- Read `references/orchestration.md` before generating or substantially rewriting course content.
- Read `references/answering-loop.md` before answering learner questions.
- Read `references/content-verification.md` before adding technical claims, commands, APIs, or protocol fields.
- Read `docs/content-forms.md`, `docs/evidence-and-sources.md`, and `docs/course-quality.md` before preparing a course for reuse or publication.

## Guardrails

- Keep source edits in Markdown/YAML. Treat `dist/` as generated output.
- Preserve stable section ids; learner questions depend on them.
- Do not treat fluent generated text as verified knowledge.
- Prefer small course updates over broad rewrites.
- Mark unverifiable technical details instead of presenting them as confirmed.
