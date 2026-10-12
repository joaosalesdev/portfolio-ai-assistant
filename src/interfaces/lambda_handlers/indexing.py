"""Indexing entry point: validate the event; ingestion is not implemented yet."""

import logging

from interfaces.s3_event_parser import parse_s3_event

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        objects = parse_s3_event(event)
    except ValueError:
        logger.exception("Invalid S3 event")
        raise

    logger.info("S3 event validated: %d object(s)", len(objects))

    return {
        "statusCode": 200,
        "body": "S3 event validated; document ingestion not implemented yet.",
        "objects": objects,
    }
