"""V23: strictly frozen heldout of joint from-scratch learners.

New environment seeds; 24 worlds per cluster, 6 clusters;
comparison to several fixed-rate role switching baselines, no gift,
no donation history and randomized private-person placement.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C
from v23_joint_cold import roll
from v23_joint_audit import load_model
from v22_frozen_holdout import reshuffle_private
from audit_targeted import SEEDS

ROOT=Path(__file__).resolve().parent
class NoGifts:
  def __init__(self,base):self.base=base
  @torch.no_grad()
  def act(self,c,w,mode="normal",greedy=False):
    dest,gift,lp,en=self.base.act(c,w,mode=mode,greedy=greedy)
    return dest,torch.zeros_like(gift),lp,en

@torch.no_grad()
def main():
  p=argparse.ArgumentParser()
  p.add_argument("--name",required=True)
  p.add_argument("--worlds",type=int,default=24)
  p.add_argument("--steps",type=int,default=48)
  p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
  a=p.parse_args()
  torch.set_num_threads(2)
  gift,role,spec=load_model(a.name,a.device)
  original=bool(spec["social"])
  role_reloc,gift_reloc=reshuffle_private(role,gift,881171,a.device,
              dict(hidden=spec["hidden"],init_scale=spec["init_scale"]))
  conditions=[
    ("joint_learned",gift,role,None,original),
    ("donation_history_hidden",gift,role,None,False),
    ("role_fixed",gift,role,"fixed",original),
    ("role_random_015",gift,role,"random_0.15",original),
    ("role_random_035",gift,role,"random_0.35",original),
    ("role_random_060",gift,role,"random_0.60",original),
    ("all_gifts_blocked",NoGifts(gift),role,None,original),
    ("people_relocated",gift_reloc,role_reloc,None,original)]
  rows=[];t0=time.perf_counter()
  for topology,degree in (("ring",2),("rewired",2),("ring",4)):
    for init in ("monolith","random"):
      by_cond={name:[] for name,*_ in conditions}
      for seed in SEEDS:
        c=C(n=spec["n"],k=2,degree=degree,topology=topology,
            batch=a.worlds,horizon=a.steps,cost=spec["cost"],
            gamma=spec["gamma"],device=a.device,
            social=True)
        for idx,(label,d,r,baseline,social) in enumerate(conditions):
          torch.manual_seed(seed*79+degree*31+(init=="random")*13)
          m,*_=roll(c,d,r,seed,init=init,social=social,
             interval=spec["role_interval"],switch_cost=spec["switch_cost"],
             baseline=baseline)
          by_cond[label].append(dict(seed=seed,**m))
      for label,vals in by_cond.items():
        row=dict(model=a.name,topology=topology,degree=degree,init=init,
           condition=label,worlds=len(SEEDS)*a.worlds,
           **{key:float(np.mean([v[key] for v in vals])) for key in (
             "mean_food","last_food","gift","complementary_links",
             "balanced","switches_per_agent")},
           by_seed=vals)
        rows.append(row)
        if topology=="ring" and degree==2 and init=="monolith":
          print("V23_HOLDOUT",a.name,label,"FOOD",round(row["mean_food"],4),
                "GIVE",round(row["gift"],3),
                "OPPOSITE",round(row["complementary_links"],3),
                "BAL",round(row["balanced"],3),flush=True)
  target=ROOT/"results"/("v23_joint_holdout_"+a.name+".json")
  target.write_text(json.dumps(dict(model=a.name,train_spec=spec,
     seeds=SEEDS,worlds_per_seed=a.worlds,
     conditions=[x[0] for x in conditions],steps=a.steps,rows=rows,
     caveat="No donor pretraining. Frozen weights. Role random baselines have different number of PRNG samples; matched initial worlds, not perfectly common random numbers after intervention. No training-seed uncertainty covered."),indent=1),
     encoding="utf8")
  print("V23_HOLDOUT_DONE",a.name,"rows",len(rows),
        "seconds",round(time.perf_counter()-t0,1),flush=True)
if __name__=="__main__":main()
