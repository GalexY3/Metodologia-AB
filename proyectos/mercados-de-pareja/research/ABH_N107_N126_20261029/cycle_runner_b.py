"""AB-H N112-N116 frozen block: synthetic norm-conditioned scheduling, no human data."""
import json,time
import numpy as np
import esbm_dynamic as o
import esbm_schedule_adapter as a
SEEDS=[101,211,307,401,503,601]
def plan(p,e,t,mode):
 return a.audit_pair_schedule(p,e,np.arange(o.N),t,mode)['events']
def fraction(p,edges):
 return sum(int(p['norm'][i]==p['norm'][j]) for i,j in edges)/len(edges) if edges else None
def N112():
 checks=[];modes=('pair_max','pair_norm_same','pair_norm_cross')
 for seed in SEEDS:
  p=o.people(seed);e=o.compatibility(p,'general')
  for t in (0,3):
   for mode in modes:
    edges=plan(p,e,t,mode)
    checks.append(dict(seed=seed,tick=t,mode=mode,encounters=len(edges),same_group_fraction=fraction(p,edges)))
 assert len(checks)==36 and all(x['encounters']<=o.N//2 for x in checks)
 return dict(status='PASS',risksets=36,rows=checks,next='N113')
def N113():
 checks=[]
 for seed in SEEDS:
  p=o.people(seed);e=o.compatibility(p,'general')
  for t in (0,3):
   s={frozenset(x) for x in plan(p,e,t,'pair_sham')}
   b={frozenset(x) for x in plan(p,e,t,'pair_max')}
   assert s==b
   checks.append(dict(seed=seed,tick=t,edges=len(b),exact=True))
 runs=[]
 for seed in (101,211):
  config=o.SCENARIOS['mixed_random']
  a0=a.simulate(seed,'baseline',{**config,'schedule_mode':'pair_max'})
  b0=a.simulate(seed,'sham',{**config,'schedule_mode':'pair_sham'})
  # Only scenario label is different. Remove it from exact comparison.
  a0.pop('scenario');b0.pop('scenario')
  assert a0==b0,'Sham differs'
  runs.append(dict(seed=seed,exact_full_run=True,formed=a0['total_relationships_formed']))
 return dict(status='PASS',risksets=12,full_run_shams=2,rows=checks,shams=runs,next='N114')
def N114():
 cases=[]
 for seed in SEEDS:
  p=o.people(seed);e=o.compatibility(p,'general')
  for t in (0,3):
   stats={}
   for mode in ('pair_max','pair_norm_same','pair_norm_cross'):
    edges=plan(p,e,t,mode);stats[mode]=dict(encounters=len(edges),same_group_fraction=fraction(p,edges))
   cases.append(dict(seed=seed,tick=t,**stats))
 assert len(cases)==12
 changed=sum(x['pair_norm_same']['same_group_fraction'] != x['pair_norm_cross']['same_group_fraction'] for x in cases)
 assert changed>0,'No composition contrast on all fixed risksets'
 return dict(status='PASS',risksets=12,changed=changed,rows=cases,next='N115')
def N115():
 rows=[]
 for seed in (101,211):
  for mode in ('pair_max','pair_norm_same','pair_norm_cross'):
   r=a.simulate(seed,'random_'+mode,{**o.SCENARIOS['mixed_random'],'schedule_mode':mode})
   assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
   rows.append(dict(seed=seed,mode=mode,impressions=r['total_impressions'],formed=r['total_relationships_formed'],dissolved=r['total_dissolutions'],active=r['active_partnerships_end'],same_exposures=r['group_same_exposure'],same_formed=r['group_same_new_couples'],gini=r['receiver_impression_gini']))
 assert len(rows)==6
 return dict(status='PASS',runs=6,rows=rows,next='N116')
def N116():
 rows=[]
 for seed in (101,211):
  p=o.people(seed);e=o.compatibility(p,'general')
  shuffled=p.copy();shuffled['norm']=p['norm'][np.random.default_rng(seed+10000).permutation(o.N)]
  for t in (0,3):
   for mode in ('pair_max','pair_norm_same','pair_norm_cross'):
    aa={frozenset(x) for x in plan(p,e,t,mode)}
    bb={frozenset(x) for x in plan(shuffled,e,t,mode)}
    changed=len(aa^bb)
    if mode=='pair_max':assert changed==0
    rows.append(dict(seed=seed,tick=t,mode=mode,symmetric_difference=changed))
 assert len(rows)==12
 valid_signal=sum(x['symmetric_difference']>0 for x in rows if x['mode']!='pair_max')
 return dict(status='PASS' if valid_signal else 'INCONCLUSIVE',risksets=12,norm_response_checks=valid_signal,rows=rows,next='Assess capability, R5 and independent contrasts before next block')
if __name__=='__main__':
 from pathlib import Path
 out={'schema':'ABH_N112_N116_SYNTHETIC','preregistered':True,'external':False,'cycles':[]}
 for f in (N112,N113,N114,N115,N116):
  st=time.perf_counter()
  try:result=f()
  except Exception as ex:result=dict(status='INVALID',error=repr(ex))
  out['cycles'].append(dict(cycle=f.__name__,seconds=round(time.perf_counter()-st,3),**result))
  print(f.__name__,result['status'],flush=True)
  if result['status']!='PASS':break
 Path('BLOCK_B_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
