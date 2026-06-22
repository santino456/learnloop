from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from .model import Block, CourseDoc, LearnLoopError, ModuleDoc


SECTION_RE = re.compile(r"^(#{2,3})\s+\[([a-zA-Z0-9_-]+)\]\s+(.+?)\s*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
ORDERED_RE = re.compile(r"^\d+\.\s+(.+)$")


def read_course(course_dir: Path) -> CourseDoc:
    course_dir = course_dir.resolve()
    course_file = course_dir / "course.yaml"
    if not course_file.exists():
        raise LearnLoopError(f"Missing course.yaml in {course_dir}")

    data = parse_course_yaml(course_file.read_text(encoding="utf-8"))
    modules = [
        ModuleDoc(
            id=str(item["id"]),
            title=str(item["title"]),
            file=str(item["file"]),
            summary=str(item.get("summary", "")),
            template=str(item.get("template", "")) or None,
        )
        for item in data.get("modules", [])
    ]
    if not modules:
        raise LearnLoopError("course.yaml must define at least one module")

    return CourseDoc(
        root=course_dir,
        id=str(data.get("id", course_dir.name)),
        title=str(data.get("title", course_dir.name)),
        subtitle=str(data.get("subtitle", "")),
        audience=str(data.get("audience", "")),
        default_port=int(data.get("default_port", 8787)),
        template=str(data.get("template", "")) or None,
        modules=modules,
    )


def parse_course_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    modules: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_modules = False

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("modules:"):
            in_modules = True
            data["modules"] = modules
            continue
        if in_modules:
            if raw.startswith("  - "):
                current = {}
                modules.append(current)
                key, value = raw[4:].split(":", 1)
                current[key.strip()] = strip_yaml_value(value)
            elif raw.startswith("    ") and current is not None:
                key, value = raw.strip().split(":", 1)
                current[key.strip()] = strip_yaml_value(value)
            elif not raw.startswith(" "):
                in_modules = False
        if not in_modules and ":" in raw:
            key, value = raw.split(":", 1)
            data[key.strip()] = strip_yaml_value(value)

    return data


def strip_yaml_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_module(path: Path) -> tuple[dict[str, str], list[Block]]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, parse_markdown(text)
    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = strip_yaml_value(value)
    return frontmatter, parse_markdown(match.group(2))


def parse_markdown(text: str) -> list[Block]:
    lines = text.splitlines()
    blocks, _ = _parse_blocks(lines, 0, _never_stop)
    return blocks


def _never_stop(_line: str) -> bool:
    return False


def _parse_blocks(
    lines: list[str],
    start: int,
    stop_pred: Any,
) -> tuple[list[Block], int]:
    blocks: list[Block] = []
    i = start
    n = len(lines)

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        if stop_pred(line):
            return blocks, i
        if not line.strip():
            i += 1
            continue

        # Container blocks
        if line.startswith(":::"):
            marker = line[3:].strip()
            i += 1
            inner: list[str] = []
            while i < n and not lines[i].strip().startswith(":::"):
                inner.append(lines[i])
                i += 1
            if i < n:
                i += 1  # consume closing :::
            inner_blocks = parse_markdown("\n".join(inner))
            blocks.append(Block(type=marker, blocks=inner_blocks))
            continue

        # Fenced code blocks
        if line.startswith("```"):
            lang = line[3:].strip()
            i += 1
            content_lines: list[str] = []
            while i < n and not lines[i].startswith("```"):
                content_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1
            blocks.append(
                Block(
                    type="code",
                    language=lang,
                    content="\n".join(content_lines),
                )
            )
            continue

        # Section headings (question anchors)
        section_match = SECTION_RE.match(line)
        if section_match:
            level = len(section_match.group(1))
            section_id = section_match.group(2)
            title = section_match.group(3)
            inner_blocks, i = _parse_blocks(
                lines,
                i + 1,
                lambda l, lvl=level: _is_section_at_or_above(l, lvl),
            )
            blocks.append(
                Block(
                    type="section",
                    level=level,
                    id=section_id,
                    title=title,
                    blocks=inner_blocks,
                )
            )
            continue

        # Top-level H1 (rare; render as heading block)
        if line.startswith("# "):
            blocks.append(Block(type="heading", level=1, title=line[2:].strip()))
            i += 1
            continue

        # Callouts
        if line.startswith("> "):
            blocks.append(Block(type="callout", text=inline(line[2:].strip())))
            i += 1
            continue

        # Unordered lists
        if line.startswith("- "):
            items: list[str] = []
            while i < n and lines[i].startswith("- "):
                items.append(inline(lines[i][2:].strip()))
                i += 1
            blocks.append(Block(type="list", ordered=False, items=items))
            continue

        # Ordered lists
        ordered = ORDERED_RE.match(line)
        if ordered:
            items = []
            while i < n:
                m = ORDERED_RE.match(lines[i])
                if not m:
                    break
                items.append(inline(m.group(1)))
                i += 1
            blocks.append(Block(type="list", ordered=True, items=items))
            continue

        # Paragraph
        para_lines: list[str] = []
        while i < n and lines[i].strip():
            if (
                lines[i].startswith(":::")
                or lines[i].startswith("```")
                or SECTION_RE.match(lines[i])
                or lines[i].startswith("# ")
                or lines[i].startswith("> ")
                or lines[i].startswith("- ")
                or ORDERED_RE.match(lines[i])
            ):
                break
            para_lines.append(lines[i].strip())
            i += 1
        blocks.append(Block(type="paragraph", text=inline(" ".join(para_lines))))

    return blocks, i


def _is_section_at_or_above(line: str, level: int) -> bool:
    match = SECTION_RE.match(line)
    if not match:
        return False
    return len(match.group(1)) <= level


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def extract_section_text(markdown: str, section_id: str) -> str:
    lines = markdown.splitlines()
    collecting = False
    found: list[str] = []
    for line in lines:
        match = SECTION_RE.match(line)
        if match:
            if collecting:
                break
            collecting = match.group(2) == section_id
        if collecting:
            found.append(line)
    return "\n".join(found).strip()


def collect_sections(blocks: list[Block]) -> list[Section]:
    from .model import Section

    sections: list[Section] = []
    for block in blocks:
        if block.type == "section" and block.id:
            sections.append(Section(id=block.id, title=block.title or "", blocks=block.blocks or []))
        if block.blocks:
            sections.extend(collect_sections(block.blocks))
    return sections


def collect_block_types(blocks: list[Block]) -> set[str]:
    types: set[str] = set()
    for block in blocks:
        types.add(block.type)
        if block.blocks:
            types.update(collect_block_types(block.blocks))
    return types
