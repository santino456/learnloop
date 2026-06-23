# Evidence And Sources

LearnLoop does not need a heavy citation manager, but reusable courses need a
minimum evidence trail. The goal is simple: a learner or agent should be able
to tell which important claims are verified, inferred, conflicting, or waiting
for human review.

## Source Inventory

Record sources in `.learnloop/source_inventory.yaml`:

```yaml
sources:
  - id: official-docs
    type: official
    title: "Project documentation"
    location: "https://example.com/docs"
    trust: primary-source
    read_status: complete
```

Use stable `id` values. Claims that use `source_id` must reference one of these
ids.

## Claims Ledger

Record important technical or reusable claims in `.learnloop/claims.jsonl`:

```json
{"id":"claim-001","claim":"The generated HTML preserves section ids.","module_id":"m1","section_id":"m1-purpose","status":"verified","source_id":"local-source","checked_at":"2026-06-23"}
```

Allowed statuses:

- `verified`: supported by a reliable source, source code, runnable output, or
  user confirmation.
- `unverified`: not yet supported.
- `conflicting`: sources disagree.
- `needs-human-review`: depends on human taste, judgment, or private context.
- `agent-inference`: generated inference only.

`verified` claims must include `source_id` or `source`. Prefer `source_id`
because `learnloop validate` can check it against `source_inventory.yaml`.

## In-Course Source Notes

For normal prose, do not clutter every sentence. Add source notes when a claim
is important, surprising, version-sensitive, or likely to be reused:

```markdown
> Source note: claim-001, source `local-source`.
```

For Perspective content, cite the basis in words:

```markdown
依据：基于 claim-001 和本章练习观察；最终产品判断仍需 needs-human-review。
```

## Conflicts

If sources disagree, write the conflict to `.learnloop/conflicts.jsonl` instead
of silently choosing the convenient answer:

```json
{"id":"conflict-001","summary":"Two sources describe different protocol versions.","status":"open","sources":["docs-a","docs-b"]}
```

Then either resolve it with a stronger source or mark the course text as
unverified.
