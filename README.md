# LearnLoop

LearnLoop is a local-first adaptive learning loop for technical topics.

It turns course material into a small local workspace where every learner question is saved with the exact course, module, and section context that produced it. An agent can then answer the question, generate follow-up material, and help update the course source.

## Why It Exists

Static learning material is easy to save but bad at remembering where a learner got stuck. Chat is flexible but often loses the structure of the course.

LearnLoop connects the two:

1. Write course source in Markdown and `course.yaml`.
2. Build static HTML pages using a chosen template.
3. Ask questions beside the exact section that caused confusion.
4. Store those questions in `questions.jsonl`.
5. Use `learnloop context` and the LearnLoop skill to answer and improve the course.

## Quick Start

Build and serve the ACP sample course:

```bash
cd learnloop
python3 -m learnloop build courses/acp-fundamentals
python3 -m learnloop serve courses/acp-fundamentals
```

If installed as a package, the same commands are:

```bash
learnloop build courses/acp-fundamentals
learnloop serve courses/acp-fundamentals
```

## Course Layout

```text
courses/acp-fundamentals/
├── course.yaml
├── modules/
│   ├── 01.md
│   └── ...
├── answers/
├── questions.jsonl
└── dist/
```

`dist/` is generated output. Edit `course.yaml` and `modules/*.md`.

## Templates

LearnLoop renders the same course source through different templates. Set the default template in `course.yaml` and override it per module in the module's frontmatter:

```yaml
# course.yaml
template: editorial
```

```markdown
---
# modules/07.md
template: workshop
---
```

Built-in templates live in `templates/`:

- `editorial` — quiet, paper-like reading style.
- `workshop` — exercise and checkpoint emphasized layout.

List templates and see which template each module uses:

```bash
python3 -m learnloop templates courses/acp-fundamentals
```

## Container Syntax

Mark practice blocks inside a module with `::: exercise` and `::: checkpoint` containers:

```markdown
::: exercise
Write a minimal bridge responsibility list.
:::

::: checkpoint
Confirm you can explain why a browser cannot spawn a local process.
:::
```

Both containers can contain any LearnLoop Markdown (paragraphs, lists, code blocks, etc.).

## CLI

```bash
python3 -m learnloop init my-course
python3 -m learnloop build courses/acp-fundamentals
python3 -m learnloop validate courses/acp-fundamentals
python3 -m learnloop context courses/acp-fundamentals --question-id <id>
python3 -m learnloop serve courses/acp-fundamentals --port 8787
python3 -m learnloop templates courses/acp-fundamentals
```

## Current Status

- ACP sample course migrated to Markdown/YAML source.
- Template-capable rendering pipeline with course- and module-level template selection.
- Local server writes structured learner questions.
- Generated pages read `/config.js`, so non-default ports work.
- LearnLoop skill is normalized for agent-guided question answering.

Not included in the first version: accounts, cloud sync, multi-user spaces, hosted marketplaces, or a long-running cloud agent service.
