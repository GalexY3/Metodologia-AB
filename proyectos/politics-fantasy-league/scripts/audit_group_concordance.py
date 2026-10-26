#!/usr/bin/env python3
"""C07: organizational group-code concordance, no personal-level values."""
from pathlib import Path
from collections import defaultdict,Counter
import json,unicodedata
P=Path("/tmp/pf-congress-probe")
def norm(s):return " ".join(unicodedata.normalize("NFKC",str(s)).casefold().split())
def run():
    vote=json.loads((P/"vote_original.json").read_text())
    roster=json.loads((P/"official_1.json").read_text())+json.loads((P/"official_7.json").read_text())
    idx={norm(r["NOMBRE"]):r for r in roster}
    pairs=Counter((v["grupo"],idx[norm(v["diputado"])]["GRUPOPARLAMENTARIO"]) for v in vote["votaciones"])
    mapping=defaultdict(set)
    reverse=defaultdict(set)
    for (short,long),n in pairs.items():
        mapping[short].add(long);reverse[long].add(short)
    x={"cycle":"C07","pairs":[{"abbreviation":short,"official_title":full,"n":n} for (short,full),n in sorted(pairs.items())],
       "forward_conflicts":{k:len(v) for k,v in mapping.items() if len(v)>1},
       "reverse_conflicts":{k:len(v) for k,v in reverse.items() if len(v)>1},
       "supported_vote_rows":sum(pairs.values()),
       "source_note":"names used only as candidate joins; only public organizational group labels emitted; no enduring identity resolved"}
    (P/"group_concordance.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n")
    print("C07_GROUP="+json.dumps(x,ensure_ascii=False))
if __name__=="__main__":run()
