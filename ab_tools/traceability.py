"""M040: a claim/evidence link register with local-file integrity checks.

An attested link never constitutes proof of empirical truth, nor a review of a URL.
"""
from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlparse

from .core import ABError, content_sha256, nonempty, require, utc_now

RELATIONS = ("supports", "contradicts", "context", "unreviewed")
SHA_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def new_ledger() -> dict:
    return {"schema": "AB-CLAIMS-0.1", "claims": [], "evidence": [], "links": []}


def _validated(doc: dict):
    if doc.get("schema") != "AB-CLAIMS-0.1":
        raise ABError("Unknown claims ledger schema")
    for key in ("claims", "evidence", "links"):
        if not isinstance(doc.get(key), list):
            raise ABError(f"{key} must be list")


def _unique(records: list, record_id: str) -> None:
    if any(r.get("id") == record_id for r in records):
        raise ABError(f"Duplicate identifier {record_id}")


def add_claim(doc: dict, claim_id: str, text: str, scope: str = "") -> dict:
    _validated(doc)
    claim_id = nonempty(claim_id, "claim_id")
    text = nonempty(text, "claim")
    result = deepcopy(doc)
    _unique(result["claims"], claim_id)
    result["claims"].append({"id": claim_id, "text": text, "scope": scope,
                             "status": "UNREVIEWED", "at": utc_now()})
    return result


def _local_path(root: str | Path, relative: str) -> Path:
    base = Path(root).resolve()
    source = (base / relative).resolve()
    if not source.is_relative_to(base):
        raise ABError("Evidence path escapes project root")
    return source


def add_file_evidence(doc: dict, evidence_id: str, relative_path: str,
                      root: str | Path, kind: str = "analysis") -> dict:
    _validated(doc)
    _unique(doc["evidence"], evidence_id)
    source = _local_path(root, nonempty(relative_path, "relative_path"))
    if not source.is_file():
        raise ABError("Evidence file does not exist")
    result = deepcopy(doc)
    result["evidence"].append({
        "id": nonempty(evidence_id, "evidence_id"), "type": "file",
        "kind": kind, "location": relative_path, "sha256": content_sha256(source),
        "registered_at": utc_now(), "content_verified": False,
    })
    return result


def add_external_evidence(doc: dict, evidence_id: str, url: str,
                          kind: str = "publication", digest: str = "") -> dict:
    _validated(doc)
    _unique(doc["evidence"], evidence_id)
    parsed = urlparse(nonempty(url, "url"))
    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        raise ABError("Evidence URL must be absolute HTTP(S)")
    if digest and not SHA_PATTERN.fullmatch(digest):
        raise ABError("Invalid SHA-256 hex")
    result = deepcopy(doc)
    result["evidence"].append({
        "id": nonempty(evidence_id, "evidence_id"), "type": "external",
        "kind": kind, "location": url, "sha256": digest or None,
        "registered_at": utc_now(), "content_verified": False,
    })
    return result


def link(doc: dict, claim_id: str, evidence_id: str, relationship: str,
         locator: str = "", reviewer: str = "", note: str = "") -> dict:
    _validated(doc)
    if relationship not in RELATIONS:
        raise ABError("Invalid relation")
    if not any(c["id"] == claim_id for c in doc["claims"]):
        raise ABError("Unknown claim")
    if not any(e["id"] == evidence_id for e in doc["evidence"]):
        raise ABError("Unknown evidence")
    if relationship in ("supports", "contradicts"):
        nonempty(locator, "locator")
        nonempty(reviewer, "reviewer")
    result = deepcopy(doc)
    if any(x["claim_id"] == claim_id and x["evidence_id"] == evidence_id
           and x["relationship"] == relationship for x in result["links"]):
        raise ABError("Duplicate relationship")
    result["links"].append({
        "claim_id": claim_id, "evidence_id": evidence_id,
        "relationship": relationship, "locator": locator,
        "reviewer": reviewer, "note": note, "recorded_at": utc_now(),
        "attestation": "LINK_ASSERTED_NOT_INDEPENDENTLY_CONFIRMED",
    })
    return result


def audit(doc: dict, root: str | Path = ".") -> dict:
    _validated(doc)
    evidence_status = {}
    for evidence in doc["evidence"]:
        require(evidence, {"id": str, "type": str, "location": str}, "evidence")
        if evidence["type"] == "file":
            try:
                path = _local_path(root, evidence["location"])
                if not path.exists():
                    status = "MISSING"
                elif not path.is_file():
                    status = "NOT_FILE"
                elif content_sha256(path) != evidence.get("sha256"):
                    status = "HASH_MISMATCH"
                else:
                    status = "HASH_MATCH_CONTENT_NOT_AUDITED"
            except (OSError, ABError):
                status = "PATH_INVALID"
        else:
            status = "EXTERNAL_CONTENT_NOT_FETCHED"
        evidence_status[evidence["id"]] = status
    findings = []
    for c in doc["claims"]:
        links = [x for x in doc["links"] if x["claim_id"] == c["id"]]
        bad = [x for x in links if evidence_status.get(x["evidence_id"]) in
               ("MISSING", "NOT_FILE", "HASH_MISMATCH", "PATH_INVALID", None)]
        support = [x for x in links if x["relationship"] == "supports"]
        contradictions = [x for x in links if x["relationship"] == "contradicts"]
        if bad:
            state = "BROKEN_EVIDENCE"
        elif contradictions:
            state = "CONFLICT_NEEDS_REVIEW"
        elif not support:
            state = "NO_REVIEWED_SUPPORT"
        else:
            state = "ATTESTED_SUPPORT_NOT_VERIFIED"
        findings.append({
            "claim_id": c["id"], "state": state, "support_count": len(support),
            "contradiction_count": len(contradictions),
            "evidence_links": len(links),
        })
    return {
        "schema": "AB-CLAIM-AUDIT-0.1",
        "evidence_integrity": evidence_status,
        "claims": findings,
        "meaning": "A recorded attestation and file hash are not validation of a scientific claim.",
    }
