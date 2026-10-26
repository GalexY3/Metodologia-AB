"""Conservative information-availability contract for day-granularity sources.

The date on BOE is the official publication day, not a timestamp proving
what was known at a particular clock time. No personal scoring output.
"""
from __future__ import annotations

from datetime import date

SOURCE_DOCUMENT="BOE-A-2023-23543"
PUBLICATION_DAY=date(2023,11,21)
SIGNATURE_DAY=date(2023,11,20)

def publication_visibility(as_of: str)->dict:
    if not isinstance(as_of,str) or len(as_of)!=10:
        raise ValueError("STRICT_DATE_YYYY_MM_DD_REQUIRED")
    try:
        x=date.fromisoformat(as_of)
    except ValueError as exc:
        raise ValueError("INVALID_AS_OF_DATE") from exc
    if x.isoformat()!=as_of:
        raise ValueError("NON_CANONICAL_DATE")
    if x < PUBLICATION_DAY:
        cls="NOT_OFFICIALLY_PUBLISHED_BY_DATE"
        known=False
    elif x==PUBLICATION_DAY:
        cls="INTRADAY_UNKNOWN_NO_EXACT_FIRST_PUBLIC_AT"
        known=False
    else:
        cls="DOCUMENT_PUBLISHED_ON_PRIOR_DAY"
        known=True
    return {"document":SOURCE_DOCUMENT,"as_of_date":as_of,
            "signed_on":SIGNATURE_DAY.isoformat(),
            "official_publication_day":PUBLICATION_DAY.isoformat(),
            "first_public_at":None,
            "classification":cls,
            "safe_to_use_historical_document_for_day_level_study":known,
            "safe_to_score_person":False,
            "date_of_nomination_not_information_timestamp":True}
