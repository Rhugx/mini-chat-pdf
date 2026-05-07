from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from backend.app.services.embedding import get_embedding
from backend.app.services.store import store_embedding
from backend.app.utils.pdf_loader import load_pdf
from backend.app.utils.chunking import chunk_text
from sqlalchemy import text
from backend.app.core.database import engine
import os

router = APIRouter()

# -------------------------------
# 🔹 DELETE OLD DOCUMENT DATA
# -------------------------------
def delete_old_doc(doc_id):
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM documents WHERE doc_id = :doc_id"),
            {"doc_id": doc_id}
        )
        conn.commit()


# -------------------------------
# 🔹 TEXT UPLOAD
# -------------------------------
class UploadRequest(BaseModel):
    text: str

@router.post("/upload")
def upload_text(data: UploadRequest):
    embedding = get_embedding(data.text)
    store_embedding(data.text, embedding, doc_id="manual")
    return {"message": "Stored successfully"}


# -------------------------------
# 🔹 PDF UPLOAD (FINAL)
# -------------------------------
@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        return {"error": "Please upload a valid PDF file"}

    file_path = f"temp_{file.filename}"

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        text = load_pdf(file_path)
    except Exception:
        os.remove(file_path)
        return {"error": "Invalid PDF"}

    chunks = chunk_text(text)

    doc_id = file.filename

    # 🔥 remove old data
    delete_old_doc(doc_id)

    stored_count = 0

    for chunk in chunks:
        if chunk.strip() and len(chunk) > 50:
            embedding = get_embedding(chunk)
            store_embedding(chunk, embedding, doc_id)
            stored_count += 1

    os.remove(file_path)

    return {
        "message": "PDF processed successfully",
        "doc_id": doc_id,
        "chunks_stored": stored_count
    }