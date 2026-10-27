import logging
import os
from pathlib import Path

from langchain_text_splitters import TokenTextSplitter

from hybrid_rag.rag.embeddings import embed_text, embed_texts
from hybrid_rag.rag.ingestion import ingest_file

logger = logging.getLogger(__name__)

splitter = TokenTextSplitter(
    chunk_size=int(os.environ["CHUNK_SIZE"]),
    chunk_overlap=int(os.environ["CHUNK_OVERLAP"]),
)


def prepare_file(path: Path) -> tuple[list[str], list[list[float]]]:
    with path.open("r", encoding="utf-8") as file:
        content = file.read()

    chunks = splitter.split_text(content)
    logger.info("Number of chunks: %s", len(chunks))

    # for i in range(3):
    #     if i < len(chunks):
    #         print(f"Chunks {i}: {chunks[i]}")

    embeddings = embed_texts(chunks)

    if len(chunks) != len(embeddings):
        raise ValueError(f"Got {len(embeddings)} embeddings for {len(chunks)} chunks")

    return chunks, embeddings


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # sample = Path("data/org/Shin Megami Tensei - Majin Guide.md")

    # test simple embedding
    # chunks, embeddings = prepare_file(sample)

    # print(f"Chunks: {len(chunks)}")
    # print(f"Embeddings: {len(embeddings)}")
    # if embeddings:
    #     print(f"Vector dimensions: {len(embeddings[0])}")

    # test ingest_file
    # chunk_count = ingest_file(sample)
    # logger.info("Ingested %s chunks from file %s", chunk_count, sample)

    test_text = "Stats of David in the game"
    embedding = embed_text(test_text)
    logger.info("%s", embedding)
    # logger.info("Embedding for '%s' has %s dimensions", test_text, len(embedding))
