"""Essential question validation tests without external services."""

import base64
import json
from pathlib import Path

import pytest

from interfaces.lambda_handlers.retrieval import lambda_handler


@pytest.fixture
def event():
    path = Path(__file__).resolve().parents[2] / "events/retrieval/post_question.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_valid_question(event):
    event["body"] = json.dumps({"question": "  Quais oportunidades João procura?  "})
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["question"] == "Quais oportunidades João procura?"
    assert response["headers"]["Content-Type"] == "application/json"


def test_base64_question(event):
    question = json.loads(event["body"])["question"]
    event["body"] = base64.b64encode(event["body"].encode()).decode()
    event["isBase64Encoded"] = True
    assert json.loads(lambda_handler(event, None)["body"])["question"] == question


@pytest.mark.parametrize("body", ['{', '[]', '{}', '{"question": 1}', '{"question": "  "}'])
def test_invalid_body(event, body):
    event["body"] = body
    assert lambda_handler(event, None)["statusCode"] == 400


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
