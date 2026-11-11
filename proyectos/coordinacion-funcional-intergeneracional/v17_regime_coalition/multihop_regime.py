"""Distributed many-hop role inference: distinct coworker identities, not global census.

Testing how much gossip radius is needed to disambiguate personal payoff
collisions, under N=120, various k/d/graph/segregation regimes.
All role observations are masked to R-hop reachable graph nodes. R=0 is own
reward. R beyond graph diameter becomes full global observation reconstructed
from messages and is NOT equivalent to the original restricted observation.
"""
from pathlib import Path
import sys,json,itertools,math,time
from dataclasses import replace
import numpy as np,torch
import coalition_protocols as c
from regime_benchmark import setup as setup_v, infer_reward
HERE=Path(__file__).resolve().parent
KS=(4,12,30,60)
MS=(50,80)
DS=(4,8,16)
TOP=('ring','rewired')
INITS=('random','trap','cluster')
RADS=(0,1,2,4,8,16,32)
def binary_likelihood_log(x,draw,n,N):
 p=(n-1)/(N-1)
 p=np.clip(p,1e-6,1-1e-6)
 return x*np.log(p)+(draw-x)*np.log(1-p)
def classify(r,q,ownc,reach,n=120):
 rs=np.asarray(r,dtype=float)
 sub=q*rs
 sup=q/np.maximum(rs,1e-12)
 possible_sub=(sub>=1-1e-5)&(sub<q-1e-5)&(abs(sub-np.rint(sub))<2e-5)
 possible_over=(sup>q+1e-5)&(sup<=n+1e-5)&(abs(sup-np.rint(sup))<2e-5)
 sign=np.where(possible_sub&~possible_over,-1,
       np.where(possible_over&~possible_sub,1,
        np.where(rs>=1-1e-5,0,99)))
 ambiguous=sign==99
 if not ambiguous.any():return sign
 if reach is None:
  # Without messages, ambiguous cases are unresolved.
  return sign
 # Maximum number of distinct same-prof coworkers reachable within R hops.
 # The simulator masks the jobs matrix to the R-hop graph. The policy DOES
 # NOT inspect nodes outside that mask; this is equivalent to forwarding
 # job labels+unique worker identifiers along each edge.
 draw=reach.sum(1)-1
 x=ownc
 lo=np.rint(sub).astype(int)
 hi=np.rint(sup).astype(int)
 # Bayesian occupancy hypothesis under random-mixing prior, but cluster
 # mismatch can make it poorly calibrated. No global role counts supplied.
 l0=binary_likelihood_log(x,draw[None,:],lo,n)
 l1=binary_likelihood_log(x,draw[None,:],hi,n)
 inferred=np.where(l1>l0,1,-1)
 # Rigorous one-sided certificate: if more than n_sub-1 coworkers seen,
 # the global career cannot possibly be on the subcritical branch.
 inferred=np.where(x>=lo,1,inferred)
 return np.where(ambiguous,inferred,sign)

def main():
 t0=time.perf_counter()
 cases=[]
 for m,k,degree,top,init in itertools.product(MS,KS,DS,TOP,INITS):
  if k>m:continue
  for s in (271001,271009):
   cfg=c.v12.Config(n=120,m=m,k=k,degree=degree,topology=top,
         batch=32,device='cpu')
   e=setup_v(cfg,s+37*m+11*k,init)
   jobs=e.jobs.numpy()
   q=120/k
   counts=e.counts.gather(1,e.jobs).numpy()
   food=e.food.numpy()
   truth=np.sign(counts-q).astype(int)
   noncritical=truth!=0
   match=(jobs[:,:,None]==jobs[:,None,:])
   for R in RADS:
    if R==0:
     estimated,cover=None,0
     sign=classify(food,q,None,None)
    else:
     reach=c.reachable(e.adj.numpy(),R)
     seen=((match&reach[None,:,:]).sum(2)-1)
     sign=classify(food,q,seen,reach)
     cover=int(reach.sum(1).max())
    pred=(sign==truth)
    valid=noncritical
    cases.append(dict(m=m,k=k,degree=degree,topology=top,init=init,
        seed=s,R=R,coverage_nodes=cover,
        accuracy=float(pred.mean()),
        balanced_acc=float(np.mean([
            float(np.mean(pred[truth==label])) if (truth==label).any() else float('nan')
                for label in (-1,1)])),
        accuracy_noncritical=float(pred[valid].mean()) if valid.any() else None,
        accuracy_critical=float(pred[~valid].mean()) if (~valid).any() else None,
        unresolved_fraction=float(np.mean(sign==99)),
        total=truth.size))
  if len(cases)%500==0:
   print('MULTIHOP_PROGRESS',len(cases),m,k,degree,top,init,flush=True)
 out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
 (out/'multihop_regime_v17.json').write_text(json.dumps(
    dict(description='Different local gossip radius R, caller receives only own reward plus roles relayed along R graph hops',
         cases=cases,elapsed_seconds=time.perf_counter()-t0),indent=1),encoding='utf8')
 for k in KS:
  for init in ('trap','cluster'):
   for R in (0,1,2,4,8,16,32):
    z=[x for x in cases if x['k']==k and x['init']==init and x['R']==R and x['degree']==8]
    acc=np.mean([x['accuracy_noncritical'] for x in z if x['accuracy_noncritical'] is not None])
    print('MULTIHOP_SUM',k,init,'R',R,'acc_noncritical',
        round(float(acc),4),'cases',len(z),flush=True)
 print('MULTIHOP_COMPLETE',len(cases),'conditions',flush=True)
if __name__=='__main__':main()
