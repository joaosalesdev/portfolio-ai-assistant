"""Answer portfolio questions using retrieved document context."""

import json
import logging
import os

import psycopg

from openai import OpenAI

from embeddings.embedding_service import DIMENSIONS, MODEL, embed_query
from generation.generator import generate_answer

from interfaces.question_parser import RequestValidationError, parse_question
from retrieval.context_selector import select_context
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

    selected = select_context(matches)
    try:
        if selected["context"]:
            with OpenAI(timeout=30.0, max_retries=0) as client:
                generated = generate_answer(client, question, selected["context"])
        else:
            generated = generate_answer(None, question, selected["context"])
    except Exception:
        logger.exception("Response generation failed")
        return {
            "statusCode": 502,
            "headers": headers,
            "body": json.dumps({"error": "Unable to generate an answer."}),
        }

    logger.info("Response generated; skipped: %s", generated["generation_skipped"])
    logger.info("Context sources selected: %d; characters: %d",
                len(selected["sources"]), len(selected["context"]))
    logger.info("Chunks retrieved: %d", len(matches))
    logger.info("Query embedding generated: %d dimensions", len(vector))
    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({
            "message": "Request processed.",
            **generated,
            "question": question,
            "embedding_model": MODEL,
            "embedding_dimensions": DIMENSIONS,
            "matches": matches,
            "matches_count": len(matches),
            "context": selected["context"],
            "sources": selected["sources"],
            "sources_count": len(selected["sources"]),
            "has_context": bool(selected["sources"]),
        }, ensure_ascii=False),
    }
