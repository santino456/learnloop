# LearnLoop Course Format

Use this reference when creating, migrating, or repairing a LearnLoop course. For the pedagogical reasoning behind forms and components, read the main `SKILL.md`.

## Required Files

- `course.yaml`: course metadata and ordered module list.
- `modules/*.md`: editable course source.
- `assets/`: optional local images copied into generated `dist/course-assets/`.
- `questions.jsonl`: learner question log.
- `answers/`: agent answer artifacts and follow-up material.
- `raw/`: optional folder for original source artifacts such as papers, datasets, or official documents.
- `.learnloop/`: optional orchestration workspace.
- `.learnloop/materials/`: generated material packs from `learnloop ingest`.
- `dist/`: generated HTML output.

For new source-grounded courses, prefer:

```bash
learnloop scaffold-course my-course --target courses
```

Use `learnloop init` only for a minimal blank course.

## course.yaml

```yaml
id: acp-fundamentals
title: "ACP Fundamentals"
subtitle: "Short course promise."
audience: "Target learner."
default_port: 8787
template: tutorial
lang: auto
prerequisites:
  - "What the learner should already know before starting."
modules:
  - id: m1
    title: "What ACP is"
    file: "modules/01.md"
    summary: "One-sentence module summary."
```

- `template` sets the default rendering template. It can be overridden per module.
- `lang` controls UI label language: `zh`, `en`, or `auto`.
- `prerequisites` should be concrete and checkable.
- Keep module ids short and stable.

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

Questionable sections use this heading syntax:

```markdown
## [m1-problem] The integration problem
```

Section ids must be unique across the course. Do not rename them after learners have submitted questions unless you also migrate `questions.jsonl`.

Markdown links are supported. In "延伸阅读" sections, prefer internal links to other modules over bare external links.

Local images live under `assets/`:

```markdown
![KV Cache decode flow](assets/decode-flow.png)
```

For source PDFs and documents, do not point image components at `raw/*.pdf`. Run `learnloop ingest <raw-file> --course <course-dir>` first.

## Container Syntax

```markdown
::: exercise
Write a minimal bridge responsibility list.

- List item inside the exercise.
:::

::: checkpoint
Explain why a browser cannot spawn a local subprocess.
:::
```

Perspective exercises use an exercise container with a `--- perspective` section:

```markdown
::: exercise
Judge whether this integration needs a local bridge.

--- perspective
依据：基于本章关于 browser sandbox 和 local bridge 的 verified claims。

A mature implementation treats the bridge as the trust boundary.
---
:::
```

## Semantic Learning Components

```markdown
::: concept
title: KV Cache
why: Decode becomes cheap only if old keys and values are reused.

The cache is the stored attention state from prior tokens.
:::

::: compare
left: No cache
right: KV cache

- Decode cost | Recompute old tokens | Append only the new token
- Memory use | Lower | Higher
:::

::: evidence
claim: Decode appends one token at a time.
source: [Local notes](raw/notes.md)
status: verified
basis: 本地材料 chunk 2.
:::

::: figure
src: assets/decode-flow.png
alt: KV Cache decode flow
caption: Decode 阶段每次只追加一个 token 的 KV。
source: 本地示意图
:::

::: gallery
- assets/before.png | Before | 没有 cache 的重复计算
- assets/after.png | After | 复用 KV 后的路径
:::

::: flow
用户输入 -> React UI -> FastAPI -> Agent Loop -> SSE -> 浏览器渲染
:::

::: timeline
- Prefill | 一次性处理 prompt，生成初始 KV
- Decode | 每步追加新 token 的 KV
- Evict/Compact | 长上下文时管理显存压力
:::

::: decision
Should this project use Docker now?

- A. Yes, immediately
- B. Not necessarily
- C. Only after multiple services appear

--- perspective
依据：基于部署复杂度、隔离需求和当前团队维护成本。

C 是更成熟的判断。
---
:::

::: qa
question: Why is decode serial?
section_id: m1-problem
answer: |
  Because each new token depends on the previous one.
:::
```

`concept` needs `title` and either `why` or body text. `compare` needs `left`, `right`, and at least one row. `evidence` needs `claim`, `source`, and `status`.

`decision` must include `--- perspective` or `--- answer`.

Containers cannot be nested inside other containers.

## Templates

Built-in templates are `tutorial`, `reference`, `practice`, and `perspective`. Each contains:

- `manifest.yaml`: metadata and supported block types.
- `template.html`: page shell.
- `style.css`: template styles.
- `runtime.js`: question button and drawer logic.

Check `manifest.yaml` before using a block type. Unsupported blocks may render as "None" or plain text.

## Generated Output

```bash
python3 -m learnloop build <course-dir>
```

Do not hand-edit `dist/` unless debugging generated output.
