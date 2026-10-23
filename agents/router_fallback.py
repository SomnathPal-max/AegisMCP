"""
AegisMCP Fallback Router — router_fallback.py

Keyword-based tool router for when Bedrock credentials are not available.
Uses the fastmcp Client to call tools over Streamable HTTP.
"""

from __future__ import annotations

import os
from fastmcp import Client


MCP_URL = os.getenv("AEGIS_MCP_URL", "http://127.0.0.1:8000/mcp")


async def call_tool(tool: str, args: dict) -> dict:
    """Call a single MCP tool via the Streamable HTTP client."""
    async with Client(MCP_URL) as c:
        result = await c.call_tool(tool, args)
        return {"tool": tool, "args": args, "result": str(result)}


async def route_and_call(utterance: str) -> list[dict]:
    """
    Route an utterance to the appropriate MCP tool(s) by keyword matching.
    Returns a list of (tool, args, result) dicts.
    """
    lower = utterance.lower()
    results = []

    async with Client(MCP_URL) as c:
        # Scam keywords
        if any(kw in lower for kw in ("scam", "fraud", "caller", "suspicious", "verify")):
            r = await c.call_tool("analyze_live_scam_call", {
                "transcript": utterance,
                "claimed_institution": "Unknown",
            })
            results.append({"tool": "analyze_live_scam_call", "result": str(r)})

        # Emergency keywords
        emergency_map = {
            "water heater": "water_heater_rupture",
            "pipe burst": "pipe_burst",
            "flood": "flooding",
            "gas leak": "gas_leak",
            "gas smell": "gas_leak",
            "fire": "fire_smoke",
            "smoke": "fire_smoke",
            "carbon monoxide": "carbon_monoxide",
            "co detector": "carbon_monoxide",
            "electrical": "electrical_surge",
            "power surge": "electrical_surge",
            "break in": "security_breach",
            "intruder": "security_breach",
            "hvac": "hvac_failure",
            "air condition": "hvac_failure",
            "garage door": "garage_door_malfunction",
            "appliance": "appliance_malfunction",
        }
        for keyword, etype in emergency_map.items():
            if keyword in lower:
                r = await c.call_tool("arbitrate_home_emergency", {
                    "emergency_type": etype,
                    "user_observation": utterance,
                })
                results.append({"tool": "arbitrate_home_emergency", "result": str(r)})
                break

        # Claim keywords
        if any(kw in lower for kw in ("claim", "compile", "report")):
            r = await c.call_tool("compile_forensic_claim", {})
            results.append({"tool": "compile_forensic_claim", "result": str(r)})

        # Reset
        if "reset" in lower:
            r = await c.call_tool("reset_demo", {})
            results.append({"tool": "reset_demo", "result": str(r)})

    return results
