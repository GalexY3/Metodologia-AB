"""No party-affiliation or fantasy scores inferred by the source-pinned API."""
import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from politics_fantasy.official_appointments import status,DEFAULT
from politics_fantasy.server import handler_factory

def test_exact_historical_22_source_pinned():
    s=status()
    assert s["ok"] is True,s
    assert s["n_historical_nominations"]==22
    assert s["eligible_current_officeholders"] is None
    assert s["registered_party_memberships_verified"]==0
    assert s["real_scoring_enabled"] is False
    assert all(x["fantasy_points"] is None and
               x["registered_party_membership"] is None and
               x["current_mandate_status"]=="UNKNOWN_NOT_RECONCILED"
               for x in s["appointments"])

def mutate(tmp_path,change):
    d=json.loads(DEFAULT.read_text(encoding="utf8"))
    change(d)
    p=tmp_path/"bad.json"
    p.write_text(json.dumps(d,ensure_ascii=False),encoding="utf8")
    return status(p)

def test_wrong_digest_rejected(tmp_path):
    d=mutate(tmp_path,lambda d:d.update(source_pdf_sha256="f"*64))
    assert not d["ok"] and d["appointments"]==[]

def test_invented_party_and_score_rejected(tmp_path):
    d=mutate(tmp_path,lambda d:d["rows"][0].update(legal_party_registration_id="RPP:guessed"))
    assert not d["ok"]
    d=mutate(tmp_path,lambda d:d["rows"][1].update(fantasy_points=10))
    assert not d["ok"]
    d=mutate(tmp_path,lambda d:d["rows"][2].update(end_of_tenure="2026-10-06"))
    assert not d["ok"]

def test_changed_2023_role_rejected_by_pinned_derivative_digest(tmp_path):
    d=mutate(tmp_path,lambda d:d["rows"][0].update(office="Ministerio de Invención"))
    assert d["ok"] is False
    assert d["error"]=="DERIVATIVE_SNAPSHOT_UNPINNED"

def test_local_http_endpoint_never_asserts_current_office(tmp_path):
    httpd=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(tmp_path/"db.sqlite",None,None))
    thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start()
    try:
        conn=http.client.HTTPConnection("127.0.0.1",httpd.server_port,timeout=8)
        conn.request("GET","/api/official-appointments")
        response=conn.getresponse()
        data=json.loads(response.read())
        conn.close()
        assert response.status==200 and data["ok"]
        assert len(data["appointments"])==22
        assert data["real_scoring_enabled"] is False
        assert all(p["fantasy_points"] is None for p in data["appointments"])
        conn=http.client.HTTPConnection("127.0.0.1",httpd.server_port,timeout=8)
        conn.request("GET","/api/official-appointments",headers={"Host":"attacker.invalid"})
        bad=conn.getresponse();bad.read();conn.close()
        assert bad.status==403
    finally:
        httpd.shutdown();httpd.server_close();thread.join(timeout=8)
