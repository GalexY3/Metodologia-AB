"""V40 causal all-person immediate welfare wedge: conditional vs unconditional gifts.

One intervention on first slot per individual at round25; identical pretrained
contract policies and other proposals; evaluate own/recipient/social payoff.
Source V30/V31 six locked checkpoints, 6 environment seeds, heldout worlds.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
from targeted_gifts import C
from v24_k4_joint import start4
from v25_holdout import load
from v25_multi_capacity import step_multi
from v30_consensual import contract_step,OBSERVATIONS
from audit_targeted import SEEDS
from v39_contract_outage import SOURCE_NAMES
ROOT=Path(__file__).resolve().parent
FIELDS=("roles","prev_gift","prev_recipient","incoming","trust",
 "lastfood","full","cover","last_switch")

@torch.no_grad()
def decision_state(seed,c,actor,role,spec):
 """Exactly 24 original contract rounds, then decide t=25 professions and gifts."""
 torch.manual_seed(seed*73+41)
 w=start4(c,seed,"monolith")
 OBSERVATIONS.clear()
 for t in range(24):
  if t%spec["role_interval"]==0:
   occupations,_,_=role.act(c,w)
   changed=(occupations!=w["roles"]).float()
   w["roles"]=occupations;w["last_switch"]=changed
  actions=[actor.act(c,w,mode="normal") for _ in range(3)]
  dest=torch.stack([a[0] for a in actions],2)
  offers=torch.stack([a[1] for a in actions],2)
  r,_=contract_step(c,w,dest,offers)
  if t%spec["role_interval"]==0:
   w["lastfood"]=r-spec["move_cost"]*changed
 assert w["t"]==24
 # Subject's private job choice t25 remains unchanged in both counterfactuals.
 nextrole,_,_=role.act(c,w)
 w["last_switch"]=(nextrole!=w["roles"]).float()
 w["roles"]=nextrole
 actions=[actor.act(c,w,mode="normal") for _ in range(3)]
 dest=torch.stack([a[0] for a in actions],2)
 offers=torch.stack([a[1] for a in actions],2)
 return w,dest,offers

@torch.no_grad()
def paired(seed,name,worlds,device):
 actor,role,spec=load(name,device)
 n=spec["n"]
 c=C(n=n,k=4,degree=6,topology="ring",batch=worlds,horizon=48,
    cost=spec["cost"],gamma=spec["gamma"],device=device)
 w,dest,offers=decision_state(seed,c,actor,role,spec)
 big=replace(c,batch=worlds*n)
 subjects=torch.arange(n,device=device).repeat(worlds)
 indices=torch.arange(worlds*n,device=device)
 extended_dest=dest.repeat_interleave(n,dim=0)
 extended_offers=offers.repeat_interleave(n,dim=0)
 source={key:(val.repeat_interleave(n,dim=0)
  if isinstance(val,torch.Tensor) and key!="graph" else val)
  for key,val in w.items()}
 assert source["roles"].shape==(worlds*n,n)
 byregime={}
 for settlement in ("unilateral","contract"):
  yes=extended_offers.clone();no=extended_offers.clone()
  yes[indices,subjects,0]=1.
  no[indices,subjects,0]=0.
  envY={k:(v.clone() if isinstance(v,torch.Tensor) else v) for k,v in source.items()}
  envN={k:(v.clone() if isinstance(v,torch.Tensor) else v) for k,v in source.items()}
  if settlement=="unilateral":
   rY,_=step_multi(big,envY,extended_dest,yes)
   rN,_=step_multi(big,envN,extended_dest,no)
  else:
   rY,_=contract_step(big,envY,extended_dest,yes)
   rN,_=contract_step(big,envN,extended_dest,no)
  difference=rY-rN
  own=difference[indices,subjects]
  targeted_recipient=extended_dest[indices,subjects,0]
  recipient=difference[indices,targeted_recipient]
  others=difference.sum(1)-own
  social=difference.sum(1)
  nonlocal_effect=(others-recipient).abs()
  assert float(nonlocal_effect.max())<2e-5,(name,settlement,'nonlocal recipient effect')
  if settlement=="unilateral":
   assert torch.allclose(own,torch.full_like(own,-spec["cost"]),atol=2e-5)
  per_agent=lambda x:x.reshape(worlds,n).mean(0).cpu().tolist()
  avg=lambda x:float(x.mean())
  byregime[settlement]=dict(
    own_private=avg(own),targeted_recipient_gain=avg(recipient),
    net_social_total=avg(social),net_social_per_capita=avg(social)/n,
    useful_fraction=avg((recipient>1e-5).float()),
    new_deal_fraction=avg((social.abs()>1e-5).float()),
    profitable_private_fraction=avg((own>1e-5).float()),
    socially_profitable_fraction=avg((social>1e-5).float()),
    private_agent_means=per_agent(own),
    social_agent_means=per_agent(social),
    recipient_agent_means=per_agent(recipient),
    recipients_positive_per_agent=per_agent((recipient>1e-5).float()))
 return dict(seed=seed,name=name,n=n,cost=spec["cost"],
   worlds=worlds,round=25,
   by_regime=byregime,
   positive_slot_rate= float(offers[:,:,0].mean()))

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",choices=SOURCE_NAMES,required=True)
 p.add_argument("--worlds",type=int,default=12)
 p.add_argument("--n-seeds",type=int,default=6)
 p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 p.add_argument("--smoke",action="store_true")
 a=p.parse_args()
 torch.set_num_threads(2)
 assert 1<=a.n_seeds<=len(SEEDS)
 t0=time.perf_counter()
 records=[]
 for seed in SEEDS[:a.n_seeds]:
  x=paired(seed,a.name,a.worlds,a.device)
  records.append(x)
  unilateral=x["by_regime"]["unilateral"]
  contract=x["by_regime"]["contract"]
  print("V40",a.name,seed,"own_uni",round(unilateral["own_private"],4),
   "social_uni",round(unilateral["net_social_total"],4),
   "recipient_uni",round(unilateral["targeted_recipient_gain"],4),
   "own_contract",round(contract["own_private"],4),
   "social_contract",round(contract["net_social_total"],4),
   flush=True)
 if not a.smoke:
  path=ROOT/"results"/("v40_marginal_"+a.name+".json")
  path.write_text(json.dumps(dict(model=a.name,rows=records,
      seeds=SEEDS[:a.n_seeds],worlds=a.worlds,
      all_agents_forced=True,no_training=True,
      note="Own -cost for unilateral, recipient material benefit and social net from forcing ONE proposal in round25, not long-run stable best response."),indent=1),encoding="utf8")
 print("V40_FINISHED",a.name,"envs",len(records),
    "seconds",round(time.perf_counter()-t0,2))
if __name__=="__main__":main()
