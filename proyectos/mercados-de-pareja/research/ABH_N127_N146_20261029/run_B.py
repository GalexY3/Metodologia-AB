"""N132–N136, 30 artificial social networks; preoutcome fixed runner."""
import hashlib,json,time
from pathlib import Path
import numpy as np
import esbm_dynamic as original
import esbm_event_engine as engine
import mini_world as mini
import social_graph as sg
SEEDS=range(3000,3030)
def N132():
 rows=[]
 for seed in SEEDS:
  p=mini.people(seed);g=sg.build(p,seed,'ring');s=sg.stats(g,p,mini.compatibility(p,'general'))
  assert s['connected'] and s['edges']==48 and s['degree_sequence']==[4]*24
  rows.append(dict(seed=seed,eligible_edges=s['eligible_edges'],mean_q_gap=s['mean_quality_difference']))
 return dict(status='PASS',checks=30,rows=rows)
def N133():
 rows=[]
 for seed in SEEDS:
  p=mini.people(seed);a=sg.build(p,seed,'ring');b=sg.build(p,seed,'rewired')
  assert sorted(dict(a.degree()).values())==sorted(dict(b.degree()).values())==[4]*24
  overlap=len({frozenset(e) for e in a.edges()}&{frozenset(e) for e in b.edges()})
  rows.append(dict(seed=seed,overlap=overlap,ring_edges=len(a.edges()),rewired_edges=len(b.edges())))
 return dict(status='PASS',checks=30,all_exact_degree_preserving=True,rows=rows)
def N134():
 rows=[]
 for seed in SEEDS:
  p=mini.people(seed);eligible=mini.compatibility(p,'general');cfg=original.SCENARIOS['mixed_random']
  for kind in ('ring','rewired'):
   g=sg.build(p,seed,kind);stats=sg.stats(g,p,eligible)
   schedule=sg.scheduler(g)
   meetings=list(schedule(p,eligible,np.arange(24),cfg,np.zeros(24,int),0,'pair_max',1))
   assert len(meetings)<=12 and len({i for edge in meetings for i in edge})==2*len(meetings)
   assert all(g.has_edge(i,j) and eligible[i,j] for i,j in meetings)
   rows.append(dict(seed=seed,kind=kind,riskset_eligible=stats['eligible_edges'],meetings=len(meetings),
                    same_group=sum(p['norm'][i]==p['norm'][j] for i,j in meetings)/len(meetings) if meetings else None))
 return dict(status='PASS',fixed_riskset_checks=60,rows=rows)
def N135():
 rows=[]
 for seed in SEEDS:
  p=mini.people(seed);cfg={**original.SCENARIOS['mixed_random'],'schedule_mode':'pair_max','schedule_slots':1}
  for kind in ('ring','rewired'):
   r=mini.simulate(engine,seed,'net_'+kind,cfg,scheduler=sg.scheduler(sg.build(p,seed,kind)))
   assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
   rows.append(dict(seed=seed,kind=kind,formed=r['total_relationships_formed'],active=r['active_partnerships_end'],
                    impressions=r['total_impressions'],same_couples=r['group_same_new_couples']))
 assert len(rows)==60
 paired=[]
 for seed in SEEDS:
  x=next(r for r in rows if r['seed']==seed and r['kind']=='ring')
  y=next(r for r in rows if r['seed']==seed and r['kind']=='rewired')
  paired.append(dict(seed=seed,delta_active_ring_minus_rewired=x['active']-y['active'],delta_exposure=x['impressions']-y['impressions']))
 return dict(status='PASS',runs=60,paired=paired,rows=rows)
def N136():
 rows=[]
 for seed in SEEDS:
  p=mini.people(seed);eligible=mini.compatibility(p,'general')
  for kind in ('ring','rewired'):
   s=sg.stats(sg.build(p,seed,kind),p,eligible)
   rows.append(dict(seed=seed,kind=kind,cross_norm=s['cross_norm_edges'],eligible=s['eligible_edges'],q_gap=s['mean_quality_difference']))
 assert len(rows)==60
 return dict(status='PASS',checks=60,rows=rows)
def run():
 a=[]
 for fn in (N132,N133,N134,N135,N136):
  t=time.perf_counter()
  try:z=fn()
  except Exception as err:z=dict(status='INVALID',error=repr(err))
  a.append(dict(id=fn.__name__,seconds=round(time.perf_counter()-t,4),**z))
  print(fn.__name__,z['status'],flush=True)
  if z['status']!='PASS':break
 return a
if __name__=='__main__':
 out=dict(schema='ABH_NETWORK_RESULTS',original_sha=engine.SOURCE_SHA256,source_sha=hashlib.sha256(Path(sg.__file__).read_bytes()).hexdigest(),cycles=run())
 Path('RESULTS_B.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
