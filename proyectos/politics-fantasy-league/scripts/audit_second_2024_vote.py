#!/usr/bin/env python3
"""C25 confirm source-scoped 2024 name/group drift on distinct second original vote."""
from html.parser import HTMLParser
from collections import Counter,defaultdict
from datetime import date
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlparse
import json,hashlib,unicodedata
P=Path("/tmp/pf-congress-probe")
URL="https://www.congreso.es/es/opendata/votaciones?targetDate=09%2F04%2F2024&targetLegislatura=XV"
class H(HTMLParser):
 def __init__(self):super().__init__();self.hrefs=[]
 def handle_starttag(self,t,a):
    if t=="a":
      v=dict(a).get("href")
      if v:self.hrefs.append(urljoin(URL,v))
def norm(s):return " ".join(unicodedata.normalize("NFKC",str(s)).casefold().split())
def get(url):
 with urlopen(Request(url,headers={"User-Agent":"PF-AB32/0.1"}),timeout=18) as r:
    u=urlparse(r.geturl())
    if u.scheme!="https" or u.hostname!="www.congreso.es" or r.status!=200:raise ValueError("BAD_OFFICIAL_HOST")
    return r.read(4_000_001)
def main():
 output={"cycle":"C25","status":"STOP_R5"}
 try:
    html=get(URL);p=H();p.feed(html.decode("utf8","replace"))
    links=sorted(set(x for x in p.hrefs if "/webpublica/opendata/votaciones/Leg15/Sesion034/20240409/" in x and x.endswith(".json")))
    if len(links)<2:raise ValueError("SECOND_VOTE_MISSING")
    data=get(links[1]);doc=json.loads(data)
    active=json.loads((P/"official_1.json").read_text());baja=json.loads((P/"official_7.json").read_text())
    rost={norm(x["NOMBRE"]):x for x in active+baja}
    old=json.loads((P/"vote_original.json").read_text())
    aliases=defaultdict(set)
    for v in old["votaciones"]:
      q=rost.get(norm(v["diputado"]))
      if q:aliases[v["grupo"]].add(q["GRUPOPARLAMENTARIO"])
    flags=Counter()
    for v in doc["votaciones"]:
      x=rost.get(norm(v["diputado"]))
      if x is None:flags["unmatched_name"]+=1;continue
      if x["GRUPOPARLAMENTARIO"] not in aliases.get(v["grupo"],set()):
         flags["group_map_conflict"]+=1
    totals=doc["totales"];counts=Counter(v["voto"] for v in doc["votaciones"])
    output.update(status="SECOND_2024_ORIGINAL_ANALYZED",source_url=links[1],sha256=hashlib.sha256(data).hexdigest(),vote_rows=len(doc["votaciones"]),calendar_links=len(links),vote_number=doc["informacion"]["numeroVotacion"],diff_counts=dict(flags),official_tallies_match=(totals["afavor"],totals["enContra"],totals["abstenciones"],totals["noVotan"])==(counts["Sí"],counts["No"],counts["Abstención"],counts["No vota"]))
 except Exception as ex:output.update(error_type=type(ex).__name__,error_code=str(ex)[:70])
 P.mkdir(parents=True,exist_ok=True)
 (P/"second_2024_vote_audit.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
 print("C25_SECOND_2024="+json.dumps(output,ensure_ascii=False))
if __name__=="__main__":main()
