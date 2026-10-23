"""Send optional RAG question/answer notifications without breaking the chat."""

import json
import logging
import os
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


def _message_parts(text, limit=3500):
    # Telegram limits messages to 4096 characters; count UTF-16 units conservatively.
    parts = []
    start = 0
    size = 0
    for index, character in enumerate(text):
        units = 2 if ord(character) > 0xFFFF else 1
        if size + units > limit:
            parts.append(text[start:index])
            start = index
            size = 0
        size += units
    if start < len(text):
        parts.append(text[start:])
    return parts


def notify_telegram(question, answer):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return False

    text = f"Melita | Portfolio AI Assistant\n\nPergunta:\n{question}\n\nResposta:\n{answer}"
    try:
        for part in _message_parts(text):
            request = Request(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=json.dumps({
                    "chat_id": chat_id,
                    "text": part,
                    "link_preview_options": {"is_disabled": True},
                }, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=2) as response:
                if json.load(response).get("ok") is not True:
                    logger.warning("Telegram notification rejected")
                    return False
    except Exception as exc:
        # Exception messages can include the URL containing the bot token.
        logger.warning("Telegram notification failed (%s)", type(exc).__name__)
        return False

    return True
