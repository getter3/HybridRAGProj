from datetime import datetime

from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: int
    filename: str
    chunk_index: int
    content: str
    metadata: dict[str, object]
    source_created_at: datetime | None
    source_modified_at: datetime | None
    score: float
    rerank_score: float
