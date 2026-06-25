# Course Quality

LearnLoop is useful only when generated courses are more reliable and more learnable than a generic long-form answer. A good course should pass three checks: truth, structure, and learning value.

## Truth

- Important factual claims are tied to sources, runnable output, source code, or explicit user confirmation.
- Unverified details are marked as unverified instead of written as settled facts.
- Perspective content states its basis and does not pretend to be a universal answer.

For reusable or published courses, consider adding a `.learnloop/` workspace to track sources, claims, and conflicts explicitly. For personal courses, agent-driven fact checking is enough.

## Structure

- `course.yaml` describes the learner, module order, and default template.
- Each module has stable section ids such as `m3-handshake`.
- Generated HTML lives in `dist/`; source edits happen in Markdown/YAML.
- Content forms are chosen intentionally:
  - Tutorial for explanation.
  - Reference for dense lookup.
  - Practice for checkable action.
  - Perspective for judgment and taste.

## Learning Value

- The course starts from the learner's likely confusion, not from the source material's table of contents.
- Each module has one job.
- Practice blocks train real skills or decisions.
- Reference modules are dense enough to be worth scanning.
- Perspective modules help the learner use AI and their own judgment better.

## Release Checklist

Before sharing a course:

```bash
learnloop validate <course-dir>
learnloop audit <course-dir>
learnloop build <course-dir>
```

Then open the course locally and check:

- the first screen makes the learning path obvious;
- question buttons target the right sections;
- no private names, paths, or internal examples remain;
- Reference, Practice, and Perspective are justified by the content.
