#!/usr/bin/env python3
"""C07 independent Congress BOCG historical change-event source vs 2024 vote orphan; no names logged."""
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urlparse
from pathlib import Path
import unicodedata,re,hashlib,json
from ab20_profile_semantic import norm
BOCG="https://www.congreso.es/es/busqueda-de-publicaciones?_publicaciones_id_texto=BOCG-15-D-121.CODI.&_publicaciones_legislatura=XV&_publicaciones_mode=mostrarTextoIntegro&p_p_id=publicaciones&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal"
VOTE="https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion034/20240409/Votacion001/VOT_20240409210631.json"
OLD=Path("/tmp/pf-congress-probe");ROOT=Path("/tmp/pfl-ab20")
class Txt(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=False
 def handle_data(self,x):self.parts.append(x)
def get(u,cap):
 with urlopen(Request(u,headers={"User-Agent":"PFL-AB20-Research/0.1"}),timeout=25) as r:
  p=urlparse(r.geturl())
  if p.scheme!="https" or p.hostname!="www.congreso.es" or r.status!=200:raise ValueError("NOT_VERIFIED_SOURCE")
  b=r.read(cap+1)
 if len(b)>cap:raise ValueError("DOCUMENT_OVERSIZE")
 return b
def run():
 out={"cycle":"C07","status":"STOP_R5"}
 try:
  original=get(BOCG,4_000_000);h=Txt();h.feed(original.decode("utf-8","replace"))
  flat=norm(" ".join(h.parts))
  if "11 de abril de 2024" not in flat or "grupo" not in flat or "bocg" not in flat:raise ValueError("NOT_EXPECTED_OFFICIAL_BOCG")
  people=json.loads((OLD/"official_1.json").read_text())+json.loads((OLD/"official_7.json").read_text())
  names=set(norm(x["NOMBRE"]) for x in people)
  vote=get(VOTE,3_000_000);rows=json.loads(vote)["votaciones"]
  miss=set(norm(x["diputado"]) for x in rows)-names
  if len(miss)!=1:raise ValueError("NOT_ONE_ORPHAN")
  # Source is separate publication; identity cannot follow automatically.
  flag=next(iter(miss)) in flat
  out.update(status="BOCG_ORIGINAL_OBSERVED",BOCG_sha256=hashlib.sha256(original).hexdigest(),vote_sha256=hashlib.sha256(vote).hexdigest(),
             has_composition_notice=("composicion y organizacion" in unicodedata.normalize("NFKD",flat).encode("ascii","ignore").decode()),orphan_exact_spelling_in_notice=flag,
             group_mentions=flat.count("grupos parlamentarios"),change_notice_mentions=flat.count("altas")+flat.count("bajas")+flat.count("alta:")+flat.count("baja:"),
             independently_proven_person_id=False,publication_calendar_date="2024-04-11")
 except Exception as e:out.update(error_type=type(e).__name__,error_code=str(e)[:90])
 ROOT.mkdir(parents=True,exist_ok=True);(ROOT/"C07_result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C07="+json.dumps(out,ensure_ascii=False))
if __name__=="__main__":run()
