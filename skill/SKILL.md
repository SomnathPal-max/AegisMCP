---
name: aegis-mcp-alexa-plus
description: Autonomous household crisis assistant, scam call firewall, and insurance claim prep for Alexa+ via Streamable HTTP Model Context Protocol (MCP).
version: 1.0.0
author: AegisMCP Contributors
license: MIT
metadata:
  protocol: mcp-2025-11-25
  transport: streamable-http
  endpoint: http://127.0.0.1:8000/mcp
  categories:
    - smart-home
    - crisis-management
    - fraud-prevention
    - insurance
---

# AegisMCP — Household Crisis Assistant for Alexa+

AegisMCP turns Alexa+ into an active crisis arbitrator and scam call firewall for elderly individuals and families at home.

> **DISCLAIMER**: AegisMCP is a hackathon prototype. All smart home device actions, sensor telemetry, insurance policies, and phone directories are **SIMULATED**. AegisMCP does not provide official legal, insurance, or emergency dispatch services. In a real emergency, call 911 immediately.

## Capabilities

1. **Live Scam Call Coercion Analysis** (`analyze_live_scam_call`)
   - Text-heuristic evaluation of caller transcripts for coercion markers (arrest warrants, gift card demands, wire transfers, safe accounts, OTP harvesting).
   - Cross-checks caller phone numbers against a SIMULATED directory of official institution numbers.
   - Computes a threat score (0-99%) and returns immediate spoken Alexa+ interjections and safe counter-questions.

2. **Autonomous Home Crisis Containment** (`arbitrate_home_emergency`)
   - Supports all household components:
     - Water heater rupture / pipe burst / flooding (automatic main water valve isolation)
     - Gas leak / carbon monoxide (automatic main gas line shutoff + HVAC shutdown)
     - Electrical surge / arc fault (isolated smart breaker with explicit safety confirmation)
     - Fire / smoke (automatic fire sprinkler activation + HVAC shutdown)
     - Security breach / forced entry (automatic door lock & alarm arming)
     - HVAC breakdown / appliance failure / garage door mechanism
   - Matches incidents against SIMULATED homeowner insurance clauses, deductibles, and warranty preservation rules.
   - Provides life-safety guidance first.

3. **Forensic Claim Compilation** (`compile_forensic_claim`)
   - Packages user observations, sensor snapshots, IoT mitigation actions, and policy citations into a timestamped JSON and PDF claim dossier saved to `out/`.

4. **Demo State Reset** (`reset_demo`)
   - Restores all simulated valves, breakers, locks, and sensors to baseline state.

## MCP Protocol Wire Integration

- **Transport**: Single-endpoint Streamable HTTP on `/mcp` (Spec 2025-11-25).
- **Session Tracking**: `Mcp-Session-Id` header across multi-turn exchanges.
- **Origin Validation**: Strict HTTP 403 enforcement for non-localhost origins to prevent DNS-rebinding attacks.
- **Wire Inspector**: Live endpoint at `/debug/wire` and host UI panel.

## Alexa+ Voice Invocations

- *"Alexa, verify this caller with Aegis"* -> Triggers scam firewall on speakerphone transcript.
- *"Alexa, my basement water heater just ruptured!"* -> Triggers water valve shutoff and policy check.
- *"Alexa, I smell natural gas in the kitchen!"* -> Triggers gas shutoff and evacuation guidance.
- *"Alexa, compile my insurance claim packet with Aegis"* -> Generates PDF dossier in `out/`.
- *"Alexa, reset the Aegis crisis demo"* -> Restores baseline smart home state.
