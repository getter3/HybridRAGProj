import logging
import os

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector

from hybrid_rag.models import SearchResult
from hybrid_rag.rag.embeddings import embed_text
from hybrid_rag.rag.reranking import rerank

QUERY_SQL = """
WITH semantic_results AS (
    SELECT
        chunk_id,
        RANK() OVER (ORDER BY embedding <=> %s::vector) AS rank
    FROM "SMT1db".smt1doc
    ORDER BY embedding <=> %s::vector
    LIMIT 20
),
fulltext_results AS (
    SELECT
        chunk_id,
        RANK() OVER (ORDER BY score DESC) AS rank
    FROM (
        SELECT
            chunk_id,
            pdb.score(chunk_id) AS score
        FROM "SMT1db".smt1doc
        WHERE content @@@ %s
        ORDER BY pdb.score(chunk_id) DESC
        LIMIT 20
    ) AS fulltext_candidates
),
rrf_results AS (
    SELECT chunk_id, 1.0 / (60 + rank) AS score FROM semantic_results
    UNION ALL
    SELECT chunk_id, 1.0 / (60 + rank) AS score FROM fulltext_results
)
SELECT
    sm.chunk_id,
    sm.filename,
    sm.chunk_index,
    sm.content,
    sm.metadata,
    sm.source_created_at,
    sm.source_modified_at,
    SUM(rrf.score) AS score
FROM rrf_results AS rrf
JOIN "SMT1db".smt1doc AS sm USING (chunk_id)
GROUP BY
    sm.chunk_id,
    sm.filename,
    sm.chunk_index,
    sm.content,
    sm.metadata,
    sm.source_created_at,
    sm.source_modified_at
ORDER BY score DESC
LIMIT %s;
"""


logger = logging.getLogger(__name__)


def hybrid_search(query: str, *, limit: int = 10) -> list[SearchResult]:
    """Retrieve BM25 and vector candidates, fuse their ranks, and return results.

    TODO: implement and inspect keyword and vector retrieval independently before
    choosing a rank-fusion method.
    """

    connection = None
    search_results = []

    try:
        # embed the query
        query_embedding = embed_text(query)

        connection = open_database_connection()
        cursor = connection.execute(
            QUERY_SQL, (query_embedding, query_embedding, query, limit)
        )
        results = cursor.fetchall()

        search_results = [
            SearchResult(
                chunk_id=row[0],
                filename=row[1],
                chunk_index=row[2],
                content=row[3],
                metadata=row[4],
                source_created_at=row[5],
                source_modified_at=row[6],
                score=row[7],
            )
            for row in results
        ]
        search_results = rerank(query, search_results)

    except Exception as e:
        logger.error(f"Error during hybrid search: {e}")
    finally:
        if connection is not None:
            connection.close()

    return search_results


def open_database_connection():
    return psycopg.connect(
        host=os.environ["DATABASE_HOST"],
        port=int(os.environ["DATABASE_PORT"]),
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        connect_timeout=30,
    )


with open_database_connection() as connection:
    register_vector(connection)  # once per connection, if not already done

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    query = "Where we met Pascal the dog?"
    results = hybrid_search(query, limit=5)
    for result in results:
        logging.info(
            "result: id:%s index:%s score:%s  file:%s  content:%s",
            result.chunk_id,
            result.chunk_index,
            result.score,
            result.filename,
            result.content[:50],
        )
