"""Indexing entry point: validate S3 events, prepare documents and generate embeddings."""

import logging

import boto3
from openai import OpenAI

from embeddings.embedding_service import embed_chunks

from ingestion.chunker import chunk_document
from ingestion.loader import load_document
from ingestion.preprocessor import preprocess_text

from interfaces.s3_event_parser import parse_s3_event

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        objects = parse_s3_event(event)
    except ValueError:
        logger.exception("Invalid S3 event")
        raise

    logger.info("S3 event validated: %d object(s)", len(objects))

    s3_client = boto3.client("s3")
    try:
        documents = [load_document(s3_client, obj) for obj in objects]
        chunks = []
        for document in documents:
            document["text"] = preprocess_text(document["text"])
            chunks.extend(chunk_document(document))
    except Exception:
        logger.exception("Document ingestion, preprocessing or chunking failed")
        raise

    try:
        embedded_chunks = []
        if chunks:
            with OpenAI(timeout=20.0, max_retries=2) as client:
                embedded_chunks = embed_chunks(client, chunks)
    except Exception:
        logger.exception("Embedding generation failed")
        raise

    logger.info("Embeddings generated: %d", len(embedded_chunks))
    logger.info("Documents processed: %d; chunks created: %d", len(documents), len(chunks))

    return {
        "statusCode": 200,
        "body": "Embeddings generated; persistence not implemented yet.",
        "objects": objects,
        "documents_loaded": len(documents),
        "chunks_created": len(chunks),
        "embeddings_generated": len(embedded_chunks),
    }
