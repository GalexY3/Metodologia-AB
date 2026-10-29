"""N120-121 repaired miniature 24x4 trials; source prereg and fixture committed first."""
import json,time
import small_fixture as f
import esbm_dynamic as o
def N120():
 rows=[]
 for seed in (101,211):
  for private in (False,True):
   c={**o.SCENARIOS['mixed_random'],'private':private,'schedule_mode':'pair_max','schedule_slots':2}
   r=f.simulate_small(seed,'mini_feedback',c)
   assert r['n_agents']==24 and len(r['track'])==4
   assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
   rows.append(dict(seed=seed,private=private,formed=r['total_relationships_formed'],active=r['active_partnerships_end'],proposals=r['total_proposals'],positive=r['total_positive_responses'],bias=r['final_private_aspiration_bias_mean']))
 return dict(status='PASS',runs=4,rows=rows)
def N121():
 rows=[]
 for seed in (101,211):
  for name in ('longer_partnerships','mixed_random','shorter_partnerships'):
   r=f.simulate_small(seed,'mini_'+name,{**o.SCENARIOS[name],'schedule_mode':'pair_max','schedule_slots':2})
   assert r['n_agents']==24 and len(r['track'])==4
   assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
   assert r['right_censored_count']==r['active_partnerships_end']
   rows.append(dict(seed=seed,scenario=name,formed=r['total_relationships_formed'],dissolved=r['total_dissolutions'],active=r['active_partnerships_end'],censored=r['right_censored_count'],complete_mean=r['duration_completed_mean'],complete_n=r['duration_completed_n']))
 return dict(status='PASS',runs=6,rows=rows)
if __name__=='__main__':
 from pathlib import Path
 r={'schema':'ABH.MINI_REPAIR_C','n_agents':24,'ticks':4,'human_data':0,'cycles':[]}
 for fn in (N120,N121):
  st=time.perf_counter()
  try:z=fn()
  except Exception as ex:z=dict(status='INVALID',error=repr(ex))
  r['cycles'].append(dict(id=fn.__name__,elapsed=round(time.perf_counter()-st,3),**z))
  print(fn.__name__,z['status'],flush=True)
  if z['status']!='PASS':break
 Path('N120_N121_REPAIRED_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
