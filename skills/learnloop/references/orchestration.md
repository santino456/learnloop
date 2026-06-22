# LearnLoop Orchestration

Use this reference when turning raw material or a learner goal into course content. Keep the process lightweight, but do not skip the thinking. The goal is not to create many intermediate files; the goal is to make the agent choose the right learning form and avoid unsupported generated lessons.

## Minimal Stage Notes

Before drafting, write short notes for:

```text
Intent:
- learner goal:
- background:
- desired outcome:
- exclusions:

Research:
- sources used:
- sources still needed:
- reliability notes:

Evidence:
- key supported facts:
- weak or unverified points:
- examples worth teaching:

Design:
- module plan:
- content form decisions:
- why Reference is or is not needed:
```

For small personal courses, these notes can stay in the conversation. For formal or reusable courses, persist them under `.learnloop/`.

## Content Form Rubric

Choose forms because the learner needs them, not because sample courses contain them.

### Tutorial

Use Tutorial for concepts, mental models, and narrative explanation.

A good Tutorial:

- starts from the learner's likely confusion;
- builds one clear mental model;
- uses examples or diagrams when they reduce cognitive load;
- avoids dense lookup tables unless the learner must repeatedly consult them;
- marks technical uncertainty instead of overclaiming.

### Reference

Use Reference only for dense reusable lookup material.

Reference is justified when the content has several of:

- APIs, fields, methods, commands, formulas, symbols, source locations, or configuration keys;
- comparison tables, boundary conditions, edge cases, failure modes, or version-sensitive facts;
- facts the learner will likely revisit while doing work;
- enough source-backed detail that a normal explanation would become hard to scan.

Do not create Reference for simple explanations, summaries, or "what is X" material. If it is not dense enough to be a useful lookup surface, keep it in Tutorial.

A good Reference:

- is structured for lookup, not storytelling;
- has tables or clearly grouped facts;
- includes constraints, edge cases, and failure modes;
- includes citations or source notes for important technical facts;
- avoids filler prose.

### Practice

Use Practice when the learner needs to do something checkable.

A good Practice block:

- trains a real skill, calculation, debugging move, design choice, or retrieval step;
- has an answer, feedback, or expected reasoning;
- is not a trivia quiz unless recall itself is the learning goal;
- ties back to a concrete module objective.

### Perspective

Use Perspective to extract higher-level human judgment from the learned material.

A good Perspective:

- explains how the learner's judgment should change;
- names quality signals, bad smells, tradeoffs, or AI-use acceptance criteria;
- states its basis: verified claims, practice observations, author experience, or `needs-human-review`;
- avoids pretending that agent opinion is a standard answer.

## Subagents

Subagents are optional speedups, not the soul of LearnLoop. Use them when the work benefits from parallelism or independent review.

Good subagent tasks:

```text
Researcher: read these sources and return only sources, evidence, uncertainties, and citations.
Architect: inspect the intent/evidence and propose module plan plus content-form decisions; do not draft.
Reviewer: inspect this draft for unsupported claims, fake Reference, weak Practice, and empty Perspective.
Verifier: check whether cited sources support the claims; downgrade unsupported claims.
```

Minimal prompt:

```text
Use the LearnLoop skill. Your role is <role>.
Input: <paths or source list>.
Return only <artifact>. Do not edit modules/*.md or dist/.
Flag unsupported claims and content-form mismatches.
```

The main agent owns final merges and may perform all stages alone for small courses.

## Persistent Files

Use `.learnloop/` when the course is technical, reusable, high-risk, or likely to be maintained:

- `source_inventory.yaml`: source list and reliability notes.
- `course_architecture.md`: learner goal, module plan, and content-form decisions.
- `chapter_briefs/*.md`: chapter boundaries when the course is large.
- `evidence_packs/*.md`: source-grounded evidence for technical chapters.
- `claims.jsonl`: key claims and status.
- `conflicts.jsonl`: unresolved source conflicts.

Allowed claim statuses:

- `verified`: supported by official docs, source code, runnable output, or user confirmation.
- `unverified`: not supported by a reliable source yet.
- `conflicting`: sources disagree.
- `needs-human-review`: requires author judgment, taste, or private context.
- `agent-inference`: generated inference only; never present as a settled fact.

Run `python3 -m learnloop audit <course-dir>` when `.learnloop/` is present or when the course is meant to be reused.
