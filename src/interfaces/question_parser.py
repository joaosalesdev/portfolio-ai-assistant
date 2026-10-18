"""Validate a JSON question received through a Lambda Function URL."""

import base64
import binascii
import json

MAX_QUESTION_CHARS = 2000
MAX_BODY_BYTES = 16384


class RequestValidationError(ValueError):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


def parse_question(event):
    if not isinstance(event, dict):
        raise RequestValidationError("Invalid request event.")
    try:
        method = event["requestContext"]["http"]["method"]
    except (KeyError, TypeError):
        raise RequestValidationError("Missing HTTP request context.") from None
    if method != "POST":
        raise RequestValidationError("Only POST requests are supported.", 405)

    body = event.get("body")
    if not isinstance(body, str) or not body:
        raise RequestValidationError("A JSON request body is required.")
    # Allow base64 overhead while bounding decoding and JSON parsing.
    if len(body.encode("utf-8")) > MAX_BODY_BYTES * 4 // 3 + 4:
        raise RequestValidationError("Request body is too large.", 413)
    encoded = event.get("isBase64Encoded", False)
    if not isinstance(encoded, bool):
        raise RequestValidationError("isBase64Encoded must be a boolean.")
    try:
        raw = base64.b64decode(body, validate=True) if encoded else body.encode("utf-8")
    except (binascii.Error, ValueError, UnicodeError):
        raise RequestValidationError("Request body must contain valid base64.") from None
    if len(raw) > MAX_BODY_BYTES:
        raise RequestValidationError("Request body is too large.", 413)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise RequestValidationError("Request body must contain valid UTF-8 JSON.") from None

    question = payload.get("question") if isinstance(payload, dict) else None
    if not isinstance(question, str) or not question.strip():
        raise RequestValidationError("question must be a non-empty string.")
    question = question.strip()
    if len(question) > MAX_QUESTION_CHARS:
        raise RequestValidationError(f"question must not exceed {MAX_QUESTION_CHARS} characters.")
    return question
