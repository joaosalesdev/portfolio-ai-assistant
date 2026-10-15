"""Essential ingestion tests without AWS calls."""

from io import BytesIO
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

from ingestion.loader import load_document
from ingestion.preprocessor import preprocess_text
from interfaces.lambda_handlers.indexing import lambda_handler


@pytest.fixture
def obj():
    return {"bucket": "test-bucket", "key": "documents/career.md",
            "version_id": "v1", "sequencer": "123"}


def test_load_versioned_document(obj):
    body = BytesIO("Experiência AWS".encode("utf-8"))
    client = Mock()
    client.get_object.return_value = {"Body": body}

    document = load_document(client, obj)

    assert document == {**obj, "text": "Experiência AWS"}
    client.get_object.assert_called_once_with(
        Bucket="test-bucket", Key="documents/career.md", VersionId="v1")
    assert body.closed


def test_load_without_version(obj):
    obj["version_id"] = None
    obj["key"] = "documents/career.txt"
    client = Mock()
    client.get_object.return_value = {"Body": BytesIO(b"Career")}

    assert load_document(client, obj)["text"] == "Career"
    client.get_object.assert_called_once_with(Bucket="test-bucket", Key="documents/career.txt")


def test_unsupported_format(obj):
    obj["key"] = "documents/career.pdf"
    client = Mock()

    with pytest.raises(ValueError, match="supported"):
        load_document(client, obj)
    client.get_object.assert_not_called()


@pytest.mark.parametrize("content, error", [(b"  ", ValueError), (b"\xff", UnicodeDecodeError)])
def test_invalid_content(obj, content, error):
    body = BytesIO(content)
    client = Mock()
    client.get_object.return_value = {"Body": body}

    with pytest.raises(error):
        load_document(client, obj)
    assert body.closed


def test_handler_loads_each_document(monkeypatch):
    client = Mock()
    client.get_object.side_effect = [
        {"Body": BytesIO(b"First")}, {"Body": BytesIO(b"Second")},
    ]
    monkeypatch.setattr("interfaces.lambda_handlers.indexing.boto3.client", lambda service: client)
    record = {"eventSource": "aws:s3", "eventName": "ObjectCreated:Put",
              "s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "documents/career.md"}}}

    preprocessor = Mock(wraps=preprocess_text)
    monkeypatch.setattr("interfaces.lambda_handlers.indexing.preprocess_text", preprocessor)

    result = lambda_handler({"Records": [record, record]}, None)

    assert preprocessor.call_count == 2
    assert result["documents_loaded"] == 2
    assert client.get_object.call_count == 2
    assert "text" not in result["objects"][0]


def test_handler_propagates_s3_failure(monkeypatch):
    client = Mock()
    client.get_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}, "GetObject")
    monkeypatch.setattr("interfaces.lambda_handlers.indexing.boto3.client", lambda service: client)
    record = {"eventSource": "aws:s3", "eventName": "ObjectCreated:Put",
              "s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "documents/career.md"}}}

    with pytest.raises(ClientError):
        lambda_handler({"Records": [record]}, None)
