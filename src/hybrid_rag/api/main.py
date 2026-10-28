from typing import Annotated

from fastapi import FastAPI, Query

from hybrid_rag.api.schemas import SearchRequest, SearchResponse, SeekRequest
from hybrid_rag.rag.retrieval import hybrid_search, seekDoc

app = FastAPI(title="Hybrid RAG Learning API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/search", response_model=SearchResponse)
def search(request: Annotated[SearchRequest, Query()]) -> SearchResponse:
    return SearchResponse(
        query=request.query, results=hybrid_search(request.query, limit=request.limit)
    )


@app.get("/seek", response_model=SearchResponse)
def seek(request: Annotated[SeekRequest, Query()]) -> SearchResponse:
    return SearchResponse(
        query=f"chunk_id={request.chunk_id} chunk_index={request.chunk_index}",
        results=seekDoc(chunk_id=request.chunk_id, chunk_index=request.chunk_index),
    )
