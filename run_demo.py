"""
AegisMCP Dual Runner — run_demo.py

Starts both:
1. AegisMCP Server on http://127.0.0.1:8000 (Streamable HTTP /mcp)
2. Alexa+ Host Simulator on http://127.0.0.1:8080 (serves UI console and proxies MCP)
"""

import io
import os
import subprocess
import sys
import time

# Windows console encoding safety
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DIR = os.path.dirname(os.path.abspath(__file__))

print("=" * 60)
print("Starting AegisMCP Ecosystem on localhost...")
print("=" * 60)

# 1. Start MCP Server on :8000
print("1. Launching MCP Server on http://127.0.0.1:8000/mcp ...")
p_server = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "server.aegis_mcp_server:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"],
    cwd=DIR
)

time.sleep(2)

# 2. Start Alexa+ Host on :8080
print("2. Launching Alexa+ Console Host on http://127.0.0.1:8080 ...")
p_host = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "host.app:app", "--host", "127.0.0.1", "--port", "8080", "--log-level", "info"],
    cwd=DIR
)

print("\n" + "=" * 60)
print("[OK] AegisMCP is RUNNING!")
print(">> Open your browser to: http://localhost:8080")
print(">> MCP Endpoint:        http://127.0.0.1:8000/mcp")
print(">> Debug Wire Log:      http://127.0.0.1:8000/debug/wire")
print("=" * 60)
print("Press Ctrl+C to stop both servers.\n")

try:
    while True:
        time.sleep(1)
        if p_server.poll() is not None or p_host.poll() is not None:
            break
except KeyboardInterrupt:
    print("\nStopping servers...")
finally:
    p_host.terminate()
    p_server.terminate()
    try:
        p_host.wait(timeout=3)
        p_server.wait(timeout=3)
    except Exception:
        p_host.kill()
        p_server.kill()
    print("All servers stopped.")
