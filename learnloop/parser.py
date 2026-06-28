from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any
import yaml

from .model import Block, CourseDoc, LearnLoopError, ModuleDoc


SECTION_RE = re.compile(r"^(#{2,3})\s+\[([a-zA-Z0-9_-]+)\]\s+(.+?)\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
ORDERED_RE = re.compile(r"^\d+\.\s+(.+)$")
TABLE_RE = re.compile(r"^\|(.+)\|\s*$")
IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
INLINE_MATH_RE = re.compile(r"(?<!\$)\$([^\$\n]+?)\$(?!\$)")
BLOCK_MATH_RE = re.compile(r"\$\$([\s\S]+?)\$\$")
ARXIV_SOURCE_RE = re.compile(
    r"\[([^\]]+)\]\((https?://arxiv\.org/abs/(\d+\.\d+)(?:v\d+)?)\)"
    r"(?:(?:\s*,\s*|\s+)§\s*([\d.]+))?"
    r"(?:(?:\s*,\s*|\s+)Appendix\s+([A-Z](?:\.\d+)?))?",
    re.I,
)


def _arxiv_anchor(section: str) -> str:
    parts = section.split(".")
    if len(parts) == 1:
        return f"S{parts[0]}"
    return f"S{parts[0]}.SS{parts[1]}"


def _arxiv_appendix_anchor(section: str) -> str:
    letter, *rest = section.split(".")
    n = ord(letter.upper()) - ord("A") + 1
    if rest:
        return f"A{n}.SS{rest[0]}"
    return f"A{n}"


def _rewrite_arxiv_sources(text: str) -> tuple[str, list[str]]:
    snippets: list[str] = []

    def repl(match: re.Match[str]) -> str:
        link_text = html.escape(match.group(1))
        arxiv_id = match.group(3)
        section = match.group(4)
        appendix = match.group(5)
        suffix = ""
        anchor = ""
        if section:
            suffix = f", §{section}"
            anchor = _arxiv_anchor(section)
        if appendix:
            suffix += f", Appendix {appendix}"
            anchor = _arxiv_appendix_anchor(appendix)
        url = f"https://arxiv.org/html/{arxiv_id}"
        if anchor:
            url += f"#{anchor}"
        snippet = (
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
            f"{link_text}{suffix}</a>"
        )
        snippets.append(snippet)
        return f"\x00ARXIV{len(snippets) - 1}\x00"

    rewritten = ARXIV_SOURCE_RE.sub(repl, text)
    return rewritten, snippets


def read_course(course_dir: Path) -> CourseDoc:
    course_dir = course_dir.resolve()
    course_file = course_dir / "course.yaml"
    if not course_file.exists():
        raise LearnLoopError(f"Missing course.yaml in {course_dir}")

    data = parse_course_yaml(course_file.read_text(encoding="utf-8"))
    modules = []
    for idx, item in enumerate(data.get("modules", []), start=1):
        context = f"{course_file}: modules[{idx}]"
        modules.append(
            ModuleDoc(
                id=_required_yaml_field(item, "id", context),
                title=_required_yaml_field(item, "title", context),
                file=_required_yaml_field(item, "file", context),
                summary=str(item.get("summary", "")),
                template=str(item.get("template", "")) or None,
            )
        )
    if not modules:
        raise LearnLoopError("course.yaml must define at least one module")
    try:
        default_port = int(data.get("default_port", 8787))
    except (TypeError, ValueError) as exc:
        raise LearnLoopError(f"{course_file}: default_port must be an integer") from exc

    return CourseDoc(
        root=course_dir,
        id=str(data.get("id", course_dir.name)),
        title=str(data.get("title", course_dir.name)),
        subtitle=str(data.get("subtitle", "")),
        audience=str(data.get("audience", "")),
        default_port=default_port,
        template=str(data.get("template", "")) or None,
        modules=modules,
        lang=str(data.get("lang", "auto")),
    )


def _required_yaml_field(item: dict[str, Any], field: str, context: str) -> str:
    value = str(item.get(field, "")).strip()
    if not value:
        raise LearnLoopError(f"{context}: missing required field '{field}'")
    return value


def parse_course_yaml(text: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        raise LearnLoopError(f"Invalid course.yaml: {exc}") from exc
    if not isinstance(data, dict):
        raise LearnLoopError("course.yaml must be a mapping")
    modules = data.get("modules", [])
    if modules is None:
        data["modules"] = []
    elif not isinstance(modules, list):
        raise LearnLoopError("course.yaml modules must be a list")
    elif not all(isinstance(item, dict) for item in modules):
        raise LearnLoopError("course.yaml modules entries must be mappings")
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
        return {}, parse_markdown(text, source=str(path))
    try:
        loaded = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise LearnLoopError(f"Invalid frontmatter in {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise LearnLoopError(f"Frontmatter in {path} must be a mapping")
    frontmatter = {str(key): str(value) for key, value in loaded.items()}
    body_line_offset = match.group(1).count("\n") + 3
    return frontmatter, parse_markdown(
        match.group(2), source=str(path), line_offset=body_line_offset
    )


def parse_markdown(
    text: str, source: str | None = None, line_offset: int = 0
) -> list[Block]:
    lines = text.splitlines()
    blocks, _ = _parse_blocks(lines, 0, _never_stop, source, line_offset)
    return blocks


def _source(source: str | None, line: int) -> dict[str, Any] | None:
    if source is None:
        return None
    return {"file": source, "line": line}


def _format_location(source: str | None, line: int) -> str:
    if source:
        return f"{source}:{line}"
    return f"line {line}"


def _never_stop(_line: str) -> bool:
    return False


CONTAINER_MARKERS = {
    "answer",
    "explanation",
    "perspective",
    "tradeoffs",
    "pitfalls",
}


def split_container_content(lines: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    """Split container content into task and labeled sections.

    Markers are lines of the form '--- label' where label is one of the known
    markers. Each section continues until the next marker or a standalone '---'
    closing marker.
    """
    sections: dict[str, list[str]] = {}
    task_end = len(lines)
    marker_start: int | None = None
    current_label: str | None = None

    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped == "---":
            task_end = min(task_end, idx)
            if current_label is not None:
                sections[current_label] = lines[marker_start:idx]
                current_label = None
            continue
        if stripped.startswith("--- "):
            label = stripped[4:].strip()
            if label in CONTAINER_MARKERS:
                task_end = min(task_end, idx)
                if current_label is not None:
                    sections[current_label] = lines[marker_start:idx]
                current_label = label
                marker_start = idx + 1
                continue

    if current_label is not None:
        sections[current_label] = lines[marker_start:]

    return lines[:task_end], sections


def split_on_answer(lines: list[str]) -> tuple[list[str], list[str]]:
    """Backward-compatible splitter for simple answer-only containers."""
    task, sections = split_container_content(lines)
    return task, sections.get("answer", [])


CHOICE_RE = re.compile(r"^([A-Z])\.\s*(.+)$")
BLANK_RE = re.compile(r"_{8,}")
BUG_MARKER = re.compile(r"<!--\s*bug\s*-->$")


def classify_exercise(
    task_blocks: list[Block], answer_text: str | None
) -> tuple[str, list[str] | None, list[str] | None, list[int] | None]:
    """Classify an exercise based on task shape and answer text.

    Returns (kind, choices, answers, buggy_lines). Unknown values are None.
    """
    # Perspective exercises are identified by their marker sections.
    # We do not inspect answer_text here; the caller already has perspective etc.

    # Multiple choice: task contains a list whose items look like A. B. C.
    for block in task_blocks:
        if block.type == "list" and block.items:
            choices: list[str] = []
            valid = True
            for item in block.items:
                match = CHOICE_RE.match(item)
                if not match:
                    valid = False
                    break
                # Strip inline HTML generated by `inline` so choices are plain text.
                text = re.sub(r"<[^>]+>", "", match.group(2)).strip()
                choices.append(text)
            if valid and len(choices) >= 2:
                return "choice", choices, None, None

    # Fill-in-the-blank: task text or code contains 8+ consecutive underscores.
    for block in task_blocks:
        candidate = ""
        if block.type == "paragraph" and block.text:
            candidate = block.text
        elif block.type == "code" and block.content:
            candidate = block.content
        if candidate and BLANK_RE.search(candidate):
            answers = _split_answers(answer_text)
            return "fill", None, answers, None

    # Spot-the-bug: code block inside the task contains <!-- bug --> markers.
    buggy_lines: list[int] = []
    for block in task_blocks:
        if block.type == "code" and block.content:
            for idx, line in enumerate(block.content.splitlines(), start=1):
                if BUG_MARKER.search(line.rstrip()):
                    buggy_lines.append(idx)
    if buggy_lines:
        return "bug", None, _split_answers(answer_text), buggy_lines

    return "open", None, None, None


def _split_answers(answer_text: str | None) -> list[str] | None:
    if not answer_text:
        return None
    parts = [part.strip() for part in answer_text.split(";")]
    parts = [part for part in parts if part]
    return parts if parts else None


def _parse_key_values(lines: list[str]) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for raw in lines:
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        if key:
            attrs[key] = value.strip()
    return attrs


def _parse_gallery_items(lines: list[str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped.startswith("- "):
            continue
        parts = [part.strip() for part in stripped[2:].split("|")]
        if not parts or not parts[0]:
            continue
        items.append(
            {
                "src": parts[0],
                "alt": parts[1] if len(parts) > 1 else "",
                "caption": parts[2] if len(parts) > 2 else "",
            }
        )
    return items


def _parse_timeline_items(lines: list[str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped.startswith("- "):
            continue
        parts = [part.strip() for part in stripped[2:].split("|", 1)]
        if not parts or not parts[0]:
            continue
        items.append({"title": parts[0], "text": parts[1] if len(parts) > 1 else ""})
    return items


def _parse_flow_items(lines: list[str]) -> list[str]:
    text = " ".join(line.strip() for line in lines if line.strip())
    return [part.strip() for part in text.split("->") if part.strip()]


def _split_leading_attrs(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    attrs: dict[str, str] = {}
    body_start = 0
    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            body_start = idx + 1
            break
        if ":" not in raw:
            body_start = idx
            break
        key, value = raw.split(":", 1)
        key = key.strip()
        if not key:
            body_start = idx
            break
        attrs[key] = value.strip()
        body_start = idx + 1
    return attrs, lines[body_start:]


def _parse_compare_items(lines: list[str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped.startswith("- "):
            continue
        parts = [part.strip() for part in stripped[2:].split("|")]
        if len(parts) < 3:
            continue
        items.append({"label": parts[0], "left": parts[1], "right": parts[2]})
    return items


def _parse_decision(
    inner: list[str], source: str | None = None, line_offset: int = 0
) -> Block:
    task_lines, sections = split_container_content(inner)
    task_blocks = parse_markdown(
        "\n".join(task_lines), source=source, line_offset=line_offset
    )
    choices: list[str] = []
    for block in task_blocks:
        if block.type != "list" or not block.items:
            continue
        for item in block.items:
            text = re.sub(r"<[^>]+>", "", item).strip()
            choices.append(text)
    return Block(
        type="decision",
        source=_source(source, line_offset),
        blocks=task_blocks,
        choices=choices or None,
        answer="\n".join(sections.get("answer", [])).strip() or None,
        explanation="\n".join(sections.get("explanation", [])).strip() or None,
        perspective="\n".join(sections.get("perspective", [])).strip() or None,
    )


def _parse_blocks(
    lines: list[str],
    start: int,
    stop_pred: Any,
    source: str | None,
    line_offset: int,
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
            container_start = i
            marker = line[3:].strip()
            i += 1
            inner: list[str] = []
            while i < n and not lines[i].strip().startswith(":::"):
                inner.append(lines[i])
                i += 1
            if i >= n:
                raise LearnLoopError(
                    f"{_format_location(source, line_offset + container_start + 1)}: "
                    f"unclosed ::: {marker or 'container'} block"
                )
            i += 1  # consume closing :::
            inner_line_offset = line_offset + container_start + 1
            if marker in ("exercise", "checkpoint"):
                task_lines, sections = split_container_content(inner)
                task_blocks = parse_markdown(
                    "\n".join(task_lines), source=source, line_offset=inner_line_offset
                )
                answer_text = "\n".join(sections.get("answer", [])).strip() or None
                explanation_text = "\n".join(sections.get("explanation", [])).strip() or None
                perspective_text = "\n".join(sections.get("perspective", [])).strip() or None
                tradeoffs_text = "\n".join(sections.get("tradeoffs", [])).strip() or None
                pitfalls_text = "\n".join(sections.get("pitfalls", [])).strip() or None

                kind, choices, answers, buggy_lines = classify_exercise(
                    task_blocks, answer_text
                )
                if perspective_text or tradeoffs_text or pitfalls_text:
                    kind = "perspective"

                blocks.append(
                    Block(
                        type=marker,
                        source=_source(source, line_offset + container_start + 1),
                        blocks=task_blocks,
                        answer=answer_text,
                        explanation=explanation_text,
                        kind=kind,
                        choices=choices,
                        answers=answers,
                        buggy_lines=buggy_lines,
                        perspective=perspective_text,
                        tradeoffs=tradeoffs_text,
                        pitfalls=pitfalls_text,
                    )
                )
            elif marker == "figure":
                blocks.append(
                    Block(
                        type="figure",
                        source=_source(source, line_offset + container_start + 1),
                        attrs=_parse_key_values(inner),
                    )
                )
            elif marker == "gallery":
                blocks.append(
                    Block(
                        type="gallery",
                        source=_source(source, line_offset + container_start + 1),
                        media=_parse_gallery_items(inner),
                    )
                )
            elif marker == "flow":
                blocks.append(
                    Block(
                        type="flow",
                        source=_source(source, line_offset + container_start + 1),
                        items=_parse_flow_items(inner),
                    )
                )
            elif marker == "timeline":
                blocks.append(
                    Block(
                        type="timeline",
                        source=_source(source, line_offset + container_start + 1),
                        media=_parse_timeline_items(inner),
                    )
                )
            elif marker == "concept":
                attrs, body_lines = _split_leading_attrs(inner)
                blocks.append(
                    Block(
                        type="concept",
                        source=_source(source, line_offset + container_start + 1),
                        attrs=attrs,
                        blocks=parse_markdown(
                            "\n".join(body_lines),
                            source=source,
                            line_offset=inner_line_offset + len(inner) - len(body_lines),
                        )
                        if body_lines
                        else None,
                    )
                )
            elif marker == "compare":
                attrs, body_lines = _split_leading_attrs(inner)
                blocks.append(
                    Block(
                        type="compare",
                        source=_source(source, line_offset + container_start + 1),
                        attrs=attrs,
                        media=_parse_compare_items(body_lines),
                    )
                )
            elif marker == "evidence":
                attrs, body_lines = _split_leading_attrs(inner)
                blocks.append(
                    Block(
                        type="evidence",
                        source=_source(source, line_offset + container_start + 1),
                        attrs=attrs,
                        blocks=parse_markdown(
                            "\n".join(body_lines),
                            source=source,
                            line_offset=inner_line_offset + len(inner) - len(body_lines),
                        )
                        if body_lines
                        else None,
                    )
                )
            elif marker == "decision":
                decision = _parse_decision(inner, source, inner_line_offset)
                decision.source = _source(source, line_offset + container_start + 1)
                blocks.append(decision)
            else:
                inner_blocks = parse_markdown(
                    "\n".join(inner), source=source, line_offset=inner_line_offset
                )
                blocks.append(
                    Block(
                        type=marker,
                        source=_source(source, line_offset + container_start + 1),
                        blocks=inner_blocks,
                    )
                )
            continue

        # Fenced code blocks
        if line.startswith("```"):
            code_start = i
            lang = line[3:].strip()
            i += 1
            content_lines: list[str] = []
            while i < n and not lines[i].startswith("```"):
                content_lines.append(lines[i])
                i += 1
            if i >= n:
                raise LearnLoopError(
                    f"{_format_location(source, line_offset + code_start + 1)}: "
                    "unclosed fenced code block"
                )
            i += 1
            blocks.append(
                Block(
                    type="code",
                    source=_source(source, line_offset + code_start + 1),
                    language=lang,
                    content="\n".join(content_lines),
                )
            )
            continue

        # Section headings (question anchors)
        section_match = SECTION_RE.match(line)
        if section_match:
            section_start = i
            level = len(section_match.group(1))
            section_id = section_match.group(2)
            title = section_match.group(3)
            inner_blocks, i = _parse_blocks(
                lines,
                i + 1,
                lambda l, lvl=level: _is_section_at_or_above(l, lvl),
                source,
                line_offset,
            )
            blocks.append(
                Block(
                    type="section",
                    source=_source(source, line_offset + section_start + 1),
                    level=level,
                    id=section_id,
                    title=title,
                    blocks=inner_blocks,
                )
            )
            continue

        # Plain headings without question anchors.
        heading_match = HEADING_RE.match(line)
        if heading_match:
            blocks.append(
                Block(
                    type="heading",
                    source=_source(source, line_offset + i + 1),
                    level=len(heading_match.group(1)),
                    title=heading_match.group(2).strip(),
                )
            )
            i += 1
            continue

        # Callouts
        if line.startswith("> "):
            blocks.append(
                Block(
                    type="callout",
                    source=_source(source, line_offset + i + 1),
                    text=inline(line[2:].strip()),
                )
            )
            i += 1
            continue

        # Markdown image blocks
        image = IMAGE_RE.match(line)
        if image:
            blocks.append(
                Block(
                    type="figure",
                    source=_source(source, line_offset + i + 1),
                    attrs={"alt": image.group(1).strip(), "src": image.group(2).strip()},
                )
            )
            i += 1
            continue

        # Unordered lists
        if line.startswith("- "):
            list_start = i
            items: list[str] = []
            while i < n and lines[i].startswith("- "):
                items.append(inline(lines[i][2:].strip()))
                i += 1
            blocks.append(
                Block(
                    type="list",
                    source=_source(source, line_offset + list_start + 1),
                    ordered=False,
                    items=items,
                )
            )
            continue

        # Ordered lists
        ordered = ORDERED_RE.match(line)
        if ordered:
            list_start = i
            items = []
            while i < n:
                m = ORDERED_RE.match(lines[i])
                if not m:
                    break
                items.append(inline(m.group(1)))
                i += 1
            blocks.append(
                Block(
                    type="list",
                    source=_source(source, line_offset + list_start + 1),
                    ordered=True,
                    items=items,
                )
            )
            continue

        # Tables
        table = _parse_table(lines, i, source, line_offset)
        if table:
            blocks.append(table[0])
            i = table[1]
            continue

        # Paragraph
        para_start = i
        para_lines: list[str] = []
        while i < n and lines[i].strip():
            if (
                lines[i].startswith(":::")
                or lines[i].startswith("```")
                or SECTION_RE.match(lines[i])
                or HEADING_RE.match(lines[i])
                or lines[i].startswith("> ")
                or IMAGE_RE.match(lines[i])
                or lines[i].startswith("- ")
                or ORDERED_RE.match(lines[i])
            ):
                break
            para_lines.append(lines[i].strip())
            i += 1
        blocks.append(
            Block(
                type="paragraph",
                source=_source(source, line_offset + para_start + 1),
                text=inline(" ".join(para_lines)),
            )
        )

    return blocks, i


def _is_section_at_or_above(line: str, level: int) -> bool:
    match = SECTION_RE.match(line)
    if not match:
        return False
    return len(match.group(1)) <= level


def _parse_table(
    lines: list[str], start: int, source: str | None = None, line_offset: int = 0
) -> tuple[Block, int] | None:
    """Parse a Markdown table starting at `start`.

    Returns a table Block and the index of the first line after the table,
    or None if no valid table is found.
    """
    n = len(lines)
    if start >= n or not TABLE_RE.match(lines[start]):
        return None

    def parse_row(line: str) -> list[str]:
        # Strip leading/trailing pipes, then split by pipe
        content = line.strip()
        if content.startswith("|"):
            content = content[1:]
        if content.endswith("|"):
            content = content[:-1]
        return [cell.strip() for cell in content.split("|")]

    header = parse_row(lines[start])
    if not header or start + 1 >= n:
        return None

    separator = parse_row(lines[start + 1])
    # Separator row should contain only dashes (with optional alignment colons)
    if not all(re.match(r"^:?-+:?$", cell.strip()) for cell in separator):
        if TABLE_RE.match(lines[start + 1]):
            raise LearnLoopError(
                f"{_format_location(source, line_offset + start + 2)}: "
                "malformed table separator"
            )
        return None

    rows: list[list[str]] = []
    i = start + 2
    while i < n:
        match = TABLE_RE.match(lines[i])
        if not match:
            break
        rows.append(parse_row(lines[i]))
        i += 1

    if not rows:
        raise LearnLoopError(
            f"{_format_location(source, line_offset + start + 1)}: "
            "table must include at least one body row"
        )

    return (
        Block(
            type="table",
            source=_source(source, line_offset + start + 1),
            headers=header,
            rows=rows,
        ),
        i,
    )


def inline(text: str) -> str:
    # Protect math, arXiv source links, other links, and generated HTML.
    maths: list[str] = []
    arxivs: list[str] = []
    links: list[str] = []

    text, arxivs = _rewrite_arxiv_sources(text)

    def math_repl(match: re.Match[str], kind: str) -> str:
        wrapper = "div" if kind == "block" else "span"
        maths.append(f'<{wrapper} class="math {kind}">{match.group(0)}</{wrapper}>')
        return f"\x00MATH{len(maths) - 1}\x00"

    def link_repl(match: re.Match[str]) -> str:
        link_text = html.escape(match.group(1))
        url = html.escape(match.group(2))
        links.append(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">{link_text}</a>'
        )
        return f"\x00LINK{len(links) - 1}\x00"

    text = BLOCK_MATH_RE.sub(lambda m: math_repl(m, "block"), text)
    text = INLINE_MATH_RE.sub(lambda m: math_repl(m, "inline"), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)

    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)

    for i, math_html in enumerate(maths):
        escaped = escaped.replace(f"\x00MATH{i}\x00", math_html)
    for i, link_html in enumerate(links):
        escaped = escaped.replace(f"\x00LINK{i}\x00", link_html)
    for i, arxiv_html in enumerate(arxivs):
        escaped = escaped.replace(f"\x00ARXIV{i}\x00", arxiv_html)

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
            sections.append(
                Section(
                    id=block.id,
                    title=block.title or "",
                    blocks=block.blocks or [],
                    source=block.source,
                )
            )
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
