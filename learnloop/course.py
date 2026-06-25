from __future__ import annotations

import json
from pathlib import Path

from .model import LearnLoopError, ModuleDoc
from .parser import extract_section_text, read_course
from .renderer import build_course, validate_course
from .server import find_available_port, load_questions, serve_course

__all__ = [
    "LearnLoopError",
    "build_course",
    "init_course",
    "serve_course",
    "validate_course",
    "make_context",
    "find_available_port",
]


def make_context(course_dir: Path, question_id: str) -> str:
    course = read_course(course_dir)
    questions = load_questions(course.root / "questions.jsonl")
    question = next((q for q in questions if q.get("id") == question_id), None)
    if not question:
        raise LearnLoopError(f"Question id not found: {question_id}")

    module = next(
        (m for m in course.modules if m.id == question.get("module_id")), None
    )
    if not module:
        raise LearnLoopError(
            f"Question references missing module: {question.get('module_id')}"
        )

    module_path = course.root / module.file
    section_text = extract_section_text(
        module_path.read_text(encoding="utf-8"),
        str(question.get("section_id", "")),
    )
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
template: tutorial
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
