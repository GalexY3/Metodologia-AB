"""V50 frozen 48-person four-role multi-neighbor market.

Each person can send 3 independent unilateral gifts simultaneously to three
distinct occupations. V25 food: .20 + .55*coverage + .25*full - .04*sent.
The interaction graph has exactly one reciprocal link per other profession.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from v46_exact_opponent_shaping import N,B,V,C,GAMMA,H
from v48_within_episode_rewire import load
ROOT=Path(__file__).resolve().parent
SEEDS=(996101,996107,996109,996121,996131,996137)
RATES=(0.,.25,1.)
MEMORY=("carry","public","none")
K=4;M=N//K;S=K-1
ROLE=np.repeat(np.arange(K),M)
OTHER_ROLE=np.asarray([[j for j in range(K) if j!=k] for k in range(K)])
SLOT=np.full((K,K),-1,dtype=np.int64)
for k in range(K):
 for idx,j in enumerate(OTHER_ROLE[k]):SLOT[k,j]=idx
assert (SLOT[0]==[-1,0,1,2]).all()

def matching(seed,worlds,r,steps=H,q=.95):
 """One uniform precomputed matching for each pair of role categories."""
 assert 0<=r<=1
 matcher=np.random.default_rng(seed*52319+41)
 lifetime=np.random.default_rng(seed*52319+43)
 changes=matcher.random((steps,worlds))
 candidates={}
 for a in range(K):
  for b in range(a+1,K):
   candidate=np.empty((steps,worlds,M),dtype=np.int64)
   for t in range(steps):
    for w in range(worlds):candidate[t,w]=matcher.permutation(M)
   candidates[(a,b)]=candidate
 graph=np.empty((steps,worlds,N,S),dtype=np.int64)
 alive=np.ones((steps,worlds),dtype=bool)
 current=np.empty((worlds,N,S),dtype=np.int64)
 for t in range(steps):
  if t:alive[t]=alive[t-1]&(lifetime.random(worlds)<q)
  for w in range(worlds):
   if t==0 or changes[t,w]<r:
    for (a,b),choices in candidates.items():
     dest=b*M+choices[t,w]
     src=np.arange(a*M,(a+1)*M)
     current[w,src,SLOT[a,b]]=dest
     current[w,dest,SLOT[b,a]]=src
   graph[t,w]=current[w]
 assert np.all(ROLE[graph]==OTHER_ROLE[ROLE][None,None,:,:])
 return graph,alive

def action_draws(seed,worlds,steps=H):
 return np.random.default_rng(seed*52319+47).random((steps,worlds,N,S))

def get_received(action,graph):
 worlds,n,slots=action.shape
 batch=np.arange(worlds)[:,None,None]
 source_role=ROLE[graph]
 destination_role=ROLE[None,:,None]
 reverse=SLOT[source_role,destination_role]
 return action[batch,graph,reverse]

def simulate(params,graph,alive,uniform,mode,forced=None,subjects=None):
 """Causally identical environment for forced vs unforced individual gift."""
 assert mode in MEMORY
 tmax,worlds,n,slots=graph.shape
 assert slots==3 and n==48
 probs=1/(1+np.exp(-params))
 ownlast=np.zeros((worlds,N,S),dtype=np.int64)
 recvlast=np.zeros_like(ownlast)
 actor_food=np.zeros(worlds,dtype=np.float64)
 init=None
 aggregate=dict(food=0.,gifts=0.,mutual=0.,coverage=0.,full=0.)
 alive_rounds=0.
 for t in range(tmax):
  partner=graph[t]
  if t==0:p=np.broadcast_to(probs[:,0][None,:,None],(worlds,N,S))
  else:
   if mode=="carry":info=recvlast
   elif mode=="public":
    # Public record: last action by this partner TO YOUR PROFESSION.
    # Same fixed role-target slot even if the previous recipient was different.
    info=get_received(ownlast,partner)
   else:info=np.zeros_like(ownlast)
   idx=1+ownlast*2+info
   p=probs[np.arange(N)[None,:,None],idx]
  action=(uniform[t]<p).astype(np.int64)
  if t==0 and forced is not None:
   assert subjects is not None and subjects.shape==(worlds,)
   action[np.arange(worlds),subjects,0]=int(forced)
  received=get_received(action,partner)
  types=received.sum(2)
  cover=types/3.
  full=(types==3).astype(np.float64)
  food=B+.55*cover+.25*full-C*action.sum(2)
  mask=alive[t,:,None]
  aggregate["food"]+=float((food*mask).sum())
  aggregate["gifts"]+=float((action*mask[:,:,None]).sum())
  aggregate["mutual"]+=float((action*received*mask[:,:,None]).sum())
  aggregate["coverage"]+=float((cover*mask).sum())
  aggregate["full"]+=float((full*mask).sum())
  alive_rounds+=int(alive[t].sum())*N
  if subjects is not None:
   value=food[np.arange(worlds),subjects]*alive[t]
   actor_food+=(GAMMA**t)*value
   if t==0:init=value.copy()
  ownlast=action;recvlast=received
 den=max(alive_rounds,1)
 return dict(
  food=aggregate["food"]/den,
  gifts_per_person=aggregate["gifts"]/den,
  gifts_slot_rate=aggregate["gifts"]/(den*3),
  mutual_slot_rate=aggregate["mutual"]/(den*3),
  coverage=aggregate["coverage"]/den,
  full=aggregate["full"]/den,
  discounted=actor_food if subjects is not None else None,
  initial=init)

def ordinary(params,seed,worlds,rate,mode):
 graph,alive=matching(seed,worlds,rate)
 u=action_draws(seed,worlds)
 a=simulate(params,graph,alive,u,mode)
 return dict(seed=seed,**{key:value for key,value in a.items()
  if key not in ("discounted","initial")})

def paired(params,seed,worlds,rate,mode):
 graph,alive=matching(seed,worlds,rate)
 u=np.random.default_rng(seed*52319+53).random((H,worlds,N,N,S))
 replica=lambda x:np.repeat(x,N,axis=1)
 g=replica(graph);a=replica(alive);draw=u.reshape(H,worlds*N,N,S)
 subjects=np.tile(np.arange(N),worlds)
 yes=simulate(params,g,a,draw,mode,forced=1,subjects=subjects)
 no=simulate(params,g,a,draw,mode,forced=0,subjects=subjects)
 initial=(yes["initial"]-no["initial"]).reshape(worlds,N)
 diff=(yes["discounted"]-no["discounted"]).reshape(worlds,N)
 assert np.allclose(initial,-C,atol=1e-9)
 return dict(seed=seed,
  mean=float(diff.mean()),
  immediate=float(initial.mean()),
  future=float((diff-initial).mean()),
  per_agent=diff.mean(0).tolist())

def evaluate(name,worlds=64,causal_worlds=4):
 params,spec=load(name)
 outcomes=[]
 start=time.perf_counter()
 for rate in RATES:
  for mode in MEMORY:
   trials=[ordinary(params,s,worlds,rate,mode) for s in SEEDS]
   interventions=[paired(params,s,causal_worlds,rate,mode) for s in SEEDS]
   totals=np.asarray([r["per_agent"] for r in interventions])
   data=dict(name=name,rate=rate,mode=mode,
    food=float(np.mean([z["food"] for z in trials])),
    gifts=float(np.mean([z["gifts_per_person"] for z in trials])),
    mutual=float(np.mean([z["mutual_slot_rate"] for z in trials])),
    coverage=float(np.mean([z["coverage"] for z in trials])),
    full=float(np.mean([z["full"] for z in trials])),
    causal=float(totals.mean()),
    positive_agents=int((totals.mean(0)>0).sum()),
    immediate=float(np.mean([v["immediate"] for v in interventions])),
    causal_future=float(np.mean([v["future"] for v in interventions])),
    by_seed_holdout=trials,
    by_seed_causal=interventions,
    causal_person=totals.mean(0).tolist())
   outcomes.append(data)
   print("V50",name,"r",rate,mode,"food",round(data["food"],4),
    "full",round(data["full"],3),"mutual",round(data["mutual"],3),
    "causal",round(data["causal"],4),"POS",data["positive_agents"],
    flush=True)
 target=ROOT/"results"/("v50_network_"+name+".json")
 target.write_text(json.dumps(dict(name=name,seed_list=SEEDS,
  role_assignment=ROLE.tolist(),occupations_exogenous=True,
  distinct_specialty_matching=True,worlds_per_seed=worlds,
  causal_worlds_per_seed=causal_worlds,rows=outcomes),indent=1),
  encoding="utf8")
 print("V50_DONE",name,"elapsed",round(time.perf_counter()-start,2),flush=True)
 return outcomes

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--name",required=True)
 parser.add_argument("--worlds",type=int,default=64)
 parser.add_argument("--causal-worlds",type=int,default=4)
 a=parser.parse_args()
 evaluate(a.name,a.worlds,a.causal_worlds)
if __name__=="__main__":main()
