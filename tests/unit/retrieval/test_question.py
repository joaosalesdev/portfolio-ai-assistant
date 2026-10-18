"""Essential question validation tests without external services."""

import base64
import json
from unittest.mock import MagicMock
from pathlib import Path

import pytest

from interfaces.lambda_handlers.retrieval import lambda_handler


@pytest.fixture(autouse=True)
def openai_client(monkeypatch):
    from types import SimpleNamespace

    factory = MagicMock()
    client = factory.return_value.__enter__.return_value
    client.embeddings.create.return_value = SimpleNamespace(
        data=[SimpleNamespace(index=0, embedding=[0.1] * 1536)])
    client.responses.create.return_value = SimpleNamespace(
        status="completed", output_text="João procura Backend e Cloud [S1].")
    monkeypatch.setattr("interfaces.lambda_handlers.retrieval.OpenAI", factory)
    return factory


@pytest.fixture(autouse=True)
def database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    factory = MagicMock()
    monkeypatch.setattr("interfaces.lambda_handlers.retrieval.psycopg.connect", factory)
    retriever = MagicMock(return_value=[])
    monkeypatch.setattr("interfaces.lambda_handlers.retrieval.retrieve_chunks", retriever)
    return factory, retriever


@pytest.fixture
def event():
    path = Path(__file__).resolve().parents[2] / "events/retrieval/post_question.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_valid_question(event, openai_client):
    event["body"] = json.dumps({"question": "  Quais  oportunidades\nJoão\tprocura?  "})
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["question"] == "Quais oportunidades João procura?"
    body = json.loads(response["body"])
    assert body["embedding_dimensions"] == 1536
    assert "embedding" not in body
    assert body["context"] == ""
    assert body["has_context"] is False
    assert body["generation_skipped"] is True
    assert body["generation_model"] is None
    openai_client.return_value.__enter__.return_value.responses.create.assert_not_called()
    client = openai_client.return_value.__enter__.return_value
    assert client.embeddings.create.call_args.kwargs["input"] == ["Quais oportunidades João procura?"]
    assert response["headers"]["Content-Type"] == "application/json"


def test_base64_question(event):
    question = json.loads(event["body"])["question"]
    event["body"] = base64.b64encode(event["body"].encode()).decode()
    event["isBase64Encoded"] = True
    assert json.loads(lambda_handler(event, None)["body"])["question"] == question


@pytest.mark.parametrize("body", ['{', '[]', '{}', '{"question": 1}', '{"question": "  "}'])
def test_invalid_body(event, body, openai_client):
    event["body"] = body
    assert lambda_handler(event, None)["statusCode"] == 400
    openai_client.assert_not_called()


def test_question_length_limit(event):
    event["body"] = json.dumps({"question": "a" * 2000})
    assert lambda_handler(event, None)["statusCode"] == 200
    event["body"] = json.dumps({"question": "a" * 2001})
    assert lambda_handler(event, None)["statusCode"] == 400


def test_reject_get(event):
    event["requestContext"]["http"]["method"] = "GET"
    response = lambda_handler(event, None)
    assert response["statusCode"] == 405
    assert response["headers"]["Allow"] == "POST"


def test_malformed_event():
    assert lambda_handler({}, None)["statusCode"] == 400


def test_invalid_base64(event):
    event.update(body="%%%", isBase64Encoded=True)
    assert lambda_handler(event, None)["statusCode"] == 400


def test_oversized_body(event):
    event["body"] = " " * 16385
    assert lambda_handler(event, None)["statusCode"] == 413


def test_embedding_failure(event, openai_client):
    client = openai_client.return_value.__enter__.return_value
    client.embeddings.create.side_effect = RuntimeError("Private provider details")
    response = lambda_handler(event, None)
    assert response["statusCode"] == 502
    assert "Private provider details" not in response["body"]


def test_search_results(event, database):
    factory, retriever = database
    retriever.return_value = [{"source": "documents/career_goals.md", "text": "Backend e Cloud", "distance": 0.2}]
    response = lambda_handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["matches_count"] == 1
    assert body["context"] == "[S1]\nBackend e Cloud"
    assert body["sources"][0]["id"] == "S1"
    assert body["sources_count"] == 1
    assert body["has_context"] is True
    assert body["generation_model"] == "gpt-6-luna"
    assert body["answer"] == "João procura Backend e Cloud [S1]."
    assert body["matches"][0]["source"] == "documents/career_goals.md"
    assert len(retriever.call_args.args[1]) == 1536


def test_database_failure(event, database):
    factory, retriever = database
    factory.side_effect = RuntimeError("Private database details")
    response = lambda_handler(event, None)
    assert response["statusCode"] == 503
    assert "Private database details" not in response["body"]


def test_generation_failure(event, database, openai_client):
    database[1].return_value = [{"source": "career.md", "text": "Backend"}]
    client = openai_client.return_value.__enter__.return_value
    client.responses.create.side_effect = RuntimeError("Private provider details")
    response = lambda_handler(event, None)
    assert response["statusCode"] == 502
    assert "Private provider details" not in response["body"]
