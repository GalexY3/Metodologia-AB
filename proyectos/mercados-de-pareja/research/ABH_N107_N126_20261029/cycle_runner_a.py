"""AB-H cycles N107–N111. Pre-outcome registered executable checks.
Run beside immutable esbm_dynamic.py and esbm_schedule_adapter.py; no external files.
"""
import json, time
import numpy as np
import esbm_dynamic as o
import esbm_schedule_adapter as a
SEEDS=[101,211,307,401,503,601]

def N107():
 rows=[]
 for seed in SEEDS:
  for name,config in o.SCENARIOS.items():
   old=o.simulate(seed,name,config); new=a.simulate(seed,name,config)
   assert old==new,(seed,name,'legacy regression')
   rows.append(dict(seed=seed,scenario=name,formed=old['total_relationships_formed']))
 assert len(rows)==60
 return dict(n=60,all_exact=True,rows=rows,next='N108')

def N108():
 count=0
 for seed in SEEDS:
  p=o.people(seed);e=o.compatibility(p,'general')
  for t in range(0,o.STEPS,2):
   for mode in ('pair_max','pair_greedy','pair_budgeted_max'):
    a.audit_pair_schedule(p,e,np.arange(o.N),t,mode);count+=1
 assert count==144
 return dict(valid_risksets=count,next='N109')

def N109():
 rows=[]
 for seed in SEEDS:
  p=o.people(seed);e=o.compatibility(p,'general')
  for t in range(o.STEPS):
   vals={m:a.audit_pair_schedule(p,e,np.arange(o.N),t,m)['pairs'] for m in ('pair_greedy','pair_max','pair_budgeted_max')}
   assert vals['pair_greedy']==vals['pair_budgeted_max'] and vals['pair_max']>=vals['pair_greedy']
   rows.append(dict(seed=seed,tick=t,**vals))
 return dict(common_riskset_equal_budget=96,strict_max_gain=sum(r['pair_max']>r['pair_greedy'] for r in rows),rows=rows,next='N110')

def N110():
 bad=[];checks=0
 for seed in SEEDS[:3]:
  p=o.people(seed);e=o.compatibility(p,'general')
  for rep in range(4):
   perm=np.random.default_rng(seed*100+rep).permutation(o.N)
   rp={k:(v[:,perm,:][:,:,perm] if isinstance(v,np.ndarray) and v.ndim==3 else v[perm] if isinstance(v,np.ndarray) and v.ndim==1 else v) for k,v in p.items()}
   re=e[perm,:][:,perm]
   for mode in ('pair_max','pair_greedy','pair_budgeted_max'):
    before={frozenset((int(i),int(j))) for i,j in a.audit_pair_schedule(p,e,np.arange(o.N),0,mode)['events']}
    after={frozenset((int(perm[i]),int(perm[j]))) for i,j in a.audit_pair_schedule(rp,re,np.arange(o.N),0,mode)['events']}
    checks+=1
    if before!=after:bad.append(dict(seed=seed,rep=rep,mode=mode,symmetric_difference=len(before^after)))
 assert not bad,bad
 return dict(relabel_checks=checks,failures=bad,next='N111')

def N111():
 rows=[]
 for seed in SEEDS:
  for name in ('mixed_random','institutional_segregation','longer_partnerships','shorter_partnerships'):
   for mode in ('pair_max','pair_greedy','pair_budgeted_max'):
    r=a.simulate(seed,name+'_'+mode,{**o.SCENARIOS[name],'schedule_mode':mode,'schedule_slots':1})
    assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
    assert all(0<=t['new_pairs']<=t['reciprocals']<=t['proposals']<=t['impressions'] and t['active_pairs']<=o.N//2 for t in r['track'])
    rows.append(dict(seed=seed,scenario=name,mode=mode,impressions=r['total_impressions'],formed=r['total_relationships_formed'],dissolved=r['total_dissolutions'],active=r['active_partnerships_end'],gini=r['receiver_impression_gini']))
 assert len(rows)==72
 return dict(runs=72,rows=rows,warning='Differences in dynamic risk sets invalidate equal total exposure budget; descriptive simulation only',next='Design adaptive N112-N116')

def run():
 outcomes=[]
 for f in [N107,N108,N109,N110,N111]:
  start=time.perf_counter()
  try: result=f(); status='PASS'
  except Exception as exc:
   result=dict(error=str(exc));status='INVALID'
  outcomes.append(dict(cycle=f.__name__,status=status,elapsed_seconds=round(time.perf_counter()-start,2),**result))
  print(f.__name__,status,flush=True)
  if status!='PASS': break
 return outcomes
if __name__=='__main__':
 from pathlib import Path
 data={'schema':'ABH_BLOCK_A_EXECUTION','pre_registered':True,'external':False,'original_sha256':a.SOURCE_SHA256,'cycles':run()}
 Path('BLOCK_A_RESULTS.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
