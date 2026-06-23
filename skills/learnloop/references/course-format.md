# LearnLoop Course Format

Use this reference when creating, migrating, or repairing a LearnLoop course.

## Required Files

- `course.yaml`: course metadata and ordered module list.
- `modules/*.md`: editable course source.
- `questions.jsonl`: learner question log.
- `answers/`: agent answer artifacts and follow-up material.
- `.learnloop/`: optional orchestration workspace for sources, claims, conflicts, chapter briefs, and evidence packs.
- `dist/`: generated HTML output.

## course.yaml

Use this shape:

```yaml
id: acp-fundamentals
title: "ACP Fundamentals"
subtitle: "Short course promise."
audience: "Target learner."
default_port: 8787
template: tutorial
modules:
  - id: m1
    title: "What ACP is"
    file: "modules/01.md"
    summary: "One-sentence module summary."
```

- `template` sets the default rendering template for the course. It can be overridden per module in module frontmatter.
- Keep module ids short and stable. The current convention is `m1`, `m2`, etc.

## Module Markdown

Each module starts with frontmatter:

```markdown
---
id: m1
title: "What ACP is"
summary: "One-sentence summary."
template: practice
---
```

- `template` in module frontmatter overrides the course-level template for that module only.

Questionable sections use this heading syntax:

```markdown
## [m1-problem] The integration problem
```

Section ids must be unique across the course. Do not rename them after learners have submitted questions unless you also migrate `questions.jsonl`.

### Container Syntax

Use `::: exercise` and `::: checkpoint` containers for practice and self-check blocks. Containers can contain paragraphs, lists, code blocks, and callouts:

```markdown
::: exercise
Write a minimal bridge responsibility list.

- List item inside the exercise.
:::

::: checkpoint
Explain why a browser cannot spawn a local subprocess.
:::
```

Perspective exercises use an exercise container with a `--- perspective` section. Include an explicit basis:

```markdown
::: exercise
Judge whether this integration needs a local bridge.

--- perspective
依据：基于本章关于 browser sandbox 和 local bridge 的 verified claims。

A mature implementation treats the bridge as the trust boundary, not decorative middleware.
---
:::
```

## Knowledge State

For small personal learning notes, stage-gate notes can stay in the conversation. When generating formal, technical, reusable, or high-risk content, keep orchestration files in `.learnloop/`:

- `source_inventory.yaml`
- `course_architecture.md`
- `chapter_briefs/*.md`
- `evidence_packs/*.md`
- `claims.jsonl`
- `conflicts.jsonl`

`claims.jsonl` records key facts:

```json
{"id":"claim-001","claim":"LearnLoop preserves section ids in generated HTML.","module_id":"m1","section_id":"m1-purpose","status":"verified","source_id":"local-source","checked_at":"2026-06-22"}
```

`verified` claims must include `source_id` or `source`.

## Templates

Built-in templates are packaged under `learnloop/assets/templates/<name>/` and contain:

- `manifest.yaml`: template metadata and supported block types.
- `template.html`: page shell with placeholders `{{ page_title }}`, `{{ course_title }}`, `{{ content }}`, `{{ css_href }}`, `{{ js_src }}`.
- `style.css`: template styles.
- `runtime.js`: question button and drawer logic.

Example `manifest.yaml`:

```yaml
name: tutorial
version: 1
renderer: semantic-html-v1
supports:
  blocks:
    - paragraph
    - list
    - code
    - callout
    - section
    - exercise
    - checkpoint
requires:
  section_ids: true
  question_buttons: true
assets:
  css: style.css
  js: runtime.js
```

Built-in templates are `tutorial`, `reference`, `practice`, and `perspective`.

## Generated Output

Run:

```bash
python3 -m learnloop build <course-dir>
```

Do not hand-edit `dist/` unless debugging generated output.
