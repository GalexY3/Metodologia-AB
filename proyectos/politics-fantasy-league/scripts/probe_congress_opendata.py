#!/usr/bin/env python3
"""Strictly bounded official Congress open-data catalogue probe.

No names, political affiliations, or raw records are emitted to logs or
version control. Raw downloads remain in a short-lived private CI artifact.
HTTPS certificate validation remains enabled.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

CATALOGUE="https://www.congreso.es/es/opendata/diputados"
ROOT=Path(os.environ.get("PF_CONGRESS_PROBE_DIR","/tmp/pf-congress-probe"))
MAX_HTML=3_000_000
MAX_BYTES=12_000_000

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows=[]
        self.href=None
        self.label=[]
    def handle_starttag(self, tag, attrs):
        if tag=="a":
            self.href=dict(attrs).get("href")
            self.label=[]
    def handle_data(self,data):
        if self.href is not None:self.label.append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self.href is not None:
            self.rows.append({"label":" ".join("".join(self.label).split())[:60],"url":urljoin(CATALOGUE,self.href)})
            self.href=None
            self.label=[]

def transfer(url,maxbytes,opener=urlopen):
    request=Request(url,headers={"User-Agent":"PFL-SourceResearch/0.1","Accept":"text/html,application/json,text/csv,application/xml,*/*"})
    with opener(request,timeout=24) as response:
        final=response.geturl()
        p=urlparse(final)
        if p.scheme!="https" or p.hostname!="www.congreso.es":
            raise ValueError("OFFICIAL_HOST_REDIRECT_REJECTED")
        if response.status!=200:raise ValueError("SOURCE_STATUS_NOT_200")
        raw=response.read(maxbytes+1)
        if len(raw)>maxbytes:raise ValueError("SOURCE_TOO_LARGE")
        if len(raw)<20:raise ValueError("SOURCE_TOO_SMALL")
        return raw,final,response.headers.get("Content-Type","")

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    result={"cycle":"BR12_C01","catalogue":CATALOGUE,"catalogue_ok":False,"rows":[],"status":"STOP_R5","note":"no roster/entity claim; downloads remain private"}
    try:
        data,final,mime=transfer(CATALOGUE,MAX_HTML)
        if b"Datos abiertos" not in data and b"Opendata" not in data:
            raise ValueError("UNEXPECTED_CATALOGUE_HTML")
        parser=Links()
        parser.feed(data.decode("utf-8","replace"))
        links=[x for x in parser.rows if "/opendata/diputados/" in x["url"] and urlparse(x["url"]).hostname=="www.congreso.es"]
        result["catalogue_ok"]=True
        result["catalogue_sha256"]=hashlib.sha256(data).hexdigest()
        result["catalogue_link_count"]=len(links)
        result["catalogue_final"]=final
        result["catalogue_content_type"]=mime
        for x in links[:8]:
            url=x["url"]
            row={"format":url.rsplit(".",1)[-1].lower(),"source_url":url,"label":x["label"],"retrieved":False}
            try:
                payload,got,ct=transfer(url,MAX_BYTES)
                kind=row["format"]
                if kind=="json":
                    parsed=json.loads(payload)
                    if not isinstance(parsed,(dict,list)):raise ValueError("BAD_JSON_ROOT")
                    row["structure"]="array" if isinstance(parsed,list) else "object"
                    row["row_count"]=len(parsed)
                    row["field_names"]=sorted(parsed[0].keys())[:20] if isinstance(parsed,list) and parsed and isinstance(parsed[0],dict) else (sorted(parsed.keys())[:20] if isinstance(parsed,dict) else [])
                elif kind=="xml":
                    if not payload.lstrip().startswith(b"<?xml"):raise ValueError("NOT_XML")
                    row["structure"]="xml_magic"
                elif kind=="csv":
                    # Deliberately no real-person data exposure
                    row["structure"]="csv_text"
                    row["row_count_lower_bound"]=max(0,payload.count(b"\n")-1)
                else:raise ValueError("UNSUPPORTED_EXTENSION")
                target=ROOT/("official_"+str(len(result["rows"]))+"."+kind)
                target.write_bytes(payload)
                row.update(retrieved=True,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest(),mime=ct)
            except (HTTPError,URLError,TimeoutError,OSError,ValueError,json.JSONDecodeError) as error:
                row.update(error_type=type(error).__name__,http_code=getattr(error,"code",None))
            result["rows"].append(row)
        result["status"]="CAPTURED_OR_DISCOVERED" if any(x["retrieved"] for x in result["rows"]) else "CATALOGUE_ONLY_STOP_R5"
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as error:
        result.update(error_type=type(error).__name__,http_code=getattr(error,"code",None))
    (ROOT/"probe_manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("CONGRESS_PROBE_SUMMARY="+json.dumps({k:result[k] for k in ("cycle","status","catalogue_ok")}))
    for x in result["rows"]:
        print("CONGRESS_PROBE_FILE="+json.dumps({k:x.get(k) for k in ("format","retrieved","bytes","sha256","http_code","error_type","row_count","structure")}))
    return result
if __name__=="__main__":main()
