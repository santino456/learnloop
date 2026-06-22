from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .model import Block


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
