import logging
import os

import httpx

from hybrid_rag.models import SearchResult

logger = logging.getLogger(__name__)


def rerank(query: str, candidates: list[SearchResult]) -> list[SearchResult]:
    """Rerank a bounded candidate list using OpenRouter.

    TODO: preserve chunk IDs and metadata while applying the rerank response order.
    """
    if not candidates:
        logger.warning("No candidates to rerank.")
        return []

    payload = {
        "model": os.environ["RERANK_MODEL"],
        "query": query,
        "documents": [candidate.content for candidate in candidates],
        "top_n": len(candidates),
    }
    logger.info("Sending rerank request with payload")
    response = httpx.post(
        os.environ["RERANK_BASE_URL"],
        headers={
            "Authorization": f"Bearer {os.environ['RERANK_API_KEY']}",
        },
        json=payload,
        timeout=int(os.environ["RERANK_REQUEST_TIMEOUT"]),
    )
    response.raise_for_status()
    response_data = response.json()
    logger.info("Received rerank response: %s", response.status_code)

    ranked_candidates = []
    for item in response_data["results"]:
        index = item["index"]
        rerank_score = item.get("relevance_score", 0.0)
        # check if the index is valid
        if not isinstance(index, int) or not (0 <= index < len(candidates)):
            logger.warning("Invalid index in rerank response: %s", index)
            continue
        candidates[index].rerank_score = rerank_score
        ranked_candidates.append(candidates[index])

    return ranked_candidates
