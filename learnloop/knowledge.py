from __future__ import annotations

import json
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
    errors.extend(_validate_claims(workspace / "claims.jsonl"))
    errors.extend(_validate_conflicts(workspace / "conflicts.jsonl"))
    return errors


def audit_generation_readiness(course_dir: Path) -> list[str]:
    """Check whether an agent-generated course has enough process evidence.

    This is intentionally lightweight. It catches the common failure mode where
    an agent jumps straight to a long module draft without source inventory,
    architecture decisions, or evidence packs.
    """
    course_dir = course_dir.resolve()
    workspace = course_dir / ".learnloop"
    errors: list[str] = []

    if not workspace.exists():
        return ["missing .learnloop workspace for generated course"]

    source_inventory = workspace / "source_inventory.yaml"
    if not source_inventory.exists():
        errors.append("missing .learnloop/source_inventory.yaml")
    elif "- id:" not in source_inventory.read_text(encoding="utf-8"):
        errors.append("source_inventory.yaml must list at least one source with an id")

    architecture = workspace / "course_architecture.md"
    if not architecture.exists():
        errors.append("missing .learnloop/course_architecture.md")
    else:
        text = architecture.read_text(encoding="utf-8").lower()
        for phrase in ("learner goal", "content form decisions", "module plan"):
            if phrase not in text:
                errors.append(f"course_architecture.md missing section: {phrase}")

    chapter_briefs = workspace / "chapter_briefs"
    if not any(chapter_briefs.glob("*.md")):
        errors.append("missing chapter brief in .learnloop/chapter_briefs/")

    evidence_packs = workspace / "evidence_packs"
    packs = list(evidence_packs.glob("*.md"))
    if not packs:
        errors.append("missing evidence pack in .learnloop/evidence_packs/")
    for pack in packs:
        text = pack.read_text(encoding="utf-8").lower()
        if "## sources" not in text or "## evidence" not in text:
            errors.append(f"{pack.relative_to(course_dir)} must include Sources and Evidence sections")

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


def _validate_claims(path: Path) -> list[str]:
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
