"""Essential chunking tests without external services."""

import pytest

from ingestion.chunker import chunk_document


def test_short_document_preserves_source():
    document = {"bucket": "test-bucket", "key": "documents/career.md",
                "version_id": "v1", "sequencer": "123", "text": "Experiência AWS"}

    assert chunk_document(document) == [{
        **document, "chunk_index": 0, "start_char": 0, "end_char": 15,
    }]


def test_prefer_paragraph_boundaries():
    chunks = chunk_document({"text": "First.\n\nSecond paragraph."}, max_chars=16)

    assert chunks[0]["text"] == "First.\n\n"
    assert "".join(chunk["text"] for chunk in chunks) == "First.\n\nSecond paragraph."


def test_long_paragraphs_keep_all_text_and_offsets():
    text = "Experiência AWS e Python. " + "x" * 35
    chunks = chunk_document({"text": text}, max_chars=12)

    assert chunks[0]["text"] == "Experiência "
    assert "".join(chunk["text"] for chunk in chunks) == text
    for index, chunk in enumerate(chunks):
        assert chunk["chunk_index"] == index
        assert 0 < len(chunk["text"]) <= 12
        assert chunk["text"] == text[chunk["start_char"]:chunk["end_char"]]
    assert chunks == chunk_document({"text": text}, max_chars=12)


def test_empty_text():
    assert chunk_document({"text": " \n "}) == []


def test_invalid_limit():
    with pytest.raises(ValueError, match="positive integer"):
        chunk_document({"text": "Career"}, max_chars=0)
