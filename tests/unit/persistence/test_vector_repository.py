"""Essential storage tests with a simulated database connection."""

from unittest.mock import MagicMock

import pytest

from persistence.vector_repository import save_document


@pytest.fixture
def storage():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (1, None)
    document = {"bucket": "test", "key": "career.md", "version_id": "v1",
                "sequencer": "0A", "text": "AWS"}
    chunk = {**document, "chunk_index": 0, "start_char": 0, "end_char": 3,
             "embedding": [0.1] * 1536, "embedding_model": "text-embedding-3-small",
             "embedding_dimensions": 1536}
    return connection, cursor, document, chunk


def test_replace_document_and_chunks_in_transaction(storage):
    connection, cursor, document, chunk = storage
    assert save_document(connection, document, [chunk]) is True
    statements = [call.args[0] for call in cursor.execute.call_args_list]
    assert "FOR UPDATE" in statements[1]
    assert "DELETE FROM portfolio_chunks" in statements[3]
    assert "INSERT INTO portfolio_chunks" in statements[4]
    assert cursor.execute.call_args.args[1][4] == "AWS"
    connection.transaction.return_value.__exit__.assert_called_once_with(None, None, None)


@pytest.mark.parametrize("previous", ["A", "000B"])
def test_skip_duplicate_or_older_event(storage, previous):
    connection, cursor, document, chunk = storage
    cursor.fetchone.return_value = (1, previous)
    assert save_document(connection, document, [chunk]) is False
    assert cursor.execute.call_count == 2


def test_failure_exits_transaction_with_error(storage):
    connection, cursor, document, chunk = storage
    cursor.execute.side_effect = [None, None, None, None, RuntimeError("Insert failed")]
    with pytest.raises(RuntimeError, match="Insert failed"):
        save_document(connection, document, [chunk])
    assert connection.transaction.return_value.__exit__.call_args.args[0] is RuntimeError


def test_reject_wrong_source(storage):
    connection, cursor, document, chunk = storage
    chunk["key"] = "other.md"
    with pytest.raises(ValueError, match="source"):
        save_document(connection, document, [chunk])
