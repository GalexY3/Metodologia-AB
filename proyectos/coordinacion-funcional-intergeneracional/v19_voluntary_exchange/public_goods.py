"""V19B: voluntary, unilateral, locally accessible public-goods provision.

An individual may consume neighbors' donated goods without donating.
Donating costs private food and supplies own good to EVERY neighbor and self.
The physical production rule is programmed; the decision to contribute and
the choice of occupation are learned independently from each own reward.

No enforced bilateral reciprocity and no global/team reward.
"""
from __future__ import annotations
import torch
from exchange import Config,create_world,IndependentActors,metrics,rollout as _old_rollout
from exchange import observe
def advance(c,world,roles,offers):
    r=roles
    neighbor_roles=r[:,world['adj']]
    neighbor_offers=offers[:,world['adj']]
    colors=torch.nn.functional.one_hot(neighbor_roles,c.k).float()
    received=(colors*neighbor_offers[:,:,:,None]).sum(2)>0
    own_produce=torch.nn.functional.one_hot(r,c.k).bool()&(
        offers[:,:,None]>0.5)
    obtainable=received|own_produce
    distinct=obtainable.sum(2).float()
    coverage=distinct/c.k
    full=(distinct>=c.k).float()
    switch=(roles!=world['roles']).float()
    reward=.20+.55*coverage+.25*full-c.cost*offers-c.switch_cost*switch
    world['roles']=r
    world['offers']=offers
    world['reward']=reward
    world['coverage']=coverage
    world['full']=full
    world['t']+=1
    return reward

def rollout(c,actor,seed,mode='normal',deterministic=False,record=False,
            force_offer=None,random_actor=False):
    world=create_world(c,seed)
    logs=[];ents=[];rewards=[];timefood=[]
    for t in range(c.horizon):
        if random_actor:
            roles=torch.randint(c.k,(c.batch,c.n),device=c.device)
            offers=(torch.rand(c.batch,c.n,device=c.device)<.5).float()
            lp=ent=None
        else:
            roles,offers,lp,ent=actor.act(c,world,mode,deterministic,force_offer)
        realized=advance(c,world,roles,offers)
        if lp is not None:
            logs.append(lp);ents.append(ent)
        rewards.append(realized)
        if record:timefood.append(float(realized.mean()))
    return dict(metrics=metrics(c,world),logs=logs,ents=ents,
                rewards=rewards,history=timefood)

def marginal_spillover(c,world,roles,offers,agent_indices):
    """Counterfactual causal local externality of each donor, at one snapshot.

    Uses cloned states and fixed partner decisions. Distinguishes the
    donor's own immediate gain from neighbors' gain; zero if irrelevant.
    """
    import copy
    original=copy.deepcopy(world)
    advance(c,original,roles,offers)
    food_original=original['reward']
    results=[]
    for i in agent_indices:
        cf=offers.clone()
        cf[:,i]=0.
        altered=copy.deepcopy(world)
        advance(c,altered,roles,cf)
        delta=food_original-altered['reward']
        # Counterfactual donor gain includes saved personal cost.
        # External benefits exclude donor's own payoff change.
        results.append(dict(agent=i,
          donor_private=float(delta[:,i].mean()),
          neighbor_external=float(delta.sum(1).mean()-delta[:,i].mean()),
          participant_donation=float(offers[:,i].mean())))
    return results
