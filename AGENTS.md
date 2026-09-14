# AGENTS.md — MediBot

MediBot is a RAG-based clinical reference assistant evolving toward a production-grade, modular FastAPI backend.

## Load these before starting work

- **Docs index:** read `docs/00-overview.md` first, then the relevant section (`requirements/design/implementation/testing/evaluation/release/learning`).
- **Architecture:** read `ARCHITECTURE.md` (root) for the target-state architecture diagram, file structure, and key points.
- **Roadmap:** read `docs/phases/README.md` for the phased upgrade plan.
- **Artifacts:** read `docs/04-testing/test-results/` and `docs/05-evaluation/results/` for latest test/eval state; `docs/07-learning/known-gaps.md` for open items.
- **UI work:** load the `medibot-ui-design` skill (`.opencode/skills/medibot-ui-design/SKILL.md`).
- **Architecture/refactor work:** load the `medibot-architecture` skill (`.opencode/skills/medibot-architecture/SKILL.md`).
- **Phase implementation:** read the specific `docs/phases/PHASE-<N>-*.md` doc and execute its todos.

## Commands

- Run tests: `uv run pytest tests/ -v`
- Lint: `uv run ruff check src/ tests/`
- Format check: `uv run ruff format --check src/ tests/`
- Launch web UI: `uv run medibot web`
- Run the app backend (after Phase 1): `uv run uvicorn medibot.main:app --reload`

## Conventions

- `src/` layout; `snake_case`; docstrings on all modules/functions.
- Type hints everywhere (`str | None`).
- Config centralized via `Session`/`Settings` (Pydantic BaseSettings) — no scattered `os.getenv`.
- **Prompts live in `src/medibot/prompts/` as `.py` module exports — never inline prompt strings in routes, services, or UI code.**
- Dependencies for ruff (E, F, I, N, W, UP; line-length 100) and pytest in `pyproject.toml`.

## Security

- Never commit or log secrets. `.env` (GROQ_API_KEY) is gitignored.
- Never log API keys/tokens.
