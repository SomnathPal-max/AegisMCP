"""
mcp-streamable-crisis-kit — Reusable toolkit for Streamable HTTP MCP crisis servers.
"""

from __future__ import annotations

import collections
import datetime
import re
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


ALLOWED_ORIGIN_REGEX = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$")
GLOBAL_WIRE_LOG: collections.deque[dict[str, Any]] = collections.deque(maxlen=200)


class LocalhostOriginGuard(BaseHTTPMiddleware):
    """
    Middleware that enforces local-only origin validation per MCP 2025-11-25.
    Blocks DNS-rebinding attacks by rejecting non-localhost origins with HTTP 403.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        origin = request.headers.get("origin")
        if origin and not ALLOWED_ORIGIN_REGEX.match(origin):
            return JSONResponse(
                {"error": "origin not allowed by crisis kit guard", "origin": origin},
                status_code=403,
            )
        return await call_next(request)


class MemoryWireLog(BaseHTTPMiddleware):
    """
    Non-intrusive metadata logger capturing HTTP method, path, status, and Mcp-Session-Id.
    Strictly avoids logging request bodies or sensitive tokens.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        GLOBAL_WIRE_LOG.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "http_method": request.method,
            "path": str(request.url.path),
            "status": response.status_code,
            "origin": request.headers.get("origin"),
            "mcp_session_id": (
                request.headers.get("mcp-session-id")
                or response.headers.get("mcp-session-id")
            ),
        })
        return response


__all__ = ["LocalhostOriginGuard", "MemoryWireLog", "GLOBAL_WIRE_LOG"]
