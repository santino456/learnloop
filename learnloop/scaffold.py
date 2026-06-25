from __future__ import annotations

from pathlib import Path

from .model import LearnLoopError


def scaffold_course(
    target: Path,
    slug: str,
    title: str | None = None,
    topic: str | None = None,
    audience: str | None = None,
) -> Path:
    course_dir = target / slug
    if course_dir.exists():
        raise LearnLoopError(f"Course already exists: {course_dir}")

    title = title or _title_from_slug(slug)
    topic = topic or title
    audience = audience or "Learners who want a clear, source-grounded technical course."

    (course_dir / "modules").mkdir(parents=True)
    (course_dir / "answers").mkdir()
    (course_dir / "assets").mkdir()
    (course_dir / "raw").mkdir()
    (course_dir / ".learnloop" / "chapter_briefs").mkdir(parents=True)
    (course_dir / ".learnloop" / "evidence_packs").mkdir()

    (course_dir / "questions.jsonl").write_text("", encoding="utf-8")
    (course_dir / ".learnloop" / "claims.jsonl").write_text("", encoding="utf-8")
    (course_dir / ".learnloop" / "conflicts.jsonl").write_text("", encoding="utf-8")

    _write_course_yaml(course_dir, slug, title, audience)
    _write_starter_module(course_dir, title, topic)
    _write_generation_brief(course_dir, title, topic, audience)
    _write_source_inventory(course_dir)
    _write_course_architecture(course_dir, title)
    _write_chapter_brief(course_dir)
    _write_readmes(course_dir)
    return course_dir


def _title_from_slug(slug: str) -> str:
    words = [part for part in slug.replace("_", "-").split("-") if part]
    return " ".join(word.capitalize() for word in words) or "New LearnLoop Course"


def _write_course_yaml(course_dir: Path, slug: str, title: str, audience: str) -> None:
    (course_dir / "course.yaml").write_text(
        f"""id: {slug}
title: "{title}"
subtitle: "A source-grounded LearnLoop course scaffold."
audience: "{audience}"
default_port: 8787
template: tutorial
modules:
  - id: m1
    title: "Course Design Brief"
    file: "modules/01.md"
    summary: "Clarify the learner, sources, and first course plan before drafting."
""",
        encoding="utf-8",
    )


def _write_starter_module(course_dir: Path, title: str, topic: str) -> None:
    (course_dir / "modules" / "01.md").write_text(
        f"""---
id: m1
title: "Course Design Brief"
summary: "Clarify the learner, sources, and first course plan before drafting."
---

## [m1-learning-job] Learning job

This scaffold is for **{title}**.

Before writing the final course, define the learner's job in one sentence:

> After this course, the learner should be able to understand or do what?

## [m1-source-plan] Source plan

Start by adding reliable sources to `.learnloop/source_inventory.yaml`.

For **{topic}**, prefer official documentation, source code, runnable output, papers, or user-provided materials. Mark anything else as unverified.

::: checkpoint
Can you name the first two reliable sources this course should use?

--- answer
Add them to `.learnloop/source_inventory.yaml`, then summarize what each source proves in `.learnloop/evidence_packs/`.
---
:::

## [m1-course-shape] Course shape

Use `generation_brief.md` to decide module boundaries before drafting. A strong LearnLoop course usually mixes:

- Tutorial for the first mental model.
- Reference only when dense lookup value is real.
- Practice for checkable skills.
- Perspective for judgment and tradeoffs.

::: decision
Should the first draft immediately become a long polished module?

- A. Yes, write the full lesson now.
- B. No, first collect sources and choose the module shape.
- C. Only if the user explicitly asked for a quick personal note.

--- perspective
依据：基于 LearnLoop 的课程生成规范。可复用课程需要先明确 learner job、sources、chapter boundaries 和 content forms；否则很容易写出流畅但空洞的长文。

B 是默认选择。C 可以用于个人速记，但应标注未验证内容。
---
:::
""",
        encoding="utf-8",
    )


def _write_generation_brief(
    course_dir: Path, title: str, topic: str, audience: str
) -> None:
    (course_dir / "generation_brief.md").write_text(
        f"""# Generation Brief: {title}

This file is the first stop for any Agent generating or revising this course.

## Learner

- Audience: {audience}
- Topic: {topic}
- Current assumption: the learner wants a clear, trustworthy, practical course, not a generic article.

## Stage 1: Ask Better Questions

Before drafting, ask 2-4 content-derived questions that change the course shape. Good questions are about:

- learner background and target depth;
- which source materials are authoritative;
- whether the course is for personal study or public reuse;
- which parts require hands-on practice or judgment.

Do not ask a fixed questionnaire. If the user does not answer, choose a conservative default and mark optional advanced sections.

## Stage 2: Source And Evidence

Update `.learnloop/source_inventory.yaml` with each source you actually read.

For each planned chapter, create an evidence pack in `.learnloop/evidence_packs/`:

- key facts with source links;
- uncertain or conflicting claims;
- useful diagrams, tables, commands, or examples;
- what should not be claimed yet.

Important claims can go into `.learnloop/claims.jsonl`. Verified claims need a source.

## Stage 3: Course Shape

Use `.learnloop/course_architecture.md` and `.learnloop/chapter_briefs/` before editing `modules/*.md`.

Content form rules:

- Tutorial: first mental model, guided explanation, low cognitive load.
- Reference: source-grounded lookup tables, commands, fields, APIs, edge cases.
- Practice: checkable tasks with answers or expected reasoning.
- Perspective: judgment, taste, tradeoffs, quality signals, AI-use criteria.

If a form is not justified, omit it.

## Stage 4: HTML Learning Components

Use components only when they improve learning:

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
""",
        encoding="utf-8",
    )


def _write_source_inventory(course_dir: Path) -> None:
    (course_dir / ".learnloop" / "source_inventory.yaml").write_text(
        """sources:
  # - id: official-docs
  #   type: official
  #   title: "Official documentation"
  #   url: "https://example.com/docs"
  #   status: unread
""",
        encoding="utf-8",
    )


def _write_course_architecture(course_dir: Path, title: str) -> None:
    (course_dir / ".learnloop" / "course_architecture.md").write_text(
        f"""# Course Architecture: {title}

## Course Promise

Write one sentence describing what the learner can do after the course.

## Proposed Modules

| Module | Form | Learning job | Sources | Components |
|--------|------|--------------|---------|------------|
| m1 | Tutorial | Establish the first mental model | TBD | flow/figure if useful |
| m2 | Reference | Provide dense lookup value if justified | TBD | table/figure |
| m3 | Practice | Train a checkable skill | TBD | exercise/decision |
| m4 | Perspective | Extract judgment and tradeoffs | TBD | decision |

## Open Questions

- What should be excluded from the first version?
- Which facts are version-sensitive?
- Which examples need human confirmation?
""",
        encoding="utf-8",
    )


def _write_chapter_brief(course_dir: Path) -> None:
    (course_dir / ".learnloop" / "chapter_briefs" / "m1.md").write_text(
        """# Chapter Brief: m1

## Boundary

One chapter, one learning job. Define it here before drafting.

## Inputs

- Sources:
- Prior learner context:
- Adjacent modules:

## Output Requirements

- Stable section ids using `m1-...`.
- Clear content form choice.
- Claims backed by evidence or marked unverified.
- Components only when they improve understanding.

## Review Checklist

- Is this chapter specific enough to teach?
- Are citations present for external claims?
- Does every exercise or decision have feedback?
""",
        encoding="utf-8",
    )


def _write_readmes(course_dir: Path) -> None:
    (course_dir / "assets" / "README.md").write_text(
        """# Assets

Put local course images here. Reference them from Markdown as `assets/name.png`.
LearnLoop copies them to `dist/course-assets/` during build.
""",
        encoding="utf-8",
    )
    (course_dir / "raw" / "README.md").write_text(
        """# Raw Materials

Put PDFs, source excerpts, datasets, notes, or other original materials here.
Do not cite raw files as verified unless the Agent has actually read them.
""",
        encoding="utf-8",
    )
    (course_dir / ".learnloop" / "evidence_packs" / "README.md").write_text(
        """# Evidence Packs

Create one file per chapter after reading sources. Evidence packs should collect:

- sourced claims;
- useful examples;
- uncertainties;
- conflicts;
- items needing human review.
""",
        encoding="utf-8",
    )
