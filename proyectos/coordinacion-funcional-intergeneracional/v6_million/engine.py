"""MARL V6. 144 independent learners, strictly local information, common team reward.

The graph is a five-regular *toroidal square lattice with a diagonal perfect
matching*. It is NOT claimed to be a geometric Archimedean snub-square tiling.
Every individual's trainable weights have a disjoint leading dimension N.
"""
from dataclasses import dataclass
import math
import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Categorical

COLORS = 10
NC = 5
FC = 14
FT = 9

def make_graph(side=12, device="cpu"):
    if side < 4 or side % 2:
        raise ValueError("side must be even and >=4")
    neighbors=[]
    for r in range(side):
        for c in range(side):
            # Two diagonals inside each disjoint 2x2 block = a perfect matching.
            local=(r%2,c%2)
            if local == (0,0): mate=(r+1,c+1)
            elif local == (1,1): mate=(r-1,c-1)
            elif local == (0,1): mate=(r+1,c-1)
            else: mate=(r-1,c+1)
            ns=[((r-1)%side,c),((r+1)%side,c),
                (r,(c-1)%side),(r,(c+1)%side),mate]
            ids=[a*side+b for a,b in ns]
            if len(set(ids))!=5:raise AssertionError("Repeated neighbor")
            neighbors.append(ids)
    for i,ns in enumerate(neighbors):
        for j in ns:
            if i not in neighbors[j]:raise AssertionError(f"Not undirected: {i},{j}")
    return torch.tensor(neighbors,device=device,dtype=torch.long)

@dataclass
class Settings:
    side:int=12
    batch:int=48
    horizon:int=16
    hidden:int=64
    seed:int=6123
    gamma:float=.99
    lr:float=.0007
    entropy:float=.0015
    clip:float=5.
    proximity:float=.25
    terminal:float=2.
    ema_alpha:float=.15
    device:str="cpu"

def distance(counts,k,n):
    """L1/2 distance to nearest k-supported uniform distribution on 10 colors."""
    p=counts.to(torch.float32)/n
    top=p.topk(4,dim=-1).values
    eligible=(torch.arange(4,device=counts.device)[None,:]<k[:,None])
    covered=torch.minimum(top,1/k[:,None].float())*eligible
    return (1-covered.sum(dim=1)).clamp(0,1)

class Society:
    def __init__(self, cfg:Settings, ks=None):
        self.cfg=cfg
        self.graph=make_graph(cfg.side,cfg.device)
        self.n=cfg.side**2
        B=cfg.batch
        self.k=ks.to(cfg.device) if ks is not None else torch.tensor(
            ([2,3,4]*((B+2)//3))[:B],device=cfg.device)
        if tuple(self.k.shape)!=(B,):raise ValueError("bad k")
        self.colors=torch.randint(0,COLORS,(B,self.n),device=cfg.device)
        self.prev_colors=self.colors.clone()
        self.prev_sent=torch.full((B,self.n),-1,device=cfg.device,dtype=torch.long)
        self.prev_recv=torch.zeros((B,self.n,COLORS),device=cfg.device)
        self.prev_target=torch.full((B,self.n),-1,device=cfg.device,dtype=torch.long)
        self.prev_delta=torch.zeros(B,device=cfg.device)
        self.prev_churn=torch.zeros(B,device=cfg.device)
        self.turn=0
        self.local=self.local_frequencies()
        self.ema=self.local.clone()
        self.D=self.calcD()
        self.initial=self.D.clone()
    def counts(self):
        return F.one_hot(self.colors,COLORS).sum(1)
    def calcD(self):
        return distance(self.counts(),self.k,self.n)
    def local_frequencies(self):
        cols=self.colors[:,self.graph]  # B,N,5, observed directly
        a=F.one_hot(cols,COLORS).sum(2).float()
        return (a+F.one_hot(self.colors,COLORS).float())/(NC+1)
    def info(self):
        return self.D, self.prev_delta, self.prev_churn
    def send_messages(self,slot,request):
        """Only actual directed messages expose senders' local observations."""
        B,N=self.colors.shape
        active=slot!=NC  # index 5 = silence
        targets=self.graph[None].expand(B,-1,-1).gather(
            2,slot.clamp_max(NC-1).unsqueeze(-1)).squeeze(-1)
        indices=targets.unsqueeze(-1).expand(B,N,COLORS)
        weights=active.unsqueeze(-1).to(torch.float32)
        requests=torch.zeros(B,N,COLORS,device=self.colors.device)
        requests.scatter_add_(1,indices,F.one_hot(request,COLORS).float()*weights)
        snapshots=torch.zeros_like(requests)
        snapshots.scatter_add_(1,indices,self.local*weights)
        send_counts=requests.sum(-1,keepdim=True)
        # Content of nonmessages never passes through this function.
        average=snapshots/send_counts.clamp_min(1)
        normalized=requests/send_counts.clamp_min(1)
        return normalized,average,active,targets,send_counts.squeeze(-1)
    def advance(self,new_colors,slot,request,requests):
        if new_colors.shape!=self.colors.shape:raise ValueError("wrong action shape")
        old=self.D
        churn=(new_colors!=self.colors).float().mean(-1)
        self.prev_colors=self.colors
        self.colors=new_colors
        self.D=self.calcD()
        delta=old-self.D
        self.prev_delta=delta
        self.prev_churn=churn
        self.prev_sent=torch.where(slot!=NC,request,torch.full_like(request,-1))
        self.prev_recv=requests.detach()
        self.prev_target=torch.where(slot!=NC,slot,torch.full_like(slot,-1))
        self.local=self.local_frequencies()
        self.ema=(1-self.cfg.ema_alpha)*self.ema+self.cfg.ema_alpha*self.local
        self.turn+=1
        return delta,churn
    def exact(self):
        counts=self.counts()
        target=self.n/self.k.float()
        occupancy=(counts>0).sum(-1)
        good=(counts==target[:,None])|(counts==0)
        return (occupancy==self.k)&good.all(-1)

def batchlinear(x,w,b):
    # x: B,N,choices,features; w: N,features,hidden
    return torch.einsum("bncf,nfh->bnch",x,w)+b[None,:,None,:]

class IndependentPolicy(nn.Module):
    def __init__(self, n=144, hidden=64):
        super().__init__()
        self.n=n
        self.hidden=hidden
        # Distinct tensor slice θ_i for each individual. Within one agent,
        # the same function scores 10 exchangeable color labels.
        self.color_w=nn.Parameter(torch.empty(n,FC,hidden))
        self.color_b=nn.Parameter(torch.zeros(n,hidden))
        self.color_out=nn.Parameter(torch.empty(n,hidden))
        self.color_bias=nn.Parameter(torch.zeros(n))
        self.target_w=nn.Parameter(torch.empty(n,FT,hidden))
        self.target_b=nn.Parameter(torch.zeros(n,hidden))
        self.target_out=nn.Parameter(torch.empty(n,hidden))
        self.silent=nn.Parameter(torch.full((n,),-.25))
        for w in (self.color_w,self.target_w):
            for slice in w:nn.init.xavier_uniform_(slice)
        with torch.no_grad():
            nn.init.normal_(self.color_out,std=.05)
            nn.init.normal_(self.target_out,std=.05)
    def color_features(self,e,req=None,snap=None):
        B,N=e.colors.shape
        if req is None:req=torch.zeros(B,N,COLORS,device=e.colors.device)
        if snap is None:snap=torch.zeros_like(req)
        own=F.one_hot(e.colors,COLORS).float()
        prev=F.one_hot(e.prev_colors,COLORS).float()
        sent=F.one_hot(e.prev_sent.clamp_min(0),COLORS).float()
        sent=sent*(e.prev_sent>=0).unsqueeze(-1)
        every=lambda v:v[:,None,None].expand(B,N,COLORS)
        kval=e.k.float()/COLORS
        t=float(e.turn)/max(e.cfg.horizon,1)
        churn=e.prev_churn
        features=torch.stack((
            own,prev,e.local,e.ema,e.local-e.ema,req,snap,
            sent,e.prev_recv,
            every(e.D), every(e.prev_delta),every(kval),
            every(churn),torch.full_like(e.local,t),
        ),dim=-1)
        return features
    def color_logits(self,e,req=None,snap=None):
        x=self.color_features(e,req,snap)
        h=torch.tanh(batchlinear(x,self.color_w,self.color_b))
        return torch.einsum("bnch,nh->bnc",h,self.color_out)+self.color_bias[None,:,None]
    def target_logits(self,e):
        B,N=e.colors.shape
        nb=e.colors[:,e.graph]  # B,N,5
        local_neighbor=e.local.gather(-1,nb)
        ema_neighbor=e.ema.gather(-1,nb)
        own=(nb==e.colors[:,:,None]).float()
        last=(e.prev_target[:,:,None]==torch.arange(NC,device=nb.device)).float()
        every=lambda v:v[:,None,None].expand(B,N,NC)
        x=torch.stack((
            own,local_neighbor,ema_neighbor,last,
            every(e.D),every(e.prev_delta),every(e.k.float()/COLORS),
            every(e.prev_churn),
            torch.full_like(own,float(e.turn)/max(e.cfg.horizon,1)),
        ),-1)
        h=torch.tanh(batchlinear(x,self.target_w,self.target_b))
        z=torch.einsum("bnsh,nh->bns",h,self.target_out)
        return torch.cat((z,self.silent[None,:,None].expand(B,N,1)),dim=-1)
    def decisions(self,e,greedy=False,disable_messages=False):
        target=self.target_logits(e)
        if disable_messages:
            target=target.masked_fill(torch.arange(NC+1,device=target.device)[None,None,:]!=NC,-1e9)
        dist_t=Categorical(logits=target)
        slot=target.argmax(-1) if greedy else dist_t.sample()
        before=self.color_logits(e)
        dist_r=Categorical(logits=before)
        request=before.argmax(-1) if greedy else dist_r.sample()
        rec,snap,active,targets,count=e.send_messages(slot,request)
        after=self.color_logits(e,rec,snap)
        dist_c=Categorical(logits=after)
        choice=after.argmax(-1) if greedy else dist_c.sample()
        logp=dist_t.log_prob(slot)+active.float()*dist_r.log_prob(request)+dist_c.log_prob(choice)
        entropy=dist_t.entropy()+active.float()*dist_r.entropy()+dist_c.entropy()
        return {"slot":slot,"request":request,"choice":choice,"logp":logp,
                "entropy":entropy,"rec":rec,"snap":snap,"active":active,
                "targets":targets,"inbound_count":count}
