---
name: learnloop
description: Work with LearnLoop local-first adaptive learning courses. Use when creating or updating LearnLoop course source, answering saved learner questions, or improving modules based on learner confusion.
---

# LearnLoop

LearnLoop is a local-first AI course compiler and adaptive learning package format. Its purpose is not to produce a perfect course in one shot, but to run a **learning loop**:

```text
sources + learner goal -> Markdown/YAML course -> local HTML
                          ^                                      |
                          |                                      v
                    improved source <- agent context <- learner questions
```

A course is a living artifact. The first build is the starting point; the real measure of quality is whether the loop converges. Learners read, get stuck, ask questions, and the course improves at exactly the places where they get stuck.

Your job is **learning design and epistemic control**. Do not optimize for fluent prose. Optimize for a learner who can actually understand, verify, practice, and judge the material after reading it.

## First Principles

1. **The course serves the learner, not the author.** Every paragraph, component, and exercise should be justifiable by a learner action: understand, compare, verify, practice, or judge. If it does not help the learner do one of those things, remove it.
2. **Confusion is signal.** Learner questions in `questions.jsonl` are the most valuable data. They reveal where the course's mental model diverges from the learner's mental model.
3. **Keep the main line short.** The primary narrative should be tight. Deep explanations, proofs, examples, and tangents belong in collapsible or attached components near the relevant point, not inlined into the main text.
4. **Earn trust, don't claim it.** Every explanation should be traceable: show the calculation, give a concrete example, cite the paper section, or provide a runnable check. Avoid hand-waving.
5. **Iterate locally, verify externally.** Use `validate`, `build`, `audit`, and tests as gates, but remember they only catch syntax and structure errors. The real test is a human reading the rendered page.

## The Shape of Good Explanation

A good explanation usually answers several of these questions, weighted by the learner's background and the module's learning job:

- **What** is it? (definition, boundary, name)
- **How** does it work? (mechanism, step-by-step process)
- **Why** is it true? (proof, derivation, causal story)
- **When** does it apply? (scope, assumptions, edge cases)
- **What if** it were different? (counterfactual, common mistake, failure mode)

Do not force every concept through all five layers. A high-level overview may need only *what* and *when*; a proof-heavy topic may need *why* above all. Let the learner's likely confusion decide the depth.

A practical heuristic: after drafting a section, ask *"If a learner got stuck here, what would they ask?"* Then add the answer as a `qa` or `concept` block near that point.

## Content Forms

Choose Tutorial, Reference, Practice, or Perspective because the learner needs that form, not because a sample course used it. A module can use only the forms it needs.

**Block support is unified across forms.** All standard blocks (paragraph, list, code, concept, compare, evidence, example, qa, exercise, checkpoint, etc.) are available in every template. Do not switch a module's template just to use a particular block. Instead, choose blocks based on the learning scene.

| Form | Learner need | Do | Don't |
|---|---|---|---|
| **Tutorial** | Build a mental model from confusion to clarity | Start from likely confusion; explain real mechanism; use examples and analogies that map exactly; link to Reference for details | Dump every fact, lookup table, or dense formula here |
| **Reference** | Look up specific facts repeatedly | Ground in sources; use tables, boundary conditions, edge cases, failure modes; cite every external claim | Write from memory; include narrative or judgment |
| **Practice** | Train a checkable skill | Give real problems with feedback; tie to module objective; train debugging, design, or retrieval | Use trivia unless recall itself is the goal |
| **Perspective** | Develop judgment | Name tradeoffs, quality signals, bad smells; state the basis of each judgment | Present agent opinion as standard answer |

Record form decisions in `.learnloop/course_blueprint.md` for non-trivial courses.

## Expert Teacher Workflow

Before drafting, reason through:

1. **Learner**: Who are they? What do they already know? What specific confusion or goal brings them here? Confirm language and set `lang` in `course.yaml`.
2. **Learning job**: What should the learner be able to understand or do after this module? One module, one job.
3. **Sources**: Which papers, docs, code, runnable output, or user context support the content?
4. **High-stakes claims**: Exact names, commands, APIs, protocol fields, versions, institutions. Verify these before writing.
5. **Design**: Module boundaries, content forms, section-level learning actions, evidence needs, and components.
6. **Draft**: Write only content supported by the design and evidence. Use semantic components instead of paragraphs when they expose structure.
7. **Fix and format**: Run `learnloop fix` and `learnloop fmt`.
8. **Build and inspect**: Run `validate`, `build`, `audit`. Then spot-check `dist/` for broken links, broken formulas, missing images, unsupported blocks rendered as "None", and other tool-induced bugs.
9. **Prepare for the question loop**: Identify likely confusion points and add `qa` or `concept` blocks there. Do not wait for questions.

For small personal courses, planning notes can stay in the conversation. For technical, reusable, or multi-module courses, persist them under `.learnloop/`.

## Semantic Components

Use components when they make the learning object clearer than another paragraph. All components work in every template; match the component to the learning scene, not the template name. Local images belong in `assets/`; remote images stay as links and are not downloaded.

| Component | Best scene | Avoid |
|---|---|---|
| `concept` | A self-contained idea the learner must hold in memory | Nesting one inside another (unsupported) |
| `evidence` | A quantitative or factual claim that needs a source | Subjective opinions or unsourced claims |
| `qa` | A likely learner question attached to the relevant section; works in Tutorial, Reference, Practice, or Perspective | A dump of all questions at the end of a module |
| `example` | A concrete, worked instance of an abstraction; especially useful in Reference and Perspective | Examples that do not map to the concept |
| `compare` | Side-by-side comparison of two ideas | More than two sides or decorative tables |
| `exercise` | Active practice with feedback | Passive reading disguised as a question |

Containers cannot be nested inside other containers. If you need a note inside a `concept`, close the `concept` first and place the note as a sibling block. For exact syntax, read `references/course-format.md`.

## Sources, Claims, and Verification

Truth beats fluency. Verify exact names, version-sensitive facts, commands, protocol fields, timelines, performance numbers, and project maturity before writing them. If the source does not prove a claim, mark it `unverified`, `needs-human-review`, or `agent-inference`. Never present `agent-inference` as settled fact.

The following claims should use an `::: evidence` component:

- Paper authors, institutions, and submission dates
- Performance numbers (speedup, accuracy, throughput, accepted length)
- Model parameters, training configs, and hardware requirements
- Commands, APIs, protocol fields, and version-sensitive facts

For important facts in reusable courses, also record them in `.learnloop/claims.jsonl`.

Read `references/content-verification.md` for the full verification standard.

## The Question Loop

Learner questions are the steering signal of the course. Treat them as seriously as the original sources.

### Receiving a question

1. Run `learnloop context <course-dir> --question-id <id>` to get the question, selected text, selected context, and section context.
2. Classify the question:
   - **Factual**: missing definition, number, or reference. Add the fact to the main text or an evidence block.
   - **Conceptual**: the learner lacks the mental model. Add a `qa` block with a concrete example, analogy, or derivation.
   - **Proof/derivation**: the learner wants to see why. Add a `qa` block with step-by-step math and a paper reference.
   - **Tool/UI**: the question is about the platform. Fix the LearnLoop code or instructions.
3. Write an answer artifact at `answers/<question-id>.md` with the restated question, detailed answer, references, and a note on where it belongs.

### Integrating the answer

1. Locate the relevant section using `section_id` from the question or selected context.
2. Add a `qa` block near the relevant paragraph:
   ```markdown
   ::: qa
   question: <exact learner question>
   section_id: <the-section-id>
   answer: |
     <detailed answer>
   :::
   ```
3. If the main text is misleading, fix the main text. Otherwise keep it tight and put the deeper explanation in the `qa` block.
4. If the same question appears repeatedly, promote the `qa` content into a `concept` block or inline it into the main narrative.

### Quality bar for answers

A good answer should contain at least one of the following:

- A concrete numerical example worked step by step
- A derivation or proof with each step justified
- A runnable command, code snippet, or configuration
- A precise citation (paper section, page, theorem, or official doc)
- An analogy that maps exactly to the technical mechanism

Do not settle for a one-sentence conceptual pointer.

Read `references/answering-loop.md` for the answer artifact template and detailed workflow.

## Optional `.learnloop/` Workspace

A `.learnloop/` workspace is optional. Use it when the course is shared, reusable, high-risk, or maintained by multiple people. It may contain:

- `course_blueprint.md` - learner goal, module plan, section actions, evidence, components.
- `source_inventory.yaml` - sources consulted.
- `claims.jsonl` - important claims with verification status.
- `conflicts.jsonl` - unresolved disagreements between sources.

For personal or quick courses, skip the workspace.

## Subagents

Subagents are optional speedups, not the method itself. Use them only for bounded work:

- **Researcher**: return sources, evidence, uncertainties, citations. Do not draft.
- **Architect**: propose module boundaries and content-form decisions. Do not write modules.
- **Reviewer**: find unsupported claims, fake Reference, weak Practice, empty Perspective, duplication.
- **Verifier**: check whether cited sources support the claims; downgrade unsupported claims.

The main agent owns final merges and truth status.

## Commands

```bash
learnloop validate <course-dir>
learnloop audit <course-dir>
learnloop build <course-dir>
learnloop fix <course-dir>
learnloop fmt <course-dir>
learnloop context <course-dir> --question-id <id>
learnloop scaffold-course <slug> --target courses
learnloop ingest <course-dir>/raw/<source-file> --course <course-dir>
learnloop start courses --port 8787
```

Use `python3 -m learnloop ...` only when the package is not installed. If you modify code under `learnloop/`, run `python3 -m unittest discover -s tests -v`.

## References

- `references/course-format.md` - file structure, YAML, Markdown section syntax, container syntax.
- `references/orchestration.md` - quick reference for content-form rubric and subagent prompts.
- `references/answering-loop.md` - answer artifact template and detailed question workflow.
- `references/content-verification.md` - verification standard for technical claims and entity facts.

## Guardrails

- Keep source edits in Markdown/YAML. Treat `dist/` as generated output.
- Preserve stable section ids; learner questions depend on them.
- Do not treat fluent generated text as verified knowledge.
- Prefer small course updates over broad rewrites.
- Do not require a `.learnloop/` workspace for every course.
- Do not nest containers inside other containers.
- Always build and spot-check the rendered HTML after structural changes.
- Choose blocks by the learning scene, not by template restrictions: all standard blocks are supported in every template.
