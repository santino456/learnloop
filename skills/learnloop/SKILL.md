---
name: learnloop
description: Work with LearnLoop local-first adaptive learning courses. Use when creating or updating LearnLoop course source, generating trustworthy AI-assisted tutorials, choosing Tutorial/Reference/Practice/Perspective content forms, answering saved learner questions from questions.jsonl, or improving modules based on learner confusion.
---

# LearnLoop

LearnLoop turns raw material into a local, verifiable learning loop:

```text
sources + learner goal -> Markdown/YAML course -> local HTML -> questions -> agent context -> improved source
```

Your first job is **epistemic control**, not fast drafting. A fluent lesson is not good enough unless the learner goal, sources, evidence, content forms, and validation state are clear.

Think like an experienced teacher preparing a lesson: research first, check the facts, decide what form the material should take, then write. Do not jump straight to a long module draft.

## Task Router

- **Answer learner question**: read `references/answering-loop.md`, run `learnloop context`, write an answer artifact, and update course source only if the answer should be reused.
- **Small course edit**: inspect the target module, preserve section ids, make the narrow edit, then run `learnloop validate` and `learnloop build`.
- **Course structure or template change**: read `references/course-format.md` before editing `course.yaml`, module frontmatter, containers, templates, or section ids.
- **New or substantial course generation**: start with `learnloop scaffold-course <slug> --target courses` unless the course already exists. Then follow the Expert Teacher Workflow below and read `docs/content-forms.md` first.
- **Course from PDF/DOCX/PPTX/Markdown/text material**: put the original file in `raw/`, run `learnloop ingest <file> --course <course-dir>`, then use `.learnloop/materials/<source>/` as the reading substrate. Do not draft directly from memory or cite `raw/*.pdf` as an image.
- **Named entities, technical claims, commands, APIs, protocol fields, or version-sensitive facts**: verify them against a reliable source before adding them.
- **Publication or reusable course**: also read `docs/evidence-and-sources.md` and `docs/course-quality.md`; optionally add a `.learnloop/` workspace to track sources and claims.

## Expert Teacher Workflow

Before drafting a new or substantial course, work through these steps in your reasoning. You do not need to write long planning documents unless the user asks for them or the course will be published.

1. **Understand the learner**: Who are they? What do they already know? What specific confusion or goal brings them here?
2. **Define the learning job**: What should the learner be able to understand or do after this module? One module, one job.
3. **Research and fact-check**: Identify the sources (official docs, source code, runnable output, papers, user context). For high-stakes claims, verify exact names, versions, commands, and protocol fields. Mark uncertainty instead of guessing.
4. **Ingest local materials**: For PDFs, Word documents, slide decks, Markdown, or text files, run `learnloop ingest` and inspect `material.json`, `chunks.jsonl`, and any `figures.md` before drafting. Treat extracted figures as candidates that still need visual checking.
5. **Ask content-derived questions**: After you understand the material, identify 2–4 choices that actually change the course shape. The questions must come from the content, not a fixed questionnaire. If the user does not respond, fall back to a high-quality default that keeps the course complete but marks optional advanced sections.
6. **Design the module plan**: Decide which modules are Tutorial, Reference, Practice, or Perspective, and why.
7. **Draft**: Write only content supported by the design and evidence. Convert suitable material into semantic learning components instead of piling up paragraphs.
8. **Self-review**: Check for unsupported claims, fake Reference, weak Practice, empty Perspective, private examples, and section id stability.
9. **Build**: run `validate`, `build`, and optionally `audit`.

Do not write a long module before you understand the learner, the learning job, and the evidence.

## Content Form Rules

- **Tutorial** explains concepts and mental models. Start from a likely confusion; introduce one idea at a time; mark uncertainty instead of sounding definitive without evidence. Link to Reference when the learner may want to go deeper.
- **Reference** is a source-grounded deep dive: cite official docs, papers, or authoritative articles with clickable Markdown links `[source name](URL)`. Label local materials as `本地`. Do not write Reference from memory alone.
- **Practice** trains a checkable action, calculation, debugging move, implementation step, or decision. Include answer, feedback, or expected reasoning.
- **Perspective** extracts judgment, taste, tradeoffs, quality signals, bad smells, or AI-use criteria. State the basis: verified claims, practice observations, author experience, or `needs-human-review`.

If a form is not justified, omit it. Do not mirror sample modules just because they exist.

## Semantic Component Rules

Use HTML learning components when they make the lesson more direct:

- `figure`: one image that explains evidence, architecture, UI state, or a visual mechanism. Always include meaningful `alt`.
- `gallery`: compare two or more visual states, such as before/after or wrong/right.
- `flow`: show a process, data path, request path, or causal chain.
- `timeline`: show phases, lifecycle, ordering, or staged execution.
- `decision`: train judgment. Include `--- perspective` or `--- answer`, and state the basis.

Do not use components as decoration. If a block does not improve understanding,
write a normal paragraph. Local images belong in the course `assets/` folder;
remote images stay as links and are not downloaded.

## Source And Claim Rules

- Prefer official docs, source code, runnable output, papers, or user-provided current context.
- When a course is built from an external paper or document, keep the original artifact in the course `raw/` folder and cite specific sections or figures in the modules.
- Run `learnloop ingest` for local PDF/DOCX/PPTX/Markdown/text sources before writing reusable course content. Use the material pack as evidence, not the PDF filename alone.
- Cite external sources with clickable Markdown links: `[source name](URL)`. Label local materials as `本地`. Do not write source notes as plain text without a link.
- Verify exact names for institutions, products, projects, repositories, people, models, protocols, and organizations before writing them. Do not normalize names from memory.
- Do not invent timelines, usage history, performance numbers, architecture motives, or project maturity. If the source does not prove it, mark it unverified or omit it.
- For reusable courses, track important claims in `.learnloop/claims.jsonl`. For personal courses, simply mark uncertainty in the prose.
- Conflicts between sources should be noted; do not silently choose the convenient version.
- Use fictitious public examples unless the user explicitly asks for private context.

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
- Read `docs/content-forms.md` before choosing templates.
- Read `docs/evidence-and-sources.md` and `docs/course-quality.md` before preparing a course for reuse or publication.

## Guardrails

- Keep source edits in Markdown/YAML. Treat `dist/` as generated output.
- Preserve stable section ids; learner questions depend on them.
- Do not treat fluent generated text as verified knowledge.
- Prefer small course updates over broad rewrites.
- Mark unverifiable technical details instead of presenting them as confirmed.
- Do not require a `.learnloop/` workspace for every course.
