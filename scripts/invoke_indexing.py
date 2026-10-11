"""Executa o handler de indexing localmente com o evento de exemplo."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from interfaces.lambda_handlers.indexing import lambda_handler

if __name__ == "__main__":
    with (ROOT / "tests/events/indexing/s3_object_created.json").open(encoding="utf-8") as file:
        event = json.load(file)

    print(lambda_handler(event, None))
