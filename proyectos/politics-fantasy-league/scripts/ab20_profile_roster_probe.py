#!/usr/bin/env python3
"""C02 original Congress sample profile↔open-data name text diagnostic, no names released."""
from pathlib import Path
from urllib.parse import urlparse,parse_qs,urljoin
from urllib.request import Request,urlopen
from html.parser import HTMLParser
from collections import Counter
import unicodedata,json,re,hashlib
INDEX="https://www.congreso.es/es/index-diputados?_diputadosindex_viewMode=1&idLegislatura=15&p_p_id=diputadosindex&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal"
ROOT=Path("/tmp/pfl-ab20")
OLD=Path("/tmp/pf-congress-probe")
class Scan(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.parts=[];self.within_script=0
 def handle_starttag(self,t,a):
  if t=="a":
   h=dict(a).get("href")
   if h:self.links.append(urljoin(INDEX,h))
  if t in ("script","style"):self.within_script+=1
 def handle_endtag(self,t):
  if t in ("script","style"):self.within_script=max(0,self.within_script-1)
 def handle_data(self,s):
  if not self.within_script:self.parts.append(s)
def norm(s):
 return " ".join(unicodedata.normalize("NFKC",str(s)).casefold().split())
def download(u,cap):
 with urlopen(Request(u,headers={"User-Agent":"PFL-AB20-Research/0.1"}),timeout=19) as h:
  p=urlparse(h.geturl())
  if h.status!=200 or p.scheme!="https" or p.hostname!="www.congreso.es":raise ValueError("OFFICIAL_HOST")
  v=h.read(cap+1)
 if len(v)>cap:raise ValueError("FILE_OVERSIZE")
 return v
def main():
 res={"cycle":"C02","status":"STOP_R5","sample_count":0}
 try:
  active=json.loads((OLD/"official_1.json").read_text(encoding="utf-8-sig"))
  discharged=json.loads((OLD/"official_7.json").read_text(encoding="utf-8-sig"))
  names=set(norm(x["NOMBRE"]) for x in active+discharged)
  ix=Scan();ix.feed(download(INDEX,3_000_000).decode("utf-8","replace"))
  links={}
  for url in ix.links:
   q=parse_qs(urlparse(url).query);a=q.get("_diputadomodule_codParlamentario",[])
   if len(a)==1 and a[0].isdigit() and q.get("_diputadomodule_idLegislatura")==["XV"]:links[int(a[0])]=url
  if len(links)<350:raise ValueError("MISSING_INDEX_COVERAGE")
  ids=sorted(links)
  chosen=[ids[round(i*(len(ids)-1)/7)] for i in range(8)]
  result=[]
  for code in chosen:
   record={"source_scoped_code":code,"retrieved":False}
   try:
    blob=download(links[code],2_000_000);html=Scan();html.feed(blob.decode("utf-8","replace"))
    clean=norm(" ".join(html.parts))
    exact=[name for name in names if name in clean]
    record.update(retrieved=True,sha256=hashlib.sha256(blob).hexdigest(),
        exact_roster_name_occurrences=len(exact),matched_one=(len(exact)==1),contains_legislature=("xv legislatura" in clean))
   except Exception as e:record.update(error_type=type(e).__name__)
   result.append(record)
  res.update(status="SAMPLED_PROFILES",sample_count=len(chosen),retrieved=sum(v["retrieved"] for v in result),
    exactly_one_roster_name=sum(v.get("matched_one",False) for v in result),
    multiple_candidate_names=sum(v.get("exact_roster_name_occurrences",0)>1 for v in result),
    no_candidate_names=sum(v.get("exact_roster_name_occurrences",-1)==0 for v in result),
    records=result,warning="Diagnostics only, no accepted identity joins; sampled codes deterministic, NOT random")
 except Exception as e:res.update(error_type=type(e).__name__,error_code=str(e)[:100])
 ROOT.mkdir(parents=True,exist_ok=True)
 (ROOT/"C02_result.json").write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C02="+json.dumps(res,ensure_ascii=False))
if __name__=="__main__":main()
