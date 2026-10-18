"""Essential vector search tests with a simulated database."""

from unittest.mock import MagicMock

import pytest

from retrieval.retriever import retrieve_chunks


def test_search_filters_orders_and_limits():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [{"source": "documents/career_goals.md", "distance": 0.2}]

    matches = retrieve_chunks(connection, [0.1] * 1536, top_k=3)

    query, parameters = cursor.execute.call_args.args
    assert "<=>" in query
    assert "embedding_model = %s" in query
    assert "embedding_dimensions = %s" in query
    assert "ORDER BY distance ASC" in query
    assert parameters[1:] == ("text-embedding-3-small", 1536, 3)
    assert matches == cursor.fetchall.return_value


def test_empty_base():
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.fetchall.return_value = []
    assert retrieve_chunks(connection, [0.1] * 1536) == []


def test_invalid_top_k():
    connection = MagicMock()
    with pytest.raises(ValueError, match="top_k"):
        retrieve_chunks(connection, [0.1] * 1536, top_k=0)
    connection.cursor.assert_not_called()


@pytest.mark.parametrize("vector", [[0.1], [0.0] * 1536, [float("nan")] * 1536])
def test_invalid_vector(vector):
    connection = MagicMock()
    with pytest.raises(ValueError):
        retrieve_chunks(connection, vector)
    connection.cursor.assert_not_called()
