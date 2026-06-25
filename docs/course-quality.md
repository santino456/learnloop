# Course Quality

LearnLoop is useful only when generated courses are more reliable and more learnable than a generic long-form answer. A good course should pass three checks: truth, structure, and learning value.

The bar is not "valid Markdown that builds into HTML." The bar is: a careful
learner can read the course, trust the important claims, see the structure, and
practice the judgment or skill the topic actually requires.

## Good Course Standard

A reusable LearnLoop course should have:

- a clear learner job, not a topic dump;
- source-grounded claims for names, APIs, commands, versions, timelines, and protocol fields;
- module boundaries that reduce cognitive load;
- Reference only when it contains dense lookup value;
- Practice that trains a checkable skill or decision;
- Perspective that names real tradeoffs, quality signals, and basis;
- HTML components that clarify mechanisms, comparisons, or judgment;
- no private paths, private project names, or invented project history.

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

## HTML Learning Value

HTML should do more than make Markdown prettier.

Use components when they change how fast or deeply the learner understands:

- `figure`: architecture, UI state, data structure, visual evidence.
- `gallery`: before/after, wrong/right, two competing designs.
- `flow`: request path, lifecycle, causal chain, data movement.
- `timeline`: phases, version evolution, staged execution, operational sequence.
- `decision`: tradeoff training with a visible author perspective or answer.

Do not add components as decoration. A component is weak if it repeats the
previous paragraph without adding structure, comparison, or judgment.

## Bad Smells

Stop and revise when you see:

- a long first module that says "overview" but teaches no concrete model;
- Reference that only answers simple "what is X" questions;
- Practice with no answer, feedback, or expected reasoning;
- Perspective that sounds wise but has no basis;
- exact names, dates, versions, or protocol fields written from memory;
- generated claims about project age, adoption, maturity, or performance with no source;
- components that look nice but do not reduce confusion;
- repeated content across Tutorial, Reference, Practice, and Perspective.

## Human Review Questions

Before calling a course good, answer:

1. What should the learner be able to do after this course?
2. Which claims would be embarrassing if wrong?
3. Which section would a learner most likely ask about?
4. Which Reference table is actually worth returning to?
5. Which Practice block changes learner behavior?
6. Which Perspective block teaches judgment rather than opinion?
7. Which component could be removed without losing learning value?

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
