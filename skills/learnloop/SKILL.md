---
name: learnloop
description: Work with LearnLoop local-first adaptive learning courses. Use when creating or updating LearnLoop course source, generating trustworthy AI-assisted tutorials, choosing Tutorial/Reference/Practice/Perspective content forms, answering saved learner questions from questions.jsonl, or improving modules based on learner confusion.
---

# LearnLoop

LearnLoop is a local-first AI course compiler and learning package format. It
turns raw material into a local, verifiable learning loop:

```text
sources + learner goal -> Markdown/YAML course -> local HTML -> questions -> agent context -> improved source
```

Your first job is **learning design and epistemic control**, not fast drafting.
A fluent lesson is not good enough unless the learner goal, section-level
learning actions, sources, evidence, content forms, and validation state are clear.

Think like an experienced teacher preparing a lesson: research first, check the facts, decide what form the material should take, then write. Do not jump straight to a long module draft.

## Task Router

- **Answer learner question**: read `references/answering-loop.md`, run `learnloop context`, write an answer artifact, and update course source only if the answer should be reused.
- **Small course edit**: inspect the target module, preserve section ids, make the narrow edit, then run `learnloop validate` and `learnloop build`.
- **Course structure or template change**: read `references/course-format.md` before editing `course.yaml`, module frontmatter, containers, templates, or section ids.
- **New or substantial course generation**: start with `learnloop scaffold-course <slug> --target courses` unless the course already exists. Then follow the Expert Teacher Workflow below and read `references/orchestration.md` first.
- **Course from PDF/DOCX/PPTX/Markdown/text material**: put the original file in `raw/`, run `learnloop ingest <file> --course <course-dir>`, then use `.learnloop/materials/<source>/` as the reading substrate. Do not draft directly from memory or cite `raw/*.pdf` as an image.
- **Named entities, technical claims, commands, APIs, protocol fields, or version-sensitive facts**: verify them against a reliable source before adding them.
- **Publication or reusable course**: also read `references/content-verification.md`; optionally add a `.learnloop/` workspace to track sources and claims.
- **Language and audience**: generate course content and UI labels in the user's interaction language. Chinese interaction → default to Chinese content (`lang: zh` or keep `lang: auto` when the text is clearly Chinese); English interaction → default to English (`lang: en`). When language is mixed or unclear, ask: "你希望课程用中文、英文，还是中英双语呈现？" Record the final choice in `course.yaml` under `lang`.

## Expert Teacher Workflow

Before drafting a new or substantial course, work through these steps in your reasoning. You do not need to write long planning documents unless the user asks for them or the course will be published.

1. **Understand the learner and language**: Who are they? What do they already know? What specific confusion or goal brings them here? Confirm the content language from the user's interaction and set `lang` in `course.yaml` (zh, en, or auto).
2. **Define the learning job**: What should the learner be able to understand or do after this module? One module, one job.
3. **Research and fact-check**: Identify the sources (official docs, source code, runnable output, papers, user context). For high-stakes claims, verify exact names, versions, commands, and protocol fields. Mark uncertainty instead of guessing.
4. **Ingest local materials**: For PDFs, Word documents, slide decks, Markdown, or text files, run `learnloop ingest` and inspect `material.json`, `chunks.jsonl`, and any `figures.md` before drafting. Treat extracted figures as candidates that still need visual checking.
5. **Ask content-derived questions**: After you understand the material, identify 2–4 choices that actually change the course shape. The questions must come from the content, not a fixed questionnaire. If the user does not respond, fall back to a high-quality default that keeps the course complete but marks optional advanced sections.
6. **Write the Course Blueprint**: Decide the learner job, module jobs, section-level learning actions, evidence needs, and components before editing modules. Use `.learnloop/course_blueprint.md` when present.
7. **Design the module plan**: Decide which modules are Tutorial, Reference, Practice, or Perspective, and why.
8. **Draft**: Write only content supported by the design and evidence. Convert suitable material into semantic learning components instead of piling up paragraphs. Do not stop to perfect container syntax while drafting.
9. **Auto-fix and format**: Run `learnloop fix <course-dir>` to repair common syntax issues (missing concept titles, evidence status/source, unclosed containers), then `learnloop fmt <course-dir>` to normalize indentation and component layout.
10. **Self-review**: Check for unsupported claims, fake Reference, weak Practice, empty Perspective, private examples, and section id stability.
11. **Build**: run `validate`, `build`, and optionally `audit`.

### Content-first checklist

Use this order when deciding what to change:

1. Does the section make a clear learning action (understand, compare, verify, practice, judge)?
2. Is the evidence reliable and sourced?
3. Does the chosen component reduce cognitive load or expose structure?
4. Is the syntax valid after `learnloop fix`?

Do not let container rules slow down the first draft.
Every section should ask the learner to do one thing: understand, compare,
verify, practice, or judge. If a section only asks the learner to read, redesign it.

## Content Form Decision

Choose Tutorial, Reference, Practice, and Perspective because the learner needs
that form, not because a sample course used it. If the choice is unclear, read
`references/orchestration.md` and write down the learning job before drafting. Omit a
form when it has no real job.

## Semantic Components

Use components only when they reduce confusion, expose evidence, train a move,
or make a judgment visible. Do not add components as decoration. Local images
belong in `assets/`; remote images stay as links and are not downloaded. For
exact syntax, read `references/course-format.md`.

## Source And Claim Rules

Truth beats fluency. Verify exact names, version-sensitive facts, commands,
protocol fields, timelines, performance numbers, and project maturity before
writing them. If the source does not prove a claim, mark it unverified or omit
it. Read `references/content-verification.md` for the verification standard and
when preparing a reusable course.

## Optional `.learnloop/` Workspace

A `.learnloop/` workspace is **optional**. Use it only when:

- The course will be shared or published.
- Multiple agents or people will edit it.
- The topic has conflicting sources that need tracking.

When used, it may contain:

- `source_inventory.yaml` — sources consulted.
- `claims.jsonl` — important claims with verification status.
- `conflicts.jsonl` — unresolved disagreements between sources.

For personal or quick courses, skip the workspace and rely on agent-driven fact checking.

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
learnloop fix <course-dir>
learnloop fmt <course-dir>
learnloop context <course-dir> --question-id <id>
learnloop scaffold-course <slug> --target courses
learnloop ingest <course-dir>/raw/<source-file> --course <course-dir>
learnloop start courses --port 8787
```

Use `python3 -m learnloop ...` only when the package is not installed.

## References

- Read `references/course-format.md` before creating or restructuring course files.
- Read `references/orchestration.md` before generating or substantially rewriting course content.
- Read `references/answering-loop.md` before answering learner questions.
- Read `references/content-verification.md` before adding technical claims, commands, APIs, or protocol fields.

## Guardrails

- Keep source edits in Markdown/YAML. Treat `dist/` as generated output.
- Preserve stable section ids; learner questions depend on them.
- Do not treat fluent generated text as verified knowledge.
- Prefer small course updates over broad rewrites.
- Mark unverifiable technical details instead of presenting them as confirmed.
- Do not require a `.learnloop/` workspace for every course.
