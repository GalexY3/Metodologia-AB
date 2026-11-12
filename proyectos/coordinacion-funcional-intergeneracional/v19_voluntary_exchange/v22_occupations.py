"""V22 exploratory learned occupational switches with V21 frozen gift policy.

Individuals choose role switches privately; no target quotas, external
occupational planner, pooled reward, behavioral teacher, or shared weights.
The costly-gift actor was learned previously from each actor's own food,
is frozen, and must be disclosed as a pretraining intervention.
"""
from __future__ import annotations
import json,argparse,time,os
from pathlib import Path
import torch,numpy as np
from torch import nn
from torch.distributions import Bernoulli
from targeted_gifts import C,create,step
from audit_targeted import load
ROOT=Path(__file__).resolve().parent

class PrivateOccupationActor(nn.Module):
    def __init__(self,n=24,hidden=20):
        super().__init__()
        self.n=n
        self.W=nn.Parameter(torch.randn(n,10,hidden)*.075)
        self.b=nn.Parameter(torch.zeros(n,hidden))
        self.v=nn.Parameter(torch.randn(n,hidden)*.075)
        self.bias=nn.Parameter(torch.full((n,),-1.0))
    def act(self,c,w,interval=8,greedy=False):
        graph=w["graph"]
        roles=w["roles"]
        neighbor=roles[:,graph]
        complement=(neighbor!=roles[:,:,None]).float().mean(2)
        same=1-complement
        prev_offer=w["prev_gift"][:,graph].float().mean(2)
        prior_help=w["trust"].float().mean(2)
        own_last=w["lastfood"]
        own_prev=w["prev_gift"]
        own_switch=w["last_switch"]
        timefrac=torch.full_like(own_last,w["t"]/max(1,c.horizon))
        # Role identity permits independent actors to break occupational symmetry
        # but does not supply a target role, quota or global occupation counts.
        own_role=roles.float()
        one=torch.ones_like(own_last)
        f=torch.stack((complement,same,prev_offer,prior_help,
                own_last,own_prev,own_switch,timefrac,own_role,one),2)
        h=torch.tanh(torch.einsum("bnf,nfh->bnh",f,self.W)+self.b[None,:,:])
        logits=torch.einsum("bnh,nh->bn",h,self.v)+self.bias[None,:]
        dist=Bernoulli(logits=logits)
        action=(logits>0).float() if greedy else dist.sample()
        return action,dist.log_prob(action),dist.entropy()

def start(c,seed,init="mixed"):
    w=create(c,seed)
    gen=torch.Generator(device=c.device)
    gen.manual_seed(seed+1661007)
    mono=torch.randint(2,(c.batch,1),device=c.device,generator=gen)
    group=torch.bernoulli(torch.full((c.batch,c.n),.5,device=c.device),
                generator=gen).long()
    if init=="mixed":
        monoworld=(torch.arange(c.batch,device=c.device)%2==0)
        roles=torch.where(monoworld[:,None],mono,group)
    elif init=="monolith": roles=mono.expand(c.batch,c.n).clone()
    elif init=="random":roles=group
    elif init=="alternating":roles=w["roles"]
    else:raise ValueError(init)
    w["roles"]=roles
    w["last_switch"]=torch.zeros(c.batch,c.n,device=c.device)
    return w

def rollout(c,gifts,occup,seed,init="mixed",role_interval=8,
            switch_cost=.015,baseline=None,social="normal",greedy=False,
            save_gradient=True):
    w=start(c,seed,init)
    g=c.degree
    rews=[];rl=[];rents=[];switchcounts=[];giftcounts=[]
    mean_food=[];mean_complement=[]
    for t in range(c.horizon):
        if t%role_interval==0:
            if baseline=="fixed":
                switch=torch.zeros(c.batch,c.n,device=c.device)
                lp=ent=None
            elif baseline=="random":
                switch=(torch.rand(c.batch,c.n,device=c.device)<.15).float()
                lp=ent=None
            else:
                assert occup is not None
                switch,lp,ent=occup.act(c,w)
            w["roles"]=torch.remainder(w["roles"]+switch.long(),2)
            w["last_switch"]=switch
            switchcounts.append(switch)
            if lp is not None:
                rl.append((t,lp))
                rents.append(ent)
        dest,gift,_,_=gifts.act(c,w,mode=social,greedy=greedy)
        reward=step(c,w,dest,gift)
        if t%role_interval==0:
            reward=reward-switch_cost*switch
            w["lastfood"]=reward
        rews.append(reward)
        giftcounts.append(gift.mean())
        mean_food.append(reward.mean().detach())
        mean_complement.append((w["roles"][:,w["graph"]]!=w["roles"][:,:,None]).float().mean().detach())
    finalrole=w["roles"]
    counts=(finalrole==0).sum(1).float()
    links=(finalrole[:,w["graph"]]!=finalrole[:,:,None]).float().mean((1,2))
    metrics=dict(mean_food=float(torch.stack(mean_food).mean()),
         final_food=float(rews[-1].mean()),
         gift=float(torch.stack(giftcounts).mean()),
         opposite_links=float(links.mean()),
         role_zero=float(counts.mean()),
         exactly_balanced=float((counts==c.n//2).float().mean()),
         mean_switches_per_agent=float(torch.stack(switchcounts).sum(0).mean()),
         final_role_variability=float((counts*(c.n-counts)).mean()/((c.n/2)**2)),
         worlds=c.batch)
    return metrics,rl,rents,rews

def evaluate(role_actor,gift_actor,device,switch_cost,interval,seed=897110):
    rows=[]
    for degree,topology in ((2,"ring"),(2,"rewired"),(4,"ring")):
        for init in ("monolith","random"):
            c=C(n=gift_actor.n,k=2,degree=degree,topology=topology,
                batch=32,horizon=48,cost=.12,gamma=.995,device=device)
            for label,actor,base,social in (
              ("learned",role_actor,None,"normal"),
              ("no_social",role_actor,None,"no_social"),
              ("fixed",None,"fixed","normal"),
              ("random_switch",None,"random","normal")):
                torch.manual_seed(seed+degree*100+(init=="random")*17)
                m,*_=rollout(c,gift_actor,actor,seed+degree*100+(init=="random")*17,
                  init=init,role_interval=interval,switch_cost=switch_cost,
                  baseline=base,social=social,save_gradient=False)
                rows.append(dict(degree=degree,topology=topology,init=init,
                                condition=label,**m))
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--gift-source",required=True)
    p.add_argument("--seed",type=int,default=3111)
    p.add_argument("--updates",type=int,default=600)
    p.add_argument("--batch",type=int,default=24)
    p.add_argument("--horizon",type=int,default=48)
    p.add_argument("--hidden",type=int,default=20)
    p.add_argument("--role-interval",type=int,default=8)
    p.add_argument("--switch-cost",type=float,default=.015)
    p.add_argument("--entropy",type=float,default=.01)
    p.add_argument("--lr",type=float,default=.003)
    p.add_argument("--eval-every",type=int,default=150)
    p.add_argument("--device",choices=("cuda","cpu"),default="cuda")
    a=p.parse_args()
    assert a.batch>=2 and a.horizon%a.role_interval==0
    torch.set_num_threads(2)
    torch.manual_seed(a.seed);np.random.seed(a.seed)
    folder=ROOT/"runs"/a.name;folder.mkdir(parents=True,exist_ok=False)
    (folder/"v22_spec.json").write_text(json.dumps(vars(a),indent=2),encoding="utf8")
    gifts,spec,epoch=load(a.gift_source,a.device)
    gifts.eval().requires_grad_(False)
    role=PrivateOccupationActor(gifts.n,a.hidden).to(a.device)
    optim=torch.optim.Adam(role.parameters(),lr=a.lr)
    t0=time.perf_counter()
    for u in range(1,a.updates+1):
        c=C(n=gifts.n,k=2,degree=2,topology="ring",
            batch=a.batch,horizon=a.horizon,cost=spec["cost"],
            gamma=spec["gamma"],device=a.device)
        metrics,roles,ent,rewards=rollout(c,gifts,role,a.seed*19301+u*31,
              init="mixed",role_interval=a.role_interval,switch_cost=a.switch_cost)
        rr=torch.stack(rewards)
        G=torch.zeros_like(rr[0])
        ret=[]
        for reward in reversed(rr):
            G=reward+c.gamma*G
            ret.append(G)
        R=torch.stack(ret[::-1])
        lps=torch.stack([logprob for t,logprob in roles])
        vals=torch.stack([R[t] for t,logprob in roles])
        leave=(vals.sum(1,keepdim=True)-vals)/(a.batch-1)
        adv=((vals-leave)/vals.std(1,unbiased=False,keepdim=True).clamp_min(.25)).detach()
        loss=-(lps*adv).mean()-a.entropy*torch.stack(ent).mean()
        optim.zero_grad(set_to_none=True)
        loss.backward()
        norms=torch.zeros(c.n,device=a.device)
        for pval in role.parameters():
            if pval.grad is not None:
                norms+=pval.grad.detach().reshape(c.n,-1).square().sum(1)
        with torch.no_grad():
            scale=(2/(norms.sqrt()+1e-10)).clamp(max=1)
            for pval in role.parameters():
                if pval.grad is not None:
                    pval.grad.mul_(scale.reshape(c.n,*([1]*(pval.ndim-1))))
        optim.step()
        if u==1 or u%a.eval_every==0 or u==a.updates:
            with torch.no_grad():
                v=evaluate(role,gifts,a.device,a.switch_cost,a.role_interval)
            row=dict(update=u,train=metrics,loss=float(loss.detach()),
                     dev=v,elapsed=time.perf_counter()-t0)
            with (folder/"v22_history.jsonl").open("a",encoding="utf8") as fh:
                fh.write(json.dumps(row)+"\n")
            tmp=folder/"role_tmp.pt"
            torch.save(dict(model=role.state_dict(),optimizer=optim.state_dict(),
               update=u,gift_source=a.gift_source),tmp)
            os.replace(tmp,folder/"role_latest.pt")
            sample=[z for z in v if z["degree"]==2 and z["topology"]=="ring"
                         and z["init"]=="monolith"]
            print("V22",a.name,"u",u,
                 [(z["condition"],round(z["mean_food"],4),
                   round(z["opposite_links"],3),round(z["exactly_balanced"],3),
                   round(z["mean_switches_per_agent"],3)) for z in sample],
                 "elapsed",round(time.perf_counter()-t0,1),flush=True)
    (folder/"role_status.json").write_text(json.dumps(
        dict(state="completed",updates=a.updates,elapsed_seconds=time.perf_counter()-t0)))
    print("V22_FINISHED",a.name,flush=True)
if __name__=="__main__":main()
