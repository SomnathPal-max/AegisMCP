"""
tests/test_realism.py - Test suite for AegisMCP Realistic Capabilities:
- Carrier-Grade Phone Intelligence (VoIP, Toll-free, Spoof heuristics)
- Home Assistant Hardware Bridge (Matter/Zigbee graceful fallback)
- Semantic Policy RAG (HO-3 clauses, deductibles, warranty exclusions)
- SHA-256 Cryptographic Forensic Ledger (Tamper-evident audit trail)
- Caregiver & Family Alert Dispatch
"""

import json
import os
import sys
from pathlib import Path
import pytest

# Ensure project root is on path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from server.phone_intel import (
    lookup_phone_intelligence,
    inspect_caller_intelligence,
    sanitize_number,
    extract_area_code,
)
from server.hass_bridge import (
    is_configured as hass_is_configured,
    dispatch_hardware_containment_sync,
    ENTITY_MAP,
)
from server.policy_rag import get_policy_rag, PolicyRAG
from server.caregiver_notifier import dispatch_caregiver_alert
from server.aegis_core import (
    arbitrate_home_emergency,
    analyze_live_scam_call,
    compile_forensic_claim,
    reset_demo,
)


class TestPhoneIntelligence:
    def test_sanitize_and_area_code(self):
        assert sanitize_number("(800) 555-0199") == "+18005550199"
        assert extract_area_code("+18005550199") == "800"
        assert extract_area_code("+12125550144") == "212"

    def test_toll_free_identification(self):
        intel = lookup_phone_intelligence("+1-888-555-0144", "Chase")
        assert intel["is_toll_free"] is True
        assert intel["line_type"] == "toll_free"

    def test_voip_prefix_detection(self):
        # 500 / 533 is a known virtual non-geographic VoIP prefix
        intel = lookup_phone_intelligence("+1-500-555-0188", "Chase")
        assert intel["is_voip"] is True
        assert intel["line_type"] == "voip"
        assert intel["spoofing_risk_score"] >= 25

    def test_international_routing_detection(self):
        intel = lookup_phone_intelligence("+44-20-7946-0991", "Bank of America")
        assert intel["line_type"] == "international"
        assert intel["spoofing_risk_score"] >= 30


class TestHomeAssistantBridge:
    def test_fallback_when_unconfigured(self):
        # In test environment, HASS_URL is not set
        res = dispatch_hardware_containment_sync("water_heater_rupture")
        assert "SIMULATED" in res["mode"]
        assert res["configured"] is False

    def test_entity_map_keys(self):
        assert "water_valve" in ENTITY_MAP
        assert "gas_valve" in ENTITY_MAP
        assert "hvac_climate" in ENTITY_MAP
        assert "electrical_breaker" in ENTITY_MAP


class TestSemanticPolicyRAG:
    def setup_method(self):
        self.rag = get_policy_rag()

    def test_water_heater_clause_retrieval(self):
        summary = self.rag.get_coverage_summary("water_heater_rupture", "water pooling around 50 gallon tank")
        assert summary["covered"] is True
        assert summary["clause_id"] in ("SEC_4_2_B", "SEC_4_1_A")
        assert "warranty" in summary["warranty_warning"].lower()
        assert summary["deductible_usd"] == 500

    def test_electrical_surge_clause_retrieval(self):
        summary = self.rag.get_coverage_summary("electrical_surge", "sparking outlets and tripped smart panel breaker")
        assert summary["covered"] is True
        assert summary["clause_id"] == "SEC_6_1_A"
        assert summary["deductible_usd"] == 250

    def test_gas_leak_clause_retrieval(self):
        summary = self.rag.get_coverage_summary("gas_leak", "strong rotten egg smell in kitchen")
        assert summary["covered"] is True
        assert summary["clause_id"] == "SEC_7_3_A"
        assert summary["deductible_usd"] == 0
        assert summary["diy_voids_warranty"] is True

    def test_garage_door_clause_retrieval(self):
        summary = self.rag.get_coverage_summary("garage_door_malfunction", "torsion spring snapped")
        assert summary["clause_id"] == "SEC_5_4_A"
        assert summary["deductible_usd"] == 100


class TestCaregiverAlerting:
    def test_dispatch_caregiver_simulated(self):
        res = dispatch_caregiver_alert(
            incident_type="pipe_burst",
            severity="CRITICAL",
            summary="Main basement pipe ruptured, auto-shutoff engaged",
            caregiver_phone="+1-555-019-9944",
        )
        assert res["dispatched_successfully"] is True
        assert "CRITICAL" in res["alert_text"]
        assert res["recipient_phone"] == "+1-555-019-9944"
        assert "SIMULATED" in res["mode"]


class TestCryptographicForensicLedger:
    def setup_method(self):
        reset_demo()

    def test_sha256_forensic_digest_generation(self):
        emg = arbitrate_home_emergency("pipe_burst", "Pipes ruptured in kitchen wall")
        claim = compile_forensic_claim(emg["claim_reference_id"])

        assert "forensic_hash_sha256" in claim
        assert len(claim["forensic_hash_sha256"]) == 64  # Valid SHA-256 hex string

        # Check that forensic ledger file was created and contains the hash
        ledger_path = Path(claim["tamper_evident_ledger"])
        assert ledger_path.exists()

        with open(ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            last_entry = json.loads(lines[-1])
            assert last_entry["forensic_hash_sha256"] == claim["forensic_hash_sha256"]
            assert last_entry["claim_reference_id"] == emg["claim_reference_id"]
            assert last_entry["tamper_evident_status"] == "COMMITTED_IMMUTABLE"

    def test_integrated_arbitration_includes_realism_fields(self):
        res = arbitrate_home_emergency("gas_leak", "Natural gas odor near furnace")
        assert "policy_rag" in res
        assert "hardware_bridge" in res
        assert "caregiver_alert" in res
        assert res["policy_rag"]["clause_id"] == "SEC_7_3_A"
        assert res["caregiver_alert"]["dispatched_successfully"] is True
