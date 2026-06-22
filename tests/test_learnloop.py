from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib import request

from learnloop.course import build_course, init_course, make_context, validate_course


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "courses" / "acp-fundamentals"


class LearnLoopTests(unittest.TestCase):
    def test_sample_course_builds_and_validates(self) -> None:
        self.assertEqual(validate_course(SAMPLE), [])
        dist = build_course(SAMPLE)
        self.assertTrue((dist / "index.html").exists())
        self.assertTrue((dist / "m1.html").exists())
        self.assertIn("What ACP is", (dist / "index.html").read_text(encoding="utf-8"))

    def test_init_creates_valid_course(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "demo-course")
            self.assertEqual(validate_course(created), [])
            self.assertTrue((created / "modules" / "01.md").exists())

    def test_duplicate_section_id_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "bad-course")
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8") + "\n## [m1-purpose] Duplicate\n\nText.\n",
                encoding="utf-8",
            )
            errors = validate_course(created)
            self.assertTrue(any("Duplicate section id" in error for error in errors))

    def test_context_returns_question_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "context-course")
            question = {
                "id": "q1",
                "timestamp": "2026-06-22T12:00:00",
                "course_id": "context-course",
                "module_id": "m1",
                "section_id": "m1-purpose",
                "section_title": "Why this course exists",
                "question": "What is the goal?",
                "status": "open",
            }
            (created / "questions.jsonl").write_text(json.dumps(question) + "\n", encoding="utf-8")
            context = json.loads(make_context(created, "q1"))
            self.assertEqual(context["question"]["id"], "q1")
            self.assertIn("Why this course exists", context["section_context"])

    def test_server_config_and_ask_on_non_default_port(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "served-course")
            proc = subprocess.Popen(
                [sys.executable, "-m", "learnloop", "serve", str(created), "--port", "8798"],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                wait_for("http://localhost:8798/config.js")
                config = request.urlopen("http://localhost:8798/config.js", timeout=5).read().decode()
                self.assertIn("8798", config)
                body = json.dumps(
                    {
                        "module_id": "m1",
                        "section_id": "m1-purpose",
                        "section_title": "Why this course exists",
                        "question": "How does this work?",
                    }
                ).encode()
                req = request.Request(
                    "http://localhost:8798/ask",
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                saved = json.loads(request.urlopen(req, timeout=5).read().decode())
                self.assertEqual(saved["saved"]["status"], "open")
                questions = (created / "questions.jsonl").read_text(encoding="utf-8")
                self.assertIn("How does this work?", questions)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


def wait_for(url: str) -> None:
    last_error: Exception | None = None
    for _ in range(40):
        try:
            request.urlopen(url, timeout=1).read()
            return
        except Exception as exc:  # pragma: no cover - diagnostic path
            last_error = exc
            time.sleep(0.1)
    raise AssertionError(f"server did not start: {last_error}")


if __name__ == "__main__":
    unittest.main()
