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
