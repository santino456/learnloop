from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml

from .model import CourseDoc, LearnLoopError, ModuleDoc


@dataclass
class Template:
    name: str
    manifest: dict[str, Any]
    template_html: str
    css_path: Path
    js_path: Path


def template_root() -> Path:
    return Path(__file__).resolve().parent / "assets" / "templates"


def list_templates(root: Path | None = None) -> list[Template]:
    root = root or template_root()
    templates: list[Template] = []
    if not root.exists():
        return templates
    for path in sorted(root.iterdir()):
        if path.is_dir() and (path / "manifest.yaml").exists():
            templates.append(load_template(path.name, root))
    return templates


def load_template(name: str, root: Path | None = None) -> Template:
    root = root or template_root()
    path = root / name
    manifest_file = path / "manifest.yaml"
    if not manifest_file.exists():
        raise LearnLoopError(f"Template not found: {name}")

    manifest = parse_simple_yaml(manifest_file.read_text(encoding="utf-8"))
    assets = manifest.get("assets", {})
    css_path = path / str(assets.get("css", "style.css"))
    js_path = path / str(assets.get("js", "runtime.js"))
    template_html_path = path / "template.html"
    if not template_html_path.exists():
        raise LearnLoopError(f"Template {name} is missing template.html")

    return Template(
        name=name,
        manifest=manifest,
        template_html=template_html_path.read_text(encoding="utf-8"),
        css_path=css_path,
        js_path=js_path,
    )


def select_template(
    course_dir: Path,
    course: CourseDoc,
    module: ModuleDoc | None = None,
    root: Path | None = None,
) -> Template:
    root = root or template_root()
    name: str | None = None
    if module and module.template:
        name = module.template
    elif course.template:
        name = course.template

    if not name:
        # Default to tutorial if available, otherwise the first installed template.
        if (root / "tutorial").exists():
            name = "tutorial"
        elif root.exists():
            dirs = [p for p in root.iterdir() if p.is_dir()]
            if dirs:
                name = dirs[0].name

    if not name:
        raise LearnLoopError("No templates installed")

    return load_template(name, root)


def validate_template_support(template: Template, blocks_used: set[str]) -> list[str]:
    supported: set[str] = set(template.manifest.get("supports", {}).get("blocks", []))
    errors: list[str] = []
    for block_type in sorted(blocks_used - supported):
        errors.append(
            f"Template '{template.name}' does not support block type: {block_type}"
        )
    return errors


def parse_simple_yaml(text: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        raise LearnLoopError(f"Invalid template manifest: {exc}") from exc
    if not isinstance(data, dict):
        raise LearnLoopError("Template manifest must be a mapping")
    return data

