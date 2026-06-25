# Evidence And Sources

LearnLoop expects content to be trustworthy, but it does not force every course through a heavy citation workflow. The default workflow is light: the agent behaves like a careful teacher and marks uncertainty where it matters.

## Default: agent-driven fact checking

When generating or updating a course, the agent should:

1. **Identify high-stakes claims** — exact commands, API names, protocol fields, version numbers, institution names, performance numbers, timelines.
2. **Check those claims against reliable sources** — official docs, source code, runnable output, papers, or the user's own current context.
3. **Mark uncertainty** — use phrasing like "据官方文档..." or "这一点还需要验证" instead of presenting guesses as settled facts.
4. **Separate judgment from fact** — Perspective content must state its basis (experience, observations, or `needs-human-review`).

For most personal courses, this is enough.

## Optional: persistent knowledge state

If you are building a reusable or published course, you can add a `.learnloop/` workspace to track evidence more explicitly:

- `source_inventory.yaml` — list of sources used.
- `claims.jsonl` — important claims with status (`verified`, `unverified`, `conflicting`, `needs-human-review`, `agent-inference`).
- `conflicts.jsonl` — sources that disagree.

These files are validated when present, but they are **not required**.

### In-course source notes

For normal prose, do not clutter every sentence. Add a source note when a claim is important, surprising, version-sensitive, or likely to be reused.

Reference modules must cite external sources with clickable Markdown links:

```markdown
> 来源：[React 官方文档 — Thinking in React](https://react.dev/learn/thinking-in-react)。
```

For local materials, label them explicitly:

```markdown
> 来源：本地 m7《部署与运维：从本机到线上》。
```

For Perspective content, cite the basis in words:

```markdown
依据：基于本章已验证的 browser sandbox 约束。
```

## Source artifacts in `raw/`

When a course is built from an external source such as a paper, dataset, or official document, keep the original artifact in a `raw/` folder inside the course directory:

```text
courses/<course-slug>/
  raw/
    lifescibench_preprint.pdf
  course.yaml
  modules/
```

This makes the source inspectable alongside the generated modules and keeps the provenance clear. Modules should still cite the specific section, table, or figure they rely on, rather than pointing vaguely at the artifact.

## When to add the full workspace

Add `.learnloop/` only when:

- The course will be shared or published.
- Multiple agents or people will edit it over time.
- The topic has conflicting sources that need to be tracked.

For a quick personal course, skip it.
