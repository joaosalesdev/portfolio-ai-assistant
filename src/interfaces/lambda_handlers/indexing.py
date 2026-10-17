"""Indexing entry point: validate S3 events, prepare documents, generate embeddings and persist them."""

import logging
import os

import psycopg

import boto3
from openai import OpenAI

from embeddings.embedding_service import embed_chunks

from ingestion.chunker import chunk_document
from ingestion.loader import load_document
from ingestion.preprocessor import preprocess_text

from interfaces.s3_event_parser import parse_s3_event
from persistence.vector_repository import save_document

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
        unique_objects = {tuple(obj.items()): obj for obj in objects}
        documents = [load_document(s3_client, obj) for obj in unique_objects.values()]
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

    try:
        saved = 0
        with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True, connect_timeout=10) as connection:
            for document in documents:
                document_chunks = [chunk for chunk in embedded_chunks if all(
                    chunk.get(key) == document.get(key)
                    for key in ("bucket", "key", "version_id", "sequencer")
                )]
                saved += save_document(connection, document, document_chunks)
    except Exception:
        logger.exception("Vector storage failed")
        raise

    logger.info("Documents saved: %d", saved)
    logger.info("Embeddings generated: %d", len(embedded_chunks))
    logger.info("Documents processed: %d; chunks created: %d", len(documents), len(chunks))

    return {
        "statusCode": 200,
        "body": "Indexing completed.",
        "objects": objects,
        "documents_loaded": len(documents),
        "chunks_created": len(chunks),
        "embeddings_generated": len(embedded_chunks),
        "documents_saved": saved,
        "documents_skipped": len(documents) - saved,
    }
