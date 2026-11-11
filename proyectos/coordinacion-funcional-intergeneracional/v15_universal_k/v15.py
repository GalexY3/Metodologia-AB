"""V15: independent recurrent actor on task-general primitive actions.

All policy gradients use strictly individual food, with NO global rewards,
global role counts, centralized critic, or foreign agent weights.
Candidate operations: remain, local modal, local least common, local sampled,
uniform anywhere, absent locally, own best historical profession, own previous,
local frequency-proportional sample. Neural selection of options learns
k-conditioning while being permutation-equivariant over profession labels.
"""
from __future__ import annotations
from dataclasses import asdict,replace
from pathlib import Path
import sys,json,random,math,os,time,argparse
import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Categorical
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'v12_variable_mk'))
import v12 as envlib

# Allow fractional target quotas in evaluation; the personal payoff itself
# already supports q=N/k. Training below still uses divisible pairs.
def validate_any_k(c):
    if not (2<=c.k<=min(c.m,c.n) and c.m<=80):
        raise ValueError('2 <= k <= min(M,N), M<=80 required')
    if c.n<12 or c.n%2:raise ValueError('N must be even and >=12')
    if not 1<=c.degree<c.n:raise ValueError('Invalid degree')
    if c.init not in ('random','trap'):raise ValueError('Invalid init')
    if not 0<=c.alpha<1:raise ValueError('Invalid alpha')
envlib.validate=validate_any_k

NFEAT=27
NOPS=9
OPERATIONS=('stay','local_modal','local_minority','random_neighbor',
            'random_profession','locally_absent','best_past','previous_role',
            'neighbor_weighted')
class OptionActor(nn.Module):
    def __init__(self,n,hidden=24,recurrent=True):
        super().__init__()
        self.n=n;self.h=hidden;self.recurrent=recurrent
        self.wx=nn.Parameter(torch.randn(n,NFEAT,hidden)*(.42/math.sqrt(NFEAT)))
        self.wh=nn.Parameter(torch.randn(n,hidden,hidden)*(.28/math.sqrt(hidden)))
        self.bias=nn.Parameter(torch.zeros(n,hidden))
        self.wout=nn.Parameter(torch.randn(n,hidden,NOPS)*(.22/math.sqrt(hidden)))
        self.bout=nn.Parameter(torch.zeros(n,NOPS))
        with torch.no_grad():
            self.bout[:,0]=1.8
            self.bout[:,3]=.2
            self.bout[:,4]=-.5
            self.bout[:,5]=-.6
            self.bout[:,6]=.8
            self.bout[:,7]=.3
        self.reset()
    def reset(self):
        self.ema=None;self.mem=None;self.ema_food=None
        self.lastjobs=None;self.bestjobs=None;self.bestfood=None
        self.tenure=None;self.was_moving=None
    def _features(self,e):
        c=e.c
        b,n=e.jobs.shape
        local=e.local()
        if self.ema is None or self.ema.shape!=local.shape:
            self.ema=local.detach().clone()
            self.ema_food=e.food.clone()
            self.mem=torch.zeros(b,n,self.h,device=c.device)
            self.lastjobs=e.jobs.clone()
            self.bestjobs=e.jobs.clone()
            self.bestfood=e.food.clone()
            self.tenure=torch.zeros(b,n,device=c.device)
            self.was_moving=torch.zeros(b,n,device=c.device)
        self.ema=(.7*self.ema+.3*local).detach()
        self.ema_food=(.8*self.ema_food+.2*e.food).detach()
        improve=e.food>self.bestfood+1e-7
        self.bestjobs=torch.where(improve,e.jobs,self.bestjobs)
        self.bestfood=torch.maximum(e.food,self.bestfood)
        current=local.gather(2,e.jobs[...,None]).squeeze(2)
        oldlocal=self.ema.gather(2,e.jobs[...,None]).squeeze(2)
        loglocal=-torch.where(local>0,local*local.clamp_min(1e-12).log(),torch.zeros_like(local)).sum(-1)/math.log(c.degree)
        unique=(local>0).float().sum(-1)
        minfreq=torch.where(local>0,local,torch.ones_like(local)).min(-1).values
        maxfreq=local.max(-1).values
        ones=((local>0)&(local<1.5/c.degree)).float().sum(-1)/c.degree
        delta=e.food-e.lastfood
        q=c.n/c.k
        def constant(v):return torch.full_like(e.food,float(v))
        inputs=torch.stack([
            e.food,delta,current,oldlocal,maxfreq,minfreq,
            unique/c.degree,loglocal,self.tenure/10,
            self.bestfood,self.bestfood-e.food,self.ema_food,
            constant(c.m/c.n),constant(c.k/c.n),constant(1/c.k),
            constant(math.log(q)/math.log(c.n)),constant(math.log(c.m)/math.log(80)),
            constant(c.k/c.m),ones,constant(e.t/c.horizon),
            current*q,oldlocal*q,
            self.was_moving,(e.food>.85).float(),
            delta*self.was_moving,constant(math.log1p(c.k)),
            constant(math.log1p(c.m/c.k))
        ],dim=-1)
        assert inputs.shape==(b,n,NFEAT)
        return inputs,local
    def _candidates(self,e,local):
        c=e.c;b,n=e.jobs.shape
        random_scores=torch.rand_like(local)
        # Random tie-breaks prevent lowest-index profession privilege.
        modal=(local+random_scores*.00001).argmax(-1)
        local_positive=local>0
        minority=(local+((~local_positive).float()*100)+random_scores*.00001).argmin(-1)
        ix=torch.randint(c.degree,(b,n,1),device=c.device)
        nb=e.adj[None].expand(b,-1,-1).gather(2,ix).squeeze(2)
        nbr=e.jobs.gather(1,nb)
        anywhere=torch.randint(c.m,(b,n),device=c.device)
        masked_random=torch.where(local_positive,torch.full_like(local,-1.),random_scores)
        absent=masked_random.argmax(-1)
        freqweighted=Categorical(probs=local).sample()
        options=torch.stack([e.jobs,modal,minority,nbr,anywhere,absent,
                             self.bestjobs,self.lastjobs,freqweighted],dim=-1)
        assert options.shape==(b,n,NOPS)
        return options
    def act(self,e,greedy=False,disable_messages=False,alter_messages=False):
        inputs,local=self._features(e)
        h=torch.einsum('bnd,ndh->bnh',inputs,self.wx)+self.bias[None,:,:]
        if self.recurrent:
            h=h+torch.einsum('bnh,nhj->bnj',self.mem.detach(),self.wh)
        h=torch.tanh(h)
        self.mem=h.detach()
        logits=torch.einsum('bnh,nhq->bnq',h,self.wout)+self.bout[None,:,:]
        dist=Categorical(logits=logits)
        operation=logits.argmax(-1) if greedy else dist.sample()
        choices=self._candidates(e,local)
        jobs=choices.gather(2,operation[...,None]).squeeze(2)
        moving=jobs!=e.jobs
        self.tenure=torch.where(moving,torch.zeros_like(self.tenure),self.tenure+1).detach()
        self.was_moving=moving.float()
        self.lastjobs=e.jobs.clone()
        return jobs,dist.log_prob(operation),dist.entropy()

def parse():
    p=argparse.ArgumentParser()
    p.add_argument('--name',required=True)
    p.add_argument('--n',type=int,default=120)
    p.add_argument('--train-pairs',default='24:2,24:3,24:4,24:6,24:10,24:15,24:20,80:2,80:4,80:6,80:10,80:15,80:20,80:30,80:40,80:60')
    p.add_argument('--degree',type=int,default=8)
    p.add_argument('--h',type=int,default=24)
    p.add_argument('--no-recurrence',action='store_true')
    p.add_argument('--updates',type=int,default=2500)
    p.add_argument('--batch',type=int,default=16)
    p.add_argument('--horizon',type=int,default=26)
    p.add_argument('--eval-every',type=int,default=100)
    p.add_argument('--save-every',type=int,default=100)
    p.add_argument('--lr',type=float,default=.006)
    p.add_argument('--entropy',type=float,default=.008)
    p.add_argument('--gamma',type=float,default=.97)
    p.add_argument('--seed',type=int,default=3111)
    p.add_argument('--device',choices=('cpu','cuda'),default='cpu')
    return p.parse_args()
def run(args):
    torch.set_num_threads(min(4,os.cpu_count() or 2))
    pairs=[tuple(map(int,t.split(':'))) for t in args.train_pairs.split(',')]
    for m,k in pairs:
        assert 2<=k<=m<=80 and args.n%k==0
    root=HERE/'runs'/args.name
    root.mkdir(parents=True,exist_ok=True)
    cfg=envlib.Config(n=args.n,m=pairs[0][0],k=pairs[0][1],degree=args.degree,
             batch=args.batch,horizon=args.horizon,device=args.device,
             gamma=args.gamma,lr=args.lr,entropy=args.entropy,
             communication=False,public=False,alpha=0.0,blind=False,seed=args.seed)
    design=dict(args=vars(args),pairs=pairs,policy=NOPS,
      independent_per_agent=True,personal_reward_only=True,
      no_privileged_global_information=True,operations=OPERATIONS)
    spec=root/'spec.json'
    if spec.exists() and json.loads(spec.read_text('utf8'))!=design:
        raise RuntimeError('Cannot silently resume with mismatched parameters.')
    envlib.write_json(spec,design)
    torch.manual_seed(args.seed)
    actor=OptionActor(args.n,args.h,recurrent=not args.no_recurrence).to(args.device)
    optimizer=torch.optim.Adam(actor.parameters(),lr=args.lr)
    print('MODEL',args.name,'params',sum(p.numel() for p in actor.parameters()),
          'per_agent',sum(p.numel() for p in actor.parameters())//args.n,
          'recurrent',actor.recurrent,'ops',OPERATIONS,flush=True)
    ck=root/'latest.pt';start=0
    if ck.exists():
        snap=torch.load(ck,map_location=args.device,weights_only=False)
        actor.load_state_dict(snap['model'])
        optimizer.load_state_dict(snap['optimizer'])
        start=int(snap['update'])
    def save(i):
        tmp=root/'latest.tmp'
        torch.save(dict(model=actor.state_dict(),optimizer=optimizer.state_dict(),
                        update=i),tmp)
        os.replace(tmp,ck)
    evalpairs=[(10,2),(24,4),(80,2),(80,5),(80,8),(80,12),
               (80,20),(80,30),(80,40),(80,60),(80,80)]
    started=time.monotonic()
    for u in range(start+1,args.updates+1):
        m,k=pairs[(u-1)%len(pairs)]
        c=replace(cfg,m=m,k=k)
        tr=envlib.train_step(actor,optimizer,c,args.seed+977*u)
        if u==1 or u%args.eval_every==0 or u==args.updates:
            ev={}
            for tm,tk in evalpairs:
                ec=replace(cfg,m=tm,k=tk)
                z=envlib.evaluate(actor,ec,91110+tm*100+tk,
                    batch=24,horizon=64)
                ev[f'M{tm}_k{tk}']=z['final']
            row=dict(update=u,train=dict(m=m,k=k,**tr),eval=ev)
            with (root/'history.jsonl').open('a',encoding='utf8') as fh:
                fh.write(json.dumps(row,ensure_ascii=False)+'\n')
            envlib.write_json(root/'status.json',dict(
                update=u,state='running',elapsed=time.monotonic()-started,
                eval=ev))
            print('UPDATE',args.name,u,'known_k4',round(ev['M24_k4']['food'],4),
              'new_k5',round(ev['M80_k5']['food'],4),
              'new_k12',round(ev['M80_k12']['food'],4),
              'k30',round(ev['M80_k30']['food'],4),
              'k60',round(ev['M80_k60']['food'],4),
              'k80',round(ev['M80_k80']['food'],4),flush=True)
        if u%args.save_every==0 or u==args.updates:save(u)
    envlib.write_json(root/'status.json',dict(update=args.updates,state='completed',
                                            elapsed=time.monotonic()-started,eval=ev))
    print('V15_DONE',args.name,flush=True)
if __name__=='__main__':run(parse())
