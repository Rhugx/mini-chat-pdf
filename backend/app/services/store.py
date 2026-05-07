from app.models.vector_store import Document
from app.core.database import SessionLocal


def store_embeddings(chunks, embeddings, doc_id):

    db = SessionLocal()

    for chunk, embedding in zip(chunks, embeddings):

        doc = Document(
            doc_id=doc_id,
            content=chunk,
            embedding=embedding
        )

        db.add(doc)

    db.commit()

    db.close()