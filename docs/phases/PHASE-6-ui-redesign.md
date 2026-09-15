# Phase 6 — Monochrome UI (React frontend, brand "Nura")

**Status:** In progress — React scaffold built, backend SSE contract wired
**Dependencies:** Phases 1–5 (backend API + SSE streaming + intent guardrails)
**Skills to load:** `medibot-ui-design`, `web-design-guidelines`, `design-taste-frontend`

## Objective

Replace the Streamlit UI with a dedicated **React (Vite + TypeScript)** frontend branded **Nura**, connected to the FastAPI SSE backend. Strict **black-and-white / monochrome** design only — no accent color, no gradients, no neon. Clean, professional, medical-grade.

## Scope

- New `frontend/` directory: Vite + React 19 + TypeScript single-page app.
- Consumes backend endpoints: `POST /api/chat/stream` (SSE), `POST /api/sessions`, `GET /api/sessions/{id}/messages`, `GET /api/health`.
- Vite dev proxy: `/api` → `http://localhost:8000`.
- Streaming contract (SSE event types): `meta`, `token`, `sources`, `done`, `error`.
- Session persistence via `localStorage` (`nura.sessionId`); messages restored on load.

## In-Depth Todos

### 1. Scaffold frontend
- [x] `package.json` (react 19, react-markdown, @phosphor-icons/react, vite 7, @vitejs/plugin-react 5, typescript ~5.8).
- [x] `vite.config.ts` with `/api` proxy to `localhost:8000`.
- [x] `tsconfig.json`, `index.html`, `src/main.tsx`, `src/vite-env.d.ts`.
- [x] `.gitignore` entries: `frontend/node_modules/`, `frontend/dist/`.

### 2. Monochrome design system
- [x] `src/styles/global.css` — single token block, **black & white only**:
  - Light: `--bg #FAFAFA`, `--surface #FFF`, `--border #E4E4E7`, `--ink #0A0A0A`, `--text #18181B`.
  - Dark mode via `prefers-color-scheme` + optional toggle (`data-theme`), same ink-on-paper tokens inverted.
  - One radius scale (10px), system font stack, focus-visible rings, reduced-motion support.
- [ ] Verify contrast ≥ 4.5:1 for all body text (both modes).

### 3. Components
- [x] `Nav.tsx` — brand mark, back/home control, theme toggle (Sun/Moon).
- [x] `Landing.tsx` — hero (eyebrow, headline, subhead, 2 CTAs) + "How it works" 3-step section + minimal footer. No stats clutter, no tiny-tagline strip.
- [x] `Chat.tsx` — message list, SSE streaming, composer, auto-scroll, error handling, session create/restore.
- [x] `Message.tsx` — user bubble (black bg / white text), assistant bubble (white bg / black border), markdown rendering, expandable sources `<details>`, typing indicator.
- [x] `App.tsx` — landing ↔ chat view toggle, theme state.

### 4. Data layer
- [x] `src/lib/types.ts` — `ChatEvent`, `SourceDoc`, `HistoryMessage`, `StoredMessage`.
- [x] `src/lib/api.ts` — `createSession`, `fetchMessages`, SSE stream parser (`streamChat`).
- [x] `src/lib/session.ts` — localStorage session id helpers.

### 5. Verification
- [x] `npm run build` passes (tsc + vite build).
- [ ] Launch backend `uv run uvicorn medibot.main:app --reload`, then `npm run dev`.
- [ ] Confirm SSE streaming, citations, refusals, session restore, dark mode, and 768px/480px layout.

## Definition of Done

- Monochrome only: no accent color, gradients, or neon anywhere.
- Chat, citations, refusals, session persistence all functional against the FastAPI backend.
- Accessibility and responsive breakpoints verified.

## Run Commands

- Backend: `uv run uvicorn medibot.main:app --reload`
- Frontend dev: `npm run dev` (in `frontend/`, http://localhost:5173)
- Build: `npm run build` (in `frontend/`)