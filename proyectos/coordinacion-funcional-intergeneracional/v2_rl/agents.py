"""Neural policy with no explicit role-selection or balancing heuristics.

All agents run the same parameterized policy, but see different local states
and send/receive different directed messages. Central critic is trainer-only.
"""
import torch
from torch import nn
from torch.distributions import Categorical
import torch.nn.functional as F
from environment import OBS_DIM,MAX_K

class LocalActor(nn.Module):
    def __init__(self,hidden=64):
        super().__init__()
        self.encoder=nn.Sequential(
            nn.Linear(OBS_DIM,hidden),nn.Tanh(),
            nn.Linear(hidden,hidden),nn.Tanh())
        self.send_head=nn.Linear(hidden,1+5*MAX_K)
        self.reject_head=nn.Linear(hidden,1)
        self.accept_head=nn.Sequential(
            nn.Linear(hidden+OBS_DIM+MAX_K,hidden),
            nn.Tanh(),nn.Linear(hidden,1))
        # Near-uniform initial actions; neither color is privileged ex ante.
        nn.init.zeros_(self.send_head.weight)
        nn.init.zeros_(self.send_head.bias)
        nn.init.zeros_(self.reject_head.weight)
        nn.init.zeros_(self.reject_head.bias)
        nn.init.zeros_(self.accept_head[-1].weight)
        nn.init.zeros_(self.accept_head[-1].bias)

    def send_logits(self,obs,allowed):
        z=self.encoder(obs)
        logits=self.send_head(z).masked_fill(~allowed,-1e8)
        return logits,z

    def accept_logits(self,z,sender_observations,incoming,requested):
        B,N,degree,D=sender_observations.shape
        own=z.unsqueeze(2).expand(B,N,degree,-1)
        color_onehot=F.one_hot(requested,MAX_K).float()
        inputs=torch.cat((own,sender_observations,color_onehot),dim=-1)
        candidates=self.accept_head(inputs).squeeze(-1)
        reject=self.reject_head(z)
        logits=torch.cat((reject,candidates),dim=-1)
        legal=torch.cat((torch.ones_like(incoming[:,:,:1]),incoming),dim=-1)
        return logits.masked_fill(~legal,-1e8)

    def sample_sender(self,obs,allowed,deterministic=False,random_baseline=False):
        logits,z=self.send_logits(obs,allowed)
        if random_baseline:logits=torch.zeros_like(logits).masked_fill(~allowed,-1e8)
        cat=Categorical(logits=logits)
        actions=logits.argmax(-1) if deterministic else cat.sample()
        return actions,cat.log_prob(actions),cat.entropy(),z

    def sample_receiver(self,z,sender_observations,incoming,requested,
                        deterministic=False,random_baseline=False):
        logits=self.accept_logits(z,sender_observations,incoming,requested)
        if random_baseline:
            allowed=logits>-1e7
            logits=torch.zeros_like(logits).masked_fill(~allowed,-1e8)
        cat=Categorical(logits=logits)
        actions=logits.argmax(-1) if deterministic else cat.sample()
        return actions,cat.log_prob(actions),cat.entropy()

class CentralCritic(nn.Module):
    def __init__(self,hidden=64):
        super().__init__()
        self.net=nn.Sequential(nn.Linear(4+4+1,hidden),nn.Tanh(),
            nn.Linear(hidden,hidden),nn.Tanh(),nn.Linear(hidden,1))

    def forward(self,soc):
        fractions=soc.distribution()
        legal=F.one_hot(soc.k,5).float()[:,1:5]
        feedback=(soc.feedback/soc.n).clamp(-1,1).unsqueeze(-1)
        return self.net(torch.cat((fractions,legal,feedback),dim=-1)).squeeze(-1)
