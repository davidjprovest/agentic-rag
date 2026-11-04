import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "gemini-3.5-flash" 

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

PROMPT_TEMPLATE = """
Your task is to answer questions based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."

User location (use this to choose the nearest store):
{user_context}

Question:
{question}

Context:
{context}
""".strip()

# Database of company information
def search(question):
    return [
        "Hurstville Kmart is open from 8am until 10pm.",
        "Blacktown Kmart is open 6am until 12am."
    ]

def build_prompt(question, search_results, user_context):
    return PROMPT_TEMPLATE.format(
        question=question,
        context="\n\n".join(search_results),
        user_context=user_context,
    )

def llm(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

# retrieval, augemented generation (RAG)
def rag(question, user_context):
    search_results = search(question)
    prompt = build_prompt(question, search_results, user_context)
    return llm(prompt)

def main():
    print(llm(prompt))


if __name__ == "__main__":
    main()
