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
6. If the confusion is likely reusable, add a `qa` block to the relevant section in `modules/*.md`.
7. Run `validate` and `build`.

## Answer Artifact

```markdown
---
question_id: "<id>"
course_id: "<course id>"
module_id: "<module id>"
section_id: "<section id>"
---

# Answer

<direct answer with concrete example, derivation, code, or citation>

## Course Update Recommendation

<where to add a qa block and why>
```

## Judgment

Answer the learner first. Only update the course source when the answer reveals a durable explanation, missing prerequisite, misleading wording, or useful example.

If an answer adds a new technical fact, mark its status in the prose or, for reusable courses, in `.learnloop/claims.jsonl`.
