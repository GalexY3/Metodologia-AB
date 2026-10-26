"""Bounded, historical, source-replayed aggregate Congress roll calls (NOT player scores)."""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit
import json,re

DEFAULT=Path(__file__).resolve().parents[2]/"data/observatory/congress_20260723_vote_aggregate_verified.json"
PINNED={1:("d83a10d39bad98a4f69c1e1b374700be949505aa40cb574ec0577b44d68c12d9",33,315,0,2),
        2:("e4609110932f34421fd08ac16dbddd5dcc23e4d113fe0a241700dab1956936b8",170,178,0,2)}
ROOT_KEYS={"source_type","as_of_observed_date","first_public_at","person_scoring_allowed",
 "read_only_aggregate_only","source_rights_per_dataset","source_provenance_note","votes"}
ROW_KEYS={"source_url","source_sha256","capture_workflow_id","event_date","legislature",
 "session","vote","individual_rows","yes","no","abstain","no_vote","present"}
STOP={"ok":False,"real_person_scoring":False,"first_public_at":None,"event_count":0,
      "release_ready":False,"events":[]}
def status(path: Path|None=None):
    p=Path(path) if path is not None else DEFAULT
    try:
        if not p.is_file() or p.stat().st_size>12000:
            return {**STOP,"error":"MISSING_OR_OVERSIZED"}
        x=json.loads(p.read_text(encoding="utf8"))
        if (not isinstance(x,dict) or set(x)!=ROOT_KEYS or
            x["source_type"]!="OFFICIAL_CONGRESS_ROLL_CALL_JSON" or
            x["first_public_at"] is not None or
            x["person_scoring_allowed"] is not False or
            x["read_only_aggregate_only"] is not True or
            x["source_rights_per_dataset"]!="NOT_INDEPENDENTLY_ADJUDICATED" or
            x["as_of_observed_date"]!="2026-10-26"):
            return {**STOP,"error":"PROVENANCE_OR_RELEASE_GUARD"}
        rows=x["votes"]
        if not isinstance(rows,list) or len(rows)!=2:
            return {**STOP,"error":"VOTE_COUNT"}
        out=[]
        for v in rows:
            if not isinstance(v,dict) or set(v)!=ROW_KEYS or type(v["vote"]) is not int or v["vote"] not in PINNED:
                return {**STOP,"error":"UNEXPECTED_EVENT_FIELDS"}
            u=urlsplit(v["source_url"])
            if (u.scheme!="https" or u.hostname!="www.congreso.es" or
                not re.fullmatch(r"/webpublica/opendata/votaciones/Leg15/Sesion193/20260723/Votacion00[12]/VOT_20260723\d{6}\.json",u.path)):
                return {**STOP,"error":"SOURCE_URL_CHANGED"}
            fingerprint,yes,no,abstain,no_vote=PINNED[v["vote"]]
            if (v["source_sha256"]!=fingerprint or v["event_date"]!="2026-07-23" or
                v["legislature"]!="XV" or v["session"]!=193 or
                v["individual_rows"]!=350 or v["present"]!=348 or
                tuple(v[k] for k in ("yes","no","abstain","no_vote"))!=(yes,no,abstain,no_vote) or
                type(v["capture_workflow_id"]) is not int):
                return {**STOP,"error":"PINNED_ORIGINAL_MISMATCH"}
            out.append({"legislature":v["legislature"],"session":v["session"],"vote":v["vote"],
              "event_date":v["event_date"],"yes":yes,"no":no,"abstain":abstain,
              "no_vote":no_vote,"present":348,"individual_rows":350,
              "official_source":v["source_url"],"original_sha256":fingerprint})
        if {v["vote"] for v in out}!={1,2}:
            return {**STOP,"error":"DUPLICATE_VOTE"}
        return {"ok":True,"historical_source_only":True,"event_count":len(out),
          "events":sorted(out,key=lambda q:q["vote"]),"first_public_at":None,
          "real_person_scoring":False,"release_ready":False,
          "verified_original_sha_replay":"CI_40344682502",
          "warning":"These are two historical roll-call aggregates, not individual player points, institutional influence or legal entity registry. Source publication timestamp and rights must be independently adjudicated."}
    except (OSError,ValueError,KeyError,TypeError,AttributeError):
        return {**STOP,"error":"INVALID_DOCUMENT"}
