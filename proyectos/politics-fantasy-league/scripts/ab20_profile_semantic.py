#!/usr/bin/env python3
"""C03 semantic heading-based source record linkage; counts only, no personal names."""
from html.parser import HTMLParser
from html import unescape
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlparse,parse_qs,urljoin
import unicodedata,json,hashlib
ROOT=Path("/tmp/pfl-ab20")
OLD=Path("/tmp/pf-congress-probe")
INDEX="https://www.congreso.es/es/index-diputados?_diputadosindex_viewMode=1&idLegislatura=15&p_p_id=diputadosindex&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal"
def norm(s):return " ".join(unicodedata.normalize("NFKC",unescape(str(s))).casefold().split())
class Head(HTMLParser):
 def __init__(self):
  super().__init__();self.in_head=[];self.headings=[];self.title=[];self.links=[];self.meta_titles=[]
 def handle_starttag(self,t,a):
  if t in ("h1","h2","h3","h4","title"):self.in_head.append([t,[]])
  if t=="a":
   v=dict(a).get("href")
   if v:self.links.append(urljoin(INDEX,v))
  if t=="meta":
   d=dict(a)
   if d.get("property","").lower() in ("og:title","twitter:title") and d.get("content"):self.meta_titles.append(d["content"])
 def handle_data(self,s):
  if self.in_head:self.in_head[-1][1].append(s)
 def handle_endtag(self,t):
  if self.in_head and self.in_head[-1][0]==t:
   _,parts=self.in_head.pop();line=" ".join("".join(parts).split())
   if t=="title":self.title.append(line)
   else:self.headings.append((t,line))
def get(url):
 with urlopen(Request(url,headers={"User-Agent":"PFL-AB20-Research/0.1"}),timeout=19) as r:
  p=urlparse(r.geturl())
  if r.status!=200 or p.scheme!="https" or p.hostname!="www.congreso.es":raise ValueError("INVALID_CONGRESS_HOST")
  raw=r.read(2_000_001)
 if len(raw)>2_000_000:raise ValueError("OVERSIZE")
 return raw
def main():
 report={"cycle":"C03","status":"STOP_R5"}
 try:
  roster=json.loads((OLD/"official_1.json").read_text())+json.loads((OLD/"official_7.json").read_text())
  keys=set(norm(q["NOMBRE"]) for q in roster)
  x=Head();x.feed(get(INDEX).decode("utf-8","replace"))
  ix={}
  for u in x.links:
   q=parse_qs(urlparse(u).query)
   id=q.get("_diputadomodule_codParlamentario",[])
   if len(id)==1 and id[0].isdigit() and q.get("_diputadomodule_idLegislatura")==["XV"]:
    ix[int(id[0])]=u
  ids=sorted(ix)
  selected=[ids[round(i*(len(ids)-1)/7)] for i in range(8)]
  records=[]
  for id in selected:
   raw=get(ix[id]);h=Head();h.feed(raw.decode("utf-8","replace"))
   candidate_by_tag={}
   for typ in ("h1","h2","h3","h4","meta","title"):
    strings=[v for t,v in h.headings if t==typ] if typ not in ("meta","title") else (h.meta_titles if typ=="meta" else h.title)
    matched=set()
    for value in strings:
     n=norm(value)
     for key in keys:
      if key and key in n:matched.add(key)
    candidate_by_tag[typ]=len(matched)
   records.append({"codParlamentario":id,"matched_name_count_by_tag":candidate_by_tag,"headings_count":len(h.headings),"document_sha256":hashlib.sha256(raw).hexdigest()})
  report.update(status="DOM_HEADING_INSPECTED",sample_count=len(records),records=records,
   unique_any_heading=sum(any(v==1 for k,v in rec["matched_name_count_by_tag"].items() if k.startswith("h")) for rec in records),
   exactly_one_h1=sum(rec["matched_name_count_by_tag"]["h1"]==1 for rec in records),
   exactly_one_h2=sum(rec["matched_name_count_by_tag"]["h2"]==1 for rec in records),
   exactly_one_ogtitle=sum(rec["matched_name_count_by_tag"]["meta"]==1 for rec in records),
   caveat="No automated identity joins accepted: tag-based exact names are diagnostic and may contain other actors.")
 except Exception as e:report.update(error_type=type(e).__name__,error_code=str(e)[:120])
 ROOT.mkdir(parents=True,exist_ok=True);(ROOT/"C03_result.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C03="+json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
