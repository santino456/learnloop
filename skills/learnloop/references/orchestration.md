# LearnLoop Orchestration

Use this reference when turning raw material or a learner goal into course content.

## Main Agent Responsibility

The main agent is responsible for epistemic control, whether or not subagents are used. Do not start by writing polished lessons. Start by making the knowledge state explicit:

- What sources exist.
- Which parts were read.
- Which claims are verified, inferred, conflicting, or need human review.
- Which chapter owns each learning goal.
- Which content is Tutorial, Reference, Practice, or Perspective.

Subagents are optional speedups. Use them for parallel research, draft, or review only when the task is large enough. A single capable main agent can perform the same workflow sequentially.

## Stage Gates

Follow these gates in order:

1. **Intent gate**: write the learner goal, background, desired outcome, and exclusions.
2. **Source gate**: list sources before drafting. Prefer official docs, papers, source code, and runnable checks.
3. **Evidence gate**: write evidence packs with `## Sources` and `## Evidence`.
4. **Architecture gate**: write `.learnloop/course_architecture.md` with `Learner Goal`, `Module Plan`, and `Content Form Decisions`.
5. **Draft gate**: only now write `modules/*.md`.
6. **Audit gate**: run `python3 -m learnloop audit <course-dir>`, then validate and build.

## Knowledge State Files

Store orchestration artifacts under `.learnloop/`:

- `source_inventory.yaml`: sources, source type, trust level, location, and read status.
- `course_architecture.md`: learner goal, module plan, and content form decisions.
- `chapter_briefs/*.md`: chapter goal, boundaries, inputs, adjacent context, and output expectations.
- `evidence_packs/*.md`: source-grounded evidence, runnable checks, unresolved questions, and claim candidates.
- `claims.jsonl`: key facts, source ids, module/section ids, status, and check date.
- `conflicts.jsonl`: unresolved source conflicts and current decision.

Allowed claim statuses:

- `verified`: supported by official docs, source code, runnable output, or user confirmation.
- `unverified`: not supported by a reliable source yet.
- `conflicting`: sources disagree.
- `needs-human-review`: requires author judgment, taste, or private context.
- `agent-inference`: generated inference only; never present as a settled fact.

## Content Form Decisions

Choose forms because the learner needs them, not because sample courses contain them:

- **Tutorial**: use for concepts, mental models, and narrative explanation.
- **Reference**: use only for dense reusable lookup material: APIs, fields, formulas, commands, terminology, edge cases, comparison tables, or source-backed facts. If the content is just a simple explanation, keep it in Tutorial.
- **Practice**: use for checkable skills, calculations, debugging, implementation choices, or retrieval practice.
- **Perspective**: use for higher-level judgment, taste, tradeoffs, failure smells, and how to use AI better after learning the topic.

It is valid for a course to have no Reference module. It is also valid for a chapter to combine explanation, small checks, and a short Perspective block in one module.

## Chapter-Sharded Workflow

1. Create or update source inventory.
2. Split the learning goal by chapter, not by template.
3. For each chapter, write a chapter brief with a clear ownership boundary.
4. Read assigned materials and write an evidence pack before drafting.
5. Draft the chapter from the evidence pack. A chapter may include Tutorial, Reference, Practice, and Perspective layers together, but only if each form is justified in the architecture.
6. Review the draft for unsupported claims, repeated content, chapter drift, weak practice, and empty Perspective.
7. The main agent merges only reviewed content into `modules/*.md`.
8. Run validate and build.

## Optional Subagent Pattern

When using subagents, give each one a bounded task:

- Research task: read only assigned sources and produce an evidence pack with citations.
- Architecture task: inspect evidence and propose content-form decisions; do not draft.
- Draft task: use one evidence pack and one chapter brief to produce a chapter draft.
- Review task: inspect one draft against the brief, evidence pack, claims, and content-form decisions.

Do not ask subagents to read the whole course unless the task is a whole-course review. Do not allow subagents to write final source files directly.

Minimal subagent prompt:

```text
Use the LearnLoop skill. Your role is <researcher|architect|draft reviewer>.
Input files: <paths>.
Return only the requested artifact. Do not edit modules/*.md or dist/.
Flag unsupported claims and content-form mismatches.
```

## Perspective Layer

Perspective is not a scenario template and not a standard answer. It extracts higher-level experience from the chapter:

- How judgment should change after learning the material.
- What beginners commonly misread.
- What quality signals or bad smells matter.
- How a human can use AI with better intent, taste, verification, and acceptance criteria.

Every Perspective block must state its basis, such as verified claims, practice observations, author experience, or `needs-human-review`.
