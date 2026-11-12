"""Frozen V25 capacity-3 evaluation on unseen societies."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK
from v25_multi_capacity import roll,oracle
from audit_targeted import SEEDS
ROOT=Path(__file__).resolve().parent

def load(name,device):
 p=ROOT/"runs"/name
 spec=json.loads((p/"v25_spec.json").read_text("utf8"))
 state=json.loads((p/"v25_status.json").read_text("utf8"))
 assert state["state"]=="completed"
 weights=torch.load(p/"joint_latest.pt",map_location="cpu",weights_only=False)
 assert state["updates"]==weights["update"]
 donor=PrivateGiftActor(spec["n"],spec["hidden"],spec["init_scale"]).to(device)
 occup=PrivateOccupationK(spec["n"],spec["k"],spec["hidden"]).to(device)
 donor.load_state_dict(weights["gift"]);occup.load_state_dict(weights["role"])
 donor.eval().requires_grad_(False);occup.eval().requires_grad_(False)
 return donor,occup,spec

class NoDonations:
 def __init__(self,donor):self.donor=donor
 def act(self,c,w,mode="normal",greedy=False):
  dest,gift,lp,ent=self.donor.act(c,w,mode=mode,greedy=greedy)
  return dest,torch.zeros_like(gift),lp,ent

def relocated(donor,role,spec,device,seed=919911):
 rng=torch.Generator(device="cpu");rng.manual_seed(seed)
 perm=torch.randperm(spec["n"],generator=rng)
 def reorder(state):
  return {k:(v.index_select(0,perm.to(v.device)).clone()
    if v.ndim>=1 and v.shape[0]==spec["n"] else v.clone())
    for k,v in state.items()}
 d=PrivateGiftActor(spec["n"],spec["hidden"],spec["init_scale"]).to(device)
 r=PrivateOccupationK(spec["n"],spec["k"],spec["hidden"]).to(device)
 d.load_state_dict(reorder(donor.state_dict()))
 r.load_state_dict(reorder(role.state_dict()))
 d.eval().requires_grad_(False);r.eval().requires_grad_(False)
 return d,r

@torch.no_grad()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--worlds",type=int,default=16)
 p.add_argument("--steps",type=int,default=48)
 p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
 a=p.parse_args()
 torch.set_num_threads(2)
 donor,role,spec=load(a.name,a.device)
 altgift,altrole=relocated(donor,role,spec,a.device)
 conditions=[("learned",donor,role,None,True),
  ("no_history",donor,role,None,False),
  ("role_fixed",donor,role,"fixed",True),
  ("role_random_015",donor,role,"random_0.15",True),
  ("role_random_035",donor,role,"random_0.35",True),
  ("role_random_060",donor,role,"random_0.60",True),
  ("donations_blocked",NoDonations(donor),role,None,True),
  ("people_relocated",altgift,altrole,None,True)]
 rows=[];t0=time.perf_counter()
 for topology,init in (("ring","monolith"),("ring","random"),
                       ("ring","balanced"),("rewired","monolith")):
  accum={n:[] for n,*_ in conditions}
  for seed in SEEDS:
   c=C(n=spec["n"],k=spec["k"],degree=6,topology=topology,
       batch=a.worlds,horizon=a.steps,cost=spec["cost"],
       gamma=spec["gamma"],device=a.device)
   for name,g,r,baseline,social in conditions:
    torch.manual_seed(seed*73+41)
    m,*_=roll(c,g,r,seed,init=init,social=social,
              interval=spec["role_interval"],move_cost=spec["move_cost"],
              baseline=baseline)
    accum[name].append(dict(seed=seed,**m))
  for name,byseed in accum.items():
   fields=("food","final_food","gifts_per_person","distinct_coverage",
           "complete","useful_delivery_ratio","potential_coverage",
           "balanced","professions","switches")
   row=dict(model=a.name,topology=topology,init=init,condition=name,
       worlds=a.worlds*len(SEEDS),**{k:float(np.mean([x[k] for x in byseed]))
         for k in fields},by_seed=byseed)
   rows.append(row)
   if topology=="ring" and init=="monolith":
    print("V25_HOLDOUT",a.name,name,"FOOD",round(row["food"],4),
      "GIFT",round(row["gifts_per_person"],4),
      "COVER",round(row["distinct_coverage"],4),
      "FULL",round(row["complete"],4),flush=True)
 c=C(n=spec["n"],k=4,degree=6,topology="ring",
     batch=a.worlds,horizon=a.steps,cost=spec["cost"],device=a.device)
 ref=oracle(c)
 out=dict(model=a.name,spec=spec,seeds=SEEDS,worlds_per_seed=a.worlds,
   steps=a.steps,oracle_constructive=ref,rows=rows,
   caveat="Frozen trained policy. Oracle is hardcoded only as feasibility benchmark, never used for learning. Six environmental seed clusters do not substitute independent neural initializations.")
 (ROOT/"results"/("v25_holdout_"+a.name+".json")).write_text(
   json.dumps(out,indent=1),encoding="utf8")
 print("V25_HOLDOUT_DONE",a.name,len(rows),
   "elapsed",round(time.perf_counter()-t0,1),flush=True)
if __name__=="__main__":main()
