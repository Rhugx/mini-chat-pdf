from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.embedding import get_embedding
from backend.app.services.retrieval import search_similar
import ollama

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    doc_id: str   # 🔥 NEW

@router.post("/ask")
def ask_question(data: AskRequest):
    # Step 1: embedding
    embedding = get_embedding(data.question)

    # Step 2: retrieve ONLY from this document
    if "summarize" in data.question.lower():
        results = search_similar(embedding, data.doc_id, top_k=15)
    else:
        results = search_similar(embedding, data.doc_id, top_k=5)

    if not results:
        return {"answer": "No relevant data found"}

    # DEBUG
    print("\n🔍 Retrieved Chunks:\n")
    for i, chunk in enumerate(results):
        print(f"Chunk {i+1}:\n{chunk}\n{'-'*50}")

    # Step 3: context
    context = "\n\n".join(results)

    # Step 4: prompt
    prompt = f"""
You are a strict document extraction system.

RULES:
- Use ONLY the provided context
- DO NOT add external knowledge
- DO NOT assume anything
- DO NOT hallucinate

TASK:
Answer the question using only the context.

Context:
{context}

Question:
{data.question}

Answer:
"""

    # Step 5: LLM
    response = ollama.chat(
        model='mistral',
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

    return {
        "answer": response['message']['content']
    }