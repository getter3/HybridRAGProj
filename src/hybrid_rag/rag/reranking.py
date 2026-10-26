from hybrid_rag.api.schemas import SearchResult


def rerank(query: str, candidates: list[SearchResult]) -> list[SearchResult]:
    """Rerank a bounded candidate list using OpenRouter.

    TODO: preserve chunk IDs and metadata while applying the rerank response order.
    """
    raise NotImplementedError
