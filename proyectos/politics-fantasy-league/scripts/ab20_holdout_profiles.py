#!/usr/bin/env python3
"""C04 heldout 16 Congress public profiles, parser frozen from C03, no name outputs."""
from pathlib import Path
from urllib.parse import urlparse,parse_qs
import json,hashlib
from ab20_profile_semantic import Head,get,norm,INDEX
P=Path("/tmp/pfl-ab20");ROOT=Path("/tmp/pf-congress-probe")
def run():
 out={"cycle":"C04","status":"STOP_R5"}
 try:
  roster=json.loads((ROOT/"official_1.json").read_text())+json.loads((ROOT/"official_7.json").read_text())
  keys=set(norm(x["NOMBRE"]) for x in roster)
  ix=Head();ix.feed(get(INDEX).decode("utf-8","replace"))
  links={}
  for u in ix.links:
   q=parse_qs(urlparse(u).query);z=q.get("_diputadomodule_codParlamentario",[])
   if len(z)==1 and z[0].isdigit() and q.get("_diputadomodule_idLegislatura")==["XV"]:
    links[int(z[0])]=u
  original=sorted(links);train={original[round(i*(len(original)-1)/7)] for i in range(8)}
  pool=[n for n in original if n not in train]
  choose=sorted(pool,key=lambda n:hashlib.sha256(("AB20_C04_HOLDOUT_"+str(n)).encode()).hexdigest())[:16]
  records=[]
  for n in choose:
   h=Head();blob=get(links[n]);h.feed(blob.decode("utf-8","replace"))
   candidates=set()
   for t,s in h.headings:
    if t=="h2":
     value=norm(s)
     candidates.update(v for v in keys if v in value)
   records.append({"code":n,"n_h2_name_matches":len(candidates),"profile_sha256":hashlib.sha256(blob).hexdigest()})
  out.update(status="HOLDOUT_OBSERVED",sample_size=len(records),unique=sum(x["n_h2_name_matches"]==1 for x in records),empty=sum(x["n_h2_name_matches"]==0 for x in records),multiple=sum(x["n_h2_name_matches"]>1 for x in records),records=records,freeze="H2 matcher unchanged since C03",independent_publisher=False)
 except Exception as e:out.update(error_type=type(e).__name__,error_code=str(e)[:100])
 P.mkdir(parents=True,exist_ok=True);(P/"C04_result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C04="+json.dumps(out,ensure_ascii=False))
if __name__=="__main__":run()
