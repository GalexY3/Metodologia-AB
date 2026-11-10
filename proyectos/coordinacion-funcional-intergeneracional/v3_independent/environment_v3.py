"""V3 color-only state actions and directed one-outgoing, many-incoming messages.

There are N separately trained policies. Communication is OPTIONAL for
changing one's own color; decisions are synchronous. The scalar team
feedback is the ONLY learning reward. Environment global fractions are
returned for ANALYST instrumentation, never as actor input.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"v2_rl"))
import torch
from environment import VectorSociety,MAX_K

class IndependentSociety(VectorSociety):
    def own_color_mask(self):
        B,N=self.batch,self.n
        return (torch.arange(MAX_K)[None,None,:]<self.k[:,None,None]).expand(B,N,MAX_K)

    def step(self,send_actions,next_colors,incoming,requested):
        if send_actions.shape!=(self.batch,self.n) or next_colors.shape!=(self.batch,self.n):
            raise ValueError("Both outgoing and chosen color must be B x N")
        if not torch.all((send_actions>=0)&(send_actions<1+5*MAX_K)):
            raise RuntimeError("Outgoing request index out of range")
        if not torch.all(self.send_mask().gather(-1,send_actions.unsqueeze(-1))).item():
            raise RuntimeError("Illegal recipient or color in outgoing request")
        if not torch.all((next_colors>=0)&(next_colors<MAX_K)):
            raise RuntimeError("Invalid self-selected color")
        if not torch.all(self.own_color_mask().gather(-1,next_colors.unsqueeze(-1))).item():
            raise RuntimeError("Color outside this society's k")
        old=self.colors
        changed=(next_colors!=old)
        # "Coincides with a request" is observational, NOT evidence of
        # deliberately obeying that request.
        matching=(incoming & (requested==next_colors[:,:,None])).any(-1)
        received=incoming.any(-1)
        previous=self.tv()
        self.colors=next_colors.clone()
        after=self.tv()
        reward=self.n*(previous-after)
        self.feedback=reward.detach()
        self.turn+=1
        return {
            "reward":reward,
            "tv":after,
            "churn":changed.float().mean(-1),
            "messages":(send_actions>0).float().mean(-1),
            "changed_when_requested":(changed&matching).float().mean(-1),
            "choice_matches_request":(received&matching).float().mean(-1),
            "choices_with_requests":received.float().mean(-1),
            "requests_received":incoming.sum(-1),
            "global_fraction":self.distribution(),
        }
