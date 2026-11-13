"""V52 frozen joint co-learning: six-environment holdout and private t0 gifts.

Every intervention clones each subject into separate worlds, matches ALL RNG
draws and role samples within the yes/no pair, and forces one unilateral gift.
Only self-discounted food counts. Compare PRIOR to frozen V51 on new same seeds.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np,torch
from v51_endogenous_roles import (PrivateRoleActor,scenario as frozen_v51,
 context,load_frozen_gifts,N,K)
from v52_joint_roles_gifts import rollout
ROOT=Path(__file__).resolve().parent
SEEDS=(998101,998107,998109,998121,998131,998137)
INIT=("monolith","random")
CONDITIONS=("learned","fixed","random_0.15","random_0.35","random_0.60")
METRICS=("food","gifts","gift_slot_rate","coverage","full",
 "balanced_teams","role_switches_per_agent",
 "terminal_food","terminal_full","terminal_occupations")

def load(name,device):
 folder=ROOT/"runs"/name
 spec=json.loads((folder/"v52_spec.json").read_text("utf8"))
 status=json.loads((folder/"v52_status.json").read_text("utf8"))
 ck=torch.load(folder/"v52_latest.pt",map_location="cpu",weights_only=False)
 assert status["state"]=="completed" and ck["update"]==spec["updates"]==1500
 actor=PrivateRoleActor().to(device)
 actor.load_state_dict(ck["role"])
 actor.eval().requires_grad_(False)
 donor=ck["gift"].to(device).detach()
 donor.requires_grad_(False)
 return donor,actor,spec

def load_frozen_reference(donor_seed,role_seed,device):
 name=f"v51_LOLA20_D{donor_seed}_R{role_seed}"
 p=ROOT/"runs"/name
 spec=json.loads((p/"v51_spec.json").read_text("utf8"))
 ck=torch.load(p/"v51_latest.pt",map_location="cpu",weights_only=False)
 assert ck["update"]==1500
 actor=PrivateRoleActor().to(device)
 actor.load_state_dict(ck["actor"])
 actor.eval().requires_grad_(False)
 donor=load_frozen_gifts(f"v47_Q95_LOLA20_s{donor_seed}",device)
 return donor,actor

@torch.no_grad()
def causal_model(donor,role,seed,init,worlds,device):
 c=context(worlds*N,device)
 subs=torch.arange(N,device=device).repeat(worlds)
 yes=rollout(c,donor,role,seed,init=init,
     forced=1,subjects=subs,return_own=True)
 no=rollout(c,donor,role,seed,init=init,
     forced=0,subjects=subs,return_own=True)
 change=(yes[-2]-no[-2]).reshape(worlds,N)
 initial=(yes[-1]-no[-1]).reshape(worlds,N)
 assert bool(torch.allclose(initial,torch.full_like(initial,-.04),atol=3e-5))
 return dict(seed=seed,worlds=worlds,
   own_effect=change.mean(0).cpu().tolist(),
   mean_private=float(change.mean()),
   mean_immediate=float(initial.mean()),
   mean_future=float((change-initial).mean()),
   positive_agents=int((change.mean(0)>0).sum()))

@torch.no_grad()
def evaluate(name,device="cpu",worlds=24,causal_worlds=4):
 torch.set_num_threads(2)
 donor,role,spec=load(name,device)
 c=context(worlds,device)
 frozen=None
 if spec["source"]=="prior":
  frozen=load_frozen_reference(spec["gift_seed"],spec["role_seed"],device)
 results=[];effects=[];comparators=[]
 start=time.perf_counter()
 for init in INIT:
  for seed in SEEDS:
   for condition in CONDITIONS:
    baseline=None if condition=="learned" else condition
    metric,*_=rollout(c,donor,role,seed,
      init=init,role_baseline=baseline)
    results.append(dict(model=name,init=init,seed=seed,
      condition=condition,**metric))
   if frozen is not None:
    ref,*_=frozen_v51(c,frozen[0],frozen[1],seed,init=init)
    comparators.append(dict(seed=seed,init=init,**ref))
   effects.append(dict(init=init,**causal_model(donor,role,seed,init,
      worlds=causal_worlds,device=device)))
  main=[r for r in results if r["init"]==init and r["condition"]=="learned"]
  effect=[r for r in effects if r["init"]==init]
  avg={k:float(np.mean([x[k] for x in main])) for k in METRICS}
  causal=np.asarray([r["own_effect"] for r in effect])
  print("V52_HOLDOUT",name,init,
    "food",round(avg["food"],4),
    "terminal_roles",round(avg["terminal_occupations"],3),
    "gift_rate",round(avg["gift_slot_rate"],4),
    "causal",round(float(causal.mean()),4),
    "positive",int((causal.mean(0)>0).sum()),flush=True)
 assert len(results)==len(INIT)*len(SEEDS)*len(CONDITIONS)==60
 assert len(effects)==len(INIT)*len(SEEDS)==12
 if frozen is not None:assert len(comparators)==12
 target=ROOT/"results"/("v52_holdout_"+name+".json")
 target.write_text(json.dumps(dict(model=name,source_spec=spec,
   seeds=SEEDS,conditions=CONDITIONS,init_states=INIT,
   worlds_per_seed=worlds,causal_worlds_per_seed=causal_worlds,
   matched_counterfactual_own_rewards=True,
   rows=results,causal_by_seed=effects,
   frozen_reference_v51_by_seed=comparators),indent=1),encoding="utf8")
 print("V52_DONE",name,"elapsed",round(time.perf_counter()-start,2),flush=True)
 return results

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 p.add_argument("--worlds",type=int,default=24)
 p.add_argument("--causal-worlds",type=int,default=4)
 a=p.parse_args()
 evaluate(a.name,a.device,a.worlds,a.causal_worlds)
if __name__=="__main__":main()
