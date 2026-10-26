#!/usr/bin/env python3
"""C13 institutional chronology: independently fetch official BOE 2026 decree XML/HTML."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlparse
import hashlib,json,re,html
DEST=Path("/tmp/pf-congress-probe")
URL="https://www.boe.es/buscar/doc.php?id=BOE-A-2026-20742"
def main():
    report={"cycle":"C13","official_source":URL,"status":"STOP_R5_UNVERIFIED"}
    try:
        with urlopen(Request(URL,headers={"User-Agent":"PFL-AB-Research/0.1"}),timeout=24) as res:
            loc=urlparse(res.geturl())
            if loc.scheme!="https" or loc.hostname not in ("www.boe.es","boe.es") or res.status!=200:
                raise ValueError("UNTRUSTED_HOST")
            blob=res.read(1_600_001)
        if len(blob)>1_600_000:raise ValueError("BOE_OVERSIZE")
        raw=html.unescape(re.sub(r"<[^>]*>"," ",blob.decode("utf-8","replace")))
        normalized=" ".join(raw.split()).casefold()
        clauses={
            "title":"real decreto 806/2026" in normalized,
            "reference":"boe-a-2026-20742" in normalized,
            "congress_senate_dissolved":("quedan disueltos el congreso de los diputados y el senado" in normalized),
            "election_nov29":("29 de noviembre de 2026" in normalized),
            "publication_oct6":("6 de octubre de 2026" in normalized)
        }
        if not all(clauses.values()):raise ValueError("REQUIRED_OFFICIAL_CLAUSE_ABSENT_"+",".join(k for k,v in clauses.items() if not v))
        DEST.mkdir(parents=True,exist_ok=True)
        (DEST/"boe_dissolution_original.html").write_bytes(blob)
        report.update(status="ORIGINAL_CLAUSES_VERIFIED",source_sha256=hashlib.sha256(blob).hexdigest(),source_bytes=len(blob),clause_checks=clauses,official_publication_calendar_date="2026-10-06",dissolution_date="2026-10-06",new_election_date="2026-11-29",note="legal dissolution chronology, not timestamp of congressional vote JSON")
    except Exception as exc:report.update(error_type=type(exc).__name__,http_code=getattr(exc,"code",None))
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/"boe_dissolution_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("C13_BOE="+json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
