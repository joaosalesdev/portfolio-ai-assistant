"""Validate, normalize and embed questions and retrieve chunks; generation is not implemented yet."""

import json
import logging
import os

import psycopg

from openai import OpenAI

from embeddings.embedding_service import DIMENSIONS, MODEL, embed_query

from interfaces.question_parser import RequestValidationError, parse_question
from retrieval.query_preprocessor import preprocess_query
from retrieval.retriever import retrieve_chunks


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

    try:
        with psycopg.connect(
            os.environ["DATABASE_URL"], connect_timeout=10,
            options="-c default_transaction_read_only=on -c statement_timeout=10000",
        ) as connection:
            matches = retrieve_chunks(connection, vector)
    except Exception:
        logger.exception("Vector search failed")
        return {
            "statusCode": 503,
            "headers": headers,
            "body": json.dumps({"error": "Unable to search the document base."}),
        }

    logger.info("Chunks retrieved: %d", len(matches))
    logger.info("Query embedding generated: %d dimensions", len(vector))
    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({
            "message": "Chunks retrieved; response generation not implemented yet.",
            "question": question,
            "embedding_model": MODEL,
            "embedding_dimensions": DIMENSIONS,
            "matches": matches,
            "matches_count": len(matches),
        }, ensure_ascii=False),
    }
