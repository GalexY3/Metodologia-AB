"""V43 frozen-policy heldouts and every-person t0 causal one-gift interventions.

Time-of-termination random streams use a separate torch.Generator; this is
the preregistered technical amendment, not a new training mechanism.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK,start4
from v25_holdout import NoDonations,relocated
from v25_multi_capacity import step_multi
from v43_random_horizon import roll
from audit_targeted import SEEDS
ROOT=Path(__file__).resolve().parent
CONFIGS=(("ring","monolith"),("ring","random"),("rewired","monolith"))
STATE_FIELDS=("roles","prev_gift","prev_recipient","incoming","trust",
 "lastfood","full","cover","last_switch")
METRICS=("food","gifts_per_person","coverage","complete","potential",
 "mean_alive_rounds","last_round_survival","total_alive_agent_rounds")

def load(name,device):
 p=ROOT/"runs"/name
 spec=json.loads((p/"v43_spec.json").read_text("utf8"))
 status=json.loads((p/"v43_status.json").read_text("utf8"))
 assert status["state"]=="completed" and status["updates"]==spec["updates"]
 ck=torch.load(p/"joint_latest.pt",map_location="cpu",weights_only=False)
 assert ck["update"]==spec["updates"]
 gift=PrivateGiftActor(spec["n"],spec["hidden"],spec["init_scale"]).to(device)
 role=PrivateOccupationK(spec["n"],spec["k"],spec["hidden"]).to(device)
 gift.load_state_dict(ck["gift"]);role.load_state_dict(ck["role"])
 gift.eval().requires_grad_(False);role.eval().requires_grad_(False)
 return gift,role,spec

def termination_generator(seed,device):
 gen=torch.Generator(device=device)
 gen.manual_seed(seed*83031+432)
 return gen

@torch.no_grad()
def holdout(name,worlds=12,steps=48,device="cuda"):
 gift,role,spec=load(name,device)
 alt_gift,alt_role=relocated(gift,role,spec,device)
 conditions=[
  ("learned",gift,role,None),
  ("role_fixed",gift,role,"fixed"),
  ("role_random_015",gift,role,"random_0.15"),
  ("role_random_035",gift,role,"random_0.35"),
  ("role_random_060",gift,role,"random_0.60"),
  ("donations_blocked",NoDonations(gift),role,None),
  ("relocated_people",alt_gift,alt_role,None)]
 results=[]
 for topo,init in CONFIGS:
  records={n:[] for n,*_ in conditions}
  for seed in SEEDS:
   c=C(n=spec["n"],k=4,degree=6,topology=topo,batch=worlds,
    horizon=steps,cost=spec["cost"],gamma=spec["gamma"],device=device)
   for label,d,r,baseline in conditions:
    torch.manual_seed(seed*73+41)
    measure,*_=roll(c,d,r,seed,init=init,
      q=spec["effective_q"],hidden_clock=spec["hidden_clock"],
      interval=spec["role_interval"],move_cost=spec["move_cost"],
      role_baseline=baseline,survival_generator=termination_generator(seed,device))
    records[label].append(dict(seed=seed,**measure))
   # Survival is identical across role and donor ablations by construction.
   reference=records["learned"][-1]["mean_alive_rounds"]
   for x in records.values():
    assert abs(x[-1]["mean_alive_rounds"]-reference)<1e-8
  for label,values in records.items():
   r=dict(model=name,topology=topo,init=init,condition=label,
     worlds=worlds*len(SEEDS),
     **{key:float(np.mean([v[key] for v in values])) for key in METRICS},
     by_seed=values)
   results.append(r)
   if topo=="ring" and init=="monolith":
    print("V43_HOLDOUT",name,label,"FOOD",round(r["food"],4),
       "GIFTS",round(r["gifts_per_person"],4),
       "ACTIVE",round(r["mean_alive_rounds"],2),flush=True)
 target=ROOT/"results"/("v43_holdout_"+name+".json")
 target.write_text(json.dumps(dict(model=name,spec=spec,
    worlds_per_seed=worlds,seeds=SEEDS,
    independently_seeded_survival=True,
    rows=results),indent=1),encoding="utf8")
 assert len(results)==len(CONFIGS)*len(conditions)==21
 print("V43_HOLDOUT_DONE",name,len(results),flush=True)

@torch.no_grad()
def force_one(c,gift,role,seed,init,forced,q,hidden_clock,
              interval=8,move_cost=.015):
 """Every person's first offer is independently forced yes/no in matched worlds."""
 n=c.n;big=replace(c,batch=c.batch*n)
 torch.manual_seed(seed*41+211)
 base=start4(c,seed,init)
 w={"graph":base["graph"],"t":0}
 for key in STATE_FIELDS:w[key]=base[key].repeat_interleave(n,0)
 ids=torch.arange(big.batch,device=c.device)
 subjects=torch.arange(n,device=c.device).repeat(c.batch)
 alive=torch.ones(c.batch,dtype=torch.bool,device=c.device)
 generator=termination_generator(seed,c.device)
 total=torch.zeros(big.batch,device=c.device)
 initial=None
 for t in range(c.horizon):
  if t>0 and q<1.:
   alive=alive&(torch.rand(c.batch,device=c.device,generator=generator)<q)
  per_branch=alive.repeat_interleave(n).float()
  obs=({**w,"t":0} if hidden_clock else w)
  if t%interval==0:
   chosen,_,_=role.act(big,obs,history=True)
   changed=(chosen!=w["roles"]).float()
   w["roles"]=chosen
   w["last_switch"]=changed
  obs=({**w,"t":0} if hidden_clock else w)
  drawn=[gift.act(big,obs,mode="normal") for _ in range(big.k-1)]
  dest=torch.stack([v[0] for v in drawn],2)
  offers=torch.stack([v[1] for v in drawn],2)
  if t==0:
   offers=offers.clone()
   offers[ids,subjects,0]=float(forced)
  food,_=step_multi(big,w,dest,offers)
  if t%interval==0:
   food=food-move_cost*changed
   w["lastfood"]=food
  own=food[ids,subjects]*per_branch
  total+=(c.gamma**t)*own
  if t==0:initial=own.clone()
 array=lambda x:x.reshape(c.batch,n).detach().cpu().numpy()
 return dict(total=array(total),initial=array(initial),future=array(total-initial))

@torch.no_grad()
def causal(name,worlds=6,steps=48,device="cuda"):
 gift,role,spec=load(name,device)
 rows=[]
 for topo,init in CONFIGS:
  c=C(n=spec["n"],k=4,degree=6,topology=topo,batch=worlds,
    horizon=steps,cost=spec["cost"],gamma=spec["gamma"],device=device)
  outcomes=[]
  for seed in SEEDS:
   yes=force_one(c,gift,role,seed,init,1,
     q=spec["effective_q"],hidden_clock=spec["hidden_clock"],
     interval=spec["role_interval"],move_cost=spec["move_cost"])
   no=force_one(c,gift,role,seed,init,0,
     q=spec["effective_q"],hidden_clock=spec["hidden_clock"],
     interval=spec["role_interval"],move_cost=spec["move_cost"])
   difference={k:yes[k]-no[k] for k in yes}
   assert np.allclose(difference["initial"],-spec["cost"],atol=3e-5)
   outcomes.append(dict(seed=seed,per_agent={
     key:value.mean(0).tolist() for key,value in difference.items()}))
  totals=np.asarray([v["per_agent"]["total"] for v in outcomes])
  instant=np.asarray([v["per_agent"]["initial"] for v in outcomes])
  row=dict(model=name,topology=topo,init=init,
    mean_total=float(totals.mean()),
    mean_initial=float(instant.mean()),
    mean_future=float(totals.mean()-instant.mean()),
    positive_agents=int((totals.mean(0)>0).sum()),
    per_agent=totals.mean(0).tolist(),by_seed=outcomes)
  rows.append(row)
  print("V43_CAUSAL",name,topo,init,
    "TOTAL",round(row["mean_total"],4),
    "FUTURE",round(row["mean_future"],4),
    "POS",row["positive_agents"],"/",spec["n"],flush=True)
 (ROOT/"results"/("v43_causal_"+name+".json")).write_text(
  json.dumps(dict(model=name,spec=spec,worlds_per_seed=worlds,
    seeds=SEEDS,steps=steps,rows=rows,
    matched_world_termination=True),indent=1),encoding="utf8")
 assert len(rows)==len(CONFIGS)
 print("V43_CAUSAL_DONE",name,len(rows),flush=True)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--kind",choices=("holdout","causal"),required=True)
 p.add_argument("--worlds",type=int,default=12)
 p.add_argument("--steps",type=int,default=48)
 p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
 a=p.parse_args();torch.set_num_threads(2)
 start=time.perf_counter()
 if a.kind=="holdout":holdout(a.name,a.worlds,a.steps,a.device)
 else:causal(a.name,a.worlds,a.steps,a.device)
 print("V43_EVAL_SECONDS",round(time.perf_counter()-start,1),flush=True)
if __name__=="__main__":main()
