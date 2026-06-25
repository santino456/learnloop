from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .model import LearnLoopError


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".md", ".markdown", ".txt"}
CAPTION_RE = re.compile(
    r"^\s*((?:fig(?:ure)?\.?|图|table|表)\s*[\dIVXLC]+[a-zA-Z]?)\s*[:.\-：]?\s*(.*)",
    re.I,
)


@dataclass
class IngestResult:
    source: Path
    material_dir: Path
    material_json: Path
    chunks_jsonl: Path
    figures_json: Path | None = None
    figures_md: Path | None = None
    figures: int = 0
    chunks: int = 0


def ingest_material(
    source: Path,
    course_dir: Path,
    *,
    backend: str = "auto",
    overwrite: bool = False,
) -> IngestResult:
    """Convert a raw source file into a LearnLoop material pack."""
    source = source.expanduser().resolve()
    course_dir = course_dir.expanduser().resolve()
    if not source.exists():
        raise LearnLoopError(f"Source file does not exist: {source}")
    if not course_dir.exists():
        raise LearnLoopError(f"Course directory does not exist: {course_dir}")

    ext = source.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise LearnLoopError(
            f"Unsupported source type: {ext or '(none)'}. "
            "Supported: PDF, DOCX, PPTX, Markdown, text."
        )

    material_dir = course_dir / ".learnloop" / "materials" / _safe_stem(source)
    if material_dir.exists() and overwrite:
        shutil.rmtree(material_dir)
    material_dir.mkdir(parents=True, exist_ok=True)
    (course_dir / "assets").mkdir(exist_ok=True)

    if ext == ".pdf":
        chunks, figures, metadata = _ingest_pdf(source, course_dir, material_dir, backend)
        selected_backend = metadata["backend"]
    elif ext == ".docx":
        chunks, figures, metadata = _ingest_docx(source, material_dir, backend)
        selected_backend = metadata["backend"]
    elif ext == ".pptx":
        chunks, figures, metadata = _ingest_pptx(source, material_dir, backend)
        selected_backend = metadata["backend"]
    else:
        chunks, figures, metadata = _ingest_text(source, material_dir, backend)
        selected_backend = metadata["backend"]

    chunks_jsonl = material_dir / "chunks.jsonl"
    _write_jsonl(chunks_jsonl, chunks)

    figures_json: Path | None = None
    figures_md: Path | None = None
    if figures:
        figures_json = material_dir / "figures.json"
        figures_json.write_text(
            json.dumps({"figures": figures}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        figures_md = material_dir / "figures.md"
        figures_md.write_text(_figures_markdown(figures), encoding="utf-8")

    material = {
        "schema_version": 1,
        "source": {
            "path": str(source),
            "filename": source.name,
            "type": ext.lstrip("."),
        },
        "backend": selected_backend,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "outputs": {
            "chunks_jsonl": "chunks.jsonl",
            "figures_json": "figures.json" if figures_json else None,
            "figures_md": "figures.md" if figures_md else None,
        },
        "stats": {
            "chunks": len(chunks),
            "figures": len(figures),
        },
        "metadata": metadata,
    }
    material_json = material_dir / "material.json"
    material_json.write_text(
        json.dumps(material, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _register_source(course_dir, source, material_dir, material["stats"])

    return IngestResult(
        source=source,
        material_dir=material_dir,
        material_json=material_json,
        chunks_jsonl=chunks_jsonl,
        figures_json=figures_json,
        figures_md=figures_md,
        figures=len(figures),
        chunks=len(chunks),
    )


def _ingest_pdf(
    source: Path, course_dir: Path, material_dir: Path, backend: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if backend not in {"auto", "pymupdf"}:
        raise LearnLoopError(
            f"PDF backend '{backend}' is not available in the base install. "
            "Use 'pymupdf' or install an advanced extractor outside LearnLoop."
        )
    try:
        import fitz  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise LearnLoopError(
            "PDF ingest requires PyMuPDF. Install it with: python3 -m pip install pymupdf"
        ) from exc

    doc = fitz.open(source)
    chunks: list[dict[str, Any]] = []
    figures: list[dict[str, Any]] = []
    source_id = _safe_stem(source)
    assets_dir = course_dir / "assets"

    for page_index, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        for chunk_index, paragraph in enumerate(_split_paragraphs(text), start=1):
            chunks.append(
                {
                    "id": f"{source_id}:p{page_index}:c{chunk_index}",
                    "source": source.name,
                    "page": page_index,
                    "kind": "text",
                    "text": paragraph,
                }
            )

        caption_blocks = _caption_blocks(page)
        visual_rects = _visual_rects(page)
        for figure_index, caption in enumerate(caption_blocks, start=1):
            rect = _infer_figure_rect(page.rect, caption["bbox"], visual_rects)
            if rect is None:
                continue
            global_index = len(figures) + 1
            asset_name = f"{source_id}-fig-{global_index}.png"
            asset_path = assets_dir / asset_name
            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                clip=rect,
                alpha=False,
            )
            pix.save(asset_path)
            figures.append(
                {
                    "id": f"{source_id}:fig-{global_index}",
                    "source": source.name,
                    "page": page_index,
                    "label": caption["label"],
                    "caption": caption["text"],
                    "asset": f"assets/{asset_name}",
                    "bbox": [round(value, 2) for value in rect],
                    "method": "caption-nearby-crop",
                }
            )

    metadata = {
        "backend": "pymupdf",
        "pages": doc.page_count,
        "title": doc.metadata.get("title") or "",
        "author": doc.metadata.get("author") or "",
        "figure_extraction": "caption-nearby-crop",
    }
    doc.close()
    return chunks, figures, metadata


def _ingest_docx(
    source: Path, _material_dir: Path, backend: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if backend not in {"auto", "python-docx"}:
        raise LearnLoopError("DOCX ingest currently supports backend 'python-docx'.")
    try:
        import docx  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise LearnLoopError(
            "DOCX ingest requires python-docx. Install it with: python3 -m pip install python-docx"
        ) from exc

    document = docx.Document(str(source))
    source_id = _safe_stem(source)
    chunks = []
    for index, paragraph in enumerate(document.paragraphs, start=1):
        text = paragraph.text.strip()
        if not text:
            continue
        style = paragraph.style.name if paragraph.style else ""
        chunks.append(
            {
                "id": f"{source_id}:p{index}",
                "source": source.name,
                "kind": "heading" if style.lower().startswith("heading") else "text",
                "style": style,
                "text": text,
            }
        )
    return chunks, [], {"backend": "python-docx", "paragraphs": len(chunks)}


def _ingest_pptx(
    source: Path, _material_dir: Path, backend: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if backend not in {"auto", "python-pptx"}:
        raise LearnLoopError("PPTX ingest currently supports backend 'python-pptx'.")
    try:
        import pptx  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise LearnLoopError(
            "PPTX ingest requires python-pptx. Install it with: python3 -m pip install python-pptx"
        ) from exc

    presentation = pptx.Presentation(str(source))
    source_id = _safe_stem(source)
    chunks = []
    for slide_index, slide in enumerate(presentation.slides, start=1):
        texts: list[str] = []
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text = shape.text.strip()
                if text:
                    texts.append(text)
        if texts:
            chunks.append(
                {
                    "id": f"{source_id}:s{slide_index}",
                    "source": source.name,
                    "slide": slide_index,
                    "kind": "slide",
                    "text": "\n".join(texts),
                }
            )
    return chunks, [], {"backend": "python-pptx", "slides": len(presentation.slides)}


def _ingest_text(
    source: Path, _material_dir: Path, backend: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if backend not in {"auto", "plain-text"}:
        raise LearnLoopError("Text ingest currently supports backend 'plain-text'.")
    source_id = _safe_stem(source)
    text = source.read_text(encoding="utf-8")
    chunks = [
        {
            "id": f"{source_id}:c{index}",
            "source": source.name,
            "kind": "text",
            "text": paragraph,
        }
        for index, paragraph in enumerate(_split_paragraphs(text), start=1)
    ]
    return chunks, [], {"backend": "plain-text"}


def _caption_blocks(page: Any) -> list[dict[str, Any]]:
    blocks = []
    for block in page.get_text("blocks"):
        if len(block) < 5:
            continue
        text = _clean_text(block[4])
        match = CAPTION_RE.match(text)
        if not match:
            continue
        blocks.append(
            {
                "bbox": page.rect.__class__(block[:4]),
                "label": match.group(1).strip(),
                "text": text,
            }
        )
    return blocks


def _visual_rects(page: Any) -> list[Any]:
    rects = []
    for image in page.get_images(full=True):
        xref = image[0]
        try:
            rects.extend(page.get_image_rects(xref))
        except Exception:
            continue
    try:
        for drawing in page.get_drawings():
            rect = drawing.get("rect")
            if rect is not None and rect.get_area() >= 100:
                rects.append(rect)
    except Exception:
        pass
    return rects


def _infer_figure_rect(page_rect: Any, caption_rect: Any, visual_rects: list[Any]) -> Any | None:
    margin = 12
    max_gap = page_rect.height * 0.45
    candidates = []
    for rect in visual_rects:
        if rect.y1 <= caption_rect.y0 + 4 and rect.y1 >= caption_rect.y0 - max_gap:
            horizontal_overlap = min(rect.x1, caption_rect.x1) - max(rect.x0, caption_rect.x0)
            if horizontal_overlap > -page_rect.width * 0.3:
                candidates.append(rect)

    if candidates:
        combined = candidates[0]
        for rect in candidates[1:]:
            combined |= rect
        return _clip_rect(
            page_rect.__class__(
                combined.x0 - margin,
                combined.y0 - margin,
                combined.x1 + margin,
                combined.y1 + max(4, caption_rect.y0 - combined.y1 - 2),
            ),
            page_rect,
        )

    top = max(page_rect.y0, caption_rect.y0 - page_rect.height * 0.32)
    if caption_rect.y0 - top < 48:
        return None
    return _clip_rect(
        page_rect.__class__(
            page_rect.x0 + margin,
            top,
            page_rect.x1 - margin,
            caption_rect.y0 - 4,
        ),
        page_rect,
    )


def _clip_rect(rect: Any, page_rect: Any) -> Any:
    return rect & page_rect


def _split_paragraphs(text: str) -> list[str]:
    paragraphs = []
    current: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if current:
                paragraphs.append(_clean_text(" ".join(current)))
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append(_clean_text(" ".join(current)))
    return [paragraph for paragraph in paragraphs if paragraph]


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _safe_stem(path: Path) -> str:
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", path.stem).strip("-").lower()
    return stem or "material"


def _register_source(
    course_dir: Path, source: Path, material_dir: Path, stats: dict[str, Any]
) -> None:
    workspace = course_dir / ".learnloop"
    workspace.mkdir(exist_ok=True)
    inventory = workspace / "source_inventory.yaml"
    source_id = _safe_stem(source)
    existing = inventory.read_text(encoding="utf-8") if inventory.exists() else ""
    if re.search(rf"^\s*-\s+id:\s*['\"]?{re.escape(source_id)}['\"]?\s*$", existing, re.M):
        return

    if not existing.strip():
        existing = "sources:\n"
    elif not existing.endswith("\n"):
        existing += "\n"
    if "sources:" not in existing:
        existing = "sources:\n" + existing

    try:
        raw_path = source.relative_to(course_dir).as_posix()
    except ValueError:
        raw_path = str(source)
    try:
        material_path = (material_dir / "material.json").relative_to(course_dir).as_posix()
    except ValueError:
        material_path = str(material_dir / "material.json")

    entry = (
        f"  - id: {source_id}\n"
        "    type: local-material\n"
        f"    title: {json.dumps(source.name, ensure_ascii=False)}\n"
        f"    path: {json.dumps(raw_path, ensure_ascii=False)}\n"
        "    status: ingested\n"
        f"    material: {json.dumps(material_path, ensure_ascii=False)}\n"
        f"    chunks: {int(stats.get('chunks', 0))}\n"
        f"    figures: {int(stats.get('figures', 0))}\n"
    )
    inventory.write_text(existing + entry, encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _figures_markdown(figures: list[dict[str, Any]]) -> str:
    parts = ["# Extracted Figures\n\n"]
    for figure in figures:
        caption = figure.get("caption", "")
        label = figure.get("label", "Figure")
        asset = figure["asset"]
        alt = f"{label} from {figure['source']}"
        parts.append(
            "::: figure\n"
            f"src: {asset}\n"
            f"alt: {alt}\n"
            f"caption: {caption}\n"
            f"source: 本地 {figure['source']} p.{figure['page']}\n"
            ":::\n\n"
        )
    return "".join(parts)
