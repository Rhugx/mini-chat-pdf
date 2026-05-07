from fastapi import APIRouter
from pydantic import BaseModel

from dotenv import load_dotenv
import os
import ollama

from app.services.embedding import get_embedding
from app.services.retrieval import search_similar

# Load environment variables
load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    doc_id: str


@router.post("/ask")
def ask_question(data: AskRequest):

    # Step 1: Generate embedding
    embedding = get_embedding(data.question)

    # Step 2: Retrieve similar chunks
    if "summarize" in data.question.lower():

        results = search_similar(
            embedding,
            data.doc_id,
            top_k=15
        )

    else:

        results = search_similar(
            embedding,
            data.doc_id,
            top_k=5
        )

    # No results found
    if not results:

        return {
            "answer": "No relevant data found in document.",
            "sources": []
        }

    # Debug logs
    print("\n🔍 Retrieved Chunks:\n")

    for i, chunk in enumerate(results):

        print(
            f"Chunk {i+1} "
            f"(Page {chunk['page']}): "
            f"{chunk['content'][:150]}..."
        )

    # Step 3: Build context
    context = "\n\n".join(
        [
            item["content"]
            for item in results
        ]
    )

    # Step 4: Prompt
    prompt = f"""
You are a strict document extraction system.

RULES:
- Use ONLY the provided context
- DO NOT use outside knowledge
- DO NOT hallucinate
- If answer is unavailable, say:
  "Answer not found in document"

Context:
{context}

Question:
{data.question}

Answer:
"""

    # Step 5: Connect to Ollama
    client = ollama.Client(
        host=OLLAMA_HOST
    )

    # Step 6: Generate response
    response = client.chat(
        model=OLLAMA_MODEL,
        options={
            "temperature": 0.0
        },
        messages=[
            {
                "role": "system",
                "content": "Answer only using provided context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Step 7: Return answer + sources
    return {
        "answer": response["message"]["content"],
        "sources": results
    }