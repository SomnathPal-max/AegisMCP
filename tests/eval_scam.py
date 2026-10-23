"""
AegisMCP Scam Evaluation — eval_scam.py

Runs the scam test set through analyze_live_scam_call and prints honest results.
This is a small hand-made test set — not a production benchmark.

Usage: python -m tests.eval_scam
"""

import io
import json
import os
import sys

# Windows cp1252 console safety
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from server.aegis_core import analyze_live_scam_call, reset_demo


def run_eval():
    test_file = os.path.join(os.path.dirname(__file__), "scam_cases.json")
    with open(test_file, encoding="utf-8") as f:
        cases = json.load(f)

    reset_demo()

    results = {
        "total": len(cases),
        "scam_caught": 0,
        "scam_missed": 0,
        "legit_correct": 0,
        "legit_false_alarm": 0,
        "ambiguous_flagged": 0,
        "ambiguous_unflagged": 0,
        "details": [],
    }

    print(f"\nAegisMCP Scam Evaluation — {len(cases)} cases")
    print("=" * 70)
    print(f"{'ID':<12} {'Label':<12} {'Expected':<16} {'Got':<16} {'Score':>5}  {'OK?'}")
    print("-" * 70)

    for case in cases:
        reset_demo()
        r = analyze_live_scam_call(
            transcript=case["transcript"],
            claimed_institution=case["institution"],
            caller_number=case.get("caller_number", "Unknown"),
        )

        threat = r["threat_level"]
        score = r["risk_score"]
        label = case["label"]
        expected = case["expected_level"]

        # Determine if result is correct
        ok = False
        if label == "scam":
            if threat == "CRITICAL_SCAM":
                results["scam_caught"] += 1
                ok = True
            else:
                results["scam_missed"] += 1
        elif label == "legitimate":
            if threat == "LOW_RISK":
                results["legit_correct"] += 1
                ok = True
            else:
                results["legit_false_alarm"] += 1
        elif label == "ambiguous":
            if threat in ("SUSPICIOUS", "CRITICAL_SCAM"):
                results["ambiguous_flagged"] += 1
                ok = True  # We want ambiguous cases flagged for user caution
            else:
                results["ambiguous_unflagged"] += 1

        marker = "[OK]" if ok else "[MISMATCH]"
        print(f"{case['id']:<12} {label:<12} {expected:<16} {threat:<16} {score:>5}  {marker}")

        results["details"].append({
            "id": case["id"],
            "label": label,
            "expected": expected,
            "got": threat,
            "score": score,
            "matched_markers": r["matched_markers"],
            "ok": ok,
        })

    print("-" * 70)
    print(f"RESULTS (hand-made test set, {len(cases)} cases):")
    print(f"  Scams caught:              {results['scam_caught']}/8")
    print(f"  Scams missed:              {results['scam_missed']}/8")
    print(f"  Legitimate correct:        {results['legit_correct']}/8")
    print(f"  Legitimate false alarms:   {results['legit_false_alarm']}/8")
    print(f"  Ambiguous flagged:         {results['ambiguous_flagged']}/4")
    print(f"  Ambiguous unflagged:       {results['ambiguous_unflagged']}/4")
    print("=" * 70 + "\n")

    return results


if __name__ == "__main__":
    run_eval()
