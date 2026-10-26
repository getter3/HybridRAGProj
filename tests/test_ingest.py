import os
from pathlib import Path
from hybrid_rag.rag.embeddings import embed_texts
from hybrid_rag.rag.ingestion import ingest_file
from langchain_text_splitters import TokenTextSplitter
from hybrid_rag.rag.embeddings import embed_texts

splitter = TokenTextSplitter(
    chunk_size=int(os.environ["CHUNK_SIZE"]),
    chunk_overlap=int(os.environ["CHUNK_OVERLAP"]),
)


def prepare_file(path: Path) -> tuple[list[str], list[list[float]]]:
    with path.open("r", encoding="utf-8") as file:
        content = file.read()

    chunks = splitter.split_text(content)
    print(f"Number of chunks: {len(chunks)}")

    # for i in range(3):
    #     if i < len(chunks):
    #         print(f"Chunks {i}: {chunks[i]}")

    embeddings = embed_texts(chunks)

    if len(chunks) != len(embeddings):
        raise ValueError(f"Got {len(embeddings)} embeddings for {len(chunks)} chunks")

    return chunks, embeddings


if __name__ == "__main__":
    sample = Path("data/org/Shin Megami Tensei - Majin Guide.md")

    # test simple embedding
    # chunks, embeddings = prepare_file(sample)

    # print(f"Chunks: {len(chunks)}")
    # print(f"Embeddings: {len(embeddings)}")
    # if embeddings:
    #     print(f"Vector dimensions: {len(embeddings[0])}")

    # test ingest_file
    chunk_count = ingest_file(sample)
    print(f"Ingested {chunk_count} chunks from file {sample}")
