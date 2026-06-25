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

Install from the GitHub repository:

```bash
pipx install git+https://github.com/santino456/learnloop.git
```

Create a local course library and start LearnLoop:

```bash
mkdir -p courses
learnloop init demo-course --target courses
learnloop start courses --port 8787
```

Open `http://127.0.0.1:8787/` to see the course library.

To try the richer ACP sample course, run from a local checkout:

```bash
git clone https://github.com/santino456/learnloop.git
cd learnloop
python3 -m pip install -e .
learnloop start courses --port 8787
```

The sample is documented in [courses/acp-fundamentals](courses/acp-fundamentals/README.md).

Each course is served as a resource on the same local service:

```text
/course/acp-fundamentals/
/course/kv-cache/
```

Use `status` and `stop` for the background service:

```bash
learnloop status courses
learnloop stop courses
```

`serve` is still available for foreground debugging:

```bash
learnloop serve courses --port 8787
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
├── dist/                 # generated output
└── .learnloop/           # optional: sources, claims, conflicts for reusable courses
```

Edit `course.yaml` and `modules/*.md`; use `dist/` for generated HTML. Add `.learnloop/` only when you want explicit source tracking, claims, or conflict management for a reusable course.

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

Built-in templates are packaged with LearnLoop:

- `tutorial` — quiet, paper-like reading style.
- `reference` — dense lookup and comparison layout.
- `practice` — exercise and checkpoint emphasized layout.
- `perspective` — judgment, taste, tradeoff, and higher-level experience layer.

List templates and see which template each module uses:

```bash
learnloop templates courses/acp-fundamentals
```

See [Content Forms](docs/content-forms.md) for when to use Tutorial,
Reference, Practice, and Perspective.

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

## Agent-Guided Course Generation

LearnLoop is not a hosted course platform. It is a local protocol for helping a learner's own agent generate better learning material.

The agent should think like an experienced teacher:

1. Understand the learner and the learning job.
2. Research sources and verify high-stakes claims.
3. Decide which modules are Tutorial, Reference, Practice, or Perspective.
4. Draft content supported by the design and evidence.
5. Self-review for unsupported claims, weak exercises, or private examples.
6. Run `learnloop validate`, `learnloop build`, and optionally `learnloop audit`.

For reusable or published courses, you can add a `.learnloop/` workspace to track sources, claims, and conflicts explicitly. For personal courses, agent-driven fact checking is enough.

See [Evidence And Sources](docs/evidence-and-sources.md) for optional source tracking.
See [Course Quality](docs/course-quality.md) for the release checklist and quality bar.

## CLI

```bash
learnloop init my-course
learnloop build courses/acp-fundamentals
learnloop validate courses/acp-fundamentals
learnloop audit courses/acp-fundamentals
learnloop context courses/acp-fundamentals --question-id <id>
learnloop start courses --port 8787
learnloop status courses
learnloop stop courses
learnloop serve courses --port 8787
learnloop templates courses/acp-fundamentals
```

## Development

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
learnloop validate courses/acp-fundamentals
learnloop build courses/acp-fundamentals
learnloop audit courses/acp-fundamentals
```

## Current Status

- ACP sample course migrated to Markdown/YAML source.
- Template-capable rendering pipeline with course- and module-level template selection.
- Perspective template for judgment, taste, and higher-level learning experience.
- Lightweight knowledge-state validation for verified claims and Perspective basis.
- Single local library service manages all courses under one port.
- Generated pages read course-local `config.js`, so questions use the correct course API.
- LearnLoop skill is normalized for agent-guided course generation and question answering.
- `.learnloop/` workspace is now optional; the default workflow relies on agent-driven fact checking.

Not included in the first version: accounts, cloud sync, multi-user spaces, hosted marketplaces, or a long-running cloud agent service.
