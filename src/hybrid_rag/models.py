from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: str
    text: str
    source: str
    score: float
