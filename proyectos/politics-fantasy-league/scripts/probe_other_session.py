#!/usr/bin/env python3
"""C17: deliberately query independently indexed official voting day, no guessed JSON timestamp."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlparse
import json,hashlib
ROOT=Path("/tmp/pf-congress-probe")
URL="https://www.congreso.es/es/opendata/votaciones?targetDate=10%2F09%2F2026&targetLegislatura=XV"
class Links(HTMLParser):
 def __init__(self):super().__init__();self.hrefs=[]
 def handle_starttag(self,tag,attrs):
    if tag=="a":
      val=dict(attrs).get("href")
      if val:self.hrefs.append(urljoin(URL,val))
def get(u,limit):
 with urlopen(Request(u,headers={"User-Agent":"PFL-Research-AB32/0.1"}),timeout=25) as f:
    x=urlparse(f.geturl())
    if x.scheme!="https" or x.hostname!="www.congreso.es" or f.status!=200:raise ValueError("OFFICIAL_HOST_MISMATCH")
    b=f.read(limit+1)
 if len(b)>limit:raise ValueError("FILE_TOO_LARGE")
 return b
def main():
 result={"cycle":"C17","calendar":URL,"status":"STOP_R5"}
 try:
    raw=get(URL,3_000_000);h=Links();h.feed(raw.decode("utf-8","replace"))
    links=sorted(set(x for x in h.hrefs if "/webpublica/opendata/votaciones/Leg15/Sesion196/20260910/" in x and x.endswith(".json")))
    result.update(official_json_links=len(links),calendar_sha256=hashlib.sha256(raw).hexdigest())
    if not links:raise ValueError("NO_OFFICIAL_SESSION196_LINKS")
    js=get(links[0],4_000_000);event=json.loads(js)
    assert event["informacion"]["sesion"]==196
    assert event["informacion"]["fecha"] in ("10/9/2026","10/09/2026")
    ROOT.mkdir(parents=True,exist_ok=True)
    (ROOT/"session196_vote_original.json").write_bytes(js)
    result.update(status="ORIGINAL_INDEPENDENT_DAY_CAPTURED",source_url=links[0],source_sha256=hashlib.sha256(js).hexdigest(),bytes=len(js),vote_rows=len(event["votaciones"]),date=event["informacion"]["fecha"],declared_totals=event["totales"])
 except Exception as e:result.update(error_type=type(e).__name__,http_code=getattr(e,"code",None))
 ROOT.mkdir(parents=True,exist_ok=True)
 (ROOT/"session196_discovery.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("C17_OTHER_DAY="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
