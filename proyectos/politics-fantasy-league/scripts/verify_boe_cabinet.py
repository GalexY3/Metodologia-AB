"""Reextract original 2023 BOE cabinet appointment PDF and verify 22 public roles.

This certifies only a signed-decree NOMINATION as a 2023 documentary event.
It does not infer a minister's full 2023-2026 tenure or political party.
"""
import hashlib
import json
from pathlib import Path
import re
import ssl
import subprocess
import tempfile
from urllib.request import Request, urlopen

URL = "https://www.boe.es/boe/dias/2023/11/21/pdfs/BOE-A-2023-23543.pdf"
HERE = Path(__file__).resolve().parents[1]
SNAPSHOT = HERE / "data/observatory/boe_2023_minister_appointments_reviewed.json"

def extract_appointments(pdf_bytes: bytes) -> list[tuple[str,str]]:
    if not pdf_bytes.startswith(b"%PDF-") or len(pdf_bytes)<5000:
        raise ValueError("ORIGINAL_PDF_MAGIC_OR_SIZE")
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)/"official.pdf"
        p.write_bytes(pdf_bytes)
        process=subprocess.run(["pdftotext","-layout",str(p),"-"],
                               capture_output=True,text=True,check=True)
    txt=re.sub(r"\s+"," ",process.stdout).strip()
    if "Real Decreto 835/2023" not in txt or "BOE-A-2023-23543" not in txt:
        raise ValueError("WRONG_OFFICIAL_DOCUMENT")
    if "vengo en nombrar:" not in txt or "Dado en Madrid" not in txt:
        raise ValueError("UNRECOGNIZED_BODY")
    block=txt.split("vengo en nombrar:",1)[1].split("Dado en Madrid",1)[0]
    sentences=[p.strip() for p in block.split(".") if p.strip()]
    rows=[]
    for sentence in sentences:
        m=re.fullmatch(r"Ministr[oa] (?:de|del|para) (.+?) a (?:don|doña) (.+)",sentence)
        if not m:
            raise ValueError(f"UNMATCHED_APPOINTMENT_SENTENCE: {sentence[:90]}")
        portfolio,name=m.groups()
        if not all(name.split()) or not portfolio.strip():
            raise ValueError("EMPTY_NOMINATION")
        rows.append((portfolio,name))
    return rows

def replay(pdf_bytes: bytes, snapshot: dict) -> dict:
    if (snapshot.get("source_id")!="BOE-A-2023-23543" or
        snapshot.get("source_pdf")!=URL or
        snapshot.get("date_of_official_publication") is not None or
        snapshot.get("eligible_for_real_scoring") is not False or
        snapshot.get("reconciled_legal_party_ids")!=0 or
        snapshot.get("party_memberships_inferred")!=0):
        raise ValueError("UNSAFE_SOURCE_OR_SCOPE")
    real=extract_appointments(pdf_bytes)
    stored=snapshot["rows"]
    if len(real)!=22 or len(stored)!=22 or snapshot["n_expected"]!=22:
        raise ValueError("NOT_22_APPOINTMENTS")
    for n,((portfolio,name),row) in enumerate(zip(real,stored),1):
        expected_id=f"BOE-A-2023-23543:APPOINTMENT:{n:02d}"
        if (row.get("document_local_appointment_id")!=expected_id or
            row.get("name")!=name or row.get("office")!="Ministerio de "+portfolio or
            row.get("date_of_nomination_decree")!="2023-11-20" or
            row.get("date_of_official_publication")!="2023-11-21" or
            row.get("end_of_tenure") is not None or
            row.get("legal_party_registration_id") is not None or
            row.get("eligible_for_real_scoring") is not False or
            set(row)!={"document_local_appointment_id","name","office",
                        "date_of_nomination_decree","date_of_official_publication",
                        "end_of_tenure","legal_party_registration_id",
                        "eligible_for_real_scoring"}):
            raise ValueError(f"PUBLIC_DOCUMENT_MISMATCH_ROW_{n:02d}")
    return {"matched":22,"document":"BOE-A-2023-23543",
            "source_bytes":len(pdf_bytes),"sha256":hashlib.sha256(pdf_bytes).hexdigest(),
            "scope":"ORIGINAL_2023_MINISTER_NOMINATIONS_ONLY",
            "current_mandate_certified":False,"party_legal_id_certified":False,
            "scoring_enabled":False}

def main():
    request=Request(URL,headers={"User-Agent":"PF-DocumentaryResearch/0.1"})
    with urlopen(request,timeout=35,context=ssl.create_default_context()) as resp:
        if resp.status != 200:
            raise ValueError(f"HTTP_{resp.status}")
        blob=resp.read(300_000)
    snapshot=json.loads(SNAPSHOT.read_text(encoding="utf8"))
    result=replay(blob,snapshot)
    print("MATCH_BOE_CABINET_22",json.dumps(result,ensure_ascii=False))
    Path("/tmp/pf-boe-cabinet-audit.json").write_text(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
