"""V20 preregistered audit extension: intervene in ALL 24 private agents.

Vectorizes focus-person interventions over the batch dimension, preserving
paired random numbers per treatment and equal world initializations. This
fixes V19 auditor's even-index selection bias (all one profession at k=2).
No optimization occurs; all actor weights are frozen.
"""
from __future__ import annotations
import argparse,json,time
from dataclasses import replace
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C,create,step
from audit_targeted import load,SEEDS
ROOT=Path(__file__).resolve().parent
BATCH_KEYS=("roles","prev_gift","prev_recipient","incoming",
            "trust","lastfood","full","cover")

@torch.no_grad()
def forced(c,actor,seed,mode,condition):
    n=c.n
    fullc=replace(c,batch=c.batch*n)
    torch.manual_seed(seed*41+211)
    original=create(c,seed)
    w={"graph":original["graph"],"t":0}
    for key in BATCH_KEYS:
        w[key]=original[key].repeat_interleave(n,dim=0)
    focus=torch.arange(n,device=c.device).repeat(c.batch)
    row=torch.arange(fullc.batch,device=c.device)
    ret=torch.zeros(fullc.batch,device=c.device)
    immediate=None
    next_gifts=None
    next_incoming=None
    for t in range(c.horizon):
        dest,gift,_,_=actor.act(fullc,w,mode)
        if t==0:
            gift=gift.clone()
            gift[row,focus]=float(condition)
        reward=step(fullc,w,dest,gift)[row,focus]
        ret+=c.gamma**t*reward
        if t==0: immediate=reward.clone()
        if t==1:
            next_gifts=gift[row,focus].clone()
            next_incoming=w["incoming"][row,focus,:].sum(1).clone()
    assert immediate is not None
    return dict(total=ret.reshape(c.batch,n).cpu().numpy(),
                immediate=immediate.reshape(c.batch,n).cpu().numpy(),
                next_incoming=(next_incoming.reshape(c.batch,n).cpu().numpy() if next_incoming is not None else None),
                next_gifts=(next_gifts.reshape(c.batch,n).cpu().numpy() if next_gifts is not None else None))

@torch.no_grad()
def evaluate_model(name,worlds=32,steps=48,device="cuda"):
    actor,spec,update=load(name,device)
    scenarios=[]
    for k,degree,topology in ((2,2,"ring"),(2,2,"rewired"),(3,2,"ring")):
        c=C(n=actor.n,k=k,degree=degree,topology=topology,
            batch=worlds,horizon=steps,device=device,cost=spec["cost"],gamma=spec["gamma"])
        for mode in ("normal","scramble","no_social"):
            by_seed=[]
            for seed in SEEDS:
                give=forced(c,actor,seed,mode,1)
                refuse=forced(c,actor,seed,mode,0)
                delta={x:give[x]-refuse[x] for x in give if give[x] is not None}
                by_seed.append(dict(seed=seed,worlds=worlds,
                    per_agent_total=delta["total"].mean(axis=0).tolist(),
                    per_agent_immediate=delta["immediate"].mean(axis=0).tolist(),
                    per_agent_next_incoming=delta.get("next_incoming",np.zeros_like(delta["total"])).mean(axis=0).tolist(),
                    per_agent_next_gift=delta.get("next_gifts",np.zeros_like(delta["total"])).mean(axis=0).tolist()))
            agent=np.array([x["per_agent_total"] for x in by_seed])
            row=dict(k=k,topology=topology,degree=degree,mode=mode,
                 worlds=worlds*len(SEEDS),focal_agents=c.n,
                 mean_total=float(agent.mean()),
                 mean_even=float(agent[:,::2].mean()),
                 mean_odd=float(agent[:,1::2].mean()),
                 positive_agents=int((agent.mean(axis=0)>0).sum()),
                 positive_seed_agent_pairs=int((agent>0).sum()),
                 evaluated_seed_agent_pairs=int(agent.size),
                 agent_means=agent.mean(axis=0).tolist(),
                 per_environment_seed=by_seed)
            scenarios.append(row)
            print("V20_ALL_AGENTS",name,k,topology,mode,
                 "return",round(row["mean_total"],4),
                 "EVEN",round(row["mean_even"],4),
                 "ODD",round(row["mean_odd"],4),
                 "pos_agents",row["positive_agents"],"/",c.n,
                 flush=True)
    out=dict(model=name,checkpoint=update,steps=steps,worlds_per_seed=worlds,
             seeds=SEEDS,scenarios=scenarios,
             note="All 24 persons; 6 paired environmental seeds, 32 worlds each; returns grouped by distinct privately learned person and even/odd location.")
    path=ROOT/"results"/("v20_allagents_"+name+".json")
    path.write_text(json.dumps(out,indent=1),encoding="utf8")
    print("V20_ALL_AGENTS_DONE",name,len(scenarios),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--worlds",type=int,default=32)
    p.add_argument("--steps",type=int,default=48)
    p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
    a=p.parse_args()
    torch.set_num_threads(2)
    evaluate_model(a.name,a.worlds,a.steps,a.device)
