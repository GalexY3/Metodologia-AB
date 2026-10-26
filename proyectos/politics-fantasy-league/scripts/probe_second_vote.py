#!/usr/bin/env python3
"""C08: second independent official Congress vote, no person values logged."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlparse
from collections import Counter
import json,hashlib,unicodedata
P=Path("/tmp/pf-congress-probe")
URL="https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion193/20260723/Votacion002/VOT_20260723211930.json"
def norm(s):return " ".join(unicodedata.normalize("NFKC",str(s)).casefold().split())
def main():
    report={"cycle":"C08","url":URL,"status":"STOP_R5"}
    try:
        with urlopen(Request(URL,headers={"User-Agent":"PFL-Research-AB32/0.1"}),timeout=25) as r:
            if r.status!=200 or urlparse(r.geturl()).hostname!="www.congreso.es" or urlparse(r.geturl()).scheme!="https":raise ValueError("BAD_HOST")
            data=r.read(4_000_001)
        if len(data)>4_000_000:raise ValueError("OVERSIZE")
        js=json.loads(data)
        votes=js["votaciones"]
        first=json.loads((P/"vote_original.json").read_text())
        roster=json.loads((P/"official_1.json").read_text())+json.loads((P/"official_7.json").read_text())
        idx={norm(x["NOMBRE"]):x for x in roster}
        original_map={}
        for v in first["votaciones"]:original_map.setdefault(v["grupo"],set()).add(idx[norm(v["diputado"])]["GRUPOPARLAMENTARIO"])
        covered=sum(norm(v.get("diputado","")) in idx for v in votes)
        variants=[v for v in votes if norm(v.get("diputado","")) in idx and idx[norm(v["diputado"])]["GRUPOPARLAMENTARIO"] not in original_map.get(v.get("grupo",""),set())]
        ct=Counter(v["voto"] for v in votes)
        report.update(status="RAW_CAPTURED",bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
                      fields=sorted(js),vote_rows=len(votes),unique_vote_names=len({norm(v["diputado"]) for v in votes}),
                      exact_roster_name_matches=covered,group_mapping_conflicts=len(variants),
                      vote_counts=dict(ct),declared_totals=js["totales"],date=js["informacion"]["fecha"])
        (P/"vote2_original.json").write_bytes(data)
    except Exception as e:report.update(error_type=type(e).__name__,http_code=getattr(e,"code",None))
    (P/"vote2_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("C08_SECOND_VOTE="+json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
