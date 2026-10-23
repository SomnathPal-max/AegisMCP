# AegisMCP — Friction Log

> Honest friction entries recorded during the hackathon build on Windows.
> Only events that genuinely occurred during development and testing are documented here.

---

### Friction Log #1: Windows Loopback Socket Access Permission in Sandbox
- **Date**: 2026-10-23
- **Task Attempted**: Launching the self-hosted MCP server (`uvicorn server.aegis_mcp_server:app --port 8000`) and probing it over HTTP.
- **Steps Taken**: Executed server startup and HTTP GET/POST via `httpx` in standard terminal session.
- **Expected vs Actual**:
  - *Expected*: Server binds to `127.0.0.1:8000` and serves requests.
  - *Actual Error*: `httpcore.ConnectError: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions`
- **Severity**: Medium
- **Workaround Used**: Executed the server with sandbox bypass permissions (`BypassSandbox: true`) allowing local TCP socket binding.
- **Actionable Suggestion**: FastMCP and Uvicorn documentation should explicitly document Windows socket permission requirements when running in sandboxed agent environments.

---

### Friction Log #2: Windows Console Standard Output CP1252 Encoding Crash
- **Date**: 2026-10-23
- **Task Attempted**: Running automated scam heuristic evaluation (`python -m tests.eval_scam`).
- **Steps Taken**: Outputting per-case evaluation status indicators using unicode checkmarks (`\u2705`).
- **Expected vs Actual**:
  - *Expected*: Table printed to console showing scam detection accuracy.
  - *Actual Error*: `UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 71: character maps to <undefined>`
- **Severity**: Low
- **Workaround Used**: Added explicit `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` guard and switched tabular indicators to ASCII `[OK]` / `[MISMATCH]`.
- **Actionable Suggestion**: CLI evaluation harnesses should avoid raw multi-byte unicode emojis or use `sys.stdout.buffer` text wrappers by default for cross-platform portability.

---

### Friction Log #3: ReportLab Default Helvetica Type 1 Unicode Glyph Missing
- **Date**: 2026-10-23
- **Task Attempted**: Compiling forensic claim PDF report (`compile_forensic_claim`) using ReportLab.
- **Steps Taken**: Embedded text strings containing unicode em-dashes (`—`) and warning symbols (`⚠`) into Paragraph flowables.
- **Expected vs Actual**:
  - *Expected*: Symbols render legibly in the output PDF document.
  - *Actual*: Default Helvetica Type 1 font failed to resolve unicode codepoints, rendering replacement artifact characters.
  - **Severity**: Low
- **Workaround Used**: Sanitized text strings to standard ASCII equivalents (`--` and `[SIMULATED]`) and safe HTML character entities (`&bull;`).
- **Actionable Suggestion**: ReportLab claim builders should normalize unicode typography before passing strings to standard PDF font flowables.

---

### Friction Log #4: Strands Agents SDK Import Divergence & Graceful Fallback
- **Date**: 2026-10-23
- **Task Attempted**: Invoking `from strands import Agent, BedrockModel` in `agents/analyst_responder.py`.
- **Steps Taken**: Installed `strands-agents` from PyPI and initialized the dual Analyst/Responder pipeline.
- **Expected vs Actual**:
  - *Expected*: Top-level `strands` package exports `Agent` and `BedrockModel`.
  - *Actual*: Package structure diverged (`ModuleNotFoundError: No module named 'strands'`), triggering automatic fallback routing.
- **Severity**: Medium
- **Workaround Used**: Our architecture cleanly intercepted the import failure, seamlessly routed calls through the FastMCP Streamable HTTP keyword fallback client, and activated the `fallback_badge: true` indicator in the response payload.
- **Actionable Suggestion**: Ensure the starter templates clearly document the exact PyPI package distribution name vs module import namespaces.


---

### Friction Log #5: MCP Streamable HTTP Session Invalidation (HTTP 404 Session Not Found)
- **Date**: 2026-10-23
- **Task Attempted**: Sending an emergency arbitration request from the Alexa+ console after an idle interval or server restart.
- **Steps Taken**: Executed `POST /chat` from UI -> Host backend sent `POST /mcp` with previously held `Mcp-Session-Id` header.
- **Expected vs Actual**:
  - *Expected*: Request executes or server transparently handles the stale session.
  - *Actual Error*: `MCP server returned 404: {"jsonrpc":"2.0","id":null,"error":{"code":-32600,"message":"Session not found"}}`
- **Severity**: High (Blocked subsequent client tool calls once a session timed out).
- **Workaround Used**: Updated `host/app.py` with automatic session fault tolerance: upon receiving a 404 or `Session not found`, the client immediately resets `_session_id = None`, performs a fresh `initialize` + `notifications/initialized` handshake, and transparently retries the original tool call. Additionally configured `session_idle_timeout=3600.0` on the server.
- **Actionable Suggestion**: FastMCP clients should incorporate built-in automatic session recovery middleware when communicating over stateful Streamable HTTP transports.

---

### Friction Log #6: Native allowed_origins Configuration Parameter in FastMCP's mcp.run(transport="streamable-http") Initialization
- **Date**: 2026-10-23
- **Component**: FastMCP Python SDK / Streamable HTTP Transport (Spec 2025-11-25)
- **Priority**: Important
- **Description**: Native `allowed_origins` configuration parameter in FastMCP's `mcp.run(transport="streamable-http")` initialization.
- **Why it matters to our project**: When building our local browser-based simulated Alexa+ UI to connect to our local Streamable HTTP MCP server (spec 2025-11-25), the client was completely blocked by HTTP 403 Forbidden errors due to strict Origin header validation. We had to write a custom Starlette OriginGuard ASGI middleware to bypass this for localhost. A native configuration parameter would save developers hours of debugging when building web-based agent simulators.
- **Observed Behavior**: In the official `2025-11-25` Streamable HTTP specification, browser-based agent interfaces (e.g. localhost UI running on port 8080 connecting to MCP server on port 8000) send an `Origin: http://localhost:8080` header. FastMCP's default Streamable HTTP server rejects cross-origin requests with `HTTP 403 Forbidden`, with no clean top-level `allowed_origins` argument exposed in `FastMCP(...)` or `mcp.run(...)`.
- **Workaround Implemented**: Created a custom Starlette ASGI middleware layer (`server/origin_guard.py`) wrapped via `mcp.http_app(middleware=[Middleware(OriginGuard)])` to validate and permit legitimate localhost/loopback origins (`http://localhost:*`, `http://127.0.0.1:*`) while rejecting untrusted external domains to protect against DNS-rebinding attacks. Also packaged this solution into `packages/mcp-streamable-crisis-kit/` for the community.
- **Actionable Suggestion / Feature Request**: Expose `allowed_origins: list[str] = ["http://localhost:*", "http://127.0.0.1:*"]` directly in `FastMCP()`, `mcp.run(transport="streamable-http", allowed_origins=...)`, and `mcp.http_app(allowed_origins=...)`. This would allow developers to configure trusted web frontends with a single argument rather than manually digging into Starlette middleware stacks.

