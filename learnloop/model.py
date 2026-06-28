from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class LearnLoopError(Exception):
    pass


@dataclass
class CourseDoc:
    root: Path
    id: str
    title: str
    subtitle: str
    audience: str
    default_port: int
    template: str | None
    modules: list[ModuleDoc]
    lang: str = "auto"


@dataclass
class ModuleDoc:
    id: str
    title: str
    file: str
    summary: str = ""
    template: str | None = None


@dataclass
class Section:
    id: str
    title: str
    blocks: list[Block]
    source: dict[str, Any] | None = None


@dataclass
class Block:
    type: str
    source: dict[str, Any] | None = None
    level: int | None = None
    id: str | None = None
    title: str | None = None
    blocks: list[Block] | None = None
    text: str | None = None
    ordered: bool | None = None
    items: list[str] | None = None
    language: str | None = None
    content: str | None = None
    answer: str | None = None
    explanation: str | None = None
    headers: list[str] | None = None
    rows: list[list[str]] | None = None
    kind: str | None = None
    choices: list[str] | None = None
    answers: list[str] | None = None
    buggy_lines: list[int] | None = None
    perspective: str | None = None
    tradeoffs: str | None = None
    pitfalls: str | None = None
    attrs: dict[str, str] | None = None
    media: list[dict[str, str]] | None = None
