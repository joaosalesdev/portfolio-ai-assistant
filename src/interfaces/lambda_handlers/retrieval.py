"""Validate, normalize and embed incoming questions; search and generation are not implemented yet."""

import json
import logging

from openai import OpenAI

from embeddings.embedding_service import DIMENSIONS, MODEL, embed_query

from interfaces.question_parser import RequestValidationError, parse_question
from retrieval.query_preprocessor import preprocess_query


logger = logging.getLogger(__name__)


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

    try:
        with OpenAI(timeout=20.0, max_retries=2) as client:
            vector = embed_query(client, question)
    except Exception:
        logger.exception("Query embedding generation failed")
        return {
            "statusCode": 502,
            "headers": headers,
            "body": json.dumps({"error": "Unable to generate the question embedding."}),
        }

    logger.info("Query embedding generated: %d dimensions", len(vector))
    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({
            "message": "Question embedding generated; search and generation not implemented yet.",
            "question": question,
            "embedding_model": MODEL,
            "embedding_dimensions": DIMENSIONS,
        }, ensure_ascii=False),
    }
