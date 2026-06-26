# Content Verification

Use this reference before adding named entities, technical claims, commands, APIs, protocol fields, version numbers, timelines, or runnable code.

## Verification Order

1. Prefer local source files, existing docs, and runnable commands.
2. Try the command or minimal code path when feasible.
3. For fast-moving technology, check current official documentation or release notes.
4. If a detail cannot be verified, mark it clearly in the course.

## Entity Facts

Verify exact names before writing them. This includes institutions, companies,
projects, repositories, people, models, protocols, frameworks, products, and
organizations.

Use the strongest available source:

- official website or official documentation;
- local project files provided by the user;
- source code or package metadata;
- explicit user confirmation.

Do not translate, rename, abbreviate, or "correct" an entity from memory. If a
course uses a nickname, introduce it only after the verified full name.

For institutions and organizations, copy the exact name from the strongest
source you have and keep a source note nearby. If two names look similar, do
not guess which one is correct; mark the claim `needs-human-review` until the
user or an official source resolves it.

## Claim Status

For important facts introduced during course generation, mark the status in the prose or, for reusable courses, in `.learnloop/claims.jsonl`:

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
