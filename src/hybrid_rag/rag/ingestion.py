import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb

from hybrid_rag.rag.embeddings import embed_texts

logger = logging.getLogger(__name__)

headers_to_split_on = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]

# Initialize the header-based text splitter
header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False,
)

size_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=int(os.environ["CHUNK_SIZE"]),
    chunk_overlap=int(os.environ["CHUNK_OVERLAP"]),
)

# basic splitter based on token
# splitter = TokenTextSplitter(
#     chunk_size=int(os.environ["CHUNK_SIZE"]),
#     chunk_overlap=int(os.environ["CHUNK_OVERLAP"]),
# )

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

        sections = header_splitter.split_text(content)
        chunk_documents = size_splitter.split_documents(sections)
        chunks = [document.page_content for document in chunk_documents]

        # chunks = splitter.split_text(content)

        logger.info("Chunked %s chunks from file %s", len(chunks), path)
        embeddings = embed_texts(chunks)
        logger.info(
            "Generated embeddings for %s chunks from file %s",
            len(embeddings),
            path,
        )
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
        logger.info("Opened database connection for file %s", path)

        # Persist the chunks and embeddings to the database or storage
        chunk_inserted = 0

        for chunk_index, (document, embedding) in enumerate(
            zip(chunk_documents, embeddings)
        ):
            chunk = document.page_content
            chunk_metadata = {
                **document.metadata,
                "target_chunk_size_tokens": int(os.environ["CHUNK_SIZE"]),
                "chunk_size_chars": len(chunk),
                "embedding_dimensions": len(embedding),
                "total_chunk": len(chunk_documents),
            }
            insert_document(
                connection,
                str(path.resolve()),
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
                logger.info("Inserted %s chunks for file %s", chunk_inserted, path)

        if chunk_inserted % 10 != 0:
            connection.commit()
            logger.info("Inserted %s chunks for file %s", chunk_inserted, path)

        connection.commit()
        logger.info("Persisted %s chunks from file %s", len(chunks), path)
    except Exception:
        logger.exception("Error ingesting file %s", path)
        return 0
    finally:
        if connection is not None:
            connection.close()
            logger.info("Closed database connection for file %s", path)
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


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ingest_folder = Path(os.environ["INGEST_SOURCE_DIR"])

    # ingest all the md files
    for sample_file in ingest_folder.glob("*.md"):
        logger.info("Processing file %s", sample_file)
        chunk_count = ingest_file(sample_file)
        logger.info("Ingested %s chunks from %s", chunk_count, sample_file)


if __name__ == "__main__":
    main()
