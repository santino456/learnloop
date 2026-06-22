# LearnLoop Course Format

Use this reference when creating, migrating, or repairing a LearnLoop course.

## Required Files

- `course.yaml`: course metadata and ordered module list.
- `modules/*.md`: editable course source.
- `questions.jsonl`: learner question log.
- `answers/`: agent answer artifacts and follow-up material.
- `dist/`: generated HTML output.

## course.yaml

Use this shape:

```yaml
id: acp-fundamentals
title: "ACP Fundamentals"
subtitle: "Short course promise."
audience: "Target learner."
default_port: 8787
modules:
  - id: m1
    title: "What ACP is"
    file: "modules/01.md"
    summary: "One-sentence module summary."
```

Keep module ids short and stable. The current convention is `m1`, `m2`, etc.

## Module Markdown

Each module starts with frontmatter:

```markdown
---
id: m1
title: "What ACP is"
summary: "One-sentence summary."
---
```

Questionable sections use this heading syntax:

```markdown
## [m1-problem] The integration problem
```

Section ids must be unique across the course. Do not rename them after learners have submitted questions unless you also migrate `questions.jsonl`.

## Generated Output

Run:

```bash
python3 -m learnloop build <course-dir>
```

Do not hand-edit `dist/` unless debugging generated output.
