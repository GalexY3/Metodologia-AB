"""V14: independent neural agents conditioned on desired k; V12 environment.

The task instruction k is not an oracle for colors or a global histogram.
Models differ ONLY in the whether the k channels are exposed; same parameter
count, optimizer and local signals, individual food reward in both arms.
"""
from __future__ import annotations
import sys, math, json
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Categorical

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'v12_variable_mk'))
import v12 as old

KNOW_K=True

class Actor(nn.Module):
    """Color equivariant policy. No shared parameters between agents."""
    def __init__(self,n:int,h:int=16):
        super().__init__()
        self.n=n;self.h=h;self.ema=None
        self.W=nn.Parameter(torch.randn(n,12,h)/math.sqrt(12)*.7)
        self.b=nn.Parameter(torch.zeros(n,h))
        self.v=nn.Parameter(torch.randn(n,h)/math.sqrt(h)*.2)
        self.stay=nn.Parameter(torch.ones(n))
    def reset(self):self.ema=None
    def act(self,e,greedy=False,disable_messages=False,alter_messages=False):
        c=e.c
        loc=e.local()
        if self.ema is None or self.ema.shape!=loc.shape:
            self.ema=loc.detach()
        self.ema=(.75*self.ema+.25*loc).detach()
        own=F.one_hot(e.jobs,c.m).float()
        f=e.food.unsqueeze(-1).expand_as(loc)
        df=(e.food-e.lastfood).unsqueeze(-1).expand_as(loc)
        kk=c.k if KNOW_K else 0
        def constant(x):return torch.full_like(loc,float(x))
        feats=torch.stack([
            loc,self.ema,own,f,df,loc*kk,self.ema*kk,
            constant(math.log(c.k)/math.log(c.n) if KNOW_K else 0),
            constant(1/c.k if KNOW_K else 0),
            constant(math.log(c.m)/math.log(80)),
            own*f,own*df],dim=-1)
        h=torch.tanh(torch.einsum('bnmd,ndh->bnmh',feats,self.W)+self.b[None,:,None,:])
        logits=torch.einsum('bnmh,nh->bnm',h,self.v)+own*self.stay[None,:,None]
        dist=Categorical(logits=logits)
        chosen=logits.argmax(-1) if greedy else dist.sample()
        return chosen,dist.log_prob(chosen),dist.entropy()

def configure(know_k):
    global KNOW_K
    KNOW_K=bool(know_k)
    old.ROOT=HERE
    old.IndividualAgent=Actor

def main():
    import argparse
    prefix=argparse.ArgumentParser(add_help=False,allow_abbrev=False)
    prefix.add_argument('--hide-k',action='store_true')
    flags,others=prefix.parse_known_args()
    sys.argv=[sys.argv[0]]+others
    configure(not flags.hide_k)
    args=old.parse()
    out=HERE/'runs'/args.name
    out.mkdir(parents=True,exist_ok=True)
    description=dict(knows_requested_k=KNOW_K,
                     independent_parameters_per_agent=225,
                     train_rewards='strictly individual realized food',
                     externally_specified_k='yes for k-conditioned; all k channels zeroed for control',
                     colors_are_exchangeable=True,
                     no_global_counts=True,no_messaging=True,no_centralized_critic=True)
    meta=out/'V14_MODEL_SPEC.json'
    if meta.exists() and json.loads(meta.read_text('utf8'))!=description:
        raise RuntimeError('Incompatible experiment treatment for resumed run.')
    old.write_json(meta,description)
    print('K_VISIBLE',KNOW_K,flush=True)
    old.run(args)

if __name__=='__main__':main()
