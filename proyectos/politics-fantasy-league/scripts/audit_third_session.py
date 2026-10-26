#!/usr/bin/env python3
"""C18 aggregate cross-time check third parliamentary sitting, no person outputs."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime
import json,unicodedata
P=Path("/tmp/pf-congress-probe")
def k(s):return " ".join(unicodedata.normalize("NFKC",str(s)).casefold().split())
def d(s):return datetime.strptime(s,"%d/%m/%Y").date()
def run():
    a=json.loads((P/"official_1.json").read_text());b=json.loads((P/"official_7.json").read_text())
    reg={k(x["NOMBRE"]):x for x in a+b}
    july=json.loads((P/"vote_original.json").read_text())
    aliases=defaultdict(set)
    for v in july["votaciones"]:
      if k(v["diputado"]) in reg:
         aliases[v["grupo"]].add(reg[k(v["diputado"])]["GRUPOPARLAMENTARIO"])
    sep=json.loads((P/"session196_vote_original.json").read_text())
    day=d(sep["informacion"]["fecha"])
    counts=Counter()
    for v in sep["votaciones"]:
       x=reg.get(k(v["diputado"]))
       if x is None:counts["unknown_name"]+=1;continue
       counts["source_scoped_name_match"]+=1
       if not (d(x["FECHAALTA"])<=day and (not x.get("FECHABAJA") or day<d(x["FECHABAJA"]))):
          counts["outside_office_interval"]+=1
       if x["GRUPOPARLAMENTARIO"] not in aliases.get(v["grupo"],set()):
          counts["group_map_conflict"]+=1
    by=Counter(v["voto"] for v in sep["votaciones"])
    totals=sep["totales"]
    good=(by["Sí"],by["No"],by["Abstención"],by["No vota"])==(totals["afavor"],totals["enContra"],totals["abstenciones"],totals["noVotan"])
    result={"cycle":"C18","date":str(day),"official_vote_rows":len(sep["votaciones"]),"quality_counts":dict(counts),"official_tallies_reconcile":good,"roster_total_universe":len(a)+len(b)}
    (P/"third_session_quality.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C18_THIRD_SESSION="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":run()
