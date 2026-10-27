from datetime import UTC, datetime

from hybrid_rag.models import SearchResult


def test_search_result_matches_searchable_table_fields() -> None:
    created_at = datetime(2026, 10, 26, tzinfo=UTC)
    modified_at = datetime(2026, 10, 27, tzinfo=UTC)

    result = SearchResult(
        chunk_id=12,
        filename="guide.md",
        chunk_index=3,
        content="A searchable chunk",
        metadata={"section": "Walkthrough"},
        source_created_at=created_at,
        source_modified_at=modified_at,
        score=0.032,
    )

    assert result.chunk_id == 12
    assert result.content == "A searchable chunk"
    assert result.model_dump()["source_created_at"] == created_at
