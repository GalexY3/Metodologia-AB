"""Synthetic N24x4 providers. No original ESBM mutation, no runtime exec.
These synthetic gender/scope values are NOT population frequencies.
"""
import numpy as np
import esbm_dynamic as original
N=24
TICKS=4
def people(seed):
 p=original.people(seed)
 return {k:(v[:TICKS,:N,:N].copy() if isinstance(v,np.ndarray) and v.ndim==3 else v[:N].copy() if isinstance(v,np.ndarray) and v.ndim==1 else v) for k,v in p.items()}
def compatibility(p,mode):
 g=p['genders'];scope=p['scopes'];edges=np.zeros((N,N),dtype=bool)
 for i in range(N):
  for j in range(i+1,N):
   if mode=='FM_only':valid=(g[i]=='F' and g[j]=='M') or (g[i]=='M' and g[j]=='F')
   else:
    ai=(scope[i]=='all' or (scope[i]=='same' and g[i]==g[j]) or (scope[i]=='other' and g[i]!=g[j]))
    aj=(scope[j]=='all' or (scope[j]=='same' and g[j]==g[i]) or (scope[j]=='other' and g[j]!=g[i]))
    valid=bool(ai and aj)
   edges[i,j]=edges[j,i]=valid
 return edges
def simulate(engine,seed,scenario,config,*,trace=False,scheduler=None):
 return engine.simulate(seed,scenario,config,scheduler=scheduler,trace=trace,people_provider=people,compatibility_provider=compatibility,population_size=N,steps=TICKS)
