#!/usr/bin/env python3
"""C05: compare roll-call arithmetic and name-string join candidates; no links accepted."""
from pathlib import Path
import json,unicodedata
from collections import Counter
P=Path("/tmp/pf-congress-probe")
def norm(x):return " ".join(unicodedata.normalize("NFKC",str(x)).casefold().split())
def run():
    raw=json.loads((P/"vote_original.json").read_text())
    active=json.loads((P/"official_1.json").read_text())
    discharged=json.loads((P/"official_7.json").read_text())
    votes=raw["votaciones"]
    counts=Counter(v["voto"] for v in votes)
    names_vote=[norm(v["diputado"]) for v in votes]
    names_active=[norm(v["NOMBRE"]) for v in active]
    names_baja=[norm(v["NOMBRE"]) for v in discharged]
    names_roster=names_active+names_baja
    counts_names=Counter(names_roster)
    candidates=sum(n in counts_names and counts_names[n]==1 for n in names_vote)
    ambiguous=sum(counts_names.get(n,0)>1 for n in names_vote)
    result={"cycle":"C05","vote_rows":len(votes),"unique_vote_name_keys":len(set(names_vote)),"unique_roster_name_keys":len(set(names_roster)),"votes_by_choice":dict(counts),"declared_vote_totals":raw["totales"],"raw_name_exact_unique_candidates":candidates,"raw_name_ambiguous":ambiguous,"name_unmatched":len(votes)-candidates-ambiguous,"explicit_identifier":False,"no_automatic_identity_claim":True}
    (P/"join_report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C05_JOIN="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":run()
