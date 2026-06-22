from __future__ import annotations

import html
import json
import re
import shutil
import socket
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SECTION_RE = re.compile(r"^(#{2,3})\s+\[([a-zA-Z0-9_-]+)\]\s+(.+?)\s*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)


@dataclass
class Module:
    id: str
    title: str
    file: str
    summary: str = ""


@dataclass
class Course:
    root: Path
    id: str
    title: str
    subtitle: str
    audience: str
    default_port: int
    modules: list[Module]


class LearnLoopError(Exception):
    pass


def read_course(course_dir: Path) -> Course:
    course_dir = course_dir.resolve()
    course_file = course_dir / "course.yaml"
    if not course_file.exists():
        raise LearnLoopError(f"Missing course.yaml in {course_dir}")

    data = parse_course_yaml(course_file.read_text(encoding="utf-8"))
    modules = [
        Module(
            id=str(item["id"]),
            title=str(item["title"]),
            file=str(item["file"]),
            summary=str(item.get("summary", "")),
        )
        for item in data.get("modules", [])
    ]
    if not modules:
        raise LearnLoopError("course.yaml must define at least one module")

    return Course(
        root=course_dir,
        id=str(data.get("id", course_dir.name)),
        title=str(data.get("title", course_dir.name)),
        subtitle=str(data.get("subtitle", "")),
        audience=str(data.get("audience", "")),
        default_port=int(data.get("default_port", 8787)),
        modules=modules,
    )


def parse_course_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    modules: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_modules = False

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("modules:"):
            in_modules = True
            data["modules"] = modules
            continue
        if in_modules:
            if raw.startswith("  - "):
                current = {}
                modules.append(current)
                key, value = raw[4:].split(":", 1)
                current[key.strip()] = strip_yaml_value(value)
            elif raw.startswith("    ") and current is not None:
                key, value = raw.strip().split(":", 1)
                current[key.strip()] = strip_yaml_value(value)
            elif not raw.startswith(" "):
                in_modules = False
        if not in_modules and ":" in raw:
            key, value = raw.split(":", 1)
            data[key.strip()] = strip_yaml_value(value)

    return data


def strip_yaml_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_module(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    frontmatter = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = strip_yaml_value(value)
    return frontmatter, match.group(2)


def build_course(course_dir: Path) -> Path:
    course = read_course(course_dir)
    dist = course.root / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    (dist / "assets").mkdir(parents=True)

    (dist / "assets" / "learnloop.css").write_text(CSS, encoding="utf-8")
    (dist / "assets" / "learnloop.js").write_text(JS, encoding="utf-8")
    (dist / "index.html").write_text(render_index(course), encoding="utf-8")

    for idx, module in enumerate(course.modules):
        source = course.root / module.file
        frontmatter, body = parse_module(source)
        html_body, _sections = render_markdown(body)
        previous_module = course.modules[idx - 1] if idx > 0 else None
        next_module = course.modules[idx + 1] if idx + 1 < len(course.modules) else None
        page = render_module_page(course, module, frontmatter, html_body, previous_module, next_module)
        (dist / module_output_name(module)).write_text(page, encoding="utf-8")

    return dist


def render_index(course: Course) -> str:
    cards = []
    for idx, module in enumerate(course.modules, start=1):
        cards.append(
            f"""<a class="module-card" href="{html.escape(module_output_name(module))}">
  <span class="module-number">{idx:02d}</span>
  <span class="module-text"><strong>{html.escape(module.title)}</strong><em>{html.escape(module.summary)}</em></span>
</a>"""
        )
    return page_shell(
        title=f"{course.title} | LearnLoop",
        body=f"""<header class="hero">
  <p class="eyebrow">LearnLoop Course</p>
  <h1>{html.escape(course.title)}</h1>
  <p class="lede">{html.escape(course.subtitle)}</p>
</header>
<section class="intro">
  <p>Read one module at a time. When a concept gets fuzzy, ask directly beside that section. LearnLoop stores the question with its exact course context so an agent can answer and improve the material later.</p>
</section>
<nav class="modules">{''.join(cards)}</nav>""",
    )


def render_module_page(
    course: Course,
    module: Module,
    frontmatter: dict[str, str],
    body: str,
    previous_module: Module | None,
    next_module: Module | None,
) -> str:
    prev_link = (
        f'<a href="{html.escape(module_output_name(previous_module))}">Previous</a>'
        if previous_module
        else "<span></span>"
    )
    next_link = (
        f'<a href="{html.escape(module_output_name(next_module))}">Next</a>'
        if next_module
        else "<span></span>"
    )
    summary = html.escape(frontmatter.get("summary", module.summary))
    content = f"""<nav class="top-nav"><a href="index.html">Learning path</a><span>{html.escape(module.id)}</span></nav>
<article class="lesson" data-course-id="{html.escape(course.id)}" data-module-id="{html.escape(module.id)}">
  <header class="lesson-header">
    <p class="eyebrow">{html.escape(course.title)}</p>
    <h1>{html.escape(module.title)}</h1>
    <p class="lede">{summary}</p>
  </header>
  {body}
  <footer class="next-prev">{prev_link}{next_link}</footer>
</article>
{QUESTION_UI}"""
    return page_shell(title=f"{module.title} | LearnLoop", body=content)


def render_markdown(text: str) -> tuple[str, list[dict[str, str]]]:
    lines = text.splitlines()
    out: list[str] = []
    sections: list[dict[str, str]] = []
    paragraph: list[str] = []
    list_type: str | None = None
    code: list[str] | None = None
    code_lang = ""

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    for raw in lines:
        line = raw.rstrip()
        if code is not None:
            if line.startswith("```"):
                out.append(
                    f'<pre><code class="language-{html.escape(code_lang)}">{html.escape(chr(10).join(code))}</code></pre>'
                )
                code = None
                code_lang = ""
            else:
                code.append(line)
            continue

        if line.startswith("```"):
            flush_paragraph()
            close_list()
            code = []
            code_lang = line[3:].strip()
            continue

        if not line.strip():
            flush_paragraph()
            close_list()
            continue

        section = SECTION_RE.match(line)
        if section:
            flush_paragraph()
            close_list()
            level = len(section.group(1))
            section_id = section.group(2)
            title = section.group(3)
            sections.append({"id": section_id, "title": title})
            out.append(
                f'<h{level} data-section-id="{html.escape(section_id)}" data-section-title="{html.escape(title)}">'
                f'{html.escape(title)} <button class="ask-btn" data-ask-section="{html.escape(section_id)}" '
                f'data-ask-title="{html.escape(title)}">Ask here</button></h{level}>'
            )
            continue

        if line.startswith("# "):
            flush_paragraph()
            close_list()
            out.append(f"<h1>{inline(line[2:].strip())}</h1>")
            continue

        if line.startswith("> "):
            flush_paragraph()
            close_list()
            out.append(f'<div class="callout">{inline(line[2:].strip())}</div>')
            continue

        if line.startswith("- "):
            flush_paragraph()
            if list_type != "ul":
                close_list()
                list_type = "ul"
                out.append("<ul>")
            out.append(f"<li>{inline(line[2:].strip())}</li>")
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        if ordered:
            flush_paragraph()
            if list_type != "ol":
                close_list()
                list_type = "ol"
                out.append("<ol>")
            out.append(f"<li>{inline(ordered.group(1))}</li>")
            continue

        paragraph.append(line.strip())

    flush_paragraph()
    close_list()
    if code is not None:
        out.append(f"<pre><code>{html.escape(chr(10).join(code))}</code></pre>")
    return "\n".join(out), sections


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def page_shell(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="assets/learnloop.css">
</head>
<body>
  <div class="file-warning" id="file-warning">Interactive questions require the local LearnLoop server.</div>
  <main class="page">{body}</main>
  <script src="/config.js"></script>
  <script src="assets/learnloop.js"></script>
</body>
</html>
"""


def module_output_name(module: Module) -> str:
    return f"{module.id}.html"


def validate_course(course_dir: Path) -> list[str]:
    errors: list[str] = []
    try:
        course = read_course(course_dir)
    except LearnLoopError as exc:
        return [str(exc)]

    seen_sections: set[str] = set()
    seen_modules: set[str] = set()
    for module in course.modules:
        if module.id in seen_modules:
            errors.append(f"Duplicate module id: {module.id}")
        seen_modules.add(module.id)
        path = course.root / module.file
        if not path.exists():
            errors.append(f"Missing module file: {module.file}")
            continue
        _frontmatter, body = parse_module(path)
        _html, sections = render_markdown(body)
        if not sections:
            errors.append(f"Module has no question sections: {module.file}")
        for section in sections:
            key = section["id"]
            if key in seen_sections:
                errors.append(f"Duplicate section id: {key}")
            seen_sections.add(key)

    questions = course.root / "questions.jsonl"
    if questions.exists():
        for idx, line in enumerate(questions.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"questions.jsonl:{idx}: invalid JSON: {exc.msg}")
                continue
            for field in ("id", "timestamp", "course_id", "module_id", "section_id", "question", "status"):
                if field not in item:
                    errors.append(f"questions.jsonl:{idx}: missing {field}")
    return errors


def make_context(course_dir: Path, question_id: str) -> str:
    course = read_course(course_dir)
    questions = load_questions(course.root / "questions.jsonl")
    question = next((q for q in questions if q.get("id") == question_id), None)
    if not question:
        raise LearnLoopError(f"Question id not found: {question_id}")

    module = next((m for m in course.modules if m.id == question.get("module_id")), None)
    if not module:
        raise LearnLoopError(f"Question references missing module: {question.get('module_id')}")

    _frontmatter, body = parse_module(course.root / module.file)
    section_text = extract_section_text(body, str(question.get("section_id", "")))
    payload = {
        "course": {
            "id": course.id,
            "title": course.title,
            "audience": course.audience,
        },
        "module": {
            "id": module.id,
            "title": module.title,
            "summary": module.summary,
        },
        "question": question,
        "section_context": section_text,
        "answer_instructions": "Answer the learner's question, then suggest whether the course source should be updated.",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def extract_section_text(markdown: str, section_id: str) -> str:
    lines = markdown.splitlines()
    collecting = False
    found: list[str] = []
    for line in lines:
        match = SECTION_RE.match(line)
        if match:
            if collecting:
                break
            collecting = match.group(2) == section_id
        if collecting:
            found.append(line)
    return "\n".join(found).strip()


def init_course(target: Path, slug: str) -> Path:
    course_dir = target / slug
    if course_dir.exists():
        raise LearnLoopError(f"Course already exists: {course_dir}")
    (course_dir / "modules").mkdir(parents=True)
    (course_dir / "answers").mkdir()
    (course_dir / "questions.jsonl").write_text("", encoding="utf-8")
    (course_dir / "course.yaml").write_text(
        f"""id: {slug}
title: "New LearnLoop Course"
subtitle: "A local-first adaptive learning course."
audience: "Learners who want structured feedback."
default_port: 8787
modules:
  - id: m1
    title: "Start Here"
    file: "modules/01.md"
    summary: "Define the topic and first learning goal."
""",
        encoding="utf-8",
    )
    (course_dir / "modules" / "01.md").write_text(
        """---
id: m1
title: "Start Here"
summary: "Define the topic and first learning goal."
---

## [m1-purpose] Why this course exists

Write the first learning objective here.

## [m1-summary] Module recap

- Replace this module with real course content.
""",
        encoding="utf-8",
    )
    return course_dir


def serve_course(course_dir: Path, port: int | None = None) -> None:
    course = read_course(course_dir)
    selected_port = find_available_port(port or course.default_port)
    dist = build_course(course.root)
    questions_file = course.root / "questions.jsonl"
    questions_file.touch(exist_ok=True)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(dist), **kwargs)

        def end_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            super().end_headers()

        def do_OPTIONS(self) -> None:
            self.send_response(204)
            self.end_headers()

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/questions":
                self.send_json(load_questions(questions_file))
                return
            if parsed.path == "/config.js":
                config = {
                    "apiBase": f"http://localhost:{selected_port}",
                    "courseId": course.id,
                    "courseTitle": course.title,
                }
                body = "window.LEARNLOOP_CONFIG = " + json.dumps(config, ensure_ascii=False) + ";"
                self.send_response(200)
                self.send_header("Content-Type", "application/javascript; charset=utf-8")
                self.end_headers()
                self.wfile.write(body.encode("utf-8"))
                return
            super().do_GET()

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/ask":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", 0))
            try:
                data = json.loads(self.rfile.read(length).decode("utf-8"))
            except json.JSONDecodeError:
                self.send_error(400, "invalid json")
                return

            question = str(data.get("question", "")).strip()
            section_id = str(data.get("section_id", "")).strip()
            module_id = str(data.get("module_id", "")).strip()
            if not question or not section_id or not module_id:
                self.send_error(400, "module_id, section_id, and question are required")
                return

            entry = {
                "id": uuid.uuid4().hex,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "course_id": course.id,
                "module_id": module_id,
                "section_id": section_id,
                "section_title": str(data.get("section_title", "")).strip(),
                "question": question,
                "status": "open",
            }
            with questions_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self.send_json({"ok": True, "saved": entry})

        def send_json(self, data: Any) -> None:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"[{time.strftime('%H:%M:%S')}] {fmt % args}")

    server = ThreadingHTTPServer(("localhost", selected_port), Handler)
    print(f"LearnLoop serving {course.title}")
    print(f"URL: http://localhost:{selected_port}/")
    print(f"Questions: {questions_file}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLearnLoop stopped")


def load_questions(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not path.exists():
        return items
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return items


def find_available_port(start: int) -> int:
    port = start
    while port < start + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("localhost", port))
                return port
            except OSError:
                port += 1
    raise LearnLoopError(f"No available port found near {start}")


QUESTION_UI = """<template id="ask-template">
  <form class="ask-form">
    <textarea name="question" placeholder="What is unclear here?"></textarea>
    <div class="ask-actions">
      <button type="button" data-cancel>Cancel</button>
      <button type="submit">Save question</button>
    </div>
    <p class="ask-status" role="status"></p>
  </form>
</template>
<button class="question-fab" data-open-drawer>Questions <span id="question-count">0</span></button>
<aside class="question-drawer" id="question-drawer" aria-hidden="true">
  <header><h2>Questions</h2><button data-close-drawer>Close</button></header>
  <div id="question-list" class="question-list"></div>
  <footer>Ask an agent to read <code>questions.jsonl</code> or run <code>learnloop context</code>.</footer>
</aside>"""


CSS = r""":root {
  --paper: #f6f1e8;
  --ink: #18211f;
  --muted: #60706a;
  --line: #d8cdbc;
  --panel: #fffaf0;
  --accent: #0d7c66;
  --accent-strong: #b4442e;
  --code: #17211e;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  line-height: 1.7;
}
.page { width: min(920px, calc(100vw - 40px)); margin: 0 auto; padding: 56px 0 120px; }
.file-warning { display: none; background: var(--accent-strong); color: white; padding: 12px 20px; text-align: center; }
.file-warning.visible { display: block; }
.hero, .lesson-header { border-bottom: 3px solid var(--ink); padding-bottom: 34px; margin-bottom: 34px; }
.eyebrow { margin: 0 0 10px; color: var(--accent); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; text-transform: uppercase; letter-spacing: .14em; }
h1 { font-size: clamp(42px, 7vw, 76px); line-height: .98; margin: 0 0 22px; max-width: 820px; }
h2 { font-size: 30px; line-height: 1.2; margin: 56px 0 16px; display: flex; gap: 12px; align-items: baseline; flex-wrap: wrap; }
h3 { font-size: 22px; margin: 34px 0 12px; display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }
p, li { font-size: 18px; }
.lede { color: var(--muted); font-size: 22px; max-width: 760px; }
.intro, .callout { background: var(--panel); border-left: 5px solid var(--accent); padding: 22px 26px; margin: 28px 0; }
.modules { display: grid; gap: 14px; margin-top: 34px; }
.module-card { display: grid; grid-template-columns: 86px 1fr; color: inherit; text-decoration: none; background: var(--panel); border: 1px solid var(--line); transition: transform .15s ease, box-shadow .15s ease; }
.module-card:hover { transform: translateX(5px); box-shadow: 6px 6px 0 #cfe4dd; }
.module-number { display: grid; place-items: center; background: #e8dfcf; color: var(--accent-strong); font: 700 30px ui-monospace, SFMono-Regular, Menlo, monospace; }
.module-text { padding: 22px 24px; }
.module-text strong { display: block; font-size: 22px; }
.module-text em { display: block; margin-top: 4px; color: var(--muted); font-style: normal; }
.top-nav, .next-prev { display: flex; justify-content: space-between; gap: 16px; border-bottom: 1px solid var(--line); padding-bottom: 18px; margin-bottom: 42px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; }
.next-prev { border-bottom: 0; border-top: 3px solid var(--ink); padding: 24px 0 0; margin: 64px 0 0; }
a { color: var(--accent-strong); }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: #e8dfcf; padding: 2px 5px; border-radius: 3px; }
pre { background: var(--code); color: #f7f1e8; padding: 20px; overflow-x: auto; border-radius: 4px; }
pre code { background: transparent; padding: 0; }
.ask-btn { border: 1px solid #b6d2c9; background: transparent; color: var(--accent); border-radius: 4px; padding: 4px 9px; font: 12px ui-monospace, SFMono-Regular, Menlo, monospace; cursor: pointer; }
.ask-btn:hover { background: var(--accent); color: white; }
.ask-form { background: var(--panel); border: 1px solid var(--line); padding: 16px; margin: 12px 0 24px; }
.ask-form textarea { width: 100%; min-height: 90px; padding: 12px; border: 1px solid var(--line); font: 16px ui-serif, Georgia, serif; }
.ask-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; }
.ask-actions button, .question-fab, .question-drawer button { cursor: pointer; border: 0; border-radius: 4px; padding: 9px 13px; background: var(--accent); color: white; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.ask-actions button[data-cancel] { background: #d8cdbc; color: var(--ink); }
.ask-status { margin: 10px 0 0; color: var(--accent); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; }
.question-fab { position: fixed; right: 22px; bottom: 22px; box-shadow: 0 8px 20px rgba(0,0,0,.16); }
.question-drawer { position: fixed; top: 0; right: -420px; width: min(420px, 92vw); height: 100vh; background: var(--panel); border-left: 1px solid var(--line); padding: 22px; transition: right .2s ease; overflow-y: auto; z-index: 5; }
.question-drawer.open { right: 0; }
.question-drawer header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--line); margin-bottom: 18px; }
.question-drawer h2 { margin: 0; }
.question-item { border-left: 4px solid var(--accent); background: white; padding: 12px; margin-bottom: 12px; }
.question-item strong { display: block; font-size: 13px; color: var(--accent); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
@media (max-width: 640px) {
  .page { width: min(100vw - 28px, 920px); padding-top: 34px; }
  .module-card { grid-template-columns: 64px 1fr; }
  h1 { font-size: 42px; }
  h2 { font-size: 25px; }
}
"""


JS = r"""(() => {
  const config = window.LEARNLOOP_CONFIG || { apiBase: window.location.origin };
  if (window.location.protocol === "file:") {
    document.getElementById("file-warning")?.classList.add("visible");
  }

  const lesson = document.querySelector(".lesson");
  const moduleId = lesson?.dataset.moduleId || "";
  const drawer = document.getElementById("question-drawer");
  const list = document.getElementById("question-list");
  const count = document.getElementById("question-count");

  document.querySelectorAll("[data-ask-section]").forEach((button) => {
    button.addEventListener("click", () => openAsk(button));
  });
  document.querySelector("[data-open-drawer]")?.addEventListener("click", () => {
    drawer?.classList.add("open");
    loadQuestions();
  });
  document.querySelector("[data-close-drawer]")?.addEventListener("click", () => {
    drawer?.classList.remove("open");
  });

  function openAsk(button) {
    document.querySelectorAll(".ask-form").forEach((node) => node.remove());
    const template = document.getElementById("ask-template");
    const form = template.content.firstElementChild.cloneNode(true);
    const heading = button.closest("[data-section-id]");
    heading.insertAdjacentElement("afterend", form);
    form.querySelector("textarea").focus();
    form.querySelector("[data-cancel]").addEventListener("click", () => form.remove());
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const question = form.querySelector("textarea").value.trim();
      const status = form.querySelector(".ask-status");
      if (!question) {
        status.textContent = "Write a question first.";
        return;
      }
      const payload = {
        module_id: moduleId,
        section_id: button.dataset.askSection,
        section_title: button.dataset.askTitle,
        question
      };
      try {
        const response = await fetch(`${config.apiBase}/ask`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(await response.text());
        status.textContent = "Saved to questions.jsonl";
        form.querySelector("textarea").value = "";
        await loadQuestions();
        setTimeout(() => form.remove(), 900);
      } catch (error) {
        status.textContent = "Could not save. Start the LearnLoop server and open this page through localhost.";
      }
    });
  }

  async function loadQuestions() {
    if (!list || !count) return;
    try {
      const response = await fetch(`${config.apiBase}/questions`);
      const questions = await response.json();
      count.textContent = questions.length;
      list.innerHTML = questions.length ? questions.map(renderQuestion).join("") : "<p>No questions yet.</p>";
    } catch (_error) {
      list.innerHTML = "<p>Questions are available after the local server starts.</p>";
    }
  }

  function renderQuestion(question) {
    return `<div class="question-item"><strong>${escapeHtml(question.section_title || question.section_id)}</strong><p>${escapeHtml(question.question)}</p><small>${escapeHtml(question.status || "")} · ${escapeHtml(question.id || "")}</small></div>`;
  }

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value || "";
    return div.innerHTML;
  }

  loadQuestions();
})();
"""
