"""V30 frozen evaluation and matched all-agent causal voluntary proposal audit.

No training; preserve original V25 weights and architecture and vary only
bilateral settlement institution, with agent choices remaining private.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
import v25_multi_capacity as base
from v25_holdout import load,relocated,NoDonations
from v24_k4_joint import start4
from targeted_gifts import C
from audit_targeted import SEEDS
from v30_consensual import install,traced_roll,contract_step,control_step,oracle_contract,base_original_oracle
ROOT=Path(__file__).resolve().parent

def holdout(name,worlds=12,horizon=48,device='cpu'):
    gift,role,spec=load(name,device)
    shuffled_gift,shuffled_role=relocated(gift,role,spec,device)
    options=[("learned",gift,role,None,True),
       ("no_history",gift,role,None,False),
       ("role_fixed",gift,role,"fixed",True),
       ("role_random_015",gift,role,"random_0.15",True),
       ("role_random_035",gift,role,"random_0.35",True),
       ("role_random_060",gift,role,"random_0.60",True),
       ("donations_blocked",NoDonations(gift),role,None,True),
       ("relocated_people",shuffled_gift,shuffled_role,None,True)]
    results=[]
    for topo,init in (("ring","monolith"),("ring","random"),
                      ("ring","balanced"),("rewired","monolith")):
       values={name:[] for name,*_ in options}
       for seed in SEEDS:
          c=C(n=spec["n"],k=4,degree=6,topology=topo,batch=worlds,
             horizon=horizon,cost=spec["cost"],gamma=spec["gamma"],device=device)
          for opt_name,d,r,baseline,social in options:
             torch.manual_seed(seed*73+41)
             with torch.no_grad():
                m,*_=traced_roll(c,d,r,seed,init=init,social=social,
                   interval=spec["role_interval"],move_cost=spec["move_cost"],baseline=baseline)
             values[opt_name].append(dict(seed=seed,**m))
       keys=["food","final_food","gifts_per_person","distinct_coverage",
            "complete","potential_coverage","balanced","professions","switches",
            "proposals_per_person","settled_units_per_person",
            "acceptance_fraction","physical_useful_ratio"]
       for label,items in values.items():
          row=dict(model=name,topology=topo,init=init,condition=label,
               worlds=worlds*len(SEEDS),**{key:float(np.mean([v[key] for v in items]))
                  for key in keys},by_seed=items)
          results.append(row)
          if topo=="ring" and init=="monolith":
             print("V30_HOLDOUT",name,label,"FOOD",round(row["food"],4),
               "CONTRACTS",round(row["settled_units_per_person"],3),
               "PROPOSALS",round(row["proposals_per_person"],3),
               "COVER",round(row["distinct_coverage"],3),flush=True)
    c=C(n=spec["n"],k=4,degree=6,topology="ring",
         batch=worlds,horizon=horizon,cost=spec["cost"],device=device)
    oracle=oracle_contract(c) if spec["settlement"]=="mutual" else base_original_oracle(c)
    out=dict(model=name,settlement=spec["settlement"],
       spec=spec,seeds=SEEDS,worlds_per_seed=worlds,oracle=oracle,rows=results)
    target=ROOT/"results"/("v30_holdout_"+name+".json")
    target.write_text(json.dumps(out,indent=1),encoding="utf8")
    print("V30_HOLDOUT_DONE",name,len(results),flush=True)

REPEAT=("roles","prev_gift","prev_recipient","incoming","trust",
        "lastfood","full","cover","last_switch")
@torch.no_grad()
def force_one(c,gift,role,seed,init,mode,condition,interval=8,move_cost=.015):
    n=c.n
    big=replace(c,batch=c.batch*n)
    torch.manual_seed(seed*41+211)
    original=start4(c,seed,init)
    w={"graph":original["graph"],"t":0}
    for key in REPEAT:w[key]=original[key].repeat_interleave(n,0)
    subjects=torch.arange(n,device=c.device).repeat(c.batch)
    idx=torch.arange(big.batch,device=c.device)
    total=torch.zeros(big.batch,device=c.device)
    later=torch.zeros_like(total)
    immediate=None
    for t in range(c.horizon):
       if t%interval==0:
          newrole,_,_=role.act(big,w,history=(mode=="normal"))
          switched=(newrole!=w["roles"]).float()
          w["roles"]=newrole
          w["last_switch"]=switched
       action=[gift.act(big,w,mode=("normal" if mode=="normal" else "no_social"))
               for _ in range(c.k-1)]
       dest=torch.stack([v[0] for v in action],2)
       offers=torch.stack([v[1] for v in action],2)
       if t==0:
          offers=offers.clone()
          offers[idx,subjects,0]=condition
       r,_=base.step_multi(big,w,dest,offers)
       if t%interval==0:
          r-=move_cost*switched
          w["lastfood"]=r
       own=r[idx,subjects]
       total+=(c.gamma**t)*own
       if t==0:immediate=own.clone()
       else:later+=(c.gamma**t)*own
    def reshape(x):return x.reshape(c.batch,n).detach().cpu().numpy()
    return dict(total=reshape(total),initial=reshape(immediate),future=reshape(later))

def causal(name,worlds=6,horizon=48,device='cpu'):
    gift,role,spec=load(name,device)
    outcomes=[]
    for topology,init in (("ring","monolith"),("ring","random"),
                          ("rewired","monolith"),("ring","balanced")):
      c=C(n=spec["n"],k=4,degree=6,topology=topology,batch=worlds,
           horizon=horizon,cost=spec["cost"],gamma=spec["gamma"],device=device)
      for mode in ("normal","no_history"):
        records=[]
        for seed in SEEDS:
          yes=force_one(c,gift,role,seed,init,mode,1,
                         interval=spec["role_interval"],move_cost=spec["move_cost"])
          no=force_one(c,gift,role,seed,init,mode,0,
                        interval=spec["role_interval"],move_cost=spec["move_cost"])
          delta={key:yes[key]-no[key] for key in yes}
          if spec["settlement"]=="unilateral":
             assert np.max(np.abs(delta["initial"]+spec["cost"]))<1e-5
          records.append(dict(seed=seed,per_person={
              key:array.mean(0).tolist() for key,array in delta.items()}))
        tot=np.asarray([x["per_person"]["total"] for x in records])
        instant=np.asarray([x["per_person"]["initial"] for x in records])
        row=dict(model=name,topology=topology,init=init,mode=mode,
           mean_total=float(tot.mean()),
           mean_initial=float(instant.mean()),
           mean_future=float(tot.mean()-instant.mean()),
           positive_agents=int((tot.mean(0)>0).sum()),
           per_agent=tot.mean(0).tolist(),by_seed=records)
        outcomes.append(row)
        print("V30_CAUSAL",name,topology,init,mode,
          "TOTAL",round(row["mean_total"],4),
          "IMMEDIATE",round(row["mean_initial"],4),
          "POS",row["positive_agents"],"/",spec["n"],flush=True)
    target=ROOT/"results"/("v30_causal_"+name+".json")
    target.write_text(json.dumps(dict(model=name,settlement=spec["settlement"],
      worlds_per_seed=worlds,steps=horizon,seeds=SEEDS,rows=outcomes,
      caveat="Force first OFFER vs no offer. Under mutual settlement unmatched offers cost zero and matching gives both sides goods; private causal effects differ structurally from unilateral gifts."),indent=1),encoding="utf8")
    print("V30_CAUSAL_DONE",name,len(outcomes),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--kind",choices=("holdout","causal"),required=True)
    p.add_argument("--worlds",type=int,default=8)
    p.add_argument("--steps",type=int,default=48)
    p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
    a=p.parse_args()
    torch.set_num_threads(2)
    spec=json.loads((ROOT/"runs"/a.name/"v25_spec.json").read_text("utf8"))
    assert spec["settlement"] in ("mutual","unilateral")
    install(spec["settlement"])
    if a.kind=="holdout":
      holdout(a.name,worlds=a.worlds,horizon=a.steps,device=a.device)
    else:causal(a.name,worlds=a.worlds,horizon=a.steps,device=a.device)
if __name__=="__main__":main()
