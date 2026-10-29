"""Frozen N137–N141: joint network/slots, right censor and artificial quality; no humans."""
import json,time
from pathlib import Path
import numpy as np
import esbm_dynamic as original
import esbm_event_engine as engine
import mini_world as mini
import social_graph as sg
SEEDS=range(4000,4030)
def reconstruct(events,p,horizon):
 active={};records=[];tick_quality=[]
 for t in range(horizon):
  for e in (e for e in events if e['t']==t):
   pair=tuple(sorted((e['i'],e['j'])))
   if e['stage']=='dissolution':
    assert pair in active
    start,q=active.pop(pair)
    records.append(dict(duration=t-start,event=1,q=q))
   if e['stage']=='formation':
    assert pair not in active
    quality=1-abs(float(p['q'][pair[0]])-float(p['q'][pair[1]]))
    assert 0<=quality<=1
    active[pair]=(t,quality)
  tick_quality.append(sum(q for _,q in active.values()))
 for start,q in active.values():records.append(dict(duration=horizon-start,event=0,q=q))
 return dict(records=records,tick_quality=tick_quality,active_at_end=len(active))
def km_rmst(rows,tau=3):
 if not rows:return None
 s=1.;area=0.;survivals=[]
 for t in range(1,tau+1):
  area+=s
  risk=sum(r['duration']>=t for r in rows)
  failed=sum(r['duration']==t and r['event']==1 for r in rows)
  if risk:s*=1-failed/risk
  survivals.append(s)
 assert all(x>=y for x,y in zip([1.]+survivals,survivals))
 return dict(rmst=area,survival=survivals)
def all_runs():
 rows=[]
 for seed in SEEDS:
  p=mini.people(seed)
  for kind in ('ring','rewired'):
   graph=sg.build(p,seed,kind)
   for slots in (1,2):
    c={**original.SCENARIOS['mixed_random'],'schedule_mode':'pair_max','schedule_slots':slots}
    r=mini.simulate(engine,seed,'trial',c,trace=True,scheduler=sg.scheduler(graph))
    metrics=reconstruct(r['events'],p,4)
    assert len(metrics['records'])==r['total_relationships_formed']
    assert sum(x['event'] for x in metrics['records'])==r['total_dissolutions']
    assert metrics['active_at_end']==r['active_partnerships_end']
    assert sum(1-x['event'] for x in metrics['records'])==r['right_censored_count']
    assert all(x['duration']>=1 for x in metrics['records'])
    assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
    row=dict(seed=seed,network=kind,slots=slots,formed=r['total_relationships_formed'],active=r['active_partnerships_end'],
             impressions=r['total_impressions'],gini=r['receiver_impression_gini'],never_seen=r['never_displayed_receivers'],
             quality_sum=float(sum(x['q'] for x in metrics['records'])),quality_mean=float(np.mean([x['q'] for x in metrics['records']])) if metrics['records'] else None,
             pairtime_quality=float(sum(metrics['tick_quality'])),pairtime=float(sum(t['active_pairs'] for t in r['track'])),
             naive_completed_duration=r['duration_completed_mean'],censored=r['right_censored_count'],
             km=km_rmst(metrics['records']),records=metrics['records'])
    rows.append(row)
 assert len(rows)==120
 return rows
def N137(rows):
 data=[]
 for seed in SEEDS:
  for kind in ('ring','rewired'):
   a=next(z for z in rows if z['seed']==seed and z['network']==kind and z['slots']==1)
   b=next(z for z in rows if z['seed']==seed and z['network']==kind and z['slots']==2)
   data.append(dict(seed=seed,network=kind,delta_active=b['active']-a['active'],delta_impressions=b['impressions']-a['impressions']))
 return dict(status='PASS',paired=60,rows=data)
def N138(rows):
 comparisons=[]
 for seed in SEEDS:
  p=mini.people(seed);eligible=mini.compatibility(p,'general')
  for network in ('ring','rewired'):
   g=sg.build(p,seed,network);stat=sg.stats(g,p,eligible)
   for slots in (1,2):
    row=next(z for z in rows if z['seed']==seed and z['network']==network and z['slots']==slots)
    comparisons.append(dict(seed=seed,network=network,slots=slots,eligible_edges=stat['eligible_edges'],realized_impressions=row['impressions']))
 assert len(comparisons)==120
 return dict(status='PASS',cases=120,rows=comparisons)
def N139(rows):
 summary=[]
 for kind in ('ring','rewired'):
  subset=[z for z in rows if z['network']==kind and z['slots']==2]
  allrecords=[r for z in subset for r in z['records']]
  k=km_rmst(allrecords)
  assert k and k['rmst']>=1
  completed=[r['duration'] for r in allrecords if r['event']==1]
  summary.append(dict(network=kind,relationships=len(allrecords),censored=sum(1-r['event'] for r in allrecords),
                      completed_only_mean=float(np.mean(completed)) if completed else None,restricted_mean_survival_t3=k['rmst'],survivals=k['survival']))
 return dict(status='PASS',populations=2,rows=summary)
def N140(rows):
 pairdata=[]
 for seed in SEEDS:
  for slots in (1,2):
   a=next(z for z in rows if z['seed']==seed and z['network']=='ring' and z['slots']==slots)
   b=next(z for z in rows if z['seed']==seed and z['network']=='rewired' and z['slots']==slots)
   pairdata.append(dict(seed=seed,slots=slots,delta_formed=a['formed']-b['formed'],
        delta_quality_sum=a['quality_sum']-b['quality_sum'],delta_active=a['active']-b['active'],
        delta_pairtime_quality=a['pairtime_quality']-b['pairtime_quality']))
 return dict(status='PASS',contrasts=60,rows=pairdata,warning='q-distance utility is arbitrary proxy, NOT self-reported satisfaction or wellbeing')
def N141(rows):
 paired=[]
 for seed in SEEDS:
  for slots in (1,2):
   x=next(z for z in rows if z['seed']==seed and z['network']=='ring' and z['slots']==slots)
   y=next(z for z in rows if z['seed']==seed and z['network']=='rewired' and z['slots']==slots)
   paired.append(dict(seed=seed,slots=slots,delta_gini=x['gini']-y['gini'],delta_never_seen=x['never_seen']-y['never_seen'],delta_active=x['active']-y['active']))
 return dict(status='PASS',contrasts=60,rows=paired,interpretation='Synthetic display inequality, NOT social welfare or real-world fairness')
def run():
 allrows=all_runs();out=[]
 for fn in (N137,N138,N139,N140,N141):
  st=time.perf_counter()
  try:z=fn(allrows)
  except Exception as ex:z=dict(status='INVALID',error=repr(ex))
  out.append(dict(id=fn.__name__,seconds=round(time.perf_counter()-st,4),**z))
  print(fn.__name__,z['status'],flush=True)
  if z['status']!='PASS':break
 return dict(cycles=out,full_runs=120,results=allrows)
if __name__=='__main__':
 a=run()
 Path('RESULTS_C.json').write_text(json.dumps(a,indent=2,allow_nan=False)+'\n')
