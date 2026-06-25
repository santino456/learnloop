from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .model import Block
from .parser import parse_module, read_course
from .templates import select_template


CLAIM_STATUSES = {
    "verified",
    "unverified",
    "conflicting",
    "needs-human-review",
    "agent-inference",
}


def validate_knowledge_state(course_dir: Path) -> list[str]:
    workspace = course_dir / ".learnloop"
    if not workspace.exists():
        return []

    errors: list[str] = []
    source_ids = _read_source_ids(workspace / "source_inventory.yaml")
    errors.extend(_validate_claims(workspace / "claims.jsonl", source_ids))
    errors.extend(_validate_conflicts(workspace / "conflicts.jsonl"))
    return errors


def audit_generation_readiness(course_dir: Path) -> list[str]:
    """Lightweight content-form audit. Process artifacts are optional.

    LearnLoop courses do not require a .learnloop/ workspace. If one exists,
    we validate the knowledge state it contains. The main job of this audit is
    to catch mismatches between the chosen template and the actual module
    content (e.g., a Practice module with no exercises).
    """
    course_dir = course_dir.resolve()
    workspace = course_dir / ".learnloop"
    errors: list[str] = []

    if workspace.exists():
        errors.extend(validate_knowledge_state(course_dir))

    errors.extend(_audit_reference_modules(course_dir))
    errors.extend(_audit_learning_form_fit(course_dir))
    return errors


def validate_perspective_basis(blocks: list[Block], module_file: str) -> list[str]:
    errors: list[str] = []
    for block in _walk_blocks(blocks):
        if block.type == "exercise" and block.kind == "perspective":
            text = "\n".join(
                part
                for part in (block.perspective, block.tradeoffs, block.pitfalls)
                if part
            )
            if not _has_perspective_basis(text):
                errors.append(
                    f"{module_file}: perspective exercise must include basis or needs-human-review"
                )
    return errors


def _audit_reference_modules(course_dir: Path) -> list[str]:
    try:
        course = read_course(course_dir)
    except Exception:
        return []

    errors: list[str] = []
    for module in course.modules:
        path = course.root / module.file
        if not path.exists():
            continue
        try:
            frontmatter, _ = parse_module(path)
            module.template = frontmatter.get("template") or module.template
            template = select_template(course_dir, course, module)
        except Exception:
            continue
        if template.name != "reference":
            continue
        text = path.read_text(encoding="utf-8")
        if "|" not in text:
            errors.append(f"{module.file}: reference module should use tables or dense lookup structure")
        if len(text.splitlines()) < 60:
            errors.append(f"{module.file}: reference module is too short to justify the reference template")
    return errors


def _audit_learning_form_fit(course_dir: Path) -> list[str]:
    try:
        course = read_course(course_dir)
    except Exception:
        return []

    errors: list[str] = []
    for module in course.modules:
        path = course.root / module.file
        if not path.exists():
            continue
        try:
            frontmatter, blocks = parse_module(path)
            module.template = frontmatter.get("template") or module.template
            template = select_template(course_dir, course, module)
        except Exception:
            continue

        flat = _walk_blocks(blocks)
        if template.name == "practice":
            practice_blocks = [block for block in flat if block.type in {"exercise", "checkpoint"}]
            if not practice_blocks:
                errors.append(f"{module.file}: practice module must include exercise or checkpoint blocks")
            elif not any(block.answer or block.explanation for block in practice_blocks):
                errors.append(f"{module.file}: practice module should include answers or feedback")

        if template.name == "perspective" and not any(
            block.type == "exercise" and block.kind == "perspective" for block in flat
        ):
            errors.append(f"{module.file}: perspective module must include a perspective exercise")

    return errors


def _validate_claims(path: Path, source_ids: set[str] | None = None) -> list[str]:
    if not path.exists():
        return []

    errors: list[str] = []
    for idx, item in _read_jsonl(path, errors):
        for field in ("id", "claim", "module_id", "section_id", "status"):
            if field not in item:
                errors.append(f"{path.name}:{idx}: missing {field}")
        status = str(item.get("status", ""))
        if status and status not in CLAIM_STATUSES:
            errors.append(f"{path.name}:{idx}: unsupported status: {status}")
        if status == "verified" and not (item.get("source_id") or item.get("source")):
            errors.append(f"{path.name}:{idx}: verified claim requires source_id or source")
        source_id = str(item.get("source_id", "")).strip()
        if source_id and source_ids is not None and source_id not in source_ids:
            errors.append(f"{path.name}:{idx}: unknown source_id: {source_id}")
    return errors


def _validate_conflicts(path: Path) -> list[str]:
    if not path.exists():
        return []

    errors: list[str] = []
    for idx, item in _read_jsonl(path, errors):
        for field in ("id", "summary", "status"):
            if field not in item:
                errors.append(f"{path.name}:{idx}: missing {field}")
    return errors


def _read_jsonl(path: Path, errors: list[str]) -> list[tuple[int, dict[str, Any]]]:
    items: list[tuple[int, dict[str, Any]]] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{idx}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(item, dict):
            errors.append(f"{path.name}:{idx}: expected object")
            continue
        items.append((idx, item))
    return items


def _read_source_ids(path: Path) -> set[str] | None:
    if not path.exists():
        return None
    source_ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*-\s+id:\s*(.+?)\s*$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if value:
            source_ids.add(value)
    return source_ids


def _walk_blocks(blocks: list[Block]) -> list[Block]:
    out: list[Block] = []
    for block in blocks:
        out.append(block)
        if block.blocks:
            out.extend(_walk_blocks(block.blocks))
    return out


def _has_perspective_basis(text: str) -> bool:
    markers = ("依据：", "Basis:", "based on", "needs-human-review")
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)
