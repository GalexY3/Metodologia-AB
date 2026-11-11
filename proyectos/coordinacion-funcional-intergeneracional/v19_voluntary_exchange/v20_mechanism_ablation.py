"""V20: intervention on frozen *information channels*, not on training rewards.

Disentangle direct-recipient memory from neighbors' publicly visible generosity.
The base actor's parameters are unchanged; only selected observation features
are zeroed at inference time. The donor intervention remains paired by world.
"""
import argparse,json,math,time
from pathlib import Path
import numpy as np
import torch
from torch.distributions import Categorical,Bernoulli
from targeted_gifts import C,PrivateGiftActor,simulate
from audit_targeted import causal,SEEDS,load

ROOT=Path(__file__).resolve().parent
MODES=("normal","no_direct_identity","no_public_offer",
       "no_both_except_receipt","no_own_target_memory","no_social")

class FeatureAblatedActor(PrivateGiftActor):
    def act(self,c,w,mode="normal",greedy=False):
        if mode in ("normal","no_social","scramble"):
            return super().act(c,w,mode,greedy)
        if mode not in MODES:raise ValueError(mode)
        graph=w["graph"]
        batch,n=w["roles"].shape
        degree=c.degree
        neighbor_roles=w["roles"][:,graph]
        complementary=(neighbor_roles!=w["roles"][:,:,None]).float()
        true_help=w["trust"]
        prior_help=true_help
        prior_offer=w["prev_gift"][:,graph]
        prior_target=(w["prev_recipient"][:,:,None]==graph[None,:,:]).float()
        scalar=lambda x:x[:,:,None].expand(-1,-1,degree)
        ownlast=scalar(w["lastfood"])
        ownprev=scalar(w["prev_gift"])
        lastreceived=scalar((true_help.sum(2)>0).float())
        timefeature=torch.full_like(prior_help,float(w["t"]/c.horizon))
        if mode in ("no_direct_identity","no_both_except_receipt"):
            prior_help=torch.zeros_like(prior_help)
        if mode in ("no_public_offer","no_both_except_receipt"):
            prior_offer=torch.zeros_like(prior_offer)
        if mode=="no_own_target_memory":
            prior_target=torch.zeros_like(prior_target)
        f=torch.stack((complementary,prior_help,prior_offer,prior_target,
             ownlast,ownprev,lastreceived,timefeature,
             torch.full_like(timefeature,float(c.k/12))),dim=-1)
        hidden=torch.tanh(torch.einsum("bnjf,nfh->bnjh",f,self.target_W)+
                          self.target_b[None,:,None,:])
        target_logits=torch.einsum("bnjh,nh->bnj",hidden,self.target_v)
        target_dist=Categorical(logits=target_logits)
        slot=target_logits.argmax(2) if greedy else target_dist.sample()
        dest=graph[None,:,:].expand(batch,-1,-1).gather(2,slot[:,:,None]).squeeze(2)
        selected=f.gather(2,slot[:,:,None,None].expand(-1,-1,1,f.shape[-1])).squeeze(2)
        gh=torch.tanh(torch.einsum("bnf,nfh->bnh",selected,self.gift_W)+self.gift_b[None,:,:])
        gift_logits=torch.einsum("bnh,nh->bn",gh,self.gift_v)+self.gift_bias[None,:]
        gift_dist=Bernoulli(logits=gift_logits)
        gift=(gift_logits>0).float() if greedy else gift_dist.sample()
        lp=gift_dist.log_prob(gift)+gift*target_dist.log_prob(slot)
        entropy=gift_dist.entropy()+gift*target_dist.entropy()
        return dest,gift,lp,entropy

@torch.no_grad()
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--worlds",type=int,default=24)
    p.add_argument("--steps",type=int,default=48)
    p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
    a=p.parse_args()
    torch.set_num_threads(2)
    old,spec,u=load(a.name,a.device)
    actor=FeatureAblatedActor(spec["n"],spec["hidden"],spec["init_scale"]).to(a.device)
    actor.load_state_dict(old.state_dict())
    actor.eval()
    c=C(n=spec["n"],k=2,degree=2,topology="ring",
        batch=a.worlds,horizon=a.steps,cost=spec["cost"],
        gamma=spec["gamma"],device=a.device)
    rows=[]
    for mode in MODES:
        metrics=[]
        for seed in SEEDS:
            torch.manual_seed(51*seed+31)
            data=simulate(c,actor,seed,mode=mode,watch=True)[0]
            metrics.append(data)
        cf=causal(c,actor,mode=mode)
        row=dict(mode=mode,worlds=sum(x["worlds"] for x in metrics),
           mean_food=float(np.mean([x["food"] for x in metrics])),
           mean_gift=float(np.mean([x["gift"] for x in metrics])),
           causal=cf)
        rows.append(row)
        print("V20_MECHANISM",a.name,mode,
           "food",round(row["mean_food"],4),
           "gift",round(row["mean_gift"],4),
           "return",round(cf["mean_total"],4),
           "future",round(cf["mean_future"],4),
           "next_incoming",round(cf["mean_next_incoming"],4),
           "positive",cf["successes_total"],"/",cf["pairs"],flush=True)
    payload=dict(model=a.name,checkpoint=u,worlds=a.worlds,steps=a.steps,
      seeds=SEEDS,rows=rows,method="Paired forced-donation counterfactuals; only observation channels ablated.")
    out=ROOT/"results"/("v20_mechanisms_"+a.name+".json")
    out.write_text(json.dumps(payload,indent=1),encoding="utf8")
    print("V20_MECHANISMS_DONE",a.name,flush=True)

if __name__=="__main__":main()
