"""Load Pokémon documents and build the search index.

Imported by main.py and the tests. Nothing runs on import.
"""

import json
from pathlib import Path

from minsearch import Index

DATA = Path(__file__).parent / "data" / "pokemon.json"


def load_documents():
    """Return the list of Pokémon documents from data/pokemon.json.

    Raises:
        FileNotFoundError: if the file is missing (run `uv run fetch.py`).
    """
    return json.loads(DATA.read_text())


def build_index(documents):
    """Build an in-memory minsearch index over the Pokémon documents.

    Text fields are ranked by relevance; keyword fields are exact-match
    filters (e.g. {"generation": "generation-i"}).
    """
    index = Index(
        text_fields=["name", "genus", "types", "abilities", "pokedex", "stats"],
        keyword_fields=["generation", "primary_type"],
    )
    index.fit(documents)
    return index
