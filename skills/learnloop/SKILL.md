---
name: learnloop
description: Work with LearnLoop local-first adaptive learning courses and epistemic course-generation workflows. Use when creating or updating LearnLoop course source, orchestrating research/drafting/review for learning materials, validating claims and sources, answering saved learner questions from questions.jsonl, generating answer artifacts, or improving modules based on learner confusion.
---

# LearnLoop

Use this skill to help a learner turn raw material into a trustworthy local course. The main agent owns the learning design and truth status: what the learner needs, what sources support it, which content forms are justified, and what must remain uncertain.

Never start by writing a long lesson. First run the stage gates below. For lightweight private notes, the gates can be short notes in your response. For formal or technical courses, persist the gates in `.learnloop/`.

## Stage Gates

1. **Intent**: state the learner goal, background, desired outcome, and exclusions.
2. **Research**: list sources used or needed. Prefer official docs, papers, source code, and runnable checks for technical claims.
3. **Evidence**: extract only the facts and examples needed for the course. Mark weak, missing, or conflicting evidence.
4. **Design**: decide modules and content forms. Do not mirror sample course structure.
5. **Draft**: write only content justified by the design and evidence.
6. **Review**: check accuracy, learning value, content-form fit, and unsupported claims. Then run validate/build.

## Hard Gates

- Do not draft `modules/*.md` until you have at least a short Intent, Research, Evidence, and Design note.
- Do not create a Reference module unless the material contains dense reusable lookup facts such as APIs, fields, formulas, commands, edge cases, source locations, or comparison tables.
- Do not create Practice unless the learner needs to perform a skill, calculate something, debug something, or make a checkable decision.
- Do not create Perspective unless there is a meaningful higher-level judgment, taste, tradeoff, failure smell, or AI-use lesson to extract.
- If a content form is not justified, omit it.
- Do not mark generated inference as `verified`.

## Learner Questions

1. Inspect `questions.jsonl` for `status=open`.
2. Run `python3 -m learnloop context <course-dir> --question-id <id>`.
3. Write answers to `answers/` and link them to the original question id.
4. Update `modules/*.md` only when the answer reveals reusable course improvement.

## References

- Read `references/course-format.md` before creating or restructuring course files.
- Read `references/orchestration.md` before generating or substantially rewriting course content. It contains the content-form rubric and subagent prompts.
- Read `references/answering-loop.md` before answering learner questions.
- Read `references/content-verification.md` before adding technical claims, commands, APIs, or protocol fields.
- Read the repository docs `docs/content-forms.md` and `docs/course-quality.md` when preparing a course for reuse or publication.

## Persistence Policy

- For small personal learning notes, keep stage-gate notes in the conversation and write only the final course files.
- For formal, technical, or reusable courses, persist stage gates in `.learnloop/source_inventory.yaml`, `.learnloop/course_architecture.md`, evidence packs, and claims.
- Use `python3 -m learnloop audit <course-dir>` when `.learnloop/` is present or when the course is meant to be reused.

## Guardrails

- Keep source edits in Markdown/YAML. Treat `dist/` as generated output.
- Preserve stable section ids. Learner questions depend on them.
- Do not treat fluent generated text as verified knowledge.
- Use subagents only as optional parallel workers for bounded research, architecture, draft review, or verification. The main agent owns final content.
- Prefer small, clear course updates over broad rewrites.
- Use fictitious public examples unless the user explicitly asks to use private project context.
- Mark unverifiable technical details instead of presenting them as confirmed.
- Perspective content should raise judgment and taste, but must state its basis or mark `needs-human-review`.
