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

Start one local LearnLoop service for every course under `courses/`:

```bash
cd learnloop
python3 -m learnloop start courses --port 8787
```

If installed as a package, the same commands are:

```bash
learnloop start courses --port 8787
```

Open `http://127.0.0.1:8787/` to see the course library. Each course is served as a resource on the same local service:

```text
/course/acp-fundamentals/
/course/kv-cache/
```

Use `status` and `stop` for the background service:

```bash
python3 -m learnloop status courses
python3 -m learnloop stop courses
```

`serve` is still available for foreground debugging:

```bash
python3 -m learnloop serve courses --port 8787
```

Ports are strict by default: LearnLoop fails clearly instead of silently moving to another port. Use `--auto-port` only when you explicitly want a temporary alternative. Check a running server with:

```bash
curl http://127.0.0.1:8787/healthz
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
├── .learnloop/
│   ├── source_inventory.yaml
│   ├── course_architecture.md
│   ├── claims.jsonl
│   ├── conflicts.jsonl
│   ├── chapter_briefs/
│   └── evidence_packs/
└── dist/
```

`dist/` is generated output. Edit `course.yaml` and `modules/*.md`; use `.learnloop/` to track sources, claims, conflicts, and chapter-level evidence when generating substantial content with an agent.

## Templates

LearnLoop renders the same course source through different templates. Set the default template in `course.yaml` and override it per module in the module's frontmatter:

```yaml
# course.yaml
template: tutorial
```

```markdown
---
# modules/07.md
template: perspective
---
```

Built-in templates live in `templates/`:

- `tutorial` — quiet, paper-like reading style.
- `reference` — dense lookup and comparison layout.
- `practice` — exercise and checkpoint emphasized layout.
- `perspective` — judgment, taste, tradeoff, and higher-level experience layer.

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

Perspective exercises add higher-level experience and judgment. They must state their basis or mark that human review is needed:

```markdown
::: exercise
Judge whether this integration needs a local bridge.

--- perspective
依据：基于本章已验证的 browser sandbox 约束。

A mature implementation treats the bridge as the trust boundary.
---
:::
```

## Epistemic Workflow

LearnLoop is not a hosted course platform. It is a local protocol for helping a learner's own agent generate better learning material. For serious generation tasks, the main agent should:

1. Inventory sources in `.learnloop/source_inventory.yaml`.
2. Split work by chapter with `.learnloop/chapter_briefs/`.
3. Gather evidence before drafting in `.learnloop/evidence_packs/`.
4. Track important facts in `.learnloop/claims.jsonl`.
5. Record unresolved conflicts in `.learnloop/conflicts.jsonl`.
6. Run `learnloop audit`, validate, and build before showing the course.

Subagents are optional parallel workers for research, drafting, or review; the main agent remains responsible for final merges and truth status.

## CLI

```bash
python3 -m learnloop init my-course
python3 -m learnloop build courses/acp-fundamentals
python3 -m learnloop validate courses/acp-fundamentals
python3 -m learnloop audit courses/acp-fundamentals
python3 -m learnloop context courses/acp-fundamentals --question-id <id>
python3 -m learnloop start courses --port 8787
python3 -m learnloop status courses
python3 -m learnloop stop courses
python3 -m learnloop serve courses --port 8787
python3 -m learnloop templates courses/acp-fundamentals
```

## Current Status

- ACP sample course migrated to Markdown/YAML source.
- Template-capable rendering pipeline with course- and module-level template selection.
- Perspective template for judgment, taste, and higher-level learning experience.
- Lightweight knowledge-state validation for verified claims and Perspective basis.
- Single local library service manages all courses under one port.
- Generated pages read course-local `config.js`, so questions use the correct course API.
- LearnLoop skill is normalized for agent-guided course generation and question answering.

Not included in the first version: accounts, cloud sync, multi-user spaces, hosted marketplaces, or a long-running cloud agent service.
