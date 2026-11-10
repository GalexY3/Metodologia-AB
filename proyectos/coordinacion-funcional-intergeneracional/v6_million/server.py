"""Local-only dashboard for real training data; never synthesizes metrics.

http://127.0.0.1:8765   (no internet-facing listening socket)
The Python worker is a separate, checkpointed subprocess controlled by JSON.
"""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
import subprocess,threading,webbrowser,json,os,sys,time,traceback

ROOT=Path(__file__).resolve().parent
RUN=ROOT/"runs"/"principal"
RUN.mkdir(parents=True,exist_ok=True)
WORKER=None
HOLDOUT=None
LOCK=threading.Lock()

def read_json(path,fallback):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError):return fallback
def write_json(path,data):
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data,indent=2),encoding="utf-8")
    os.replace(tmp,path)
def state():
    cfg=read_json(RUN/"config.json",{})
    last=read_json(RUN/"status.json",{})
    history=[]
    f=RUN/"history.jsonl"
    if f.exists():
        # At 1,000,000 episodes/batch48 every 20 updates: ~1040 rows.
        for line in f.read_text(encoding="utf-8").splitlines()[-3000:]:
            try:history.append(json.loads(line))
            except ValueError:pass
    worker=read_json(RUN/"control.json",{"pause":False,"stop":False})
    global WORKER,HOLDOUT
    return {"config":cfg,"status":last,"history":history,
            "replay":read_json(RUN/"replay.json",None),
            "control":worker,
            "holdout":read_json(RUN/"holdout"/"SUMMARY.json",None),
            "worker_running":(WORKER is not None and WORKER.poll() is None),
            "holdout_running":(HOLDOUT is not None and HOLDOUT.poll() is None)}
class App(BaseHTTPRequestHandler):
    def json(self,status,data):
        out=json.dumps(data,ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(out)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(out)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/state":
            self.json(200,state());return
        if path in ("/","/index.html"):
            buf=(ROOT/"index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(buf)))
            self.send_header("Cache-Control","no-store")
            self.end_headers()
            self.wfile.write(buf);return
        self.json(404,{"error":"Unknown route"})
    def do_POST(self):
        global WORKER,HOLDOUT
        path=urlparse(self.path).path
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n>8000:raise ValueError("Request too big")
            body=json.loads(self.rfile.read(n) or b"{}")
            if path=="/api/start":
                with LOCK:
                    if WORKER is not None and WORKER.poll() is None:
                        raise RuntimeError("The training worker is already running.")
                    status=read_json(RUN/"status.json",{})
                    if status.get("state") in ("training","paused"):
                        last=RUN/"status.json"
                        if last.exists() and time.time()-last.stat().st_mtime<120:
                            raise RuntimeError("Previous worker appears active; do not duplicate it.")
                    args=[sys.executable,"-u",str(ROOT/"trainer.py"),"--run","principal"]
                    # Configuration is fixed on first start; later use same settings to resume.
                    for key,flag,low,high in (
                      ("episodes","--episodes",1,50_000_000),
                      ("side","--side",4,64),
                      ("batch","--batch",9,512),
                      ("horizon","--horizon",1,256),
                      ("hidden","--hidden",8,256)):
                        if key in body:
                            value=int(body[key])
                            if not low<=value<=high:raise ValueError(f"Invalid {key}")
                            args.extend([flag,str(value)])
                    if "device" in body:
                        if body["device"] not in ("auto","cpu","cuda"):raise ValueError("Invalid device")
                        args.extend(["--device",body["device"]])
                    write_json(RUN/"control.json",{"pause":False,"stop":False})
                    log=(RUN/"worker.log").open("a",encoding="utf-8")
                    WORKER=subprocess.Popen(args,cwd=str(ROOT),stdout=log,stderr=subprocess.STDOUT,
                        creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
                    log.close()
                self.json(200,{"started":True,"pid":WORKER.pid,"args":args});return
            if path in ("/api/pause","/api/resume","/api/stop"):
                c=read_json(RUN/"control.json",{"pause":False,"stop":False})
                if path=="/api/pause":c["pause"]=True
                elif path=="/api/resume":c.update(pause=False,stop=False)
                else:c.update(pause=False,stop=True)
                write_json(RUN/"control.json",c)
                self.json(200,{"control":c});return
            if path=="/api/evaluate":
                with LOCK:
                    if HOLDOUT is not None and HOLDOUT.poll() is None:raise RuntimeError("Evaluation already active")
                    st=read_json(RUN/"status.json",{})
                    if st.get("state")!="completed":
                        raise RuntimeError("Sealed holdout is only available after training reaches its target.")
                    if (RUN/"holdout"/"SUMMARY.json").exists():
                        raise RuntimeError("Sealed holdout already evaluated. No repeated testing.")
                    log=(RUN/"holdout.log").open("a",encoding="utf-8")
                    HOLDOUT=subprocess.Popen([sys.executable,"-u",str(ROOT/"validate.py")],
                         cwd=str(ROOT),stdout=log,stderr=subprocess.STDOUT,
                         creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
                    log.close()
                self.json(200,{"started":True,"pid":HOLDOUT.pid});return
            self.json(404,{"error":"Unknown action"})
        except Exception as e:
            self.json(400,{"error":str(e)})
    def log_message(self,fmt,*args):
        sys.stdout.write(f"[panel] {self.address_string()} {fmt%args}\n")
if __name__=="__main__":
    port=int(os.environ.get("MARL_PORT",8765))
    server=ThreadingHTTPServer(("127.0.0.1",port),App)
    print(f"VISOR V6: http://127.0.0.1:{port}",flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    server.server_close()
