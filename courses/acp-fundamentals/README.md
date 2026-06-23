# ACP Fundamentals

This is the flagship LearnLoop sample course for v0.1.

It demonstrates the full local learning loop:

```text
Markdown/YAML course source
-> generated HTML
-> section-level learner questions
-> agent-readable context
-> source improvements
```

## What It Shows

- **Tutorial**: `m1` introduces the client-to-agent integration problem.
- **Reference**: `m2` is a dense lookup module with protocol roles, message
  shape, transport notes, and failure modes.
- **Practice**: `m3`, `m4`, and `m6` use checkpoints and exercises to train
  operational understanding.
- **Perspective**: `m5`, `m7`, and `m8` extract protocol-choice judgment,
  integration taste, and AI-era engineering tradeoffs.

## Run It

From the repository root:

```bash
learnloop validate courses/acp-fundamentals
learnloop audit courses/acp-fundamentals
learnloop build courses/acp-fundamentals
learnloop start courses --port 8787
```

Then open `http://127.0.0.1:8787/course/acp-fundamentals/`.

## Public Example Policy

The course uses fictitious public examples such as `CampusGuide` and safe paths
such as `/workspace/campus-guide/README.md`. Do not add private project names,
home-directory paths, internal workflows, or real user data to this sample.
