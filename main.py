import os

from dotenv import load_dotenv
from openai import OpenAI

from ingest import build_index, load_documents
from rag_helper import RAGBase


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY not set — add it to .env")

    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    index = build_index(load_documents())
    assistant = RAGBase(index=index, llm_client=client)

    # Only returning top 3 search results. Output: I don't know. The provided context contains information for Alakazam, Machamp, and Gengar, but does not contain any information about Golem.
    print(assistant.rag("Compare Gengar, Alakazam, Machamp and Golem"))


if __name__ == "__main__":
    main()
