"""Minimal backend that identifies itself, so load balancing is observable.

Stdlib only — no dependencies, no build stage, ~50 MB image.
"""

import json
import os
import signal
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOSTNAME = socket.gethostname()  # the container ID, unless overridden


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib naming
        if self.path == "/healthz":
            self._send(200, {"status": "ok", "replica": HOSTNAME})
        else:
            self._send(
                200,
                {
                    "app": os.getenv("APP_NAME", "backend"),
                    "replica": HOSTNAME,
                    "path": self.path,
                    "request_id": self.headers.get("X-Request-ID"),
                    "client": self.headers.get("X-Forwarded-For"),
                },
            )

    def log_message(self, fmt: str, *args) -> None:
        print(json.dumps({"replica": HOSTNAME, "msg": fmt % args}), flush=True)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8000), Handler)  # 0.0.0.0, not 127.0.0.1

    def shutdown(signum, _frame):
        print(json.dumps({"replica": HOSTNAME, "msg": f"signal {signum}, shutting down"}), flush=True)
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    print(json.dumps({"replica": HOSTNAME, "msg": "listening on :8000"}), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
