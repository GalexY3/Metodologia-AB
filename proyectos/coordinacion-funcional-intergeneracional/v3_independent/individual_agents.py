"""One neural policy per agent; no parameter sharing or centralized critic.

Param axes start with agent index, e.g., W1[i], W_send[i], W_accept[i].
Operations batch worlds only. Gradient on actor i is structurally separated
from actor j parameters, with the SAME team reward for both.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"v2_rl"))
import torch
from torch import nn
from torch.distributions import Categorical
from torch.nn import functional as F
from environment import OBS_DIM,MAX_K
from environment_v3 import ACTION_DIM

class IndependentActors(nn.Module):
    def __init__(self,n:int=36,hidden:int=32):
        super().__init__()
        self.n=int(n);self.hidden=int(hidden)
        self.W1=nn.Parameter(torch.empty(n,OBS_DIM,hidden))
        self.b1=nn.Parameter(torch.zeros(n,hidden))
        self.W2=nn.Parameter(torch.empty(n,hidden,hidden))
        self.b2=nn.Parameter(torch.zeros(n,hidden))
        self.Wsend=nn.Parameter(torch.empty(n,hidden,1+5*MAX_K))
        self.bsend=nn.Parameter(torch.zeros(n,1+5*MAX_K))
        self.Wreject=nn.Parameter(torch.empty(n,hidden,1))
        self.breject=nn.Parameter(torch.zeros(n,1))
        self.Wself=nn.Parameter(torch.empty(n,hidden,MAX_K))
        self.bself=nn.Parameter(torch.zeros(n,MAX_K))
        self.Waccept=nn.Parameter(torch.empty(n,hidden+OBS_DIM+MAX_K,hidden))
        self.baccept=nn.Parameter(torch.zeros(n,hidden))
        self.Wacceptout=nn.Parameter(torch.empty(n,hidden,1))
        self.bacceptout=nn.Parameter(torch.zeros(n,1))
        self.reset_parameters()

    def reset_parameters(self):
        for p in (self.W1,self.W2,self.Wsend,self.Wreject,self.Wself,self.Waccept,self.Wacceptout):
            for m in p:
                nn.init.xavier_uniform_(m)
        # Lower starting logit magnitudes prevent saturation and high bias.
        with torch.no_grad():
            self.Wsend.mul_(.25)
            self.Wacceptout.mul_(.25)
            self.Wreject.mul_(.25)
            self.Wself.mul_(.25)

    def encode(self,obs):
        if obs.shape[1]!=self.n or obs.shape[-1]!=OBS_DIM:
            raise ValueError("One independent model per node. Mismatched population size")
        z=torch.tanh(torch.einsum("bni,nih->bnh",obs,self.W1)+self.b1[None])
        return torch.tanh(torch.einsum("bnh,nhj->bnj",z,self.W2)+self.b2[None])

    def send_logits(self,obs,mask):
        h=self.encode(obs)
        logits=torch.einsum("bnh,nhj->bnj",h,self.Wsend)+self.bsend[None]
        logits=logits.masked_fill(~mask,-1e8)
        return logits,h

    def accept_logits(self,h,snapshot,incoming,requests,k):
        B,N,S,D=snapshot.shape
        assert N==self.n and S==5 and D==OBS_DIM
        own=h.unsqueeze(2).expand(-1,-1,S,-1)
        color=F.one_hot(requests,MAX_K).float()
        combined=torch.cat((own,snapshot,color),dim=-1)
        z=torch.tanh(torch.einsum("bnsi,nih->bnsh",combined,self.Waccept)+self.baccept[None,:,None])
        options=(torch.einsum("bnsh,nhj->bnsj",z,self.Wacceptout)+self.bacceptout[None,:,None]).squeeze(-1)
        decline=torch.einsum("bnh,nhj->bnj",h,self.Wreject)+self.breject[None]
        # Self-initiated choices are fully independent of whether requests exist.
        voluntary=torch.einsum("bnh,nhj->bnj",h,self.Wself)+self.bself[None]
        active=(torch.arange(MAX_K)[None,None,:]<k[:,None,None]).expand(B,N,MAX_K)
        legal=torch.cat((torch.ones_like(incoming[:,:,:1]),active,incoming),dim=-1)
        return torch.cat((decline,voluntary,options),dim=-1).masked_fill(~legal,-1e8)

    def act_send(self,obs,legal,deterministic=False,uniform=False):
        logits,h=self.send_logits(obs,legal)
        if uniform:logits=torch.zeros_like(logits).masked_fill(~legal,-1e8)
        cat=Categorical(logits=logits)
        action=logits.argmax(-1) if deterministic else cat.sample()
        return action,cat.log_prob(action),cat.entropy(),h

    def act_accept(self,h,snapshot,incoming,requests,k,deterministic=False,uniform=False):
        # k is public task information; no global counts are consulted.
        logits=self.accept_logits(h,snapshot,incoming,requests,k)
        if uniform:
            permitted=logits>-1e7
            logits=torch.zeros_like(logits).masked_fill(~permitted,-1e8)
        cat=Categorical(logits=logits)
        a=logits.argmax(-1) if deterministic else cat.sample()
        return a,cat.log_prob(a),cat.entropy()

    def agent_parameter_block(self,i:int):
        return {name:p[i].detach().clone() for name,p in self.named_parameters()}
