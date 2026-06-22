# LearnLoop — Project Progress

## Current status

Comprehensive frontend redesign completed for the ACP fundamentals sample course. All four templates (`tutorial`, `reference`, `practice`, `case`) now share a unified warm-purple + cream design system, use a distinctive serif/sans/mono font pairing, and have polished, template-specific interactions.

## Completed work

- **Shared design system**
  - Added `templates/base.css` with the warm-purple palette, typography, spacing, tables, code blocks with copy buttons, callouts, module cards, navigation, ask forms, question drawer, and shared exercise/checkpoint primitives.
  - Updated all `templates/*/template.html` files to load Google Fonts and `assets/base.css` plus their own `style.css`.
  - Updated `learnloop/renderer.py` to copy `templates/base.css` into `dist/assets/base.css` during every build.

- **Template-specific polish**
  - `tutorial`: editorial reading experience, generous whitespace, reflection checkpoints with amber accent.
  - `reference`: dense knowledge warehouse with sticky header, file-folder cards, smooth expand/collapse via `.card-inner`, and a runtime card-filter input.
  - `practice`: worksheet aesthetic with styled radio cards, underlined fill-in-the-blank inputs, spot-the-bug line highlighting, smooth feedback reveal, and prominent check buttons.
  - `case`: judgment notebook with scenario card, lined reasoning textarea, smooth accordion reveal, and colored perspective/tradeoffs/pitfalls sections.

- **Runtime parity**
  - Rewrote all four `runtime.js` files to keep: question drawer, `/ask` posting, copy buttons, mark-done checkboxes, answer toggles, reference card toggles/filter, practice exercise checking, and case judgment reveal.

- **Content**
  - Deepened `modules/02.md` into a dense reference module with role tables, JSON-RPC field reference, request/response/error examples, stdio rules and Python snippet, lifecycle steps, and quick-reference card.

- **Tests**
  - Updated `tests/test_learnloop.py` to assert that `assets/base.css` is generated and loaded, and added `test_all_templates_produce_non_empty_html`.

## Verification

Run:

```bash
cd /Users/hqyone/Documents/learn-with-ai
python3 -m learnloop validate courses/acp-fundamentals
python3 -m learnloop build courses/acp-fundamentals
python3 -m unittest discover -s tests -v
python3 /Users/hqyone/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/learnloop
```

Browser check:

```bash
python3 -m learnloop serve courses/acp-fundamentals --port 8800
```

Then open `index.html`, `m1.html`, `m2.html`, `m3.html`, `m5.html`.

## Template / theme architecture

```text
templates/
├── base.css            # shared variables, typography, components, utilities
├── tutorial/
│   ├── template.html   # loads base.css + style.css + fonts
│   ├── style.css       # editorial overrides
│   └── runtime.js
├── reference/
│   ├── template.html
│   ├── style.css       # dense/card overrides
│   └── runtime.js      # card toggles + filter
├── practice/
│   ├── template.html
│   ├── style.css       # interactive exercise overrides
│   └── runtime.js      # choice / fill / bug checking
└── case/
    ├── template.html
    ├── style.css       # judgment notebook overrides
    └── runtime.js      # perspective/tradeoffs/pitfalls reveal
```

## Known issues / next steps

- Google Fonts require an internet connection on first load. If offline-first becomes a hard requirement, bundle font files or switch to refined system-only stacks.
- Reference card expand/collapse uses CSS `grid-template-rows` animation; very long cards (> viewport height) still expand instantly because `grid-template-rows: 1fr` expands to content size—acceptable for reference cards.
- The judgment reveal uses a fixed `max-height` transition; extremely long judgment cards may clip if content exceeds the chosen max-height.
- No visual regression automation; browser screenshots are still a manual step.
- Consider adding a dark mode toggle or print stylesheet in a future pass.
