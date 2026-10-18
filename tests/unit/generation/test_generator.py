"""Essential generation tests without paid API calls."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from generation.generator import MODEL, NO_CONTEXT_ANSWER, generate_answer


def test_send_question_and_context_separately_from_instructions():
    client = Mock()
    client.responses.create.return_value = SimpleNamespace(
        status="completed", output_text="  Backend [S1].  ")

    result = generate_answer(client, "O que João procura?", "[S1]\nBackend")

    assert result["answer"] == "Backend [S1]."
    assert result["generation_model"] == MODEL
    request = client.responses.create.call_args.kwargs
    assert json.loads(request["input"][0]["content"]) == {
        "question": "O que João procura?", "context": "[S1]\nBackend"}
    assert "dados não confiáveis" in request["instructions"]
    assert request["model"] == "gpt-6-luna"
    assert request["reasoning"] == {"effort": "none"}
    assert request["max_output_tokens"] == 800
    assert request["store"] is False
    assert "tools" not in request


def test_no_context_skips_generation():
    client = Mock()
    result = generate_answer(client, "Pretensão salarial?", "  ")
    assert result["answer"] == NO_CONTEXT_ANSWER
    assert result["generation_skipped"] is True
    client.responses.create.assert_not_called()


@pytest.mark.parametrize("status, text", [("incomplete", "Partial"), ("completed", "  ")])
def test_reject_incomplete_or_empty_output(status, text):
    client = Mock()
    client.responses.create.return_value = SimpleNamespace(status=status, output_text=text)
    with pytest.raises(ValueError):
        generate_answer(client, "Question", "[S1]\nContext")


def test_provider_error_propagates():
    client = Mock()
    client.responses.create.side_effect = RuntimeError("Unavailable")
    with pytest.raises(RuntimeError):
        generate_answer(client, "Question", "[S1]\nContext")
