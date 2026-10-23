"""
AegisMCP Server — aegis_mcp_server.py

Self-hosted MCP server on /mcp (Streamable HTTP, spec 2025-11-25).
Registers tools, resources, Origin guard, wire log, /healthz, and /debug/wire.

All IoT devices, sensors, policies, and phone numbers are SIMULATED.
"""

from __future__ import annotations

import uvicorn
from starlette.middleware import Middleware
from starlette.responses import JSONResponse

from fastmcp import FastMCP, Context
from server import aegis_core as core
from server.origin_guard import OriginGuard, WireLog, WIRE_RING

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "AegisMCP",
    instructions=(
        "Household crisis, scam-call check and claim prep. "
        "Devices and policies are SIMULATED. Prioritise life safety."
    ),
)

# Register tools
mcp.tool(core.analyze_live_scam_call)
mcp.tool(core.compile_forensic_claim)
mcp.tool(core.reset_demo)


@mcp.tool
async def arbitrate_home_emergency(
    emergency_type: str,
    user_observation: str,
    ctx: Context,
    confirm_electrical: bool = False,
) -> dict:
    """
    Contain a home emergency (SIMULATED) and look up coverage.
    Supports all household components: water_heater_rupture, electrical_surge,
    gas_leak, hvac_failure, fire_smoke, carbon_monoxide, security_breach,
    flooding, appliance_malfunction, garage_door_malfunction, pipe_burst.
    Only reversible IoT actions are automatic. Electrical isolation requires
    explicit confirm_electrical=True.
    """
    try:
        await ctx.report_progress(1, 4, "Reading sensor snapshot")
    except Exception:
        pass

    try:
        await ctx.report_progress(2, 4, "Executing IoT hazard containment")
    except Exception:
        pass

    result = core.arbitrate_home_emergency(
        emergency_type, user_observation, confirm_electrical
    )

    try:
        await ctx.report_progress(3, 4, "Matching policy clause & warranty terms")
    except Exception:
        pass

    try:
        await ctx.report_progress(4, 4, "Done")
    except Exception:
        pass

    return result


# Register resources with 2025-11-25 annotations
mcp.resource(
    "policy://household/master-insurance-2026",
    name="Household Master Insurance & Warranty Policy [SIMULATED]",
    mime_type="application/json",
    annotations={"audience": ["user", "assistant"], "priority": 0.95},
)(core.get_policy_json)

mcp.resource(
    "telemetry://smart-home-sensors",
    name="Smart Home Sensor Telemetry [SIMULATED]",
    mime_type="application/json",
)(core.get_sensor_json)


# ---------------------------------------------------------------------------
# ASGI application with OriginGuard and WireLog
# ---------------------------------------------------------------------------

def create_app():
    """Create the full ASGI app with /mcp, /healthz, and /debug/wire."""
    server_app = mcp.http_app(
        path="/mcp",
        transport="streamable-http",
        middleware=[Middleware(OriginGuard), Middleware(WireLog)],
    )

    async def healthz(request):
        return JSONResponse({
            "status": "ok",
            "service": "AegisMCP",
            "mcp_spec": "2025-11-25",
            "transport": "streamable-http",
            "simulated": True,
        })

    async def debug_wire(request):
        return JSONResponse(list(WIRE_RING))

    server_app.add_route("/healthz", healthz, methods=["GET"])
    server_app.add_route("/debug/wire", debug_wire, methods=["GET"])

    return server_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "server.aegis_mcp_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
