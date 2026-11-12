"""V29 private target-history correction and factorial training.

Follows V25 training exactly except explicitly declared: target history,
price, degree and the optional no-social negative control. Uses the same
9-dimensional donor observation and private weights per individual.
"""
from __future__ import annotations
import argparse,sys,math
from dataclasses import replace
import torch
from torch.distributions import Categorical,Bernoulli
from targeted_gifts import C as OriginalC, PrivateGiftActor
import v25_multi_capacity as base

def actual_sent_neighbor(w,dests,gifts):
    """Flag each neighbor that REALLY received at least one of 3 own gifts."""
    graph=w["graph"]
    return (((dests[:,:,None,:]==graph[None,:,:,None])&
             (gifts[:,:,None,:]>.5)).any(-1)).float()

class PreciseGiftActor(PrivateGiftActor):
 def act(self,c,w,mode='normal',greedy=False):
    graph=w['graph'];b,n=w['roles'].shape;deg=c.degree
    neighbors=w['roles'][:,graph]
    complementary=(neighbors!=w['roles'][:,:,None]).float()
    prior_help=w['trust']
    prior_offer=w['prev_gift'][:,graph]
    # Distinct change from the V25 legacy policy:
    prior_target=w.get('prev_donated_slots')
    if prior_target is None:
        prior_target=torch.zeros(b,n,deg,device=c.device)
    if mode=='no_social' or not c.social:
        prior_help=prior_help*0
        prior_offer=prior_offer*0
    elif mode=='scramble':
        flip=torch.randperm(n,device=c.device)
        prior_help=prior_help[:,flip,:]
        prior_offer=prior_offer[:,flip,:]
    elif mode!='normal':raise ValueError(mode)
    scalar=lambda x:x[:,:,None].expand(-1,-1,deg)
    ownlast=scalar(w['lastfood'])
    ownprev=scalar(w['prev_gift'])
    lastreceived=scalar((prior_help.sum(2)>0).float())
    T=torch.full_like(prior_help,float(w['t']/c.horizon))
    f=torch.stack([complementary,prior_help,prior_offer,
      prior_target,ownlast,ownprev,lastreceived,T,
      torch.full_like(T,float(c.k/12))],dim=-1)
    hidden=torch.tanh(torch.einsum('bnjf,nfh->bnjh',f,self.target_W)+
                     self.target_b[None,:,None,:])
    logits=torch.einsum('bnjh,nh->bnj',hidden,self.target_v)
    dist=Categorical(logits=logits)
    slot=logits.argmax(2) if greedy else dist.sample()
    dest=graph[None,:,:].expand(b,-1,-1).gather(2,slot[:,:,None]).squeeze(2)
    selected=f.gather(2,slot[:,:,None,None].expand(-1,-1,1,f.shape[-1])).squeeze(2)
    gh=torch.tanh(torch.einsum('bnf,nfh->bnh',selected,self.gift_W)+
                 self.gift_b[None,:,:])
    give_logits=torch.einsum('bnh,nh->bn',gh,self.gift_v)+self.gift_bias[None,:]
    give_dist=Bernoulli(logits=give_logits)
    gift=(give_logits>0).float() if greedy else give_dist.sample()
    lp=give_dist.log_prob(gift)+gift*dist.log_prob(slot)
    ent=give_dist.entropy()+gift*dist.entropy()
    return dest,gift,lp,ent

ORIGINAL_STEP=base.step_multi
def precise_step(c,w,dests,gifts):
    reward,distinct=ORIGINAL_STEP(c,w,dests,gifts)
    w["prev_donated_slots"]=actual_sent_neighbor(w,dests,gifts)
    return reward,distinct

def settings():
 p=argparse.ArgumentParser(add_help=False,allow_abbrev=False)
 p.add_argument('--degree',type=int,choices=(4,6),required=True)
 p.add_argument('--relational-feature',choices=('legacy','precise'),required=True)
 p.add_argument('--no-social-training',type=int,choices=(0,1),default=0)
 opts,_=p.parse_known_args()
 return opts

def install(opts):
   original_args=base.args
   original_roll=base.roll
   def compatible_args():
     p=original_args()
     for action in p._actions:
       if action.dest=='cost':action.choices=(.01,.02,.04,.12)
     p.add_argument('--degree',type=int,choices=(4,6),required=True)
     p.add_argument('--relational-feature',choices=('legacy','precise'),required=True)
     p.add_argument('--no-social-training',type=int,choices=(0,1),default=0)
     return p
   base.args=compatible_args
   def chosen_graph(*args,**kwargs):
     assert kwargs.get('degree',6)==6, "Training/evaluation original V25 must request degree six"
     kwargs["degree"]=opts.degree
     return OriginalC(*args,**kwargs)
   base.C=chosen_graph
   if opts.relational_feature=='precise':
     base.PrivateGiftActor=PreciseGiftActor
     base.step_multi=precise_step
   else:
     assert base.step_multi is ORIGINAL_STEP
   if opts.no_social_training:
     def train_without_social(*args,**kwargs):
       if torch.is_grad_enabled():
         kwargs['social']=False
       return original_roll(*args,**kwargs)
     base.roll=train_without_social

if __name__=='__main__':
 settings_=settings()
 install(settings_)
 base.main()
