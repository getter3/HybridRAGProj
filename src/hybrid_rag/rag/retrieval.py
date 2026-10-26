from hybrid_rag.models import SearchResult


def hybrid_search(query: str, *, limit: int = 10) -> list[SearchResult]:
    """Retrieve BM25 and vector candidates, fuse their ranks, and return results.

    TODO: implement and inspect keyword and vector retrieval independently before
    choosing a rank-fusion method.
    """
    raise NotImplementedError
