"""Feasible no-learning random-then-freeze baseline across population sizes.

Random sender/receptor decisions respect original directed request protocol:
each sender contacts ≤1 neighbor; each receiver can receive many and accept ≤1.
After 8 or 24 ticks, all agents simply stop. No network optimization,
global counts, RL or smart stopping. Executable baseline, not learned roles.
"""
import json,time,hashlib,math
from pathlib import Path
import torch
from agents import LocalActor
from environment import VectorSociety,Configuration
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"freeze_v2d";OUT.mkdir(exist_ok=True)
SIZES=((6,6,96),(10,12,60),(12,20,24),(20,24,16),(30,32,8))
K=4
MODES=("random_8_then_freeze","random_24_then_freeze","random_always")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
LOCK={"protocol":"PREREG_SCALE_STRATEGY_AUDIT.md plus exploratory extension to larger N",
      "script_sha":sha(ROOT/"random_freeze_scaling.py"),
      "env_sha":sha(ROOT/"environment.py"),"agents_sha":sha(ROOT/"agents.py"),
      "N":[r*c for r,c,_ in SIZES],"k":K,"steps":90,"modes":list(MODES),
      "world_seed":"1710000+200*N+100*k",
      "rule":"uniform random send+accept for 8 or24 steps, then no activity"}
p=OUT/"TEST_LOCK.json"
if p.exists():
 if json.loads(p.read_text(encoding="utf-8"))!=LOCK:raise RuntimeError("Lock changed")
else:p.write_text(json.dumps(LOCK,ensure_ascii=False,indent=2),encoding="utf-8")
actor=LocalActor(hidden=16)
actor.eval()
@torch.no_grad()
def run(rows,cols,batch,mode):
 n=rows*cols
 seed=1710000+200*n+100*K
 torch.manual_seed(seed+len(mode)*11)
 env=VectorSociety(Configuration(rows=rows,cols=cols,batch=batch,
     seed=seed,randomize_majority=True))
 env.reset(k=K)
 tv=[env.tv().clone()]
 changed=[]
 for t in range(90):
  obs=env.observe()
  active=t<(8 if mode=="random_8_then_freeze" else
               24 if mode=="random_24_then_freeze" else 90)
  if not active:
   s=torch.zeros((batch,n),dtype=torch.long)
   incoming,req,snap=env.deliveries(obs,s)
   a=torch.zeros_like(s)
  else:
   s,_,_,z=actor.sample_sender(obs,env.send_mask(),random_baseline=True)
   incoming,req,snap=env.deliveries(obs,s)
   a,_,_=actor.sample_receiver(z,snap,incoming,req,random_baseline=True)
  out=env.step(s,a,incoming,req)
  tv.append(out["tv"].clone())
  changed.append(out["churn"].clone())
 series=torch.stack(tv)
 churn=torch.stack(changed)
 stable=((series[-10:]<=.06)&(churn[-10:]<=.05)).all(0)
 return {"n":n,"k":K,"batch":batch,"mode":mode,"seed":seed,
     "initial_tv":float(series[0].mean()),
     "final_tv":float(series[-1].mean()),
     "final_tail_tv":float(series[-10:].mean()),
     "final_tail_churn":float(churn[-10:].mean()),
     "stable_count":int(stable.sum()),
     "stable_frac":float(stable.float().mean()),
     "near_final_count":int((series[-1]<=.06).sum()),
     "exact_final_count":int((series[-1].abs()<1e-6).sum()),
     "ever_near_count":int((series<=.06).any(0).sum()),
     "final_tv_worlds":series[-1].tolist(),
     "final_stable_worlds":stable.tolist(),
     "tv_curve_mean":[float(z) for z in series.mean(1)]}

def main():
 start=time.perf_counter()
 allr=[]
 for rows,cols,batch in SIZES:
  for mode in MODES:
   n=rows*cols
   target=OUT/f"N{n}_k4_{mode}.json"
   if target.exists():raise RuntimeError("No overwrites allowed")
   result=run(rows,cols,batch,mode)
   target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
   allr.append({x:y for x,y in result.items() if x not in
    ("final_tv_worlds","final_stable_worlds","tv_curve_mean")})
   print("RANDOM_FREEZE",n,mode,"tv",round(result["final_tv"],5),
     "stable",result["stable_count"],"/",batch,
     "exact",result["exact_final_count"],
     "elapsed",round(time.perf_counter()-start,1),flush=True)
 (OUT/"SUMMARY.json").write_text(json.dumps({"lock":LOCK,"results":allr,
   "interpretation":"random stop is engineered fixed clock, no context-dependent learned decision; tests trivial concentration as N rises"},
   ensure_ascii=False,indent=2),encoding="utf-8")
 print("FREEZE_DONE",len(allr),round(time.perf_counter()-start,1),flush=True)
if __name__=="__main__":main()
