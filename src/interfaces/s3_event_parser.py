"""Parse S3 object creation notifications without accessing AWS."""

from urllib.parse import unquote_plus


def parse_s3_event(event):
    records = event.get("Records") if isinstance(event, dict) else None
    if not isinstance(records, list) or not records:
        raise ValueError("The event must contain a non-empty Records list.")

    objects = []
    for index, record in enumerate(records):
        try:
            if record["eventSource"] != "aws:s3":
                raise ValueError("The event source must be aws:s3.")
            name = record["eventName"]
            if not isinstance(name, str) or not name.startswith("ObjectCreated:"):
                raise ValueError("The event must be an object creation notification.")
            bucket = record["s3"]["bucket"]["name"]
            obj = record["s3"]["object"]
            key = obj["key"]
            if not isinstance(bucket, str) or not bucket.strip():
                raise ValueError("The bucket name must be a non-empty string.")
            if not isinstance(key, str) or not key:
                raise ValueError("The object key must be a non-empty string.")
            for field in ("versionId", "sequencer"):
                if field in obj and (not isinstance(obj[field], str) or not obj[field]):
                    raise ValueError(f"{field} must be a non-empty string.")
            objects.append({
                "bucket": bucket,
                "key": unquote_plus(key),
                "version_id": obj.get("versionId"),
                "sequencer": obj.get("sequencer"),
            })
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid S3 record at Records[{index}]: {exc}") from exc
    return objects
