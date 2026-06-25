# LearnLoop Answering Loop

Use this reference when answering learner questions saved by a LearnLoop course.

## Workflow

1. Run `python3 -m learnloop validate <course-dir>`.
2. Inspect `questions.jsonl` for `status=open`.
3. For each chosen question, run:

```bash
python3 -m learnloop context <course-dir> --question-id <id>
```

4. Answer the learner using the course, module, and section context.
5. Save the answer in `answers/<question-id>.md`.
6. If the confusion is likely reusable, update the relevant `modules/*.md` section.
7. Run `python3 -m learnloop validate <course-dir>` and `python3 -m learnloop build <course-dir>`.

## Answer Artifact

Use this shape:

```markdown
---
question_id: "<id>"
course_id: "<course id>"
module_id: "<module id>"
section_id: "<section id>"
---

# Answer

<direct answer>

## Course Update Recommendation

<whether to update module source and why>
```

## Judgment

Answer the learner first. Only update the course source when the answer reveals a durable explanation, missing prerequisite, misleading wording, or useful example.

If an answer adds a new technical fact, mark its status in the course text (for example, "据官方文档..." or "这一点还需要验证"). Add or update `.learnloop/claims.jsonl` only if the course maintains a formal knowledge-state workspace.
