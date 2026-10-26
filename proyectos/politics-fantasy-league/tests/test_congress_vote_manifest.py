"""C10 strict negative tests, never grading politicians."""
import pytest
from politics_fantasy.congress_vote_dates import normalized_vote_date

def test_publication_not_event_date():
    from pathlib import Path
    import json
    p=Path(__file__).resolve().parents[1]/"data/observatory/congress_20260723_vote_aggregate_verified.json"
    j=json.loads(p.read_text())
    assert j["first_public_at"] is None
    assert j["read_only_aggregate_only"] is True
    assert j["person_scoring_allowed"] is False
    for v in j["votes"]:
        assert sum(v[k] for k in ("yes","no","abstain","no_vote"))==v["individual_rows"]
        assert sum(v[k] for k in ("yes","no","abstain"))==v["present"]
        assert v["event_date"]=="2026-07-23"
        assert len(v["source_sha256"])==64

def test_authentic_sha_hex_format():
    from pathlib import Path
    import json
    v=json.loads((Path(__file__).resolve().parents[1]/"data/observatory/congress_20260723_vote_aggregate_verified.json").read_text())["votes"]
    assert all(all(c in "0123456789abcdef" for c in x["source_sha256"]) for x in v)
