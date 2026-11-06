# agentic-rag

A Pokémon question-answering assistant built with retrieval-augmented generation (RAG), following the [DataTalksClub LLM Zoomcamp: Agentic RAG](https://github.com/DataTalksClub/llm-zoomcamp/tree/main/01-agentic-rag) module with Pokémon data in place of the course FAQ.

<!-- TODO (David): one or two lines on why you're building this and what you want to learn. -->

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.15.

```bash
uv sync
echo "GEMINI_API_KEY=your-key-here" > .env
```

## Usage

```bash
uv run fetch.py   # download Pokémon from PokéAPI → data/pokemon.json (only needed to refresh data)
uv run main.py    # ask a question
```

`data/pokemon.json` is committed, so `fetch.py` is only needed to add or refresh Pokémon. Re-runs skip what's already saved.

## Checks

```bash
uvx ruff check . && uvx ruff format --check . && uv run pytest
```

Tests cover search only and never call the LLM, so they need no API key.

## Layout

| File | Purpose |
|---|---|
| `fetch.py` | PokéAPI → `data/pokemon.json` |
| `ingest.py` | Load documents and build the search index |
| `rag_helper.py` | `RAGBase`: search → prompt → LLM |
| `main.py` | Entry point, wires the client, index and assistant together |
| `tests/` | Search regression tests |

See [architecture.md](architecture.md) for diagrams.

## Status

<!-- TODO (David): update as you go. -->

Steps 01–08 done (RAG pipeline, `RAGBase` helper, tests). Next: step 09, a persistent index with sqlitesearch.
