"""V54 frozen k-scaling evaluation, all predeclared k values and controls.

Policies are NEVER retrained during evaluation. Each world uses the same
environment seed across conditions (but policy-dependent RNG consumption
may differ, hence not pathwise paired action draws).
"""
from __future__ import annotations
import argparse,json,time,torch,numpy as np
from pathlib import Path
from v54_k_scaling import (ROOT,N,KS,H,TECHS,CONTROLS,PrivateOccupationK,
 donor_source,config,episode)
SEEDS=(999201,999207,999209,999221,999231,999237)
INIT=("monolith","random")
KEYS=("food","coverage","full","group_complete",
 "gifts_per_person","gifts_per_link","move_per_person",
 "terminal_food","terminal_balance","terminal_full")

@torch.no_grad()
def load(name,device):
 folder=ROOT/"runs"/name
 spec=json.loads((folder/"v54_spec.json").read_text(encoding="utf8"))
 status=json.loads((folder/"v54_status.json").read_text(encoding="utf8"))
 ck=torch.load(folder/"v54_latest.pt",map_location="cpu",weights_only=False)
 assert spec["n"]==N and spec["k"] in KS
 assert status["state"]=="completed" and spec["updates"]==1400 and ck["update"]==1400
 actor=PrivateOccupationK(spec["k"]).to(device)
 actor.load_state_dict(ck["actor"])
 actor.eval().requires_grad_(False)
 gifts,mapping=donor_source(spec["method"],spec["donor_seed"],device)
 assert mapping==spec["donor_mapping"]
 return actor,gifts,spec

@torch.no_grad()
def audit(name,device="cpu",worlds=24):
 torch.set_num_threads(2)
 actor,donor,spec=load(name,device)
 c=config(spec["k"],worlds,device)
 rows=[];start=time.perf_counter()
 for init in INIT:
  for technology in TECHS:
   for baseline in CONTROLS:
    per_seed=[]
    for seed in SEEDS:
     m,*_=episode(c,donor,actor,seed,init=init,
       technology=technology,baseline=baseline,collect_grad=False)
     if technology=="FIXED3" and spec["k"]>=5:
      assert m["full"]<=3/(spec["k"]-1)+1e-6
     per_seed.append(dict(seed=seed,**m))
    aggregate={key:float(np.mean([v[key] for v in per_seed])) for key in KEYS}
    rows.append(dict(name=name,k=spec["k"],method=spec["method"],
     donor_seed=spec["donor_seed"],role_seed=spec["role_seed"],
     init=init,technology=technology,baseline=baseline,
     **aggregate,by_seed=per_seed))
    if technology=="ELASTIC" and baseline in ("learned","random_0.60","oracle_roles"):
     print("V54_AUDIT",name,init,baseline,
       "food",round(aggregate["food"],4),
       "complete",round(aggregate["terminal_balance"],4),
       "time",round(time.perf_counter()-start,1),flush=True)
 assert len(rows)==len(INIT)*len(TECHS)*len(CONTROLS)==36
 result=dict(model=name,spec=spec,seeds=SEEDS,worlds_per_seed=worlds,
  init_conditions=INIT,technology_conditions=TECHS,role_conditions=CONTROLS,
  precise_pairing="seed-matched only, action RNG consumption not guaranteed common",
  policies_frozen=True,rows=rows,
  elapsed_seconds=time.perf_counter()-start)
 (ROOT/"results"/f"v54_holdout_{name}.json").write_text(
  json.dumps(result,indent=1),encoding="utf8")
 print("V54_AUDIT_DONE",name,"cells",len(rows),
  "seconds",round(time.perf_counter()-start,1),flush=True)
 return result

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 p.add_argument("--worlds",type=int,default=24)
 a=p.parse_args()
 audit(a.name,a.device,a.worlds)
if __name__=="__main__":main()
