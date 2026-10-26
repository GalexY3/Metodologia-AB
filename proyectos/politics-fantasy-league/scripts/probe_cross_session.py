#!/usr/bin/env python3
"""C14: discover an official second-session vote JSON by href, NEVER guess hash suffix."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlparse
import hashlib,json
ROOT=Path("/tmp/pf-congress-probe")
URL="https://www.congreso.es/es/opendata/votaciones?targetDate=30%2F09%2F2026&targetLegislatura=XV"
class Finder(HTMLParser):
 def __init__(self):
    super().__init__();self.hrefs=[]
 def handle_starttag(self,tag,attrs):
    if tag=="a":
        href=dict(attrs).get("href")
        if href:self.hrefs.append(urljoin(URL,href))
def get(url,lim):
  with urlopen(Request(url,headers={"User-Agent":"PFL-AB32-Research/0.1"}),timeout=26) as res:
    p=urlparse(res.geturl())
    if p.scheme!="https" or p.hostname!="www.congreso.es" or res.status!=200:raise ValueError("CROSS_HOST")
    data=res.read(lim+1)
  if len(data)>lim or len(data)<80:raise ValueError("SIZE")
  return data
def run():
  result={"cycle":"C14","calendar":URL,"status":"STOP_R5"}
  try:
    html=get(URL,3_000_000);finder=Finder();finder.feed(html.decode("utf-8","replace"))
    votes=sorted(set(x for x in finder.hrefs if "/webpublica/opendata/votaciones/Leg15/Sesion202/" in x and x.lower().endswith(".json")))
    result["discovered_vote_json_count"]=len(votes)
    result["calendar_sha256"]=hashlib.sha256(html).hexdigest()
    if not votes:raise ValueError("NO_JSON_LINKS_FOR_SESSION202")
    chosen=votes[0]
    blob=get(chosen,4_000_000);obj=json.loads(blob)
    if not isinstance(obj.get("votaciones"),list) or obj["informacion"]["sesion"]!=202:raise ValueError("NOT_SESSION202_VOTE")
    ROOT.mkdir(parents=True,exist_ok=True)
    (ROOT/"session202_vote_original.json").write_bytes(blob)
    (ROOT/"session202_urls.json").write_text(json.dumps(votes,ensure_ascii=False,indent=2)+"\n")
    result.update(status="ORIGINAL_SESSION202_CAPTURED",source_url=chosen,source_sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),vote_rows=len(obj["votaciones"]),vote_date=obj["informacion"]["fecha"],vote_number=obj["informacion"]["numeroVotacion"],total=obj["totales"])
  except Exception as exc:result.update(error_type=type(exc).__name__,http_code=getattr(exc,"code",None))
  ROOT.mkdir(parents=True,exist_ok=True)
  (ROOT/"cross_session_discovery.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
  print("C14_CROSS_SESSION="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":run()
