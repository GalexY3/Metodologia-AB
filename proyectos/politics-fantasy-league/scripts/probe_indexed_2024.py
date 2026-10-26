#!/usr/bin/env python3
"""C24 recover historical day identified by publisher rather than guessed schedule."""
from pathlib import Path
from collections import defaultdict
from datetime import date
import json
from ab32_adaptive_survey import audit,norm
ROOT=Path("/tmp/pf-congress-probe")
def main():
    a=json.loads((ROOT/"official_1.json").read_text());b=json.loads((ROOT/"official_7.json").read_text())
    roster={norm(z["NOMBRE"]):z for z in a+b}
    old=json.loads((ROOT/"vote_original.json").read_text())
    group=defaultdict(set)
    for x in old["votaciones"]:
       r=roster.get(norm(x["diputado"]))
       if r:group[x["grupo"]].add(r["GRUPOPARLAMENTARIO"])
    output={"cycle":"C24","indexed_primary_date":"2024-04-09","status":"STOP_R5"}
    try:
       measured=audit(date(2024,4,9),group,roster)
       output.update(measured)
    except Exception as e:output.update(error_type=type(e).__name__,error_code=str(e)[:100])
    ROOT.mkdir(parents=True,exist_ok=True)
    (ROOT/"indexed2024_original_probe.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
    print("C24_INDEXED_DATE="+json.dumps(output,ensure_ascii=False))
if __name__=="__main__":main()
