"""Expose only benchmark routes; vLLM's other development routes stay unreachable."""

import json

ALLOWED = {
    ("GET", "/health"),
    ("GET", "/version"),
    ("GET", "/v1/models"),
    ("GET", "/metrics"),
    ("POST", "/v1/completions"),
    ("POST", "/reset_prefix_cache"),
}


class BenchmarkRoutes:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in {"http", "websocket"}:
            if (scope.get("method"), scope.get("path")) not in ALLOWED:
                if scope["type"] == "websocket":
                    await send({"type": "websocket.close", "code": 1008})
                else:
                    body = json.dumps({"detail": "Benchmark route unavailable"}).encode()
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 404,
                            "headers": [(b"content-type", b"application/json")],
                        }
                    )
                    await send({"type": "http.response.body", "body": body})
                return
        await self.app(scope, receive, send)
