# Phase 6 — Professional UI Redesign

**Status:** Planned
**Dependencies:** Phases 1–5 (all backend + feature work)
**Skills to load:** `medibot-ui-design`, `web-design-guidelines`, `design-taste-frontend`

## Objective

Replaces the current gradient-heavy, decorative `app.py` styling with a clean, professional, medical-grade UI that communicates trust, precision, and calm. No full-bleed gradients, no neon colors.

## Scope

- Single file: `src/medibot/app.py` (the `_CSS` string + HTML structure + landing + chat renderers)
- Add `docs/phases/PHASE-1-UI-design-plan.md` detailed design notes (this doc is the plan)

## In-Depth Todos

### 1. Audit current styling
- [ ] Read `src/medibot/app.py` fully (623 lines) and catalog every CSS class, gradient, shadow, and color.
- [ ] Identify all full-bleed gradients, saturated colors, decorative blurs.
- [ ] List interactive elements (navbar, buttons, chat input, source citations, feedback buttons).

### 2. Establish the design token system
- [ ] Define a single CSS custom-property block at top of `_CSS`:
  - `--primary` (pick one: teal `#0F766E` OR blue `#2563EB`)
  - `--primary-hover`, `--primary-soft` (rgba tint)
  - `--bg`, `--surface`, `--border`, `--text`, `--text-muted`
  - Semantic: `--success`, `--warning`, `--error`, `--info`
  - `--radius-sm/md/lg`, `--shadow`, `--font-sans`, `--spacing-*`
- [ ] Ensure light mode is the default; add optional dark mode via `prefers-color-scheme` if feasible (keep scope conservative).

### 3. Rebuild navigation bar
- [ ] Fixed top bar, height 56–64px, surface bg, `1px solid var(--border)` bottom border.
- [ ] Brand: logo (inline SVG), "MediBot", muted subtitle "Clinical Reference".
- [ ] Status badge: "Online" with subtle green pulse dot (muted green text, not neon).
- [ ] Remove any gradient background from the current navbar.

### 4. Rebuild chat interface
- [ ] Message bubbles per skill:
  - User: `var(--primary-soft)` bg, right-aligned, radius 10px
  - Assistant: `var(--surface)` bg + 1px border, left-aligned
- [ ] Source citations: `<details>` element, "View sources (n)" label, info-blue icon, muted text. Readable expandable block.
- [ ] Feedback buttons (+1 / −1): subtle bordered buttons, primary on active.
- [ ] Welcome screen: clean centered message, muted, no heavy decoration.
- [ ] Chat input: 1px border, radius 8px, visible focus ring.
- [ ] Medical disclaimer footer: clear, muted, persistent.

### 5. Rebuild landing page
- [ ] Hero: headline (2.5–3rem, 700), one-line subhead, one primary CTA + one secondary CTA.
- [ ] Stat blocks: big number (primary, 2rem) + muted uppercase label.
- [ ] Feature cards: surface bg, 1px border, radius 12px, padding 24; soft tinted icon square; title (600) + muted description. Optional 3px primary top accent — restrained, no full-bleed gradient.
- [ ] "How It Works" steps: numbered or simple ordered cards, consistent spacing.
- [ ] CTA banner + footer: flat surfaces, muted text.

### 6. Swap emoji/decorative icons to inline SVG
- [ ] Replace emoji in landing/chat avatars with stroke-based inline SVGs using `currentColor`.
- [ ] Keep icons consistent stroke weight.

### 7. Accessibility & responsiveness
- [ ] Verify contrast ≥ 4.5:1 for all body text.
- [ ] Visible focus states on all interactive elements.
- [ ] Breakpoints at 768px and 480px; ensure nav and cards stack gracefully.
- [ ] Body font size ≥ 14px.

### 8. Verification
- [ ] Run `uv run ruff check src/` (ensure no import/style regressions).
- [ ] Launch `uv run medibot web` and visually confirm no gradients/neon remain.
- [ ] Confirm chat streaming still works with new CSS.
- [ ] Confirm source citations and disclaimer render correctly.

## Definition of Done

- No full-bleed gradients or neon colors remain.
- Single design-token palette in `_CSS`.
- Inline SVG icons replace emoji where used as icons.
- Accessibility checks pass.
- Chat streaming, citations, feedback, disclaimer all functional.
