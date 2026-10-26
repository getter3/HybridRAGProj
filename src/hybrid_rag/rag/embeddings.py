from openai import OpenAI
import os
import time

client = OpenAI(
    base_url=os.environ["EMBEDDING_API_BASE_URL"],
    api_key=os.environ["EMBEDDING_API_KEY"],
    timeout=int(os.environ["EMBEDDING_REQUEST_TIMEOUT"]),
    max_retries=int(os.environ["EMBEDDING_RETRY_LIMIT"]),
)
embedding_model = os.environ["EMBEDDING_MODEL"]
wait_time = int(os.environ["EMBEDDING_WAIT_TIME"])


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return one embedding vector per input text."""
    embeddings = []
    i = 0
    for text in texts:
        embedding = client.embeddings.create(
            model=embedding_model,
            input=text,
        )
        embeddings.append(embedding.data[0].embedding)
        i += 1
        if i % 10 == 0:
            print(f"Processed {i} texts")
            print(f"chunk : {text} ")
            print(f"vector: {embedding.data[0].embedding}")
        time.sleep(wait_time)

    return embeddings


class EmbeddingRetryError(Exception):
    """Exception raised for a failed embedding retry limit reached."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
