"""V3 independent learners: each agent can autonomously change color.

Round:
  1. Directly see own color and immediate neighbors' colors.
  2. Send 0 or 1 message to a neighbor, including local snapshot and color request.
  3. Receive 0..degree messages, even if already sending.
  4. Choose one OWN action, mutually exclusive:
      0       stay
      1..4    voluntarily choose color 0..3, restricted to legal k
      5..9    accept a specific incoming neighbor's color request, if received
  5. Update all colors synchronously and distribute SAME global progress reward.

No local balancing heuristics and no global color counts accessible to actors.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"v2_rl"))
import torch
from environment import VectorSociety,MAX_K

ACTION_DIM=1+MAX_K+5

class IndependentSociety(VectorSociety):
    def action_mask(self,incoming):
        if incoming.ndim!=3 or incoming.shape!=(self.batch,self.n,5):
            raise ValueError("Incoming requests must have B x N x 5 slots")
        valid_self=(torch.arange(MAX_K)[None,None,:]<self.k[:,None,None]).expand(
            self.batch,self.n,MAX_K)
        return torch.cat((torch.ones((self.batch,self.n,1),dtype=torch.bool),
                          valid_self,incoming),dim=-1)

    def step(self,send_actions,own_actions,incoming,requested):
        """Apply voluntary change or acceptance, with simultaneous state update."""
        if own_actions.shape!=(self.batch,self.n):
            raise ValueError("Invalid own action shape")
        if send_actions.shape!=(self.batch,self.n):
            raise ValueError("Invalid send action shape")
        if not torch.all(self.send_mask().gather(-1,send_actions.unsqueeze(-1))):
            raise RuntimeError("Illegal outgoing message")
        if torch.any(own_actions<0) or torch.any(own_actions>=ACTION_DIM):
            raise RuntimeError("Out of range own action")
        if not torch.all(self.action_mask(incoming).gather(-1,own_actions.unsqueeze(-1))):
            raise RuntimeError("Illegal self-color choice or non-existent petition")
        old=self.colors
        voluntary=(own_actions>=1)&(own_actions<=MAX_K)
        accepted=own_actions>MAX_K
        voluntary_color=(own_actions-1).clamp(0,MAX_K-1)
        chosen_slot=(own_actions-(1+MAX_K)).clamp(0,4)
        petition_color=requested.gather(2,chosen_slot.unsqueeze(-1)).squeeze(-1)
        new_color=torch.where(voluntary,voluntary_color,
                              torch.where(accepted,petition_color,old))
        before=self.tv()
        self.colors=new_color
        after=self.tv()
        reward=self.n*(before-after)
        self.feedback=reward.detach()
        self.turn+=1
        churn=(new_color!=old).float().mean(-1)
        return {
            "reward":reward,
            "tv":after,
            "churn":churn,
            "messages":(send_actions>0).float().mean(-1),
            "acceptances":accepted.float().mean(-1),
            "voluntary_choices":voluntary.float().mean(-1),
            "voluntary_changes":(voluntary&(new_color!=old)).float().mean(-1),
            "accepted_changes":(accepted&(new_color!=old)).float().mean(-1),
            "requests_received":incoming.sum(-1),
            "global_fraction":self.distribution(), # EVALUATOR only, never included in observe()
        }
