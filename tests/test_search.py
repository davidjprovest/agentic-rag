import pytest
from conftest import names

from rag_helper import NUM_RESULTS, RAGBase

FOUR = {"gengar", "alakazam", "machamp", "golem"}
FOUR_QUERY = "Compare Gengar, Alakazam, Machamp and Golem"


@pytest.mark.parametrize(
    "a, b",
    [
        ("gengar", "alakazam"),
        ("pikachu", "raichu"),
        ("charizard", "blastoise"),
        ("mewtwo", "mew"),
        ("lucario", "garchomp"),
    ],
)
def test_two_pokemon_comparison_finds_both(assistant, a, b):
    results = assistant.search(f"Compare {a.title()} and {b.title()}")
    assert {a, b} <= names(results)


def test_four_pokemon_comparison_finds_only_three_at_default_limit(assistant):
    # Known limitation: one search with NUM_RESULTS=3 can't return 4 Pokémon.
    found = FOUR & names(assistant.search(FOUR_QUERY))
    assert len(found) == NUM_RESULTS


def test_four_pokemon_comparison_works_with_more_results(index):
    assistant = RAGBase(index=index, llm_client=None, num_results=5)
    assert FOUR <= names(assistant.search(FOUR_QUERY))
