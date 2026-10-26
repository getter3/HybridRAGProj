import os
from datetime import datetime, timezone
from pathlib import Path
from hybrid_rag.rag.embeddings import embed_texts
from langchain_text_splitters import TokenTextSplitter
import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb


splitter = TokenTextSplitter(
    chunk_size=int(os.environ["CHUNK_SIZE"]),
    chunk_overlap=int(os.environ["CHUNK_OVERLAP"]),
)

INSERT_SQL = """
    INSERT INTO "SMT1db".smt1doc
        (filename, chunk_index, content, embedding,
         source_created_at, source_modified_at, metadata)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


def ingest_file(path: Path) -> int:
    """Load, chunk, embed, and persist one document; return its chunk count.

    TODO: implement each stage separately and make re-ingestion behavior explicit.
    Database setup and schema decisions belong to the learner.
    """
    connection = None
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = splitter.split_text(content)

        print(f"Chunked {len(chunks)} chunks from file {path}")
        embeddings = embed_texts(chunks)
        print(f"Generated embeddings for {len(embeddings)} chunks from file {path}")
        if len(embeddings) != len(chunks):
            raise ValueError(
                "The number of embeddings does not match the number of chunks"
            )

        stat = path.stat()
        source_created_at = datetime.fromtimestamp(
            getattr(stat, "st_birthtime", stat.st_ctime), tz=timezone.utc
        )
        source_modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

        # open a connection to the database or storage
        connection = open_database_connection()  # Replace with actual connection code
        register_vector(connection)
        print(f"Opened database connection for file {path}")

        # Persist the chunks and embeddings to the database or storage
        chunk_inserted = 0

        for chunk_index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_metadata = {
                "target_chunk_size_tokens": int(os.environ["CHUNK_SIZE"]),
                "chunk_size_chars": len(chunk),
                "embedding_dimensions": len(embedding),
                "total_chunk": len(chunks),
            }
            insert_document(
                connection,
                path.name,
                chunk_index,
                chunk_metadata,
                chunk,
                embedding,
                source_created_at,
                source_modified_at,
            )
            chunk_inserted += 1
            if chunk_inserted % 10 == 0:
                connection.commit()
                print(f"Inserted {chunk_inserted} chunks for file {path}")

        if chunk_inserted % 10 != 0:
            connection.commit()
            print(f"Inserted {chunk_inserted} chunks for file {path}")

        connection.commit()
        print(f"Persisted {len(chunks)} chunks from file {path}")
    except Exception as e:
        print(f"Error ingesting file {path}: {e}")
        return 0
    finally:
        if connection is not None:
            connection.close()
            print(f"Closed database connection for file {path}")
    return len(chunks)


def open_database_connection():
    return psycopg.connect(
        host=os.environ["DATABASE_HOST"],
        port=int(os.environ["DATABASE_PORT"]),
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        connect_timeout=30,
    )


def insert_document(
    connection,
    filename,
    chunk_index,
    metadata,
    chunk: str,
    embedding: list[float],
    source_created_at,
    source_modified_at,
):
    connection.execute(
        INSERT_SQL,
        (
            filename,
            chunk_index,
            chunk,
            Vector(embedding),
            source_created_at,
            source_modified_at,
            Jsonb(metadata),
        ),
    )
