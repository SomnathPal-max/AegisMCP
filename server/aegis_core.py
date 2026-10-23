"""
AegisMCP Core Logic — aegis_core.py

Household crisis assistant core: scam analyzer, emergency containment for ALL
home components, forensic claim builder (JSON+PDF), sensor telemetry, and demo
reset.  Every device, policy, and sensor value is SIMULATED.

This module is pure logic — no MCP, no FastAPI, no network.  The MCP server
imports and wraps these functions.
"""

from __future__ import annotations

import copy
import datetime
import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Thread-safe state lock
# ---------------------------------------------------------------------------
_LOCK = threading.Lock()

# ---------------------------------------------------------------------------
# SIMULATED — Official phone-number directory (loaded once)
# ---------------------------------------------------------------------------
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_official_numbers() -> dict:
    p = _DATA_DIR / "official_numbers.json"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f).get("institutions", {})
    return {}

OFFICIAL_NUMBERS: dict = _load_official_numbers()

# ---------------------------------------------------------------------------
# SIMULATED — IoT device state for the entire household
# ---------------------------------------------------------------------------
_IOT_BASELINE: dict[str, Any] = {
    # Plumbing
    "main_water_valve":        {"state": "OPEN",   "label": "Main Water Shutoff Valve [SIMULATED]"},
    "water_heater_valve":      {"state": "OPEN",   "label": "Water Heater Isolation Valve [SIMULATED]"},
    # Electrical
    "smart_breaker_main":      {"state": "ACTIVE", "label": "Main Smart Breaker Panel [SIMULATED]"},
    "smart_breaker_zone_3":    {"state": "ACTIVE", "label": "Smart Breaker Zone 3 [SIMULATED]"},
    # Gas
    "gas_main_valve":          {"state": "OPEN",   "label": "Main Gas Shutoff Valve [SIMULATED]"},
    "gas_water_heater_valve":  {"state": "OPEN",   "label": "Water Heater Gas Valve [SIMULATED]"},
    # HVAC
    "hvac_system":             {"state": "RUNNING","label": "Central HVAC System [SIMULATED]"},
    "hvac_thermostat":         {"state": "AUTO",   "label": "Smart Thermostat [SIMULATED]"},
    # Security
    "front_door_lock":         {"state": "LOCKED", "label": "Front Door Smart Lock [SIMULATED]"},
    "back_door_lock":          {"state": "LOCKED", "label": "Back Door Smart Lock [SIMULATED]"},
    "garage_door":             {"state": "CLOSED", "label": "Smart Garage Door [SIMULATED]"},
    "alarm_system":            {"state": "ARMED_HOME", "label": "Home Alarm System [SIMULATED]"},
    "security_cameras":        {"state": "RECORDING",  "label": "Security Cameras [SIMULATED]"},
    # Fire & Gas Detection
    "smoke_detectors":         {"state": "NORMAL", "label": "Smart Smoke Detectors [SIMULATED]"},
    "co_detectors":            {"state": "NORMAL", "label": "CO Detectors [SIMULATED]"},
    "sprinkler_system":        {"state": "STANDBY","label": "Fire Sprinkler System [SIMULATED]"},
    # Appliances
    "refrigerator":            {"state": "RUNNING","label": "Smart Refrigerator [SIMULATED]"},
    "washing_machine":         {"state": "IDLE",   "label": "Smart Washing Machine [SIMULATED]"},
    "dryer":                   {"state": "IDLE",   "label": "Smart Dryer [SIMULATED]"},
    "dishwasher":              {"state": "IDLE",   "label": "Smart Dishwasher [SIMULATED]"},
    "oven":                    {"state": "OFF",    "label": "Smart Oven [SIMULATED]"},
}

_SENSOR_BASELINE: dict[str, Any] = {
    "basement_humidity_pct":    45.2,
    "basement_temperature_f":   68.0,
    "water_flow_rate_gpm":      0.0,
    "water_pressure_psi":       55.0,
    "gas_level_ppm":            0.0,
    "co_level_ppm":             0.0,
    "smoke_density_pct":        0.0,
    "indoor_temperature_f":     72.0,
    "outdoor_temperature_f":    58.0,
    "electrical_load_kw":       4.2,
    "voltage_v":                120.0,
    "last_updated":             None,   # filled on init
}

def _now_utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

# Live mutable state (deep copies of baselines)
IOT_STATE: dict[str, Any] = copy.deepcopy(_IOT_BASELINE)
SENSOR_STATE: dict[str, Any] = copy.deepcopy(_SENSOR_BASELINE)
SENSOR_STATE["last_updated"] = _now_utc()

# Accumulated sensor time-series for the claim ledger
SENSOR_SERIES: list[dict] = []

# Stored analysis results for claim compilation
_STORED_ANALYSES: dict[str, dict] = {}
_STORED_CLAIMS: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# SIMULATED — Insurance & Warranty Policy Database (all home components)
# ---------------------------------------------------------------------------
POLICY_DB: dict[str, dict[str, Any]] = {
    "water_heater_rupture": {
        "clause": "Section 4.2.b — Sudden & Accidental Discharge of Plumbing/Appliances [SIMULATED]",
        "covered": True,
        "deductible_usd": 500,
        "warranty_warning": "CRITICAL: Do NOT unbolt the anode rod yourself; DIY disassembly voids "
                            "the 10-year manufacturer warranty under Clause 9.1. [SIMULATED]",
        "dispatch_suggestion": "RapidRooter 24/7 Emergency Plumbing (ETA ~22 min) [SIMULATED]",
        "safety_guidance": (
            "1. Do NOT wade through standing water near any electrical outlets or appliances.\n"
            "2. Turn off power to the water heater at the breaker if safe to reach.\n"
            "3. If you smell gas, leave the house immediately and call emergency services.\n"
            "4. The main water valve will be closed automatically to stop flooding."
        ),
    },
    "electrical_surge": {
        "clause": "Section 6.1.a — Power Surge & Smart Panel Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 250,
        "warranty_warning": "Keep damaged breaker trip logs intact in telemetry memory for adjuster "
                            "inspection. [SIMULATED]",
        "dispatch_suggestion": "VoltGuard Certified Electricians (ETA ~35 min) [SIMULATED]",
        "safety_guidance": (
            "1. Do NOT touch any exposed wiring or damaged outlets.\n"
            "2. If you see sparks or smell burning, evacuate and call 911.\n"
            "3. Unplug sensitive electronics to prevent further damage.\n"
            "4. The affected breaker zone will be isolated automatically."
        ),
    },
    "gas_leak": {
        "clause": "Section 7.3.a — Gas Line Leak & Emergency Shutoff Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 0,
        "warranty_warning": "Gas line repairs must be performed by a licensed technician. "
                            "DIY repair voids coverage and is illegal in most jurisdictions. [SIMULATED]",
        "dispatch_suggestion": "Local Gas Company Emergency Line + Licensed Gas Fitter (ETA ~15 min) [SIMULATED]",
        "safety_guidance": (
            "1. Do NOT turn on/off any electrical switches or appliances.\n"
            "2. Do NOT light matches, lighters, or candles.\n"
            "3. Open windows and doors if safe to do so.\n"
            "4. Leave the house immediately and call 911 from outside.\n"
            "5. Gas valves will be shut off automatically."
        ),
    },
    "hvac_failure": {
        "clause": "Section 5.1.c — HVAC System Breakdown Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 200,
        "warranty_warning": "Attempting to restart the compressor manually may void the 5-year "
                            "parts warranty. Wait for a certified technician. [SIMULATED]",
        "dispatch_suggestion": "ClimateGuard HVAC Services (ETA ~45 min) [SIMULATED]",
        "safety_guidance": (
            "1. If the system is making unusual noises, turn it off at the thermostat.\n"
            "2. If you smell burning from vents, turn off the system and evacuate.\n"
            "3. In extreme cold, use blankets and close interior doors to conserve heat.\n"
            "4. In extreme heat, move to the lowest floor and stay hydrated."
        ),
    },
    "fire_smoke": {
        "clause": "Section 2.1.a — Fire & Smoke Damage Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 500,
        "warranty_warning": "Document all damage with photos before cleanup. Do not discard "
                            "damaged items until the adjuster has inspected. [SIMULATED]",
        "dispatch_suggestion": "Call 911 IMMEDIATELY. Fire Department dispatch. [SIMULATED]",
        "safety_guidance": (
            "1. EVACUATE THE HOUSE IMMEDIATELY. Do not try to fight the fire.\n"
            "2. Call 911 from outside the home.\n"
            "3. Do NOT go back inside for belongings.\n"
            "4. Close doors behind you to slow fire spread.\n"
            "5. Meet at your family's designated meeting point.\n"
            "6. Sprinkler system will be activated automatically."
        ),
    },
    "carbon_monoxide": {
        "clause": "Section 7.4.b — Carbon Monoxide Incident Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 0,
        "warranty_warning": "CO source identification requires a licensed HVAC/gas technician. "
                            "Do not re-enter until cleared by fire department. [SIMULATED]",
        "dispatch_suggestion": "Call 911 IMMEDIATELY. CO is life-threatening. [SIMULATED]",
        "safety_guidance": (
            "1. EVACUATE THE HOUSE IMMEDIATELY — CO is odorless and deadly.\n"
            "2. Call 911 from outside.\n"
            "3. Do NOT re-enter until emergency services clear the home.\n"
            "4. If anyone has symptoms (headache, dizziness, nausea), seek medical help.\n"
            "5. Gas and HVAC systems will be shut off automatically."
        ),
    },
    "security_breach": {
        "clause": "Section 8.2.a — Theft, Vandalism & Forced Entry Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 500,
        "warranty_warning": "File a police report within 24 hours to maintain coverage eligibility. "
                            "Document all missing/damaged items. [SIMULATED]",
        "dispatch_suggestion": "Call 911. Security company dispatch notified. [SIMULATED]",
        "safety_guidance": (
            "1. If you suspect someone is inside, DO NOT ENTER. Call 911.\n"
            "2. If you are inside, move to a secure room and lock the door.\n"
            "3. All doors will be locked and alarm activated automatically.\n"
            "4. Security cameras are recording and saving footage.\n"
            "5. Do not touch or clean up — preserve evidence for police."
        ),
    },
    "flooding": {
        "clause": "Section 3.1.a — Interior Water Damage & Flooding Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 750,
        "warranty_warning": "Flood damage restoration must begin within 48 hours to maintain "
                            "coverage. Professional water extraction required. [SIMULATED]",
        "dispatch_suggestion": "AquaRestore Water Damage Specialists (ETA ~30 min) [SIMULATED]",
        "safety_guidance": (
            "1. Do NOT walk through standing water — electrocution risk from submerged outlets.\n"
            "2. Turn off electricity to affected areas at the breaker panel if safe.\n"
            "3. Move valuables to higher ground if possible.\n"
            "4. Main water valve will be closed automatically.\n"
            "5. Document damage with photos for insurance claim."
        ),
    },
    "appliance_malfunction": {
        "clause": "Section 5.3.b — Major Appliance Breakdown Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 150,
        "warranty_warning": "Unplugging and restarting is acceptable. Do NOT attempt internal "
                            "repairs — this voids the manufacturer warranty. [SIMULATED]",
        "dispatch_suggestion": "AppliancePro Repair Service (ETA ~2 hours) [SIMULATED]",
        "safety_guidance": (
            "1. Unplug the malfunctioning appliance immediately.\n"
            "2. If the appliance is leaking water, close the supply valve behind it.\n"
            "3. If you smell burning or see smoke, move away and call 911.\n"
            "4. Do not attempt to repair electrical components yourself."
        ),
    },
    "garage_door_malfunction": {
        "clause": "Section 5.4.a — Garage Door & Opener Mechanism Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 100,
        "warranty_warning": "Garage door springs are under extreme tension — never attempt DIY "
                            "repair. Lethal injury risk. [SIMULATED]",
        "dispatch_suggestion": "DoorSafe Garage Services (ETA ~1 hour) [SIMULATED]",
        "safety_guidance": (
            "1. Do NOT stand under a malfunctioning garage door.\n"
            "2. Do NOT attempt to fix springs or cables yourself — they are lethal.\n"
            "3. If the door is stuck open, do not leave the garage unattended.\n"
            "4. Use the manual release cord only if instructed by a technician.\n"
            "5. Keep children and pets away from the door mechanism."
        ),
    },
    "pipe_burst": {
        "clause": "Section 4.1.a — Burst Pipe & Plumbing Emergency Coverage [SIMULATED]",
        "covered": True,
        "deductible_usd": 500,
        "warranty_warning": "Do not attempt pipe repair yourself. Temporary pipe clamps are "
                            "acceptable to reduce flow until a plumber arrives. [SIMULATED]",
        "dispatch_suggestion": "RapidRooter 24/7 Emergency Plumbing (ETA ~20 min) [SIMULATED]",
        "safety_guidance": (
            "1. Locate and close the nearest shut-off valve to the burst pipe.\n"
            "2. The main water valve will be closed automatically.\n"
            "3. Turn off electricity to affected areas if water is near outlets.\n"
            "4. Open faucets to drain remaining water from pipes.\n"
            "5. Move valuables away from the water."
        ),
    },
}

# Mapping: emergency_type -> list of IoT actions to take
_EMERGENCY_IOT_ACTIONS: dict[str, list[tuple[str, str, str]]] = {
    # (device_key, new_state, description)
    "water_heater_rupture": [
        ("main_water_valve", "CLOSED_BY_AEGIS", "Closed main water shutoff valve [SIMULATED]"),
        ("water_heater_valve", "CLOSED_BY_AEGIS", "Closed water heater isolation valve [SIMULATED]"),
    ],
    "electrical_surge": [
        ("smart_breaker_zone_3", "ISOLATED_BY_AEGIS", "Isolated breaker zone 3 to prevent arc fault [SIMULATED]"),
    ],
    "gas_leak": [
        ("gas_main_valve", "CLOSED_BY_AEGIS", "Closed main gas shutoff valve [SIMULATED]"),
        ("gas_water_heater_valve", "CLOSED_BY_AEGIS", "Closed water heater gas valve [SIMULATED]"),
        ("hvac_system", "SHUTDOWN_BY_AEGIS", "Shut down HVAC to prevent gas circulation [SIMULATED]"),
    ],
    "hvac_failure": [
        ("hvac_system", "SHUTDOWN_BY_AEGIS", "Shut down HVAC system for safety [SIMULATED]"),
    ],
    "fire_smoke": [
        ("sprinkler_system", "ACTIVATED_BY_AEGIS", "Activated fire sprinkler system [SIMULATED]"),
        ("hvac_system", "SHUTDOWN_BY_AEGIS", "Shut down HVAC to prevent smoke circulation [SIMULATED]"),
        ("gas_main_valve", "CLOSED_BY_AEGIS", "Closed gas main valve as fire precaution [SIMULATED]"),
    ],
    "carbon_monoxide": [
        ("gas_main_valve", "CLOSED_BY_AEGIS", "Closed gas main valve — potential CO source [SIMULATED]"),
        ("hvac_system", "SHUTDOWN_BY_AEGIS", "Shut down HVAC — potential CO source [SIMULATED]"),
    ],
    "security_breach": [
        ("front_door_lock", "LOCKED_BY_AEGIS", "Locked front door [SIMULATED]"),
        ("back_door_lock", "LOCKED_BY_AEGIS", "Locked back door [SIMULATED]"),
        ("garage_door", "CLOSED_BY_AEGIS", "Closed garage door [SIMULATED]"),
        ("alarm_system", "ALARM_TRIGGERED_BY_AEGIS", "Triggered alarm system [SIMULATED]"),
    ],
    "flooding": [
        ("main_water_valve", "CLOSED_BY_AEGIS", "Closed main water shutoff valve [SIMULATED]"),
    ],
    "appliance_malfunction": [],   # user should unplug manually — no auto action
    "garage_door_malfunction": [
        ("garage_door", "LOCKED_OUT_BY_AEGIS", "Disabled garage door motor for safety [SIMULATED]"),
    ],
    "pipe_burst": [
        ("main_water_valve", "CLOSED_BY_AEGIS", "Closed main water shutoff valve [SIMULATED]"),
    ],
}

# Types requiring explicit confirmation before auto-action
_CONFIRM_REQUIRED = {"electrical_surge"}

ALLOWED_EMERGENCY_TYPES = sorted(POLICY_DB.keys())

# ---------------------------------------------------------------------------
# Scam call analysis
# ---------------------------------------------------------------------------
# Coercion markers: (phrase, description, weight)
_COERCION_MARKERS: list[tuple[str, str, int]] = [
    ("gift card",          "Demands payment via untraceable gift cards", 45),
    ("wire transfer",      "Demands immediate irreversible wire transfer", 40),
    ("safe account",       "Classic 'move funds to a safe reserve account' scam script", 45),
    ("arrest warrant",     "Legal intimidation / false law-enforcement threat", 40),
    ("verification code",  "OTP / 2FA harvesting attempt", 35),
    ("stay on the line",   "Isolation tactic: forbidding user from hanging up", 25),
    ("immediately",        "Artificial time-pressure coercion marker", 15),
    ("do not hang up",     "Isolation tactic variant", 25),
    ("your account will be frozen", "Threat of financial harm", 30),
    ("send money",         "Direct money transfer demand", 40),
    ("western union",      "Untraceable money transfer demand", 40),
    ("bitcoin",            "Cryptocurrency payment demand", 35),
    ("social security number", "PII harvesting attempt", 35),
    ("remote access",      "Attempting to gain remote computer access", 40),
    ("teamviewer",         "Attempting to gain remote computer access", 40),
    ("anydesk",            "Attempting to gain remote computer access", 40),
]

# De-escalating phrases that lower the score (legitimate callers say these)
_DEESCALATION_PHRASES: list[tuple[str, str, int]] = [
    ("hang up and call the number on your card",
     "Legitimate advice: caller tells user to verify independently", -20),
    ("call us back at the number on our website",
     "Legitimate advice: directs to official channels", -15),
    ("take your time",
     "No time pressure — less likely to be a scam", -10),
    ("we will never ask for your password",
     "Legitimate institution disclaimer", -10),
]


def analyze_live_scam_call(
    transcript: str,
    claimed_institution: str,
    caller_number: str = "Unknown",
) -> dict[str, Any]:
    """
    Analyse a call transcript for social-engineering / coercion markers.

    Returns risk score (0-99), matched markers, number-mismatch flag,
    safe next steps, and a spoken interjection for Alexa+.
    Method is always 'text-heuristic' — no audio analysis, no deepfake detection.
    """
    lower = transcript.lower()
    matched: list[dict[str, Any]] = []
    score = 10  # base

    # Check coercion markers
    for phrase, reason, weight in _COERCION_MARKERS:
        if phrase in lower:
            matched.append({"phrase": phrase, "reason": reason, "weight": weight})
            score += weight

    # Check de-escalation phrases
    for phrase, reason, weight in _DEESCALATION_PHRASES:
        if phrase in lower:
            matched.append({"phrase": phrase, "reason": reason, "weight": weight})
            score += weight  # weight is negative

    # Number cross-check against SIMULATED directory
    number_check: dict[str, Any] = {"simulated": True}
    inst_key = None
    for name in OFFICIAL_NUMBERS:
        if name.lower() in claimed_institution.lower():
            inst_key = name
            break

    if inst_key:
        official = OFFICIAL_NUMBERS[inst_key].get("official_numbers", [])
        if caller_number and caller_number not in ("Unknown", ""):
            if caller_number not in official:
                number_check["match"] = False
                number_check["detail"] = (
                    f"Caller number {caller_number} does NOT match any official "
                    f"{inst_key} numbers: {official}"
                )
                score += 20
            else:
                number_check["match"] = True
                number_check["detail"] = f"Caller number matches official {inst_key} directory."
        else:
            number_check["match"] = None
            number_check["detail"] = "Caller number not provided — cannot verify."
    else:
        number_check["match"] = None
        number_check["detail"] = (
            f"Institution '{claimed_institution}' not found in SIMULATED directory. "
            "Cannot cross-check number."
        )

    score = max(0, min(score, 99))

    if score >= 60:
        threat_level = "CRITICAL_SCAM"
    elif score >= 35:
        threat_level = "SUSPICIOUS"
    else:
        threat_level = "LOW_RISK"

    if score >= 50:
        spoken = (
            f"Warning: This call shows a {score}% match with known "
            f"{claimed_institution} impersonation scams. Do not share any codes, "
            "passwords, or move money. Hang up and call the official number yourself."
        )
    else:
        spoken = (
            "This call appears lower risk, but never share one-time passcodes, "
            "passwords, or financial information over the phone. If in doubt, "
            "hang up and call the official number on your card or statement."
        )

    safe_next_steps = [
        "Hang up the call immediately.",
        f"Call {claimed_institution} directly using the number on your card or their official website.",
        "Never share verification codes, passwords, or Social Security numbers over the phone.",
        "Never buy gift cards or send wire transfers based on a phone call.",
        "Report the call to the FTC at reportfraud.ftc.gov.",
    ]

    result = {
        "method": "text-heuristic",
        "threat_level": threat_level,
        "risk_score": score,
        "claimed_institution": claimed_institution,
        "caller_number": caller_number,
        "number_check": number_check,
        "matched_markers": [m["reason"] for m in matched],
        "matched_markers_detail": matched,
        "spoken_interjection": spoken,
        "safe_next_steps": safe_next_steps,
        "counter_questions": [
            f"Ask the caller: 'What are the last 4 digits of my {claimed_institution} account?'",
            "Say: 'I am hanging up now and calling the official number on the back of my card.'",
        ],
        "simulated_components": ["phone_directory"],
    }

    # Store for potential claim compilation
    with _LOCK:
        _STORED_ANALYSES[f"scam_{_now_utc()}"] = result

    return result


# ---------------------------------------------------------------------------
# Home emergency arbitration — ALL home components
# ---------------------------------------------------------------------------

def _record_sensor_snapshot(emergency_type: str) -> dict:
    """Simulate sensor readings for the given emergency type and record a time-series entry."""
    ts = _now_utc()

    # Adjust sensor readings based on emergency type (SIMULATED)
    if emergency_type in ("water_heater_rupture", "pipe_burst", "flooding"):
        SENSOR_STATE["basement_humidity_pct"] = 92.3
        SENSOR_STATE["water_flow_rate_gpm"] = 8.5
        SENSOR_STATE["water_pressure_psi"] = 15.0
    elif emergency_type == "electrical_surge":
        SENSOR_STATE["voltage_v"] = 185.0
        SENSOR_STATE["electrical_load_kw"] = 12.8
    elif emergency_type == "gas_leak":
        SENSOR_STATE["gas_level_ppm"] = 450.0
    elif emergency_type == "carbon_monoxide":
        SENSOR_STATE["co_level_ppm"] = 120.0
    elif emergency_type == "fire_smoke":
        SENSOR_STATE["smoke_density_pct"] = 65.0
        SENSOR_STATE["indoor_temperature_f"] = 110.0
    elif emergency_type == "hvac_failure":
        SENSOR_STATE["indoor_temperature_f"] = 95.0 if SENSOR_STATE["outdoor_temperature_f"] > 80 else 42.0

    SENSOR_STATE["last_updated"] = ts

    snapshot = {**SENSOR_STATE, "timestamp": ts, "emergency_type": emergency_type, "simulated": True}
    SENSOR_SERIES.append(snapshot)
    return snapshot


def arbitrate_home_emergency(
    emergency_type: str,
    user_observation: str,
    confirm_electrical: bool = False,
) -> dict[str, Any]:
    """
    Contain a home emergency (SIMULATED) and look up insurance/warranty coverage.

    Supports all home component types.  Only reversible IoT actions are automatic.
    Electrical isolation requires explicit confirmation via confirm_electrical=True.

    Returns safety guidance, IoT actions taken, policy clause, deductible, warranty
    warning, dispatch suggestion, and a claim reference ID.
    """
    if emergency_type not in POLICY_DB:
        return {
            "error": f"Unknown emergency type: '{emergency_type}'",
            "allowed_types": ALLOWED_EMERGENCY_TYPES,
            "hint": "Please specify one of the allowed emergency types.",
        }

    with _LOCK:
        # 1. Safety guidance first
        policy = POLICY_DB[emergency_type]

        # 2. Sensor snapshot (SIMULATED)
        sensor_snapshot = _record_sensor_snapshot(emergency_type)

        # 3. IoT containment actions (SIMULATED)
        actions_taken: list[str] = []
        actions_config = _EMERGENCY_IOT_ACTIONS.get(emergency_type, [])

        needs_confirm = emergency_type in _CONFIRM_REQUIRED
        if needs_confirm and not confirm_electrical:
            # Don't auto-act — require confirmation
            actions_taken.append(
                f"⚠ Electrical isolation requires explicit confirmation. "
                f"Call again with confirm_electrical=true to proceed. [SIMULATED]"
            )
        else:
            for device_key, new_state, description in actions_config:
                if device_key in IOT_STATE:
                    IOT_STATE[device_key]["state"] = new_state
                    actions_taken.append(description)

        # Post-containment sensor adjustment
        if emergency_type in ("water_heater_rupture", "pipe_burst", "flooding"):
            if any("water" in a.lower() and "closed" in a.lower() for a in actions_taken):
                SENSOR_STATE["water_flow_rate_gpm"] = 0.0

        # 4. Generate claim reference
        claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"

        result = {
            "claim_reference_id": claim_id,
            "emergency_type": emergency_type,
            "timestamp_utc": _now_utc(),
            "safety_guidance": policy["safety_guidance"],
            "iot_containment_actions": actions_taken,
            "current_iot_state": {k: v["state"] for k, v in IOT_STATE.items()},
            "sensor_snapshot": sensor_snapshot,
            "policy_arbitration": {
                "clause": policy["clause"],
                "covered": policy["covered"],
                "deductible_usd": policy["deductible_usd"],
                "warranty_warning": policy["warranty_warning"],
                "dispatch_suggestion": policy["dispatch_suggestion"],
            },
            "user_observation": user_observation,
            "simulated_components": [
                "iot_devices", "sensors", "insurance_policy",
                "warranty_terms", "dispatch_vendor",
            ],
            "disclaimer": (
                "This is a SIMULATED emergency response. In a real emergency, "
                "call 911 or your local emergency services immediately."
            ),
        }

        _STORED_CLAIMS[claim_id] = result
        return result


# ---------------------------------------------------------------------------
# Forensic claim compilation (JSON + PDF)
# ---------------------------------------------------------------------------

def compile_forensic_claim(claim_reference_id: str | None = None) -> dict[str, Any]:
    """
    Compile a forensic claim packet from stored data.

    Writes out/claim_<ID>.json and out/claim_<ID>.pdf.
    All sensor and device data is marked SIMULATED.
    The output is 'a draft for your review' — not legal or insurance advice.
    """
    out_dir = Path(__file__).resolve().parent.parent / "out"
    out_dir.mkdir(exist_ok=True)

    with _LOCK:
        # Find the claim
        if claim_reference_id and claim_reference_id in _STORED_CLAIMS:
            claim_data = _STORED_CLAIMS[claim_reference_id]
        elif _STORED_CLAIMS:
            # Use the most recent
            claim_reference_id = list(_STORED_CLAIMS.keys())[-1]
            claim_data = _STORED_CLAIMS[claim_reference_id]
        else:
            return {
                "error": "No claim data found. Run arbitrate_home_emergency first.",
                "available_claims": list(_STORED_CLAIMS.keys()),
            }

        packet = {
            "meta": {
                "generated_utc": _now_utc(),
                "claim_reference_id": claim_reference_id,
                "status": "DRAFT_FOR_YOUR_REVIEW",
                "disclaimer": (
                    "This claim packet is a SIMULATED draft for review purposes only. "
                    "It does not constitute legal or insurance advice. All sensor readings, "
                    "device states, and policy data are SIMULATED."
                ),
            },
            "claim": claim_data,
            "sensor_time_series": SENSOR_SERIES.copy(),
            "all_stored_analyses": dict(_STORED_ANALYSES),
        }

    # Write JSON
    json_path = out_dir / f"claim_{claim_reference_id}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(packet, f, indent=2, default=str)

    # Write PDF
    pdf_path = out_dir / f"claim_{claim_reference_id}.pdf"
    _write_claim_pdf(pdf_path, packet)

    return {
        "claim_reference_id": claim_reference_id,
        "status": "DRAFT_FOR_YOUR_REVIEW",
        "json_path": str(json_path),
        "pdf_path": str(pdf_path),
        "disclaimer": packet["meta"]["disclaimer"],
    }


def _write_claim_pdf(pdf_path: Path, packet: dict) -> None:
    """Generate a PDF claim report using reportlab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        )

        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ClaimTitle", parent=styles["Heading1"],
            fontSize=18, textColor=HexColor("#1a237e"),
        )
        heading_style = ParagraphStyle(
            "ClaimHeading", parent=styles["Heading2"],
            fontSize=14, textColor=HexColor("#283593"),
        )
        body_style = styles["Normal"]
        warning_style = ParagraphStyle(
            "Warning", parent=styles["Normal"],
            textColor=HexColor("#b71c1c"), fontSize=10,
        )

        elements: list = []
        meta = packet["meta"]
        claim = packet.get("claim", {})

        # Title
        elements.append(Paragraph("AegisMCP -- Forensic Claim Report", title_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            f"<b>Claim ID:</b> {meta['claim_reference_id']} &nbsp;&nbsp; "
            f"<b>Generated:</b> {meta['generated_utc']}", body_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "[SIMULATED] -- Draft for your review. Not legal or insurance advice.",
            warning_style))
        elements.append(Spacer(1, 18))

        # Emergency details
        if claim:
            elements.append(Paragraph("Emergency Details", heading_style))
            elements.append(Spacer(1, 6))
            details = [
                ["Emergency Type", claim.get("emergency_type", "N/A")],
                ["Timestamp (UTC)", claim.get("timestamp_utc", "N/A")],
                ["User Observation", claim.get("user_observation", "N/A")],
            ]
            t = Table(details, colWidths=[2*inch, 4.5*inch])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), HexColor("#e8eaf6")),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#9fa8da")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 12))

            # Safety guidance
            elements.append(Paragraph("Safety Guidance", heading_style))
            elements.append(Spacer(1, 6))
            guidance = claim.get("safety_guidance", "")
            for line in guidance.split("\n"):
                if line.strip():
                    elements.append(Paragraph(line.strip().replace("—", "--"), body_style))
            elements.append(Spacer(1, 12))

            # IoT Actions
            elements.append(Paragraph("IoT Containment Actions [SIMULATED]", heading_style))
            elements.append(Spacer(1, 6))
            for action in claim.get("iot_containment_actions", []):
                elements.append(Paragraph(f"&bull; {action.replace('—', '--')}", body_style))
            elements.append(Spacer(1, 12))

            # Policy
            pol = claim.get("policy_arbitration", {})
            if pol:
                elements.append(Paragraph("Insurance Policy Lookup [SIMULATED]", heading_style))
                elements.append(Spacer(1, 6))
                pol_rows = [
                    ["Clause", str(pol.get("clause", "N/A")).replace("—", "--")],
                    ["Covered", str(pol.get("covered", "N/A"))],
                    ["Deductible", f"${pol.get('deductible_usd', 'N/A')}"],
                    ["Warranty Warning", str(pol.get("warranty_warning", "N/A")).replace("—", "--")],
                    ["Dispatch", str(pol.get("dispatch_suggestion", "N/A")).replace("—", "--")],
                ]
                t2 = Table(pol_rows, colWidths=[1.8*inch, 4.7*inch])
                t2.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (0, -1), HexColor("#fff3e0")),
                    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#ffcc80")),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                elements.append(t2)
                elements.append(Spacer(1, 12))

        # Sensor time-series
        series = packet.get("sensor_time_series", [])
        if series:
            elements.append(Paragraph("Sensor Time Series [SIMULATED]", heading_style))
            elements.append(Spacer(1, 6))
            for i, snap in enumerate(series[-5:]):  # last 5 entries
                elements.append(Paragraph(
                    f"<b>Entry {i+1}</b> @ {snap.get('timestamp', 'N/A')} -- "
                    f"Humidity: {snap.get('basement_humidity_pct')}%, "
                    f"Flow: {snap.get('water_flow_rate_gpm')} GPM, "
                    f"Temp: {snap.get('indoor_temperature_f')}F, "
                    f"CO: {snap.get('co_level_ppm')} ppm, "
                    f"Smoke: {snap.get('smoke_density_pct')}%",
                    body_style,
                ))
            elements.append(Spacer(1, 12))

        # Footer
        elements.append(Spacer(1, 24))
        elements.append(Paragraph(
            "This document was generated by AegisMCP, a hackathon prototype. "
            "All data marked SIMULATED is fictional. This is not legal, insurance, "
            "or emergency advice. In a real emergency, call 911.",
            warning_style,
        ))

        doc.build(elements)

    except ImportError:
        # If reportlab not available, write a text fallback
        with open(pdf_path.with_suffix(".txt"), "w", encoding="utf-8") as f:
            f.write("AegisMCP Forensic Claim Report (text fallback — reportlab not installed)\n")
            f.write("=" * 70 + "\n")
            f.write(json.dumps(packet, indent=2, default=str))


# ---------------------------------------------------------------------------
# Resources (policy and sensor telemetry)
# ---------------------------------------------------------------------------

def get_policy_json() -> str:
    """Return the full SIMULATED insurance policy database as JSON."""
    return json.dumps({
        "_meta": {
            "simulated": True,
            "description": "SIMULATED household insurance & warranty policy database",
            "disclaimer": "Not real insurance. Not legal advice.",
        },
        "policies": POLICY_DB,
    }, indent=2)


def get_sensor_json() -> str:
    """Return the current SIMULATED sensor telemetry as JSON."""
    with _LOCK:
        return json.dumps({
            "_meta": {"simulated": True, "description": "SIMULATED smart-home sensor telemetry"},
            "current": SENSOR_STATE,
            "iot_devices": {k: v for k, v in IOT_STATE.items()},
            "time_series_count": len(SENSOR_SERIES),
            "recent_series": SENSOR_SERIES[-10:] if SENSOR_SERIES else [],
        }, indent=2, default=str)


# ---------------------------------------------------------------------------
# Demo reset
# ---------------------------------------------------------------------------

def reset_demo() -> dict[str, str]:
    """Reset all SIMULATED state to baseline: valves open, sensors normal, claims cleared."""
    global IOT_STATE, SENSOR_STATE
    with _LOCK:
        IOT_STATE.clear()
        IOT_STATE.update(copy.deepcopy(_IOT_BASELINE))
        SENSOR_STATE.clear()
        SENSOR_STATE.update(copy.deepcopy(_SENSOR_BASELINE))
        SENSOR_STATE["last_updated"] = _now_utc()
        SENSOR_SERIES.clear()
        _STORED_ANALYSES.clear()
        _STORED_CLAIMS.clear()
    return {
        "status": "reset_complete",
        "message": "All SIMULATED state reset to baseline. Valves open, sensors normal, claims cleared.",
        "timestamp_utc": _now_utc(),
    }
