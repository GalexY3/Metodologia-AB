"""Ten available labels; public task k=2,3,4, selected labels NOT prechosen.

All N agents possess full autonomy to choose next color. Directed messages
provide additional private observations, one outgoing per node and arbitrary
incoming up to degree. The scalar team reward is COMMON to every agent.
"""
from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"v2_rl"))
import torch
import torch.nn.functional as F
from environment import lattice

C=10
S=5
OBS_DIM=C+S*C+S+3  # own color, five neighbors, neighbor-valid, D, delta, k/10
SEND_DIM=1+S*C

@dataclass(frozen=True)
class Config10:
    rows:int=6
    cols:int=6
    batch:int=12
    seed:int=421
    churn_penalty:float=.03
    reward_kind:str="level"

class Society10:
    def __init__(self,cfg=Config10()):
        self.cfg=cfg
        self.neighbors,self.valid,self.contact_sets=lattice(cfg.rows,cfg.cols)
        self.n=cfg.rows*cfg.cols
        self.batch=cfg.batch
        self.gen=torch.Generator(device="cpu")
        self.gen.manual_seed(cfg.seed)
        self.k=None
        self.colors=None
        self.feedback=None
        self.D=None
        self.turn=0
        self.reset()

    def reset(self,k=None):
        B,N=self.batch,self.n
        if k is None:
            self.k=torch.tensor([2+(i%3) for i in range(B)],dtype=torch.long)
        elif isinstance(k,int):
            if k not in (2,3,4): raise ValueError("The first study only trains k=2..4")
            self.k=torch.full((B,),k,dtype=torch.long)
        else:
            self.k=torch.as_tensor(k,dtype=torch.long)
            if self.k.shape!=(B,) or not torch.all((self.k>=2)&(self.k<=4)).item():
                raise ValueError("Bad k")
        # Crucial difference from V3: unbiased initial choice over ALL ten states.
        self.colors=torch.randint(0,C,(B,N),generator=self.gen)
        self.D=self.tv()
        self.feedback=torch.zeros(B)
        self.turn=0
        return self.observe()

    def histogram(self):
        return F.one_hot(self.colors,num_classes=C).sum(1)

    def distribution(self):
        return self.histogram().float()/self.n

    def tv(self):
        counts=self.distribution()
        top=counts.topk(k=4,dim=-1).values
        targets=1.0/self.k.float()
        masked=(torch.arange(4)[None,:]<self.k[:,None])
        score=torch.minimum(top,targets[:,None])*masked
        return 1.0-score.sum(-1)

    def exact(self):
        h=self.histogram()
        desired=self.n/self.k.float()
        occupied=(h>0).sum(-1)
        quota=torch.where(h>0,h.float(),desired[:,None])
        return (occupied==self.k)&((quota-desired[:,None]).abs().max(-1).values<1e-6)

    def observe(self):
        B,N=self.batch,self.n
        own=F.one_hot(self.colors,num_classes=C).float()
        other=F.one_hot(self.colors[:,self.neighbors],num_classes=C).float()
        other=other*self.valid[None,:,:,None]
        visibility=self.valid[None,:,:].float().expand(B,N,S)
        D=self.D[:,None,None].expand(B,N,1)
        feedback=self.feedback[:,None,None].expand(B,N,1)
        kval=(self.k.float()/C)[:,None,None].expand(B,N,1)
        obs=torch.cat((own,other.flatten(2),visibility,D,feedback,kval),dim=-1)
        assert obs.shape==(B,N,OBS_DIM)
        return obs

    def send_mask(self):
        visible=self.valid[None,:,:,None].expand(self.batch,self.n,S,C)
        return torch.cat((torch.ones((self.batch,self.n,1),dtype=torch.bool),
             visible.reshape(self.batch,self.n,S*C)),dim=-1)

    def deliveries(self,obs,outgoing):
        B,N=self.batch,self.n
        if outgoing.shape!=(B,N):
            raise ValueError("Outgoing decisions must be B x N")
        if (outgoing<0).any() or (outgoing>=SEND_DIM).any():
            raise ValueError("Invalid send action")
        slot=((outgoing-1).clamp(min=0)//C)
        requested=((outgoing-1).clamp(min=0)%C)
        target=self.neighbors[None].expand(B,-1,-1).gather(
              2,slot.unsqueeze(-1)).squeeze(-1)
        target=torch.where(outgoing>0,target,torch.full_like(target,-1))
        incoming=(target[:,self.neighbors]==torch.arange(N)[None,:,None])&self.valid[None]
        recipient_color=requested[:,self.neighbors]
        recipient_color=torch.where(incoming,recipient_color,
                                     torch.zeros_like(recipient_color))
        # Snapshots from neighbors that did not actually message are MASKED
        # inside the policy. The actor never sees their contents in that case.
        snapshot=obs[:,self.neighbors,:].contiguous()
        return incoming,recipient_color,snapshot

    def step(self,outgoing,next_colors,incoming,requested):
        B,N=self.batch,self.n
        if outgoing.shape!=(B,N) or next_colors.shape!=(B,N):
            raise ValueError("Invalid action dimensions")
        if not self.send_mask().gather(-1,outgoing.unsqueeze(-1)).all().item():
            raise ValueError("Illegal outgoing edge")
        if (next_colors<0).any().item() or (next_colors>=C).any().item():
            raise ValueError("Every color must be in 0..9")
        previous=self.colors
        old_D=self.D
        changed=next_colors!=previous
        self.colors=next_colors.clone()
        self.D=self.tv()
        delta=old_D-self.D
        self.feedback=delta.detach()
        turnover=changed.float().mean(-1)
        if self.cfg.reward_kind=="level":
            reward=-self.D-self.cfg.churn_penalty*turnover
        elif self.cfg.reward_kind=="delta":
            reward=self.n*delta
        else:raise ValueError("Unknown team reward")
        self.turn+=1
        matched=(incoming & (requested==next_colors[:,:,None])).any(-1)
        return {
           "reward":reward,
           "D":self.D,
           "delta_D":delta,
           "churn":turnover,
           "messages":(outgoing>0).float().mean(-1),
           "message_matches":(matched&incoming.any(-1)).float().mean(-1),
           "occupied":(self.histogram()>0).sum(-1),
           "exact":self.exact(),
        }
