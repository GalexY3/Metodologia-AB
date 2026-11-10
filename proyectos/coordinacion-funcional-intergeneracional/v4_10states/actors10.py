"""Independent color-equivariant policies across 10 candidate states.

Parameter tensors are [agent, feature, hidden], i.e. agent i shares no
trainable value with agent j. Within ONE individual all 10 colors are
evaluated with the same scorer, so labels remain arbitrary and exchangeable.
"""
import torch
from torch import nn
from torch.distributions import Categorical
from torch.nn import functional as F
from society10 import C,S,OBS_DIM,SEND_DIM

FSEND=9
FCHOOSE=11
class IndependentActors10(nn.Module):
    def __init__(self,n=36,hidden=64):
        super().__init__()
        self.n=n
        self.hidden=hidden
        self.sW1=nn.Parameter(torch.empty(n,FSEND,hidden))
        self.sb1=nn.Parameter(torch.zeros(n,hidden))
        self.sW2=nn.Parameter(torch.empty(n,hidden))
        self.sb2=nn.Parameter(torch.zeros(n))
        self.silent=nn.Parameter(torch.zeros(n))
        self.cW1=nn.Parameter(torch.empty(n,FCHOOSE,hidden))
        self.cb1=nn.Parameter(torch.zeros(n,hidden))
        self.cW2=nn.Parameter(torch.empty(n,hidden))
        self.cb2=nn.Parameter(torch.zeros(n))
        self.reset_parameters()

    def reset_parameters(self):
        for big in (self.sW1,self.cW1):
            for w in big: nn.init.xavier_uniform_(w)
        with torch.no_grad():
            nn.init.normal_(self.sW2,std=.065)
            nn.init.normal_(self.cW2,std=.065)

    def parse(self,obs):
        B,N,D=obs.shape
        if N!=self.n or D!=OBS_DIM:raise ValueError("Wrong population or obs size")
        own=obs[:,:,:C]
        neigh=obs[:,:,C:C+S*C].reshape(B,N,S,C)
        valid=obs[:,:,C+S*C:C+S*C+S]
        idx=C+S*C+S
        score=obs[:,:,idx]
        delta=obs[:,:,idx+1]
        kval=obs[:,:,idx+2]
        degree=valid.sum(2).clamp_min(1)
        local=neigh.sum(2)/degree[:,:,None]
        return own,neigh,valid,score,delta,kval,degree,local

    def send_logits(self,obs):
        B,N,D=obs.shape
        own,neighbors,valid,score,delta,kval,degree,local=self.parse(obs)
        ownC=own[:,:,None,:].expand(B,N,S,C)
        locC=local[:,:,None,:].expand(B,N,S,C)
        neq=(neighbors*own[:,:,None,:]).sum(-1)[:,:, :,None].expand(B,N,S,C)
        fea=torch.stack((
          ownC,neighbors,locC,neq,
          score[:,:,None,None].expand(B,N,S,C),
          delta[:,:,None,None].expand(B,N,S,C),
          kval[:,:,None,None].expand(B,N,S,C),
          (degree/5)[:,:,None,None].expand(B,N,S,C),
          (local*own).sum(-1)[:,:,None,None].expand(B,N,S,C),
        ),dim=-1)
        h=torch.tanh(torch.einsum("bnscf,nfh->bnsch",fea,self.sW1)
            +self.sb1[None,:,None,None,:])
        s=torch.einsum("bnsch,nh->bnsc",h,self.sW2)+self.sb2[None,:,None,None]
        s=s.masked_fill(~valid.bool()[:,:,:,None],-1e8)
        silent=self.silent[None,:,None].expand(B,N,1)
        return torch.cat((silent,s.reshape(B,N,S*C)),dim=-1)

    def choose_logits(self,obs,incoming,requested,payload):
        B,N,D=obs.shape
        if incoming.shape!=(B,N,S) or requested.shape!=(B,N,S) or payload.shape!=(B,N,S,OBS_DIM):
            raise ValueError("Invalid message dimensions")
        own,neighbors,valid,score,delta,kval,degree,local=self.parse(obs)
        inc=incoming.float()
        inc_total=inc.sum(-1).clamp_min(1)
        req_onehot=F.one_hot(requested,C).float()*inc[:,:,:,None]
        reqfrac=req_onehot.sum(2)/inc_total[:,:,None]
        sender_own=payload[:,:,:,:C]
        sender_neighbors=payload[:,:,:,C:C+S*C].reshape(B,N,S,S,C).sum(-2)
        sender_degree=payload[:,:,:,C+S*C:C+S*C+S].sum(-1)
        sender_counts=(sender_own+sender_neighbors)/(sender_degree[:,:,:,None]+1)
        sender_mean=(sender_counts*inc[:,:,:,None]).sum(2)/inc_total[:,:,None]
        # Causal masking: a nonexistent message never leaks its payload.
        any_message=incoming.any(-1).float()
        community_local=(local>0).float().sum(-1)/C
        ownfreq=(own*local).sum(-1)
        feats=torch.stack((
          own,local,reqfrac,sender_mean,
          score[:,:,None].expand(B,N,C),
          delta[:,:,None].expand(B,N,C),
          kval[:,:,None].expand(B,N,C),
          any_message[:,:,None].expand(B,N,C),
          (degree/5)[:,:,None].expand(B,N,C),
          ownfreq[:,:,None].expand(B,N,C),
          community_local[:,:,None].expand(B,N,C)
        ),dim=-1)
        h=torch.tanh(torch.einsum("bncf,nfh->bnch",feats,self.cW1)
             +self.cb1[None,:,None,:])
        return torch.einsum("bnch,nh->bnc",h,self.cW2)+self.cb2[None,:,None]

    def act_send(self,obs,disable_messages=False,uniform=False,deterministic=False):
        scores=self.send_logits(obs)
        if disable_messages:
            mask=torch.arange(SEND_DIM)[None,None,:]!=0
            scores=scores.masked_fill(mask,-1e8)
        elif uniform:
            mask=scores>-1e7
            scores=torch.zeros_like(scores).masked_fill(~mask,-1e8)
        cat=Categorical(logits=scores)
        a=scores.argmax(-1) if deterministic else cat.sample()
        return a,cat.log_prob(a),cat.entropy()

    def act_choose(self,obs,incoming,requested,payload,uniform=False,deterministic=False):
        scores=self.choose_logits(obs,incoming,requested,payload)
        if uniform:scores=torch.zeros_like(scores)
        cat=Categorical(logits=scores)
        a=scores.argmax(-1) if deterministic else cat.sample()
        return a,cat.log_prob(a),cat.entropy()
