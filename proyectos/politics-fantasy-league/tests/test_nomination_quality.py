"""Real original BOE quarantine sidecar contract, without promoting rows to candidacies."""
import json
from politics_fantasy.nomination_quality import audit, QUARANTINE_DEFAULT


def test_27_quarantined_sections_are_retained_as_noncertified_observations():
    r=audit()
    assert r["ok"] is True,r
    assert r["quarantined_provinces"]==27
    assert r["observed_but_noncertified_list_headings"]==278
    assert r["accepted_list_records"]==263
    assert r["eligible_inferred_party_identities"]==0
    assert r["current_registered_parties"] is None
    assert r["eligible_real_people_for_fantasy"]==0
    assert r["national_population_coverage_pct"] is None


def write_mutated(tmp_path, action):
    raw=json.loads(QUARANTINE_DEFAULT.read_text(encoding="utf8"))
    action(raw)
    p=tmp_path/"quarantine.json"
    p.write_text(json.dumps(raw,ensure_ascii=False),encoding="utf8")
    return audit(quarantine_path=p)


def test_missing_quarantine_fails_closed(tmp_path):
    r=audit(quarantine_path=tmp_path/"not-found.json")
    assert r["ok"] is False
    assert r["error"]=="QUARANTINE_NOT_YET_CAPTURED"


def test_tampered_source_hash_is_not_accepted(tmp_path):
    r=write_mutated(tmp_path,lambda d:d.update({"source_sha256":"f"*64}))
    assert r["ok"] is False
    assert r["error"]=="QUARANTINE_PROVENANCE_UNSAFE"


def test_injected_hidden_party_membership_is_not_accepted(tmp_path):
    r=write_mutated(tmp_path,lambda d:d["quarantined_provinces"][0]["observed_labels_only"][0].update(
        {"metadata":{"party_member_guess":"false"}}))
    assert r["ok"] is False
    assert r["error"]=="PRIVATE_OR_LEGAL_IDENTITY_IN_SOURCE"


def test_quarantine_row_cannot_gain_certified_party_identity(tmp_path):
    r=write_mutated(tmp_path,lambda d:d["quarantined_provinces"][0]["observed_labels_only"][0].update(
        {"legal_party_registration_id":"invented"}))
    assert r["ok"] is False


def test_quarantine_count_tamper_is_rejected(tmp_path):
    r=write_mutated(tmp_path,lambda d:d.update({"n_observed_headings":279}))
    assert r["ok"] is False
    assert r["error"]=="QUARANTINE_COUNT_MISMATCH"
