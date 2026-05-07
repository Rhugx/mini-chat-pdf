from sqlalchemy import text

from app.core.database import engine


def search_similar(
    query_embedding,
    doc_id,
    top_k=5
):

    embedding_str = "[" + ",".join(
        map(str, query_embedding)
    ) + "]"

    with engine.connect() as conn:

        query = text(
            """
            SELECT content, page
            FROM documents
            WHERE doc_id = :doc_id
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
            """
        )

        results = conn.execute(
            query,
            {
                "doc_id": doc_id,
                "embedding": embedding_str,
                "top_k": top_k
            }
        )

        rows = results.fetchall()

        return [
            {
                "content": row[0],
                "page": row[1]
            }
            for row in rows
        ]