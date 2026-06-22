from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from typing import Any

from .model import Block, CourseDoc, LearnLoopError, ModuleDoc
from .parser import collect_block_types, collect_sections, inline, parse_markdown, parse_module, read_course
from .templates import select_template, template_root, validate_template_support


def render_blocks(blocks: list[Block], template: Any | None = None) -> str:
    out: list[str] = []
    for block in blocks:
        if block.type == "paragraph":
            out.append(f"<p>{block.text}</p>")
        elif block.type == "list":
            tag = "ol" if block.ordered else "ul"
            items = "".join(f"<li>{item}</li>" for item in (block.items or []))
            out.append(f"<{tag}>{items}</{tag}>")
        elif block.type == "code":
            lang = html.escape(block.language or "")
            code = html.escape(block.content or "")
            out.append(f'<pre><code class="language-{lang}">{code}</code></pre>')
        elif block.type == "callout":
            out.append(f'<div class="callout">{block.text}</div>')
        elif block.type == "table":
            headers = "".join(f"<th>{inline(cell)}</th>" for cell in (block.headers or []))
            rows = ""
            for row in (block.rows or []):
                cells = "".join(f"<td>{inline(cell)}</td>" for cell in row)
                rows += f"<tr>{cells}</tr>"
            out.append(f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>")
        elif block.type == "heading":
            out.append(f"<h1>{html.escape(block.title or '')}</h1>")
        elif block.type == "section":
            out.append(render_section(block, template))
        elif block.type == "exercise":
            out.append(render_exercise(block, template))
        elif block.type == "checkpoint":
            out.append(render_checkpoint(block, template))
        else:
            # Unknown blocks pass through as plain div with their type as class
            inner = render_blocks(block.blocks or [], template)
            out.append(f'<div class="block-{html.escape(block.type)}">{inner}</div>')
    return "\n".join(out)


def render_section(block: Block, template: Any | None = None) -> str:
    level = block.level or 2
    section_id = html.escape(block.id or "")
    title = html.escape(block.title or "")
    inner = render_blocks(block.blocks or [], template)
    ask_button = (
        f'<button class="ask-btn" data-ask-section="{section_id}" '
        f'data-ask-title="{title}">提问</button>'
    )

    if template and template.name == "reference":
        summary = _first_text_summary(block.blocks or [])
        summary_html = f'<div class="card-summary">{html.escape(summary)}</div>' if summary else ""
        return (
            f'<section class="card" data-section-id="{section_id}" data-section-title="{title}">\n'
            f'  <div class="card-header">\n'
            f'    <button class="card-toggle" type="button" aria-expanded="false" aria-label="展开/折叠">'
            f'<span aria-hidden="true">▶</span></button>\n'
            f'    <span class="card-title">{title}</span>\n'
            f'    {ask_button}\n'
            f'  </div>\n'
            f'  {summary_html}\n'
            f'  <div class="card-body"><div class="card-inner">\n{inner}\n  </div></div>\n'
            f'</section>'
        )

    heading = (
        f'<h{level} data-section-id="{section_id}" data-section-title="{title}">'
        f'{title} {ask_button}</h{level}>'
    )
    return f"<section>{heading}\n{inner}</section>"


def _first_text_summary(blocks: list[Block]) -> str:
    for block in blocks:
        if block.type == "paragraph" and block.text:
            text = block.text.replace("<code>", "").replace("</code>", "").replace("<strong>", "").replace("</strong>", "")
            text = text.strip()
            if len(text) > 120:
                text = text[:119] + "…"
            return text
        if block.blocks:
            summary = _first_text_summary(block.blocks)
            if summary:
                return summary
    return ""


def render_exercise(block: Block, template: Any | None = None) -> str:
    template_name = template.name if template else ""
    kind = block.kind or "open"

    if template_name == "case" and kind == "case":
        return render_case_exercise(block, template)

    if template_name == "practice":
        if kind == "choice":
            return render_choice_exercise(block, template)
        if kind == "fill":
            return render_fill_exercise(block, template)
        if kind == "bug":
            return render_bug_exercise(block, template)

    # Default / open exercise: show-answer toggle.
    task = render_blocks(block.blocks or [], template)
    answer_html = ""
    if block.answer:
        answer_body = render_blocks(parse_markdown(block.answer), template)
        answer_html = (
            f'<div class="exercise-answer" hidden>\n{answer_body}\n</div>'
        )
    has_answer = "true" if block.answer else "false"
    controls = (
        '<div class="exercise-controls">\n'
        '  <button class="exercise-toggle" type="button" aria-expanded="false">'
        '显示答案</button>\n'
        '  <label class="exercise-done">\n'
        '    <input type="checkbox"> 已完成\n'
        '  </label>\n'
        '</div>'
    )
    return (
        f'<div class="exercise" data-kind="open" data-has-answer="{has_answer}">\n'
        f'<div class="exercise-task">\n{task}\n</div>\n'
        f'{answer_html}\n'
        f'{controls}\n'
        f'</div>'
    )


def _render_task_without_choices(blocks: list[Block], template: Any | None) -> str:
    filtered = [b for b in blocks if not (b.type == "list" and b.items and _is_choice_list(b.items))]
    return render_blocks(filtered, template)


def _is_choice_list(items: list[str]) -> bool:
    from .parser import CHOICE_RE
    return all(CHOICE_RE.match(item) for item in items)


def render_choice_exercise(block: Block, template: Any | None) -> str:
    task = _render_task_without_choices(block.blocks or [], template)
    choices = block.choices or []
    correct = (block.answer or "").strip().upper()
    explanation_html = ""
    if block.answer:
        answer_md = block.answer
        if block.explanation:
            answer_md += f"\n\n{block.explanation}"
        answer_body = render_blocks(parse_markdown(answer_md), template)
        explanation_html = f'<div class="exercise-answer" hidden>\n{answer_body}\n</div>'
    radios = "\n".join(
        f'<label class="choice-option" data-choice="{chr(65 + i)}">'
        f'<input type="radio" name="choice" value="{chr(65 + i)}"> '
        f'<span>{html.escape(text)}</span></label>'
        for i, text in enumerate(choices)
    )
    feedback = '<div class="exercise-feedback" role="status" hidden></div>'
    controls = (
        '<div class="exercise-controls">\n'
        '  <button class="exercise-check" type="button">检查</button>\n'
        '  <button class="exercise-toggle" type="button" aria-expanded="false" hidden>显示答案</button>\n'
        '  <label class="exercise-done">\n'
        '    <input type="checkbox"> 已完成\n'
        '  </label>\n'
        '</div>'
    )
    return (
        f'<div class="exercise" data-kind="choice" data-correct="{html.escape(correct)}">\n'
        f'<div class="exercise-task">\n{task}\n</div>\n'
        f'<form class="exercise-choices">\n{radios}\n</form>\n'
        f'{feedback}\n'
        f'{explanation_html}\n'
        f'{controls}\n'
        f'</div>'
    )


def render_fill_exercise(block: Block, template: Any | None) -> str:
    task = render_blocks(block.blocks or [], template)
    answers = block.answers or []
    data_answers = html.escape(";".join(answers))
    task = _replace_blanks_with_inputs(task, answers)
    explanation_html = ""
    if block.answer:
        answer_md = block.answer
        if block.explanation:
            answer_md += f"\n\n{block.explanation}"
        answer_body = render_blocks(parse_markdown(answer_md), template)
        explanation_html = f'<div class="exercise-answer" hidden>\n{answer_body}\n</div>'
    feedback = '<div class="exercise-feedback" role="status" hidden></div>'
    controls = (
        '<div class="exercise-controls">\n'
        '  <button class="exercise-check" type="button">检查</button>\n'
        '  <button class="exercise-toggle" type="button" aria-expanded="false" hidden>显示答案</button>\n'
        '  <label class="exercise-done">\n'
        '    <input type="checkbox"> 已完成\n'
        '  </label>\n'
        '</div>'
    )
    return (
        f'<div class="exercise" data-kind="fill" data-answers="{data_answers}">\n'
        f'<div class="exercise-task">\n{task}\n</div>\n'
        f'{feedback}\n'
        f'{explanation_html}\n'
        f'{controls}\n'
        f'</div>'
    )


def _replace_blanks_with_inputs(task_html: str, answers: list[str]) -> str:
    blank_re = re.compile(r"_{8,}")
    idx = [0]

    def replacer(match: re.Match[str]) -> str:
        answer = html.escape(answers[idx[0]]) if idx[0] < len(answers) else ""
        idx[0] += 1
        return f'<input type="text" class="ll-blank" data-answer="{answer}" autocomplete="off">'

    return blank_re.sub(replacer, task_html)


def render_bug_exercise(block: Block, template: Any | None) -> str:
    task = render_blocks(block.blocks or [], template)
    buggy = block.buggy_lines or []
    data_bugs = html.escape(",".join(str(n) for n in buggy))
    task = _decorate_buggy_lines(task, buggy)
    explanation_html = ""
    if block.answer:
        answer_body = render_blocks(parse_markdown(block.answer), template)
        explanation_html = f'<div class="exercise-answer" hidden>\n{answer_body}\n</div>'
    feedback = '<div class="exercise-feedback" role="status" hidden></div>'
    controls = (
        '<div class="exercise-controls">\n'
        '  <button class="exercise-check" type="button">检查</button>\n'
        '  <button class="exercise-toggle" type="button" aria-expanded="false" hidden>显示答案</button>\n'
        '  <label class="exercise-done">\n'
        '    <input type="checkbox"> 已完成\n'
        '  </label>\n'
        '</div>'
    )
    return (
        f'<div class="exercise" data-kind="bug" data-buggy-lines="{data_bugs}">\n'
        f'<div class="exercise-task">\n{task}\n</div>\n'
        f'{feedback}\n'
        f'{explanation_html}\n'
        f'{controls}\n'
        f'</div>'
    )


def _decorate_buggy_lines(task_html: str, buggy_lines: list[int]) -> str:
    # Operate on the textual content of <pre><code ...>...</code></pre> blocks.
    pre_re = re.compile(r"(<pre><code[^>]*>)(.*?)(</code></pre>)", re.S)

    def repl_pre(match: re.Match[str]) -> str:
        open_tag, content, close_tag = match.groups()
        lines = content.split("\n")
        out: list[str] = [open_tag]
        for line_no, raw_line in enumerate(lines, start=1):
            clean = re.sub(r"\s*<!--\s*bug\s*-->\s*$", "", raw_line)
            cls = "buggy-line" if line_no in buggy_lines else ""
            checkbox = f'<input type="checkbox" class="bug-checkbox" data-line="{line_no}">'
            out.append(f'<div class="code-line {cls}" data-line="{line_no}">{checkbox}<span>{clean}</span></div>')
        out.append(close_tag)
        return "\n".join(out)

    return pre_re.sub(repl_pre, task_html)


def render_case_exercise(block: Block, template: Any | None) -> str:
    task = render_blocks(block.blocks or [], template)
    perspective = render_blocks(parse_markdown(block.perspective or ""), template) if block.perspective else ""
    tradeoffs = render_blocks(parse_markdown(block.tradeoffs or ""), template) if block.tradeoffs else ""
    pitfalls = render_blocks(parse_markdown(block.pitfalls or ""), template) if block.pitfalls else ""
    hidden_sections = ""
    if perspective or tradeoffs or pitfalls:
        parts = []
        if perspective:
            parts.append(f'<section class="judgment-section perspective" hidden><h4>作者视角</h4>\n{perspective}\n</section>')
        if tradeoffs:
            parts.append(f'<section class="judgment-section tradeoffs" hidden><h4>取舍与 trade-offs</h4>\n{tradeoffs}\n</section>')
        if pitfalls:
            parts.append(f'<section class="judgment-section pitfalls" hidden><h4>常见误区</h4>\n{pitfalls}\n</section>')
        joined_parts = "\n".join(parts)
        hidden_sections = f'<div class="judgment-reveal" hidden>\n{joined_parts}\n</div>'
    return (
        f'<div class="exercise" data-kind="case">\n'
        f'<div class="exercise-task judgment-task">\n{task}\n</div>\n'
        f'<textarea class="judgment-reasoning" placeholder="写下你的判断和顾虑…"></textarea>\n'
        f'{hidden_sections}\n'
        f'<div class="exercise-controls">\n'
        '  <button class="exercise-compare" type="button">对比作者视角</button>\n'
        '  <label class="exercise-done">\n'
        '    <input type="checkbox"> 已完成\n'
        '  </label>\n'
        '</div>\n'
        f'</div>'
    )


def render_checkpoint(block: Block, template: Any | None = None) -> str:
    task = render_blocks(block.blocks or [], template)
    answer_html = ""
    if block.answer:
        answer_body = render_blocks(parse_markdown(block.answer), template)
        answer_html = (
            f'<div class="checkpoint-answer" hidden>\n{answer_body}\n</div>'
        )
    has_answer = "true" if block.answer else "false"
    controls = (
        '<div class="checkpoint-controls">\n'
        '  <button class="checkpoint-toggle" type="button" aria-expanded="false">'
        '显示提示</button>\n'
        '</div>'
    )
    return (
        f'<div class="checkpoint" data-has-answer="{has_answer}">\n'
        f'<div class="checkpoint-task">\n{task}\n</div>\n'
        f'{answer_html}\n'
        f'{controls}\n'
        f'</div>'
    )


def render_module_page(
    course: CourseDoc,
    module: ModuleDoc,
    sections: list[Block],
    template: Any,
) -> str:
    content = render_blocks(sections, template)
    template_label = template.name
    content = f"""<nav class="top-nav"><a href="index.html">学习路径</a><span>{html.escape(module.id)}</span><span class="top-nav-template">{html.escape(template_label)}</span></nav>
<article class="lesson" data-course-id="{html.escape(course.id)}" data-module-id="{html.escape(module.id)}">
  <header class="lesson-header">
    <p class="eyebrow">{html.escape(course.title)}</p>
    <h1>{html.escape(module.title)}</h1>
    <p class="lede">{html.escape(module.summary)}</p>
  </header>
  {content}
  {module_nav_links(course, module)}
</article>
{QUESTION_UI}"""

    page = template.template_html
    page = page.replace("{{ page_title }}", html.escape(f"{module.title} | LearnLoop"))
    page = page.replace("{{ course_title }}", html.escape(course.title))
    page = page.replace("{{ content }}", content)
    page = page.replace("{{ css_href }}", f"assets/{template.name}/style.css")
    page = page.replace("{{ js_src }}", f"assets/{template.name}/runtime.js")
    return page


def module_nav_links(course: CourseDoc, module: ModuleDoc) -> str:
    idx = next((i for i, m in enumerate(course.modules) if m.id == module.id), -1)
    previous_module = course.modules[idx - 1] if idx > 0 else None
    next_module = course.modules[idx + 1] if idx + 1 < len(course.modules) else None
    prev_link = (
        f'<a href="{html.escape(module_output_name(previous_module))}">上一节</a>'
        if previous_module
        else "<span></span>"
    )
    next_link = (
        f'<a href="{html.escape(module_output_name(next_module))}">下一节</a>'
        if next_module
        else "<span></span>"
    )
    return f'<footer class="next-prev">{prev_link}{next_link}</footer>'


def render_index(course: CourseDoc, template: Any) -> str:
    cards = []
    for idx, module in enumerate(course.modules, start=1):
        cards.append(
            f"""<a class="module-card" href="{html.escape(module_output_name(module))}">
  <span class="module-number">{idx:02d}</span>
  <span class="module-text"><strong>{html.escape(module.title)}</strong><em>{html.escape(module.summary)}</em></span>
</a>"""
        )
    content = f"""<header class="hero">
  <p class="eyebrow">LearnLoop 课程</p>
  <h1>{html.escape(course.title)}</h1>
  <p class="lede">{html.escape(course.subtitle)}</p>
</header>
<section class="intro">
  <p>一次学习一个模块。当某个概念变得模糊时，直接在对应章节旁提问。LearnLoop 会把问题连同它所在的课程上下文一起保存，方便后续让 Agent 回答或改进材料。</p>
</section>
<nav class="modules">{''.join(cards)}</nav>"""

    page = template.template_html
    page = page.replace("{{ page_title }}", html.escape(f"{course.title} | LearnLoop"))
    page = page.replace("{{ course_title }}", html.escape(course.title))
    page = page.replace("{{ content }}", content)
    page = page.replace("{{ css_href }}", f"assets/{template.name}/style.css")
    page = page.replace("{{ js_src }}", f"assets/{template.name}/runtime.js")
    return page


def build_course(course_dir: Path) -> Path:
    course = read_course(course_dir)
    dist = course.root / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    (dist / "assets").mkdir(parents=True)
    base_css = template_root() / "base.css"
    if base_css.exists():
        shutil.copy(base_css, dist / "assets" / "base.css")
    base_js = template_root() / "runtime-base.js"
    if base_js.exists():
        shutil.copy(base_js, dist / "assets" / "runtime-base.js")

    index_template = select_template(course_dir, course)
    (dist / "index.html").write_text(
        render_index(course, index_template), encoding="utf-8"
    )
    _copy_template_assets(dist, index_template)

    for module in course.modules:
        source = course.root / module.file
        frontmatter, blocks = parse_module(source)
        effective_module = ModuleDoc(
            id=module.id,
            title=module.title,
            file=module.file,
            summary=frontmatter.get("summary", module.summary),
            template=frontmatter.get("template") or module.template,
        )
        template = select_template(course_dir, course, effective_module)
        block_types = collect_block_types(blocks)
        errors = validate_template_support(template, block_types)
        if errors:
            raise LearnLoopError(errors[0])

        _copy_template_assets(dist, template)
        page = render_module_page(course, effective_module, blocks, template)
        (dist / module_output_name(effective_module)).write_text(page, encoding="utf-8")

    return dist


def _copy_template_assets(dist: Path, template: Any) -> None:
    assets_dir = dist / "assets" / template.name
    if assets_dir.exists():
        return
    assets_dir.mkdir(parents=True)
    shutil.copy(template.css_path, assets_dir / template.css_path.name)
    shutil.copy(template.js_path, assets_dir / template.js_path.name)


def module_output_name(module: ModuleDoc) -> str:
    return f"{module.id}.html"


def validate_course(course_dir: Path) -> list[str]:
    errors: list[str] = []
    try:
        course = read_course(course_dir)
    except LearnLoopError as exc:
        return [str(exc)]

    seen_sections: set[str] = set()
    seen_modules: set[str] = set()

    for module in course.modules:
        if module.id in seen_modules:
            errors.append(f"Duplicate module id: {module.id}")
        seen_modules.add(module.id)

        path = course.root / module.file
        if not path.exists():
            errors.append(f"Missing module file: {module.file}")
            continue

        try:
            frontmatter, blocks = parse_module(path)
        except LearnLoopError as exc:
            errors.append(f"Error parsing {module.file}: {exc}")
            continue

        effective_module = ModuleDoc(
            id=module.id,
            title=module.title,
            file=module.file,
            summary=frontmatter.get("summary", module.summary),
            template=frontmatter.get("template") or module.template,
        )

        try:
            template = select_template(course_dir, course, effective_module)
        except LearnLoopError as exc:
            errors.append(f"Template error for {module.file}: {exc}")
            continue

        block_types = collect_block_types(blocks)
        errors.extend(
            f"{module.file}: {error}" for error in validate_template_support(template, block_types)
        )

        sections = collect_sections(blocks)
        if not sections:
            errors.append(f"Module has no question sections: {module.file}")
        for section in sections:
            if section.id in seen_sections:
                errors.append(f"Duplicate section id: {section.id}")
            seen_sections.add(section.id)

    questions = course.root / "questions.jsonl"
    if questions.exists():
        for idx, line in enumerate(
            questions.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"questions.jsonl:{idx}: invalid JSON: {exc.msg}")
                continue
            for field in (
                "id",
                "timestamp",
                "course_id",
                "module_id",
                "section_id",
                "question",
                "status",
            ):
                if field not in item:
                    errors.append(f"questions.jsonl:{idx}: missing {field}")

    return errors


QUESTION_UI = """<template id="ask-template">
  <form class="ask-form">
    <textarea name="question" placeholder="你对这一节有什么疑问？"></textarea>
    <div class="ask-actions">
      <button type="button" data-cancel>取消</button>
      <button type="submit">保存问题</button>
    </div>
    <p class="ask-status" role="status"></p>
  </form>
</template>
<button class="question-fab" data-open-drawer>问题 <span id="question-count">0</span></button>
<aside class="question-drawer" id="question-drawer" aria-hidden="true">
  <header><h2>本模块问题</h2><button data-close-drawer>关闭</button></header>
  <div id="question-list" class="question-list"></div>
  <footer>让 Agent 读取 <code>questions.jsonl</code>，或运行 <code>learnloop context</code>。</footer>
</aside>"""
