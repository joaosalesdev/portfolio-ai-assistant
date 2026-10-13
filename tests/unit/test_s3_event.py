"""Local tests for S3 event handling without external services."""

import copy
import json
from pathlib import Path

import pytest

from interfaces.s3_event_parser import parse_s3_event


@pytest.fixture
def s3_event():
    path = Path(__file__).resolve().parents[1] / "events/indexing/s3_object_created.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_real_event_preserves_object_identity(s3_event):
    assert parse_s3_event(s3_event) == [{
        "bucket": "portfolio-ai-assistant-documents-338034595477-us-east-1",
        "key": "documents/career_goals.md",
        "version_id": "cOjYVMxhB81cpYXJrZXLlt3AGeLOykXv",
        "sequencer": "006ACC0B4C50421DFB",
    }]


def test_multiple_records_and_url_encoded_key(s3_event):
    record = copy.deepcopy(s3_event["Records"][0])
    record["s3"]["object"] = {"key": "documents/experi%C3%AAncia+AWS%2BIA.md"}
    s3_event["Records"].append(record)

    objects = parse_s3_event(s3_event)

    assert len(objects) == 2
    assert objects[1]["key"] == "documents/experiência AWS+IA.md"
    assert objects[1]["version_id"] is None
    assert objects[1]["sequencer"] is None


def test_missing_records():
    with pytest.raises(ValueError, match="Records"):
        parse_s3_event({})


def test_unsupported_event(s3_event):
    s3_event["Records"][0]["eventName"] = "ObjectRemoved:Delete"

    with pytest.raises(ValueError, match="object creation"):
        parse_s3_event(s3_event)


def test_missing_object_key(s3_event):
    del s3_event["Records"][0]["s3"]["object"]["key"]

    with pytest.raises(ValueError, match="Invalid S3 record"):
        parse_s3_event(s3_event)
