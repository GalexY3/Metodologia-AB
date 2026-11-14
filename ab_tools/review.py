"""M041: separate scientific gate from editorial changes.

Content meaning cannot be certified automatically: editorial acceptance is
conditional on an external scientific audit and structured frozen claims.
"""
from __future__ import annotations

import re
from collections import Counter

from .core import ABError, nonempty, require

MANDATORY_GATES = (
    "source_integrity",
    "design_fidelity",
    "statistical_reproduction",
    "citation_support",
    "leakage_and_selection",
)
GATE_STATES = ("PASS", "FAIL", "UNKNOWN")
NUMERIC = re.compile(r"(?<!\w)[+-]?\d+(?:[.,]\d+)?(?:%|\b)")
CITATION = re.compile(r"\\cite(?:\[[^\]]*\])?\{[^{}]+\}|\[[0-9]+(?:\s*[-,]\s*[0-9]+)*\]")


def scientific_gate(audit: dict, author_id: str) -> dict:
    require(audit, {"reviewer_id": str, "checks": dict}, "scientific_audit")
    nonempty(audit["reviewer_id"], "reviewer_id")
    if audit["reviewer_id"] == nonempty(author_id, "author_id"):
        raise ABError("The manuscript author cannot approve their own scientific gate")
    failures, unknowns, evidence_missing = [], [], []
    for name in MANDATORY_GATES:
        item = audit["checks"].get(name, {})
        if not isinstance(item, dict):
            unknowns.append(name)
            continue
        status = item.get("status", "UNKNOWN")
        if status not in GATE_STATES:
            raise ABError(f"Invalid gate status for {name}")
        if status == "FAIL":
            failures.append(name)
        elif status == "UNKNOWN":
            unknowns.append(name)
        elif not item.get("evidence_ref"):
            evidence_missing.append(name)
    state = ("FAIL" if failures else
             "NEEDS_EVIDENCE" if unknowns or evidence_missing else
             "ATTESTED_PASS")
    return {
        "state": state, "failed": failures, "unknown": unknowns,
        "missing_evidence": evidence_missing,
        "warning": "ATTESTED_PASS documents an auditor's judgment; it is not proof of scientific validity.",
    }


def compare_editorial(original: dict, revision: dict, scientific_audit: dict,
                      reviewer_id: str) -> dict:
    """Conservative comparison: never accept changed frozen evidence claims."""
    for label, doc in (("original", original), ("revision", revision)):
        require(doc, {"text": str, "frozen_claims": list, "author_id": str}, label)
    nonempty(reviewer_id, "editorial reviewer")
    if reviewer_id == revision["author_id"]:
        raise ABError("Editorial reviewer must not be revision author")
    gate = scientific_gate(scientific_audit, revision["author_id"])
    defects = []
    if original["frozen_claims"] != revision["frozen_claims"]:
        defects.append("frozen_claims_changed")
    # Secondary heuristic only; does not establish semantic equivalence.
    if Counter(NUMERIC.findall(original["text"])) != Counter(NUMERIC.findall(revision["text"])):
        defects.append("numeric_tokens_changed")
    if Counter(CITATION.findall(original["text"])) != Counter(CITATION.findall(revision["text"])):
        defects.append("citation_tokens_changed")
    if gate["state"] != "ATTESTED_PASS":
        verdict = "NEEDS_SCIENTIFIC_AUDIT"
    elif defects:
        verdict = "REJECT_EDITORIAL_REVISION"
    else:
        verdict = "EDITORIAL_REVIEW_POSSIBLE"
    return {
        "verdict": verdict, "scientific_gate": gate, "flags": defects,
        "reviewer_id": reviewer_id,
        "limitation": (
            "Text meaning, attribution and statistical validity are NOT guaranteed by "
            "token comparisons. Reviewer must explicitly approve before publication."
        ),
    }
