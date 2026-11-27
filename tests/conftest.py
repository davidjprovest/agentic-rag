"""Shared pytest fixtures. Tests use search only and never call the LLM."""

import pytest

from ingest import DB_PATH, open_index
from rag_helper import RAGBase


@pytest.fixture(scope="session")
def index():
    """Search index opened once for the whole test run."""
    if not DB_PATH.exists():
        pytest.skip("data/pokemon.db missing — run: uv run ingest.py")
    return open_index()


@pytest.fixture
def assistant(index):
    """RAGBase with default settings and no LLM client."""
    return RAGBase(index=index, llm_client=None)


def names(results):
    """Return the set of Pokémon names in a list of search results."""
    return {doc["name"] for doc in results}
