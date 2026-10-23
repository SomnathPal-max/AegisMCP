# AegisMCP — Real vs. Simulated

Everything in AegisMCP is clearly labelled. This table lists what is live/real and what is simulated.

## LIVE (Real)

| Component | Description |
|-----------|-------------|
| MCP Protocol | Streamable HTTP transport on `/mcp`, spec 2025-11-25 |
| MCP Tool Calls | Real JSON-RPC calls over the wire between host and server |
| Origin Validation | Real HTTP 403 for disallowed origins |
| Wire Log | Real HTTP request/response metadata captured per call |
| Scam Analysis | Real heuristic text analysis on supplied transcripts |
| Claim Files | Real JSON and PDF files written to `out/` |
| Bedrock Calls | Real AWS Bedrock API calls (when credentials present) |
| Progress Notifications | Real MCP progress notifications streamed to client |

## SIMULATED

| Component | Description |
|-----------|-------------|
| Alexa+ Console | Web UI simulating Alexa+ multimodal interface |
| IoT Devices | All smart home devices (valves, breakers, sensors, locks, thermostats, detectors) |
| Sensor Telemetry | Humidity, flow rate, temperature, CO levels, smoke readings |
| Insurance Policy | Fixture policy data — not real insurance advice |
| Phone Directory | Small set of official institution numbers for demo |
| Emergency Dispatch | Vendor dispatch suggestions are fictional |
| Warranty Terms | Fictional warranty clauses |

> **Disclaimer**: AegisMCP is a hackathon prototype. It does not provide legal, insurance, or emergency advice. All device interactions, policies, and vendor data are simulated. In a real emergency, call your local emergency services.
