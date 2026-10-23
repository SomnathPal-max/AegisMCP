"""server/policy_rag.py - Semantic Retrieval-Augmented Generation for Homeowner Insurance Policies.

Matches incoming emergency observations and sensor alerts against actual HO-3
standard homeowners insurance policy clauses, deductibles, warranty exclusions,
and approved emergency dispatch networks.
"""

from __future__ import annotations

import json
import math
import os
import re
from typing import Any, Dict, List, Optional


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase alphanumeric words."""
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


class PolicyRAG:
    """In-memory semantic policy clause retriever for AegisMCP crisis arbitration."""

    def __init__(self, policy_path: Optional[str] = None):
        if not policy_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            policy_path = os.path.join(base_dir, "data", "homeowner_policy_standard.json")
        self.policy_path = policy_path
        self.policy_meta: Dict[str, Any] = {}
        self.clauses: List[Dict[str, Any]] = []
        self._load_policy()

    def _load_policy(self) -> None:
        if not os.path.isfile(self.policy_path):
            self.policy_meta = {
                "policy_form": "HO-3 Standard (Fallback)",
                "insurer": "Aegis Mutual [SIMULATED]",
                "policy_number": "POL-DEFAULT",
                "effective_year": 2026,
            }
            self.clauses = []
            return

        with open(self.policy_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.policy_meta = data.get("policy_meta", {})
            self.clauses = data.get("clauses", [])

    def query_clauses(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 2,
    ) -> List[Dict[str, Any]]:
        """Score and return top policy clauses matching the emergency query."""
        if not self.clauses:
            return []

        q_tokens = _tokenize(query)
        scored: List[tuple[float, Dict[str, Any]]] = []

        for clause in self.clauses:
            score = 0.0
            clause_cat = clause.get("category", "").lower()
            keywords = [k.lower() for k in clause.get("keywords", [])]
            title_tokens = _tokenize(clause.get("title", ""))
            text_tokens = _tokenize(clause.get("text", ""))

            # Category match bonus
            if category and clause_cat == category.lower():
                score += 3.0

            # Keyword matches (high weight)
            for kw in keywords:
                kw_tokens = _tokenize(kw)
                if kw_tokens.issubset(q_tokens):
                    score += 2.5
                elif any(t in q_tokens for t in kw_tokens):
                    score += 1.2

            # Title token overlap
            title_overlap = len(q_tokens.intersection(title_tokens))
            score += title_overlap * 1.5

            # Body text overlap (TF-IDF style dampening)
            text_overlap = len(q_tokens.intersection(text_tokens))
            score += math.log(1.0 + text_overlap)

            if score > 0.0:
                clause_copy = dict(clause)
                clause_copy["relevance_score"] = round(score, 2)
                scored.append((score, clause_copy))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def get_coverage_summary(
        self,
        incident_type: str,
        user_description: str = "",
    ) -> Dict[str, Any]:
        """Produce an actionable coverage decision, deductible quote, and warranty warning."""
        category_map = {
            "water_heater": "plumbing",
            "pipe_burst": "plumbing",
            "electrical_surge": "electrical",
            "gas_leak": "gas",
            "carbon_monoxide": "gas",
            "fire_smoke": "fire",
            "security_breach": "security",
            "flooding": "flooding",
            "hvac": "hvac",
            "garage_door": "garage",
            "appliance": "appliance",
        }
        cat = category_map.get(incident_type, "")
        combined_query = f"{incident_type} {cat} {user_description}"

        matches = self.query_clauses(combined_query, category=cat, top_k=2)

        if not matches:
            return {
                "source": "HO-3 Special Form [SIMULATED POLICY RAG]",
                "policy_number": self.policy_meta.get("policy_number", "POL-2026-9812-HG"),
                "covered": True,
                "deductible_usd": 500,
                "clause_id": "SEC_GENERAL_EMERGENCY",
                "clause_title": "General Emergency Property Loss Mitigation",
                "warranty_warning": "Preserve all damaged components for adjuster review; avoid unauthorized DIY disassembly.",
                "dispatch": "Certified Emergency Trade Dispatch (ETA ~30 min)",
                "diy_voids_warranty": False,
                "mitigation_mandate": "Standard HO-3 terms require insured to take immediate reasonable measures to mitigate further property loss.",
                "matched_clauses": [],
            }

        primary = matches[0]
        return {
            "source": f"{self.policy_meta.get('policy_form', 'HO-3')} [SIMULATED POLICY RAG]",
            "policy_number": self.policy_meta.get("policy_number", "POL-2026-9812-HG"),
            "insurer": self.policy_meta.get("insurer", "Aegis Mutual [SIMULATED]"),
            "covered": primary.get("covered", True),
            "deductible_usd": primary.get("deductible_usd", 500),
            "clause_id": primary.get("id", ""),
            "section": primary.get("section", ""),
            "clause_title": primary.get("title", ""),
            "warranty_warning": primary.get("warranty_warning", ""),
            "dispatch": primary.get("dispatch", "24/7 Trade Dispatch"),
            "diy_voids_warranty": primary.get("diy_voids_warranty", False),
            "mitigation_mandate": (
                f"Under {primary.get('section', 'Clause')}, immediate proactive containment is legally required "
                "to preserve full sudden-and-accidental coverage and prevent excluded secondary mold/structural rot."
            ),
            "matched_clauses": [
                {
                    "id": m.get("id"),
                    "section": m.get("section"),
                    "title": m.get("title"),
                    "deductible_usd": m.get("deductible_usd"),
                    "relevance_score": m.get("relevance_score"),
                }
                for m in matches
            ],
        }


# Singleton instance for quick queries
_GLOBAL_POLICY_RAG: Optional[PolicyRAG] = None


def get_policy_rag() -> PolicyRAG:
    global _GLOBAL_POLICY_RAG
    if _GLOBAL_POLICY_RAG is None:
        _GLOBAL_POLICY_RAG = PolicyRAG()
    return _GLOBAL_POLICY_RAG
