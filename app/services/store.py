from sqlalchemy import text
from app.core.database import engine

def store_embedding(content, embedding, doc_id):
    # Convert embedding list → string format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    query = """
    INSERT INTO documents (content, embedding, doc_id)
    VALUES (:content, :embedding, :doc_id)
    """

    with engine.connect() as conn:
        conn.execute(
            text(query),
            {
                "content": content,
                "embedding": embedding_str,  # ✅ NO ::vector
                "doc_id": doc_id
            }
        )
        conn.commit()