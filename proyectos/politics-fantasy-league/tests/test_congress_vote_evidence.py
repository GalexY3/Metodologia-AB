"""C11 authoritative aggregate-only metadata, tamper and HTTP host guard."""
import json,http.client,threading
from http.server import ThreadingHTTPServer
from politics_fantasy.congress_vote_evidence import status,DEFAULT
from politics_fantasy.server import handler_factory

def test_local_read_only_aggregates():
    r=status()
    assert r["ok"] is True,r
    assert r["event_count"]==2
    assert [x["yes"] for x in r["events"]]==[33,170]
    assert all(x["individual_rows"]==350 for x in r["events"])
    assert r["first_public_at"] is None
    assert r["real_person_scoring"] is False
    assert "persons" not in r and "names" not in r

def test_tamper_rejected(tmp_path):
    root=json.loads(DEFAULT.read_text())
    for field,value in [("person_scoring_allowed",True),("first_public_at","2026-07-23T00:00:00Z")]:
        d=dict(root);d[field]=value
        p=tmp_path/"v.json";p.write_text(json.dumps(d))
        assert status(p)["ok"] is False
    d=json.loads(DEFAULT.read_text());d["votes"][0]["yes"]=340
    p.write_text(json.dumps(d));assert not status(p)["ok"]
    d=json.loads(DEFAULT.read_text());d["votes"][0]["person_name"]="invented"
    p.write_text(json.dumps(d));assert not status(p)["ok"]

def test_http_read_only_and_host_rejected(tmp_path):
    srv=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(tmp_path/"db.sqlite",None,None))
    t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
    try:
        host="127.0.0.1";port=srv.server_port
        conn=http.client.HTTPConnection(host,port,timeout=5)
        conn.request("GET","/api/verified-rollcalls")
        res=conn.getresponse();v=json.loads(res.read());conn.close()
        assert res.status==200 and v["ok"] and v["event_count"]==2
        conn=http.client.HTTPConnection(host,port,timeout=5)
        conn.request("GET","/api/verified-rollcalls",headers={"Host":"evil.example"})
        res=conn.getresponse();res.read();conn.close()
        assert res.status==403
    finally:srv.shutdown();srv.server_close();t.join(timeout=5)
