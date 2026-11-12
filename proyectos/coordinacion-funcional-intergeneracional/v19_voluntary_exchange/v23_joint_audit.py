"""V23: all-agent counterfactual joint-policy audit on frozen models.

For each person, force a costly gift vs no gift only in the initial round.
All subsequent donations AND occupational switches remain freely learned
and stochastic; coupled random numbers in matched environments.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor,step
from v22_occupations import PrivateOccupationActor,start
from audit_targeted import SEEDS
ROOT=Path(__file__).resolve().parent
REPEAT_KEYS=("roles","prev_gift","prev_recipient","incoming","trust",
             "lastfood","full","cover","last_switch")

def load_model(name,device):
  folder=ROOT/"runs"/name
  spec=json.loads((folder/"v23_spec.json").read_text("utf8"))
  status=json.loads((folder/"v23_status.json").read_text("utf8"))
  assert status["state"]=="completed"
  raw=torch.load(folder/"joint_latest.pt",weights_only=False,map_location="cpu")
  assert raw["update"]==status["updates"]==spec["updates"]
  gift=PrivateGiftActor(spec["n"],spec["hidden"],spec["init_scale"]).to(device)
  role=PrivateOccupationActor(spec["n"],spec["hidden"]).to(device)
  gift.load_state_dict(raw["gift"]);role.load_state_dict(raw["role"])
  gift.eval().requires_grad_(False)
  role.eval().requires_grad_(False)
  return gift,role,spec

@torch.no_grad()
def forced(c,gift,role,seed,init="monolith",mode="normal",
           condition=1,interval=8,switch_cost=.015):
  assert mode in ("normal","no_history","scramble")
  n=c.n;big=replace(c,batch=c.batch*n)
  torch.manual_seed(seed*41+211)
  original=start(c,seed,init=init)
  w=dict(graph=original["graph"],t=0)
  for key in REPEAT_KEYS:
    w[key]=original[key].repeat_interleave(n,dim=0)
  index=torch.arange(big.batch,device=c.device)
  focus=torch.arange(n,device=c.device).repeat(c.batch)
  ret=torch.zeros(big.batch,device=c.device)
  initial=None
  future=torch.zeros_like(ret)
  change=torch.zeros_like(ret)
  received_next=None
  for t in range(c.horizon):
    if t%interval==0:
      obs=w
      if mode=="no_history":
        obs=dict(w,prev_gift=torch.zeros_like(w["prev_gift"]),
                 trust=torch.zeros_like(w["trust"]))
      action,_,_=role.act(big,obs)
      w["roles"]=(w["roles"]+action.long())%c.k
      w["last_switch"]=action
      change+=action[index,focus]
    dm={"normal":"normal","no_history":"no_social","scramble":"scramble"}[mode]
    dest,offers,_,_=gift.act(big,w,mode=dm)
    if t==0:
      offers=offers.clone()
      offers[index,focus]=float(condition)
    r=step(big,w,dest,offers)
    if t%interval==0:
      r=r-switch_cost*action
      w["lastfood"]=r
    own=r[index,focus]
    ret+=(c.gamma**t)*own
    if t==0:initial=own.clone()
    else: future+=(c.gamma**t)*own
    if t==1:received_next=w["incoming"][index,focus].sum(1).clone()
  reshape=lambda x:x.reshape(c.batch,n).detach().cpu().numpy()
  return dict(total=reshape(ret),initial=reshape(initial),
      future=reshape(future),switches=reshape(change),
      next_received=reshape(received_next) if received_next is not None else None)

@torch.no_grad()
def main():
  p=argparse.ArgumentParser()
  p.add_argument("--name",required=True)
  p.add_argument("--worlds",type=int,default=20)
  p.add_argument("--steps",type=int,default=48)
  p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
  a=p.parse_args()
  torch.set_num_threads(2)
  gift,role,spec=load_model(a.name,a.device)
  t0=time.perf_counter()
  rows=[]
  for topo,degree,init in (
    ("ring",2,"monolith"),("ring",2,"random"),
    ("rewired",2,"monolith"),("ring",4,"monolith")):
    c=C(n=spec["n"],k=2,degree=degree,topology=topo,
      batch=a.worlds,horizon=a.steps,cost=spec["cost"],
      gamma=spec["gamma"],device=a.device)
    for mode in ("normal","no_history","scramble"):
      by_seed=[]
      for seed in SEEDS:
        yes=forced(c,gift,role,seed,init=init,mode=mode,
           condition=1,interval=spec["role_interval"],
           switch_cost=spec["switch_cost"])
        no=forced(c,gift,role,seed,init=init,mode=mode,
           condition=0,interval=spec["role_interval"],
           switch_cost=spec["switch_cost"])
        diff={x:yes[x]-no[x] for x in yes if yes[x] is not None}
        # Exact immediate private donation cost independent of partners.
        assert np.max(np.abs(diff["initial"]+spec["cost"]))<1.e-5,(
          a.name,topo,degree,init,mode,np.unique(diff["initial"]))
        by_seed.append(dict(seed=seed,
          all_agents={k:v.mean(0).tolist() for k,v in diff.items()},
          mean_return=float(diff["total"].mean())))
      x=np.array([s["all_agents"]["total"] for s in by_seed])
      row=dict(topology=topo,degree=degree,init=init,mode=mode,
        mean_total=float(x.mean()),positive_agents=int((x.mean(0)>0).sum()),
        positive_seed_person_pairs=int((x>0).sum()),pairs=int(x.size),
        per_agent=x.mean(0).tolist(),by_seed=by_seed,
        worlds_per_seed=a.worlds)
      rows.append(row)
      print("V23_CAUSAL",a.name,topo,degree,init,mode,
        "RETURN",round(row["mean_total"],4),
        "POSITIVE",row["positive_agents"],"/",c.n,
        "elapsed",round(time.perf_counter()-t0,1),flush=True)
  (ROOT/"results"/("v23_joint_audit_"+a.name+".json")).write_text(
    json.dumps(dict(model=a.name,checkpoint=spec["updates"],
         seeds=SEEDS,rows=rows,steps=a.steps,worlds_per_seed=a.worlds,
         caveat="All agents, paired intervention; occupational changes and donation policies stochastic and frozen; two-profession experiment."),indent=1),
    encoding="utf8")
  print("V23_AUDIT_FINISHED",a.name,len(rows),flush=True)
if __name__=="__main__":main()
