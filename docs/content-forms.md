# Content Forms

LearnLoop courses use four content forms. Pick the form that matches the
learner's job; do not copy a sample course structure by habit.

## Tutorial

Use Tutorial when the learner needs an explanation, mental model, or guided
path through unfamiliar material.

Good Tutorial content:

- starts from a likely confusion;
- introduces one idea at a time;
- uses examples only when they reduce cognitive load;
- turns mechanisms into `figure`, `flow`, or `timeline` components when a visual
  sequence would reduce mental load;
- marks uncertainty instead of sounding definitive without evidence;
- links to Reference modules when the learner may want to go deeper.

Do not use Tutorial as a dumping ground for every fact. Dense lookup material
belongs in Reference.

## Reference

Use Reference when the learner needs a source-grounded deep dive that they can read as a self-contained entry point, or look up repeatedly.

Reference is justified by dense material such as:

- APIs, fields, commands, formulas, symbols, source locations, or config keys;
- comparison tables, version-sensitive details, edge cases, and failure modes;
- explanations drawn from official docs, papers, or authoritative articles;
- curated links that replace the need to hunt through primary sources.

Every external claim in a Reference module should be backed by a source. Use
Markdown links `[source name](URL)` so the source is both cited and clickable.
For local materials, label them explicitly as `本地`.

Do not create Reference for simple explanations, summaries, or "what is X"
content that you could only write from memory. If it does not cite primary
sources or provide dense lookup value, it is probably Tutorial.

## Practice

Use Practice when the learner must do something checkable.

Good Practice trains:

- debugging moves;
- calculations;
- implementation steps;
- retrieval from memory;
- design choices with expected reasoning.

Practice should include answers, feedback, or expected reasoning. Avoid trivia
unless recall is the actual learning goal.

Use `decision` blocks when the learner is practicing a design choice or
operational judgment. Use ordinary `exercise` blocks for checkable recall,
debugging, implementation, or calculation.

## Perspective

Use Perspective when the chapter can teach judgment, taste, or higher-level
experience beyond the factual material.

Good Perspective names:

- quality signals;
- bad smells;
- tradeoffs;
- when to use AI and when to distrust the output;
- what a mature practitioner would notice.

Perspective must state its basis: verified claims, practice observations,
author experience, or `needs-human-review`. Do not present agent opinion as a
standard answer.

Use `decision` blocks for Perspective when there is a concrete fork in the road:
several plausible choices, a rationale, and a reusable judgment the learner can
practice. If there is no real choice, write a concise paragraph instead.
