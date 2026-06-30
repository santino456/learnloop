# MCP Fundamentals

This is the flagship LearnLoop sample course for v0.1.

It demonstrates why LearnLoop is more than rendered Markdown:

- **Tutorial**: `m1` builds the first mental model with a figure and flow.
- **Reference**: `m2` is a source-linked lookup surface for MCP primitives.
- **Practice**: `m3` trains primitive selection with checkpoints and exercises.
- **Tutorial + media**: `m4` uses gallery, timeline, and flow components for transport and lifecycle.
- **Perspective**: `m5` trains engineering judgment around security, reuse, and scope.

## Run It

From the repository root:

```bash
learnloop validate courses/mcp-fundamentals
learnloop audit courses/mcp-fundamentals
learnloop build courses/mcp-fundamentals
learnloop start courses --port 8787
```

Then open `http://127.0.0.1:8787/course/mcp-fundamentals/`.

## Source Policy

The course uses official Model Context Protocol documentation as its source
base. Important protocol claims should cite the relevant official page or be
tracked in `.learnloop/claims.jsonl`.

Keep examples fictional and public. Do not add private project names,
home-directory paths, internal workflows, or real user data to this sample.
