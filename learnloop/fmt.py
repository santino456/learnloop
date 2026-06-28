from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .parser import FRONTMATTER_RE, read_course

CONTAINER_RE = re.compile(r"^:::\s*(\S*)\s*$")
SECTION_RE = re.compile(r"^(#{2,3})\s+\[[a-zA-Z0-9_-]+\]\s+.+?\s*$")
ROW_RE = re.compile(r"^(\s*- )\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$")


def _format_frontmatter(data: dict[str, Any]) -> str:
    ordered: dict[str, Any] = {}
    for key in ("id", "title", "summary", "template"):
        if key in data:
            ordered[key] = data[key]
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value

    dumped = yaml.safe_dump(
        ordered,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    return f"---\n{dumped}---\n"


def _container_spans(lines: list[str]) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    stack: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        match = CONTAINER_RE.match(line)
        if not match:
            continue
        if stack:
            start, marker = stack.pop()
            spans.append((start, i, marker))
        elif match.group(1):
            stack.append((i, match.group(1)))
    return spans


def _attr_region_end(lines: list[str]) -> int:
    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            return idx
        if ":" not in raw:
            return idx
        key = raw.split(":", 1)[0].strip()
        if not key or " " in key:
            return idx
    return len(lines)


def _normalize_row(line: str) -> str:
    match = ROW_RE.match(line)
    if not match:
        return line
    cells = [match.group(2).strip(), match.group(3).strip(), match.group(4).strip()]
    return f"{match.group(1)}{cells[0]} | {cells[1]} | {cells[2]}"


def _format_body(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []

    for i, raw in enumerate(lines):
        line = raw.rstrip()

        # Section headings should stand on their own with surrounding blank lines.
        if SECTION_RE.match(line):
            if out and out[-1] != "":
                out.append("")
            out.append(line)
            if i + 1 < len(lines) and lines[i + 1].strip():
                out.append("")
            continue

        # Container markers.
        container_match = CONTAINER_RE.match(line)
        if container_match:
            marker = container_match.group(1)
            if marker:
                # Opening marker: keep it close to the attribute lines that follow.
                if out and out[-1] != "":
                    out.append("")
                out.append(line)
            else:
                # Closing marker: keep it close to the content above, blank after.
                out.append(line)
                if i + 1 < len(lines) and lines[i + 1].strip():
                    out.append("")
            continue

        if ROW_RE.match(line):
            out.append(_normalize_row(line))
            continue

        out.append(line)

    # Collapse runs of more than two blank lines.
    formatted = "\n".join(out)
    formatted = re.sub(r"\n{3,}", "\n\n", formatted)
    return formatted


def _sort_compare_rows(lines: list[str]) -> list[str]:
    spans = _container_spans(lines)
    for start, end, marker in reversed(spans):
        if marker != "compare":
            continue
        inner = lines[start + 1 : end]
        attr_end = _attr_region_end(inner)

        # Find the contiguous block of list rows inside the compare container.
        row_start = attr_end
        while row_start < len(inner) and not inner[row_start].strip().startswith("- "):
            row_start += 1
        row_end = row_start
        while row_end < len(inner) and inner[row_end].strip().startswith("- "):
            row_end += 1

        if row_start >= row_end:
            continue
        rows = inner[row_start:row_end]

        def sort_key(row: str) -> str:
            label = row.strip().removeprefix("- ").split("|", 1)[0].strip()
            return label.lower()

        rows.sort(key=sort_key)
        inner[row_start:row_end] = rows
        lines[start + 1 : end] = inner

    return lines


def format_module_text(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if match:
        try:
            data = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            data = None
        if isinstance(data, dict):
            frontmatter = _format_frontmatter(data)
            body = match.group(2)
        else:
            frontmatter = None
            body = text
    else:
        frontmatter = None
        body = text

    body = _format_body(body)
    lines = body.splitlines()
    lines = _sort_compare_rows(lines)
    body = "\n".join(lines)

    if frontmatter is not None:
        result = frontmatter + "\n" + body.lstrip("\n")
    else:
        result = body
    if not result.endswith("\n"):
        result += "\n"
    return result


def fmt_course(course_dir: Path, check: bool = False) -> list[str]:
    """Format all module files in a course. Returns changed paths (or notes in check mode)."""
    course_dir = course_dir.resolve()
    try:
        course = read_course(course_dir)
        module_files = [course.root / module.file for module in course.modules]
    except Exception:
        module_files = sorted((course_dir / "modules").glob("*.md"))

    changed: list[str] = []
    for path in module_files:
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        formatted = format_module_text(original)
        if formatted == original:
            continue
        rel = path.relative_to(course_dir)
        if check:
            changed.append(f"{rel}: would reformat")
        else:
            path.write_text(formatted, encoding="utf-8")
            changed.append(str(rel))
    return changed
