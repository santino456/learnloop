---
name: learnloop
description: Work with LearnLoop local-first adaptive learning courses. Use when creating or updating LearnLoop course source, building course HTML, validating course structure, answering saved learner questions from questions.jsonl, generating answer artifacts, or improving modules based on learner confusion.
---

# LearnLoop

Use this skill to maintain a LearnLoop course as a feedback loop:

1. Inspect `course.yaml`, `modules/*.md`, and `questions.jsonl`.
2. Run `python3 -m learnloop validate <course-dir>` before and after changes.
3. Use `python3 -m learnloop context <course-dir> --question-id <id>` for question-specific context.
4. Write answers to `answers/` and link them to the original question id.
5. Update `modules/*.md` only when the answer reveals reusable course improvement.
6. Rebuild with `python3 -m learnloop build <course-dir>`.

## References

- Read `references/course-format.md` before creating or restructuring course files.
- Read `references/answering-loop.md` before answering learner questions.
- Read `references/content-verification.md` before adding technical claims, commands, APIs, or protocol fields.

## Guardrails

- Keep source edits in Markdown/YAML. Treat `dist/` as generated output.
- Preserve stable section ids. Learner questions depend on them.
- Prefer small, clear course updates over broad rewrites.
- Use fictitious public examples unless the user explicitly asks to use private project context.
- Mark unverifiable technical details instead of presenting them as confirmed.
