# LearnLoop Orchestration

Use this reference when turning raw material or a learner goal into course content. Keep the process lightweight: the agent should think like an experienced teacher, not fill out a long planning document.

## Pre-Draft Thinking

Before drafting, reason through:

- **Learner**: Who are they? What do they already know? What specific confusion or goal brings them here?
- **Learning job**: What should the learner be able to understand or do after this module? One module, one job.
- **Sources**: Which official docs, source code, runnable output, papers, or user context support the content?
- **High-stakes claims**: Exact commands, API names, protocol fields, version numbers, institution names. Verify these before writing.
- **Design**: Module plan, content-form decisions, and why each form is justified.

For small personal courses, these notes can stay in the conversation. For formal or reusable courses, you may persist them under `.learnloop/`.

Ask the user 2–4 focused questions before a substantial course, but only after you have read the sources and understood the material. The questions should be derived from the content itself, not from a standard questionnaire. Good questions surface choices that genuinely change the course: which prerequisite to assume, which angle to emphasize, which tradeoff to foreground, or which audience the examples should speak to.

If the user does not respond, do not stall. Fall back to a high-quality default: produce a complete course, keep the core path accessible, and mark advanced or skippable sections explicitly.

Before drafting, make an entity pass: list exact institution, project, repository, product, protocol, model, and person names that will appear in the course, and attach the source or user confirmation that fixes each name. Do not write a course around a guessed name.

## Content Form Rubric

Choose forms because the learner needs them, not because sample courses contain them.

### Tutorial

Use Tutorial for concepts, mental models, and narrative explanation.

A good Tutorial:

- starts from the learner's likely confusion;
- builds one clear mental model;
- explains the real mechanism, not just labels and high-level praise;
- uses examples or diagrams when they reduce cognitive load;
- avoids dense lookup tables unless the learner must repeatedly consult them;
- marks technical uncertainty instead of overclaiming;
- links to Reference modules when the learner may want to go deeper.

Do not dump every fact into Tutorial. If a topic is better covered as a source-grounded lookup surface, move it to Reference and link from Tutorial.

### Reference

Use Reference only for dense reusable lookup material that is grounded in primary sources.

Reference is justified when the content has several of:

- APIs, fields, methods, commands, formulas, symbols, source locations, or configuration keys;
- comparison tables, boundary conditions, edge cases, failure modes, or version-sensitive facts;
- explanations drawn from official docs, papers, or authoritative articles;
- facts the learner will likely revisit while doing work;
- enough source-backed detail that a normal explanation would become hard to scan.

Do not create Reference for simple explanations, summaries, or "what is X" content that you can only write from memory. Every external claim in Reference should be cited with a clickable Markdown link `[source name](URL)`. Label local materials as `本地`.

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

## Optional Persistent Files

Use `.learnloop/` only when the course is technical, reusable, high-risk, or likely to be maintained:

- `source_inventory.yaml`: source list and reliability notes.
- `course_blueprint.md`: learner goal, module plan, section actions, evidence, and components.
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
