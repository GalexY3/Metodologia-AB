#!/usr/bin/env python3
"""C06: orthographic comparison only, no names or automatic identity output."""
from pathlib import Path
from collections import Counter
from urllib.request import Request,urlopen
from urllib.parse import urlparse
from difflib import SequenceMatcher
import unicodedata,re,json,hashlib
from ab20_profile_semantic import norm
A="https://www.congreso.es/webpublica/opendata/diputados/Diput__20261026050221.json"
V="https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion034/20240409/Votacion001/VOT_20240409210631.json"
OLD=Path("/tmp/pf-congress-probe");P=Path("/tmp/pfl-ab20")
def get(u,cap):
 with urlopen(Request(u,headers={"User-Agent":"PFL-AB20/0.1"}),timeout=35) as resp:
  p=urlparse(resp.geturl())
  if resp.status!=200 or p.scheme!="https" or p.hostname!="www.congreso.es":raise ValueError("OFFICIAL_HOST")
  v=resp.read(cap+1)
 if len(v)>cap:raise ValueError("OVERSIZE")
 return v
def orth(s):
 s=unicodedata.normalize("NFKD",norm(s))
 s="".join(c for c in s if not unicodedata.combining(c))
 return " ".join(re.sub(r"[^\w]+"," ",s).split())
def main():
 result={"cycle":"C06","status":"STOP_R5"}
 try:
  roster=json.loads((OLD/"official_1.json").read_text())+json.loads((OLD/"official_7.json").read_text())
  names={norm(z["NOMBRE"]) for z in roster}
  raw=get(V,3_000_000);v=json.loads(raw)
  target=set(norm(z["diputado"]) for z in v["votaciones"])-names
  if len(target)!=1:raise ValueError("NO_UNIQUE_ORPHAN_TO_STUDY")
  q=next(iter(target))
  archraw=get(A,24_000_000);arch=json.loads(archraw)
  arch_names={norm(z.get("APELLIDOS","")+", "+z.get("NOMBRE","")) for z in arch}
  if q in arch_names:raise ValueError("NOT_AN_ORPHAN_IN_ARCHIVE")
  key=orth(q);n=Counter(orth(z) for z in names);a=Counter(orth(z) for z in arch_names)
  sim_name=sorted((SequenceMatcher(None,key,z).ratio() for z in n),reverse=True)
  sim_arch=sorted((SequenceMatcher(None,key,z).ratio() for z in a),reverse=True)
  result.update(status="ORTHOGRAPHIC_DIAGNOSIS",original_vote_sha=hashlib.sha256(raw).hexdigest(),archive_sha=hashlib.sha256(archraw).hexdigest(),conservative_roster_candidates=n[key],conservative_archive_name_candidates=a[key],roster_fuzzy_top2=[round(z,4) for z in sim_name[:2]],archive_fuzzy_top2=[round(z,4) for z in sim_arch[:2]],identity_resolved=False,warning="Fuzzy is diagnostic, not evidence of same person")
 except Exception as e:result.update(error_type=type(e).__name__,error_code=str(e)[:100])
 P.mkdir(parents=True,exist_ok=True);(P/"C06_result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C06="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
