"""Validate and normalize incoming questions; search and generation are not implemented yet."""

import json

from interfaces.question_parser import RequestValidationError, parse_question
from retrieval.query_preprocessor import preprocess_query


def lambda_handler(event, context):
    headers = {"Content-Type": "application/json"}
    try:
        question = preprocess_query(parse_question(event))
    except RequestValidationError as exc:
        if exc.status_code == 405:
            headers["Allow"] = "POST"
        return {
            "statusCode": exc.status_code,
            "headers": headers,
            "body": json.dumps({"error": str(exc)}),
        }

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({
            "message": "Question validated and normalized; search and generation not implemented yet.",
            "question": question,
        }, ensure_ascii=False),
    }
