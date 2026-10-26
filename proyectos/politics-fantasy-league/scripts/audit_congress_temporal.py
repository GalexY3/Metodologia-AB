#!/usr/bin/env python3
"""C03: aggregate temporal and overlap diagnostics, no person values logged."""
import json,re,unicodedata
from datetime import datetime
from collections import Counter
from pathlib import Path
P=Path("/tmp/pf-congress-probe")
def normalize(s):return " ".join(unicodedata.normalize("NFKC",s).casefold().split())
def parse(s):
    for fmt in ("%d/%m/%Y","%Y-%m-%d","%d-%m-%Y","%Y/%m/%d"):
        try:return datetime.strptime(str(s).strip(),fmt).date()
        except ValueError:pass
    return None
def run():
    a=json.loads((P/"official_1.json").read_text(encoding="utf-8-sig"))
    b=json.loads((P/"official_7.json").read_text(encoding="utf-8-sig"))
    assert isinstance(a,list) and isinstance(b,list)
    sa=[normalize(x["NOMBRE"]) for x in a];sb=[normalize(x["NOMBRE"]) for x in b]
    dates={}
    for k,rows in [("active",a),("discharged",b)]:
        columns=[x for x in ("FECHAALTA","FECHABAJA","FECHACONDICIONPLENA","FECHAALTAENGRUPOPARLAMENTARIO","FECHABAJAENGRUPOPARLAMENTARIO") if all(x in row for row in rows)]
        cols={}
        for field in columns:
            vals=[parse(q[field]) for q in rows]
            cols[field]={"valid":sum(v is not None for v in vals),"invalid":sum(v is None for v in vals),
                          "min":str(min(v for v in vals if v)) if any(vals) else None,
                          "max":str(max(v for v in vals if v)) if any(vals) else None}
        nwrong=0
        if "FECHABAJA" in columns:
            nwrong=sum(parse(q["FECHAALTA"]) is not None and parse(q["FECHABAJA"]) is not None and parse(q["FECHABAJA"]) < parse(q["FECHAALTA"]) for q in rows)
        dates[k]={"columns":cols,"date_inversion_count":nwrong}
    result={"cycle":"C03","active":len(a),"discharged":len(b),
            "duplicate_name_keys_active":sum(v-1 for v in Counter(sa).values() if v>1),
            "duplicate_name_keys_discharged":sum(v-1 for v in Counter(sb).values() if v>1),
            "exact_normalized_name_overlap_between_sources":len(set(sa)&set(sb)),
            "dates":dates,
            "no_identification_claim":"name overlap is a diagnostic, never automatic person matching"}
    (P/"temporal_report.json").write_text(json.dumps(result,indent=2)+"\n")
    print("C03_TEMPORAL="+json.dumps(result))
if __name__=="__main__":run()
