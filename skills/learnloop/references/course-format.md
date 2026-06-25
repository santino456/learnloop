# LearnLoop Course Format

Use this reference when creating, migrating, or repairing a LearnLoop course.

## Required Files

- `course.yaml`: course metadata and ordered module list.
- `modules/*.md`: editable course source.
- `assets/`: optional local images copied into generated `dist/course-assets/`.
- `questions.jsonl`: learner question log.
- `answers/`: agent answer artifacts and follow-up material.
- `raw/`: optional folder for original source artifacts such as papers, datasets, or official documents.
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

Markdown links are supported and rendered as clickable anchors:

```markdown
See the [React docs](https://react.dev) for details.
```

Use them for source citations and cross-module references.

Block images are rendered as figures. Local course images should live under
`assets/`:

```markdown
![KV Cache decode flow](assets/decode-flow.png)
```

Images must include useful alt text. During build, `assets/decode-flow.png` is
copied to `dist/course-assets/decode-flow.png` and the generated HTML points to
`course-assets/decode-flow.png`. `https://...` image URLs are preserved.

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

### Semantic Learning Components

Use components when they make the learning object clearer than another
paragraph. Keep them source-grounded; do not invent diagrams or image sources.

```markdown
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

C 是更成熟的判断：先看服务数量和环境一致性问题是否真的出现。
---
:::
```

`decision` must include `--- perspective` or `--- answer`; otherwise
`learnloop audit` reports it.

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
