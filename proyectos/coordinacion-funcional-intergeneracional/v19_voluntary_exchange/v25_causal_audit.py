"""Frozen V25 full-population marginal causal gift audit.

Force one (of three) individual donation slots at the initial round,
leave the other two slots and all future actions freely stochastic.
All agents, paired environmental worlds and PRNG states.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
from targeted_gifts import C
from v24_k4_joint import start4
from v25_multi_capacity import step_multi
from v25_holdout import load
from audit_targeted import SEEDS
ROOT=Path(__file__).resolve().parent
BATCH=("roles","prev_gift","prev_recipient","incoming",
       "trust","lastfood","full","cover","last_switch")

@torch.no_grad()
def forced(c,donor,role,seed,init,mode,condition,
           interval=8,move_cost=.015):
 assert mode in ("normal","no_history")
 n=c.n;big=replace(c,batch=c.batch*n)
 torch.manual_seed(seed*41+211)
 original=start4(c,seed,init)
 w=dict(graph=original["graph"],t=0)
 for key in BATCH:
  w[key]=original[key].repeat_interleave(n,0)
 focus=torch.arange(n,device=c.device).repeat(c.batch)
 rows=torch.arange(big.batch,device=c.device)
 ret=torch.zeros(big.batch,device=c.device)
 future=torch.zeros_like(ret)
 initial=None
 for t in range(c.horizon):
  if t%interval==0:
   newrole,_,_=role.act(big,w,history=(mode=="normal"))
   switched=(newrole!=w["roles"]).float()
   w["roles"]=newrole
   w["last_switch"]=switched
  actions=[donor.act(big,w,mode=("normal" if mode=="normal" else "no_social"))
    for _ in range(c.k-1)]
  dest=torch.stack([x[0] for x in actions],2)
  gifts=torch.stack([x[1] for x in actions],2)
  if t==0:
   gifts=gifts.clone()
   gifts[rows,focus,0]=float(condition)
  reward,_=step_multi(big,w,dest,gifts)
  if t%interval==0:
   reward=reward-move_cost*switched
   w["lastfood"]=reward
  own=reward[rows,focus]
  ret+=(c.gamma**t)*own
  if t==0:initial=own.clone()
  else:future+=(c.gamma**t)*own
 reshape=lambda x:x.reshape(c.batch,n).detach().cpu().numpy()
 return dict(total=reshape(ret),initial=reshape(initial),
             future=reshape(future))

@torch.no_grad()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--worlds",type=int,default=8)
 p.add_argument("--steps",type=int,default=48)
 p.add_argument("--device",choices=("cuda","cpu"),default="cuda")
 a=p.parse_args()
 torch.set_num_threads(2)
 gift,role,spec=load(a.name,a.device)
 rows=[];t0=time.perf_counter()
 for topo,init in (("ring","monolith"),("ring","random"),
                   ("rewired","monolith"),("ring","balanced")):
  c=C(n=spec["n"],k=4,degree=6,topology=topo,
      batch=a.worlds,horizon=a.steps,cost=spec["cost"],
      gamma=spec["gamma"],device=a.device)
  for mode in ("normal","no_history"):
   byseed=[]
   for seed in SEEDS:
    yes=forced(c,gift,role,seed,init,mode,1,
       interval=spec["role_interval"],move_cost=spec["move_cost"])
    no=forced(c,gift,role,seed,init,mode,0,
       interval=spec["role_interval"],move_cost=spec["move_cost"])
    delta={key:yes[key]-no[key] for key in yes}
    assert np.max(np.abs(delta["initial"]+spec["cost"]))<1.e-5
    byseed.append(dict(seed=seed,mean_agents={
      key:v.mean(0).tolist() for key,v in delta.items()}))
   x=np.asarray([r["mean_agents"]["total"] for r in byseed])
   row=dict(model=a.name,topology=topo,init=init,mode=mode,
      mean_total=float(x.mean()),positive_agents=int((x.mean(0)>0).sum()),
      positive_seed_person_pairs=int((x>0).sum()),
      n_pairs=int(x.size),per_agent=x.mean(0).tolist(),by_seed=byseed)
   rows.append(row)
   print("V25_CAUSAL",a.name,topo,init,mode,
      "RETURN",round(row["mean_total"],4),
      "POSITIVE",row["positive_agents"],"/",spec["n"],
      "elapsed",round(time.perf_counter()-t0,1),flush=True)
 (ROOT/"results"/("v25_causal_"+a.name+".json")).write_text(
     json.dumps(dict(model=a.name,spec=spec,steps=a.steps,
       worlds_per_seed=a.worlds,seeds=SEEDS,rows=rows,
       method="One of three costly donations forced at t=0; remaining slots and all future role/donation actions sampled under frozen private policies. Six environment seeds, all individuals."),indent=1),
     encoding="utf8")
 print("V25_CAUSAL_DONE",a.name,len(rows),flush=True)
if __name__=="__main__":main()
