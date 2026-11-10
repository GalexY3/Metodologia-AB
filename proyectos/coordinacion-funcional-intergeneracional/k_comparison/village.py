"""Experimental village: 10 professions, personal reward, no global census for actors.

N is divisible by 4; each job's productive optimum is N/4.
All 10 jobs are interchangeable. Each agent independently learns a policy,
with its own weights, memory, individual food reward, and optional messages.
No global distance, population counts or counterfactual food enters the actor.
"""
from __future__ import annotations
import argparse, json, math, os, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Categorical

JOBS=10
SYMBOLS=5  # silence (0) + four uninterpreted symbols
FEATURES=10+10+5+3  # own job, neighbor frequencies, messages, food, delta, time
ROOT=Path(__file__).resolve().parent

def network(n:int,degree:int,topology:str,seed:int=19) -> np.ndarray:
    assert n>degree>0 and n%2==0
    assert degree%2==0 or degree==5
    edges=set()
    for u in range(n):
        for step in range(1,degree//2+1):
            v=(u+step)%n
            edges.add(tuple(sorted((u,v))))
        if degree%2:
            edges.add(tuple(sorted((u,(u+n//2)%n))))
    if topology=="rewired":
        rng=np.random.default_rng(seed)
        # Degree-preserving, undirected edge swap, avoiding multi-edges and self-edges.
        for _ in range(50*n):
            a,b=tuple(sorted(rng.choice(len(edges),size=2,replace=False)))
            es=sorted(edges)
            x,y=es[a];v,w=es[b]
            if len({x,y,v,w})<4:continue
            if rng.random()<.5:
                candidate=((min(x,w),max(x,w)),(min(v,y),max(v,y)))
            else:
                candidate=((min(x,v),max(x,v)),(min(y,w),max(y,w)))
            if candidate[0] in edges or candidate[1] in edges or candidate[0]==candidate[1]:continue
            edges.remove(es[a]);edges.remove(es[b])
            edges.add(candidate[0]);edges.add(candidate[1])
    elif topology!="ring":
        raise ValueError("topology must be ring or rewired")
    neighbors=[[] for _ in range(n)]
    for a,b in edges:
        neighbors[a].append(b);neighbors[b].append(a)
    assert all(len(x)==degree for x in neighbors)
    return np.array([sorted(x) for x in neighbors],dtype=np.int64)

def food_of_memberships(colors:torch.Tensor,n:int,k:int=4) -> tuple[torch.Tensor,torch.Tensor]:
    b=colors.shape[0]
    counts=torch.zeros(b,JOBS,device=colors.device)
    counts.scatter_add_(1,colors,torch.ones_like(colors,dtype=torch.float32))
    per=counts.gather(1,colors)
    q=n/k
    foods=torch.minimum(per/q,q/per.clamp_min(1))
    return foods,counts

def measures(colors:torch.Tensor,food:torch.Tensor,counts:torch.Tensor,k:int=4,prev:Optional[torch.Tensor]=None) -> dict:
    n=colors.shape[1];q=n/k
    top=torch.topk(counts,k,dim=1).values
    d=(1-top.clamp(max=q).sum(1)/n)
    return {
        "food_mean":float(food.mean()),
        "food_min":float(food.min()),
        "hunger_fraction":float((food<.85).float().mean()),
        "occupied":float((counts>0).sum(1).float().mean()),
        "Dk":float(d.mean()),
        "exact":int((d<1e-8).sum()),
        "worlds":int(colors.shape[0]),
        "churn":float((colors!=prev).float().mean()) if prev is not None else 0.
    }

@dataclass
class Config:
    n:int=36
    k:int=4
    batch:int=32
    horizon:int=30
    hidden:int=12
    degree:int=5
    topology:str="ring"
    communication:bool=False
    blind:bool=False  # Ablation: hide both neighbor states and incoming symbols.
    gamma:float=.97
    lr:float=.0015
    entropy:float=.012
    device:str="cpu"
    seed:int=1411

class Village:
    def __init__(self,cfg:Config,seed:int):
        torch.manual_seed(seed)
        self.cfg=cfg
        self.graph=torch.as_tensor(network(cfg.n,cfg.degree,cfg.topology,seed=cfg.seed+7),
                                   dtype=torch.long,device=cfg.device)
        self.colors=torch.randint(JOBS,(cfg.batch,cfg.n),device=cfg.device)
        self.food,self.counts=food_of_memberships(self.colors,cfg.n,cfg.k)
        self.prev_food=self.food.clone()
        self.messages=torch.zeros(cfg.batch,cfg.n,dtype=torch.long,device=cfg.device)
        self.t=0
    def observations(self) -> torch.Tensor:
        nb=self.colors[:,self.graph]
        local=F.one_hot(nb,JOBS).float().mean(2)
        incoming=F.one_hot(self.messages[:,self.graph],SYMBOLS).float().mean(2)
        if self.cfg.blind:
            local=torch.zeros_like(local)
            incoming=torch.zeros_like(incoming)
        return torch.cat((
            F.one_hot(self.colors,JOBS).float(),local,incoming,
            self.food[...,None],(self.food-self.prev_food)[...,None],
            torch.full_like(self.food[...,None],self.t/self.cfg.horizon)
            ),dim=-1)
    def advance(self,new:torch.Tensor,msg:torch.Tensor) -> torch.Tensor:
        oldfood=self.food
        self.colors=new
        self.prev_food=oldfood
        self.food,self.counts=food_of_memberships(new,self.cfg.n,self.cfg.k)
        self.messages=msg if self.cfg.communication else torch.zeros_like(msg)
        self.t+=1
        return self.food

class IndividualRNN(nn.Module):
    """No cross-agent trainable matrices. A distinct tanh-RNN for every actor."""
    def __init__(self,n:int,hidden:int):
        super().__init__()
        self.n,self.hidden=n,hidden
        self.win=nn.Parameter(torch.randn(n,FEATURES,hidden)/math.sqrt(FEATURES))
        self.wrec=nn.Parameter(torch.randn(n,hidden,hidden)/math.sqrt(hidden)*.45)
        self.bias=nn.Parameter(torch.zeros(n,hidden))
        self.wa=nn.Parameter(torch.randn(n,hidden,JOBS+1)/math.sqrt(hidden)*.14)
        self.ba=nn.Parameter(torch.zeros(n,JOBS+1))
        self.wm=nn.Parameter(torch.randn(n,hidden,SYMBOLS)/math.sqrt(hidden)*.14)
        self.bm=nn.Parameter(torch.zeros(n,SYMBOLS))
        self.memory=None
    def reset(self,b,device):
        self.memory=torch.zeros(b,self.n,self.hidden,device=device)
    def choose(self,obs:torch.Tensor,colors:torch.Tensor,communication:bool,greedy=False):
        if self.memory is None or self.memory.shape[0]!=obs.shape[0]:
            self.reset(obs.shape[0],obs.device)
        h=torch.tanh(torch.einsum("bnf,nfh->bnh",obs,self.win)+
                     torch.einsum("bnh,nhq->bnq",self.memory,self.wrec)+self.bias)
        self.memory=h
        acts=Categorical(logits=torch.einsum("bnh,nha->bna",h,self.wa)+self.ba)
        action=acts.logits.argmax(-1) if greedy else acts.sample()
        new=torch.where(action==JOBS,colors,action)
        logp=acts.log_prob(action);ent=acts.entropy()
        if communication:
            m=Categorical(logits=torch.einsum("bnh,nhs->bns",h,self.wm)+self.bm)
            symbol=m.logits.argmax(-1) if greedy else m.sample()
            logp=logp+m.log_prob(symbol);ent=ent+m.entropy()
        else:
            symbol=torch.zeros_like(colors)
        return new,symbol,logp,ent

def rollout(model:Optional[IndividualRNN],cfg:Config,seed:int,greedy=False,
            baseline="model",record=False,with_grad=True):
    e=Village(cfg,seed)
    if model is not None:model.reset(cfg.batch,cfg.device)
    logs=[];ents=[];rs=[];snapshot=[]
    def collect():
        v=measures(e.colors,e.food,e.counts,cfg.k)
        if record:
            snapshot.append(dict(t=e.t,colors=e.colors[0].cpu().tolist(),
                 counts=e.counts[0].int().cpu().tolist(),
                 food=float(e.food[0].mean()),Dk=float(1-torch.minimum(
                 torch.topk(e.counts[0],cfg.k).values,torch.tensor(cfg.n/cfg.k,device=e.counts.device)).sum()/cfg.n)))
        return v
    first=collect()
    last=first
    for t in range(cfg.horizon):
        old=e.colors.clone()
        if baseline=="model":
            new,msg,lp,en=model.choose(e.observations(),e.colors,cfg.communication,greedy)
            if with_grad: logs.append(lp);ents.append(en)
        elif baseline=="random":
            new=torch.randint(JOBS,e.colors.shape,device=cfg.device)
            msg=torch.zeros_like(new)
        elif baseline=="frozen":
            new=e.colors;msg=torch.zeros_like(new)
        elif baseline=="imitate":
            # Copies a random observed neighbor, no access to rewards of neighbors.
            ix=torch.randint(cfg.degree,(cfg.batch,cfg.n,1),device=cfg.device)
            neighbor=e.graph[None].expand(cfg.batch,-1,-1).gather(2,ix).squeeze(-1)
            new=e.colors.gather(1,neighbor)
            msg=torch.zeros_like(new)
        else: raise ValueError(baseline)
        r=e.advance(new,msg)
        rs.append(r.detach())
        last=collect()
        last["churn"]=float((old!=new).float().mean())
    return dict(initial=first,final=last,rewards=torch.stack(rs),
         logprobs=logs,entropies=ents,frames=snapshot)

def update(model,opt,cfg,seed):
    r=rollout(model,cfg,seed)
    running=torch.zeros(cfg.batch,cfg.n,device=cfg.device)
    returns=[]
    for reward in reversed(r["rewards"]):
        running=reward+cfg.gamma*running
        returns.append(running)
    returns=torch.stack(list(reversed(returns)))
    mu=(returns.sum(dim=1,keepdim=True)-returns)/(cfg.batch-1)
    scale=returns.std(dim=1,keepdim=True,unbiased=False).clamp_min(.5)
    adv=((returns-mu)/scale).detach()
    lp=torch.stack(r["logprobs"])
    entropy=torch.stack(r["entropies"])
    loss=-(lp*adv).mean()-cfg.entropy*entropy.mean()
    opt.zero_grad(set_to_none=True)
    loss.backward()
    norm=torch.zeros(cfg.n,device=cfg.device)
    for p in model.parameters():
        if p.grad is not None:norm+=p.grad.detach().reshape(cfg.n,-1).square().sum(1)
    norm=norm.sqrt()
    for p in model.parameters():
        if p.grad is not None:
            factor=(1/(norm+1e-8)).clamp(max=1).reshape(cfg.n,*([1]*(p.ndim-1)))
            p.grad.mul_(factor)
    opt.step()
    return dict(loss=float(loss.detach()),train_food=r["final"]["food_mean"],
         train_Dk=r["final"]["Dk"],grad=float(norm.mean()),entropy=float(entropy.detach().mean()))

@torch.no_grad()
def evaluate(model,cfg,seed,batch=48,horizon=40,baseline="model",greedy=True,record=True):
    cf=Config(**{**asdict(cfg),"batch":batch,"horizon":horizon})
    result=rollout(model,cf,seed,greedy=greedy,baseline=baseline,
                   record=record,with_grad=False)
    return {k:result[k] for k in ("initial","final","frames")}

def atomic_json(path,obj):
    temp=Path(str(path)+".tmp")
    temp.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding="utf-8")
    os.replace(temp,path)

def run(args):
    if args.k not in (2,4):raise ValueError("comparison only tests k=2 or k=4")
    if args.n%args.k or args.n<12:raise ValueError("n must be divisible by k and >=12")
    if args.batch<4:raise ValueError("batch must be >= 4")
    torch.set_num_threads(min(3,os.cpu_count() or 2))
    cfg=Config(n=args.n,k=args.k,batch=args.batch,horizon=args.horizon,
               hidden=args.hidden,degree=args.degree,topology=args.topology,
               communication=args.communication,blind=args.blind,lr=args.lr,entropy=args.entropy,
               seed=args.seed,device=args.device)
    folder=ROOT/"runs"/args.name;folder.mkdir(parents=True,exist_ok=True)
    torch.manual_seed(cfg.seed)
    model=IndividualRNN(cfg.n,cfg.hidden).to(cfg.device)
    opt=torch.optim.Adam(model.parameters(),lr=cfg.lr)
    setup={"version":"k_comparison_1","config":asdict(cfg),
           "updates":args.updates,"eval_seed":args.eval_seed,
           "eval_every":args.eval_every}
    configfile=folder/"config.json"
    if configfile.exists():
        existing=json.loads(configfile.read_text(encoding="utf-8"))
        existing.get("config",{}).setdefault("blind",False)  # Backward compatibility for first pilots.
        if existing!=setup:
            raise ValueError("run exists with different settings")
    atomic_json(configfile,setup)
    ck=folder/"latest.pt";start=0
    if ck.exists():
        st=torch.load(ck,map_location=cfg.device,weights_only=False)
        model.load_state_dict(st["model"]);opt.load_state_dict(st["optimizer"])
        start=st["update"]
        torch.random.set_rng_state(st["rng"])
    def save(u):
        temp=Path(str(ck)+".tmp")
        torch.save(dict(update=u,model=model.state_dict(),
                        optimizer=opt.state_dict(),rng=torch.random.get_rng_state()),temp)
        os.replace(temp,ck)
    control=folder/"control.json"
    if not control.exists():atomic_json(control,dict(stop=False))
    history=folder/"history.jsonl"
    t0=time.time()
    def status(u,state,extra=None):
        atomic_json(folder/"status.json",dict(update=u,
             episodes=u*cfg.batch,state=state,elapsed=time.time()-t0,
             report=extra))
    if start>=args.updates:
        prev=json.loads(history.read_text(encoding="utf-8").splitlines()[-1]) if history.exists() else {}
        status(start,"completed",prev)
        print("Run already completed",args.name,"at",start,flush=True)
        return
    status(start,"training")
    for u in range(start+1,args.updates+1):
        if json.loads(control.read_text(encoding="utf-8")).get("stop",False):
            save(u-1);status(u-1,"stopped");break
        row=update(model,opt,cfg,cfg.seed+7919*u)
        if u==1 or u%args.eval_every==0 or u==args.updates:
            ev=evaluate(model,cfg,args.eval_seed,batch=args.eval_batch,
                        horizon=args.eval_horizon,record=True,greedy=False)
            eg=evaluate(model,cfg,args.eval_seed,batch=args.eval_batch,
                        horizon=args.eval_horizon,record=False,greedy=True)
            row.update(update=u,episodes=u*cfg.batch,
                stochastic=ev["final"],greedy=eg["final"])
            with history.open("a",encoding="utf-8") as f:f.write(json.dumps(row)+"\n")
            atomic_json(folder/"replay.json",dict(
                arm=args.name,degree=cfg.degree,n=cfg.n,
                frames=ev["frames"],label="trained stochastic, single development world"))
            status(u,"training",row)
            print(args.name,u,"food",round(ev["final"]["food_mean"],4),
              "Dk",round(ev["final"]["Dk"],4),
              "exact",ev["final"]["exact"],"occ",round(ev["final"]["occupied"],2),
              "hunger",round(ev["final"]["hunger_fraction"],3),
              "greedy",round(eg["final"]["food_mean"],3),flush=True)
        if u%args.checkpoint_every==0 or u==args.updates:save(u)
    else:status(args.updates,"completed",row)

def parse():
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--n",type=int,default=36)
    p.add_argument("--k",type=int,default=4)
    p.add_argument("--degree",type=int,default=5)
    p.add_argument("--topology",choices=["ring","rewired"],default="ring")
    p.add_argument("--communication",action="store_true")
    p.add_argument("--blind",action="store_true")
    p.add_argument("--updates",type=int,default=80)
    p.add_argument("--batch",type=int,default=32)
    p.add_argument("--horizon",type=int,default=30)
    p.add_argument("--hidden",type=int,default=12)
    p.add_argument("--seed",type=int,default=1411)
    p.add_argument("--eval-seed",type=int,default=450001)
    p.add_argument("--eval-batch",type=int,default=48)
    p.add_argument("--eval-horizon",type=int,default=48)
    p.add_argument("--eval-every",type=int,default=10)
    p.add_argument("--checkpoint-every",type=int,default=10)
    p.add_argument("--lr",type=float,default=.0015)
    p.add_argument("--entropy",type=float,default=.012)
    p.add_argument("--device",default="cpu",choices=["cpu","cuda"])
    return p.parse_args()

if __name__=="__main__":run(parse())
