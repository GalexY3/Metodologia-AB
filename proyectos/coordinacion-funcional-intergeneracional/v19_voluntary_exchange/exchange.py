"""V19: decentralized role choice and voluntary reciprocal exchange.

N independent role-equivariant MLPs (one distinct parameter set per person).
The environment computes only personal realized consumption:
  reward_i = 0.20 + 0.55*unique_complementary_roles_received/(k-1)
                    + 0.25*all_complementary_roles_received
                    - 0.12*voluntary_offer_i
                    - 0.02*role_switched_i
Roles and offers are simultaneous independent personal decisions.
Reciprocal exchange: goods pass along (i,j) iff BOTH offer. One-way control:
goods pass if sender offers (recipient can free-ride).
No global census or team reward is observed by any policy.
"""
from __future__ import annotations
import math,random,torch,networkx as nx
from dataclasses import dataclass
from torch import nn
from torch.distributions import Categorical,Bernoulli

MAX_K=12
@dataclass(frozen=True)
class Config:
    n:int=60
    k:int=4
    degree:int=10
    topology:str='ring'
    batch:int=16
    horizon:int=24
    device:str='cuda'
    mutual:bool=True
    social:bool=True
    init:str='random'
    gamma:float=.95
    cost:float=.12
    switch_cost:float=.02
    def validate(self):
        assert 2<=self.k<=MAX_K,(self.k,MAX_K)
        assert self.k<=self.n
        assert self.n%self.k==0,(self.n,self.k)
        assert 2<=self.degree<self.n and self.degree%2==0
        assert self.batch>1 and self.horizon>0
        assert self.init in ('random','monolith','half','balanced')
        assert self.topology in ('ring','rewired')

def make_graph(n,degree,topology,seed,device):
    if topology=='ring':
        half=degree//2
        adj=[[((i+j)%n) for j in range(-half,half+1) if j]
             for i in range(n)]
        g=nx.from_numpy_array(__import__('numpy').zeros((1,1))) if False else None
    elif topology=='rewired':
        g=nx.random_regular_graph(degree,n,seed=seed+991)
        adj=[sorted(g.neighbors(i)) for i in range(n)]
    else:raise ValueError(topology)
    a=torch.tensor(adj,device=device,dtype=torch.long)
    assert tuple(a.shape)==(n,degree)
    assert not bool((a==torch.arange(n,device=device)[:,None]).any())
    return a

def create_world(c,seed):
    c.validate()
    gen=torch.Generator(device=c.device)
    gen.manual_seed(seed)
    a=make_graph(c.n,c.degree,c.topology,seed,c.device)
    if c.init=='monolith':
        label=torch.randint(c.k,(c.batch,1),device=c.device,generator=gen)
        roles=label.expand(-1,c.n).clone()
    elif c.init=='half':
        k2=max(1,c.k//2)
        labels=torch.randint(k2,(c.batch,c.n),device=c.device,generator=gen)
        if c.k>1:
            # Random label rotation preserves role-label symmetry.
            shift=torch.randint(c.k,(c.batch,1),device=c.device,generator=gen)
            labels=(labels+shift)%c.k
        roles=labels
    elif c.init=='balanced':
        roles=torch.stack([torch.randperm(c.n,device=c.device,generator=gen)%c.k
            for _ in range(c.batch)])
    else:
        roles=torch.randint(c.k,(c.batch,c.n),device=c.device,generator=gen)
    offers=torch.zeros(c.batch,c.n,device=c.device,dtype=torch.float32)
    rewards=torch.full_like(offers,.2)
    coverage=torch.zeros_like(offers)
    return dict(adj=a,roles=roles,offers=offers,reward=rewards,
      coverage=coverage,full=torch.zeros_like(offers),t=0,gen=gen)

def observe(c,world,mode='normal'):
    b,n=world['roles'].shape
    roles=world['roles']
    neighbor_roles=roles[:,world['adj']]
    neighbor_offers=world['offers'][:,world['adj']]
    counts=torch.nn.functional.one_hot(neighbor_roles,c.k).float().mean(2)
    offered=torch.nn.functional.one_hot(neighbor_roles,c.k).float()
    willing=(offered*neighbor_offers[:,:,:,None]).sum(2)/c.degree
    if mode=='shuffled_social':
        rng=torch.Generator(device=c.device)
        rng.manual_seed(9811+world['t']*71)
        perm=torch.randperm(n,device=c.device,generator=rng)
        counts=counts[:,perm,:]
        willing=willing[:,perm,:]
    if not c.social or mode=='no_social':
        counts=torch.zeros_like(counts)
        willing=torch.zeros_like(willing)
    else:
        counts=counts if mode=='normal' or mode=='shuffled_social' else counts
    idx=torch.arange(c.k,device=c.device)[None,None,:]
    own=(roles[:,:,None]==idx).float()
    present=(willing>1e-6).float()
    features=dict(counts=counts,willing=willing,own=own,
      present=present,reward=world['reward'],
      previous_offer=world['offers'],
      coverage=world['coverage'],
      t=world['t']/c.horizon)
    return features

class IndependentActors(nn.Module):
    def __init__(self,n=60,hidden=20):
        super().__init__()
        self.n=n
        # Every agent has private per-slot role scorer, applied to an
        # arbitrary number of occupations k. NO shared weights across people.
        self.job_w1=nn.Parameter(torch.randn(n,10,hidden)*.05)
        self.job_b1=nn.Parameter(torch.zeros(n,hidden))
        self.job_w2=nn.Parameter(torch.randn(n,hidden)*.05)
        self.job_b2=nn.Parameter(torch.zeros(n))
        self.offer_w1=nn.Parameter(torch.randn(n,9,hidden)*.05)
        self.offer_b1=nn.Parameter(torch.zeros(n,hidden))
        self.offer_w2=nn.Parameter(torch.randn(n,hidden)*.05)
        self.offer_b2=nn.Parameter(torch.zeros(n))
    def act(self,c,world,mode='normal',deterministic=False,force_offer=None,return_logits=False,return_parts=False):
        f=observe(c,world,mode)
        b,n=world['roles'].shape
        k=c.k;K=k-1
        def broad(x):
            return x[:,:,None].expand(-1,-1,k)
        scalar=lambda x:torch.full((b,n,k),float(x),device=c.device)
        local_diversity=f['present'].sum(2)/(max(1,k))
        slot_features=torch.stack((
           f['counts'],f['willing'],f['present'],f['own'],
           broad(f['reward']),broad(f['previous_offer']),
           broad(f['coverage']),broad(local_diversity),
           scalar(k/MAX_K),scalar(f['t'])
        ),dim=-1)
        hidden=torch.tanh(torch.einsum('bnkf,nfh->bnkh',slot_features,self.job_w1)+
            self.job_b1[None,:,None,:])
        logits=torch.einsum('bnkh,nh->bnk',hidden,self.job_w2)+self.job_b2[None,:,None]
        if return_logits:
            return logits
        if deterministic:
            choice=logits.argmax(2)
            logrole=torch.log_softmax(logits,dim=2).gather(2,choice[:,:,None]).squeeze(2)
            entrole=Categorical(logits=logits).entropy()
        else:
            dist=Categorical(logits=logits)
            choice=dist.sample()
            logrole=dist.log_prob(choice)
            entrole=dist.entropy()
        chosen=f['own'].new_zeros(f['own'].shape).scatter(2,choice[:,:,None],1.)
        available=(f['present']*(1-chosen)).sum(2)/K
        willing=(f['willing']*(1-chosen)).sum(2)
        trade_features=torch.stack((
           available,
           willing,
           f['willing'].sum(2),
           f['counts'].sum(2),
           (choice!=world['roles']).float(),
           f['reward'],
           f['previous_offer'],
           f['coverage'],
           torch.full((b,n),k/MAX_K,device=c.device)
        ),dim=2)
        offer_hidden=torch.tanh(torch.einsum('bnf,nfh->bnh',
           trade_features,self.offer_w1)+self.offer_b1[None,:,:])
        offer_logits=torch.einsum('bnh,nh->bn',
           offer_hidden,self.offer_w2)+self.offer_b2[None,:]
        if force_offer is not None:
            offers=torch.full((b,n),float(force_offer),device=c.device)
        elif deterministic:
            offers=(offer_logits>0).float()
        else:
            offers=Bernoulli(logits=offer_logits).sample()
        odist=Bernoulli(logits=offer_logits)
        logoffers=odist.log_prob(offers)
        entropy=entrole+odist.entropy()
        if return_parts:
            return choice,offers,logrole,logoffers,entrole,odist.entropy()
        return choice,offers,logrole+logoffers,entropy

def advance(c,world,roles,offers):
    assert roles.shape==world['roles'].shape
    neigh_roles=roles[:,world['adj']]
    neigh_offers=offers[:,world['adj']]
    contributors=neigh_offers*(offers[:,:,None] if c.mutual else 1.)
    colors=torch.nn.functional.one_hot(neigh_roles,c.k).float()
    received=(colors*contributors[:,:,:,None]).sum(2)>0
    ownmask=torch.nn.functional.one_hot(roles,c.k).bool()
    useful=received&(~ownmask)
    distinct=useful.sum(2).float()
    coverage=distinct/(c.k-1)
    full=(distinct>=c.k-1).float()
    switching=(roles!=world['roles']).float()
    # Food is personal; no aggregate term ever enters the reward.
    reward=.20+.55*coverage+.25*full-c.cost*offers-c.switch_cost*switching
    world['roles']=roles
    world['offers']=offers
    world['reward']=reward
    world['coverage']=coverage
    world['full']=full
    world['t']+=1
    return reward

def metrics(c,world):
    q=c.n//c.k
    counts=torch.nn.functional.one_hot(world['roles'],c.k).sum(1)
    global_error=(counts-q).abs().sum(1).float()/(2*c.n)
    exact=(counts==q).all(1)
    positive=(counts>0).sum(1)
    food=world['reward']
    offer=world['offers']
    mutual_edges=(offer[:,:,None]*offer[:,world['adj']]).sum()/(
       c.batch*c.n*c.degree)
    return dict(food=float(food.mean()),full=float(world['full'].mean()),
      coverage=float(world['coverage'].mean()),
      offer=float(offer.mean()),mutual_edges=float(mutual_edges),
      exact=int(exact.sum()),worlds=c.batch,
      groups=float(positive.float().mean()),
      imbalance=float(global_error.mean()),
      food_inequality=float(food.std(dim=1,unbiased=False).mean()),
      random_baseline_task=dict(n=c.n,k=c.k,degree=c.degree))

def rollout(c,actor,seed,mode='normal',deterministic=False,record=False,
            force_offer=None,random_actor=False):
    world=create_world(c,seed)
    logs=[];ents=[];rewards=[];timefood=[]
    for t in range(c.horizon):
        if random_actor:
            roles=torch.randint(c.k,(c.batch,c.n),device=c.device)
            offers=(torch.rand(c.batch,c.n,device=c.device)<.5).float()
            lp=ent=None
        else:
            roles,offers,lp,ent=actor.act(c,world,mode,deterministic,force_offer)
        r=advance(c,world,roles,offers)
        if lp is not None:
            logs.append(lp);ents.append(ent)
        rewards.append(r)
        if record:timefood.append(float(r.mean()))
    return dict(metrics=metrics(c,world),logs=logs,ents=ents,
                rewards=rewards,history=timefood)
