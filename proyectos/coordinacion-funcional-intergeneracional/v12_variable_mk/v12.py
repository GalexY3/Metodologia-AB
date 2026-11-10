"""Variable-profession/variable-optimum individual-learning village.

One joint experiment with heterogeneous tasks (M professions, k sustainable).
No agent sees k, q=N/k, counts, D_k or counterfactual rewards.
All training rewards are realized PERSONAL food, optionally + alpha*realized G.
Communication (C1) is a voluntary, neural proposal of a profession
communicated to each neighbor BEFORE the simultaneous profession change.
Proposals have pre-defined meaning, not an emergent symbolic language.
Parameters of different agents are disjoint; color scorer shared only WITHIN
an agent across candidate occupations, permitting variable M.
"""
from __future__ import annotations
import argparse, json, math, random, time, os, hashlib
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Categorical

ROOT=Path(__file__).resolve().parent

@dataclass
class Config:
    n:int=60
    m:int=10
    k:int=2
    degree:int=5
    hidden:int=8
    communication:bool=False
    public:bool=False
    blind:bool=False
    alpha:float=0.0
    gamma:float=.97
    lr:float=.008
    entropy:float=.006
    topology:str='ring'
    init:str='random' # random or trap
    batch:int=32
    horizon:int=24
    device:str='cpu'
    seed:int=20261111


def validate(c:Config):
    if not (2<=c.k<=c.m<=80):raise ValueError('require 2<=k<=m<=80')
    if c.n%c.k:raise ValueError('N must be divisible by k for exact quota')
    if c.n<12 or c.n%2:raise ValueError('N must be even and >=12')
    if not 1<=c.degree<c.n:raise ValueError('invalid degree')
    if c.degree%2 and c.n%2:raise ValueError('odd degree requires even n')
    if c.init not in ('random','trap'):raise ValueError('invalid init')
    if not 0<=c.alpha<1:raise ValueError('alpha range')


def graph(n:int,degree:int,topology:str,seed:int) -> np.ndarray:
    rng=np.random.default_rng(seed)
    edges=set()
    for a in range(n):
        for j in range(1,degree//2+1):
            b=(a+j)%n
            edges.add((min(a,b),max(a,b)))
        if degree%2:
            b=(a+n//2)%n
            edges.add((min(a,b),max(a,b)))
    if topology=='rewired':
        for _ in range(12*n):
            e=list(edges)
            i,j=rng.choice(len(e),2,replace=False)
            a,b=e[i];c,d=e[j]
            if len({a,b,c,d})<4:continue
            v=(min(a,d),max(a,d));w=(min(c,b),max(c,b))
            if v in edges or w in edges or v==w:continue
            edges.remove(e[i]);edges.remove(e[j]);edges.add(v);edges.add(w)
    elif topology!='ring':raise ValueError('topology ring or rewired')
    adj=[set() for _ in range(n)]
    for a,b in edges:adj[a].add(b);adj[b].add(a)
    assert all(len(x)==degree for x in adj),(n,degree,[len(x) for x in adj])
    return np.array([sorted(v) for v in adj],dtype=np.int64)


def food(jobs:torch.Tensor,m:int,k:int):
    b,n=jobs.shape
    counts=torch.zeros((b,m),device=jobs.device,dtype=torch.float32)
    counts.scatter_add_(1,jobs,torch.ones_like(jobs,dtype=torch.float32))
    size=counts.gather(1,jobs)
    q=n/k
    payoff=torch.minimum(size/q,q/size.clamp_min(1))
    return payoff,counts


def metrics(jobs,foods,counts,k,previous=None):
    n=jobs.shape[1]
    top=counts.topk(k,dim=1).values
    D=1-top.clamp(max=n/k).sum(dim=1)/n
    exact=(D.abs()<1e-6)
    return dict(food=float(foods.mean()),food_std=float(foods.mean(dim=1).std(unbiased=False)),
      d=float(D.mean()),exact=int(exact.sum()),worlds=int(jobs.shape[0]),
      occupied=float((counts>0).sum(dim=1).float().mean()),
      hungry=float((foods<.85).float().mean()),
      churn=float((jobs!=previous).float().mean()) if previous is not None else 0.,
      viable=float(((counts>=.85*n/k)&(counts<=n/(.85*k))).float().sum(dim=1).mean()))


class World:
    def __init__(self,c:Config,seed:int):
        validate(c)
        torch.manual_seed(seed)
        self.c=c;self.t=0
        self.adj=torch.as_tensor(graph(c.n,c.degree,c.topology,seed=seed+8888),device=c.device)
        if c.init=='random':
            self.jobs=torch.randint(c.m,(c.batch,c.n),device=c.device)
        else:
            # Trap: k2 1 monopoly; k4 2 equally occupied; more generally
            # concentrate on floor(k/2) jobs. Labels randomized EACH world.
            occupied=max(1,c.k//2)
            self.jobs=torch.empty(c.batch,c.n,dtype=torch.long,device=c.device)
            for b in range(c.batch):
                labels=torch.randperm(c.m,device=c.device)[:occupied]
                order=torch.randperm(c.n,device=c.device)
                self.jobs[b,order]=labels[torch.arange(c.n,device=c.device)%occupied]
        self.food,self.counts=food(self.jobs,c.m,c.k)
        self.lastfood=self.food.clone()
        self.global_now=self.food.mean(dim=1)
        self.global_before=self.global_now.clone()
    def local(self):
        if self.c.blind:
            return torch.zeros(self.c.batch,self.c.n,self.c.m,device=self.c.device)
        return F.one_hot(self.jobs[:,self.adj],num_classes=self.c.m).float().mean(2)
    def reception(self,intentions):
        if self.c.blind:return torch.zeros(self.c.batch,self.c.n,self.c.m,device=self.c.device)
        return F.one_hot(intentions[:,self.adj],num_classes=self.c.m).float().mean(2)
    def advance(self,jobs):
        self.lastfood=self.food
        self.global_before=self.global_now
        self.jobs=jobs
        self.food,self.counts=food(jobs,self.c.m,self.c.k)
        self.global_now=self.food.mean(dim=1)
        self.t+=1
        return self.food


class IndividualAgent(nn.Module):
    """Independent agent weights, but color-equivariant per-candidate scoring.

    Action features [local,ema,own,received,food,delta,public_G,public_dG].
    Announcement features [local,ema,own,food]. No global oracle and no k.
    Network has no state identifier, so works at any number M>=k.
    """
    def __init__(self,n:int,h:int=8):
        super().__init__()
        self.n=n;self.h=h
        def params(prefix,d):
            setattr(self,prefix+'W',nn.Parameter(torch.randn(n,d,h)/math.sqrt(d)*.7))
            setattr(self,prefix+'b',nn.Parameter(torch.zeros(n,h)))
            setattr(self,prefix+'v',nn.Parameter(torch.randn(n,h)/math.sqrt(h)*.2))
        params('a',8)
        params('s',4)
        self.ema=None
    def reset(self):self.ema=None
    def _score(self,x,p):
        W,b,v=(getattr(self,x+key) for key in ('W','b','v'))
        return torch.einsum('bnmh,nh->bnm',
            torch.tanh(torch.einsum('bnmd,ndh->bnmh',p,W)+b[None,:,None,:]),v)
    def act(self,e:World,greedy=False,disable_messages=False,alter_messages=False):
        cfg=e.c
        loc=e.local()
        if self.ema is None or self.ema.shape!=loc.shape:
            self.ema=loc.detach()
        self.ema=(.70*self.ema+.30*loc).detach()
        own=F.one_hot(e.jobs,cfg.m).float()
        fr=e.food[...,None].expand(-1,-1,cfg.m)
        dfr=(e.food-e.lastfood)[...,None].expand(-1,-1,cfg.m)
        sg=sdg=torch.zeros_like(fr)
        if cfg.public:
            sg=e.global_now[:,None,None].expand_as(fr)
            sdg=(e.global_now-e.global_before)[:,None,None].expand_as(fr)
        logmsg=0;emsg=0;rcv=torch.zeros_like(fr)
        if cfg.communication and not disable_messages:
            score_msg=self._score('s',torch.stack([loc,self.ema,own,fr],-1))
            dist_msg=Categorical(logits=score_msg)
            intent=score_msg.argmax(-1) if greedy else dist_msg.sample()
            logmsg=dist_msg.log_prob(intent)
            emsg=dist_msg.entropy()
            if alter_messages:
                # Shuffles among worlds, destroying sender-receiver information
                intent=intent.roll(1,dims=0)
            rcv=e.reception(intent)
        feats=torch.stack([loc,self.ema,own,rcv,fr,dfr,sg,sdg],dim=-1)
        logits=self._score('a',feats)
        dist=Categorical(logits=logits)
        choice=logits.argmax(-1) if greedy else dist.sample()
        return choice,dist.log_prob(choice)+logmsg,dist.entropy()+emsg


def rollout(model:IndividualAgent|None,c:Config,seed:int,baseline='learned',greedy=False,
    record=False,disable_messages=False,alter_messages=False):
    env=World(c,seed)
    if model is not None:model.reset()
    initial=metrics(env.jobs,env.food,env.counts,c.k)
    logs=[];ents=[];rewards=[];frames=[]
    def snap():
        if record:
            frames.append(dict(t=env.t,states=env.jobs[0].detach().cpu().tolist(),
                counts=env.counts[0].int().detach().cpu().tolist(),
                food=float(env.food[0].mean()),k=c.k,m=c.m))
    snap()
    last=initial
    for t in range(c.horizon):
        old=env.jobs
        if baseline=='learned':
            nxt,lp,ent=model.act(env,greedy=greedy,disable_messages=disable_messages,
                alter_messages=alter_messages)
            logs.append(lp);ents.append(ent)
        elif baseline=='random':nxt=torch.randint(c.m,env.jobs.shape,device=c.device)
        elif baseline=='frozen':nxt=env.jobs
        elif baseline=='imitate':
            idx=torch.randint(c.degree,(c.batch,c.n,1),device=c.device)
            neighbor=env.adj[None].expand(c.batch,-1,-1).gather(2,idx).squeeze(2)
            nxt=env.jobs.gather(1,neighbor)
        else:raise ValueError(baseline)
        r=env.advance(nxt)
        rewards.append((1-c.alpha)*r+c.alpha*env.global_now[:,None])
        snap()
    last=metrics(env.jobs,env.food,env.counts,c.k,previous=old)
    return dict(initial=initial,final=last,logs=logs,ents=ents,rewards=rewards,frames=frames)


def train_step(model,opt,c:Config,seed:int):
    result=rollout(model,c,seed)
    rs=torch.stack(result['rewards']) # (T,B,N), realized after actions
    ret=torch.zeros_like(rs[0]);R=[]
    for r in rs.flip(0):
        ret=r+c.gamma*ret
        R.append(ret)
    R=torch.stack(R[::-1])
    # Other worlds, same agent, same task => no centralized critic.
    baseline=(R.sum(1,keepdim=True)-R)/(c.batch-1)
    std=R.std(dim=1,keepdim=True,unbiased=False).clamp_min(.20)
    advantage=((R-baseline)/std).detach()
    lp=torch.stack(result['logs'])
    entropy=torch.stack(result['ents'])
    loss=-(lp*advantage).mean()-c.entropy*entropy.mean()
    opt.zero_grad(set_to_none=True)
    loss.backward()
    # Clip each actor independently, not shared-gradient aggregation.
    norms=torch.zeros(c.n,device=c.device)
    for p in model.parameters():
        if p.grad is not None:norms+=p.grad.detach().reshape(c.n,-1).square().sum(1)
    norms=norms.sqrt()
    with torch.no_grad():
        factors=(2/(norms+1e-10)).clamp(max=1)
        for p in model.parameters():
            if p.grad is not None:p.grad.mul_(factors.reshape(c.n,*([1]*(p.ndim-1))))
    opt.step()
    return dict(loss=float(loss.detach()),grad=float(norms.mean()),entropy=float(entropy.mean().detach()),
        food=result['final']['food'],d=result['final']['d'])

@torch.no_grad()
def evaluate(model,c,seed,batch=64,horizon=40,baseline='learned',greedy=False,
         disable_messages=False,alter_messages=False,record=False):
    cfg=replace(c,batch=batch,horizon=horizon)
    return rollout(model,cfg,seed,baseline,greedy,record,disable_messages,alter_messages)


def write_json(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,p)


def parse():
    p=argparse.ArgumentParser()
    p.add_argument('--name',required=True)
    p.add_argument('--n',type=int,default=60)
    p.add_argument('--m-train',default='10,20')
    p.add_argument('--k-train',default='2,4')
    p.add_argument('--degree',type=int,default=5)
    p.add_argument('--topology',choices=['ring','rewired'],default='ring')
    p.add_argument('--communication',action='store_true')
    p.add_argument('--public',action='store_true')
    p.add_argument('--blind',action='store_true')
    p.add_argument('--alpha',type=float,default=0.)
    p.add_argument('--init',choices=['random','trap'],default='random')
    p.add_argument('--updates',type=int,default=500)
    p.add_argument('--batch',type=int,default=32)
    p.add_argument('--horizon',type=int,default=24)
    p.add_argument('--eval-horizon',type=int,default=40)
    p.add_argument('--eval-batch',type=int,default=48)
    p.add_argument('--eval-every',type=int,default=50)
    p.add_argument('--save-every',type=int,default=100)
    p.add_argument('--lr',type=float,default=.008)
    p.add_argument('--entropy',type=float,default=.006)
    p.add_argument('--seed',type=int,default=3111)
    p.add_argument('--device',choices=['cpu','cuda'],default='cpu')
    return p.parse_args()

def run(args):
    torch.set_num_threads(min(4,os.cpu_count() or 2))
    train_m=list(map(int,args.m_train.split(',')))
    train_k=list(map(int,args.k_train.split(',')))
    if len(train_m)*len(train_k)<1:raise ValueError('train set empty')
    tasks=[(m,k) for m in train_m for k in train_k if m>=k and args.n%k==0]
    if not tasks:raise ValueError('no valid tasks for N')
    out=ROOT/'runs'/args.name
    out.mkdir(parents=True,exist_ok=True)
    cfg=Config(n=args.n,degree=args.degree,topology=args.topology,
      communication=args.communication,public=args.public,blind=args.blind,
      alpha=args.alpha,init=args.init,lr=args.lr,entropy=args.entropy,
      batch=args.batch,horizon=args.horizon,device=args.device,seed=args.seed)
    setup=dict(name=args.name,tasks=tasks,config=asdict(cfg),updates=args.updates,
        eval_horizon=args.eval_horizon,eval_batch=args.eval_batch,
        eval_every=args.eval_every,save_every=args.save_every,model='color-equivariant-128-parameter')
    config=out/'config.json'
    if config.exists() and json.loads(config.read_text('utf-8'))!=setup:raise RuntimeError('existing run config mismatch')
    write_json(config,setup)
    torch.manual_seed(args.seed)
    model=IndividualAgent(args.n).to(args.device)
    params=sum(p.numel() for p in model.parameters())
    print('MODEL',args.name,'params',params,'per_agent',params//args.n,flush=True)
    opt=torch.optim.Adam(model.parameters(),lr=args.lr)
    checkpoint=out/'latest.pt';start=0
    if checkpoint.exists():
        st=torch.load(checkpoint,map_location=args.device,weights_only=False)
        model.load_state_dict(st['model']);opt.load_state_dict(st['optimizer']);start=int(st['update'])
    ctl=out/'control.json'
    if not ctl.exists():write_json(ctl,{'stop':False})
    def save(i):
        tmp=out/'checkpoint.tmp'
        torch.save(dict(update=i,model=model.state_dict(),optimizer=opt.state_dict()),tmp)
        os.replace(tmp,checkpoint)
    rng=random.Random(args.seed+123456)
    history=out/'history.jsonl'
    rows=[]
    if history.exists():rows=[json.loads(s) for s in history.read_text('utf-8').splitlines() if s.strip()]
    t0=time.monotonic()
    for u in range(start+1,args.updates+1):
        if json.loads(ctl.read_text('utf-8')).get('stop',False):
            save(u-1);write_json(out/'status.json',dict(state='stopped',update=u-1));return
        # Deterministic task schedule random order seeded independently of model RNG.
        m,k=tasks[(u-1)%len(tasks)]
        c=replace(cfg,m=m,k=k)
        result=train_step(model,opt,c,args.seed+u*977)
        if u==1 or u%args.eval_every==0 or u==args.updates:
            ev={}
            # Familiar (train) and two forms of unseen generalization.
            tests=[('train_k2_m10',10,2),('train_k4_m20',20,4),
                   ('new_k3_m20',20,3),('new_k5_m30',30,5),('new_k6_m30',30,6),
                   ('new_k2_m30',30,2)]
            for label,tm,tk in tests:
                if args.n%tk:continue
                ec=replace(cfg,m=tm,k=tk,init='random')
                x=evaluate(model,ec,args.seed+900000+tm*100+tk,batch=args.eval_batch,
                           horizon=args.eval_horizon)
                ev[label]=x['final']
            row=dict(update=u,trained_on=f'M{m}/k{k}',train=result,evaluations=ev)
            with history.open('a',encoding='utf-8') as fh:fh.write(json.dumps(row)+'\n')
            write_json(out/'status.json',dict(state='training',update=u,elapsed_sec=time.monotonic()-t0,summary=row))
            first=ev.get('train_k2_m10',{})
            gen=ev.get('new_k5_m30',{})
            print('UPDATE',args.name,u,'knownFood',round(first.get('food',-1),4),
                 'knownD',round(first.get('d',-1),4),'knownExact',first.get('exact'),
                 'newFood',round(gen.get('food',-1),4),'newExact',gen.get('exact'),flush=True)
        if u%args.save_every==0 or u==args.updates:save(u)
    write_json(out/'status.json',dict(state='completed',update=args.updates,
              elapsed_sec=time.monotonic()-t0,last=row))

if __name__=='__main__':run(parse())
