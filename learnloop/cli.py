from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .course import (
    LearnLoopError,
    build_course,
    init_course,
    make_context,
    serve_course,
    validate_course,
)
from .parser import read_course
from .templates import list_templates, select_template


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="learnloop", description="Local-first adaptive learning loops."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Create a new course skeleton.")
    init_p.add_argument("course_slug")
    init_p.add_argument(
        "--target", default=".", help="Directory that will contain the course folder."
    )

    build_p = sub.add_parser("build", help="Generate HTML into dist/.")
    build_p.add_argument("course_dir", nargs="?", default=".")

    serve_p = sub.add_parser("serve", help="Serve a course locally.")
    serve_p.add_argument("course_dir", nargs="?", default=".")
    serve_p.add_argument("--port", type=int, default=None)

    validate_p = sub.add_parser("validate", help="Validate course source and question logs.")
    validate_p.add_argument("course_dir", nargs="?", default=".")

    context_p = sub.add_parser("context", help="Print agent context for one question.")
    context_p.add_argument("course_dir", nargs="?", default=".")
    context_p.add_argument("--question-id", required=True)

    templates_p = sub.add_parser(
        "templates", help="List available templates and selected course/module templates."
    )
    templates_p.add_argument("course_dir", nargs="?", default=".")

    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            created = init_course(Path(args.target), args.course_slug)
            print(created)
        elif args.command == "build":
            dist = build_course(Path(args.course_dir))
            print(f"Built {dist}")
        elif args.command == "serve":
            serve_course(Path(args.course_dir), args.port)
        elif args.command == "validate":
            errors = validate_course(Path(args.course_dir))
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print("Course is valid")
        elif args.command == "context":
            print(make_context(Path(args.course_dir), args.question_id))
        elif args.command == "templates":
            list_templates_command(Path(args.course_dir))
    except LearnLoopError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


def list_templates_command(course_dir: Path) -> None:
    available = list_templates()
    print("Available templates:")
    for template in available:
        print(f"  - {template.name}")

    course = read_course(course_dir)
    print(f"\nCourse default: {course.template or '(none)'}")
    print("Module templates:")
    for module in course.modules:
        template = select_template(course_dir, course, module)
        print(f"  {module.id} ({module.file}): {template.name}")
