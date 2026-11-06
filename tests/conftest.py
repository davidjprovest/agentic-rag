"""Shared pytest fixtures. Tests use search only and never call the LLM."""

import pytest

from ingest import DATA, build_index, load_documents
from rag_helper import RAGBase


@pytest.fixture(scope="session")
def index():
    """Search index built once for the whole test run."""
    if not DATA.exists():
        pytest.skip("data/pokemon.json missing — run: uv run fetch.py")
    return build_index(load_documents())


@pytest.fixture
def assistant(index):
    """RAGBase with default settings and no LLM client."""
    return RAGBase(index=index, llm_client=None)


def names(results):
    """Return the set of Pokémon names in a list of search results."""
    return {doc["name"] for doc in results}
