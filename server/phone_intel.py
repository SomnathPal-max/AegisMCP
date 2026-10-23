"""
AegisMCP Phone Intelligence — phone_intel.py

Carrier-grade caller ID inspection:
- VoIP / virtual burner line detection
- Live Twilio / NumVerify API integration if keys configured
- Offline NPA-NXX North American area code & toll-free database
- Spoofing risk scoring: flags VoIP / international mismatch for institutional claims
"""

from __future__ import annotations

import os
import re
from typing import Any
import httpx

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY", "")

# Standard US/Canada toll-free area codes
TOLL_FREE_AREAS = {"800", "888", "877", "866", "855", "844", "833"}

# Common VoIP service exchange patterns / high-risk virtual prefixes
KNOWN_VOIP_PREFIXES = {
    # Non-geographic / virtual assignment pools
    "500", "521", "522", "533", "544", "566", "577", "588"
}


def sanitize_number(raw: str) -> str:
    """Strip formatting characters, retaining leading + and digits."""
    cleaned = re.sub(r"[^\d+]", "", raw.strip())
    if not cleaned.startswith("+") and len(cleaned) == 10:
        cleaned = "+1" + cleaned
    return cleaned


def extract_area_code(number: str) -> str | None:
    """Extract 3-digit area code from a North American E.164 number (+1NXXNXXXXXX)."""
    clean = sanitize_number(number)
    if clean.startswith("+1") and len(clean) >= 5:
        return clean[2:5]
    elif len(clean) == 10:
        return clean[:3]
    return None


async def lookup_carrier_live(phone_number: str) -> dict[str, Any] | None:
    """Query live Twilio Lookup API or NumVerify API if credentials exist."""
    clean = sanitize_number(phone_number)

    # 1. Try Twilio Lookup v2
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        url = f"https://lookups.twilio.com/v2/PhoneNumbers/{clean}?Fields=line_type_intelligence,caller_name"
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
                if resp.status_code == 200:
                    data = resp.json()
                    lt = data.get("line_type_intelligence", {})
                    return {
                        "source": "Twilio Lookup v2 (LIVE)",
                        "carrier_name": lt.get("carrier_name", "Unknown"),
                        "line_type": lt.get("type", "unknown").lower(),
                        "caller_name": data.get("caller_name", {}).get("caller_name"),
                        "valid": data.get("valid", True),
                    }
        except Exception:
            pass

    # 2. Try NumVerify API
    if NUMVERIFY_API_KEY:
        url = f"https://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={clean}"
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "source": "NumVerify API (LIVE)",
                        "carrier_name": data.get("carrier", "Unknown"),
                        "line_type": data.get("line_type", "unknown").lower(),
                        "country_code": data.get("country_code"),
                        "valid": data.get("valid", True),
                    }
        except Exception:
            pass

    return None


def inspect_caller_intelligence(phone_number: str, claimed_institution: str) -> dict[str, Any]:
    """
    Perform synchronous carrier intelligence heuristic evaluation.
    Determines line type, spoofing risk, and risk score adjustments.
    """
    clean = sanitize_number(phone_number)
    area = extract_area_code(clean)

    is_toll_free = area in TOLL_FREE_AREAS
    is_voip_prefix = area in KNOWN_VOIP_PREFIXES
    is_international = not clean.startswith("+1") and clean.startswith("+")

    flags: list[str] = []
    risk_adjustment = 0

    # Institution classification
    is_major_bank = any(b in claimed_institution.lower() for b in [
        "chase", "bank of america", "wells fargo", "citi", "capital one", "irs", "social security"
    ])

    if is_toll_free:
        line_type = "toll_free"
        flags.append("Standard North American toll-free line.")
    elif is_voip_prefix:
        line_type = "voip"
        flags.append("Non-geographic virtual / VoIP line detected.")
        risk_adjustment += 25
    elif is_international:
        line_type = "international"
        flags.append(f"Foreign country code ({clean[:3]}...) detected.")
        if is_major_bank:
            flags.append("Major domestic US institution calling from foreign country code.")
            risk_adjustment += 30
    else:
        line_type = "standard_geographic"

    # Specific spoofing heuristics
    if is_major_bank and line_type == "voip":
        flags.append("High-risk mismatch: Financial institution claiming to call from virtual VoIP line.")
        risk_adjustment += 25

    return {
        "formatted_number": clean,
        "area_code": area,
        "is_toll_free": is_toll_free,
        "is_voip": line_type == "voip",
        "line_type": line_type,
        "risk_adjustment": risk_adjustment,
        "spoofing_risk_score": min(risk_adjustment, 100),
        "intel_flags": flags,
        "engine": "carrier-intelligence-heuristics",
    }


# Convenient alias
def lookup_phone_intelligence(phone_number: str, claimed_institution: str = "Unknown") -> dict[str, Any]:
    return inspect_caller_intelligence(phone_number, claimed_institution)

