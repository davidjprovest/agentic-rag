"""Load Pokémon documents and build the search index.

Ingestion: `uv run ingest.py` writes data/pokemon.db.
Querying: other modules call open_index() to read it.
Nothing runs on import.
"""

import json
from pathlib import Path

from sqlitesearch import TextSearchIndex

DATA = Path(__file__).parent / "data" / "pokemon.json"
DB_PATH = Path(__file__).parent / "data" / "pokemon.db"


def load_documents():
    """Return the list of Pokémon documents from data/pokemon.json.

    Raises:
        FileNotFoundError: if the file is missing (run `uv run fetch.py`).
    """
    return json.loads(DATA.read_text())


def open_index(db_path=DB_PATH):
    """Open the sqlitesearch index stored at db_path.

    Creates an empty database if the file doesn't exist, so run
    ingest() first. Text fields are ranked by relevance; keyword fields
    are exact-match filters (e.g. {"generation": "generation-i"}).
    """
    return TextSearchIndex(
        text_fields=["name", "genus", "types", "abilities", "pokedex", "stats"],
        keyword_fields=["generation", "primary_type"],
        id_field="pokemon_id",  # "id" is reserved in sqlitesearch
        db_path=str(db_path),
    )


def ingest(documents, db_path=DB_PATH):
    """Replace the contents of the index at db_path with documents."""
    index = open_index(db_path)
    index.clear()
    index.fit([{**doc, "pokemon_id": doc["id"]} for doc in documents])
    count = index.count()
    index.close()
    return count


if __name__ == "__main__":
    print(f"Indexed {ingest(load_documents())} documents into {DB_PATH}")
