#!/usr/bin/env python3
"""C02: privacy-preserving structural audit on originals freshly downloaded in CI."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import json,re

BASE=Path("/tmp/pf-congress-probe")
def inspect():
    m=json.loads((BASE/"probe_manifest.json").read_text())
    reports=[]
    for i,row in enumerate(m["rows"]):
        if row["format"]!="json" or not row["retrieved"]:continue
        content=json.loads((BASE/f"official_{i}.json").read_text(encoding="utf-8-sig"))
        if not isinstance(content,list) or not all(isinstance(x,dict) for x in content):
            reports.append({"index":i,"status":"UNSUPPORTED_JSON_SCHEMA"});continue
        keys=sorted(set().union(*(r.keys() for r in content)))
        parts={}
        for k in keys:
            types=Counter(type(r.get(k)).__name__ for r in content)
            # Only shape, not field values, is released.
            parts[k]={"observed_nonnull":sum(r.get(k) is not None for r in content),
                      "types":dict(types),
                      "distinct":len({json.dumps(r.get(k),ensure_ascii=False,sort_keys=True) for r in content})}
        likely_temporal=[k for k in keys if re.search(r'fech|date|legisl|inicio|fin|baja|alta|toma|mandat|period',k,re.I)]
        likely_identity=[k for k in keys if re.search(r'id|codigo|cod|ficha|diput|number|numero|num',k,re.I)]
        reports.append({"index":i,"source_url":row["source_url"],"sha256":row["sha256"],
                        "row_count":len(content),"fields":parts,
                        "temporal_key_names":likely_temporal,"candidate_identity_key_names":likely_identity,
                        "status":"SHAPE_REPORTED_NO_VALUES"})
    result={"cycle":"C02","source_job":121636813397,"reports":reports,
            "interpretation_warning":"names, identity values and legal rights not reviewed; count is not completeness"}
    (BASE/"schema_report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("C02_STRUCTURE="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":inspect()
