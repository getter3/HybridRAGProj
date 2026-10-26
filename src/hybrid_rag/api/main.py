from fastapi import FastAPI, HTTPException

from hybrid_rag.api.schemas import SearchRequest, SearchResponse

app = FastAPI(title="Hybrid RAG Learning API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    raise HTTPException(
        status_code=501,
        detail="Implement retrieval before enabling this endpoint.",
    )
