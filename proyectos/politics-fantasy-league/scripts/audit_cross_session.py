#!/usr/bin/env python3
"""C15 strictly source-scoped September/JULY group and role concordance."""
from pathlib import Path
from datetime import datetime
import unicodedata,json,collections
P=Path("/tmp/pf-congress-probe")
def norm(v):return " ".join(unicodedata.normalize("NFKC",str(v)).casefold().split())
def day(x):return datetime.strptime(x,"%d/%m/%Y").date()
def run():
    a=json.loads((P/"official_1.json").read_text());b=json.loads((P/"official_7.json").read_text())
    roster={norm(v["NOMBRE"]):v for v in a+b}
    old=json.loads((P/"vote_original.json").read_text())["votaciones"]
    latest=json.loads((P/"session202_vote_original.json").read_text())
    prev={}
    for v in old:
        k=norm(v["diputado"])
        if k in roster:prev.setdefault(v["grupo"],set()).add(roster[k]["GRUPOPARLAMENTARIO"])
    date=day(latest["informacion"]["fecha"])
    counts=collections.Counter();group_changes=collections.Counter()
    for row in latest["votaciones"]:
        key=norm(row["diputado"])
        if key not in roster:counts["not_in_roster"]+=1;continue
        rec=roster[key];counts["matched_roster"]+=1
        begin=day(rec["FECHAALTA"]);end=day(rec["FECHABAJA"]) if rec.get("FECHABAJA") else None
        if not (begin<=date and (end is None or date<end)):counts["invalid_office_period"]+=1
        if rec["GRUPOPARLAMENTARIO"] not in prev.get(row["grupo"],set()):
            counts["group_code_map_mismatch"]+=1
            group_changes[(row["grupo"],rec["GRUPOPARLAMENTARIO"])]+=1
    by=collections.Counter(row["voto"] for row in latest["votaciones"])
    totals=latest["totales"]
    tally_match=(totals["afavor"],totals["enContra"],totals["abstenciones"],totals["noVotan"])==(by["Sí"],by["No"],by["Abstención"],by["No vota"])
    result={"cycle":"C15","source":"official 2026-09-30 session202 vote001","date":str(date),"rows":len(latest["votaciones"]),"counts":dict(counts),"tally_match":tally_match,
      "group_code_official_mapping_conflicts":[{"code":k[0],"title":k[1],"rows":n} for k,n in group_changes.items()],
      "not_a_legal_identity_claim":True}
    (P/"cross_session_roster_audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C15_CROSS_TIME="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":run()
