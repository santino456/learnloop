---
name: learnloop
description: Work with LearnLoop local-first adaptive learning courses and epistemic course-generation workflows. Use when creating or updating LearnLoop course source, orchestrating research/drafting/review for learning materials, validating claims and sources, answering saved learner questions from questions.jsonl, generating answer artifacts, or improving modules based on learner confusion.
---

# LearnLoop

Use this skill to help a learner turn raw material into a trustworthy local course. The main agent owns the course knowledge state: what is known, what is sourced, what is inferred, what conflicts, and what needs human judgment.

Never start by writing a long lesson. First decide what the learner actually needs, what sources support it, and which content forms are justified.

## Core Workflow

1. Inspect `course.yaml`, `modules/*.md`, `questions.jsonl`, and `.learnloop/` if present.
2. If generating substantial content, create or update `.learnloop/source_inventory.yaml`, `.learnloop/course_architecture.md`, chapter briefs, evidence packs, claims, and conflicts before editing modules.
3. Decide content forms from the learner goal and evidence shape. Do not mirror sample course structure.
4. Write course source only from verified evidence, marked uncertainty, or explicit human judgment.
5. Use subagents only as optional parallel workers for bounded research, draft, or review tasks. The main agent remains responsible for final content and merges.
6. Run `python3 -m learnloop audit <course-dir>` for generated courses, then `python3 -m learnloop validate <course-dir>` and `python3 -m learnloop build <course-dir>`.

## Hard Gates

- Do not create or rewrite `modules/*.md` until source inventory, course architecture, and at least one evidence pack exist.
- Do not create a Reference module unless the material contains dense reusable lookup facts such as APIs, fields, formulas, commands, edge cases, or comparison tables.
- Do not create Practice unless the learner needs to perform a skill or make a checkable decision.
- Do not create Perspective unless there is a meaningful higher-level judgment, taste, tradeoff, or AI-use lesson to extract.
- Do not mark generated inference as `verified`.
- If a course has `.learnloop/`, `python3 -m learnloop audit <course-dir>` should pass before presenting it as ready.

## Learner Questions

1. Inspect `questions.jsonl` for `status=open`.
2. Run `python3 -m learnloop context <course-dir> --question-id <id>`.
3. Write answers to `answers/` and link them to the original question id.
4. Update `modules/*.md` only when the answer reveals reusable course improvement.

## References

- Read `references/course-format.md` before creating or restructuring course files.
- Read `references/orchestration.md` before generating or substantially rewriting course content.
- Read `references/answering-loop.md` before answering learner questions.
- Read `references/content-verification.md` before adding technical claims, commands, APIs, or protocol fields.

## Guardrails

- Keep source edits in Markdown/YAML. Treat `dist/` as generated output.
- Preserve stable section ids. Learner questions depend on them.
- Do not treat fluent generated text as verified knowledge.
- Do not let subagents directly modify final course source; have them return evidence, drafts, or review reports.
- Prefer small, clear course updates over broad rewrites.
- Use fictitious public examples unless the user explicitly asks to use private project context.
- Mark unverifiable technical details instead of presenting them as confirmed.
- Perspective content should raise judgment and taste, but must state its basis or mark `needs-human-review`.
