# AGENTS.md

This repository is LearnLoop: a local-first tool for generating, validating,
serving, and improving learning courses with AI agents.

## First Read

Before changing files, read these in order:

1. `README.md` for the product shape and CLI.
2. `docs/agent-quickstart.md` for the agent workflow.
3. `skills/learnloop/SKILL.md` before creating, rewriting, or reviewing course
   content.
4. `docs/content-forms.md`, `docs/evidence-and-sources.md`, and
   `docs/course-quality.md` before preparing reusable or public courses.

## Core Model

LearnLoop is not a hosted platform. It is a local course library:

```text
courses/<course-id>/
  course.yaml
  modules/*.md
  questions.jsonl
  answers/
  .learnloop/
  dist/
```

One local service manages the whole `courses/` root:

```bash
learnloop start courses --port 8787
```

Do not start one server per course unless debugging a specific compatibility
case.

## Agent Workflow

For new or substantial course generation, do not jump straight to a long
Markdown draft. Follow the LearnLoop stage gates:

```text
Intent -> Research -> Evidence -> Design -> Draft -> Review -> Build
```

For reusable technical courses, persist evidence in `.learnloop/`:

- `source_inventory.yaml`
- `course_architecture.md`
- `chapter_briefs/*.md`
- `evidence_packs/*.md`
- `claims.jsonl`
- `conflicts.jsonl`

Subagents may help with bounded research, architecture review, draft review, or
verification, but the main agent owns final edits and truth status.

## Content Rules

- Use Tutorial for explanation.
- Use Reference only for dense reusable lookup material.
- Use Practice only for checkable action, feedback, or expected reasoning.
- Use Perspective only for judgment, tradeoffs, taste, bad smells, or AI-use
  criteria, and state the basis.
- Do not mark agent inference as verified.
- Do not add private paths, private project names, or internal examples to
  public samples.

## Commands

Run these before committing:

```bash
python3 -m unittest discover -s tests -v
learnloop validate courses/acp-fundamentals
learnloop build courses/acp-fundamentals
learnloop audit courses/acp-fundamentals
```

If the `learnloop` command is not installed, use `python3 -m learnloop`.

When changing the skill, also run the Codex skill validator if available:

```bash
python3 path/to/quick_validate.py skills/learnloop
```

## Editing Boundaries

- Treat `dist/` as generated output.
- Preserve section ids such as `m1-purpose`; learner questions depend on them.
- Keep changes small and directly tied to the task.
- Do not commit local scratch output, generated logs, or unrelated untracked
  courses unless the user explicitly asks.
