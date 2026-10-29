"""N110/N111 repaired, preregistered reduced-budget checks; no external data."""
import json,time
import numpy as np
import esbm_dynamic as o
import esbm_schedule_adapter as a

def N110():
 p=o.people(101);e=o.compatibility(p,'general')
 cases=[]
 for rep in range(2):
  perm=np.random.default_rng(10100+rep).permutation(o.N)
  rp={k:(v[:,perm,:][:,:,perm] if isinstance(v,np.ndarray) and v.ndim==3 else v[perm] if isinstance(v,np.ndarray) and v.ndim==1 else v) for k,v in p.items()}
  re=e[perm,:][:,perm]
  for mode in ('pair_greedy','pair_max','pair_budgeted_max'):
   before={frozenset(map(int,pair)) for pair in a.audit_pair_schedule(p,e,np.arange(o.N),0,mode)['events']}
   after={frozenset((int(perm[i]),int(perm[j]))) for i,j in a.audit_pair_schedule(rp,re,np.arange(o.N),0,mode)['events']}
   cases.append(dict(rep=rep,mode=mode,identical=before==after,symmetric_difference=len(before^after),size=len(before)))
 assert len(cases)==6 and all(x['identical'] for x in cases),cases
 return {'status':'PASS','cases':cases,'scope':'Six preselected exact relabel checks, not a universal theorem'}

def N111():
 rows=[]
 for seed in (101,211):
  for name in ('mixed_random','longer_partnerships'):
   for mode in ('pair_greedy','pair_max','pair_budgeted_max'):
    r=a.simulate(seed,name+'_'+mode,{**o.SCENARIOS[name],'schedule_mode':mode,'schedule_slots':1})
    assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
    assert all(0<=t['new_pairs']<=t['reciprocals']<=t['proposals']<=t['impressions'] and t['active_pairs']<=o.N//2 for t in r['track'])
    assert r['total_positive_responses']<=r['total_proposals']<=r['total_impressions']
    rows.append(dict(seed=seed,scenario=name,policy=mode,impressions=r['total_impressions'],formed=r['total_relationships_formed'],dissolved=r['total_dissolutions'],active=r['active_partnerships_end'],gini=r['receiver_impression_gini'],active_share=r['active_agent_share_end']))
 assert len(rows)==12
 return {'status':'PASS','rows':rows,'scope':'12 synthetic 16-tick runs, not matched risk sets after trajectories diverge'}

if __name__=='__main__':
 from pathlib import Path
 result={'schema':'ABH_N110_N111_REPAIRED','date':'2026-10-29','source_sha256_original':a.SOURCE_SHA256,'external_replication':False,'cycles':[]}
 for f in [N110,N111]:
  start=time.perf_counter()
  try:out=f()
  except Exception as exc:out={'status':'INVALID','error':repr(exc)}
  result['cycles'].append(dict(cycle=f.__name__,elapsed_seconds=round(time.perf_counter()-start,3),**out))
  print(f.__name__,out['status'],flush=True)
  if out['status']!='PASS':break
 Path('N110_N111_REPAIRED_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
