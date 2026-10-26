import os
from pathlib import Path
from sys import path
from hybrid_rag.rag.embeddings import embed_texts
from langchain_text_splitters import TokenTextSplitter
import psycopg


splitter = TokenTextSplitter(
    chunk_size=int(os.environ["CHUNK_SIZE"]),
    chunk_overlap=int(os.environ["CHUNK_OVERLAP"]),
)


def ingest_file(path: Path) -> int:
    """Load, chunk, embed, and persist one document; return its chunk count.

    TODO: implement each stage separately and make re-ingestion behavior explicit.
    Database setup and schema decisions belong to the learner.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = splitter.split_text(content)

        print(f"Chunked {len(chunks)} chunks from file {path}")
        embeddings = embed_texts(chunks)
        print(f"Generated embeddings for {len(embeddings)} chunks from file {path}")

        # open a connection to the database or storage
        connection = open_database_connection()  # Replace with actual connection code
        print(f"Opened database connection for file {path}")

        # Persist the chunks and embeddings to the database or storage
        for chunk, embedding in zip(chunks, embeddings):
            # Replace the following with actual persistence code, e.g., inserting into a database
            pass

        connection.commit()
        print(f"Persisted {len(chunks)} chunks from file {path}")
    except Exception as e:
        print(f"Error ingesting file {path}: {e}")
        return 0
    finally:
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
