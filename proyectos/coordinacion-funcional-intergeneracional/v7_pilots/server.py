"""V7 local dashboard. Read-only; never starts training or opens sealed tests."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, os, re
ROOT=Path(__file__).resolve().parent
RUNS=ROOT/"runs"
def read_json(path):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError):return None
def state():
    out={}
    if RUNS.exists():
        for d in sorted(RUNS.iterdir()):
            if not d.is_dir() or not re.fullmatch(r"[A-Za-z0-9_-]+",d.name):
                continue
            history=[]
            h=d/"history.jsonl"
            if h.exists():
                for line in h.read_text(encoding="utf-8").splitlines()[-1000:]:
                    try:history.append(json.loads(line))
                    except ValueError:continue
            out[d.name]=dict(config=read_json(d/"config.json"),
                status=read_json(d/"status.json"),history=history,
                replay=read_json(d/"replay.json"))
    return out
class App(BaseHTTPRequestHandler):
    def do_GET(self):
        route=self.path.split("?")[0]
        if route=="/api/state":
            raw=json.dumps(state(),ensure_ascii=False).encode("utf-8")
            ctype="application/json; charset=utf-8"
        elif route in ("/","/index.html"):
            raw=(ROOT/"index.html").read_bytes()
            ctype="text/html; charset=utf-8"
        else:
            self.send_error(404);return
        self.send_response(200)
        self.send_header("Content-Type",ctype)
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(raw)
    def log_message(self,format,*args):
        pass
if __name__=="__main__":
    port=int(os.environ.get("MARL_V7_PORT","8766"))
    print(f"V7 panel (read only): http://127.0.0.1:{port}",flush=True)
    ThreadingHTTPServer(("127.0.0.1",port),App).serve_forever()
