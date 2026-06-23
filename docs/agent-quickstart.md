# Agent Quickstart

Use this when you are an AI agent working inside a LearnLoop repository.

## What This Repo Does

LearnLoop keeps learning material local and editable:

```text
course.yaml + modules/*.md
-> learnloop build
-> dist/*.html
-> learner questions in questions.jsonl
-> learnloop context
-> answers/ and source improvements
```

The default course library is `courses/`. Each direct child directory with a
`course.yaml` is one course. A single background service serves all courses and
injects a sidebar for switching between them.

## Start The App

```bash
learnloop start courses --port 8787
learnloop status courses
```

Open `http://127.0.0.1:8787/`.

For foreground debugging:

```bash
learnloop serve courses --port 8787
```

## Create A Course

```bash
learnloop init my-topic --target courses
learnloop validate courses/my-topic
learnloop build courses/my-topic
```

Then edit:

- `courses/my-topic/course.yaml`
- `courses/my-topic/modules/*.md`

Do not hand-edit `dist/` except while debugging generated output.

## Generate Or Rewrite Course Content

Before writing substantial module content, create short stage notes:

```text
Intent:
- learner goal:
- background:
- outcome:
- exclusions:

Research:
- sources used:
- missing sources:
- reliability notes:

Evidence:
- supported facts:
- weak or conflicting points:
- examples worth teaching:

Design:
- module plan:
- content form decisions:
- why Reference/Practice/Perspective are or are not needed:
```

For reusable or technical courses, persist the notes in `.learnloop/`:

- `source_inventory.yaml`
- `course_architecture.md`
- `chapter_briefs/*.md`
- `evidence_packs/*.md`
- `claims.jsonl`
- `conflicts.jsonl`

## Choose Content Forms

- Tutorial: concepts, explanation, mental models.
- Reference: dense lookup facts, tables, APIs, commands, formulas, edge cases.
- Practice: checkable action with answer, feedback, or expected reasoning.
- Perspective: judgment, taste, tradeoffs, quality signals, bad smells, or
  AI-use criteria with an explicit basis.

If the form is not justified, omit it.

## Answer Learner Questions

1. Inspect `questions.jsonl` for open questions.
2. Run:

   ```bash
   learnloop context <course-dir> --question-id <id>
   ```

3. Write the answer under `answers/`.
4. Update `modules/*.md` only if the answer should become reusable course
   material.
5. Run validate/build/audit.

## Validate Before Handoff

```bash
python3 -m unittest discover -s tests -v
learnloop validate courses/acp-fundamentals
learnloop build courses/acp-fundamentals
learnloop audit courses/acp-fundamentals
```

For a newly generated course, replace `courses/acp-fundamentals` with the new
course path.
