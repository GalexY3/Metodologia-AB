"""V2-E time trajectories across k2,3,4, N120, 240 rounds.

Same models as previously, new world seeds. Five treatments include random
continual and random 24-ticks-then-freeze. Never update weights.
"""
from pathlib import Path
import json,hashlib,time,statistics,math
import torch
from environment import VectorSociety,Configuration
from agents import LocalActor
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"longitudinal_v2e"
OUT.mkdir(exist_ok=True)
COHORTS=(221,222,223)
KS=(2,3,4)
MODES=("credit2","credit0","random_always","random_T24","stay")
TICKS=240
BATCH=24
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def cp(seed,mode):
 w=2 if mode=="credit2" else 0
 return ROOT/"runs"/f"credit{w:g}_seed{seed}_u180"/"checkpoint_0180.pt"
lock={"protocol":"PREREG_LONGITUDINAL.md",
 "code":sha(ROOT/"longitudinal_v2e.py"),
 "env":sha(ROOT/"environment.py"),
 "agents":sha(ROOT/"agents.py"),
 "ckpts":{f"{s}_{m}":sha(cp(s,m)) for s in COHORTS for m in ("credit2","credit0")},
 "n":120,"batch":BATCH,"ks":list(KS),"cohorts":list(COHORTS),
 "modes":list(MODES),"ticks":TICKS,
 "world_seeds":"2040000+1000*train_seed+100*k"}
lp=OUT/"TEST_LOCK.json"
if lp.exists():
 if json.loads(lp.read_text(encoding="utf-8"))!=lock:
  raise RuntimeError("Locked code or model changed")
else:lp.write_text(json.dumps(lock,indent=2,ensure_ascii=False),encoding="utf-8")
actors={}
for seed in COHORTS:
 for mode in ("credit2","credit0"):
  ck=torch.load(cp(seed,mode),map_location="cpu",weights_only=False)
  a=LocalActor(hidden=ck["config"]["hidden"])
  a.load_state_dict(ck["actor"]);a.eval()
  actors[(seed,mode)]=a

@torch.no_grad()
def execute(seed,k,mode):
 world_seed=2040000+1000*seed+100*k
 torch.manual_seed(world_seed+83*len(mode))
 env=VectorSociety(Configuration(rows=10,cols=12,batch=BATCH,
                seed=world_seed,randomize_majority=True))
 env.reset(k=k)
 tv=[env.tv().clone()]
 churn=[torch.zeros(BATCH)]
 sending=[torch.zeros(BATCH)]
 accepting=[torch.zeros(BATCH)]
 a=actors[(seed,mode)] if mode in ("credit0","credit2") else actors[(seed,"credit2")]
 for t in range(TICKS):
  o=env.observe()
  active=mode!="stay" and not(mode=="random_T24" and t>=24)
  if active:
   random=mode in ("random_always","random_T24")
   s,_,_,h=a.sample_sender(o,env.send_mask(),random_baseline=random)
   inc,req,snap=env.deliveries(o,s)
   ac,_,_=a.sample_receiver(h,snap,inc,req,random_baseline=random)
  else:
   s=torch.zeros((BATCH,env.n),dtype=torch.long)
   inc,req,snap=env.deliveries(o,s)
   ac=torch.zeros_like(s)
  res=env.step(s,ac,inc,req)
  tv.append(res["tv"].clone())
  churn.append(res["churn"].clone())
  sending.append(res["messages"].clone())
  accepting.append(res["acceptances"].clone())
 v=torch.stack(tv)
 c=torch.stack(churn)
 send=torch.stack(sending)
 accept=torch.stack(accepting)
 stable10=((v[-10:]<=.06)&(c[-10:]<=.05)).all(0)
 init=v[0]
 initial_each=init.tolist()
 return {
   "seed":seed,"k":k,"mode":mode,"batch":BATCH,"ticks":TICKS,
   "world_seed":world_seed,
   "distance_curve_mean":v.mean(1).tolist(),
   "churn_curve_mean":c.mean(1).tolist(),
   "send_curve_mean":send.mean(1).tolist(),
   "accept_curve_mean":accept.mean(1).tolist(),
   "progress_curve_mean":(100*(1-v/init.unsqueeze(0))).mean(1).tolist(),
   "initial_tv_per_world":initial_each,
   "final_tv_per_world":v[-1].tolist(),
   "stable_last10":stable10.tolist(),
   "stable_count":int(stable10.sum()),
   "near_final_count":int((v[-1]<=.06).sum()),
   "exact_final_count":int((v[-1].abs()<1e-6).sum()),
   "final_tv":float(v[-1].mean()),
   "final_churn":float(c[-10:].mean()),
   "relative_progress":float((100*(1-v[-1]/init)).mean())}

def main():
 start=time.perf_counter()
 cases=[]
 for k in KS:
  for seed in COHORTS:
   for mode in MODES:
    target=OUT/f"k{k}_seed{seed}_{mode}.json"
    if target.exists():
     result=json.loads(target.read_text(encoding="utf-8"))
    else:
     result=execute(seed,k,mode)
     target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    cases.append(result)
    print("LONG",k,seed,mode,
       "D0",round(result["distance_curve_mean"][0],4),
       "Dlast",round(result["final_tv"],4),
       "progress%",round(result["relative_progress"],2),
       "stable",result["stable_count"],"/24",
       "elapsed",round(time.perf_counter()-start,1),flush=True)
 assert len(cases)==len(KS)*len(COHORTS)*len(MODES)
 summary=[]
 for k in KS:
  for mode in MODES:
   group=[x for x in cases if x["k"]==k and x["mode"]==mode]
   assert len(group)==3
   avg=lambda key:[statistics.mean(x[key][t] for x in group) for t in range(TICKS+1)]
   tv=avg("distance_curve_mean");progress=avg("progress_curve_mean")
   ch=avg("churn_curve_mean")
   def average_slice(x,a,b):return statistics.mean(x[a:b])
   plateau_slope=average_slice(tv,201,241)-average_slice(tv,161,201)
   summary.append({"k":k,"mode":mode,"cohorts":list(COHORTS),"test_worlds":BATCH*3,
    "distance_curve_mean":tv,"progress_curve_mean":progress,"churn_curve_mean":ch,
    "initial_D":tv[0],"final_D":tv[-1],"final_progress_pct":progress[-1],
    "final_churn":statistics.mean(x["final_churn"] for x in group),
    "stable_count":sum(x["stable_count"] for x in group),
    "near_count":sum(x["near_final_count"] for x in group),
    "exact_count":sum(x["exact_final_count"] for x in group),
    "late_D_change_mean_last40_minus_prev40":plateau_slope,
    "seedwise_final_D":[x["final_tv"] for x in group]})
 out=OUT/"SUMMARY.json"
 out.write_text(json.dumps({"lock":lock,"n_results":len(cases),
     "n_independent_trained_cohorts":3,"n_worlds_per_k_mode":72,
     "summary":summary,
     "note":"Progress % = 100*(1-D(t)/D0), not decision accuracy; 100 means exact balance and 0 means unchanged initial error"},
     ensure_ascii=False,indent=2),encoding="utf-8")
 for row in summary:
  print("SUMMARY",row["k"],row["mode"],"D240",round(row["final_D"],4),
   "P240",round(row["final_progress_pct"],1),
   "stable",row["stable_count"],"/72",
   "churn",round(row["final_churn"],3),
   "plateauDelta",round(row["late_D_change_mean_last40_minus_prev40"],5),
   flush=True)
 print("LONGITUDINAL_DONE",round(time.perf_counter()-start,1),flush=True)
if __name__=="__main__":main()
