# LearnLoop Orchestration

Quick reference for content-form decisions and subagent prompts.

## Content Form Rubric

### Tutorial
- Starts from likely confusion.
- Builds one clear mental model.
- Explains real mechanism, not labels.
- Uses examples or diagrams when they reduce cognitive load.
- Links to Reference for dense details.

### Reference
- Dense lookup material grounded in primary sources.
- Tables, boundary conditions, edge cases, failure modes.
- Citations for every external claim.
- No filler prose.

### Practice
- Trains a real skill with feedback.
- Ties back to a module objective.
- Avoid trivia unless recall is the goal.

### Perspective
- Develops judgment.
- Names tradeoffs, quality signals, bad smells.
- States the basis of each judgment.

## Subagent Prompts

```text
Use the LearnLoop skill. Your role is <role>.
Input: <paths or source list>.
Return only <artifact>. Do not edit modules/*.md or dist/.
Flag unsupported claims and content-form mismatches.
```

- **Researcher**: return sources, evidence, uncertainties, citations.
- **Architect**: propose module plan plus content-form decisions.
- **Reviewer**: find unsupported claims, fake Reference, weak Practice, empty Perspective, duplication.
- **Verifier**: check whether cited sources support the claims.

The main agent owns final merges and truth status.

## Optional Persistent Files

Use `.learnloop/` only when the course is technical, reusable, high-risk, or likely to be maintained:

- `source_inventory.yaml`
- `course_blueprint.md`
- `chapter_briefs/*.md`
- `evidence_packs/*.md`
- `claims.jsonl`
- `conflicts.jsonl`

Allowed claim statuses: `verified`, `unverified`, `conflicting`, `needs-human-review`, `agent-inference`.

Run `python3 -m learnloop audit <course-dir>` when `.learnloop/` is present or when the course is meant to be reused.
