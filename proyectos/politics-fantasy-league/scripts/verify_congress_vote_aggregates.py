#!/usr/bin/env python3
"""Replay pinned two-vote aggregates against current downloaded original Congress JSON.
Originals stay private and ephemeral. No individual names persisted.
"""
import json,hashlib
from pathlib import Path
from politics_fantasy.congress_vote_dates import normalized_vote_date
ROOT=Path(__file__).resolve().parents[1]
BASE=Path("/tmp/pf-congress-probe")
MANIFEST=ROOT/"data/observatory/congress_20260723_vote_aggregate_verified.json"
def verify_one(raw,expected):
    if hashlib.sha256(raw).hexdigest()!=expected["source_sha256"]:raise ValueError("SOURCE_SHA_DRIFT")
    data=json.loads(raw)
    fields=data["informacion"]
    if normalized_vote_date(fields["fecha"])!=expected["event_date"]:raise ValueError("DATE_DRIFT")
    if fields["sesion"]!=expected["session"] or fields["numeroVotacion"]!=expected["vote"]:raise ValueError("VOTE_SESSION_DRIFT")
    rows=data["votaciones"]
    c={v["voto"]:0 for v in rows}
    for v in rows:c[v["voto"]]+=1
    numbers=(c.get("Sí",0),c.get("No",0),c.get("Abstención",0),c.get("No vota",0))
    required=tuple(expected[k] for k in ("yes","no","abstain","no_vote"))
    if len(rows)!=expected["individual_rows"] or numbers!=required:raise ValueError("ROW_TALLY_DRIFT")
    tot=data["totales"]
    if (tot["afavor"],tot["enContra"],tot["abstenciones"],tot["noVotan"],tot["presentes"])!=(expected["yes"],expected["no"],expected["abstain"],expected["no_vote"],expected["present"]):
        raise ValueError("PUBLISHED_TOTALLY_DRIFT")
    if sum(required)!=len(rows):raise ValueError("COUNT_MISMATCH")
    return {"vote":expected["vote"],"matched":True,"rows":len(rows)}
def main():
    manifest=json.loads(MANIFEST.read_text())
    assert manifest["first_public_at"] is None and not manifest["person_scoring_allowed"]
    assert len(manifest["votes"])==2
    result=[verify_one((BASE/file).read_bytes(),rec) for file,rec in zip(("vote_original.json","vote2_original.json"),manifest["votes"])]
    print("C10_ORIGINAL_REPLAY="+json.dumps(result))
if __name__=="__main__":main()
