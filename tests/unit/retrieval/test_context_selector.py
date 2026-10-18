"""Essential context selection tests."""

import pytest

from retrieval.context_selector import select_context


def test_ranked_sources_preserve_metadata():
    matches = [
        {"document_id": 1, "chunk_index": 0, "source": "career.md", "version_id": "v1", "text": "Backend", "distance": 0.1},
        {"document_id": 2, "chunk_index": 0, "source": "project.md", "text": "AWS", "distance": 0.2},
    ]
    result = select_context(matches)
    assert result["context"] == "[S1]\nBackend\n\n[S2]\nAWS"
    assert result["sources"] == [{**matches[0], "id": "S1"}, {**matches[1], "id": "S2"}]
    assert "id" not in matches[0]


def test_budget_includes_labels_and_separators():
    matches = [{"source": "a.md", "text": "AWS"}, {"source": "b.md", "text": "Cloud"}]
    result = select_context(matches, max_chars=len("[S1]\nAWS"))
    assert result["context"] == "[S1]\nAWS"
    assert len(result["sources"]) == 1


def test_skip_oversized_chunk_without_truncation():
    matches = [{"source": "a.md", "text": "x" * 30}, {"source": "b.md", "text": "AWS"}]
    result = select_context(matches, max_chars=10)
    assert result["context"] == "[S1]\nAWS"
    assert result["sources"][0]["source"] == "b.md"


def test_empty_and_duplicate_chunks():
    chunk = {"document_id": 1, "chunk_index": 0, "source": "career.md", "text": "Backend"}
    result = select_context([{"source": "empty.md", "text": "  "}, chunk, chunk])
    assert len(result["sources"]) == 1
    assert select_context([]) == {"context": "", "sources": []}
    assert select_context([chunk], max_chars=1) == {"context": "", "sources": []}


def test_invalid_budget():
    with pytest.raises(ValueError, match="positive integer"):
        select_context([], max_chars=0)
