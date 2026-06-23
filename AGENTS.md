# AGENTS.md

This file is a routing note for AI agents. Do not treat it as a second copy of
the product documentation.

## Read Order

1. `README.md` explains what LearnLoop is and how to run it.
2. `skills/learnloop/SKILL.md` is the authority for agent course-generation
   workflow.
3. `docs/content-forms.md`, `docs/evidence-and-sources.md`, and
   `docs/course-quality.md` define the quality bar for reusable courses.
4. `docs/release.md` is the release checklist.

## Repository Rule

Keep workflow rules in the skill or docs above. If those rules change, update
the source document instead of duplicating the same instructions here.

## Local Notes

- `dist/` is generated output.
- Preserve section ids in `modules/*.md`; learner questions depend on them.
- Do not commit local scratch files, logs, or unrelated untracked courses unless
  the user explicitly asks.
