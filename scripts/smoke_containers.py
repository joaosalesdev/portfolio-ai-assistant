"""Invoke both local Lambda containers to check packaging and handler loading."""

import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


def invoke(port):
    request = Request(
        f"http://127.0.0.1:{port}/2015-03-31/functions/function/invocations",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(30):
        try:
            with urlopen(request, timeout=5) as response:
                payload = json.load(response)
            if payload.get("statusCode") != 200 or not payload.get("body"):
                raise RuntimeError(f"Handler failed on port {port}: {payload}")
            return
        except (URLError, TimeoutError):
            if attempt == 29:
                raise
            time.sleep(1)


if __name__ == "__main__":
    for component, port in (("indexing", 9000), ("retrieval", 9001)):
        invoke(port)
        print(f"{component}: container invocation passed")
