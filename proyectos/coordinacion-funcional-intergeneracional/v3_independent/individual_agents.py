"""N independent, exactly color-label equivariant policies.

Each agent i owns distinct tensors W*_i. Color candidates use a common
scoring network WITHIN that agent, not across agents. Hence relabeling
colors permutes logits without re-training. No fixed color-identity bias.

Input: own color, direct neighbor colors, optional directed messages with
sender snapshot and requested color, previous GLOBAL TEAM scalar feedback.
No global histogram enters an agent's action. Messages are cheap talk,
self-color is ALWAYS an independent choice, even when no messages exist.
"""
import torch
from torch import nn
from torch.distributions import Categorical
from torch.nn import functional as F
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"v2_rl"))
from environment import MAX_K,OBS_DIM

SEND_FEATURES=7
CHOOSE_FEATURES=9

class IndependentActors(nn.Module):
    def __init__(self,n:int=36,hidden:int=24):
        super().__init__()
        self.n=int(n)
        self.hidden=int(hidden)
        # Dimensions [agent, features, hidden], unique per-agent weights
        self.send_W1=nn.Parameter(torch.empty(n,SEND_FEATURES,hidden))
        self.send_b1=nn.Parameter(torch.zeros(n,hidden))
        self.send_W2=nn.Parameter(torch.empty(n,hidden))
        self.send_b2=nn.Parameter(torch.zeros(n))
        self.silence_bias=nn.Parameter(torch.zeros(n))
        self.choose_W1=nn.Parameter(torch.empty(n,CHOOSE_FEATURES,hidden))
        self.choose_b1=nn.Parameter(torch.zeros(n,hidden))
        self.choose_W2=nn.Parameter(torch.empty(n,hidden))
        self.choose_b2=nn.Parameter(torch.zeros(n))
        self.reset_parameters()

    def reset_parameters(self):
        for W in (self.send_W1,self.choose_W1):
            for w in W: nn.init.xavier_uniform_(w)
        with torch.no_grad():
            nn.init.normal_(self.send_W2,std=.08)
            nn.init.normal_(self.choose_W2,std=.08)

    def _decode_observation(self,obs):
        B,N,D=obs.shape
        if N!=self.n or D!=OBS_DIM:raise ValueError("N and observation dimension mismatch")
        own=obs[:,:,:MAX_K]
        neigh=obs[:,:,4:24].reshape(B,N,5,MAX_K)
        valid=obs[:,:,24:29]
        progress=obs[:,:,29]
        kinfo=obs[:,:,30]
        count=valid.sum(-1).clamp_min(1)
        frac=neigh.sum(2)/count[:,:,None]
        return own,neigh,valid,frac,progress,kinfo,count

    def send_logits(self,obs,k):
        B,N,D=obs.shape
        own,neigh,valid,frac,progress,kinfo,count=self._decode_observation(obs)
        # Seven scalar features per (recipient neighbor slot, candidate color).
        local_freq=frac[:,:,None,:].expand(-1,-1,5,-1)
        own_candidate=own[:,:,None,:].expand(-1,-1,5,-1)
        recipient_candidate=neigh
        recipient_matches_self=(neigh*own[:,:,None,:]).sum(-1,keepdim=True).expand(-1,-1,-1,MAX_K)
        f=torch.stack((
            own_candidate,local_freq,recipient_candidate,
            recipient_matches_self,
            progress[:,:,None,None].expand(B,N,5,MAX_K),
            kinfo[:,:,None,None].expand(B,N,5,MAX_K),
            (count/5)[:,:,None,None].expand(B,N,5,MAX_K)
        ),dim=-1)
        h=torch.tanh(torch.einsum("bnscf,nfh->bnsch",f,self.send_W1)
                     +self.send_b1[None,:,None,None,:])
        candidate=torch.einsum("bnsch,nh->bnsc",h,self.send_W2)+self.send_b2[None,:,None,None]
        legal=valid[:,:, :,None].bool() & (
            torch.arange(MAX_K)[None,None,None,:]<k[:,None,None,None])
        scores=candidate.masked_fill(~legal,-1e8).reshape(B,N,5*MAX_K)
        silence=self.silence_bias[None,:,None].expand(B,N,1)
        return torch.cat((silence,scores),-1)

    def choose_logits(self,obs,k,incoming,requested,snapshots):
        B,N,D=obs.shape
        own,neigh,valid,frac,progress,kinfo,count=self._decode_observation(obs)
        if incoming.shape!=(B,N,5) or requested.shape!=(B,N,5) or snapshots.shape!=(B,N,5,OBS_DIM):
            raise ValueError("Invalid neighbor-message format")
        # All received messages contribute, no exclusive matching.
        req_onehot=F.one_hot(requested,MAX_K).float()*incoming[:,:,:,None]
        req_frac=req_onehot.sum(2)/incoming.sum(2).clamp_min(1)[:,:,None]
        sender_own=snapshots[:,:,:,:4]
        sender_neigh=snapshots[:,:,:,4:24].reshape(B,N,5,5,MAX_K).sum(-2)
        sender_valid=snapshots[:,:,:,24:29].sum(-1)
        sender_counts=(sender_own+sender_neigh)/(sender_valid[:,:,:,None]+1).clamp_min(1)
        sender_counts=(sender_counts*incoming[:,:,:,None]).sum(2)/incoming.sum(2).clamp_min(1)[:,:,None]
        any_message=incoming.any(2).float()
        # These are observations, NOT rules to seek a minority color.
        # Same learned scorer applied to every candidate color => equivariant.
        features=torch.stack((
            own,frac,req_frac,sender_counts,
            progress[:,:,None].expand(B,N,MAX_K),
            kinfo[:,:,None].expand(B,N,MAX_K),
            (count/5)[:,:,None].expand(B,N,MAX_K),
            any_message[:,:,None].expand(B,N,MAX_K),
            ((own*frac).sum(-1))[:,:,None].expand(B,N,MAX_K)
        ),dim=-1)
        z=torch.tanh(torch.einsum("bncf,nfh->bnch",features,self.choose_W1)
                   +self.choose_b1[None,:,None,:])
        logits=torch.einsum("bnch,nh->bnc",z,self.choose_W2)+self.choose_b2[None,:,None]
        allowed=torch.arange(MAX_K)[None,None,:]<k[:,None,None]
        return logits.masked_fill(~allowed,-1e8)

    def act_send(self,obs,k,deterministic=False,uniform=False,disable_messages=False):
        scores=self.send_logits(obs,k)
        if disable_messages:
            scores=torch.zeros_like(scores).masked_fill(
                torch.arange(scores.shape[-1])[None,None,:]!=0,-1e8)
        elif uniform:
            allowed=scores>-1e7
            scores=torch.zeros_like(scores).masked_fill(~allowed,-1e8)
        cat=Categorical(logits=scores)
        action=scores.argmax(-1) if deterministic else cat.sample()
        return action,cat.log_prob(action),cat.entropy()

    def act_choose(self,obs,k,incoming,requested,snapshots,deterministic=False,uniform=False):
        scores=self.choose_logits(obs,k,incoming,requested,snapshots)
        if uniform:
            allowed=scores>-1e7
            scores=torch.zeros_like(scores).masked_fill(~allowed,-1e8)
        cat=Categorical(logits=scores)
        action=scores.argmax(-1) if deterministic else cat.sample()
        return action,cat.log_prob(action),cat.entropy()

    def agent_parameter_block(self,i):
        return {name:p[i].detach().clone() for name,p in self.named_parameters()}
