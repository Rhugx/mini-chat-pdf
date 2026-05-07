from sqlalchemy import text
from backend.app.core.database import engine

def search_similar(embedding, doc_id, top_k=5):
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    query = """
    SELECT content
    FROM documents
    WHERE doc_id = :doc_id
    ORDER BY embedding <-> :embedding
    LIMIT :top_k
    """

    with engine.connect() as conn:
        result = conn.execute(
            text(query),
            {
                "doc_id": doc_id,
                "embedding": embedding_str,
                "top_k": top_k
            }
        )
        rows = result.fetchall()

        return [row[0] for row in rows]