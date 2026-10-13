"""Indexing entry point: validate S3 events and load documents."""

import logging

import boto3

from ingestion.loader import load_document

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
        print("line 25") 
    except Exception:
        logger.exception("Document ingestion failed")
        raise

    logger.info("Documents loaded: %d", len(documents))

    return {
        "statusCode": 200,
        "body": "Documents loaded; preprocessing and indexing not implemented yet.",
        "objects": objects,
        "documents_loaded": len(documents),
    }
