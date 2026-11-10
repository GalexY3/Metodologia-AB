"""Minimal micro-agent adaptation on the EXACT existing village environment/trainer.

Each individual owns a distinct per-color scoring MLP (41,57,73 parameters).
The same individual MLP weights score all ten professions (label symmetry).
Retains V9 original payoff, graph, simultaneous dynamics, policy-gradient code.
Modes:
 basic: [local frequency, EMA(local frequency), is-own] => 41.
 food: add [own food, own delta food] => 57.
 public: also add [village mean food, village delta food] => 73.
Global food is an actor observation ONLY in public, computed from all actual
food values AFTER the previous choice. No counterfactual oracle or D-k input.
No learned messages in any arm; study information only, never claim negotiation.
"""
import os,sys,json
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Categorical
import village

class MicroAgent(nn.Module):
    def __init__(self,n,hidden):
        super().__init__()
        self.n=n;self.mode=os.environ["VILLAGE_MICRO_MODE"]
        d=dict(basic=3,food=5,public=7)[self.mode]
        self.d=d
        self.W=nn.Parameter((torch.rand(n,d,8)-.5)*1.4)
        self.b=nn.Parameter(torch.linspace(-1.1,1.1,8).expand(n,-1).clone()
                            +(torch.rand(n,8)-.5)*.15)
        self.V=nn.Parameter((torch.rand(n,8)-.5)*.25)
        self.bias=nn.Parameter(torch.zeros(n))
        assert sum(p.numel() for p in self.parameters())==n*(8*d+17)
        self.belief=None
    def reset(self,b,device):
        self.belief=None
    def choose(self,obs,colors,communication,greedy=False):
        local=obs[...,10:20]  # only neighbor states, not a global census
        own=obs[...,:10]
        if self.belief is None or self.belief.shape!=local.shape:
            self.belief=local.detach()
        self.belief=(.35*self.belief+.65*local).detach()  # fixed EMA, not learned
        fields=[local,self.belief,own]
        if self.mode in ("food","public"):
            f=obs[...,25:26]
            delta=obs[...,26:27]
            fields.extend([f.expand(-1,-1,10),delta.expand(-1,-1,10)])
        if self.mode=="public":
            # A public report of the PREVIOUSLY REALIZED, not hypothetical, welfare.
            # It is the mean of personal food, after other agents' latest actions.
            gf=obs[...,25].mean(dim=1,keepdim=True)
            gd=obs[...,26].mean(dim=1,keepdim=True)
            fields.extend([gf.unsqueeze(-1).expand(-1,obs.shape[1],10),
                           gd.unsqueeze(-1).expand(-1,obs.shape[1],10)])
        x=torch.stack(fields,dim=-1)
        h=torch.tanh(torch.einsum("bncd,ndh->bnch",x,self.W)+self.b[None,:,None,:])
        scores=torch.einsum("bnch,nh->bnc",h,self.V)+self.bias[None,:,None]
        actions=Categorical(logits=scores)
        picked=scores.argmax(-1) if greedy else actions.sample()
        msg=torch.zeros_like(colors) # no learned messaging; C0 comparison only
        return picked,msg,actions.log_prob(picked),actions.entropy()

def main():
    args=sys.argv[1:]
    if "--observation" in args:
        ix=args.index("--observation")
        mode=args[ix+1]
        del args[ix:ix+2]
    else:mode="basic"
    if mode not in ("basic","food","public"):raise ValueError(mode)
    if "--communication" in args:raise ValueError("Micro pilot has no learned messages; use C0")
    os.environ["VILLAGE_MICRO_MODE"]=mode
    sys.argv=[sys.argv[0]]+args
    a=village.parse()
    # No modifying the old code: substitute only the individual actor architecture.
    village.IndividualRNN=MicroAgent
    dest=Path(village.ROOT)/"runs"/a.name
    dest.mkdir(parents=True,exist_ok=True)
    manifest=dest/"DESIGN.json"
    config={"agent":"individual-color-equivariant-MLP","observation":mode,
        "parameters_per_agent":dict(basic=41,food=57,public=73)[mode],
        "individual_rewards_only":True,"communication":"not-enabled",
        "gossip":"none", "color_names":"exchangeable",
        "global_report":"observed post-hoc prior realized welfare" if mode=="public" else "no",
        "underlying_engine":"k_comparison/village.py"}
    if manifest.exists() and json.loads(manifest.read_text(encoding="utf8"))!=config:
        raise ValueError("Existing run has different architecture!")
    manifest.write_text(json.dumps(config,indent=2),encoding="utf8")
    village.run(a)

if __name__=="__main__":main()
