# Contributing

LearnLoop is an early local-first learning tool. Keep contributions small,
verifiable, and aligned with the core loop:

```text
course source -> generated HTML -> learner questions -> agent context -> improved source
```

## Development

Run the checks before opening a pull request:

```bash
python3 -m unittest discover -s tests -v
python3 -m learnloop validate courses/mcp-fundamentals
python3 -m learnloop build courses/mcp-fundamentals
python3 -m learnloop audit courses/mcp-fundamentals
```

If you change the LearnLoop skill inside Codex and have the system skill
validator available, also run `quick_validate.py` against `skills/learnloop`.

## Design Rules

- Prefer local files over cloud services.
- Keep the CLI stable and boring.
- Do not add accounts, hosted sync, or marketplace behavior to core.
- Treat generated HTML as build output; edit Markdown/YAML source instead.
- Do not mark agent guesses as verified course facts.
- Use Reference only for dense lookup material, not ordinary explanation.
