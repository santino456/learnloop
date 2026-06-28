from __future__ import annotations

import re
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Iterator

import yaml

from .model import CourseDoc, LearnLoopError

_LANG_CTX: ContextVar[str] = ContextVar("ll_lang", default="en")

_translations: dict[str, dict[str, Any]] = {}


def i18n_dir() -> Path:
    return Path(__file__).resolve().parent / "assets" / "i18n"


def load_translation(lang: str) -> dict[str, Any]:
    """Load a translation file, falling back to English if missing."""
    if lang in _translations:
        return _translations[lang]

    path = i18n_dir() / f"{lang}.yaml"
    if not path.exists():
        if lang == "en":
            raise LearnLoopError(f"Missing base i18n file: {path}")
        return load_translation("en")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise LearnLoopError(f"Invalid i18n file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise LearnLoopError(f"i18n file {path} must be a mapping")

    _translations[lang] = data
    return data


def t(key: str, lang: str | None = None) -> str:
    """Return a translated string for the given dot-separated key."""
    lang = lang or _LANG_CTX.get()
    data = load_translation(lang)
    value: Any = data
    for part in key.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return t(key, "en") if lang != "en" else key
    if isinstance(value, str):
        return value
    return key


@contextmanager
def use_language(lang: str) -> Iterator[None]:
    """Set the active language for the current render context."""
    token = _LANG_CTX.set(lang)
    try:
        yield
    finally:
        _LANG_CTX.reset(token)


def current_language() -> str:
    """Return the active language in the current context."""
    return _LANG_CTX.get()


_CJK_RE = re.compile(
    r"[一-鿿぀-ゟ゠-ヿ가-힯]"
)


_LATIN_RE = re.compile(r"[A-Za-z]")


def detect_language(text: str, sample_chars: int = 1000) -> str:
    """Detect 'zh' or 'en' from the first sample_chars of text."""
    sample = text[:sample_chars]
    if not sample:
        return "en"
    cjk = len(_CJK_RE.findall(sample))
    latin = len(_LATIN_RE.findall(sample))
    meaningful = cjk + latin
    if meaningful == 0:
        return "en"
    ratio = cjk / meaningful
    return "zh" if ratio > 0.30 else "en"


def resolve_course_language(course: CourseDoc) -> str:
    """Return the effective language for a course, using explicit lang or auto-detection."""
    explicit = getattr(course, "lang", None)
    if explicit and explicit != "auto":
        return explicit

    if course.modules:
        first_module = course.root / course.modules[0].file
        if first_module.exists():
            return detect_language(first_module.read_text(encoding="utf-8"))

    text = "\n".join(
        [course.title, course.subtitle, course.audience]
        + [f"{m.title} {m.summary}" for m in course.modules]
    )
    return detect_language(text)
