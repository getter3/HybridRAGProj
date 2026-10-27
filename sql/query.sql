SELECT chunk_index, content, metadata
FROM "SMT1db".smt1doc
WHERE filename = %s
  AND chunk_index BETWEEN %s AND %s
ORDER BY chunk_index;