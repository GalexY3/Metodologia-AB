"""V19C genuine repeated public-goods dilemma.

Physical goods donated by one person become available to the neighbors.
The donor does *not* consume its own contribution (no self-production bonus).
Only future actions by independently trained neighbors can create a return
to donation. Unlike the V19 mutual-exchange model, there is NO reciprocity
rule enforced by the institution. This exposes free riding and temporal
reciprocity as falsifiable learned strategies.
"""
import torch
from exchange import create_world,IndependentActors,metrics

def advance(c,world,roles,offers):
    assert roles.shape==offers.shape==world['roles'].shape
    neighbor_roles=roles[:,world['adj']]
    neighbor_offers=offers[:,world['adj']]
    colors=torch.nn.functional.one_hot(neighbor_roles,c.k).float()
    received=(colors*neighbor_offers[:,:,:,None]).sum(2)>0
    # Absolutely no own goods, even when the agent donates.
    distinct=received.sum(2).float()
    coverage=distinct/c.k
    full=(distinct>=c.k).float()
    switching=(roles!=world['roles']).float()
    reward=.20+.55*coverage+.25*full-c.cost*offers-c.switch_cost*switching
    world['roles']=roles
    world['offers']=offers
    world['reward']=reward
    world['coverage']=coverage
    world['full']=full
    world['t']+=1
    return reward

def rollout(c,actor,seed,mode='normal',deterministic=False,record=False,
            force_offer=None,random_actor=False):
    world=create_world(c,seed)
    logs=[];ents=[];rewards=[];hist=[]
    for t in range(c.horizon):
        if random_actor:
            roles=torch.randint(c.k,(c.batch,c.n),device=c.device)
            offers=(torch.rand(c.batch,c.n,device=c.device)<.5).float()
            lp=ent=None
        else:
            roles,offers,lp,ent=actor.act(c,world,mode,deterministic,force_offer)
        r=advance(c,world,roles,offers)
        if lp is not None:
            logs.append(lp);ents.append(ent)
        rewards.append(r)
        if record:hist.append(float(r.mean()))
    return dict(metrics=metrics(c,world),logs=logs,ents=ents,
                rewards=rewards,history=hist)
