# CLAUDE.md

Pokémon RAG assistant, following the DataTalksClub LLM Zoomcamp `01-agentic-rag` module. Setup, usage and layout are in README.md; diagrams in architecture.md.

## Commands

- Fetch data: `uv run fetch.py` (rarely needed; data/pokemon.json is committed)
- Run: `uv run main.py`
- Checks: `uvx ruff check . && uvx ruff format --check . && uv run pytest`

## How we work

- David writes the code to learn. Claude reviews and explains by default, and writes files only when asked.
- Reviews: list issues with file:line links, ordered by severity, and include the corrected code.
- Verify claims by running things (tests, a quick search) instead of guessing.

## Git

- Work on the `pokemon-rag` branch, reused across PRs.
- Merge PRs with a merge commit, never squash or rebase (it breaks branch reuse).
- Run `git pull origin main` right after each merge, before any new work.

## Gotchas

- Gemini goes through the OpenAI client: use `chat.completions`, not the Responses API.
- Tests call `search()` only and never the LLM (fast, free, deterministic). Assert on membership and counts, not ranking order.
- `id` is reserved in sqlitesearch: use `id_field="pokemon_id"`.
- Importing a module must not run work. Put scripts behind `if __name__ == "__main__":`.

## Current step

Step 09 (sqlitesearch), then 13–14 (function calling and the agentic loop).
