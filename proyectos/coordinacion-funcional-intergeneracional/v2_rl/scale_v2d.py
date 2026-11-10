"""V2-D preregistered scale challenge (N240,480,960), no retraining.

Three independent training seeds, global-only vs trainer-side difference credit,
random always-on negotiation and stay. 90 ticks, fixed independent world seeds.
"""
from pathlib import Path
import json,time,statistics,hashlib
import torch
from environment import VectorSociety,Configuration
from agents import LocalActor

torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"scale_v2d";OUT.mkdir(exist_ok=True)
COHORTS=(221,222,223)
SIZES=((12,20,24),(20,24,16),(30,32,8))
KS=(2,3,4)
MODES=("credit2","credit0","random","stay")

def chk_path(seed,mode):
 w=2 if mode=="credit2" else 0
 return ROOT/"runs"/f"credit{w:g}_seed{seed}_u180"/"checkpoint_0180.pt"

def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
lock={"protocol":"PREREG_SCALE_STRATEGY_AUDIT.md",
      "code_sha":filehash(ROOT/"scale_v2d.py"),
      "environment_sha":filehash(ROOT/"environment.py"),
      "agents_sha":filehash(ROOT/"agents.py"),
      "checkpoints":{f"{s}_{m}":filehash(chk_path(s,m))
                     for s in COHORTS for m in ("credit0","credit2")},
      "n_sizes":[r*c for r,c,_ in SIZES],
      "training_seeds":list(COHORTS),"k":list(KS),"modes":list(MODES),
      "horizon":90,
      "world_seed":"1010000+100000*N+1000*trainseed+100*k",
      "batches":{str(r*c):b for r,c,b in SIZES},
      "actor_training_updates":0}
lockfile=OUT/"TEST_LOCK.json"
if lockfile.exists():
 if json.loads(lockfile.read_text(encoding="utf-8"))!=lock:
  raise RuntimeError("Model/config code changed after test lock")
else:lockfile.write_text(json.dumps(lock,ensure_ascii=False,indent=2),encoding="utf-8")
models={}
for seed in COHORTS:
 for mode in ("credit0","credit2"):
  cp=torch.load(chk_path(seed,mode),map_location="cpu",weights_only=False)
  a=LocalActor(hidden=cp["config"]["hidden"])
  a.load_state_dict(cp["actor"]);a.eval()
  models[(seed,mode)]=a

@torch.no_grad()
def run(rows,cols,batch,k,seed,mode,training_seed):
 env=VectorSociety(Configuration(rows=rows,cols=cols,batch=batch,
      seed=seed,randomize_majority=True))
 env.reset(k=k)
 torch.manual_seed(seed+4*len(mode))
 tv=[env.tv().clone()]
 churn=[]
 sent=[]
 accepted=[]
 mx=0
 a=models[(training_seed,mode)] if mode in ("credit0","credit2") else models[(training_seed,"credit2")]
 for _ in range(90):
  obs=env.observe()
  if mode=="stay":
   s=torch.zeros((batch,env.n),dtype=torch.long)
   incoming,req,payload=env.deliveries(obs,s)
   q=torch.zeros_like(s)
  else:
   s,_,_,z=a.sample_sender(obs,env.send_mask(),random_baseline=mode=="random")
   incoming,req,payload=env.deliveries(obs,s)
   q,_,_=a.sample_receiver(z,payload,incoming,req,random_baseline=mode=="random")
  res=env.step(s,q,incoming,req)
  tv.append(res["tv"].clone())
  churn.append(res["churn"].clone())
  sent.append(res["messages"].clone())
  accepted.append(res["acceptances"].clone())
  mx=max(mx,int(res["requests_received"].max()))
 t=torch.stack(tv)
 c=torch.stack(churn)
 stable=((t[-10:]<=.06)&(c[-10:]<=.05)).all(0)
 return {"n":rows*cols,"k":k,"train_seed":training_seed,"world_seed":seed,
   "mode":mode,"n_worlds":batch,"steps":90,
   "mean_initial_tv":float(t[0].mean()),
   "mean_final_tv":float(t[-1].mean()),
   "mean_tail_tv":float(t[-10:].mean()),
   "mean_last10_churn":float(c[-10:].mean()),
   "stable_count":int(stable.sum()),
   "stable_fraction":float(stable.float().mean()),
   "exact_final_count":int((t[-1].abs()<1e-6).sum()),
   "ever_near_count":int((t<=.06).any(0).sum()),
   "final_near_count":int((t[-1]<=.06).sum()),
   "mean_sends":float(torch.stack(sent).mean()),
   "mean_accepts":float(torch.stack(accepted).mean()),
   "max_incoming":mx,"final_tv_each_world":t[-1].tolist(),
   "stable_each_world":stable.tolist(),
   "tail_tv_each_world":t[-10:].mean(0).tolist(),
   "tv_curve_mean":[float(v) for v in t.mean(1)]}

def main():
 t0=time.perf_counter()
 results=[]
 for rows,cols,batch in SIZES:
  n=rows*cols
  for cohort in COHORTS:
   for k in KS:
    seed=1010000+100000*n+1000*cohort+100*k
    for mode in MODES:
     path=OUT/f"N{n}_seed{cohort}_k{k}_{mode}.json"
     if path.exists():raise RuntimeError("Do not overwrite preregistered observation "+str(path))
     r=run(rows,cols,batch,k,seed,mode,cohort)
     path.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
     results.append({u:v for u,v in r.items() if u not in
      ("final_tv_each_world","stable_each_world","tail_tv_each_world","tv_curve_mean")})
     print("SCALE",n,cohort,k,mode,"TV",round(r["mean_final_tv"],4),
       "stable",r["stable_count"],"/",batch,
       "exact",r["exact_final_count"],"churn",round(r["mean_last10_churn"],4),
       "elapsed",round(time.perf_counter()-t0,1),flush=True)
 out=OUT/"SUMMARY.json"
 if out.exists():raise RuntimeError("Summary exists")
 out.write_text(json.dumps({"lock":lock,"total_case_batches":len(results),
      "total_test_societies":sum(z["n_worlds"] for z in results),
      "results":results,
      "status":"new size transfer with frozen weights; each training cohort counted separately",
      "limitations":["tests are within one simulator family",
         "number of societies nested under three model seeds",
         "random always-on requests are an intentionally unstable control",
         "credit2 uses centralized counterfactual team reward during learning"]},
         ensure_ascii=False,indent=2),encoding="utf-8")
 print("SCALE_FINISHED",len(results),"case batches",round(time.perf_counter()-t0,1),flush=True)
if __name__=="__main__":main()
