from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib import request

from learnloop.course import LearnLoopError, build_course, init_course, make_context, scaffold_course, validate_course
from learnloop.ingest import ingest_material
from learnloop.knowledge import audit_generation_readiness
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

    def test_read_course_reports_malformed_course_yaml(self) -> None:
        from learnloop.parser import read_course

        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "bad-yaml-course")
            course_yaml = created / "course.yaml"
            course_yaml.write_text(
                "id: bad-yaml-course\n"
                "title: Bad YAML Course\n"
                "default_port: not-a-port\n"
                "modules:\n"
                "  - id: m1\n"
                "    title: Start\n"
                "    file: modules/01.md\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(LearnLoopError, "default_port must be an integer"):
                read_course(created)

            course_yaml.write_text(
                "id: bad-yaml-course\n"
                "title: Bad YAML Course\n"
                "modules:\n"
                "  - id: m1\n"
                "    title: Start\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(LearnLoopError, "missing required field 'file'"):
                read_course(created)

    def test_scaffold_course_creates_generation_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = scaffold_course(
                Path(tmp),
                "quality-course",
                title="Quality Course",
                topic="Course Quality",
                audience="Agents and human reviewers",
            )
            self.assertEqual(validate_course(created), [])
            self.assertEqual(audit_generation_readiness(created), [])
            dist = build_course(created)
            self.assertTrue((dist / "m1.html").exists())
            self.assertTrue((created / "generation_brief.md").exists())
            self.assertTrue((created / ".learnloop" / "source_inventory.yaml").exists())
            self.assertTrue((created / ".learnloop" / "course_architecture.md").exists())
            self.assertTrue((created / ".learnloop" / "chapter_briefs" / "m1.md").exists())
            self.assertTrue((created / ".learnloop" / "evidence_packs" / "README.md").exists())
            brief = (created / "generation_brief.md").read_text(encoding="utf-8")
            self.assertIn("Ask Better Questions", brief)
            self.assertIn("HTML Learning Components", brief)

    def test_ingest_text_creates_material_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = scaffold_course(Path(tmp), "material-course")
            source = created / "raw" / "notes.md"
            source.write_text("# Notes\n\nFirst fact.\n\nSecond fact.", encoding="utf-8")
            result = ingest_material(source, created)
            self.assertTrue(result.material_json.exists())
            self.assertTrue(result.chunks_jsonl.exists())
            material = json.loads(result.material_json.read_text(encoding="utf-8"))
            self.assertEqual(material["stats"]["chunks"], 3)
            self.assertEqual(material["source"]["filename"], "notes.md")
            inventory = (created / ".learnloop" / "source_inventory.yaml").read_text(encoding="utf-8")
            self.assertIn("id: notes", inventory)
            self.assertIn("material: \".learnloop/materials/notes/material.json\"", inventory)

    def test_ingest_pdf_extracts_captioned_figure(self) -> None:
        try:
            import fitz  # type: ignore
        except ImportError:
            self.skipTest("PyMuPDF is not installed")

        with tempfile.TemporaryDirectory() as tmp:
            created = scaffold_course(Path(tmp), "pdf-material-course")
            source = created / "raw" / "paper.pdf"
            doc = fitz.open()
            page = doc.new_page(width=420, height=540)
            page.insert_text((72, 72), "A short paper about cache behavior.", fontsize=12)
            page.draw_rect(fitz.Rect(100, 140, 320, 260), color=(0, 0, 0), fill=(0.9, 0.95, 1))
            page.insert_text(
                (72, 292),
                "Figure 1: Cache decode flow uses stored keys and values.",
                fontsize=11,
            )
            doc.save(source)
            doc.close()

            result = ingest_material(source, created)
            self.assertEqual(result.figures, 1)
            self.assertIsNotNone(result.figures_md)
            figure_asset = created / "assets" / "paper-fig-1.png"
            self.assertTrue(figure_asset.exists())
            figures_md = result.figures_md.read_text(encoding="utf-8")
            self.assertIn("::: figure", figures_md)
            self.assertIn("src: assets/paper-fig-1.png", figures_md)
            self.assertIn("Cache decode flow", figures_md)

    def test_sample_course_passes_generation_audit(self) -> None:
        self.assertEqual(audit_generation_readiness(SAMPLE), [])

    def test_generation_audit_passes_without_learnloop_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "lightweight-course")
            errors = audit_generation_readiness(created)
            self.assertEqual(errors, [])

    def test_generation_audit_rejects_practice_without_practice_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "weak-practice-course")
            course_yaml = created / "course.yaml"
            course_yaml.write_text(
                course_yaml.read_text(encoding="utf-8").replace(
                    "template: tutorial", "template: practice"
                ),
                encoding="utf-8",
            )
            errors = audit_generation_readiness(created)
            self.assertTrue(any("practice module must include exercise or checkpoint" in error for error in errors))

    def test_generation_audit_rejects_perspective_without_perspective_exercise(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "weak-perspective-course")
            course_yaml = created / "course.yaml"
            course_yaml.write_text(
                course_yaml.read_text(encoding="utf-8").replace(
                    "template: tutorial", "template: perspective"
                ),
                encoding="utf-8",
            )
            errors = audit_generation_readiness(created)
            self.assertTrue(any("perspective module must include a perspective exercise" in error for error in errors))

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

    def test_context_skips_invalid_question_log_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "context-bad-log-course")
            question = {
                "id": "q-after-bad-line",
                "timestamp": "2026-06-22T12:00:00",
                "course_id": "context-bad-log-course",
                "module_id": "m1",
                "section_id": "m1-purpose",
                "section_title": "Why this course exists",
                "question": "Can you still find this?",
                "status": "open",
            }
            (created / "questions.jsonl").write_text(
                "{bad json}\n" + json.dumps(question) + "\n",
                encoding="utf-8",
            )
            context = json.loads(make_context(created, "q-after-bad-line"))
            self.assertEqual(context["question"]["question"], "Can you still find this?")

    def test_context_rejects_missing_section_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "context-missing-section-course")
            question = {
                "id": "q-missing-section",
                "timestamp": "2026-06-22T12:00:00",
                "course_id": "context-missing-section-course",
                "module_id": "m1",
                "section_id": "m1-does-not-exist",
                "section_title": "Missing",
                "question": "Where is this?",
                "status": "open",
            }
            (created / "questions.jsonl").write_text(json.dumps(question) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(LearnLoopError, "missing section"):
                make_context(created, "q-missing-section")

    def test_server_config_and_ask_on_non_default_port(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "served-course")
            port = find_available_port(18000)
            proc = subprocess.Popen(
                [sys.executable, "-m", "learnloop", "serve", str(created), "--port", str(port)],
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            try:
                wait_for(f"http://localhost:{port}/config.js")
                config = request.urlopen(f"http://localhost:{port}/config.js", timeout=5).read().decode()
                self.assertIn("/api/courses/served-course", config)
                health = json.loads(request.urlopen(f"http://localhost:{port}/healthz", timeout=5).read().decode())
                self.assertEqual(health["ok"], True)
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

                bad_target = json.dumps(
                    {
                        "module_id": "m1",
                        "section_id": "m1-missing",
                        "section_title": "Missing",
                        "question": "Can this target be saved?",
                    }
                ).encode()
                req = request.Request(
                    f"http://localhost:{port}/ask",
                    data=bad_target,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(HTTPError) as ctx:
                    request.urlopen(req, timeout=5).read()
                self.assertEqual(ctx.exception.code, 400)

                large_body = json.dumps(
                    {
                        "module_id": "m1",
                        "section_id": "m1-purpose",
                        "section_title": "Why this course exists",
                        "question": "x" * 5000,
                    }
                ).encode()
                req = request.Request(
                    f"http://localhost:{port}/ask",
                    data=large_body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(HTTPError) as ctx:
                    request.urlopen(req, timeout=5).read()
                self.assertEqual(ctx.exception.code, 400)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()

    def test_library_server_serves_two_courses_from_one_port(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "courses"
            root.mkdir()
            first = init_course(root, "first-course")
            second = init_course(root, "second-course")
            port = find_available_port(18200)
            proc = subprocess.Popen(
                [sys.executable, "-m", "learnloop", "serve", str(root), "--port", str(port)],
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            try:
                wait_for(f"http://localhost:{port}/healthz")
                health = json.loads(request.urlopen(f"http://localhost:{port}/healthz", timeout=5).read().decode())
                self.assertEqual(health["courses"], 2)
                courses = json.loads(request.urlopen(f"http://localhost:{port}/api/courses", timeout=5).read().decode())
                self.assertEqual({course["id"] for course in courses}, {"first-course", "second-course"})
                first_html = request.urlopen(f"http://localhost:{port}/course/first-course/m1.html", timeout=5).read().decode()
                second_html = request.urlopen(f"http://localhost:{port}/course/second-course/m1.html", timeout=5).read().decode()
                self.assertIn("Start Here", first_html)
                self.assertIn("Start Here", second_html)

                payload = json.dumps(
                    {
                        "module_id": "m1",
                        "section_id": "m1-purpose",
                        "section_title": "Why this course exists",
                        "question": "Question for second course?",
                    }
                ).encode()
                req = request.Request(
                    f"http://localhost:{port}/api/courses/second-course/ask",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                saved = json.loads(request.urlopen(req, timeout=5).read().decode())
                self.assertEqual(saved["saved"]["course_id"], "second-course")
                self.assertNotIn("Question for second course?", (first / "questions.jsonl").read_text(encoding="utf-8"))
                self.assertIn("Question for second course?", (second / "questions.jsonl").read_text(encoding="utf-8"))
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()

    def test_library_build_failure_does_not_block_other_courses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "courses"
            root.mkdir()
            good = init_course(root, "good-course")
            bad = init_course(root, "bad-course")
            bad_module = bad / "modules" / "01.md"
            bad_module.write_text(
                bad_module.read_text(encoding="utf-8") + "\n::: unsupported\nNope.\n:::\n",
                encoding="utf-8",
            )
            port = find_available_port(18300)
            proc = subprocess.Popen(
                [sys.executable, "-m", "learnloop", "serve", str(root), "--port", str(port)],
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            try:
                wait_for(f"http://localhost:{port}/healthz")
                good_html = request.urlopen(f"http://localhost:{port}/course/good-course/m1.html", timeout=5).read().decode()
                self.assertIn("Start Here", good_html)
                with self.assertRaises(Exception):
                    request.urlopen(f"http://localhost:{port}/course/bad-course/m1.html", timeout=5).read()
                self.assertTrue((good / "dist" / "m1.html").exists())
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()

    def test_explicit_occupied_port_fails_instead_of_drifting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "port-course")
            port = find_available_port(18100)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("127.0.0.1", port))
                sock.listen(1)
                second = subprocess.run(
                    [sys.executable, "-m", "learnloop", "serve", str(created), "--port", str(port)],
                    cwd=str(ROOT),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10,
                )
                self.assertNotEqual(second.returncode, 0)
                self.assertIn("already in use", second.stderr)

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

    def test_verified_claim_without_source_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "claim-course")
            claims_dir = created / ".learnloop"
            claims_dir.mkdir(parents=True)
            claims = claims_dir / "claims.jsonl"
            claims.write_text(
                json.dumps(
                    {
                        "id": "claim-1",
                        "claim": "This is claimed as verified.",
                        "module_id": "m1",
                        "section_id": "m1-purpose",
                        "status": "verified",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            errors = validate_course(created)
            self.assertTrue(any("verified claim requires source" in error for error in errors))

    def test_claim_source_id_must_exist_in_source_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "unknown-source-course")
            workspace = created / ".learnloop"
            workspace.mkdir(parents=True)
            source_inventory = workspace / "source_inventory.yaml"
            source_inventory.write_text(
                "sources:\n  - id: known-source\n    type: primary\n",
                encoding="utf-8",
            )
            claims = created / ".learnloop" / "claims.jsonl"
            claims.write_text(
                json.dumps(
                    {
                        "id": "claim-1",
                        "claim": "This source id does not exist.",
                        "module_id": "m1",
                        "section_id": "m1-purpose",
                        "status": "verified",
                        "source_id": "missing-source",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            errors = validate_course(created)
            self.assertTrue(any("unknown source_id: missing-source" in error for error in errors))

    def test_perspective_without_basis_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "perspective-basis-course")
            course_yaml = created / "course.yaml"
            course_yaml.write_text(
                course_yaml.read_text(encoding="utf-8").replace(
                    "template: tutorial", "template: perspective"
                ),
                encoding="utf-8",
            )
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8")
                + "\n::: exercise\nJudge this design.\n\n--- perspective\nThis is a mature view.\n---\n:::\n",
                encoding="utf-8",
            )
            errors = validate_course(created)
            self.assertTrue(any("perspective exercise must include basis" in error for error in errors))

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

    def test_multiple_choice_exercise_parses_choices_and_answer(self) -> None:
        blocks = parse_markdown(
            "::: exercise\n本地 ACP 最常用什么传输？\n\n"
            "- A. HTTP\n"
            "- B. SSE\n"
            "- C. stdio + line-delimited JSON\n"
            "- D. WebSocket\n\n"
            "--- answer\nC\n"
            "--- explanation\n本地最小客户端通常是子进程 stdio。\n"
            "---\n:::\n"
        )
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block.type, "exercise")
        self.assertEqual(block.kind, "choice")
        self.assertEqual(block.answer, "C")
        self.assertEqual(
            block.choices,
            [
                "HTTP",
                "SSE",
                "stdio + line-delimited JSON",
                "WebSocket",
            ],
        )
        self.assertEqual(block.explanation, "本地最小客户端通常是子进程 stdio。")

    def test_multiple_choice_supports_more_than_four_options(self) -> None:
        from learnloop.renderer import render_blocks
        from learnloop.templates import load_template

        blocks = parse_markdown(
            "::: exercise\n选择正确选项。\n\n"
            "- A. One\n"
            "- B. Two\n"
            "- C. Three\n"
            "- D. Four\n"
            "- E. Five\n\n"
            "--- answer\nE\n"
            "---\n:::\n"
        )
        block = blocks[0]
        self.assertEqual(block.type, "exercise")
        self.assertEqual(block.kind, "choice")
        self.assertEqual(block.choices, ["One", "Two", "Three", "Four", "Five"])
        html = render_blocks(blocks, load_template("practice"))
        self.assertIn('data-answer="E"', html)
        self.assertIn('data-choice="E"', html)

    def test_multiple_choice_rejects_answer_outside_options(self) -> None:
        from learnloop.renderer import render_blocks
        from learnloop.templates import load_template

        blocks = parse_markdown(
            "::: exercise\n选择正确选项。\n\n"
            "- A. One\n"
            "- B. Two\n\n"
            "--- answer\nZ\n"
            "---\n:::\n"
        )
        with self.assertRaisesRegex(LearnLoopError, "outside available options"):
            render_blocks(blocks, load_template("practice"))

    def test_fill_in_the_blank_exercise_stores_expected_answers(self) -> None:
        blocks = parse_markdown(
            "::: exercise\n"
            "补全：客户端向 Agent 的 ________ 写入 JSON。\n\n"
            "--- answer\nstdin; stdout; stderr\n"
            "--- explanation\nstdin 进，stdout 出。\n"
            "---\n:::\n"
        )
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block.type, "exercise")
        self.assertEqual(block.kind, "fill")
        self.assertEqual(block.answers, ["stdin", "stdout", "stderr"])
        self.assertEqual(block.explanation, "stdin 进，stdout 出。")

    def test_spot_the_bug_exercise_renders_json_line_metadata(self) -> None:
        from learnloop.renderer import render_blocks
        from learnloop.templates import load_template

        blocks = parse_markdown(
            "::: exercise\n"
            "找出错误行。\n\n"
            "```python\n"
            "print('ok')\n"
            "raise RuntimeError('bad')  <!-- bug -->\n"
            "print('done')\n"
            "```\n\n"
            "--- answer\n"
            "第二行会直接抛错。\n"
            "---\n"
            ":::\n"
        )
        block = blocks[0]
        self.assertEqual(block.kind, "bug")
        self.assertEqual(block.buggy_lines, [2])
        html = render_blocks(blocks, load_template("practice"))
        self.assertIn('data-buggy-lines="[2]"', html)
        self.assertIn('class="bug-checkbox" data-line="2"', html)
        self.assertNotIn("&lt;!-- bug --&gt;", html)

    def test_perspective_exercise_renders_judgment_card_html(self) -> None:
        from learnloop.renderer import render_blocks
        from learnloop.templates import load_template

        md = (
            "::: exercise\n"
            "你团队想给 IDE 加一个助手。\n\n"
            "你会怎么选？\n\n"
            "--- perspective\n"
            "依据：基于本章对协议边界的比较。\n\n"
            "真正的边界是 IDE 如何驱动本地 Agent。\n\n"
            "--- tradeoffs\n"
            "- ACP：适合。\n"
            "- MCP：适合。\n\n"
            "--- pitfalls\n"
            "- 不要过度设计。\n"
            "---\n:::\n"
        )
        blocks = parse_markdown(md)
        template = load_template("perspective")
        html = render_blocks(blocks, template)
        self.assertIn('data-kind="perspective"', html)
        self.assertIn('class="judgment-reasoning"', html)
        self.assertIn("对比作者视角", html)
        self.assertIn("作者视角", html)
        self.assertIn("取舍与 trade-offs", html)
        self.assertIn("常见误区", html)
        self.assertIn("class=\"judgment-section perspective\"", html)
        self.assertIn("class=\"judgment-section tradeoffs\"", html)
        self.assertIn("class=\"judgment-section pitfalls\"", html)

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

    def test_markdown_image_renders_as_figure(self) -> None:
        from learnloop.renderer import render_blocks

        blocks = parse_markdown("![KV Cache decode flow](assets/decode-flow.png)")
        self.assertEqual(blocks[0].type, "figure")
        html = render_blocks(blocks)
        self.assertIn('<figure class="ll-figure">', html)
        self.assertIn('src="course-assets/decode-flow.png"', html)
        self.assertIn('alt="KV Cache decode flow"', html)

    def test_semantic_learning_components_render(self) -> None:
        from learnloop.renderer import render_blocks

        md = (
            "::: figure\n"
            "src: https://example.com/flow.png\n"
            "alt: Remote flow\n"
            "caption: A remote figure.\n"
            "source: Official diagram\n"
            ":::\n\n"
            "::: gallery\n"
            "- assets/before.png | Before | No cache.\n"
            "- assets/after.png | After | Reuse KV.\n"
            ":::\n\n"
            "::: flow\n"
            "Input -> Agent Loop -> Browser\n"
            ":::\n\n"
            "::: timeline\n"
            "- Prefill | Build initial KV\n"
            "- Decode | Append one token\n"
            ":::\n\n"
            "::: decision\n"
            "Should this use Docker now?\n\n"
            "- A. Yes\n"
            "- B. Not necessarily\n\n"
            "--- perspective\n"
            "依据：基于本章部署复杂度。\n"
            "---\n"
            ":::\n"
        )
        html = render_blocks(parse_markdown(md))
        self.assertIn('class="ll-figure"', html)
        self.assertIn('src="https://example.com/flow.png"', html)
        self.assertIn('class="ll-gallery"', html)
        self.assertIn('course-assets/before.png', html)
        self.assertIn('class="ll-flow"', html)
        self.assertIn("Agent Loop", html)
        self.assertIn('class="ll-timeline"', html)
        self.assertIn("Prefill", html)
        self.assertIn('class="ll-decision"', html)
        self.assertIn("显示判断视角", html)

    def test_course_assets_are_copied_and_rewritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "asset-course")
            assets = created / "assets"
            assets.mkdir()
            (assets / "diagram.png").write_bytes(b"fake image")
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8")
                + "\n![Local diagram](assets/diagram.png)\n",
                encoding="utf-8",
            )
            dist = build_course(created)
            html_text = (dist / "m1.html").read_text(encoding="utf-8")
            self.assertTrue((dist / "course-assets" / "diagram.png").exists())
            self.assertIn('src="course-assets/diagram.png"', html_text)

    def test_missing_image_alt_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "alt-course")
            assets = created / "assets"
            assets.mkdir()
            (assets / "no-alt.png").write_bytes(b"fake image")
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8") + "\n![](assets/no-alt.png)\n",
                encoding="utf-8",
            )
            errors = validate_course(created)
            self.assertTrue(any("missing alt text" in error for error in errors))

    def test_missing_local_image_file_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "missing-image-course")
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8") + "\n![Diagram](assets/missing.png)\n",
                encoding="utf-8",
            )
            errors = validate_course(created)
            self.assertTrue(any("file does not exist: assets/missing.png" in error for error in errors))

    def test_local_figure_must_use_image_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "raw-pdf-image-course")
            raw = created / "raw"
            raw.mkdir()
            (raw / "paper.pdf").write_bytes(b"%PDF-1.4")
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8")
                + "\n::: figure\nsrc: raw/paper.pdf\nalt: Paper figure\ncaption: Bad source.\n:::\n",
                encoding="utf-8",
            )
            errors = validate_course(created)
            self.assertTrue(any("must reference an image file" in error for error in errors))
            self.assertTrue(any("must use assets/..." in error for error in errors))

    def test_decision_without_answer_or_perspective_fails_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            created = init_course(Path(tmp), "decision-course")
            module = created / "modules" / "01.md"
            module.write_text(
                module.read_text(encoding="utf-8")
                + "\n::: decision\nShould we add Docker now?\n\n- A. Yes\n- B. No\n:::\n",
                encoding="utf-8",
            )
            errors = audit_generation_readiness(created)
            self.assertTrue(any("decision block must include perspective or answer" in error for error in errors))

    def test_plain_markdown_headings_render_by_level(self) -> None:
        from learnloop.renderer import render_blocks

        blocks = parse_markdown("### 数据来源：Observations\n\n正文")
        self.assertEqual(blocks[0].type, "heading")
        self.assertEqual(blocks[0].level, 3)
        html = render_blocks(blocks)
        self.assertIn("<h3>数据来源：Observations</h3>", html)
        self.assertNotIn("### 数据来源", html)

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
        self.assertTrue((dist / "assets" / "base.css").exists())
        for template in list_templates():
            self.assertTrue((dist / f"assets/{template.name}/style.css").exists())
            self.assertTrue((dist / f"assets/{template.name}/runtime.js").exists())
        # Confirm each module was generated with the expected template assets.
        self.assertIn("assets/base.css", (dist / "m1.html").read_text(encoding="utf-8"))
        self.assertIn("assets/tutorial/style.css", (dist / "m1.html").read_text(encoding="utf-8"))
        self.assertIn("assets/reference/style.css", (dist / "m2.html").read_text(encoding="utf-8"))
        self.assertIn("assets/practice/style.css", (dist / "m3.html").read_text(encoding="utf-8"))
        self.assertIn("assets/perspective/style.css", (dist / "m5.html").read_text(encoding="utf-8"))

    def test_all_templates_produce_non_empty_html(self) -> None:
        dist = build_course(SAMPLE)
        for path in (dist / "index.html", dist / "m1.html", dist / "m2.html", dist / "m3.html", dist / "m5.html"):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(len(text) > 0)
            self.assertIn('<main class="page">', text)
            self.assertIn("</main>", text)


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
