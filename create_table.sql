CREATE TABLE "SMT1db".smt1doc (
    chunk_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    filename TEXT NOT NULL,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    content TEXT NOT NULL,
    embedding VECTOR(2048) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_created_at TIMESTAMPTZ,
    source_modified_at TIMESTAMPTZ
);


CREATE INDEX smt1doc_search_idx
ON "SMT1db".smt1doc
USING paradedb (
    chunk_id,
    filename,
    content,
    embedding vector_cosine_ops
);


CREATE INDEX smt1doc_filename_idx1
ON "SMT1db".smt1doc (filename, source_created_at);


CREATE INDEX smt1doc_filename_idx2
ON "SMT1db".smt1doc (filename, source_modified_at);

CREATE INDEX smt1doc_maintain_idx1
ON "SMT1db".smt1doc (source_created_at);

CREATE INDEX smt1doc_maintain_idx2
ON "SMT1db".smt1doc (source_modified_at);


