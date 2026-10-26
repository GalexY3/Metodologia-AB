#!/usr/bin/env python3
"""C10 test official before-vs-after group codes of one July2025 BOCG case and negative control."""
from pathlib import Path
from collections import defaultdict
from urllib.request import Request,urlopen
from urllib.parse import urlparse
from html.parser import HTMLParser
import json,hashlib
from ab20_profile_semantic import norm
P=Path("/tmp/pfl-ab20");RO=Path("/tmp/pf-congress-probe")
URLS={
"apr24":"https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion034/20240409/Votacion001/VOT_20240409210631.json",
"jul26":"https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion193/20260723/Votacion001/VOT_20260723211929.json",
"jun25":"https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion118/20250612/Votacion001/VOT_20250612132238.json",
"sep25":"https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion130/20250910/Votacion001/VOT_20250910213532.json"}
PUB="https://www.congreso.es/es/busqueda-de-publicaciones?_publicaciones_id_texto=BOCG-15-D-372.CODI.&_publicaciones_legislatura=XV&_publicaciones_mode=mostrarTextoIntegro&p_p_id=publicaciones&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal"
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
def get(u):
 with urlopen(Request(u,headers={"User-Agent":"PFL-AB20/0.1"}),timeout=26) as h:
  p=urlparse(h.geturl())
  if h.status!=200 or p.scheme!="https" or p.hostname!="www.congreso.es":raise ValueError("SOURCE_HOST")
  b=h.read(5_000_001)
 if len(b)>5_000_000:raise ValueError("OVER_LIMIT")
 return b
def main():
 x={"cycle":"C10","status":"STOP_R5"}
 try:
  raw={k:get(u) for k,u in URLS.items()}
  data={k:json.loads(b) for k,b in raw.items()}
  docraw=get(PUB);doc=Text();doc.feed(docraw.decode("utf-8","replace"));text=norm(" ".join(doc.parts))
  a=json.loads((RO/"official_1.json").read_text())+json.loads((RO/"official_7.json").read_text())
  people={norm(v["NOMBRE"]):v for v in a}
  canonical=defaultdict(set)
  for v in data["jul26"]["votaciones"]:
   me=people.get(norm(v["diputado"]))
   if me:canonical[v["grupo"]].add(me["GRUPOPARLAMENTARIO"])
  mismatches=[]
  for v in data["apr24"]["votaciones"]:
   name=norm(v["diputado"]);r=people.get(name)
   if r and r["GRUPOPARLAMENTARIO"] not in canonical.get(v["grupo"],set()):mismatches.append(name)
  if len(mismatches)!=2:raise ValueError("NOT_TWO_KNOWN_MISMATCHES")
  flagged=[name for name in mismatches if name in text]
  if len(flagged)!=1:raise ValueError("BOCG_NOT_SINGLE_CANDIDATE")
  rows={k:{norm(v["diputado"]):v["grupo"] for v in d["votaciones"]} for k,d in data.items()}
  def transitions(name):
    pre=rows["jun25"].get(name);post=rows["sep25"].get(name)
    return {"present_pre":pre is not None,"present_post":post is not None,"pre_group":pre,"post_group":post,"changed":pre!=post if pre and post else None}
  target=transitions(flagged[0]);control=transitions(next(n for n in mismatches if n!=flagged[0]))
  x.update(status="PRE_POST_SOURCE_TRIAL",observed_original_hashes={k:hashlib.sha256(z).hexdigest() for k,z in raw.items()},BOCG_sha256=hashlib.sha256(docraw).hexdigest(),
           treated=target,control=control,matched_document_change_count=len(flagged),no_automatic_legal_identity=True,
           prediction_treated_Sumar_to_Mixto=(target["pre_group"]=="GSUMAR" and target["post_group"]=="GMx"),
           negative_control_stable=(control["changed"] is False),
           explanation_limit="Date-ordered institutional group traces, not causal identification")
 except Exception as e:x.update(error_type=type(e).__name__,error_code=str(e)[:100])
 P.mkdir(parents=True,exist_ok=True);(P/"C10_result.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C10="+json.dumps(x,ensure_ascii=False))
if __name__=="__main__":main()
