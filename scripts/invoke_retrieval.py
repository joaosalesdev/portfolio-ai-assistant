"""Invoke the retrieval handler locally using the POST event fixture."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from interfaces.lambda_handlers.retrieval import lambda_handler


if __name__ == "__main__":
    path = ROOT / "tests/events/retrieval/post_question.json"
    event = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(lambda_handler(event, None), ensure_ascii=False, indent=2))
