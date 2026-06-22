from __future__ import annotations

import json
import socket
import sys
import time
import uuid
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .model import LearnLoopError
from .parser import read_course
from .renderer import build_course


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
                body = (
                    "window.LEARNLOOP_CONFIG = "
                    + json.dumps(config, ensure_ascii=False)
                    + ";"
                )
                self.send_response(200)
                self.send_header(
                    "Content-Type", "application/javascript; charset=utf-8"
                )
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
                self.send_error(
                    400, "module_id, section_id, and question are required"
                )
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
