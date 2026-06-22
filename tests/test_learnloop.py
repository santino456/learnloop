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
from learnloop.parser import parse_markdown
from learnloop.server import find_available_port
from learnloop.templates import list_templates, validate_template_support


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "courses" / "acp-fundamentals"


class LearnLoopTests(unittest.TestCase):
    def test_sample_course_builds_and_validates(self) -> None:
        self.assertEqual(validate_course(SAMPLE), [])
        dist = build_course(SAMPLE)
        self.assertTrue((dist / "index.html").exists())
        self.assertTrue((dist / "m1.html").exists())
        self.assertIn("ACP 是什么", (dist / "index.html").read_text(encoding="utf-8"))

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
            port = find_available_port(18000)
            proc = subprocess.Popen(
                [sys.executable, "-m", "learnloop", "serve", str(created), "--port", str(port)],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                wait_for(f"http://localhost:{port}/config.js")
                config = request.urlopen(f"http://localhost:{port}/config.js", timeout=5).read().decode()
                self.assertIn(str(port), config)
                body = json.dumps(
                    {
                        "module_id": "m1",
                        "section_id": "m1-purpose",
                        "section_title": "Why this course exists",
                        "question": "How does this work?",
                    }
                ).encode()
                req = request.Request(
                    f"http://localhost:{port}/ask",
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

    def test_course_level_template_selection_uses_tutorial_assets(self) -> None:
        dist = build_course(SAMPLE)
        index = (dist / "index.html").read_text(encoding="utf-8")
        m1 = (dist / "m1.html").read_text(encoding="utf-8")
        self.assertIn("assets/tutorial/style.css", index)
        self.assertIn("assets/tutorial/runtime.js", index)
        self.assertIn("assets/tutorial/style.css", m1)
        self.assertIn("assets/tutorial/runtime.js", m1)

    def test_module_level_template_override_uses_practice_assets(self) -> None:
        dist = build_course(SAMPLE)
        m3 = (dist / "m3.html").read_text(encoding="utf-8")
        self.assertIn("assets/practice/style.css", m3)
        self.assertIn("assets/practice/runtime.js", m3)

    def test_missing_template_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "missing-template-course")
            course_yaml = created / "course.yaml"
            course_yaml.write_text(
                course_yaml.read_text(encoding="utf-8").replace(
                    "template: tutorial", "template: does-not-exist"
                ),
                encoding="utf-8",
            )
            errors = validate_course(created)
            self.assertTrue(any("does-not-exist" in error for error in errors))

    def test_unsupported_block_type_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "unsupported-block-course")
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8")
                + "\n::: unsupported\nSome mystery block.\n:::\n",
                encoding="utf-8",
            )
            errors = validate_course(created)
            self.assertTrue(
                any("does not support block type: unsupported" in error for error in errors)
            )

    def test_exercise_and_checkpoint_render_in_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "container-course")
            course_yaml = created / "course.yaml"
            course_yaml.write_text(
                course_yaml.read_text(encoding="utf-8").replace(
                    "template: tutorial", "template: practice"
                ),
                encoding="utf-8",
            )
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8")
                + "\n::: exercise\nWrite a short answer.\n:::\n\n::: checkpoint\nConfirm your understanding.\n:::\n",
                encoding="utf-8",
            )
            dist = build_course(created)
            html_text = (dist / "m1.html").read_text(encoding="utf-8")
            self.assertIn('class="exercise"', html_text)
            self.assertIn('class="checkpoint"', html_text)
            self.assertIn("Write a short answer.", html_text)
            self.assertIn("Confirm your understanding.", html_text)

    def test_question_buttons_and_section_attributes_persist_across_templates(self) -> None:
        dist = build_course(SAMPLE)
        for file in ("m1.html", "m5.html"):
            text = (dist / file).read_text(encoding="utf-8")
            self.assertIn("data-section-id", text)
            self.assertIn("data-section-title", text)
            self.assertIn("ask-btn", text)
            self.assertIn("data-ask-section", text)

    def test_validate_template_support_reports_unsupported_blocks(self) -> None:
        from learnloop.templates import load_template

        template = load_template("tutorial")
        errors = validate_template_support(template, {"paragraph", "unsupported-magic"})
        self.assertEqual(len(errors), 1)
        self.assertIn("unsupported-magic", errors[0])

    def test_exercise_with_answer_parses_task_and_answer(self) -> None:
        blocks = parse_markdown(
            "::: exercise\nFill in the blank: ACP is about ____ and ____ communication.\n\n"
            "--- answer\nclient; agent\n---\n:::\n"
        )
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block.type, "exercise")
        self.assertIn("Fill in the blank", block.blocks[0].text)
        self.assertEqual(block.answer, "client; agent")

    def test_checkpoint_with_answer_parses_task_and_answer(self) -> None:
        blocks = parse_markdown(
            "::: checkpoint\nWhat does stdout need to stay parseable?\n\n"
            "--- answer\nIt must contain only line-delimited JSON; logs go to stderr.\n---\n:::\n"
        )
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block.type, "checkpoint")
        self.assertIn("stdout", block.blocks[0].text)
        self.assertIn("logs go to stderr", block.answer)

    def test_exercise_without_answer_has_no_answer(self) -> None:
        blocks = parse_markdown("::: exercise\nWrite a short answer.\n:::\n")
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block.type, "exercise")
        self.assertIsNone(block.answer)

    def test_table_parses_and_renders(self) -> None:
        from learnloop.renderer import render_blocks

        md = "| Role | Duty |\n|------|------|\n| Client | Drive session |\n| Agent | Reason and act |\n"
        blocks = parse_markdown(md)
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block.type, "table")
        self.assertEqual(block.headers, ["Role", "Duty"])
        self.assertEqual(block.rows, [["Client", "Drive session"], ["Agent", "Reason and act"]])
        html = render_blocks(blocks)
        self.assertIn("<table>", html)
        self.assertIn("<th>Role</th>", html)
        self.assertIn("<td>Agent</td>", html)

    def test_rendered_answer_is_hidden_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "answer-course")
            course_yaml = created / "course.yaml"
            course_yaml.write_text(
                course_yaml.read_text(encoding="utf-8").replace(
                    "template: tutorial", "template: practice"
                ),
                encoding="utf-8",
            )
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8")
                + "\n::: exercise\nTask text.\n\n--- answer\nModel answer.\n---\n:::\n",
                encoding="utf-8",
            )
            dist = build_course(created)
            html_text = (dist / "m1.html").read_text(encoding="utf-8")
            self.assertIn("Task text.", html_text)
            self.assertIn("Model answer.", html_text)
            self.assertIn('class="exercise-answer" hidden', html_text)
            self.assertIn('data-has-answer="true"', html_text)

    def test_all_templates_render_without_error(self) -> None:
        dist = build_course(SAMPLE)
        for template in list_templates():
            self.assertTrue((dist / f"assets/{template.name}/style.css").exists())
            self.assertTrue((dist / f"assets/{template.name}/runtime.js").exists())
        # Confirm each module was generated with the expected template assets.
        self.assertIn("assets/tutorial/style.css", (dist / "m1.html").read_text(encoding="utf-8"))
        self.assertIn("assets/reference/style.css", (dist / "m2.html").read_text(encoding="utf-8"))
        self.assertIn("assets/practice/style.css", (dist / "m3.html").read_text(encoding="utf-8"))
        self.assertIn("assets/case/style.css", (dist / "m5.html").read_text(encoding="utf-8"))


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
