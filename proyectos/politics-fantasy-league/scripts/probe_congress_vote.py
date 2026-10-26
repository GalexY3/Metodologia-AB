#!/usr/bin/env python3
"""C04: probe exactly one official roll-call JSON, no record values logged."""
from pathlib import Path
import json,hashlib
from urllib.request import urlopen, Request
from urllib.parse import urlparse
URL="https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion193/20260723/Votacion001/VOT_20260723211929.json"
OUT=Path("/tmp/pf-congress-probe")
def describe(x,depth=0):
    if depth>=5:return {"type":type(x).__name__}
    if isinstance(x,dict):
        return {"type":"object","length":len(x),"fields":{k:describe(v,depth+1) for k,v in list(x.items())[:25]}}
    if isinstance(x,list):
        return {"type":"array","length":len(x),"item_structure":describe(x[0],depth+1) if x else None}
    return {"type":type(x).__name__}
def main():
    result={"cycle":"C04","url":URL,"status":"STOP_R5","first_public_at":None}
    try:
        with urlopen(Request(URL,headers={"User-Agent":"PFL-AB32-Research/0.1"}),timeout=25) as response:
            f=urlparse(response.geturl())
            if f.scheme!="https" or f.hostname!="www.congreso.es" or response.status!=200:
                raise ValueError("UNVERIFIED_HOST_OR_STATUS")
            raw=response.read(5_000_001)
        if len(raw)>5_000_000:raise ValueError("OVERSIZE")
        obj=json.loads(raw)
        result.update(status="RAW_CAPTURED",bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),shape=describe(obj))
        (OUT/"vote_original.json").write_bytes(raw)
    except Exception as exc:
        result.update(error_type=type(exc).__name__,http_code=getattr(exc,"code",None))
    (OUT/"vote_shape.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C04_VOTE_SHAPE="+json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
