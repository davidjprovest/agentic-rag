import pytest

from ingest import DATA, build_index, load_documents
from rag_helper import RAGBase


@pytest.fixture(scope="session")
def index():
    if not DATA.exists():
        pytest.skip("data/pokemon.json missing — run: uv run fetch.py")
    return build_index(load_documents())


@pytest.fixture
def assistant(index):
    return RAGBase(index=index, llm_client=None)


def names(results):
    return {doc["name"] for doc in results}
