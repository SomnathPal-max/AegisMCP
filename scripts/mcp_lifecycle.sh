#!/usr/bin/env bash
# AegisMCP MCP Lifecycle Proof Script
# Demonstrates the full MCP 2025-11-25 Streamable HTTP lifecycle:
#   1. initialize → server returns capabilities + session ID
#   2. notifications/initialized
#   3. tools/list
#   4. tools/call analyze_live_scam_call
#   5. resources/read telemetry
#   6. Origin validation: evil origin → 403
#
# Usage: bash scripts/mcp_lifecycle.sh [MCP_URL]

set -euo pipefail

MCP_URL="${1:-http://127.0.0.1:8000/mcp}"
ORIGIN="http://localhost:8080"

echo "============================================"
echo "AegisMCP — MCP Lifecycle Proof"
echo "Server: $MCP_URL"
echo "============================================"
echo ""

# 1. Initialize
echo ">>> Step 1: initialize"
INIT_RESP=$(curl -s -D - -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Origin: $ORIGIN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-11-25",
      "capabilities": {},
      "clientInfo": {"name": "lifecycle-proof", "version": "1.0.0"}
    }
  }')

# Extract Mcp-Session-Id from headers
SESSION_ID=$(echo "$INIT_RESP" | grep -i "mcp-session-id" | head -1 | awk '{print $2}' | tr -d '\r')
echo "Session ID: $SESSION_ID"
echo "$INIT_RESP" | tail -1
echo ""

# 2. notifications/initialized
echo ">>> Step 2: notifications/initialized"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Origin: $ORIGIN" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
echo ""
echo ""

# 3. tools/list
echo ">>> Step 3: tools/list"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Origin: $ORIGIN" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
echo ""
echo ""

# 4. tools/call analyze_live_scam_call
echo ">>> Step 4: tools/call analyze_live_scam_call"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Origin: $ORIGIN" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "analyze_live_scam_call",
      "arguments": {
        "transcript": "Ma'\''am there is an arrest warrant. Buy gift cards immediately and stay on the line.",
        "claimed_institution": "IRS",
        "caller_number": "+1-800-555-9999"
      }
    }
  }'
echo ""
echo ""

# 5. resources/read telemetry
echo ">>> Step 5: resources/read telemetry://smart-home-sensors"
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Origin: $ORIGIN" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "resources/read",
    "params": {
      "uri": "telemetry://smart-home-sensors"
    }
  }'
echo ""
echo ""

# 6. Evil Origin → should get 403
echo ">>> Step 6: Evil Origin (http://evil.example) → expect 403"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Origin: http://evil.example" \
  -d '{
    "jsonrpc": "2.0",
    "id": 99,
    "method": "tools/list"
  }')
echo "HTTP status: $HTTP_CODE"
if [ "$HTTP_CODE" = "403" ]; then
  echo "✅ Origin guard working correctly — evil origin blocked."
else
  echo "❌ UNEXPECTED: expected 403 but got $HTTP_CODE"
fi
echo ""

echo "============================================"
echo "Lifecycle proof complete."
echo "============================================"
