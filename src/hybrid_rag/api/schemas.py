from pydantic import BaseModel, Field

from hybrid_rag.models import SearchResult


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=100)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
