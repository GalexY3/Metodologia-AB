"""V48 frozen V47 population: network partnerships change DURING interactions.

A bipartite matching assigns one complementary specialist to each actor per
round. Gift policy is unilateral, own rewards only; the two causal arms
have exactly the same exogenous uniform actions, partner schedule and lives.
"""
from __future__ import annotations
import argparse,json,hashlib,time
from pathlib import Path
import numpy as np,torch
from v46_exact_opponent_shaping import N,B,V,C,GAMMA,H
ROOT=Path(__file__).resolve().parent
SEEDS=(994101,994107,994109,994121,994131,994137)
RATES=(0.,.05,.25,.60,1.)
MEMORIES=("carry","reset")

def load(name):
 folder=ROOT/"runs"/name
 spec=json.loads((folder/"v47_spec.json").read_text("utf8"))
 status=json.loads((folder/"v47_status.json").read_text("utf8"))
 ck=torch.load(folder/"v47_latest.pt",map_location="cpu",weights_only=False)
 assert status["state"]=="completed" and ck["update"]==spec["updates"]==1000
 params=ck["logits"].detach().numpy().astype(np.float64)
 assert params.shape==(N,5)
 return params,spec

def schedule(seed,worlds,rate,q=.95,steps=H):
 """Partner and survival streams independent of policy/action draws."""
 assert 0<=rate<=1 and 0<q<=1
 matchrng=np.random.default_rng(seed*7411+11)
 liferng=np.random.default_rng(seed*7411+17)
 partners=np.empty((steps,worlds,N),dtype=np.int64)
 alive=np.ones((steps,worlds),dtype=bool)
 current=np.empty((worlds,N),dtype=np.int64)
 rewire_uniforms=matchrng.random((steps,worlds))
 # Draw every potential pairing independently of the rate.
 # Thus changing rate only changes whether a preselected matching is used.
 pair_candidates=np.empty((steps,worlds,24),dtype=np.int64)
 for t in range(steps):
  for w in range(worlds):
   pair_candidates[t,w]=matchrng.permutation(24)
 for t in range(steps):
  if t:
   alive[t]=alive[t-1]&(liferng.random(worlds)<q)
  for w in range(worlds):
   if t==0 or rewire_uniforms[t,w]<rate:
    right=pair_candidates[t,w]
    current[w,:24]=24+right
    current[w,24+right]=np.arange(24)
   partners[t,w]=current[w]
 assert np.all(np.take_along_axis(partners,partners,axis=2)==
    np.broadcast_to(np.arange(N),partners.shape))
 assert np.all((partners[:,:,:24]>=24)) and np.all((partners[:,:,24:]<24))
 return partners,alive

def uniforms(seed,worlds,steps=H):
 rng=np.random.default_rng(seed*7411+23)
 return rng.random((steps,worlds,N))

def batched_simulate(params,partner,alive,action_uniform,memory="carry",
                     force=None,subjects=None,causal_discount=True):
 """Run independent worlds in batch; return food and own causal experiences.

 force is None or 0/1; subjects is a subject identity for each world.
 """
 assert memory in MEMORIES
 steps,worlds,n=partner.shape
 assert params.shape==(n,5)
 assert alive.shape==(steps,worlds)
 assert action_uniform.shape==(steps,worlds,n)
 if force is not None:
  assert subjects is not None and subjects.shape==(worlds,)
 probs=1/(1+np.exp(-params))
 ownlast=np.zeros((worlds,n),dtype=np.int64)
 otherlast=np.zeros((worlds,n),dtype=np.int64)
 foodtotal=0.;gifttotal=0.;mutualtotal=0.;actor_rounds=0.
 individual=np.zeros(worlds,dtype=np.float64)
 initial=None; changes=0;unique=np.zeros((worlds,n,n),dtype=bool)
 for t in range(steps):
  partner_t=partner[t]
  if t==0:
   actionp=np.broadcast_to(probs[:,0],(worlds,n))
  else:
   other=otherlast
   if memory=="reset":
    other=np.where(partner_t==partner[t-1],other,0)
   state=1+ownlast*2+other
   actionp=probs[np.arange(n)[None,:],state]
  action=(action_uniform[t]<actionp).astype(np.int64)
  if t==0 and force is not None:
   action[np.arange(worlds),subjects]=int(force)
  received=np.take_along_axis(action,partner_t,axis=1)
  food=B+V*received-C*action
  mask=alive[t,:,None]
  foodtotal+=float((food*mask).sum())
  gifttotal+=float((action*mask).sum())
  mutualtotal+=float((action*received*mask).sum())
  actor_rounds+=int(alive[t].sum())*n
  if t>0:changes+=int(((partner_t!=partner[t-1])&mask).sum())
  # Contact coverage: identity of distinct partners encountered in live rounds
  rows=np.where(alive[t])[0]
  unique[rows[:,None],np.arange(n)[None,:],partner_t[rows]]=True
  if subjects is not None:
   own=food[np.arange(worlds),subjects]*alive[t]
   individual+=(GAMMA**t)*own
   if t==0:initial=own.copy()
  ownlast=action
  otherlast=received
 return dict(food=foodtotal/max(1,actor_rounds),
   gifts=gifttotal/max(1,actor_rounds),
   mutual=mutualtotal/max(1,actor_rounds),
   mean_lifetime=actor_rounds/(worlds*n),
   distinct_partners=float(unique.sum(axis=2).mean()),
   fraction_changed=changes/max(1,actor_rounds),
   own_discounted=individual if subjects is not None else None,
   own_initial=initial)

def ordinary_one(params,seed,worlds,rate,memory):
 partners,alive=schedule(seed,worlds,rate)
 draws=uniforms(seed,worlds)
 data=batched_simulate(params,partners,alive,draws,memory)
 return dict(seed=seed,**{k:v for k,v in data.items() if not k.startswith("own_")})

def paired_one(params,seed,worlds,rate,memory):
 """All 48 people independently treated in cloned matched world paths."""
 partner,alive=schedule(seed,worlds,rate)
 rng=np.random.default_rng(seed*7411+29)
 u=rng.random((H,worlds,N,N))
 subjects=np.tile(np.arange(N),worlds)
 pair=np.repeat(partner,N,axis=1)
 living=np.repeat(alive,N,axis=1)
 both_uniform=u.reshape(H,worlds*N,N)
 yes=batched_simulate(params,pair,living,both_uniform,memory,force=1,subjects=subjects)
 no=batched_simulate(params,pair,living,both_uniform,memory,force=0,subjects=subjects)
 initial=(yes["own_initial"]-no["own_initial"]).reshape(worlds,N)
 total=(yes["own_discounted"]-no["own_discounted"]).reshape(worlds,N)
 assert np.allclose(initial,-C,atol=1e-9)
 return dict(seed=seed,worlds=worlds,
    per_agent=total.mean(0).tolist(),
    mean_total=float(total.mean()),
    mean_future=float((total-initial).mean()),
    mean_initial=float(initial.mean()),
    positive_agents=int((total.mean(0)>0).sum()))

def evaluate(name,worlds=128,causal_worlds=8):
 params,spec=load(name)
 rows=[];start=time.perf_counter()
 for rate in RATES:
  for memory in MEMORIES:
   hold=[ordinary_one(params,s,worlds,rate,memory) for s in SEEDS]
   causal=[paired_one(params,s,causal_worlds,rate,memory) for s in SEEDS]
   individuals=np.asarray([x["per_agent"] for x in causal])
   record=dict(model=name,rate=rate,memory=memory,
    worlds_per_seed=worlds,causal_worlds_per_seed=causal_worlds,
    food=float(np.mean([x["food"] for x in hold])),
    gifts=float(np.mean([x["gifts"] for x in hold])),
    mutual=float(np.mean([x["mutual"] for x in hold])),
    mean_lifetime=float(np.mean([x["mean_lifetime"] for x in hold])),
    distinct_partners=float(np.mean([x["distinct_partners"] for x in hold])),
    fraction_changed=float(np.mean([x["fraction_changed"] for x in hold])),
    causal=float(individuals.mean()),
    causal_future=float(np.mean([x["mean_future"] for x in causal])),
    causal_initial=float(np.mean([x["mean_initial"] for x in causal])),
    positive_agents=int((individuals.mean(0)>0).sum()),
    by_seed_holdout=hold,by_seed_causal=causal,
    per_agent=individuals.mean(0).tolist())
   rows.append(record)
   print("V48",name,"r",rate,memory,"food",round(record["food"],4),
    "mutual",round(record["mutual"],3),"causal",round(record["causal"],4),
    "positive",record["positive_agents"],
    "contacts",round(record["distinct_partners"],2),flush=True)
 target=ROOT/"results"/("v48_dynamic_"+name+".json")
 target.write_text(json.dumps(dict(model=name,original_spec=spec,
  seeds=list(SEEDS),rates=list(RATES),memory_modes=list(MEMORIES),
  causal_schedule_matched=True,rows=rows),indent=1),encoding="utf8")
 print("V48_DONE",name,"seconds",round(time.perf_counter()-start,2),flush=True)
 return rows

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--name",required=True)
 parser.add_argument("--worlds",type=int,default=128)
 parser.add_argument("--causal-worlds",type=int,default=8)
 a=parser.parse_args()
 assert a.worlds>=2 and a.causal_worlds>=1
 evaluate(a.name,a.worlds,a.causal_worlds)
if __name__=="__main__":main()
