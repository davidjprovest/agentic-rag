import json
from pathlib import Path

from minsearch import Index

DATA = Path(__file__).parent / "data" / "pokemon.json"


def load_documents():
    return json.loads(DATA.read_text())


def build_index(documents):
    index = Index(
        text_fields=["name", "genus", "types", "abilities", "pokedex", "stats"],
        keyword_fields=["generation", "primary_type"],
    )
    index.fit(documents)
    return index
