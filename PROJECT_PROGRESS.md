# LearnLoop — Project Progress

## Current status

UI refinements are being driven by screenshot feedback. The course homepage and module pages now share a single, consistent type scale and spacing system across all four templates (`tutorial`, `reference`, `practice`, `perspective`).

## Completed work

- **Unified warm-paper theme**
  - Rewrote `templates/base.css` with warm paper/cream palette (`#f7f2e8` background, brown accents).
  - Removed Google Fonts; switched to system fonts optimized for Chinese (`PingFang SC`, `Microsoft YaHei`, `Noto Serif SC` fallback for headings).
  - All 4 templates now load `assets/base.css` plus a small template-specific override.

- **Template / learning-mode labels**
  - Each page shows a consistent English label in the top nav: `TUTORIAL` / `REFERENCE` / `PRACTICE` / `PERSPECTIVE`.
  - The module roadmap on the index page also shows the same scenario label per card.
  - Removed the reference-only sticky header; all templates use the same label component.

- **Compact homepage**
  - Removed the large usage-instruction callout from the index page.
  - Tightened hero spacing and reduced the title and subtitle sizes.
  - Module cards are smaller and denser.

- **Unified typography across templates**
  - Removed per-template overrides for `h1`, headings, `.lede`, body text, page width, and header spacing.
  - Rebalanced the shared type scale: body 17px/1.7, `h1` max 42px, `h2` max 26px, `.lede` 17px.

- **Question drawer rewrite**
  - Drawer now shows only questions from the current module.
  - Questions are grouped by section with section titles.
  - Item text wraps properly; no truncation.
  - UI text translated to Chinese.

- **Reference template fix**
  - Cards expand/collapse reliably with `display` toggle instead of grid animation.
  - No content truncation.
  - Content remains deep and detailed (m2).

- **Practice / Perspective polish**
  - Choice, fill-in, spot-the-bug exercises share the warm-paper theme.
  - Perspective judgment card uses consistent colors and notebook-style textarea.

- **Epistemic orchestration**
  - Added `.learnloop/` knowledge-state files for sources, chapter briefs, evidence packs, claims, and conflicts.
  - Updated the LearnLoop skill so a main agent can generate courses with optional subagents while retaining final epistemic responsibility.

- **Runtime refactor**
  - Created `templates/runtime-base.js` for shared question/ask/copy logic.
  - Each template's `runtime.js` only handles template-specific interactions.
  - All UI strings in runtime translated to Chinese.

- **Content**
  - `modules/02.md` remains the dense reference module.
  - Index and all hardcoded UI strings translated to Chinese.

## Verification

```bash
cd /Users/hqyone/Documents/learn-with-ai
python3 -m learnloop validate courses/acp-fundamentals
python3 -m learnloop build courses/acp-fundamentals
python3 -m unittest discover -s tests -v
python3 /Users/hqyone/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/learnloop
```

## Known issues / next steps

- Visual review by user is ongoing; screenshot feedback welcome.
- Consider adding a dark-mode theme later.
- Sidebar file-management / multi-course switch is a future feature, not implemented.
