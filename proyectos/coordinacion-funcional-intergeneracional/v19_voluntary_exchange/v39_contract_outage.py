"""V39 — Causal effect of removing/restoring contractual settlement.

No training. Six original cold-start V30/V31 final checkpoints, intact
private actor/role parameters; matched seeds, four settlement regimes.

Contractual: each pair trades one unit only if both issue directed proposals.
Unilateral: every proposal gives a good at a cost, even if unreciprocated.
Closed: proposals can still be issued but no goods are transferred or paid for.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C
from v24_k4_joint import start4,adjacent_potential
from v25_holdout import load
from v30_consensual import contract_step,control_step,OBSERVATIONS
from audit_targeted import SEEDS
ROOT=Path(__file__).resolve().parent
ARMS=("control","closed8","unilateral8","unilateral_permanent")
SOURCE_NAMES=[f"v30_MUTUAL_C04_s{s}" for s in (3111,4111)]+[
 f"v31_N120_MUTUAL_C{cost}_s{s}" for cost in ("04","12") for s in (3111,4111)]
WINDOWS=((0,24),(24,32),(32,40),(40,48))

def regime(arm,t):
 if t<24 or arm=="control":return "contract"
 if arm=="closed8" and t<32:return "closed"
 if arm=="unilateral8" and t<32:return "unilateral"
 if arm=="unilateral_permanent":return "unilateral"
 return "contract"

@torch.no_grad()
def run(seed,arm,gift,role,spec,worlds=12,device="cpu"):
 assert arm in ARMS
 n=spec["n"]
 c=C(n=n,k=4,degree=6,topology="ring",batch=worlds,
     horizon=48,cost=spec["cost"],gamma=spec["gamma"],device=device)
 torch.manual_seed(seed*73+41)
 w=start4(c,seed,init="monolith")
 OBSERVATIONS.clear()
 trace=[]
 for t in range(48):
  if t%spec["role_interval"]==0:
   next_role,_,_=role.act(c,w)
   changed=(next_role!=w["roles"]).float()
   w["roles"]=next_role;w["last_switch"]=changed
  samples=[gift.act(c,w,mode="normal") for _ in range(3)]
  dest=torch.stack([x[0] for x in samples],2)
  offered=torch.stack([x[1] for x in samples],2)
  kind=regime(arm,t)
  if kind=="contract": food,_=contract_step(c,w,dest,offered)
  elif kind=="unilateral": food,_=control_step(c,w,dest,offered)
  else:food,_=contract_step(c,w,dest,torch.zeros_like(offered))
  if t%spec["role_interval"]==0:
   food=food-spec["move_cost"]*changed
   w["lastfood"]=food
  sent=OBSERVATIONS[-1][1]/(worlds*n)
  proposals=float(offered.sum().item())/(worlds*n)
  trace.append(dict(round=t+1,regime=kind,
    food=float(food.mean()),proposals=proposals,transfers=sent,
    coverage=float(w["cover"].mean()),potential=adjacent_potential(c,w),
    share_full=float(w["full"].mean())))
 def period(k,start,end):
  return float(np.mean([x[k] for x in trace[start:end]]))
 data=dict(seed=seed,arm=arm,worlds=worlds,
  intervals=[dict(window=f"{i+1}",rounds=f"{start+1}-{end}",
    food=period("food",start,end),
    proposals=period("proposals",start,end),
    transfers=period("transfers",start,end),
    material_coverage=period("coverage",start,end),
    potential=period("potential",start,end))
       for i,(start,end) in enumerate(WINDOWS)],
  trace=trace)
 return data

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--name",required=True,choices=SOURCE_NAMES)
 parser.add_argument("--worlds",type=int,default=12)
 parser.add_argument("--n-seeds",type=int,default=6)
 parser.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 parser.add_argument("--smoke",action="store_true")
 a=parser.parse_args()
 torch.set_num_threads(2)
 assert 1<=a.n_seeds<=6 and a.worlds>=1
 actor,profession,spec=load(a.name,a.device)
 assert spec["settlement"]=="mutual" and spec["k"]==4
 assert spec["n"] in (48,120) and spec["cost"] in (.04,.12)
 t0=time.perf_counter()
 entries=[]
 for seed in SEEDS[:a.n_seeds]:
  by={}
  for arm in ARMS:
   x=run(seed,arm,actor,profession,spec,worlds=a.worlds,device=a.device)
   by[arm]=x
  ctl=by["control"]
  for arm in ARMS:
   datum=by[arm]
   # Pre-period is identical by construction until the 25th round.
   for a0,b0 in zip(ctl["trace"][:24],datum["trace"][:24]):
    for field in ("food","proposals","transfers","coverage","potential"):
     assert abs(a0[field]-b0[field])<1e-9, (seed,arm,field)
   datum["effects_vs_control"]=[
     dict(window=j+1,
       food=datum["intervals"][j]["food"]-ctl["intervals"][j]["food"],
       transfers=datum["intervals"][j]["transfers"]-ctl["intervals"][j]["transfers"],
       proposals=datum["intervals"][j]["proposals"]-ctl["intervals"][j]["proposals"])
     for j in range(4)]
   denom=ctl["intervals"][3]["food"]-.20
   datum["late_surplus_ratio"]=(
      (datum["intervals"][3]["food"]-.20)/denom if denom>0 else None)
   entries.append(datum)
  print("V39_SEED",a.name,seed,
    "BASE",round(ctl["intervals"][1]["food"],4),
    "CLOSED8",round(by["closed8"]["intervals"][1]["food"],4),
    "UNILATERAL8",round(by["unilateral8"]["intervals"][1]["food"],4),
    "LATE_RESTORED",round(by["closed8"]["intervals"][3]["food"],4),
    flush=True)
 if not a.smoke:
  dest=ROOT/"results"/("v39_contract_outage_"+a.name+".json")
  dest.write_text(json.dumps(dict(model=a.name,source_spec=spec,
     worlds_per_seed=a.worlds,seeds=list(SEEDS[:a.n_seeds]),
     regimes=list(ARMS),windows=[f"{x+1}-{y}" for x,y in WINDOWS],
     no_policy_training=True,matched_preperiod=True,rows=entries),
    indent=1),encoding="utf8")
 print("V39_FINISHED",a.name,"records",len(entries),
  "seconds",round(time.perf_counter()-t0,2),flush=True)

if __name__=="__main__":main()
