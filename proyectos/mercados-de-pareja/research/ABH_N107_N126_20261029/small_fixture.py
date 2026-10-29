"""Miniature, non-destructive ESBM 24x4 fixture for N120/N121 post-timeout repair.
Not an estimator for human outcomes and not the historical N=144 trajectory.
"""
import hashlib
from pathlib import Path
from types import FunctionType
import numpy as np
import esbm_dynamic as original
import esbm_schedule_adapter as adapter

N=24; TICKS=4
ORIGINAL_SHA='f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b'
assert hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest()==ORIGINAL_SHA

def people_small(seed):
 p=original.people(seed)
 out={}
 for key,value in p.items():
  if isinstance(value,np.ndarray) and value.ndim==3:out[key]=value[:TICKS,:N,:N].copy()
  elif isinstance(value,np.ndarray) and value.ndim==1:out[key]=value[:N].copy()
  else:out[key]=value
 return out

def compatibility_small(p, mode):
 g=p['genders'];scope=p['scopes'];edges=np.zeros((N,N),dtype=bool)
 for i in range(N):
  for j in range(i+1,N):
   if mode=='FM_only':valid=(g[i]=='F' and g[j]=='M') or (g[i]=='M' and g[j]=='F')
   else:
    x=(scope[i]=='all' or (scope[i]=='same' and g[i]==g[j]) or (scope[i]=='other' and g[i]!=g[j]))
    y=(scope[j]=='all' or (scope[j]=='same' and g[j]==g[i]) or (scope[j]=='other' and g[j]!=g[i]))
    valid=bool(x and y)
   edges[i,j]=edges[j,i]=valid
 return edges

def simulate_small(seed,scenario,config):
 ns=dict(adapter.simulate.__globals__)
 ns['N']=N;ns['STEPS']=TICKS;ns['people']=people_small;ns['compatibility']=compatibility_small
 f=FunctionType(adapter.simulate.__code__,ns,name='simulate_small')
 return f(seed,scenario,config)
