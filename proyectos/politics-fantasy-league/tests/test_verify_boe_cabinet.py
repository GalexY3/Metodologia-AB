"""Unit adversarial tests; official original checked separately in native CI."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
import pytest

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("cabinet_verify",HERE/"scripts/verify_boe_cabinet.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
original=json.loads(mod.SNAPSHOT.read_text(encoding="utf8"))
rows=[(row["office"].removeprefix("Ministerio de "),row["name"]) for row in original["rows"]]

def test_bounded_transcription_adjudicates_with_synthetic_extractor():
    with patch.object(mod,"extract_appointments",return_value=rows):
        x=mod.replay(b"synthetic test only",original)
    assert x["matched"]==22 and not x["scoring_enabled"]
    assert not x["party_legal_id_certified"]
    assert not x["current_mandate_certified"]

@pytest.mark.parametrize("field,value",[
    ("name","Name that is not in source"),
    ("legal_party_registration_id","RPP:invented"),
    ("end_of_tenure","2026-01-01"),
    ("eligible_for_real_scoring",True),
    ("extra_sensitive_info",{"health":"invented"})
])
def test_unverified_inference_or_corruption_is_rejected(field,value):
    changed=json.loads(json.dumps(original))
    changed["rows"][0][field]=value
    with patch.object(mod,"extract_appointments",return_value=rows):
        with pytest.raises(ValueError,match="PUBLIC_DOCUMENT_MISMATCH"):
            mod.replay(b"synthetic test only",changed)

def test_missing_actor_fails_exact_count():
    with patch.object(mod,"extract_appointments",return_value=rows[:-1]):
        with pytest.raises(ValueError,match="NOT_22"):
            mod.replay(b"synthetic test only",original)

def test_wrong_institution_disallowed():
    changed=json.loads(json.dumps(original))
    changed["source_pdf"]="https://example.test/boe.pdf"
    with patch.object(mod,"extract_appointments",return_value=rows):
        with pytest.raises(ValueError,match="UNSAFE_SOURCE"):
            mod.replay(b"synthetic test only",changed)
