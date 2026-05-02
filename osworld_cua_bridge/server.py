from __future__ import annotations

import contextlib
import json
import logging
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from osworld_cua_bridge.executor import CuaBridgeExecutor


logger = logging.getLogger("desktopenv.cua_bridge")


def find_free_port(host: str = "127.0.0.1") -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


class BridgeServer:
    def __init__(self, executor: CuaBridgeExecutor, host: str = "127.0.0.1", port: int = 0):
        self.executor = executor
        self.host = host
        self.port = port or find_free_port(host)
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def start(self) -> None:
        if self._server is not None:
            return
        handler = self._build_handler()
        self._server = ThreadingHTTPServer((self.host, self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, name="cua-bridge-server", daemon=True)
        self._thread.start()
        self._wait_until_ready()
        logger.info("CUA bridge server started at %s", self.url)

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("CUA bridge server stopped")

    def _build_handler(self) -> type[BaseHTTPRequestHandler]:
        executor = self.executor

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path != "/health":
                    self._send_json(404, {"ok": False, "error": {"code": "NOT_FOUND", "message": self.path}})
                    return
                self._send_json(200, executor.health())

            def do_POST(self) -> None:
                if self.path != "/invoke":
                    self._send_json(404, {"ok": False, "error": {"code": "NOT_FOUND", "message": self.path}})
                    return

                content_length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(content_length) if content_length > 0 else b"{}"
                try:
                    payload = json.loads(body.decode("utf-8")) if body else {}
                except json.JSONDecodeError:
                    payload = {}
                if not isinstance(payload, dict):
                    payload = {}
                response = executor.handle_payload(payload)
                self._send_json(200 if response.get("ok") else 400, response)

            def log_message(self, fmt: str, *args: Any) -> None:
                logger.debug("CUA bridge HTTP: " + fmt, *args)

            def _send_json(self, status: int, payload: dict[str, Any]) -> None:
                data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        return Handler

    def _wait_until_ready(self) -> None:
        deadline = time.time() + 5
        while time.time() < deadline:
            if self._server is not None:
                return
            time.sleep(0.05)
        raise RuntimeError("CUA bridge server did not start")
