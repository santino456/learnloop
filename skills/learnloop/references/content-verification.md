# Content Verification

Use this reference before adding technical claims, commands, APIs, protocol fields, version numbers, or runnable code.

## Verification Order

1. Prefer local source files, existing docs, and runnable commands.
2. Try the command or minimal code path when feasible.
3. For fast-moving technology, check current official documentation or release notes.
4. If a detail cannot be verified, mark it clearly in the course.

## Claim Status

Use `.learnloop/claims.jsonl` for important facts introduced during course generation:

- `verified`: supported by official docs, source code, runnable output, or user confirmation.
- `unverified`: not supported yet.
- `conflicting`: sources disagree.
- `needs-human-review`: depends on human taste, private context, or author judgment.
- `agent-inference`: generated inference only.

Never mark an `agent-inference` as `verified` without a real source. A `verified` claim must include `source_id` or `source`.

## Marking Unverified Details

Use plain text in Markdown:

```markdown
> Verification note: this field name may change. Check the current implementation before relying on it.
```

For Perspective content, write the basis directly:

```markdown
依据：基于本章已验证的 browser sandbox 约束；部署安全策略仍需 human review。
```

## Public Examples

Use fictitious project names and safe paths for publishable courses.

Recommended sample:

- Project: `CampusGuide`
- Path: `/workspace/campus-guide/README.md`
- Description: a fictional campus Q&A assistant

Do not include personal usernames, private repository names, local home paths, or private organization details in public sample content.
