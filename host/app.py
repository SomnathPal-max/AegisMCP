"""
AegisMCP Host Backend — app.py

FastAPI backend that acts as a real MCP client, connecting to the AegisMCP
server over Streamable HTTP.  This file does NOT import anything from the
server package — all communication goes through the MCP protocol wire.

Serves the Alexa+ simulator UI and proxies tool calls / resource reads.
"""

from __future__ import annotations

import json
import os
import traceback
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AegisMCP Host — Simulated Alexa+", version="1.0.0")

# Allow the UI (served on same host) to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_URL = os.getenv("AEGIS_MCP_URL", "http://127.0.0.1:8000/mcp")
MCP_WIRE_URL = os.getenv("AEGIS_WIRE_URL", "http://127.0.0.1:8000/debug/wire")
HOST_PORT = int(os.getenv("AEGIS_HOST_PORT", "8080"))

# MCP session tracking
_session_id: str | None = None
_request_id: int = 0


def _next_id() -> int:
    global _request_id
    _request_id += 1
    return _request_id


async def _mcp_call(method: str, params: dict | None = None) -> dict:
    """Send a JSON-RPC request to the MCP server and return the result."""
    global _session_id

    payload = {
        "jsonrpc": "2.0",
        "id": _next_id(),
        "method": method,
    }
    if params:
        payload["params"] = params

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Origin": f"http://localhost:{HOST_PORT}",
    }
    if _session_id:
        headers["Mcp-Session-Id"] = _session_id

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(MCP_URL, json=payload, headers=headers)

        # Capture session ID from response
        if "mcp-session-id" in resp.headers:
            _session_id = resp.headers["mcp-session-id"]

        if resp.status_code != 200:
            return {"error": f"MCP server returned {resp.status_code}", "body": resp.text}

        # Handle SSE responses
        content_type = resp.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            # Parse SSE — collect all data events
            lines = resp.text.strip().split("\n")
            last_data = None
            for line in lines:
                if line.startswith("data: "):
                    last_data = line[6:]
            if last_data:
                try:
                    return json.loads(last_data)
                except json.JSONDecodeError:
                    return {"raw_sse": resp.text}
            return {"raw_sse": resp.text}

        return resp.json()


async def _ensure_initialized():
    """Send initialize + initialized notification if not yet done."""
    global _session_id
    if _session_id:
        return

    # Initialize
    result = await _mcp_call("initialize", {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "AegisMCP-AlexaPlus-Host", "version": "1.0.0"},
    })

    # Send initialized notification
    await _mcp_call("notifications/initialized")

    return result


# ---------------------------------------------------------------------------
# API endpoints for the UI
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the Alexa+ simulator UI."""
    ui_path = Path(__file__).resolve().parent.parent / "ui" / "index.html"
    if not ui_path.exists():
        return HTMLResponse("<h1>UI not found</h1>", status_code=404)
    return HTMLResponse(ui_path.read_text(encoding="utf-8"))


@app.post("/chat")
async def chat(request: Request):
    """
    Handle a chat/action from the UI.  Routes to the appropriate MCP tool.
    Expected JSON body:
    {
        "action": "scam_check" | "emergency" | "compile_claim" | "reset",
        "params": { ... tool parameters ... }
    }
    """
    try:
        await _ensure_initialized()
        body = await request.json()
        action = body.get("action", "")
        params = body.get("params", {})

        tool_map = {
            "scam_check": "analyze_live_scam_call",
            "emergency": "arbitrate_home_emergency",
            "compile_claim": "compile_forensic_claim",
            "reset": "reset_demo",
        }

        tool_name = tool_map.get(action)
        if not tool_name:
            return JSONResponse({
                "error": f"Unknown action: {action}",
                "available": list(tool_map.keys()),
            }, status_code=400)

        result = await _mcp_call("tools/call", {
            "name": tool_name,
            "arguments": params,
        })

        return JSONResponse({
            "action": action,
            "tool": tool_name,
            "mcp_session_id": _session_id,
            "result": result,
        })

    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "traceback": traceback.format_exc(),
        }, status_code=500)


@app.get("/wire")
async def get_wire():
    """Proxy the wire log from the MCP server."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(MCP_WIRE_URL)
            return JSONResponse(resp.json())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/resource")
async def read_resource(request: Request):
    """Read an MCP resource by URI."""
    try:
        await _ensure_initialized()
        body = await request.json()
        uri = body.get("uri", "")

        result = await _mcp_call("resources/read", {"uri": uri})
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    try:
        await _ensure_initialized()
        result = await _mcp_call("tools/list")
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/reset")
async def reset():
    """Reset the demo state."""
    try:
        await _ensure_initialized()
        result = await _mcp_call("tools/call", {
            "name": "reset_demo",
            "arguments": {},
        })
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "host.app:app",
        host="127.0.0.1",
        port=HOST_PORT,
        reload=False,
    )
