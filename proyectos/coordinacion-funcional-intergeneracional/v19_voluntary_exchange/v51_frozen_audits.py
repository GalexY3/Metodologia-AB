"""V51 frozen 4-role policies, matched randomized occupation controls.

World teams have fixed K4 networks; roles and occupancies are voluntary
decisions, no quota. Gift policy is frozen from V47 source and role actor
was trained by its own food only.
"""
from __future__ import annotations
import argparse,json,time,copy
from pathlib import Path
import numpy as np,torch
from v51_endogenous_roles import (PrivateRoleActor,scenario,context,
 load_frozen_gifts,N,K,G)
ROOT=Path(__file__).resolve().parent
SEEDS=(997101,997107,997109,997121,997131,997137)
INITS=("monolith","random")
CONDITIONS=("learned","fixed","random_0.15","random_0.35","random_0.60","relocated_roles")
METRICS=("food","gifts","full","coverage","balanced_teams",
 "switches_per_person","terminal_food","terminal_full","terminal_balanced_teams")

def load(name,device):
 folder=ROOT/"runs"/name
 spec=json.loads((folder/"v51_spec.json").read_text("utf8"))
 status=json.loads((folder/"v51_status.json").read_text("utf8"))
 ck=torch.load(folder/"v51_latest.pt",map_location="cpu",weights_only=False)
 assert status["state"]=="completed" and status["updates"]==spec["updates"]==ck["update"]==1500
 actor=PrivateRoleActor().to(device)
 actor.load_state_dict(ck["actor"])
 actor.eval().requires_grad_(False)
 gift=load_frozen_gifts(spec["source"],device)
 return actor,gift,spec

def rearrange_roles(actor,seed):
 """One private actor policy per person, reassigned within each K4 group."""
 shifted=copy.deepcopy(actor)
 rng=np.random.default_rng(seed*2321+5115)
 perm=np.concatenate([
  4*j+rng.permutation(4) for j in range(G)])
 assert len(np.unique(perm))==N
 index=torch.as_tensor(perm,device=next(actor.parameters()).device)
 with torch.no_grad():
  for to,orig in zip(shifted.parameters(),actor.parameters()):
   to.copy_(orig[index])
 return shifted

@torch.no_grad()
def evaluate(name,device="cpu",worlds=24):
 torch.set_num_threads(2)
 role,gift,spec=load(name,device)
 c=context(worlds,device)
 results=[]
 t0=time.perf_counter()
 for init in INITS:
  for seed in SEEDS:
   relocated=rearrange_roles(role,seed)
   for condition in CONDITIONS:
    is_relocated=condition=="relocated_roles"
    current=relocated if is_relocated else role
    baseline=None if condition in ("learned","relocated_roles") else condition
    measure,*_=scenario(c,gift,current,seed,
      init=init,baseline=baseline)
    results.append(dict(model=name,init=init,seed=seed,condition=condition,
      **measure))
  for condition in CONDITIONS:
   sub=[x for x in results if x["init"]==init and x["condition"]==condition]
   mean={k:float(np.mean([x[k] for x in sub])) for k in METRICS}
   print("V51_AUDIT",name,init,condition,
    "food",round(mean["food"],4),
    "complete_terminal",round(mean["terminal_balanced_teams"],4),
    "full",round(mean["full"],4),
    "gifts",round(mean["gifts"],4),flush=True)
 assert len(results)==len(SEEDS)*len(INITS)*len(CONDITIONS)==72
 output=dict(model=name,source_spec=spec,
   seeds=list(SEEDS),worlds_per_seed=worlds,
   init_conditions=INITS,conditions=CONDITIONS,
   control="private role actors frozen, donation actors frozen, matched environments",
   rows=results)
 (ROOT/"results"/("v51_holdout_"+name+".json")).write_text(
  json.dumps(output,indent=1),encoding="utf8")
 print("V51_HOLDOUT_DONE",name,"elapsed",round(time.perf_counter()-t0,2),flush=True)
 return output

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 p.add_argument("--worlds",type=int,default=24)
 a=p.parse_args()
 evaluate(a.name,a.device,a.worlds)
if __name__=="__main__":main()
