"""Strict, read-only local historical appointment index; never a live cabinet list.

Document provenance was verified by original PDF replay in CI 40342982881.
This local reader checks the derivative snapshot, not an original in every GET.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT=Path(__file__).resolve().parents[2]
DEFAULT=PROJECT/"data/observatory/boe_2023_minister_appointments_reviewed.json"
PDF_URL="https://www.boe.es/boe/dias/2023/11/21/pdfs/BOE-A-2023-23543.pdf"
PDF_SHA256="16f05bba24508af229870b68dbfb72ba258e62416713a8cfe5c49c70ba792efe"
ROW_KEYS=frozenset(("document_local_appointment_id","name","office",
                    "date_of_nomination_decree","date_of_official_publication",
                    "end_of_tenure","legal_party_registration_id",
                    "eligible_for_real_scoring"))
SAFE_NAME=re.compile(r"^[\w\sÀ-ÿ'’\-]+$",re.UNICODE)
BASE={
    "ok":False,"source_class":"HISTORICAL_DOCUMENT_NOT_CURRENT_ROSTER",
    "source_id":"BOE-A-2023-23543",
    "real_scoring_enabled":False,"eligible_current_officeholders":None,
    "registered_party_memberships_verified":0,"appointments":[]
}

def status(path:Path|None=None)->dict:
    p=Path(path) if path is not None else DEFAULT
    try:
        if not p.is_file() or p.stat().st_size>20_000:
            return {**BASE,"error":"SOURCE_MISSING_OR_OVERSIZED"}
        d=json.loads(p.read_text(encoding="utf8"))
        if (d.get("source_id")!="BOE-A-2023-23543" or
            d.get("source_pdf")!=PDF_URL or
            d.get("source_pdf_sha256")!=PDF_SHA256 or
            d.get("dataset_class")!="OFFICIAL_APPOINTMENTS_2023_PINNED_ORIGINAL_BOUNDED" or
            d.get("source_authentication_level")!="CI_ORIGINAL_SHA256_REPLAY_40342982881" or
            d.get("n_expected")!=22 or
            d.get("legal_instrument")!="Real Decreto 835/2023" or
            d.get("signed_date")!="2023-11-20" or
            d.get("official_publication_date")!="2023-11-21" or
            d.get("first_public_at") is not None or
            d.get("eligible_for_real_scoring") is not False or
            d.get("reconciled_legal_party_ids")!=0 or
            d.get("party_memberships_inferred")!=0 or
            d.get("tenure_end_dates_validated")!=0):
            return {**BASE,"error":"SOURCE_NOT_PINNED_OR_UNSAFE"}
        rows=d["rows"]
        if not isinstance(rows,list) or len(rows)!=22:
            return {**BASE,"error":"ROW_COUNT_CHANGED"}
        out=[]
        for n,row in enumerate(rows,1):
            if (not isinstance(row,dict) or frozenset(row)!=ROW_KEYS or
                row.get("document_local_appointment_id")!=f"BOE-A-2023-23543:APPOINTMENT:{n:02d}" or
                not isinstance(row.get("name"),str) or
                not 4<=len(row["name"])<=120 or not SAFE_NAME.fullmatch(row["name"]) or
                not isinstance(row.get("office"),str) or
                not row["office"].startswith("Ministerio de ") or
                not 14<=len(row["office"])<=150 or
                row.get("date_of_nomination_decree")!="2023-11-20" or
                row.get("date_of_official_publication")!="2023-11-21" or
                row.get("end_of_tenure") is not None or
                row.get("legal_party_registration_id") is not None or
                row.get("eligible_for_real_scoring") is not False):
                return {**BASE,"error":f"ROW_UNSAFE_{n:02d}"}
            out.append({
                "appointment_document_id":row["document_local_appointment_id"],
                "name_in_original":row["name"],
                "portfolio_in_2023_document":row["office"],
                "nomination_document_signed":"2023-11-20",
                "officially_published":"2023-11-21",
                "current_mandate_status":"UNKNOWN_NOT_RECONCILED",
                "registered_party_membership":None,
                "fantasy_points":None,
            })
        if len({r["name_in_original"] for r in out})!=22:
            return {**BASE,"error":"DUPLICATE_DOCUMENT_LABEL"}
        return {**BASE,"ok":True,"n_historical_nominations":22,
                "source_pdf":PDF_URL,"source_pdf_sha256":PDF_SHA256,
                "source_replay_ci":"https://github.com/GalexY3/Metodologia-AB/actions/runs/40342982881",
                "appointments":out,
                "warning":"No se acreditan permanencia en 2026, afiliaciones RPP, actualidad, ni puntos. Cotejo de 22 nombramientos publicados en noviembre de 2023."}
    except (OSError,ValueError,TypeError,KeyError,OverflowError,AttributeError):
        return {**BASE,"error":"MALFORMED_OR_UNAVAILABLE_SOURCE"}
