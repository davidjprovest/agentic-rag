"""RAG pipeline: search → build prompt → LLM, wrapped in a reusable class."""

SYSTEM_PROMPT = """
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

MODEL = "gemini-3.5-flash"
BOOST = {"name": 3.0, "genus": 1.5, "abilities": 1.5, "stats": 0.3}
NUM_RESULTS = 3


class RAGBase:
    """Retrieval-augmented question answering over Pokémon documents.

    The index and LLM client are passed in rather than created here, so any
    index with a minsearch-style `search()` method (minsearch, sqlitesearch)
    and any OpenAI-compatible client can be swapped in without changing
    this class.

    Args:
        index: Search index with `search(query, boost_dict, filter_dict, num_results)`.
        llm_client: OpenAI-compatible client (Gemini via its OpenAI endpoint).
            May be None when only `search()` is used, e.g. in tests.
        system_prompt: Instructions sent as the system message.
        user_prompt_template: Template with `{question}` and `{context}` placeholders.
        generation: Optional filter, e.g. "generation-i". None searches all.
        model: Model name passed to the LLM client.
        num_results: Number of documents retrieved per question.
    """

    def __init__(
        self,
        index,
        llm_client,
        system_prompt=SYSTEM_PROMPT,
        user_prompt_template=USER_PROMPT_TEMPLATE,
        generation=None,
        model=MODEL,
        num_results=NUM_RESULTS,
    ):
        self.index = index
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.generation = generation
        self.model = model
        self.num_results = num_results

    def search(self, query):
        """Return the top `num_results` documents for the query, as dicts."""
        filter_dict = {"generation": self.generation} if self.generation else {}
        return self.index.search(
            query,
            boost_dict=BOOST,
            filter_dict=filter_dict,
            num_results=self.num_results,
        )

    def build_context(self, search_results):
        """Format retrieved documents as plain text for the prompt."""
        lines = []
        for doc in search_results:
            lines.append(f"{doc['name'].title()} ({doc['genus']}, {doc['generation']})")
            lines.append(f"Types: {doc['types']}")
            lines.append(f"Stats: {doc['stats']}")
            lines.append(f"Abilities: {doc['abilities']}")
            lines.append(f"Pokedex: {doc['pokedex']}")
            lines.append("")
        return "\n".join(lines).strip()

    def build_prompt(self, query, search_results):
        """Fill the user prompt template with the question and formatted context."""
        return self.user_prompt_template.format(
            question=query,
            context=self.build_context(search_results),
        )

    def llm(self, prompt):
        """Send the system prompt and user prompt to the LLM; return its text.

        Uses chat.completions (not the Responses API), which Gemini's
        OpenAI-compatible endpoint supports. Returns "" if the model
        returns no content.
        """
        response = self.llm_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""

    def rag(self, query):
        """Answer a question: search, build the prompt, call the LLM."""
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        return self.llm(prompt)
