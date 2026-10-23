"""Telegram notifications tested without sending real messages."""

import json
from unittest.mock import MagicMock

import pytest

from notifications.telegram import _message_parts, notify_telegram


@pytest.fixture
def transport(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    opener = MagicMock()
    opener.return_value.__enter__.return_value.read.return_value = b'{"ok": true}'
    monkeypatch.setattr("notifications.telegram.urlopen", opener)
    return opener


def test_send_question_and_answer_as_plain_text(transport):
    assert notify_telegram("Experiência?", "AWS [S1].") is True
    request = transport.call_args.args[0]
    payload = json.loads(request.data)
    assert payload["chat_id"] == "123"
    assert "Experiência?" in payload["text"] and "AWS [S1]." in payload["text"]
    assert "parse_mode" not in payload
    assert transport.call_args.kwargs["timeout"] == 2


def test_missing_config_skips_request(transport, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN")
    assert notify_telegram("Question", "Answer") is False
    transport.assert_not_called()


def test_long_unicode_message_is_split_without_losing_content(transport):
    text = "😀" * 4000
    parts = _message_parts(text)
    assert "".join(parts) == text
    assert all(len(part.encode("utf-16-le")) // 2 <= 3500 for part in parts)
    assert notify_telegram("Question", text) is True
    assert transport.call_count > 1


def test_failure_does_not_expose_token(transport, caplog):
    transport.side_effect = OSError("https://api.telegram.org/bottest-token/sendMessage")
    assert notify_telegram("Private question", "Private answer") is False
    assert "test-token" not in caplog.text
    assert "Private question" not in caplog.text


def test_api_rejection(transport):
    transport.return_value.__enter__.return_value.read.return_value = b'{"ok": false}'
    assert notify_telegram("Question", "Answer") is False
