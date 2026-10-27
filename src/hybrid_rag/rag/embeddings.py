import logging
import os
import time

from openai import OpenAI

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=os.environ["EMBEDDING_API_BASE_URL"],
    api_key=os.environ["EMBEDDING_API_KEY"],
    timeout=int(os.environ["EMBEDDING_REQUEST_TIMEOUT"]),
    max_retries=int(os.environ["EMBEDDING_RETRY_LIMIT"]),
)
embedding_model = os.environ["EMBEDDING_MODEL"]
wait_time = int(os.environ["EMBEDDING_WAIT_TIME"])


def embed_text(text: str) -> list[float]:
    """Return the embedding vector for a single text."""
    
    return (
        client.embeddings.create(
            model=embedding_model,
            input=text,
        )
        .data[0]
        .embedding
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return one embedding vector per input text."""
    embeddings = []
    for i, text in enumerate(texts, start=1):
        embedding = embed_text(text)
        embeddings.append(embedding)
        if i % 10 == 0:
            logger.info(
                "Processed %s texts; current chunk has %s characters and embedding has %s dimensions",
                i,
                len(text),
                len(embedding),
            )
        time.sleep(wait_time)

    return embeddings


class EmbeddingRetryError(Exception):
    """Exception raised for a failed embedding retry limit reached."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
