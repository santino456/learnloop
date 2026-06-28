from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import yaml

from .i18n import detect_language
from .parser import read_course

CONTAINER_RE = re.compile(r"^:::\s*(\S*)\s*$")
ATTR_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$")
BOLD_RE = re.compile(r"^\*\*(.+?)\*\*\s*$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _placeholder(kind: str, lang: str) -> str:
    phrases = {
        "title": {"zh": "未命名概念", "en": "Untitled concept"},
        "source": {"zh": "来源待补充", "en": "Source needed"},
        "basis": {"zh": "依据：待补充", "en": "Basis: to be added"},
    }
    return phrases.get(kind, {}).get(lang, phrases.get(kind, {}).get("en", ""))


def _container_spans(
    lines: list[str],
) -> tuple[list[tuple[int, int, str]], list[int]]:
    """Return closed container spans and indices of dangling lone closers."""
    spans: list[tuple[int, int, str]] = []
    danglings: list[int] = []
    stack: list[tuple[int, str]] = []

    for i, line in enumerate(lines):
        match = CONTAINER_RE.match(line)
        if not match:
            continue
        marker = match.group(1)
        if stack:
            start, open_marker = stack.pop()
            spans.append((start, i, open_marker))
        elif marker:
            stack.append((i, marker))
        else:
            danglings.append(i)

    # Close any containers still open at EOF so the file becomes parseable.
    while stack:
        start, open_marker = stack.pop()
        lines.append(":::")
        spans.append((start, len(lines) - 1, open_marker))

    return spans, danglings


def _attr_region_end(lines: list[str]) -> int:
    """Return first index after the leading key:value attribute region."""
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


def _detect_block_language(inner: list[str]) -> str:
    text = "\n".join(inner)
    return detect_language(text) if text.strip() else "zh"


def _infer_concept_title(inner: list[str], lang: str) -> str:
    attr_end = _attr_region_end(inner)
    for raw in inner[attr_end:]:
        stripped = raw.strip()
        if not stripped or stripped.startswith("- ") or stripped.startswith("```"):
            continue
        match = BOLD_RE.match(stripped)
        if match:
            return match.group(1).strip()
        # First sentence-ish chunk of plain text.
        for sep in (".", "。", "\n"):
            if sep in stripped:
                candidate = stripped.split(sep, 1)[0].strip()
                if candidate:
                    return candidate[:80]
        if stripped:
            return stripped[:80]
    return _placeholder("title", lang)


def _infer_source(inner: list[str]) -> str | None:
    text = "\n".join(inner)
    match = LINK_RE.search(text)
    return match.group(2) if match else None


def _has_attr(inner: list[str], name: str) -> bool:
    attr_end = _attr_region_end(inner)
    for raw in inner[:attr_end]:
        key = raw.split(":", 1)[0].strip()
        if key == name:
            return True
    return False


def _insert_attr(inner: list[str], name: str, value: str) -> list[str]:
    """Insert a missing attribute at the top of the attribute region."""
    attr_end = _attr_region_end(inner)
    new_line = f"{name}: {value}"
    if attr_end == 0:
        return [new_line, ""] + inner
    return [inner[0], new_line] + inner[1:]


def _fix_concept(inner: list[str]) -> list[str]:
    lang = _detect_block_language(inner)
    if not _has_attr(inner, "title"):
        title = _infer_concept_title(inner, lang)
        inner = _insert_attr(inner, "title", title)
    return inner


def _fix_evidence(inner: list[str]) -> list[str]:
    lang = _detect_block_language(inner)
    if not _has_attr(inner, "status"):
        inner = _insert_attr(inner, "status", "unverified")
    if not _has_attr(inner, "source"):
        source = _infer_source(inner)
        if not source:
            source = _placeholder("source", lang)
        inner = _insert_attr(inner, "source", source)
    return inner


def _has_section(inner: list[str], markers: Iterable[str]) -> bool:
    for raw in inner:
        stripped = raw.strip()
        if stripped.startswith("--- "):
            label = stripped[4:].strip()
            if label in set(markers):
                return True
    return False


def _fix_decision(inner: list[str]) -> list[str]:
    if _has_section(inner, {"perspective", "answer"}):
        return inner
    lang = _detect_block_language(inner)
    if inner and inner[-1].strip():
        inner.append("")
    inner.append("--- perspective")
    inner.append(_placeholder("basis", lang))
    return inner


def _fix_container_inner(marker: str, inner: list[str]) -> list[str]:
    if marker == "concept":
        return _fix_concept(inner)
    if marker == "evidence":
        return _fix_evidence(inner)
    if marker == "decision":
        return _fix_decision(inner)
    return inner


def fix_module_text(text: str) -> tuple[str, list[str]]:
    """Return fixed module text and a list of human-readable changes."""
    lines = text.splitlines()
    spans, danglings = _container_spans(lines)

    if danglings:
        # Remove lone dangling closers; recompute spans on the cleaned lines.
        lines = [line for idx, line in enumerate(lines) if idx not in danglings]
        spans, _ = _container_spans(lines)

    notes: list[str] = []

    # Work backwards so earlier line indices remain stable.
    for start, end, marker in reversed(spans):
        inner = lines[start + 1 : end]
        fixed = _fix_container_inner(marker, inner)
        if fixed != inner:
            lines[start + 1 : end] = fixed
            notes.append(f"fixed ::: {marker} at line {start + 1}")

    result = "\n".join(lines)
    if text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result, notes


def fix_course(course_dir: Path, check: bool = False) -> list[str]:
    """Fix all module files in a course. Returns changed paths (or notes in check mode)."""
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
        fixed, notes = fix_module_text(original)
        if fixed == original:
            continue
        rel = path.relative_to(course_dir)
        if check:
            for note in notes:
                changed.append(f"{rel}: {note}")
        else:
            path.write_text(fixed, encoding="utf-8")
            changed.append(str(rel))
    return changed
