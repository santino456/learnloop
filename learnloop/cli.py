from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .course import (
    LearnLoopError,
    build_course,
    init_course,
    make_context,
    scaffold_course,
    serve_course,
    validate_course,
)
from .knowledge import audit_generation_readiness
from .ingest import ingest_material
from .model import ModuleDoc
from .parser import parse_module, read_course
from .server import start_library, status_library, stop_library
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

    scaffold_p = sub.add_parser(
        "scaffold-course",
        aliases=["scaffold"],
        help="Create a source-grounded course generation workspace.",
    )
    scaffold_p.add_argument("course_slug")
    scaffold_p.add_argument(
        "--target", default=".", help="Directory that will contain the course folder."
    )
    scaffold_p.add_argument("--title", default=None, help="Course title.")
    scaffold_p.add_argument("--topic", default=None, help="Topic or learning domain.")
    scaffold_p.add_argument("--audience", default=None, help="Target learner.")

    build_p = sub.add_parser("build", help="Generate HTML into dist/.")
    build_p.add_argument("course_dir", nargs="?", default=".")

    start_p = sub.add_parser("start", help="Start the local LearnLoop library service in the background.")
    start_p.add_argument("courses_root", nargs="?", default="courses")
    start_p.add_argument("--port", type=int, default=8787)
    start_p.add_argument(
        "--auto-port",
        action="store_true",
        help="Use the requested port if available, otherwise pick the next free port.",
    )

    stop_p = sub.add_parser("stop", help="Stop the local LearnLoop library service.")
    stop_p.add_argument("courses_root", nargs="?", default="courses")

    status_p = sub.add_parser("status", help="Show the local LearnLoop library service status.")
    status_p.add_argument("courses_root", nargs="?", default="courses")

    serve_p = sub.add_parser("serve", help="Serve a course library in the foreground.")
    serve_p.add_argument("course_dir", nargs="?", default="courses")
    serve_p.add_argument("--port", type=int, default=None)
    serve_p.add_argument(
        "--auto-port",
        action="store_true",
        help="Use the requested/default port if available, otherwise pick the next free port.",
    )

    validate_p = sub.add_parser("validate", help="Validate course source and question logs.")
    validate_p.add_argument("course_dir", nargs="?", default=".")

    audit_p = sub.add_parser(
        "audit", help="Audit generated course process evidence and content-form choices."
    )
    audit_p.add_argument("course_dir", nargs="?", default=".")

    context_p = sub.add_parser("context", help="Print agent context for one question.")
    context_p.add_argument("course_dir", nargs="?", default=".")
    context_p.add_argument("--question-id", required=True)

    ingest_p = sub.add_parser(
        "ingest", help="Extract a source file into a structured LearnLoop material pack."
    )
    ingest_p.add_argument("source_file")
    ingest_p.add_argument(
        "--course",
        default=".",
        help="Course directory that will receive .learnloop/materials/ and assets/ output.",
    )
    ingest_p.add_argument(
        "--backend",
        default="auto",
        help="Extraction backend. Base install supports auto, pymupdf, python-docx, python-pptx, plain-text.",
    )
    ingest_p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the existing material pack for this source.",
    )

    templates_p = sub.add_parser(
        "templates", help="List available templates and selected course/module templates."
    )
    templates_p.add_argument("course_dir", nargs="?", default=".")

    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            created = init_course(Path(args.target), args.course_slug)
            print(created)
        elif args.command in {"scaffold-course", "scaffold"}:
            created = scaffold_course(
                Path(args.target),
                args.course_slug,
                title=args.title,
                topic=args.topic,
                audience=args.audience,
            )
            print(created)
        elif args.command == "build":
            dist = build_course(Path(args.course_dir))
            print(f"Built {dist}")
        elif args.command == "start":
            start_library(Path(args.courses_root), args.port, auto_port=args.auto_port)
        elif args.command == "stop":
            stop_library(Path(args.courses_root))
        elif args.command == "status":
            status_library(Path(args.courses_root))
        elif args.command == "serve":
            serve_course(Path(args.course_dir), args.port, auto_port=args.auto_port)
        elif args.command == "validate":
            errors = validate_course(Path(args.course_dir))
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print("Course is valid")
        elif args.command == "audit":
            errors = audit_generation_readiness(Path(args.course_dir))
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print("Course generation audit passed")
        elif args.command == "context":
            print(make_context(Path(args.course_dir), args.question_id))
        elif args.command == "ingest":
            result = ingest_material(
                Path(args.source_file),
                Path(args.course),
                backend=args.backend,
                overwrite=args.overwrite,
            )
            print(f"Material pack: {result.material_dir}")
            print(f"Chunks: {result.chunks} -> {result.chunks_jsonl}")
            if result.figures_md:
                print(f"Figures: {result.figures} -> {result.figures_md}")
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
        try:
            frontmatter, _ = parse_module(course.root / module.file)
        except Exception:
            frontmatter = {}
        effective_module = ModuleDoc(
            id=module.id,
            title=module.title,
            file=module.file,
            summary=frontmatter.get("summary", module.summary),
            template=frontmatter.get("template") or module.template,
        )
        template = select_template(course_dir, course, effective_module)
        print(f"  {module.id} ({module.file}): {template.name}")
