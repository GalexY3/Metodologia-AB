"""Pre-outcome frozen AB-H N117-N121 two-slot, sham and temporal tests; synthetic only."""
import json,time,hashlib
import numpy as np
import esbm_dynamic as o
import esbm_schedule_adapter as a
import esbm_schedule_adapter_v3 as v3
from pathlib import Path
assert hashlib.sha256(Path(v3.__file__).read_bytes()).hexdigest()=='5730fd224f86fedb5626e7ee38743fce3a0c95955c031301694e48068f5bbaa7'
SEEDS=[101,211,307,401,503,601]
def N117():
 rows=[]
 for seed in SEEDS:
  p=o.people(seed);e=o.compatibility(p,'general')
  for t in (0,3):
   for slots in (1,2):
    z=a.audit_pair_schedule(p,e,np.arange(o.N),t,'pair_max',slots=slots)
    assert z['pairs']==z['unique_dyads'] and z['max_actor_visits']<=slots
    rows.append(dict(seed=seed,tick=t,slots=slots,encounters=z['pairs'],max_actor_visits=z['max_actor_visits']))
 assert len(rows)==24
 return dict(status='PASS',risksets=24,rows=rows,next='N118')
def N118():
 rows=[]
 for seed in (101,211):
  for mode in ('pair_max','pair_norm_same','pair_norm_cross'):
   c={**o.SCENARIOS['mixed_random'],'schedule_mode':mode,'schedule_slots':1}
   old=v3.simulate(seed,'test',c)
   new=a.simulate(seed,'test',c)
   assert old==new,(seed,mode,'one slot changed')
   rows.append(dict(seed=seed,mode=mode,exact=True,formed=old['total_relationships_formed']))
 assert len(rows)==6
 return dict(status='PASS',full_trajectory_exact=6,rows=rows,next='N119')
def N119():
 rows=[]
 for seed in SEEDS:
  p=o.people(seed);e=o.compatibility(p,'general')
  for t in (0,3):
   for mode in ('pair_max','pair_greedy','pair_norm_same'):
    a1=a.audit_pair_schedule(p,e,np.arange(o.N),t,mode,slots=1)
    a2=a.audit_pair_schedule(p,e,np.arange(o.N),t,mode,slots=2)
    assert a2['pairs']>=a1['pairs'] and a2['max_actor_visits']<=2
    rows.append(dict(seed=seed,tick=t,mode=mode,one_slot=a1['pairs'],two_slots=a2['pairs']))
 assert len(rows)==36
 return dict(status='PASS',checks=36,rows=rows,warning='u_slot uses a deterministic modular transform of the same finite shocks, not independent encounter realizations',next='N120')
def N120():
 rows=[]
 for seed in (101,211):
  for private in (False,True):
   c={**o.SCENARIOS['mixed_random'],'private':private,'schedule_mode':'pair_max','schedule_slots':2}
   r=a.simulate(seed,'two_slots_feedback',c)
   assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
   rows.append(dict(seed=seed,private=private,proposals=r['total_proposals'],positive_responses=r['total_positive_responses'],formed=r['total_relationships_formed'],active=r['active_partnerships_end'],bias=r['final_private_aspiration_bias_mean']))
 assert len(rows)==4
 return dict(status='PASS',runs=4,rows=rows,next='N121')
def N121():
 rows=[]
 for seed in (101,211):
  for name in ('longer_partnerships','mixed_random','shorter_partnerships'):
   c={**o.SCENARIOS[name],'schedule_mode':'pair_max','schedule_slots':2}
   r=a.simulate(seed,name,c)
   assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
   assert r['right_censored_count']==r['active_partnerships_end']
   rows.append(dict(seed=seed,scenario=name,formed=r['total_relationships_formed'],dissolved=r['total_dissolutions'],active=r['active_partnerships_end'],right_censored=r['right_censored_count'],completed_mean=r['duration_completed_mean'],completed_n=r['duration_completed_n']))
 assert len(rows)==6
 return dict(status='PASS',runs=6,rows=rows,warning='Completed-duration mean excludes right-censored relationships; no inference about human stability',next='Reassess whether N122-N126 would add independent scientific evidence')
if __name__=='__main__':
 result={'schema':'ABH.N117_N121_RESULTS','external':False,'cycles':[]}
 for f in (N117,N118,N119,N120,N121):
  st=time.perf_counter()
  try:r=f()
  except Exception as e:r=dict(status='INVALID',error=repr(e))
  result['cycles'].append(dict(cycle=f.__name__,seconds=round(time.perf_counter()-st,3),**r))
  print(f.__name__,r['status'],flush=True)
  if r['status']!='PASS':break
 Path('BLOCK_C_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
