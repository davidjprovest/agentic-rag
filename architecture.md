# Architecture

Current RAG pipeline: a fixed, single-search flow.

```mermaid
flowchart TD
    User([User])
    App[Application]
    DB[(DB<br/>pokemon.json · minsearch)]
    Docs[[D1 ... D3]]
    Prompt[Build Prompt<br/>Question + Context]
    LLM[LLM<br/>Gemini]
    Answer([Answer])

    User -- Question --> App
    App -- Query --> DB
    DB -- Retrieved Data --> Docs
    Docs --> App
    App --> Prompt
    Prompt --> LLM
    LLM --> Answer
    Answer --> User
```

## Mapping to code

| Diagram | Code |
|---|---|
| Application | `rag()` in [main.py](main.py) |
| DB | `index` (minsearch) built from [data/pokemon.json](data/pokemon.json), produced by [ingest.py](ingest.py) |
| Query → D1 ... D3 | `search()` returns the top `NUM_RESULTS` documents |
| Build Prompt | `build_prompt()` + `build_context()` |
| LLM | `llm()` via Gemini's OpenAI-compatible endpoint |
