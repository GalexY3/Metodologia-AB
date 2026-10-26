#!/usr/bin/env python3
"""C08 original Congress group composition HTML ID/date audit, no personal data exported."""
from html.parser import HTMLParser
from urllib.parse import urlparse,parse_qs,urljoin
from urllib.request import Request,urlopen
from pathlib import Path
import re,hashlib,json
P=Path("/tmp/pfl-ab20")
URL="https://www.congreso.es/es/grupos/composicion-en-la-legislatura?idLegislatura=XV"
class S(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.parts=[]
 def handle_starttag(self,t,a):
  if t=="a":
   h=dict(a).get("href")
   if h:self.links.append(urljoin(URL,h))
 def handle_data(self,x):self.parts.append(x)
def main():
 r={"cycle":"C08","status":"STOP_R5"}
 try:
  with urlopen(Request(URL,headers={"User-Agent":"PFL-AB20/0.1"}),timeout=25) as h:
   u=urlparse(h.geturl())
   if u.scheme!="https" or u.hostname!="www.congreso.es" or h.status!=200:raise ValueError("HOST")
   raw=h.read(4_000_001)
  if len(raw)>4_000_000:raise ValueError("OVERSIZE")
  x=S();x.feed(raw.decode("utf-8","replace"))
  codes=set()
  for url in x.links:
   for k,v in parse_qs(urlparse(url).query).items():
    if "codParlamentario" in k and len(v)==1 and v[0].isdigit():codes.add(v[0])
  plain=" ".join(x.parts).casefold()
  dates=re.findall(r"\b(?:0?[1-9]|[12][0-9]|3[01])/(?:0?[1-9]|1[012])/20\d{2}\b",plain)
  r.update(status="OFFICIAL_GROUP_PAGE_OBSERVED",sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),member_code_count=len(codes),absolute_date_tokens=len(dates),distinct_date_tokens=len(set(dates)),group_mentions=plain.count("grupo parlamentario"),dynamic_loading=("loading" in plain or "cargando" in plain),historical_membership_verified=False)
 except Exception as e:r.update(error_type=type(e).__name__,error_code=str(e)[:100])
 P.mkdir(parents=True,exist_ok=True);(P/"C08_result.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C08="+json.dumps(r,ensure_ascii=False))
if __name__=="__main__":main()
