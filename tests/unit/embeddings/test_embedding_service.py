"""Essential embedding tests using a simulated OpenAI client."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from embeddings.embedding_service import BATCH_SIZE, DIMENSIONS, MODEL, embed_chunks


def response(*indices):
    return SimpleNamespace(data=[
        SimpleNamespace(index=i, embedding=[float(i)] * DIMENSIONS) for i in indices
    ])


def test_preserve_source_and_match_response_order():
    client = Mock()
    client.embeddings.create.return_value = response(1, 0)
    chunks = [{"text": "AWS", "key": "career.md", "chunk_index": 0}, {"text": "Python"}]

    result = embed_chunks(client, chunks)

    assert result[0] == {**chunks[0], "embedding": [0.0] * DIMENSIONS,
                         "embedding_model": MODEL, "embedding_dimensions": DIMENSIONS}
    assert result[1]["embedding"] == [1.0] * DIMENSIONS
    assert "embedding" not in chunks[0]
    client.embeddings.create.assert_called_once_with(
        model=MODEL, dimensions=DIMENSIONS, input=["AWS", "Python"], encoding_format="float")


def test_split_requests_into_batches():
    client = Mock()
    client.embeddings.create.side_effect = [response(*range(BATCH_SIZE)), response(0)]

    assert len(embed_chunks(client, [{"text": "AWS"}] * (BATCH_SIZE + 1))) == BATCH_SIZE + 1
    assert client.embeddings.create.call_count == 2


def test_empty_list_does_not_call_api():
    client = Mock()
    assert embed_chunks(client, []) == []
    client.embeddings.create.assert_not_called()


@pytest.mark.parametrize("result", [response(), response(1), SimpleNamespace(
    data=[SimpleNamespace(index=0, embedding=[1.0])])])
def test_reject_invalid_response(result):
    client = Mock()
    client.embeddings.create.return_value = result
    with pytest.raises(ValueError):
        embed_chunks(client, [{"text": "AWS"}])


def test_propagate_api_failure():
    client = Mock()
    client.embeddings.create.side_effect = RuntimeError("API unavailable")
    with pytest.raises(RuntimeError, match="API unavailable"):
        embed_chunks(client, [{"text": "AWS"}])


def test_embed_query_uses_document_configuration():
    from embeddings.embedding_service import embed_query

    client = Mock()
    client.embeddings.create.return_value = response(0)
    assert embed_query(client, "Quais oportunidades?") == [0.0] * DIMENSIONS
    client.embeddings.create.assert_called_once_with(
        model=MODEL, dimensions=DIMENSIONS, input=["Quais oportunidades?"], encoding_format="float")


def test_empty_query_does_not_call_api():
    from embeddings.embedding_service import embed_query

    client = Mock()
    with pytest.raises(ValueError, match="empty"):
        embed_query(client, "  ")
    client.embeddings.create.assert_not_called()
