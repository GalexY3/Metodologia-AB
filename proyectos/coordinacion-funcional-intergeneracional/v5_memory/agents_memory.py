"""Fully independent agent MLPs with strictly local fixed-length history.

History state: [batch, N individuals, 10 candidate colors, W-1 past ticks, F].
History is NOT pooled across individuals and is reset at every episode.
Neural weights: leading dimension N, each person's tensors are disjoint.
The same scorer is applied to all colors WITHIN a person (equivariance).
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"v4_10states"))
import torch
from torch import nn
from torch.distributions import Categorical
from torch.nn import functional as F
from society10 import C,S,OBS_DIM,SEND_DIM
from actors10 import IndependentActors10

FSEND=9
FCHOICE=18

class MemoryAgents10(nn.Module):
 def __init__(self,n=36,hidden=64,memory=1):
  super().__init__()
  if memory not in (1,8):raise ValueError("Design only pre-registered W1 or W8")
  self.n,self.hidden,self.memory=int(n),int(hidden),int(memory)
  self.send_W1=nn.Parameter(torch.empty(n,FSEND+(memory-1)*FCHOICE,hidden))
  self.send_b1=nn.Parameter(torch.zeros(n,hidden))
  self.send_W2=nn.Parameter(torch.empty(n,hidden,hidden))
  self.send_b2=nn.Parameter(torch.zeros(n,hidden))
  self.send_W3=nn.Parameter(torch.empty(n,hidden))
  self.send_b3=nn.Parameter(torch.zeros(n))
  self.silence=nn.Parameter(torch.zeros(n))
  self.choose_W1=nn.Parameter(torch.empty(n,memory*FCHOICE,hidden))
  self.choose_b1=nn.Parameter(torch.zeros(n,hidden))
  self.choose_W2=nn.Parameter(torch.empty(n,hidden,hidden))
  self.choose_b2=nn.Parameter(torch.zeros(n,hidden))
  self.choose_W3=nn.Parameter(torch.empty(n,hidden))
  self.choose_b3=nn.Parameter(torch.zeros(n))
  for w in (self.send_W1,self.send_W2,self.choose_W1,self.choose_W2):
   for t in w:nn.init.xavier_uniform_(t)
  with torch.no_grad():
   nn.init.normal_(self.send_W3,std=.065)
   nn.init.normal_(self.choose_W3,std=.065)
  self.history=None

 def reset_memory(self,batch):
  self.history=torch.zeros(batch,self.n,C,self.memory-1,FCHOICE,
                           device=self.send_W1.device)
 def ensure_memory(self,batch):
  if self.history is None or self.history.shape[0]!=batch:
   raise RuntimeError("Must reset memory at start of each society episode")
 def parse(self,obs):
  return IndependentActors10.parse(self,obs)

 def send_logits(self,obs):
  B,N,_=obs.shape
  self.ensure_memory(B)
  own,neighbors,valid,score,delta,kval,degree,local=self.parse(obs)
  ownC=own[:,:,None,:].expand(B,N,S,C)
  locC=local[:,:,None,:].expand(B,N,S,C)
  same=(neighbors*own[:,:,None,:]).sum(-1)[:,:,:,None].expand(B,N,S,C)
  fea=torch.stack((
   ownC,neighbors,locC,same,
   score[:,:,None,None].expand(B,N,S,C),
   delta[:,:,None,None].expand(B,N,S,C),
   kval[:,:,None,None].expand(B,N,S,C),
   (degree/S)[:,:,None,None].expand(B,N,S,C),
   (own*local).sum(-1)[:,:,None,None].expand(B,N,S,C)
  ),dim=-1)
  if self.memory>1:
   previous=self.history.flatten(-2).unsqueeze(2).expand(B,N,S,C,-1)
   fea=torch.cat((fea,previous),dim=-1)
  h=torch.tanh(torch.einsum("bnscf,nfh->bnsch",fea,self.send_W1)
                +self.send_b1[None,:,None,None,:])
  h=torch.tanh(torch.einsum("bnsch,nhj->bnscj",h,self.send_W2)
                +self.send_b2[None,:,None,None,:])
  logits=torch.einsum("bnsch,nh->bnsc",h,self.send_W3)+self.send_b3[None,:,None,None]
  logits=logits.masked_fill(~valid[:,:,:,None].bool(),-1e8)
  return torch.cat((self.silence[None,:,None].expand(B,N,1),
                    logits.reshape(B,N,S*C)),dim=-1)

 def current_features(self,obs,incoming,requested,payload,outgoing):
  B,N,_=obs.shape
  if incoming.shape!=(B,N,S) or requested.shape!=(B,N,S) \
     or payload.shape!=(B,N,S,OBS_DIM) or outgoing.shape!=(B,N):
   raise ValueError("Wrong message inputs")
  own,neighbors,valid,score,delta,kval,degree,local=self.parse(obs)
  inc=incoming.float()
  inum=inc.sum(-1).clamp_min(1)
  reqfrac=(F.one_hot(requested,C).float()*inc[:,:,:,None]).sum(2)/inum[:,:,None]
  sender_own=payload[:,:,:,:C]
  sender_other=payload[:,:,:,C:C+S*C].reshape(B,N,S,S,C).sum(-2)
  sender_degree=payload[:,:,:,C+S*C:C+S*C+S].sum(-1)
  sender_local=(sender_own+sender_other)/(sender_degree[:,:,:,None]+1)
  sender_mean=(sender_local*inc[:,:,:,None]).sum(2)/inum[:,:,None]
  any_msg=incoming.any(-1).float()
  ownfreq=(own*local).sum(-1)
  diversity=(local>0).float().sum(-1)/C
  sent=(outgoing>0).float()
  req_color=(outgoing-1).clamp(min=0)%C
  req_slot=(outgoing-1).clamp(min=0)//C
  sent_color=F.one_hot(req_color,C).float()*sent[:,:,None]
  sent_neigh=F.one_hot(req_slot,S).float()*sent[:,:,None]
  sent_slot=sent_color[:,:,:,None]*sent_neigh[:,:,None,:]
  return torch.stack((
    own,local,reqfrac,sender_mean,
    score[:,:,None].expand(B,N,C),
    delta[:,:,None].expand(B,N,C),
    kval[:,:,None].expand(B,N,C),
    any_msg[:,:,None].expand(B,N,C),
    (degree/S)[:,:,None].expand(B,N,C),
    ownfreq[:,:,None].expand(B,N,C),
    diversity[:,:,None].expand(B,N,C),
    sent_color,
    sent[:,:,None].expand(B,N,C),
    sent_slot[:,:,:,0],sent_slot[:,:,:,1],sent_slot[:,:,:,2],
    sent_slot[:,:,:,3],sent_slot[:,:,:,4],
  ),dim=-1)

 def choose_logits(self,obs,incoming,requested,payload,outgoing,advance=True):
  B,N,_=obs.shape
  self.ensure_memory(B)
  features=self.current_features(obs,incoming,requested,payload,outgoing)
  if self.memory>1:
   stack=torch.cat((self.history,features.unsqueeze(-2)),dim=-2)
   inp=stack.flatten(-2)
  else:inp=features
  h=torch.tanh(torch.einsum("bncf,nfh->bnch",inp,self.choose_W1)
                +self.choose_b1[None,:,None,:])
  h=torch.tanh(torch.einsum("bnch,nhj->bncj",h,self.choose_W2)
                +self.choose_b2[None,:,None,:])
  out=torch.einsum("bnch,nh->bnc",h,self.choose_W3)+self.choose_b3[None,:,None]
  if advance and self.memory>1:
   # Observations are discrete (colors/messages/reward). No gradients are
   # propagated between agents or through this explicit storage mechanism.
   self.history=stack[:,:,:,1:,:].detach()
  return out

 def act_send(self,obs,disable_messages=False,deterministic=False):
  logit=self.send_logits(obs)
  if disable_messages:
   mask=torch.arange(SEND_DIM,device=logit.device)[None,None,:]!=0
   logit=logit.masked_fill(mask,-1e8)
  cat=Categorical(logits=logit)
  act=logit.argmax(-1) if deterministic else cat.sample()
  return act,cat.log_prob(act),cat.entropy()

 def act_choose(self,obs,incoming,requested,payload,outgoing,deterministic=False):
  logit=self.choose_logits(obs,incoming,requested,payload,outgoing)
  cat=Categorical(logits=logit)
  act=logit.argmax(-1) if deterministic else cat.sample()
  return act,cat.log_prob(act),cat.entropy()
