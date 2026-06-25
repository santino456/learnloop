# Changelog

## 0.1.0 - Unreleased

- Add local course library service with `learnloop start`, `status`, and `stop`.
- Serve multiple courses from one local port under `/course/<course_id>/`.
- Add course-level question APIs and generated page configuration.
- Add template-capable Markdown/YAML course rendering.
- Add LearnLoop skill and lightweight course generation audit checks.
- Add course quality, content-form, evidence, and release documentation.
- Add GitHub issue and pull request templates for open-source use.
- Simplify course generation workflow: `.learnloop/` workspace is now optional; `init` creates only essential files; `audit` no longer requires source inventory, chapter briefs, or evidence packs. Quality checks focus on content-form fit.
- Add `learnloop ingest` for PDF/DOCX/PPTX/Markdown/text material packs, with PDF captioned-figure extraction into course assets.
- Harden local question handling, context generation, malformed course errors, and interactive exercise validation.
