# Release Checklist

Use this before tagging a public LearnLoop release.

## Local Checks

```bash
python3 -m unittest discover -s tests -v
learnloop --version
learnloop doctor courses
learnloop validate courses/mcp-fundamentals
learnloop build courses/mcp-fundamentals
learnloop audit courses/mcp-fundamentals
python3 -m build
```

Smoke test the wheel:

```bash
tmp=$(mktemp -d)
python3 -m venv "$tmp/venv"
"$tmp/venv/bin/python" -m pip install dist/*.whl
"$tmp/venv/bin/learnloop" --version
"$tmp/venv/bin/learnloop" init demo --target "$tmp/courses"
"$tmp/venv/bin/learnloop" validate "$tmp/courses/demo"
"$tmp/venv/bin/learnloop" build "$tmp/courses/demo"
"$tmp/venv/bin/learnloop" templates "$tmp/courses/demo"
"$tmp/venv/bin/learnloop" doctor "$tmp/courses"
```

## Public-Readiness Checks

- README quick start works for a fresh user.
- CI is green on `main`.
- MCP sample has current source links and no private paths or internal project names.
- `docs/content-forms.md`, `docs/evidence-and-sources.md`, and
  `docs/course-quality.md` match the current skill behavior.
- `CHANGELOG.md` has an entry for the release.

## Tag

```bash
git tag v0.1.0
git push origin v0.1.0
```

Create a GitHub release from the tag and summarize:

- local course library server;
- installable CLI;
- template-based rendering;
- question loop;
- quality and evidence gates;
- MCP flagship sample.
