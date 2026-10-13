"""Load Markdown and plain-text documents from S3."""

from pathlib import PurePosixPath


def load_document(s3_client, obj):
    if PurePosixPath(obj["key"]).suffix.lower() not in {".md", ".txt"}:
        raise ValueError("Only .md and .txt documents are supported.")

    request = {"Bucket": obj["bucket"], "Key": obj["key"]}
    if obj.get("version_id") is not None:
        request["VersionId"] = obj["version_id"]

    body = s3_client.get_object(**request)["Body"]
    try:
        text = body.read().decode("utf-8")
    finally:
        body.close()

    if not text.strip():
        raise ValueError("The document must not be empty.")

    return {**obj, "text": text}
