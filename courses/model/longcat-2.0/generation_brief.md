# Generation Brief: LongCat-2.0 技术解读

This file is the first stop for any Agent generating or revising this course.

## Learner

- Audience: AI 工程师与研究人员
- Topic: 大规模 MoE 长上下文语言模型
- Current assumption: the learner wants a clear, trustworthy, practical course, not a generic article.

## Stage 1: Ask Better Questions

Before drafting, ask 2-4 content-derived questions that change the course shape. Good questions are about:

- learner background and target depth;
- which source materials are authoritative;
- whether the course is for personal study or public reuse;
- which parts require hands-on practice or judgment.

Do not ask a fixed questionnaire. If the user does not answer, choose a conservative default and mark optional advanced sections.

## Stage 2: Source And Evidence

If sources are local PDFs, Word documents, slide decks, Markdown, or text files,
put them in `raw/` and run:

```bash
learnloop ingest raw/<source-file> --course .
```

Use `.learnloop/materials/<source>/chunks.jsonl` and any generated `figures.md`
as the reading substrate. Do not cite `raw/*.pdf` as an image.

Update `.learnloop/source_inventory.yaml` with each source you actually read.

For each planned chapter, create an evidence pack in `.learnloop/evidence_packs/`:

- key facts with source links;
- uncertain or conflicting claims;
- useful diagrams, tables, commands, or examples;
- what should not be claimed yet.

Important claims can go into `.learnloop/claims.jsonl`. Verified claims need a source.

## Stage 3: Course Shape

Use `.learnloop/course_blueprint.md` and `.learnloop/chapter_briefs/` before editing `modules/*.md`.

The blueprint is not bureaucracy. It is the learning design contract: learner job,
module jobs, section-level learning actions, required evidence, and components.

Content form rules:

- Tutorial: first mental model, guided explanation, low cognitive load.
- Reference: source-grounded lookup tables, commands, fields, APIs, edge cases.
- Practice: checkable tasks with answers or expected reasoning.
- Perspective: judgment, taste, tradeoffs, quality signals, AI-use criteria.

If a form is not justified, omit it.

## Stage 4: HTML Learning Components

Use components only when they improve learning:

- `concept`: the mental model the learner must keep.
- `compare`: distinctions, alternatives, wrong/right, before/after.
- `evidence`: visible support for an important factual claim.
- `figure`: architecture, UI state, mechanism, visual evidence.
- `gallery`: before/after or wrong/right comparison.
- `flow`: data path, request path, lifecycle, causal chain.
- `timeline`: phases, staged execution, historical or operational sequence.
- `decision`: judgment practice; must include `--- perspective` or `--- answer`.

Images live in `assets/` and need meaningful alt text.

## Stage 5: Draft And Review

For each module:

1. Preserve stable section ids.
2. Cite external sources with Markdown links.
3. Avoid invented timelines, maturity claims, private names, or unsupported numbers.
4. Prefer concrete examples over abstract praise.
5. Add practice or perspective only when it has a real learning job.

## Stage 6: Validate

Run:

```bash
python3 -m learnloop validate .
python3 -m learnloop audit .
python3 -m learnloop build .
```

Then open the course through the local library server and check at least one desktop and one mobile-width view.
