"""Invoke both local Lambda containers to check packaging and handler loading."""

import json
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


def invoke(port, event, expected_error=None):
    request = Request(
        f"http://127.0.0.1:{port}/2015-03-31/functions/function/invocations",
        data=json.dumps(event).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(30):
        try:
            with urlopen(request, timeout=5) as response:
                payload = json.load(response)
            if expected_error:
                if payload.get("errorType") != expected_error:
                    raise RuntimeError(f"Unexpected handler error on port {port}: {payload}")
                return
            if payload.get("statusCode") != 200 or not payload.get("body"):
                raise RuntimeError(f"Handler failed on port {port}: {payload}")
            return
        except (URLError, TimeoutError):
            if attempt == 29:
                raise
            time.sleep(1)


if __name__ == "__main__":
    for component, port in (("indexing", 9000), ("retrieval", 9001)):
        # Invalid indexing input exercises handler loading without calling AWS.
        event = {}
        if component == "retrieval":
            path = Path(__file__).resolve().parents[1] / "tests/events/retrieval/post_question.json"
            event = json.loads(path.read_text(encoding="utf-8"))
        invoke(port, event, expected_error="ValueError" if component == "indexing" else None)
        print(f"{component}: container invocation passed")
