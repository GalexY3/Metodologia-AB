"""Export unreviewed claim evidence to existing AB Atlas delta schema.

Produces a candidate batch only. The real Atlas replay validator must accept it
before anybody can apply it. This does not establish scientific validity.
"""
from __future__ import annotations

import re

from .core import ABError, stable_id, utc_now


def make_delta(ledger: dict, batch_id: str, parent_batch: str = "",
               parent_node: str = "root", mode: str = "research") -> dict:
    from .traceability import _validated
    _validated(ledger)
    if mode not in ("research", "hybrid", "meta"):
        raise ABError("Claim exports need research/hybrid/meta mode")
    if not re.fullmatch(r"[A-Za-z0-9_./:-]{1,100}", batch_id):
        raise ABError("Invalid batch id")
    ops = []
    ids = {}
    for claim in ledger["claims"]:
        node_id = stable_id("claim", claim["id"])
        ids[("claim", claim["id"])] = node_id
        ops.append({"op": "node.add", "node": {
            "id": node_id, "title": claim["text"][:170], "kind": "finding",
            "mode": mode, "status": "proposed",
            "detail": "External claim ledger ID: " + claim["id"] +
                      "; unreviewed candidate, not a validated finding",
            "sources": [], "phase": "verify",
        }})
        ops.append({"op": "edge.add", "id": stable_id("edge", parent_node, node_id),
                    "from": node_id, "to": parent_node, "relation": "related_to"})
    for evidence in ledger["evidence"]:
        node_id = stable_id("evidence", evidence["id"])
        ids[("evidence", evidence["id"])] = node_id
        ops.append({"op": "node.add", "node": {
            "id": node_id, "title": evidence["location"][:170],
            "kind": "artifact", "mode": mode, "status": "unreviewed",
            "detail": "Claim ledger evidence: " + evidence["id"] +
                      "; integrity and truth not independently audited",
            "sources": [evidence["location"]], "phase": "verify",
        }})
    for link in ledger["links"]:
        source = ids.get(("evidence", link["evidence_id"]))
        target = ids.get(("claim", link["claim_id"]))
        if not source or not target:
            raise ABError("Claim link references missing node")
        relation = {"supports": "supports", "contradicts": "refutes",
                    "context": "references", "unreviewed": "related_to"}[link["relationship"]]
        ops.append({"op": "edge.add",
                    "id": stable_id("edge", source, target, relation),
                    "from": source, "to": target, "relation": relation})
    if len(ops) > 250:
        raise ABError("Too many operations for a single Atlas batch; split export")
    return {
        "schema": "ab.atlas.delta.v1", "batch_id": batch_id,
        "parent_batch": parent_batch, "at": utc_now(),
        "actor": "ab-tools-pilot",
        "reason": ("Transfer candidate evidence links without promoting their "
                   "scientific status; validate against canonical Atlas baseline"),
        "ops": ops,
    }
