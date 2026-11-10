"""V2 RL environment: directed one-outgoing, many-incoming local communication.

Pure Torch CPU backend, 6x6=36 pilot or 10x12=120. The actor receives NO
global counts. The trainer computes a common dense progress signal.
"""
from dataclasses import dataclass
import torch
import torch.nn.functional as F

MAX_K=4
MAX_DEGREE=5
OBS_DIM=4+5*4+5+1+1

def lattice(rows=6,cols=6):
    if rows%2 or cols%2 or rows<4 or cols<4:
        raise ValueError("Even rectangular grid >=4x4 required")
    n=rows*cols
    contacts=[set() for _ in range(n)]
    for r in range(rows):
        for c in range(cols):
            a=r*cols+c
            for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
                rr,cc=r+dr,c+dc
                if 0<=rr<rows and 0<=cc<cols:contacts[a].add(rr*cols+cc)
    # Each 2x2 block contributes a perfect matching of diagonal contacts.
    for r in range(0,rows,2):
        for c in range(0,cols,2):
            for a,b in ((r*cols+c,(r+1)*cols+c+1),
                        (r*cols+c+1,(r+1)*cols+c)):
                contacts[a].add(b);contacts[b].add(a)
    assert all(len(x)<=5 for x in contacts)
    assert all(i not in x for i,x in enumerate(contacts))
    assert all(i in contacts[j] for j,x in enumerate(contacts) for i in x)
    adjacency=torch.zeros((n,5),dtype=torch.long)
    valid=torch.zeros((n,5),dtype=torch.bool)
    for i,c in enumerate(contacts):
        for z,j in enumerate(sorted(c)):
            adjacency[i,z]=j
            valid[i,z]=True
    return adjacency,valid,contacts

@dataclass
class Configuration:
    rows:int=6
    cols:int=6
    batch:int=12
    seed:int=20261110
    majority_fraction:float=.70
    randomize_majority:bool=False
    device:str="cpu"

class VectorSociety:
    def __init__(self,cfg=Configuration()):
        self.cfg=cfg
        self.neighbors,self.valid,self.contact_sets=lattice(cfg.rows,cfg.cols)
        self.n=cfg.rows*cfg.cols
        self.batch=cfg.batch
        self.gen=torch.Generator(device="cpu")
        self.gen.manual_seed(cfg.seed)
        self.k=None
        self.colors=None
        self.feedback=None
        self.turn=0
        self.reset()

    def reset(self,k=None):
        B,N=self.batch,self.n
        if k is None:
            self.k=torch.tensor([2+(z%3) for z in range(B)],dtype=torch.long)
            perm=torch.randperm(B,generator=self.gen)
            self.k=self.k[perm]
        elif isinstance(k,int):
            if not 2<=k<=MAX_K:raise ValueError("k must be 2..4 in V2 pilot")
            self.k=torch.full((B,),k,dtype=torch.long)
        else:
            self.k=torch.as_tensor(k,dtype=torch.long)
            if self.k.shape!=(B,) or not torch.all((self.k>=2)&(self.k<=MAX_K)):
                raise ValueError("Bad per-world k")
        majority=int(round(N*self.cfg.majority_fraction))
        colors=torch.zeros((B,N),dtype=torch.long)
        for b in range(B):
            kc=int(self.k[b])
            colors[b,majority:]=torch.randint(1,kc,(N-majority,),generator=self.gen)
            colors[b]=colors[b,torch.randperm(N,generator=self.gen)]
            if self.cfg.randomize_majority:
                # Randomly relabel the majority and minority colors per episode.
                # Actors cannot exploit a fixed 'color zero is overrepresented' cue.
                role_permutation=torch.randperm(kc,generator=self.gen)
                colors[b]=role_permutation[colors[b]]
        self.colors=colors
        self.feedback=torch.zeros(B,dtype=torch.float32)
        self.turn=0
        return self.observe()

    def distribution(self):
        return F.one_hot(self.colors,num_classes=MAX_K).float().mean(1)

    def tv(self):
        frac=self.distribution()
        active=(torch.arange(MAX_K)[None,:]<self.k[:,None]).float()
        target=active/self.k.float().unsqueeze(-1)
        return .5*((frac-target).abs()*active).sum(-1)

    def observe(self):
        B,N=self.batch,self.n
        own=F.one_hot(self.colors,MAX_K).float()
        neigh_color=self.colors[:,self.neighbors]
        neighbour_onehot=F.one_hot(neigh_color,MAX_K).float()
        neighbour_onehot=neighbour_onehot*self.valid[None,:,:,None]
        vis=self.valid[None,:,:].float().expand(B,N,5)
        progress=(self.feedback/self.n).clamp(-1,1)[:,None,None].expand(B,N,1)
        kinfo=(self.k.float()/MAX_K)[:,None,None].expand(B,N,1)
        obs=torch.cat((own,neighbour_onehot.flatten(2),vis,progress,kinfo),dim=-1)
        assert obs.shape==(B,N,OBS_DIM)
        return obs

    def send_mask(self):
        B,N=self.batch,self.n
        active=torch.arange(MAX_K)[None,:]<self.k[:,None]
        combinations=(self.valid[None,:,:,None]&active[:,None,None,:])
        return torch.cat((torch.ones((B,N,1),dtype=torch.bool),
                          combinations.reshape(B,N,5*MAX_K)),dim=-1)

    def deliveries(self,obs,send_actions):
        B,N=self.batch,self.n
        if send_actions.shape!=(B,N):raise ValueError("Bad actions shape")
        chosen_slot=((send_actions-1).clamp(min=0)//MAX_K).long()
        request_color=((send_actions-1).clamp(min=0)%MAX_K).long()
        target=self.neighbors[None].expand(B,-1,-1).gather(2,chosen_slot.unsqueeze(-1)).squeeze(-1)
        target=torch.where(send_actions>0,target,torch.full_like(target,-1))
        n_targets=target[:,self.neighbors]
        receiver=torch.arange(N)[None,:,None]
        incoming=(n_targets==receiver)&self.valid[None]
        requested=request_color[:,self.neighbors]
        requested=torch.where(incoming,requested,torch.zeros_like(requested))
        snapshot=obs[:,self.neighbors,:].contiguous()
        return incoming,requested,snapshot

    def step(self,send_actions,accept_actions,incoming,requested):
        B,N=self.batch,self.n
        if accept_actions.shape!=(B,N):raise ValueError("Bad accept shape")
        if send_actions.shape!=(B,N):raise ValueError("Bad send shape")
        if not torch.all(self.send_mask().gather(-1,send_actions.unsqueeze(-1))).item():
            raise RuntimeError("Invalid outgoing target or color")
        if not torch.all(accept_actions>=0).item() or not torch.all(accept_actions<=5).item():
            raise RuntimeError("Invalid acceptance action")
        choice=(accept_actions-1).clamp(min=0)
        valid_choice=incoming.gather(2,choice.unsqueeze(-1)).squeeze(-1)
        if torch.any((accept_actions>0)&(~valid_choice)).item():
            raise RuntimeError("Accepted nonexistent incoming request")
        old=self.colors
        chosen_color=requested.gather(2,choice.unsqueeze(-1)).squeeze(-1)
        nxt=torch.where(accept_actions>0,chosen_color,old)
        prior=self.tv()
        self.colors=nxt
        after=self.tv()
        r=self.n*(prior-after)
        churn=(nxt!=old).float().mean(-1)
        self.feedback=r.detach()
        self.turn+=1
        return {"reward":r,"tv":after,"churn":churn,
                "messages":(send_actions>0).float().mean(-1),
                "acceptances":(accept_actions>0).float().mean(-1),
                "requests_received":incoming.sum(-1),
                "global_fraction":self.distribution()}
