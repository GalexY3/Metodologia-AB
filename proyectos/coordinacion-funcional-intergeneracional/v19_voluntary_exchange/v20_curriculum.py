"""V20 exploratory test: path-dependence in voluntary directed donations.

Preregistered comparison: constant-high cost vs smooth/abrupt escalation.
All gradients use only each individual's discounted food; actors are private.
No shared parameters, teacher, policy cloning, or group-level reward.
Development seeds are separate from frozen audit_targeted.py holdout seeds.
"""
from __future__ import annotations
import argparse, json, math, os, time
from pathlib import Path
import numpy as np
import torch
from targeted_gifts import C, PrivateGiftActor, simulate
from train_targeted import evaluate

ROOT=Path(__file__).resolve().parent

def parse():
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--seed",type=int,required=True)
    p.add_argument("--schedule",choices=("constant","smooth","abrupt"),required=True)
    p.add_argument("--updates",type=int,default=800)
    p.add_argument("--n",type=int,default=24)
    p.add_argument("--hidden",type=int,default=20)
    p.add_argument("--init-scale",type=float,default=8.0)
    p.add_argument("--cost",type=float,default=.12)
    p.add_argument("--low-cost",type=float,default=.01)
    p.add_argument("--gamma",type=float,default=.995)
    p.add_argument("--lr",type=float,default=.002)
    p.add_argument("--entropy",type=float,default=.015)
    p.add_argument("--batch",type=int,default=16)
    p.add_argument("--horizon",type=int,default=32)
    p.add_argument("--eval-every",type=int,default=200)
    p.add_argument("--topology",choices=("ring","mixed"),default="ring")
    p.add_argument("--social",type=int,choices=(0,1),default=1)
    p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
    return p.parse_args()

def cost_at(a,u):
    if a.schedule=="constant":return a.cost
    transition=a.updates*2//3
    if a.schedule=="abrupt":return a.low_cost if u<=transition else a.cost
    t=max(0.0,min(1.0,(u-1)/max(1,transition-1)))
    return a.low_cost+(a.cost-a.low_cost)*t

def main():
    a=parse()
    assert 0<a.low_cost<=a.cost<=.2 and a.n%2==0 and a.batch>=2
    torch.set_num_threads(2)
    torch.manual_seed(a.seed)
    np.random.seed(a.seed)
    folder=ROOT/"runs"/a.name
    folder.mkdir(parents=True,exist_ok=False)
    spec=vars(a).copy()
    (folder/"v20_spec.json").write_text(json.dumps(spec,indent=2),encoding="utf8")
    # Compatible with V19 causal auditor: the frozen policy is assessed at the target cost.
    (folder/"targeted_spec.json").write_text(json.dumps({
      "n":a.n,"hidden":a.hidden,"init_scale":a.init_scale,"cost":a.cost,
      "gamma":a.gamma,"schedule":a.schedule,"seed":a.seed,
    },indent=2),encoding="utf8")
    actor=PrivateGiftActor(a.n,a.hidden,a.init_scale).to(a.device)
    optimizer=torch.optim.Adam(actor.parameters(),lr=a.lr)
    t0=time.perf_counter()
    for u in range(1,a.updates+1):
        cost=cost_at(a,u)
        topo=("ring" if (u//2)%2 else "rewired") if a.topology=="mixed" else "ring"
        c=C(n=a.n,k=2,degree=2,topology=topo,
            batch=a.batch,horizon=a.horizon,cost=cost,gamma=a.gamma,
            device=a.device,social=bool(a.social))
        metrics,logs,ents,rews=simulate(c,actor,a.seed*19301+31*u)
        reward=torch.stack(rews)
        G=torch.zeros_like(reward[0])
        R=[]
        for r in reversed(reward):
            G=r+a.gamma*G
            R.append(G)
        R=torch.stack(R[::-1])
        leave=(R.sum(dim=1,keepdim=True)-R)/(a.batch-1)
        adv=((R-leave)/R.std(dim=1,unbiased=False,keepdim=True).clamp_min(.25)).detach()
        loss=-(torch.stack(logs)*adv).mean()-a.entropy*torch.stack(ents).mean()
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        norm=torch.zeros(a.n,device=a.device)
        for p in actor.parameters():
            if p.grad is not None:
                norm+=p.grad.detach().reshape(a.n,-1).square().sum(dim=1)
        with torch.no_grad():
            scale=(2/(norm.sqrt()+1e-10)).clamp(max=1)
            for p in actor.parameters():
                if p.grad is not None:
                    p.grad.mul_(scale.reshape(a.n,*([1]*(p.ndim-1))))
        optimizer.step()
        if u==1 or u%a.eval_every==0 or u==a.updates:
            high,_=evaluate(actor,a.device,a.cost,seed=947001,batch=16,horizon=48)
            current,_=evaluate(actor,a.device,cost,seed=947001,batch=12,horizon=32)
            row=dict(update=u,training_cost=cost,train_food=metrics["food"],
                train_gift=metrics["gift"],loss=float(loss.detach()),
                high_cost=high,current_cost=current,
                elapsed_seconds=time.perf_counter()-t0)
            with (folder/"v20_history.jsonl").open("a",encoding="utf8") as f:
                f.write(json.dumps(row)+"\n")
            torch.save(dict(model=actor.state_dict(),optimizer=optimizer.state_dict(),
                      update=u,rng_cpu=torch.get_rng_state(),
                      rng_gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None),
                      folder/"targeted_latest.pt")
            tr=high["trained_normal"]
            abl=high["trained_no_social"]
            ood=high["ood_normal"]
            print("V20",a.name,"u",u,"cost",round(cost,3),
                "train",round(metrics["food"],4),"gift",round(metrics["gift"],4),
                "HIGH_FOOD",round(tr["food"],4),"HIGH_GIFT",round(tr["gift"],4),
                "HIGH_NO_SOCIAL",round(abl["food"],4),
                "HIGH_OOD",round(ood["food"],4),
                "elapsed",round(time.perf_counter()-t0,1),flush=True)
    (folder/"targeted_status.json").write_text(json.dumps(dict(
      state="completed",updates=a.updates,elapsed_seconds=time.perf_counter()-t0)),encoding="utf8")
    print("V20_DONE",a.name,flush=True)

if __name__=="__main__":
    main()
