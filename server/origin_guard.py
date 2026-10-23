"""
AegisMCP Origin Guard — origin_guard.py

Starlette middleware for:
1. Origin validation (DNS-rebinding protection per MCP spec 2025-11-25):
   - Allow localhost / 127.0.0.1 on any port
   - Allow requests with no Origin header (non-browser clients like curl)
   - Reject all other origins with 403
2. Wire logging — captures HTTP metadata for the debug wire panel.
"""

from __future__ import annotations

import collections
import datetime
import re
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


# Allowed origins: localhost or 127.0.0.1 on any port
ALLOWED_ORIGIN = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$")

# Wire log ring buffer — most recent 200 entries, served at /debug/wire
WIRE_RING: collections.deque[dict[str, Any]] = collections.deque(maxlen=200)


class OriginGuard(BaseHTTPMiddleware):
    """Reject requests whose Origin header doesn't match localhost."""

    async def dispatch(self, request: Request, call_next) -> Response:
        origin = request.headers.get("origin")
        if origin and not ALLOWED_ORIGIN.match(origin):
            return JSONResponse(
                {"error": "origin not allowed", "origin": origin},
                status_code=403,
            )
        return await call_next(request)


class WireLog(BaseHTTPMiddleware):
    """
    Log HTTP metadata to the wire ring buffer after each request.

    Captures: timestamp, method, path, status, MCP session ID, content-type.
    Does NOT log request/response bodies or secrets.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "http_method": request.method,
            "path": str(request.url.path),
            "query": str(request.url.query) if request.url.query else None,
            "status": response.status_code,
            "origin": request.headers.get("origin"),
            "mcp_session_id": (
                request.headers.get("mcp-session-id")
                or response.headers.get("mcp-session-id")
            ),
            "content_type": response.headers.get("content-type"),
            "accept": request.headers.get("accept"),
        }
        WIRE_RING.append(entry)
        return response
