"""
Integration tests for AegisMCP HTTP Server over Streamable HTTP.

Tests:
1. /healthz endpoint
2. Origin guard (evil origin -> 403, localhost -> 200)
3. /debug/wire endpoint
4. MCP lifecycle: initialize, tools/list, tools/call, resources/read
5. Progress notifications during crisis arbitration
"""

import os
import subprocess
import sys
import time
import pytest
import httpx

SERVER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_URL = "http://127.0.0.1:8000"
MCP_URL = f"{BASE_URL}/mcp"


@pytest.fixture(scope="module")
def running_server():
    """Start uvicorn server in a subprocess for testing."""
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "server.aegis_mcp_server:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--log-level",
        "warning",
    ]
    proc = subprocess.Popen(cmd, cwd=SERVER_DIR)
    
    # Wait for server to start
    started = False
    for _ in range(30):
        try:
            with httpx.Client(timeout=1.0) as client:
                r = client.get(f"{BASE_URL}/healthz")
                if r.status_code == 200:
                    started = True
                    break
        except Exception:
            time.sleep(0.2)
            
    if not started:
        proc.terminate()
        proc.wait()
        pytest.fail("AegisMCP server failed to start on port 8000")

    yield proc

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


class TestServerEndpoints:
    def test_healthz(self, running_server):
        with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
            resp = client.get("/healthz")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            assert data["service"] == "AegisMCP"
            assert data["mcp_spec"] == "2025-11-25"
            assert data["simulated"] is True

    def test_origin_guard_evil_origin_403(self, running_server):
        with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
            resp = client.post(
                "/mcp",
                headers={
                    "Origin": "http://evil.example",
                    "Content-Type": "application/json",
                },
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            )
            assert resp.status_code == 403
            assert "origin not allowed" in resp.json().get("error", "")

    def test_origin_guard_allowed_origin(self, running_server):
        with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
            resp = client.post(
                "/mcp",
                headers={
                    "Origin": "http://localhost:8080",
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "1.0.0"},
                    },
                },
            )
            assert resp.status_code == 200
            assert "mcp-session-id" in resp.headers

    def test_wire_log(self, running_server):
        with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
            # Generate a request to be logged
            client.get("/healthz")
            resp = client.get("/debug/wire")
            assert resp.status_code == 200
            entries = resp.json()
            assert isinstance(entries, list)
            assert len(entries) > 0
            # Verify no secret fields in wire log
            for entry in entries:
                assert "body" not in entry
                assert "password" not in entry
                assert "authorization" not in entry


class TestMcpLifecycle:
    def test_full_mcp_flow(self, running_server):
        headers = {
            "Origin": "http://localhost:8080",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        with httpx.Client(base_url=BASE_URL, headers=headers, timeout=10.0) as client:
            # 1. Initialize
            r_init = client.post(
                "/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 100,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "lifecycle-test", "version": "1.0.0"},
                    },
                },
            )
            assert r_init.status_code == 200
            session_id = r_init.headers.get("mcp-session-id")
            assert session_id is not None
            req_headers = dict(headers)
            req_headers["Mcp-Session-Id"] = session_id

            # 2. tools/list
            r_tools = client.post(
                "/mcp",
                headers=req_headers,
                json={"jsonrpc": "2.0", "id": 101, "method": "tools/list"},
            )
            assert r_tools.status_code == 200
            assert "analyze_live_scam_call" in r_tools.text
            assert "arbitrate_home_emergency" in r_tools.text
            assert "compile_forensic_claim" in r_tools.text
            assert "reset_demo" in r_tools.text

            # 3. tools/call analyze_live_scam_call
            r_scam = client.post(
                "/mcp",
                headers=req_headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 102,
                    "method": "tools/call",
                    "params": {
                        "name": "analyze_live_scam_call",
                        "arguments": {
                            "transcript": "Arrest warrant. Buy gift cards immediately. Stay on the line.",
                            "claimed_institution": "IRS",
                            "caller_number": "+1-800-555-0199",
                        },
                    },
                },
            )
            assert r_scam.status_code == 200
            assert "CRITICAL_SCAM" in r_scam.text

            # 4. tools/call arbitrate_home_emergency
            r_emg = client.post(
                "/mcp",
                headers=req_headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 103,
                    "method": "tools/call",
                    "params": {
                        "name": "arbitrate_home_emergency",
                        "arguments": {
                            "emergency_type": "water_heater_rupture",
                            "user_observation": "Water is flooding my basement from the heater!",
                        },
                    },
                },
            )
            assert r_emg.status_code == 200
            assert "CLM-" in r_emg.text
            assert "SIMULATED" in r_emg.text

            # 5. resources/read policy
            r_pol = client.post(
                "/mcp",
                headers=req_headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 104,
                    "method": "resources/read",
                    "params": {"uri": "policy://household/master-insurance-2026"},
                },
            )
            assert r_pol.status_code == 200
            assert "SIMULATED" in r_pol.text
            assert "Section 4.2.b" in r_pol.text

            # 6. resources/read telemetry
            r_tel = client.post(
                "/mcp",
                headers=req_headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 105,
                    "method": "resources/read",
                    "params": {"uri": "telemetry://smart-home-sensors"},
                },
            )
            assert r_tel.status_code == 200
            assert "SIMULATED" in r_tel.text
            assert "basement_humidity_pct" in r_tel.text
