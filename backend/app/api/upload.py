from fastapi import APIRouter, UploadFile, File
import uuid
import os

from app.utils.pdf_loader import load_pdf
from app.utils.chunking import chunk_text

from app.services.embedding import get_embedding
from app.services.store import store_embeddings

router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # Create temp directory
    os.makedirs(
        "temp_file",
        exist_ok=True
    )

    # Unique document ID
    doc_id = str(uuid.uuid4())

    # Save uploaded PDF
    file_path = f"temp_file/{file.filename}"

    with open(file_path, "wb") as f:

        content = await file.read()

        f.write(content)

    # Load PDF page-wise
    pages = load_pdf(file_path)

    # Create chunks with metadata
    chunks = chunk_text(pages)

    # Generate embeddings
    embeddings = [
        get_embedding(
            chunk["content"]
        )
        for chunk in chunks
    ]

    # Store in pgvector
    store_embeddings(
        chunks,
        embeddings,
        doc_id
    )

    return {
        "message": "PDF uploaded successfully",
        "doc_id": doc_id
    }