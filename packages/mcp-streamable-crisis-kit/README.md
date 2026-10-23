# mcp-streamable-crisis-kit

Reusable Python utilities for building secure, origin-guarded MCP servers over Streamable HTTP (Spec 2025-11-25) with crisis-containment state machines and forensic claim preparation.

## Features
- **Origin Guard Middleware**: Strict DNS-rebinding protection for `/mcp` endpoints.
- **Wire Logger**: In-memory FIFO ring buffer logging HTTP metadata without leaking sensitive tokens or message payloads.
- **Crisis State Store**: Thread-safe reversible IoT hazard isolation patterns.

## Installation
```bash
pip install mcp-streamable-crisis-kit
```

## Usage
```python
from fastmcp import FastMCP
from starlette.middleware import Middleware
from crisis_kit import LocalhostOriginGuard, MemoryWireLog

mcp = FastMCP("MyCrisisAssistant")
app = mcp.http_app(
    path="/mcp",
    transport="streamable-http",
    middleware=[Middleware(LocalhostOriginGuard), Middleware(MemoryWireLog)]
)
```
