#!/usr/bin/env python3
"""C06: validate vote-day interval and group label parity for unique exact strings."""
from pathlib import Path
from datetime import datetime
import json,unicodedata
P=Path("/tmp/pf-congress-probe")
def norm(s):return " ".join(unicodedata.normalize("NFKC",str(s)).casefold().split())
def date(s):return datetime.strptime(str(s),"%d/%m/%Y").date()
def run():
    obj=json.loads((P/"vote_original.json").read_text())
    a=json.loads((P/"official_1.json").read_text())
    b=json.loads((P/"official_7.json").read_text())
    records={norm(x["NOMBRE"]):x for x in a+b}
    dt=date(obj["informacion"]["fecha"])
    failures=[];groups_mismatch=0;group_pairs={}
    source_kind_counts={"remaining":0,"discharged":0}
    akeys={norm(x["NOMBRE"]) for x in a}
    for v in obj["votaciones"]:
        key=norm(v["diputado"])
        x=records.get(key)
        if x is None:failures.append("NAME_NOT_FOUND");continue
        source_kind_counts["remaining" if key in akeys else "discharged"]+=1
        start=date(x["FECHAALTA"])
        end=date(x["FECHABAJA"]) if x.get("FECHABAJA") else None
        if not (start<=dt and (end is None or dt<end)):failures.append("OUTSIDE_ROLE_INTERVAL")
        # exact group equality is diagnostic only; group names may use abbreviation.
        if norm(v["grupo"])!=norm(x["GRUPOPARLAMENTARIO"]):
            groups_mismatch+=1
            # Only exact pair *counts*, never persons.
            keypair=("len"+str(len(v["grupo"])),"len"+str(len(x["GRUPOPARLAMENTARIO"])))
            group_pairs[keypair]=group_pairs.get(keypair,0)+1
    result={"cycle":"C06","vote_date":str(dt),"votes":len(obj["votaciones"]),"invalid_office_intervals":len(failures),"failure_reasons":sorted(set(failures)),
            "active_and_discharge_source_mix":source_kind_counts,"group_label_exact_mismatches":groups_mismatch,
            "mismatch_token_length_pairs":sorted([[*k,v] for k,v in group_pairs.items()]),"identity_claim":"unique source-scoped name only"}
    (P/"vote_temporal_join.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("C06_LINK="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":run()
