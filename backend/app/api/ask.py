from fastapi import APIRouter
from pydantic import BaseModel

from app.services.embedding import get_embedding
from app.services.retrieval import search_similar

import ollama

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    doc_id: str


@router.post("/ask")
def ask_question(data: AskRequest):

    # Step 1: Generate embedding for user question
    embedding = get_embedding(data.question)

    # Step 2: Retrieve relevant chunks
    if "summarize" in data.question.lower():
        results = search_similar(embedding, data.doc_id, top_k=15)
    else:
        results = search_similar(embedding, data.doc_id, top_k=5)

    if not results:
        return {
            "answer": "No relevant data found"
        }

    # DEBUG LOGS
    print("\n🔍 Retrieved Chunks:\n")

    for i, chunk in enumerate(results):
        print(f"Chunk {i+1}:\n{chunk}\n{'-' * 50}")

    # Step 3: Build context
    context = "\n\n".join(results)

    # Step 4: Prompt
    prompt = f"""
You are a strict document extraction system.

RULES:
- Use ONLY the provided context
- DO NOT add external knowledge
- DO NOT hallucinate
- If answer is not present, say "Answer not found in document"

TASK:
Answer the question using only the context.

Context:
{context}

Question:
{data.question}

Answer:
"""

    # Step 5: Connect to Ollama running on HOST machine
    client = ollama.Client(
        host="http://host.docker.internal:11434"
    )

    # Step 6: Generate response
    response = client.chat(
        model="mistral",
        options={
            "temperature": 0.0
        },
        messages=[
            {
                "role": "system",
                "content": "Answer only from given context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Step 7: Return answer
    return {
        "answer": response["message"]["content"]
    }