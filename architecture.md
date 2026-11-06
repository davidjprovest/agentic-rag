# Architecture

Two separate flows: **ingestion** gets the data, and **query** answers questions.

## Ingestion

Run rarely, by hand.

```mermaid
flowchart LR
    API[(PokéAPI)]
    Fetch[fetch.py<br/>fetch_all]
    JSON[data/pokemon.json<br/>1,025 documents]

    API -- "/pokemon, /pokemon-species, /ability" --> Fetch
    Fetch -- save --> JSON
```

## Query

Runs on every question. The index is currently rebuilt in memory on each run.

```mermaid
flowchart TD
    User([User])
    App[RAGBase.rag]
    Index[(Index<br/>minsearch, in memory)]
    Docs[[D1 ... D3]]
    Prompt[build_prompt<br/>Question + Context]
    LLM[LLM<br/>Gemini]
    Answer([Answer])
    JSON[data/pokemon.json]

    JSON -- "load_documents + build_index" --> Index
    User -- Question --> App
    App -- search --> Index
    Index -- Retrieved docs --> Docs
    Docs --> App
    App --> Prompt
    Prompt --> LLM
    LLM --> Answer
    Answer --> User
```

## Mapping to code

| Diagram | Code |
|---|---|
| fetch.py | `fetch_all()` → `fetch_pokemon(i)` per Pokémon, `save()` |
| Index | `build_index()` in [ingest.py](ingest.py) (minsearch) |
| RAGBase.rag | [rag_helper.py](rag_helper.py): `search()` → `build_prompt()` → `llm()` |
| D1 ... D3 | `search()` returns the top `NUM_RESULTS` documents (default 3) |
| LLM | `llm()` via Gemini's OpenAI-compatible endpoint (`chat.completions`) |
| Wiring | [main.py](main.py) creates the client and index, then `RAGBase` |

## Document shape

```json
{
  "id": 94,
  "name": "gengar",
  "genus": "Shadow Pokémon",
  "generation": "generation-i",
  "primary_type": "ghost",
  "types": "ghost poison",
  "legendary": false,
  "abilities": "cursed-body: ...",
  "stats": "hp: 60, attack: 65, ...",
  "pokedex": "..."
}
```

Text fields (searched): `name`, `genus`, `types`, `abilities`, `pokedex`, `stats`.
Keyword fields (filters): `generation`, `primary_type`.

## Planned

- **Step 09:** ingestion also writes `data/pokemon.db` (sqlitesearch), and the query flow opens it instead of rebuilding the index.
- **Steps 13–14:** the LLM calls `search` as a tool, in a loop, until it can answer.
