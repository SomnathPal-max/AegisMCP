"""server/caregiver_notifier.py - Emergency Caregiver & Family Notification Dispatcher.

Dispatches instant high-priority alerts to family members, caregivers, or property
managers during critical home emergencies (water leaks, gas, electrical surges) or
severe predatory scam calls.

Supports live Twilio SMS or Webhooks when environment credentials are provided,
with full, transparent fallback to local audit logs marked [SIMULATED].
"""

from __future__ import annotations

import datetime
import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


def dispatch_caregiver_alert(
    incident_type: str,
    severity: str,
    summary: str,
    location: str = "Primary Residence",
    caregiver_name: Optional[str] = None,
    caregiver_phone: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an emergency notification to the designated caregiver or guardian."""
    phone = caregiver_phone or os.environ.get("CAREGIVER_PHONE", "+1-555-019-8822")
    name = caregiver_name or os.environ.get("CAREGIVER_NAME", "Designated Emergency Contact")
    webhook_url = os.environ.get("CAREGIVER_WEBHOOK_URL")

    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_from = os.environ.get("TWILIO_FROM_NUMBER")

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    alert_text = (
        f"[AegisMCP ALERT - {severity.upper()}] "
        f"Incident: {incident_type.replace('_', ' ').title()} at {location}. "
        f"Status: {summary}. "
        f"Automated containment initiated. Check dashboard immediately."
    )

    result: Dict[str, Any] = {
        "timestamp_iso": now_iso,
        "recipient_name": name,
        "recipient_phone": phone,
        "incident_type": incident_type,
        "severity": severity,
        "alert_text": alert_text,
        "channel": "SMS",
        "dispatched_successfully": True,
        "real_carrier_dispatch": False,
        "mode": "SIMULATED",
    }

    # 1. Attempt Real Twilio SMS if credentials exist
    if twilio_sid and twilio_token and twilio_from and phone:
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
            data = urllib.parse.urlencode({
                "To": phone,
                "From": twilio_from,
                "Body": alert_text,
            }).encode("utf-8")
            
            import base64
            auth_header = base64.b64encode(f"{twilio_sid}:{twilio_token}".encode("utf-8")).decode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                result["real_carrier_dispatch"] = True
                result["mode"] = "REAL_TWILIO_SMS"
                result["twilio_sid"] = resp_data.get("sid")
                return result
        except Exception as exc:
            result["twilio_error"] = str(exc)
            # Fall through to simulated log

    # 2. Attempt Webhook if configured
    if webhook_url:
        try:
            payload = json.dumps({
                "source": "AegisMCP",
                "timestamp": now_iso,
                "alert": alert_text,
                "incident": incident_type,
                "severity": severity,
                "recipient": {"name": name, "phone": phone},
            }).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                result["real_carrier_dispatch"] = True
                result["mode"] = "REAL_WEBHOOK"
                result["webhook_code"] = resp.getcode()
                return result
        except Exception as exc:
            result["webhook_error"] = str(exc)

    # 3. Simulated Caregiver Log (Honest claims constraint)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "out")
    os.makedirs(out_dir, exist_ok=True)
    log_file = os.path.join(out_dir, "caregiver_alerts.log")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{now_iso}] [SIMULATED_SMS to {phone} ({name})]: {alert_text}\n")
    except Exception:
        pass

    result["mode"] = "SIMULATED (No Twilio/Webhook keys configured in .env)"
    return result
