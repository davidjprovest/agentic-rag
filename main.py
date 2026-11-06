import json
import os
from pathlib import Path

from dotenv import load_dotenv
from minsearch import Index
from openai import OpenAI

load_dotenv()

MODEL = "gemini-3.5-flash"
NUM_RESULTS = 3
BOOST = {"name": 3.0, "genus": 1.5, "abilities": 1.5, "stats": 0.3}

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY not set — add it to .env")

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Load Pokemon Dataset
DATA = Path(__file__).parent / "data" / "pokemon.json"
documents = json.loads(DATA.read_text())

# Search
index = Index(
    text_fields=["name", "genus", "types", "abilities", "pokedex", "stats"],
    keyword_fields=["generation", "primary_type"],
)

index.fit(documents)


def search(question, generation=None):
    filter_dict = {"generation": generation} if generation else {}
    return index.search(
        question,
        boost_dict=BOOST,
        filter_dict=filter_dict,
        num_results=NUM_RESULTS,
    )


# Prompt
INSTRUCTIONS = """
You are a Pokemon expert. Answer the question based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
""".strip()

USER_PROMPT_TEMPLATE = """
Question:
{question}

Context:
{context}
""".strip()


def build_context(search_results):
    lines = []
    for doc in search_results:
        lines.append(f"{doc['name'].title()} ({doc['genus']}, {doc['generation']})")
        lines.append(f"Types: {doc['types']}")
        lines.append(f"Stats: {doc['stats']}")
        lines.append(f"Abilities: {doc['abilities']}")
        lines.append(f"Pokedex: {doc['pokedex']}")
        lines.append("")
    return "\n".join(lines).strip()


def build_prompt(question, search_results):
    return USER_PROMPT_TEMPLATE.format(
        question=question,
        context=build_context(search_results),
    )


# LLM
def llm(instructions, user_prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


# Retrieval-augemented generation (RAG)
def rag(question):
    search_results = search(question)
    prompt = build_prompt(question, search_results)
    return llm(INSTRUCTIONS, prompt)


def main():
    print(
        # print(rag("Compare Gengar and Alakazam"))        # Works as both names are boosted and within top 3 results
        rag(
            "Compare Gengar, Alakazam, Machamp and Golem"
        )  # Only returning top 3 search results. Output: I don't know. The provided context contains information for Alakazam, Machamp, and Gengar, but does not contain any information about Golem.
    )


if __name__ == "__main__":
    main()
