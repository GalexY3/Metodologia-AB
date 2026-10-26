#!/usr/bin/env python3
"""C05: archive explains one 2024 unmatched rollcall name? Never emit any name."""
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen
from pathlib import Path
from collections import Counter
import json,unicodedata,hashlib
from ab20_profile_semantic import norm
P=Path("/tmp/pfl-ab20");OLD=Path("/tmp/pf-congress-probe")
CAT="https://www.congreso.es/es/opendata/diputados"
VOTE="https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion034/20240409/Votacion001/VOT_20240409210631.json"
class Links(HTMLParser):
 def __init__(self):super().__init__();self.href=None;self.parts=[];self.found=[]
 def handle_starttag(self,t,a):
  if t=="a":self.href=dict(a).get("href");self.parts=[]
 def handle_data(self,s):
  if self.href is not None:self.parts.append(s)
 def handle_endtag(self,t):
  if t=="a" and self.href is not None:
   self.found.append((" ".join("".join(self.parts).split()),urljoin(CAT,self.href)))
   self.href=None
def get(url,cap):
 with urlopen(Request(url,headers={"User-Agent":"PFL-AB20-Research/0.1"}),timeout=30) as h:
  u=urlparse(h.geturl())
  if h.status!=200 or u.scheme!="https" or u.hostname!="www.congreso.es":raise ValueError("SOURCE_HOST")
  blob=h.read(cap+1)
 if len(blob)>cap:raise ValueError("SOURCE_OVERSIZE")
 return blob
def run():
 res={"cycle":"C05","status":"STOP_R5"}
 try:
  active=json.loads((OLD/"official_1.json").read_text());departed=json.loads((OLD/"official_7.json").read_text())
  current={norm(x["NOMBRE"]) for x in active+departed}
  raw=get(VOTE,3_000_000);v=json.loads(raw)
  past={norm(x["diputado"]) for x in v["votaciones"]}
  miss=sorted(past-current)
  res.update(vote_sha256=hashlib.sha256(raw).hexdigest(),voter_names_missing_current=len(miss))
  if len(miss)!=1:raise ValueError("EXPECTED_ONE_MISSING_NAME_INVALIDATED")
  html=get(CAT,3_000_000);links=Links();links.feed(html.decode("utf-8","replace"))
  json_links=[url for label,url in links.found if label.casefold()=="json" and urlparse(url).path.startswith("/webpublica/opendata/diputados/") and urlparse(url).path.endswith(".json")]
  # Source catalogue order independently verified in the official open-data page:
  # 0 activo, 1 intereses, 2 bajas, 3 diputadas all terms, 4 TODOS diputados all terms.
  res["json_dataset_links"]=len(json_links)
  if len(json_links)<5:raise ValueError("CATALOGUE_JSON_ORDER_UNVERIFIABLE")
  matches=[json_links[4]]
  res["archival_json_links"]=len(matches)
  res["repair_note"]="C05 correction 2: official current catalogue category order, 5th JSON link, rather than stale dated endpoint or preceding label in anchor"
  arch=get(matches[0],24_000_000)
  data=json.loads(arch)
  if not isinstance(data,list) or not data:raise ValueError("ARCHIVE_NOT_ARRAY")
  labels=[str(x.get("NOMBRE","")) for x in data if isinstance(x,dict)]
  compare=Counter(norm(s) for s in labels)
  res.update(status="ARCHIVE_EXAMINED",archival_source_url=matches[0],archival_sha256=hashlib.sha256(arch).hexdigest(),archive_rows=len(data),archive_fields=sorted(data[0].keys()) if isinstance(data[0],dict) else [],target_exact_archival_matches=compare.get(miss[0],0),current_people_keys=len(current),vote_name_keys=len(past),archive_distinct_name_keys=len(compare),identity_verified=False)
 except Exception as e:res.update(error_type=type(e).__name__,error_code=str(e)[:110])
 P.mkdir(parents=True,exist_ok=True);(P/"C05_result.json").write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C05="+json.dumps(res,ensure_ascii=False))
if __name__=="__main__":run()
