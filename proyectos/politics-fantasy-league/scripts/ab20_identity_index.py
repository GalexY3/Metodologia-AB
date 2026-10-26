#!/usr/bin/env python3
"""C01 — Congress official XV profile index and one canonical profile; no names logged."""
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse,parse_qs
from urllib.request import Request,urlopen
from collections import Counter
from pathlib import Path
import hashlib,json,re,os
URL="https://www.congreso.es/es/index-diputados?_diputadosindex_viewMode=1&idLegislatura=15&p_p_id=diputadosindex&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal"
OUT=Path("/tmp/pfl-ab20")
class P(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=="a":
   d=dict(attrs)
   if d.get("href"):self.links.append((urljoin(URL,d["href"]),d))
def fetch(url,cap):
 with urlopen(Request(url,headers={"User-Agent":"PFL-AB20-official-research/0.1"}),timeout=25) as x:
  p=urlparse(x.geturl())
  if x.status!=200 or p.scheme!="https" or p.hostname!="www.congreso.es":raise ValueError("UNVERIFIED_OFFICIAL_HOST")
  b=x.read(cap+1)
 if len(b)>cap or len(b)<200:raise ValueError("SIZE")
 return b
def main():
 result={"cycle":"C01","source":URL,"status":"STOP_R5"}
 try:
  raw=fetch(URL,3_000_000)
  parser=P();parser.feed(raw.decode("utf-8","replace"))
  records=[]
  for url,attrs in parser.links:
   q=parse_qs(urlparse(url).query)
   codes=q.get("_diputadomodule_codParlamentario",[])
   legs=q.get("_diputadomodule_idLegislatura",[])
   if len(codes)==1 and re.fullmatch(r"[0-9]{1,5}",codes[0]) and legs==["XV"]:
    records.append((int(codes[0]),url))
  n=Counter(x for x,_ in records)
  result.update(index_sha256=hashlib.sha256(raw).hexdigest(),total_a_hrefs=len(parser.links),indexed_profile_hrefs=len(records),unique_codParlamentario=len(n),duplicate_profile_href_counts=sum(v-1 for v in n.values() if v>1),source_legislature="XV",all_codes_numeric=True)
  if not records:raise ValueError("NO_CANONICAL_ID_LINKS")
  # Discover only one canonical profile; never scrape persons at scale.
  sample=min(records,key=lambda rec:rec[0])
  page=fetch(sample[1],2_000_000)
  result.update(profile_sample_id=sample[0],profile_sha256=hashlib.sha256(page).hexdigest(),profile_bytes=len(page),profile_has_id_in_query=str(sample[0]) in sample[1],profile_valid_html=("<html" in page[:8000].decode("utf-8","replace").lower()),status="INDEX_AND_PROFILE_RETRIEVED")
 except Exception as err:result.update(error_type=type(err).__name__,error_message_code=str(err)[:100])
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"C01_result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("AB20_C01="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
