"""V49 public reputation and corrupted social-signal causal audit.

Frozen V47 private logits. All effects arise from observation routing only,
never from changing reward mechanics, contracts or policy parameters.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from v46_exact_opponent_shaping import N,B,V,C,GAMMA,H
from v48_within_episode_rewire import schedule,uniforms,load
ROOT=Path(__file__).resolve().parent
SEEDS=(995101,995107,995109,995121,995131,995137)
RATES=(.25,.60,1.)
MODES=("carry","public","scrambled","public_noise20")

def signals(seed,worlds,steps=H):
 """A reproducible reporting source matched across both causal arms."""
 reporter=np.empty((steps,worlds,N),dtype=np.int64)
 rng=np.random.default_rng(seed*7411+37)
 for t in range(steps):
  for w in range(worlds):
   reporter[t,w,:24]=24+rng.permutation(24)
   reporter[t,w,24:]=rng.permutation(24)
 noise=np.random.default_rng(seed*7411+43).random((steps,worlds,N))
 return reporter,noise

def run(params,partner,alive,action_uniform,reporter,noise,
        mode,force=None,subjects=None):
 assert mode in MODES
 tmax,worlds,n=partner.shape
 assert action_uniform.shape==reporter.shape==noise.shape==(tmax,worlds,n)
 probs=1/(1+np.exp(-params))
 ownlast=np.zeros((worlds,n),dtype=np.int64)
 otherlast=np.zeros((worlds,n),dtype=np.int64)
 foodtotal=0.;gifts=0.;mutual=0.;active=0.
 benefits=np.zeros(worlds);initial=None
 contacts=np.zeros((worlds,n,n),dtype=bool)
 for t in range(tmax):
  current=partner[t]
  if t==0:p=np.broadcast_to(probs[:,0],(worlds,n))
  else:
   if mode=="carry":other=otherlast
   elif mode=="public":other=np.take_along_axis(ownlast,current,axis=1)
   elif mode=="scrambled":other=np.take_along_axis(ownlast,reporter[t],axis=1)
   else:
    true=np.take_along_axis(ownlast,current,axis=1)
    other=true ^ (noise[t]<.20)
   st=1+2*ownlast+other
   p=probs[np.arange(n)[None,:],st]
  acts=(action_uniform[t]<p).astype(np.int64)
  if t==0 and force is not None:
   assert subjects is not None
   acts[np.arange(worlds),subjects]=int(force)
  received=np.take_along_axis(acts,current,axis=1)
  food=B+V*received-C*acts
  live=alive[t,:,None]
  foodtotal+=float((food*live).sum())
  gifts+=float((acts*live).sum())
  mutual+=float((acts*received*live).sum())
  active+=int(alive[t].sum())*n
  worlds_alive=np.flatnonzero(alive[t])
  contacts[worlds_alive[:,None],np.arange(n)[None,:],current[worlds_alive]]=True
  if subjects is not None:
   reward=food[np.arange(worlds),subjects]*alive[t]
   benefits+=(GAMMA**t)*reward
   if t==0:initial=reward.copy()
  ownlast=acts
  otherlast=received
 return dict(food=foodtotal/max(1,active),
  gifts=gifts/max(1,active),mutual=mutual/max(1,active),
  distinct_partners=float(contacts.sum(2).mean()),
  discounted=benefits if subjects is not None else None,
  initial=initial)

def ordinary(params,seed,worlds,rate,mode):
 partner,alive=schedule(seed,worlds,rate)
 actions=uniforms(seed,worlds)
 reports,noise=signals(seed,worlds)
 z=run(params,partner,alive,actions,reports,noise,mode)
 return {k:v for k,v in z.items() if k not in ("discounted","initial")}

def paired(params,seed,worlds,rate,mode):
 partner,alive=schedule(seed,worlds,rate)
 reports,noise=signals(seed,worlds)
 rng=np.random.default_rng(seed*7411+29)
 actions=rng.random((H,worlds,N,N))
 subj=np.tile(np.arange(N),worlds)
 rep=lambda arr:np.repeat(arr,N,axis=1)
 p=rep(partner);l=rep(alive)
 rr=rep(reports);nn=rep(noise)
 uu=actions.reshape(H,worlds*N,N)
 yes=run(params,p,l,uu,rr,nn,mode,force=1,subjects=subj)
 no=run(params,p,l,uu,rr,nn,mode,force=0,subjects=subj)
 effect=(yes["discounted"]-no["discounted"]).reshape(worlds,N)
 immediate=(yes["initial"]-no["initial"]).reshape(worlds,N)
 assert np.allclose(immediate,-C,atol=1e-9)
 return dict(seed=seed,mean=float(effect.mean()),
   future=float((effect-immediate).mean()),
   immediate=float(immediate.mean()),
   by_agent=effect.mean(0).tolist())

def evaluate(name,worlds=128,causal_worlds=8):
 params,spec=load(name)
 data=[];start=time.perf_counter()
 for rate in RATES:
  for mode in MODES:
   holds=[ordinary(params,seed,worlds,rate,mode) for seed in SEEDS]
   causals=[paired(params,seed,causal_worlds,rate,mode) for seed in SEEDS]
   agents=np.asarray([v["by_agent"] for v in causals])
   result=dict(name=name,rate=rate,mode=mode,worlds_per_seed=worlds,
    causal_worlds_per_seed=causal_worlds,
    food=float(np.mean([x["food"] for x in holds])),
    gifts=float(np.mean([x["gifts"] for x in holds])),
    mutual=float(np.mean([x["mutual"] for x in holds])),
    distinct_partners=float(np.mean([x["distinct_partners"] for x in holds])),
    causal=float(agents.mean()),
    causal_future=float(np.mean([x["future"] for x in causals])),
    causal_initial=float(np.mean([x["immediate"] for x in causals])),
    positive_agents=int((agents.mean(0)>0).sum()),
    per_agent=agents.mean(0).tolist(),
    by_seed_holdout=holds,
    by_seed_causal=causals)
   data.append(result)
   print("V49",name,"r",rate,mode,
    "mutual",round(result["mutual"],3),
    "causal",round(result["causal"],4),
    "positive",result["positive_agents"],flush=True)
 path=ROOT/"results"/("v49_public_"+name+".json")
 path.write_text(json.dumps(dict(name=name,spec=spec,
   seeds=list(SEEDS),rows=data,reporting_modes=MODES,
   intervention="observation routing only; frozen private neural logits"),indent=1),encoding="utf8")
 print("V49_DONE",name,"conds",len(data),
   "elapsed",round(time.perf_counter()-start,2),flush=True)
 return data

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--worlds",type=int,default=128)
 p.add_argument("--causal-worlds",type=int,default=8)
 a=p.parse_args()
 evaluate(a.name,a.worlds,a.causal_worlds)
if __name__=="__main__":main()
