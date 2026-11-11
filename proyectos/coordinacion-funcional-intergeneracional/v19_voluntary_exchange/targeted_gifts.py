"""V19-D: voluntary directed gifts in a repeated social dilemma.

No mandatory reciprocity, collective reward, behavioral teacher, or shared
parameters between individuals. Each independently learned person chooses:
 (a) which specific social neighbor to target; (b) whether to give.
Giving has an immediate private cost and can ONLY benefit the recipient.
Receiving depends on the neighbor's actual targeted gift, not one's own.
The next round, actors locally observe WHO helped them, allowing
learned conditional reciprocity or learned free-riding.
"""
from __future__ import annotations
import math,torch,numpy as np
from torch import nn
from torch.distributions import Categorical,Bernoulli
from exchange import make_graph
from dataclasses import dataclass

@dataclass(frozen=True)
class C:
    n:int=24
    k:int=2
    degree:int=2
    topology:str='ring'
    batch:int=24
    horizon:int=48
    cost:float=.12
    gamma:float=.99
    device:str='cuda'
    social:bool=True
    warm:float=0.0  # exogenous prehistory, not taught policy

def create(c,seed):
    graph=make_graph(c.n,c.degree,c.topology,seed,c.device)
    gen=torch.Generator(device=c.device)
    gen.manual_seed(seed)
    shift=torch.randint(c.k,(c.batch,1),device=c.device,generator=gen)
    roles=(torch.arange(c.n,device=c.device)[None,:]%c.k+shift)%c.k
    w=dict(graph=graph,roles=roles,
      prev_gift=torch.zeros(c.batch,c.n,device=c.device),
      prev_recipient=torch.full((c.batch,c.n),-1,device=c.device,dtype=torch.long),
      incoming=torch.zeros(c.batch,c.n,c.degree,device=c.device),
      lastfood=torch.full((c.batch,c.n),.2,device=c.device),
      t=0,full=torch.zeros(c.batch,c.n,device=c.device),
      cover=torch.zeros(c.batch,c.n,device=c.device))
    if c.warm>0:
        assert 0<=c.warm<=1
        prev=(torch.rand(c.batch,c.n,device=c.device,generator=gen)<c.warm).float()
        slots=torch.randint(c.degree,(c.batch,c.n),device=c.device,generator=gen)
        prevdest=graph[None,:,:].expand(c.batch,-1,-1).gather(2,slots[:,:,None]).squeeze(2)
        past_received=((prevdest[:,graph]==torch.arange(c.n,device=c.device)[None,:,None])&
                       (prev[:,graph]>.5)).float()
        goods=(torch.nn.functional.one_hot(roles[:,graph],c.k).float()*
               past_received[:,:,:,None]).sum(2)>0
        own=torch.nn.functional.one_hot(roles,c.k).bool()
        d=(goods&(~own)).sum(2).float()
        full=(d>=c.k-1).float()
        w['prev_gift']=prev
        w['prev_recipient']=prevdest
        w['incoming']=past_received
        w['cover']=d/(c.k-1)
        w['full']=full
        w['lastfood']=.2+.55*w['cover']+.25*full-c.cost*prev
    return w

class PrivateGiftActor(nn.Module):
    def __init__(self,n=24,hidden=20,scale=8):
        super().__init__()
        self.n=n
        # No parameters are shared between two distinct persons.
        self.target_W=nn.Parameter(torch.randn(n,9,hidden)*(.05*scale))
        self.target_b=nn.Parameter(torch.zeros(n,hidden))
        self.target_v=nn.Parameter(torch.randn(n,hidden)*(.05*scale))
        self.gift_W=nn.Parameter(torch.randn(n,9,hidden)*(.05*scale))
        self.gift_b=nn.Parameter(torch.zeros(n,hidden))
        self.gift_v=nn.Parameter(torch.randn(n,hidden)*(.05*scale))
        self.gift_bias=nn.Parameter(torch.randn(n)*.4)
    def act(self,c,w,mode='normal',greedy=False):
        graph=w['graph'];b,n=w['roles'].shape;deg=c.degree
        neighbors=w['roles'][:,graph]
        complementary=(neighbors!=w['roles'][:,:,None]).float()
        prior_help=w['incoming']
        prior_offer=w['prev_gift'][:,graph]
        prior_target=(w['prev_recipient'][:,:,None]==graph[None,:,:]).float()
        if mode=='no_social' or not c.social:
            prior_help=prior_help*0
            prior_offer=prior_offer*0
        elif mode=='scramble':
            # Preserve donors' marginal behavior, corrupt identity-specific
            # recipient credit assignment.
            flip=torch.randperm(n,device=c.device)
            prior_help=prior_help[:,flip,:]
            prior_offer=prior_offer[:,flip,:]
        elif mode!='normal':raise ValueError(mode)
        scalar=lambda x:x[:,:,None].expand(-1,-1,deg)
        ownlast=scalar(w['lastfood'])
        ownprev=scalar(w['prev_gift'])
        lastreceived=scalar((prior_help.sum(2)>0).float())
        T=torch.full_like(prior_help,float(w['t']/c.horizon))
        reciprocal_signal=prior_help
        f=torch.stack([complementary,reciprocal_signal,prior_offer,
           prior_target,ownlast,ownprev,lastreceived,T,
           torch.full_like(T,float(c.k/12))],dim=-1)
        hidden=torch.tanh(torch.einsum('bnjf,nfh->bnjh',f,self.target_W)+
                           self.target_b[None,:,None,:])
        target_logits=torch.einsum('bnjh,nh->bnj',hidden,self.target_v)
        target_dist=Categorical(logits=target_logits)
        slot=target_logits.argmax(2) if greedy else target_dist.sample()
        gather=slot[:,:,None]
        dest=graph[None,:,:].expand(b,-1,-1).gather(2,gather).squeeze(2)
        selected=f.gather(2,slot[:,:,None,None].expand(-1,-1,1,f.shape[-1])).squeeze(2)
        gifthidden=torch.tanh(torch.einsum('bnf,nfh->bnh',
                   selected,self.gift_W)+self.gift_b[None,:,:])
        gift_logits=torch.einsum('bnh,nh->bn',gifthidden,self.gift_v)+self.gift_bias[None,:]
        gift_dist=Bernoulli(logits=gift_logits)
        gift=(gift_logits>0).float() if greedy else gift_dist.sample()
        lp=gift_dist.log_prob(gift)+gift*target_dist.log_prob(slot)
        entropy=gift_dist.entropy()+gift*target_dist.entropy()
        return dest,gift,lp,entropy

def step(c,w,dest,gift):
    n=c.n;g=w['graph'];b=gift.shape[0]
    nbrgift=gift[:,g]
    nbrdest=dest[:,g]
    incoming=((nbrdest==torch.arange(n,device=c.device)[None,:,None])&
              (nbrgift>.5)).float()
    role_of_sender=w['roles'][:,g]
    onehot=torch.nn.functional.one_hot(role_of_sender,c.k).float()
    goods=(onehot*incoming[:,:,:,None]).sum(2)>0
    own=torch.nn.functional.one_hot(w['roles'],c.k).bool()
    useful=(goods&(~own))
    distinct=useful.sum(2).float()
    cover=distinct/(c.k-1)
    full=(distinct>=c.k-1).float()
    food=.20+.55*cover+.25*full-c.cost*gift
    w['incoming']=incoming
    w['prev_gift']=gift
    w['prev_recipient']=dest
    w['lastfood']=food
    w['full']=full
    w['cover']=cover
    w['t']+=1
    return food

def simulate(c,actor,seed,mode='normal',baseline=None,greedy=False,watch=False):
    w=create(c,seed)
    log=[];entropies=[];rewards=[]
    give_probs=[];event=0;event_possible=0
    for t in range(c.horizon):
        previous_in=w['incoming']
        if baseline:
            dest=w['graph'][None,:,:].expand(c.batch,-1,-1).gather(2,
                torch.randint(c.degree,(c.batch,c.n,1),device=c.device)).squeeze(2)
            if baseline=='always':gift=torch.ones(c.batch,c.n,device=c.device)
            elif baseline=='never':gift=torch.zeros(c.batch,c.n,device=c.device)
            elif baseline=='random':gift=(torch.rand(c.batch,c.n,device=c.device)<.5).float()
            elif baseline=='titfortat':
                # Explicit baseline, NOT a neural learner.
                incoming_per_neighbor=w['incoming']
                any_receipt=incoming_per_neighbor.sum(2)>0
                which=incoming_per_neighbor.argmax(2)
                dest=torch.where(any_receipt,
                    w['graph'][None,:,:].expand(c.batch,-1,-1).gather(2,which[:,:,None]).squeeze(2),
                    dest)
                gift=torch.where(any_receipt,
                    torch.ones_like(w['prev_gift']),
                    (torch.rand(c.batch,c.n,device=c.device)<.5).float())
            else:raise ValueError(baseline)
            lp=entropy=None
        else:
            dest,gift,lp,entropy=actor.act(c,w,mode,greedy)
        r=step(c,w,dest,gift)
        rewards.append(r)
        if lp is not None:
            log.append(lp)
            entropies.append(entropy)
        if watch:
            available=(previous_in.sum(2)>0)
            event+=float(gift[available].sum()) if bool(available.any()) else 0
            event_possible+=int(available.sum())
            give_probs.append(float(gift.mean()))
    data=dict(food=float(w['lastfood'].mean()),
       gift=float(w['prev_gift'].mean()),
       coverage=float(w['cover'].mean()),
       full=float(w['full'].mean()),worlds=c.batch,
       mean_gift_trajectory=float(np.mean(give_probs)) if give_probs else None,
       gift_if_previously_received=event/event_possible if event_possible else None)
    return data,log,entropies,rewards

if __name__=='__main__':
    c=C(n=24,k=2,degree=2,device='cpu',batch=3,horizon=3)
    m=PrivateGiftActor(24,16)
    z=simulate(c,m,151);print('TARGETED_SMOKE',z[0])
