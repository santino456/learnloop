from __future__ import annotations

import json
import mimetypes
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import unquote, urlparse
from urllib.request import urlopen

from .model import LearnLoopError
from .parser import collect_sections, parse_module, read_course
from .renderer import build_course
from .templates import template_root

HOST = "127.0.0.1"
DEFAULT_PORT = 8787
MAX_ASK_BODY_BYTES = 16 * 1024
MAX_QUESTION_CHARS = 4000
MAX_ASK_FIELD_CHARS = 200
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
QUESTION_LOG_LOCKS: dict[Path, threading.Lock] = {}
QUESTION_LOG_LOCKS_GUARD = threading.Lock()


@dataclass
class CourseEntry:
    root: Path
    id: str
    title: str
    subtitle: str
    module_count: int
    error: str | None = None


def find_available_port(start: int) -> int:
    port = start
    while port < start + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((HOST, port))
                return port
            except OSError:
                port += 1
    raise LearnLoopError(f"No available port found near {start}")


def ensure_port_available(port: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((HOST, port))
        except OSError as exc:
            raise LearnLoopError(
                f"Port {port} is already in use. Stop the old LearnLoop server or choose another port."
            ) from exc
    return port


def serve_course(course_dir: Path, port: int | None = None, auto_port: bool = False) -> None:
    serve_library(course_dir, port=port, auto_port=auto_port)


def serve_library(root: Path, port: int | None = None, auto_port: bool = False) -> None:
    library = CourseLibrary(root)
    requested_port = port or library.default_port()
    selected_port = find_available_port(requested_port) if auto_port else ensure_port_available(requested_port)
    handler = make_handler(library, selected_port)
    server = ThreadingHTTPServer((HOST, selected_port), handler)

    print(f"LearnLoop library serving {library.root}", flush=True)
    print(f"URL: http://{HOST}:{selected_port}/", flush=True)
    print("Press Ctrl+C to stop", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLearnLoop stopped", flush=True)


class CourseLibrary:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def is_single_course(self) -> bool:
        return (self.root / "course.yaml").exists()

    def default_port(self) -> int:
        if self.is_single_course():
            try:
                return read_course(self.root).default_port
            except LearnLoopError:
                return DEFAULT_PORT
        return DEFAULT_PORT

    def course_dirs(self) -> list[Path]:
        if self.is_single_course():
            return [self.root]
        if not self.root.exists():
            raise LearnLoopError(f"Courses root does not exist: {self.root}")
        return sorted(
            path
            for path in self.root.iterdir()
            if path.is_dir() and (path / "course.yaml").exists()
        )

    def entries(self) -> list[CourseEntry]:
        entries: list[CourseEntry] = []
        seen: set[str] = set()
        for course_root in self.course_dirs():
            try:
                course = read_course(course_root)
                error = None
                course_id = course.id
                title = course.title
                subtitle = course.subtitle
                module_count = len(course.modules)
            except LearnLoopError as exc:
                error = str(exc)
                course_id = course_root.name
                title = course_root.name
                subtitle = ""
                module_count = 0
            if course_id in seen:
                error = f"Duplicate course id: {course_id}"
            seen.add(course_id)
            entries.append(
                CourseEntry(
                    root=course_root,
                    id=course_id,
                    title=title,
                    subtitle=subtitle,
                    module_count=module_count,
                    error=error,
                )
            )
        return entries

    def get(self, course_id: str) -> CourseEntry | None:
        for entry in self.entries():
            if entry.id == course_id:
                return entry
        return None

    def first_course_id(self) -> str | None:
        entries = self.entries()
        return entries[0].id if entries else None


def make_handler(library: CourseLibrary, port: int) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "LearnLoop/0.1"

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
            path = parsed.path
            if path == "/healthz":
                self.send_json(
                    {
                        "ok": True,
                        "root": str(library.root),
                        "port": port,
                        "courses": len(library.entries()),
                    }
                )
                return
            if path == "/api/courses":
                self.send_json([course_to_json(entry) for entry in library.entries()])
                return
            api_match = split_course_api_path(path)
            if api_match and api_match[1] == "questions":
                self.send_course_questions(api_match[0])
                return
            if path == "/":
                self.send_html(render_library_home(library))
                return

            course_match = split_course_path(path)
            if course_match:
                course_id, rel_path = course_match
                self.handle_course_get(course_id, rel_path)
                return

            if library.is_single_course():
                first = library.first_course_id()
                if first:
                    if path == "/config.js":
                        self.send_course_config(first)
                        return
                    if path == "/questions":
                        self.send_course_questions(first)
                        return
                    self.handle_course_get(first, path.lstrip("/"))
                    return

            self.send_error(404)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            api_match = split_course_api_path(path)
            if api_match and api_match[1] == "ask":
                self.handle_ask(api_match[0])
                return
            if library.is_single_course() and path == "/ask":
                first = library.first_course_id()
                if first:
                    self.handle_ask(first)
                    return
            self.send_error(404)

        def handle_course_get(self, course_id: str, rel_path: str) -> None:
            rel_path = rel_path or "index.html"
            if rel_path == "config.js":
                self.send_course_config(course_id)
                return
            if rel_path == "questions":
                self.send_course_questions(course_id)
                return

            api_match = split_course_api_path(f"/api/courses/{course_id}/{rel_path}")
            if api_match and api_match[1] == "questions":
                self.send_course_questions(course_id)
                return

            entry = library.get(course_id)
            if not entry:
                self.send_error(404, f"unknown course: {course_id}")
                return
            if entry.error:
                self.send_course_error(entry.title, entry.error)
                return
            try:
                dist = ensure_course_built(entry.root)
            except LearnLoopError as exc:
                self.send_course_error(entry.title, str(exc))
                return

            target = safe_join(dist, rel_path)
            if target is None or not target.exists() or target.is_dir():
                self.send_error(404)
                return
            self.send_file(target)

        def send_course_config(self, course_id: str) -> None:
            entry = library.get(course_id)
            if not entry:
                self.send_error(404, f"unknown course: {course_id}")
                return
            config = {
                "apiBase": f"/api/courses/{entry.id}",
                "courseId": entry.id,
                "courseTitle": entry.title,
                "courseUrl": f"/course/{entry.id}/",
                "coursesUrl": "/api/courses",
                "libraryUrl": "/",
            }
            body = "window.LEARNLOOP_CONFIG = " + json.dumps(config, ensure_ascii=False) + ";"
            self.send_bytes(body.encode("utf-8"), "application/javascript; charset=utf-8")

        def send_course_questions(self, course_id: str) -> None:
            entry = library.get(course_id)
            if not entry:
                self.send_error(404, f"unknown course: {course_id}")
                return
            self.send_json(load_questions(entry.root / "questions.jsonl"))

        def handle_ask(self, course_id: str) -> None:
            entry = library.get(course_id)
            if not entry:
                self.send_error(404, f"unknown course: {course_id}")
                return
            if entry.error:
                self.send_error(400, entry.error)
                return
            try:
                length = int(self.headers.get("Content-Length", 0))
            except ValueError:
                self.send_error(400, "invalid content length")
                return
            if length > MAX_ASK_BODY_BYTES:
                self.send_error(413, "question request is too large")
                return
            try:
                data = json.loads(self.rfile.read(length).decode("utf-8"))
            except UnicodeDecodeError:
                self.send_error(400, "request body must be utf-8")
                return
            except json.JSONDecodeError:
                self.send_error(400, "invalid json")
                return

            question = clean_question_text(str(data.get("question", "")))
            section_id = clean_short_text(str(data.get("section_id", "")))
            module_id = clean_short_text(str(data.get("module_id", "")))
            if not question or not section_id or not module_id:
                self.send_error(400, "module_id, section_id, and question are required")
                return
            if len(question) > MAX_QUESTION_CHARS:
                self.send_error(400, f"question exceeds {MAX_QUESTION_CHARS} characters")
                return
            if not course_target_exists(entry.root, module_id, section_id):
                self.send_error(400, "module_id or section_id does not exist")
                return

            questions_file = entry.root / "questions.jsonl"
            saved = {
                "id": uuid.uuid4().hex,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "course_id": entry.id,
                "module_id": module_id,
                "section_id": section_id,
                "section_title": clean_short_text(str(data.get("section_title", ""))),
                "question": question,
                "status": "open",
            }
            with question_log_lock(questions_file):
                questions_file.touch(exist_ok=True)
                with questions_file.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(saved, ensure_ascii=False) + "\n")
            self.send_json({"ok": True, "saved": saved})

        def send_course_error(self, title: str, message: str) -> None:
            self.send_response(500)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_error_page(title, message).encode("utf-8"))

        def send_json(self, data: Any) -> None:
            self.send_bytes(json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def send_html(self, html_text: str) -> None:
            self.send_bytes(html_text.encode("utf-8"), "text/html; charset=utf-8")

        def send_file(self, target: Path) -> None:
            content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            self.send_bytes(target.read_bytes(), content_type)

        def send_bytes(self, body: bytes, content_type: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"[{time.strftime('%H:%M:%S')}] {fmt % args}", flush=True)

    return Handler


def split_course_path(path: str) -> tuple[str, str] | None:
    prefix = "/course/"
    if not path.startswith(prefix):
        return None
    rest = path[len(prefix) :]
    if not rest:
        return None
    parts = rest.split("/", 1)
    course_id = unquote(parts[0])
    rel_path = unquote(parts[1]) if len(parts) > 1 else "index.html"
    return course_id, rel_path


def split_course_api_path(path: str) -> tuple[str, str] | None:
    prefix = "/api/courses/"
    if not path.startswith(prefix):
        return None
    rest = path[len(prefix) :]
    parts = rest.split("/", 1)
    if len(parts) != 2:
        return None
    return unquote(parts[0]), unquote(parts[1])


def safe_join(root: Path, rel_path: str) -> Path | None:
    candidate = (root / rel_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def ensure_course_built(course_root: Path) -> Path:
    dist = course_root / "dist"
    index = dist / "index.html"
    if not index.exists() or source_is_newer(course_root, index.stat().st_mtime):
        return build_course(course_root)
    return dist


def source_is_newer(course_root: Path, built_mtime: float) -> bool:
    candidates = [course_root / "course.yaml"]
    modules = course_root / "modules"
    if modules.exists():
        candidates.extend(path for path in modules.rglob("*.md") if path.is_file())
    templates = template_root()
    if templates.exists():
        candidates.extend(path for path in templates.rglob("*") if path.is_file())
    return any(path.exists() and path.stat().st_mtime > built_mtime for path in candidates)


def course_to_json(entry: CourseEntry) -> dict[str, Any]:
    dist = entry.root / "dist" / "index.html"
    return {
        "id": entry.id,
        "title": entry.title,
        "subtitle": entry.subtitle,
        "module_count": entry.module_count,
        "url": f"/course/{entry.id}/",
        "root": str(entry.root),
        "built": dist.exists(),
        "updated_at": int(dist.stat().st_mtime) if dist.exists() else None,
        "error": entry.error,
    }


def render_library_home(library: CourseLibrary) -> str:
    entries = library.entries()
    cards = []
    for entry in entries:
        status = "配置错误" if entry.error else ("已构建" if (entry.root / "dist" / "index.html").exists() else "待构建")
        action = (
            f'<a class="ll-home-action" href="/course/{entry.id}/">进入课程</a>'
            if not entry.error
            else '<span class="ll-home-error">需要修复 course.yaml</span>'
        )
        cards.append(
            f"""<article class="ll-home-card">
  <div>
    <span class="ll-home-status">{escape_html(status)}</span>
    <h2>{escape_html(entry.title)}</h2>
    <p>{escape_html(entry.subtitle or "本地 LearnLoop 课程")}</p>
    <small>{escape_html(entry.id)} · {entry.module_count} modules</small>
  </div>
  {action}
</article>"""
        )
    empty = '<p class="ll-home-empty">没有发现课程。把包含 course.yaml 的课程目录放到 courses/ 下，然后刷新。</p>'
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LearnLoop Library</title>
  <style>{LIBRARY_CSS}</style>
</head>
<body>
  <main class="ll-home">
    <header>
      <p>LearnLoop Library</p>
      <h1>本地课程库</h1>
      <span>{escape_html(str(library.root))}</span>
    </header>
    <section class="ll-home-grid">
      {''.join(cards) if cards else empty}
    </section>
  </main>
</body>
</html>"""


def render_error_page(title: str, message: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape_html(title)} build failed</title>
  <style>{LIBRARY_CSS}</style>
</head>
<body>
  <main class="ll-home">
    <header>
      <p>LearnLoop Build Error</p>
      <h1>{escape_html(title)}</h1>
      <span>这门课构建失败，但服务仍在运行，其他课程不受影响。</span>
    </header>
    <pre class="ll-error">{escape_html(message)}</pre>
    <a class="ll-home-action" href="/">返回课程库</a>
  </main>
</body>
</html>"""


LIBRARY_CSS = """
:root { color-scheme: light; --bg:#f4f6f4; --paper:#fffefb; --ink:#1d2422; --muted:#66736f; --line:#d8e0dc; --accent:#0f766e; --accent-strong:#0e4f49; --soft:#e0f1ee; --shadow:0 10px 30px rgba(29,36,34,.06); }
* { box-sizing: border-box; }
body { margin:0; background:linear-gradient(90deg, rgba(15,118,110,.04) 1px, transparent 1px), linear-gradient(180deg, rgba(49,95,168,.035), transparent 260px), var(--bg); background-size:64px 64px, auto, auto; color:var(--ink); font:16px/1.7 "PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
.ll-home { width:min(1040px, calc(100vw - 40px)); margin:0 auto; padding:48px 0 86px; }
.ll-home header { border-bottom:1px solid var(--line); padding-bottom:18px; margin-bottom:22px; }
.ll-home header p { margin:0 0 6px; color:var(--accent); font:800 12px/1.2 ui-monospace,SFMono-Regular,Menlo,monospace; text-transform:uppercase; }
.ll-home h1 { margin:0 0 8px; font-size:38px; line-height:1.18; }
.ll-home header span, .ll-home-card small, .ll-home-card p { color:var(--muted); }
.ll-home-grid { display:grid; gap:12px; }
.ll-home-card { display:flex; justify-content:space-between; gap:18px; align-items:center; background:rgba(255,254,251,.78); border:1px solid var(--line); border-radius:8px; padding:20px 22px; box-shadow:var(--shadow); }
.ll-home-card h2 { margin:6px 0 4px; font-size:21px; line-height:1.35; }
.ll-home-card p { margin:0 0 6px; }
.ll-home-status { display:inline-flex; border:1px solid #baded7; background:var(--soft); color:var(--accent-strong); border-radius:999px; padding:2px 8px; font:800 11px ui-monospace,SFMono-Regular,Menlo,monospace; }
.ll-home-action { flex:none; color:#fff; background:var(--accent); text-decoration:none; border-radius:5px; padding:9px 13px; font:750 13px "PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; }
.ll-home-action:hover { background:var(--accent-strong); }
.ll-home-error { color:var(--accent-strong); font-size:13px; }
.ll-home-empty { background:var(--paper); border:1px dashed var(--line); border-radius:8px; padding:22px; color:var(--muted); }
.ll-error { white-space:pre-wrap; background:#18211f; color:#f6fbf8; border-radius:8px; padding:18px; overflow:auto; }
@media (max-width: 680px) { .ll-home-card { align-items:flex-start; flex-direction:column; } .ll-home-action { width:100%; text-align:center; } }
"""


def load_questions(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not path.exists():
        return items
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def load_question_by_id(path: Path, question_id: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("id") == question_id:
                return item
    return None


def clean_question_text(value: str) -> str:
    value = CONTROL_CHARS_RE.sub("", value)
    return value.strip()


def clean_short_text(value: str) -> str:
    value = CONTROL_CHARS_RE.sub("", value)
    value = " ".join(value.split())
    return value[:MAX_ASK_FIELD_CHARS]


def course_target_exists(course_root: Path, module_id: str, section_id: str) -> bool:
    try:
        course = read_course(course_root)
        module = next((item for item in course.modules if item.id == module_id), None)
        if not module:
            return False
        _frontmatter, blocks = parse_module(course.root / module.file)
        return any(section.id == section_id for section in collect_sections(blocks))
    except (LearnLoopError, OSError):
        return False


def question_log_lock(path: Path) -> threading.Lock:
    key = path.resolve()
    with QUESTION_LOG_LOCKS_GUARD:
        lock = QUESTION_LOG_LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            QUESTION_LOG_LOCKS[key] = lock
        return lock


def pidfile_for(root: Path) -> Path:
    root = root.resolve()
    state_dir = root / ".learnloop"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "server.json"


def start_library(root: Path, port: int | None = None, auto_port: bool = False) -> dict[str, Any]:
    library = CourseLibrary(root)
    pidfile = pidfile_for(library.root)
    existing = read_pidfile(pidfile)
    if existing and pid_is_alive(int(existing.get("pid", -1))):
        url = f"http://{HOST}:{existing.get('port')}/"
        if health_ok(url):
            print(f"LearnLoop already running: {url}")
            return existing
        raise LearnLoopError(f"LearnLoop pid {existing.get('pid')} is running but health check failed. Stop it first.")
    if existing:
        pidfile.unlink(missing_ok=True)

    requested_port = port or library.default_port()
    selected_port = find_available_port(requested_port) if auto_port else ensure_port_available(requested_port)
    log_path = pidfile.with_name("server.log")
    log = log_path.open("a", encoding="utf-8")
    cmd = [sys.executable, "-m", "learnloop", "serve", str(library.root), "--port", str(selected_port)]
    if auto_port:
        cmd.append("--auto-port")
    proc = subprocess.Popen(
        cmd,
        cwd=str(Path.cwd()),
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        text=True,
    )
    log.close()
    state = {
        "pid": proc.pid,
        "port": selected_port,
        "root": str(library.root),
        "log": str(log_path),
        "url": f"http://{HOST}:{selected_port}/",
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    pidfile.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        wait_for_health(state["url"])
    except LearnLoopError:
        proc.poll()
        tail = log_path.read_text(encoding="utf-8")[-2000:] if log_path.exists() else ""
        raise LearnLoopError(f"LearnLoop failed to start. Log: {log_path}\n{tail}")
    print(f"LearnLoop started: {state['url']}")
    print(f"Log: {log_path}")
    return state


def stop_library(root: Path) -> None:
    pidfile = pidfile_for(root)
    state = read_pidfile(pidfile)
    if not state:
        print("LearnLoop is not running.")
        return
    pid = int(state.get("pid", -1))
    if not pid_is_alive(pid):
        pidfile.unlink(missing_ok=True)
        print("Removed stale LearnLoop pidfile.")
        return
    command = command_for_pid(pid)
    if "learnloop" not in command:
        raise LearnLoopError(f"Refusing to stop non-LearnLoop process {pid}: {command}")
    os.killpg(pid, signal.SIGTERM)
    for _ in range(30):
        if not pid_is_alive(pid):
            break
        time.sleep(0.1)
    if pid_is_alive(pid):
        os.killpg(pid, signal.SIGKILL)
    pidfile.unlink(missing_ok=True)
    print(f"Stopped LearnLoop on port {state.get('port')}.")


def status_library(root: Path) -> dict[str, Any] | None:
    pidfile = pidfile_for(root)
    state = read_pidfile(pidfile)
    if not state:
        print("LearnLoop is not running.")
        return None
    alive = pid_is_alive(int(state.get("pid", -1)))
    state["alive"] = alive
    state["healthy"] = health_ok(state.get("url", "")) if alive else False
    if alive and state["healthy"]:
        library = CourseLibrary(Path(str(state["root"])))
        state["courses"] = len(library.entries())
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return state


def read_pidfile(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def command_for_pid(pid: int) -> str:
    try:
        return subprocess.check_output(["ps", "-p", str(pid), "-o", "command="], text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def health_ok(url: str) -> bool:
    if not url:
        return False
    try:
        with urlopen(url.rstrip("/") + "/healthz", timeout=1) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


def wait_for_health(url: str) -> None:
    last_error: Exception | None = None
    for _ in range(50):
        try:
            with urlopen(url.rstrip("/") + "/healthz", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception as exc:
            last_error = exc
            time.sleep(0.1)
    raise LearnLoopError(f"server did not become healthy: {last_error}")


def escape_html(value: str) -> str:
    import html

    return html.escape(value, quote=True)
