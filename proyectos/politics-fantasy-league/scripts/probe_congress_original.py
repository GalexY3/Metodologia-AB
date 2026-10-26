"""Attempt authentic historical Congreso JSON in CI; never silently use fixtures.

A successful run proves transport, parsable source schema and bounded projection.
It does NOT prove current mandates, as-of July validity, or registered parties.
"""
import hashlib
import json
import ssl
from urllib.request import Request, urlopen
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from politics_fantasy.congress_members import SOURCE_URL,project

def main():
    req=Request(SOURCE_URL,headers={"User-Agent":"PFL-Research-Source-Audit/0.1"})
    with urlopen(req,timeout=28,context=ssl.create_default_context()) as response:
        assert response.status==200, f"HTTP {response.status}"
        ctype=response.headers.get("Content-Type","")
        assert "json" in ctype.lower() or "octet-stream" in ctype.lower(),ctype
        raw=response.read(10_000_001)
    digest=hashlib.sha256(raw).hexdigest()
    projected=project(raw,max_rows=5)
    assert projected["rows_in_original_response"]>=5
    expected_first_name="Abades Martínez, Cristina"
    if projected["people"][0]["display_name_from_official"]!=expected_first_name:
        raise AssertionError("SNAPSHOT_REVISION_OR_ORDER_CHANGED")
    assert all(not p["eligible_for_real_scoring"] and p["first_public_at"] is None
               for p in projected["people"])
    print("CONGRESO_OFFICIAL_SOURCE_CAPTURED",
          json.dumps({"url":SOURCE_URL,"bytes":len(raw),"sha256":digest,
                      "total_original_rows":projected["rows_in_original_response"],
                      "sample_rows":5,"first_row":expected_first_name,
                      "scope":"historical_bounded_not_current",
                      "real_scoring_enabled":False},ensure_ascii=False))
    Path("/tmp/pf-congress-extract-status.json").write_text(json.dumps(
        {"source_url":SOURCE_URL,"raw_sha256":digest,
         "raw_bytes":len(raw),"rows":projected["rows_in_original_response"],
         "validated_first_five":projected["people"]},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
