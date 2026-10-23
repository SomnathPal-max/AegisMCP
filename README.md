# AegisMCP: Autonomous Household Crisis Assistant & Scam Firewall for Alexa+

> **Build, Ship, Shape: Amazon Developer Hackathon**  
> **Track**: Alexa+ Track ($25,000) • **Mini Challenges**: AWS Builder ($5,000) & Open Source ($5,000)  
> **MCP Specification**: `2025-11-25` Streamable HTTP (`/mcp`)  
> **License**: MIT

---

## 1. Overview

When high-stakes crises strike at home—an elderly parent targeted by a coercive phone scammer demanding gift cards, a basement water heater rupturing near electrical circuits, or a sudden natural gas leak—standard voice assistants fall short. They recite generic web search blurbs while users struggle through 80-page insurance policy PDFs, warranty exclusion clauses, and phone trees.

**AegisMCP** bridges a simulated **Alexa+ Multimodal Console** to a self-hosted **Model Context Protocol (MCP)** server over the unified `2025-11-25` **Streamable HTTP transport**. It actively arbitrates emergencies across **all home components**, triggers reversible IoT safety containment, checks policy coverage, and compiles timestamped forensic claim dossiers.

```
+-----------------------------------------------------------------------------------+
|                   ALEXA+ SIMULATED MULTIMODAL CONSOLE (HTML/JS)                   |
|   [Voice Command Input]     [Live Scam Threat Gauge]     [MCP Wire Inspector]     |
+-----------------------------------------+-----------------------------------------+
                                          |
                        HTTP POST /chat, /wire, /reset
                                          v
+-----------------------------------------------------------------------------------+
|                   HOST BACKEND: "Simulated Alexa+" (FastAPI)                      |
|       • Pure MCP Client (Zero imports from server / aegis_core packages)           |
|       • Manages Mcp-Session-Id and Streamable HTTP JSON-RPC/SSE wire payloads     |
+-----------------------------------------+-----------------------------------------+
                                          |
                        POST /mcp (Accept: application/json, text/event-stream)
                        Headers: Mcp-Session-Id, Origin Validation (Spec 2025-11-25)
                                          v
+-----------------------------------------------------------------------------------+
|               AEGIS-MCP SERVER (FastMCP Python • Streamable HTTP /mcp)            |
|       • OriginGuard: Rejects non-localhost origins with HTTP 403 (DNS-Rebinding)  |
|       • WireLog: Non-intrusive metadata ring buffer served at /debug/wire        |
|                                                                                   |
|  +-----------------------------+  +--------------------------------------------+  |
|  | MCP Tools (@mcp.tool)       |  | MCP Resources (@mcp.resource, 2025-11-25)  |  |
|  | • analyze_live_scam_call()  |  | • policy://household/master-insurance-2026 |  |
|  | • arbitrate_home_emergency()|  |   (audience: ["user","assistant"], p=0.95) |  |
|  | • compile_forensic_claim()  |  | • telemetry://smart-home-sensors           |  |
|  | • reset_demo()              |  +--------------------------------------------+  |
|  +-----------------------------+                                                  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|             AWS STRANDS AGENTS SDK + BEDROCK DUAL-AGENT PIPELINE                  |
|  • Analyst Agent   : Read-only; inspects untrusted transcript; cannot act         |
|  • Responder Agent : Action tools only; never sees raw caller text (Anti-Injection)|
|  • Fallback Router : Deterministic keyword tool caller when credentials absent    |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Capabilities & Honest Positioning

In strict adherence to truth-in-advertising hackathon guidelines:

| Innovation | Implementation Details | Status |
|---|---|---|
| **Live Coercion Scam Check** | Heuristic text analysis on supplied transcripts searching for high-pressure coercion vectors (arrest warrants, gift card demands, wire transfers, safe accounts, OTP harvesting). Method is always reported as `text-heuristic`. | **REAL** |
| **Spoofed Institution Directory** | Compares caller ID against an official directory of institutions (Chase, BofA, IRS, SSA, etc.). Mismatches add +20 risk points. | **REAL** (Directory is `SIMULATED`) |
| **Emergency Arbitration for ALL Home Components** | Covers 11 distinct household crisis categories: water heater rupture, pipe burst, electrical surge, natural gas leak, carbon monoxide, fire/smoke, security breach, basement flooding, HVAC failure, appliance breakdown, and garage door malfunction. Reversible actions are automatic; electrical isolation requires explicit user confirmation. | **REAL** (Devices are `SIMULATED`) |
| **Streamable HTTP MCP Protocol** | Single `/mcp` endpoint implementing the official `2025-11-25` specification with session IDs, origin checking, and progress notifications. | **REAL** |
| **Forensic Claim Ledger (JSON + PDF)** | `compile_forensic_claim` compiles real JSON and ReportLab PDF dossiers in `out/` citing timestamps, sensor snapshots, policy clauses, and warranty warnings. | **REAL** (Data is `SIMULATED`) |
| **Analyst / Responder Split** | Security architecture separating untrusted input analysis from action tool execution to prevent prompt injection attacks. Includes automatic fallback badge. | **REAL** |

---

## 3. Real vs. Simulated Distinction

| Component | Status | Description |
|---|---|---|
| **MCP Protocol Transport** | **REAL** | Full `2025-11-25` Streamable HTTP with `Mcp-Session-Id` tracking |
| **Tool Execution & Wire RPC** | **REAL** | Host communicates with server purely over HTTP JSON-RPC / SSE |
| **Origin Guard Security** | **REAL** | Non-localhost origins rejected with HTTP 403 Forbidden |
| **Wire Log Ring Buffer** | **REAL** | Captures real HTTP method, path, status, and session IDs |
| **Claim Document Generation** | **REAL** | Real `.json` and `.pdf` files compiled to `out/` via ReportLab |
| **Smart Home Hardware** | `SIMULATED` | Valves, breakers, locks, sensors, thermostats, and appliances |
| **Insurance Policies & Terms** | `SIMULATED` | Fixture policy clauses and deductibles for demonstration |
| **Phone Directory** | `SIMULATED` | Curated sample directory of official bank/agency phone numbers |
| **Vendor Emergency Dispatch** | `SIMULATED` | Service company names and estimated arrival times |

---

## 4. Empirical Evaluation Results

We evaluated `analyze_live_scam_call` against a curated 20-case test set (`tests/scam_cases.json`):

```text
RESULTS (hand-made test set, 20 cases):
  Scams caught:              8/8  (100% detection rate on high-coercion calls)
  Scams missed:              0/8
  Legitimate correct:        8/8  (0 false alarms on standard legitimate calls)
  Legitimate false alarms:   0/8
  Ambiguous flagged:         2/4  (SSN requests & number mismatches caught)
  Ambiguous unflagged:       2/4  (Sub-threshold boundary cases)
```

Run the benchmark yourself:
```bash
python -m tests.eval_scam
```

---

## 5. Quickstart Guide (Under 5 Minutes)

### Prerequisites
- Python 3.10+
- `pip`

### Step 1: Clone & Install Dependencies
```bash
cd aegis-mcp-alexa-plus
pip install -r requirements.txt
```

### Step 2: Run Unit & HTTP Integration Tests
```bash
# Verify core logic (30 unit tests)
pytest tests/test_core.py -v

# Verify HTTP server lifecycle and OriginGuard (5 integration tests)
pytest tests/test_server_http.py -v
```

### Step 3: Start the MCP Server
```bash
python -m uvicorn server.aegis_mcp_server:app --host 127.0.0.1 --port 8000
```
*Health check*: `http://127.0.0.1:8000/healthz`  
*MCP Endpoint*: `http://127.0.0.1:8000/mcp`  
*Debug Wire*: `http://127.0.0.1:8000/debug/wire`

### Step 4: Start the Alexa+ Simulator Host
In a separate terminal:
```bash
python -m uvicorn host.app:app --host 127.0.0.1 --port 8080
```

### Step 5: Open the Multimodal Console
Open your browser to:
```
http://localhost:8080
```

---

## 6. Proving the MCP Protocol Wire

### Lifecycle Verification via Script
Execute the bundled lifecycle bash script:
```bash
bash scripts/mcp_lifecycle.sh http://127.0.0.1:8000/mcp
```
The script proves:
1. `POST /mcp` `initialize` returns session ID and capabilities.
2. `POST /mcp` `notifications/initialized` acknowledges handshake.
3. `POST /mcp` `tools/list` enumerates all crisis arbitration tools.
4. `POST /mcp` `tools/call` invokes `analyze_live_scam_call`.
5. `POST /mcp` `resources/read` fetches `telemetry://smart-home-sensors`.
6. `Origin: http://evil.example` is blocked with **HTTP 403 Forbidden**.

---

## 7. Open Source Mini Challenge: `mcp-streamable-crisis-kit`

As part of the Open Source Mini Challenge ($5,000), this repository includes a standalone reusable Python package located at `packages/mcp-streamable-crisis-kit/`:

- **`LocalhostOriginGuard`**: Reusable ASGI middleware to prevent DNS-rebinding attacks on local MCP endpoints.
- **`MemoryWireLog`**: Privacy-preserving in-memory wire logger capturing diagnostic traffic without leaking sensitive request bodies.

---

## 8. Disclaimer

AegisMCP is an academic/hackathon prototype developed for the Amazon Developer Hackathon. It does not provide certified legal, insurance, or emergency dispatch services. All smart home devices, telemetry streams, and insurer responses are **SIMULATED**. In any genuine emergency, call 911 or your local emergency services immediately.
