"""V30 voluntary pairwise contracts; same V25 cold-start actors and REINFORCE.

To settle a *pair* both parties must explicitly propose to one another
in the same round. No unilateral losses or transfers: unmatched offers cost
zero. Environment provides only a contract settlement rule, no learned
teacher, coordination plan, profession quota or shared return.
"""
from __future__ import annotations
import argparse,json,torch
from pathlib import Path
import v25_multi_capacity as base
from targeted_gifts import C
from v24_k4_joint import start4

ORIGINAL_STEP=base.step_multi
ORIGINAL_ROLL=base.roll
ORIGINAL_ARGS=base.args
ORIGINAL_EVAL=base.evaluate
OBSERVATIONS=[]

def settle(c,w,dests,gifts,contract=True):
    b,n,kminus=dests.shape
    assert c.k-1==kminus and gifts.shape==(b,n,kminus)
    mask=gifts>.5
    # A person may offer several slots to the same partner. Only one
    # agreement per undirected pair can be liquidated in a round.
    proposal=torch.zeros(b,n,n,device=c.device,dtype=torch.float32)
    proposal.scatter_add_(2,dests,gifts)
    offered=proposal>0
    mutual=offered & offered.transpose(1,2)
    actual=mutual if contract else offered
    # The unilateral training control must use the original step to
    # preserve duplicate unit transfers (not this deduplicated matrix).
    if not contract:
        reward,distinct=ORIGINAL_STEP(c,w,dests,gifts)
        emitted=gifts.sum(2)
    else:
        emitted=actual.float().sum(2)
        graph=w["graph"]
        incoming=actual.gather(2,graph[None,:,:].expand(b,-1,-1)).float()
        goods=(torch.nn.functional.one_hot(w["roles"][:,graph],c.k).float()
                *incoming[:,:,:,None]).sum(2)>0
        own=torch.nn.functional.one_hot(w["roles"],c.k).bool()
        distinct=(goods & (~own)).sum(2).float()
        cover=distinct/(c.k-1)
        full=(distinct>=c.k-1).float()
        reward=.2+.55*cover+.25*full-c.cost*emitted
        w["incoming"]=incoming
        w["trust"]=torch.maximum(incoming,c.memory_decay*w["trust"])
        w["prev_gift"]=(emitted>0).float()
        w["prev_recipient"]=dests[:,:,0]
        w["lastfood"]=reward
        w["cover"]=cover
        w["full"]=full
        w["t"]+=1
    # No gradients needed for observation statistics.
    OBSERVATIONS.append((float(gifts.sum().detach()),float(emitted.sum().detach()),
       float(distinct.sum().detach())))
    return reward,distinct

def contract_step(c,w,dests,gifts):
    return settle(c,w,dests,gifts,contract=True)
def control_step(c,w,dests,gifts):
    return settle(c,w,dests,gifts,contract=False)

def traced_roll(*args,**kwargs):
    OBSERVATIONS.clear()
    metrics,*rest=ORIGINAL_ROLL(*args,**kwargs)
    proposals=sum(x[0] for x in OBSERVATIONS)
    accepted=sum(x[1] for x in OBSERVATIONS)
    distinct=sum(x[2] for x in OBSERVATIONS)
    periods=sum(x.shape[0] for x in [rest[0]])*args[0].batch*args[0].n
    # rest[0] is [time,batch,n] reward tensor.
    periods=rest[0].numel()
    metrics["proposals_per_person"]=proposals/periods
    metrics["settled_units_per_person"]=accepted/periods
    metrics["acceptance_fraction"]=accepted/proposals if proposals else 0.
    metrics["physical_useful_ratio"]=distinct/accepted if accepted else 0.
    return (metrics,*rest)

def oracle_contract(c,seed=401):
    assert c.k==4 and c.degree==6 and c.topology=="ring"
    w=start4(c,seed,"balanced")
    i=torch.arange(c.n,device=c.device)[None,:,None]
    # Reciprocated neighbours: i +/- 1, and symmetric matching over +/- 2.
    third=torch.where((torch.arange(c.n,device=c.device)//2)%2==0,
                      torch.full((c.n,),2,device=c.device),
                      torch.full((c.n,),-2,device=c.device))
    offsets=torch.stack([torch.ones(c.n,device=c.device,dtype=torch.long),
           -torch.ones(c.n,device=c.device,dtype=torch.long),third],dim=1)
    dests=((torch.arange(c.n,device=c.device)[:,None]+offsets)%c.n)[None,:,:].expand(c.batch,-1,-1)
    offers=torch.ones(c.batch,c.n,3,device=c.device)
    r,_=contract_step(c,w,dests,offers)
    assert bool((w["full"]==1).all()),("oracular settlement missed",w["full"].mean())
    return dict(food=float(r.mean()),full=float(w["full"].mean()),
                cover=float(w["cover"].mean()),count=3.)

def original_oracle(c,seed=401):
    return base_original_oracle(c,seed)
base_original_oracle=base.oracle

def add_args():
    p=ORIGINAL_ARGS()
    p.add_argument("--settlement",choices=("mutual","unilateral"),required=True)
    return p

def install(mode):
    assert mode in ("mutual","unilateral")
    base.args=add_args
    base.step_multi=contract_step if mode=="mutual" else control_step
    base.roll=traced_roll
    base.oracle=oracle_contract if mode=="mutual" else base_original_oracle

if __name__=="__main__":
    p=argparse.ArgumentParser(add_help=False,allow_abbrev=False)
    p.add_argument("--settlement",choices=("mutual","unilateral"),required=True)
    args,_=p.parse_known_args()
    install(args.settlement)
    base.main()
