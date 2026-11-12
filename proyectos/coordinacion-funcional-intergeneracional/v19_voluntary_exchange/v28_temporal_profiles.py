"""V28 frozen action trajectories and last-round cost checks.

Profiles 48-round behavior under new societies. No training or policy updates.
Measures whether cooperation unravels near the known finite horizon.
"""
from __future__ import annotations
import json,time,argparse
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C,step
from v22_occupations import start
from v24_k4_joint import start4
from v25_multi_capacity import step_multi
from v23_joint_audit import load_model as load_v23
from v25_holdout import load as load_v25
from audit_targeted import SEEDS
ROOT=Path(__file__).resolve().parent
V23=tuple(f"v23_SMOOTH_s{v}" for v in (3111,4111,5111,6111))
V25=tuple(f"v25_N48_C04_s{v}" for v in (3111,4111))
@torch.no_grad()
def simulate(model,kind,device,seed,worlds=32,horizon=48):
 donor,role,spec=(load_v23(model,device) if kind=="v23" else load_v25(model,device))
 k=2 if kind=="v23" else 4
 c=C(n=spec["n"],k=k,degree=2 if kind=="v23" else 6,
      topology="ring",batch=worlds,horizon=horizon,
      cost=spec["cost"],gamma=spec["gamma"],device=device)
 w=(start(c,seed,"monolith") if kind=="v23" else start4(c,seed,"monolith"))
 rows=[]
 for t in range(horizon):
  if t%spec["role_interval"]==0:
   if kind=="v23":
    change,_,_=role.act(c,w)
    w["roles"]=(w["roles"]+change.long())%k
   else:
    chosen,_,_=role.act(c,w)
    change=(chosen!=w["roles"]).float()
    w["roles"]=chosen
   w["last_switch"]=change
  if kind=="v23":
   dest,gift,_,_=donor.act(c,w,mode="normal")
   r=step(c,w,dest,gift)
   giftrate=gift.float().mean()
   giftper=giftrate
  else:
   action=[donor.act(c,w,mode="normal") for _ in range(k-1)]
   targets=torch.stack([z[0] for z in action],2)
   gifts=torch.stack([z[1] for z in action],2)
   r,_=step_multi(c,w,targets,gifts)
   giftrate=gifts.float().mean()
   giftper=gifts.sum(2).float().mean()
  if t%spec["role_interval"]==0:
   r=r-spec["switch_cost" if kind=="v23" else "move_cost"]*change
   w["lastfood"]=r
  rows.append(dict(round=t+1,gift_rate=float(giftrate),
     gifts_per_agent=float(giftper),
     food=float(r.mean()),coverage=float(w["cover"].mean()),
     full=float(w["full"].mean())))
 return rows

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--device",choices=("cuda","cpu"),default="cpu")
 parser.add_argument("--worlds",type=int,default=24)
 a=parser.parse_args()
 torch.set_num_threads(2);out=[]
 t0=time.perf_counter()
 for kind,models in (("v23",V23),("v25",V25)):
  for model in models:
   gathered=[]
   for seed in SEEDS:
    torch.manual_seed(seed*19+101)
    gathered.append(simulate(model,kind,a.device,seed,a.worlds))
   arr=np.asarray([[r["gifts_per_agent"] for r in sample] for sample in gathered])
   food=np.asarray([[r["food"] for r in sample] for sample in gathered])
   mean=arr.mean(0)
   row=dict(model=model,kind=kind,worlds_per_seed=a.worlds,
      seeds=SEEDS,
      mean_gifts_by_round=mean.tolist(),
      mean_food_by_round=food.mean(0).tolist(),
      first_eight=float(mean[:8].mean()),
      last_eight=float(mean[-8:].mean()),
      final_round=float(mean[-1]),
      ratio_last_to_first=float(mean[-8:].mean()/(mean[:8].mean()+1e-10)),
      avg_first_8_seeds=arr[:,:8].mean(1).tolist(),
      avg_last_8_seeds=arr[:,-8:].mean(1).tolist())
   out.append(row)
   print("V28",model,"first8",round(row["first_eight"],4),
     "last8",round(row["last_eight"],4),
     "last/first",round(row["ratio_last_to_first"],3),
     "last",round(row["final_round"],4),flush=True)
 (ROOT/"results"/"v28_temporal_profiles.json").write_text(
  json.dumps(dict(models=out,method="Frozen six-seed trajectory profiles in heldout monolithic worlds, 48 rounds, matched initial worlds per model, no policy updates.",elapsed=time.perf_counter()-t0),indent=1),encoding="utf8")
 print("V28_DONE",len(out),flush=True)
if __name__=="__main__":main()
