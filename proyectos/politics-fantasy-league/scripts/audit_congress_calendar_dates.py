#!/usr/bin/env python3
"""C16 discover date selector options from Congress original HTML without person records."""
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urlparse
from pathlib import Path
from collections import Counter
import re,json,hashlib
URL="https://www.congreso.es/es/opendata/votaciones?targetDate=30%2F09%2F2026&targetLegislatura=XV"
P=Path("/tmp/pf-congress-probe")
PAT=re.compile(r"(?:0?[1-9]|[12][0-9]|3[01])/(?:0?[1-9]|1[012])/20(?:2[3456])")
class Parser(HTMLParser):
 def __init__(self):
    super().__init__();self.options=[];self.cur=None
 def handle_starttag(self,tag,attrs):
    if tag=="option":self.cur={"attrs":dict(attrs),"text":""}
 def handle_data(self,txt):
    if self.cur is not None:self.cur["text"]+=txt
 def handle_endtag(self,tag):
    if tag=="option" and self.cur is not None:
      self.options.append(self.cur);self.cur=None
def main():
 result={"cycle":"C16","date_catalogue":URL,"status":"STOP_R5","available_dates":[]}
 try:
    with urlopen(Request(URL,headers={"User-Agent":"PFL-AB32-Research/0.1"}),timeout=23) as res:
      if urlparse(res.geturl()).hostname!="www.congreso.es" or res.status!=200:raise ValueError("SOURCE_HOST")
      data=res.read(3_000_001)
    if len(data)>3_000_000:raise ValueError("OVERSIZE")
    parser=Parser();parser.feed(data.decode("utf-8","replace"))
    vals=set()
    for q in parser.options:
        txt=q["text"]+" "+" ".join(q["attrs"].values())
        for m in PAT.finditer(txt):vals.add(m.group())
    vals.update(m.group() for m in PAT.finditer(data.decode("utf-8","replace")))
    # Date set may include references outside a selector; flag not independently certified.
    result.update(status="CALENDAR_DATES_DISCOVERED" if len(vals)>=12 else "INSUFFICIENT_DATE_CHOICES",dates_count=len(vals),option_count=len(parser.options),available_dates=sorted(vals),html_sha256=hashlib.sha256(data).hexdigest(),warning="dates may include navigation/media metadata; individual date must independently return a valid official session JSON")
 except Exception as e:result.update(error_type=type(e).__name__,http_code=getattr(e,"code",None))
 P.mkdir(parents=True,exist_ok=True)
 (P/"calendar_dates_inventory.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("C16_DATES="+json.dumps({k:result.get(k) for k in ("status","dates_count","option_count","html_sha256")},ensure_ascii=False))
 print("C16_DATE_SAMPLE="+json.dumps(result["available_dates"][:10]))
if __name__=="__main__":main()
