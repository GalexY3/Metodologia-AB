#!/usr/bin/env python3
"""Compare a fresh SHA-verified original BOE extraction with frozen bounded atlas files.

No promotion of quarantined headings to proclaimed candidacies or legal
party/person identities. Exit nonzero on mismatch, without inventing missing data.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

EXPECTED_SHA = "d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20"


def verify(extraction: dict, accepted: dict, quarantine: dict) -> dict:
    if (extraction.get("sha256") != EXPECTED_SHA or
        accepted.get("original_sha256") != EXPECTED_SHA or
        quarantine.get("source_sha256") != EXPECTED_SHA):
        raise ValueError("ORIGINAL_DIGEST_MISMATCH")
    if extraction.get("province_sections_detected") != 52:
        raise ValueError("PROVINCE_COUNT_CHANGED")
    if (extraction.get("province_sections_parsed") != 25 or
        extraction.get("list_headings_extracted") != 263):
        raise ValueError("ACCEPTED_COUNTS_CHANGED")
    if extraction.get("provinces") != accepted.get("provinces"):
        raise ValueError("ACCEPTED_ROWS_CHANGED")
    if (extraction.get("quarantined_provinces") !=
        quarantine.get("quarantined_provinces")):
        raise ValueError("QUARANTINED_ROWS_CHANGED")
    if (len(quarantine["quarantined_provinces"]) != 27 or
        extraction.get("quarantined_observed_list_headings") != 278 or
        quarantine.get("n_observed_headings") != 278):
        raise ValueError("QUARANTINE_COUNTS_CHANGED")
    # Original parser now records missing positions explicitly; the older
    # accepted-only artifact omitted that field from its issue entries.
    for old, new in zip(accepted.get("issues", []), extraction.get("issues", [])):
        if any(new.get(key) != val for key, val in old.items()):
            raise ValueError("ISSUE_DETAILS_CHANGED")
    if len(accepted.get("issues", [])) != len(extraction.get("issues", [])):
        raise ValueError("ISSUE_COUNT_CHANGED")
    if (extraction.get("legal_parties_confirmed") != 0 or
        extraction.get("people_public_roles_joined") != 0 or
        quarantine.get("eligible_for_scoring") is not False):
        raise ValueError("UNSAFE_IDENTITY_CLAIM")
    return {"status": "MATCH_ORIGINAL_BOUNDED", "sha256": EXPECTED_SHA,
            "accepted_sections": 25, "accepted_headings": 263,
            "quarantined_sections": 27, "noncertified_observed_headings": 278,
            "proclaimed_candidacies_legally_adjudicated": None,
            "original_person_identities": 0}


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: verify_boe_nomination_snapshot.py FRESH.json ATLAS.json QUARANTINE.json")
    docs = [json.loads(Path(f).read_text(encoding="utf8")) for f in sys.argv[1:]]
    print(json.dumps(verify(*docs), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
