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


SELECT 
    sm.chunk_id,
    sm.filename,
    sm.chunk_index,
    sm.content,
    sm.metadata,
    sm.source_created_at,
    sm.source_modified_at
FROM smt1doc sm
WHERE filename = (SELECT filename FROM smt1doc WHERE chunk_id = %s)
  AND chunk_index BETWEEN %s AND %s
ORDER BY sm.chunk_index;