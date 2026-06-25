from __future__ import annotations

import sys
from pathlib import Path

from .renderer import validate_course
from .server import CourseLibrary
from .templates import list_templates


def doctor_report(courses_root: Path) -> tuple[int, list[str]]:
    """Return an install/course health report.

    The command is intentionally read-only: it does not start a server, build
    courses, or create pidfiles. A missing courses directory is a warning rather
    than an error so a fresh install can still pass with actionable next steps.
    """
    lines: list[str] = ["LearnLoop doctor"]
    exit_code = 0

    if sys.version_info < (3, 9):
        lines.append(f"ERROR Python 3.9+ required, found {sys.version.split()[0]}")
        exit_code = 1
    else:
        lines.append(f"OK Python {sys.version.split()[0]}")

    try:
        templates = list_templates()
    except Exception as exc:  # pragma: no cover - defensive packaging check
        lines.append(f"ERROR templates are not available: {exc}")
        return 1, lines
    if not templates:
        lines.append("ERROR no templates installed")
        exit_code = 1
    else:
        names = ", ".join(template.name for template in templates)
        lines.append(f"OK templates: {names}")

    root = courses_root.resolve()
    if not root.exists():
        lines.append(f"WARN courses root does not exist: {root}")
        lines.append("NEXT create it with: mkdir -p courses")
        lines.append("NEXT create a course with: learnloop init demo --target courses")
        return exit_code, lines

    library = CourseLibrary(root)
    try:
        entries = library.entries()
    except Exception as exc:
        lines.append(f"ERROR cannot scan courses root {root}: {exc}")
        return 1, lines

    if not entries:
        lines.append(f"WARN no courses found under {root}")
        lines.append("NEXT put course folders with course.yaml under this directory")
        return exit_code, lines

    lines.append(f"OK courses discovered: {len(entries)}")
    for entry in entries:
        label = f"{entry.id} ({entry.root})"
        if entry.error:
            lines.append(f"ERROR {label}: {entry.error}")
            exit_code = 1
            continue
        errors = validate_course(entry.root)
        if errors:
            lines.append(f"ERROR {label}: validation failed")
            lines.extend(f"  - {error}" for error in errors)
            exit_code = 1
        else:
            lines.append(f"OK {label}: valid")

    return exit_code, lines


def print_doctor_report(courses_root: Path) -> int:
    exit_code, lines = doctor_report(courses_root)
    for line in lines:
        print(line)
    return exit_code
