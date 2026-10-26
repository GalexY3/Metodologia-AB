#!/usr/bin/env python3
"""C09 cross-source BOCG July 2025 change attribution candidates; no politician names logged."""
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from html.parser import HTMLParser
from collections import defaultdict
import unicodedata,json,hashlib
from ab20_profile_semantic import norm
P=Path("/tmp/pfl-ab20");OLD=Path("/tmp/pf-congress-probe")
PUB="https://www.congreso.es/es/busqueda-de-publicaciones?_publicaciones_id_texto=BOCG-15-D-372.CODI.&_publicaciones_legislatura=XV&_publicaciones_mode=mostrarTextoIntegro&p_p_id=publicaciones&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal"
APR="https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion034/20240409/Votacion001/VOT_20240409210631.json"
JUL="https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion193/20260723/Votacion001/VOT_20260723211929.json"
class T(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
def get(u,cap):
 with urlopen(Request(u,headers={"User-Agent":"PFL-AB20/0.1"}),timeout=25) as h:
  z=urlparse(h.geturl())
  if h.status!=200 or z.scheme!="https" or z.hostname!="www.congreso.es":raise ValueError("BAD_SOURCE")
  raw=h.read(cap+1)
 if len(raw)>cap:raise ValueError("OVERSIZE")
 return raw
def main():
 res={"cycle":"C09","status":"STOP_R5"}
 try:
  roster=json.loads((OLD/"official_1.json").read_text())+json.loads((OLD/"official_7.json").read_text())
  names={norm(x["NOMBRE"]):x for x in roster}
  old=get(APR,2_000_000);latest=get(JUL,2_000_000);notice=get(PUB,5_000_000)
  oldrows=json.loads(old)["votaciones"];current=json.loads(latest)["votaciones"]
  groups=defaultdict(set)
  for v in current:
   rec=names.get(norm(v["diputado"]))
   if rec:groups[v["grupo"]].add(rec["GRUPOPARLAMENTARIO"])
  mismatch=[]
  for v in oldrows:
   rec=names.get(norm(v["diputado"]))
   if rec and rec["GRUPOPARLAMENTARIO"] not in groups.get(v["grupo"],set()):
    mismatch.append(norm(v["diputado"]))
  doc=T();doc.feed(notice.decode("utf-8","replace"));text=norm(" ".join(doc.parts))
  if "7 de julio de 2025" not in text or "grupos parlamentarios" not in text:raise ValueError("NOT_DATED_OFFICIAL_NOTICE")
  matched=sum(key in text for key in mismatch)
  res.update(status="BOCG_GROUP_CHANGE_TESTED",notice_sha256=hashlib.sha256(notice).hexdigest(),
   historic_vote_sha256=hashlib.sha256(old).hexdigest(),current_vote_sha256=hashlib.sha256(latest).hexdigest(),
   group_conflicts_2024=len(mismatch),documented_conflict_name_occurrences=matched,
   Sumar_and_Mixto_in_notice=("sumar" in text and "mixto" in text),
   effective_july3_mentioned=("03-07-2025" in text or "3 de julio de 2025" in text),
   link_to_people_approved=False,warning="Cross-document name overlap only; no causal claim of exactly which group change without vote-before/after test")
 except Exception as e:res.update(error_type=type(e).__name__,error_code=str(e)[:100])
 P.mkdir(parents=True,exist_ok=True);(P/"C09_result.json").write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C09="+json.dumps(res,ensure_ascii=False))
if __name__=="__main__":main()
