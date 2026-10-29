"""AB-H N122-N126 preregistered engineering/robustness checks (synthetic)."""
from pathlib import Path
import json,time,hashlib,tempfile,shutil,subprocess,sys
import numpy as np
import esbm_dynamic as o
import esbm_schedule_adapter as a
import small_fixture as f

def N122():
 rows=[]
 for seed in range(1000,1060):
  out={}
  for slots in (1,2):
   r=f.simulate_small(seed,'slotdose',{**o.SCENARIOS['mixed_random'],'schedule_mode':'pair_max','schedule_slots':slots})
   assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
   out[slots]=(r['total_impressions'],r['total_relationships_formed'],r['active_partnerships_end'])
  rows.append(dict(seed=seed,one=out[1],two=out[2],delta_active=out[2][2]-out[1][2]))
 assert len(rows)==60
 d=[x['delta_active'] for x in rows]
 return dict(status='PASS',runs=120,mean_delta_active=sum(d)/len(d),positive=sum(v>0 for v in d),negative=sum(v<0 for v in d),ties=sum(v==0 for v in d),min_delta=min(d),max_delta=max(d),rows=rows)

def N123():
 rows=[]
 for seed in range(2000,2060):
  for mode in ('pair_max','pair_norm_same','pair_norm_cross'):
   r=f.simulate_small(seed,'norm',{**o.SCENARIOS['mixed_random'],'schedule_mode':mode,'schedule_slots':2})
   assert r['total_relationships_formed']-r['total_dissolutions']==r['active_partnerships_end']
   rows.append(dict(seed=seed,mode=mode,impressions=r['total_impressions'],formed=r['total_relationships_formed'],active=r['active_partnerships_end'],same_exposure=r['group_same_exposure'],same_couples=r['group_same_new_couples']))
 assert len(rows)==180
 by_mode={}
 for mode in ('pair_max','pair_norm_same','pair_norm_cross'):
  r=[x for x in rows if x['mode']==mode]
  by_mode[mode]=dict(mean_formed=sum(x['formed'] for x in r)/60,mean_active=sum(x['active'] for x in r)/60,mean_same_exposure=sum(x['same_exposure'] for x in r if x['same_exposure'] is not None)/sum(x['same_exposure'] is not None for x in r))
 return dict(status='PASS',runs=180,by_mode=by_mode,rows=rows)

def N124():
 checks=[]
 for seed in (101,211):
  p=f.people_small(seed);eligible=f.compatibility_small(p,'general')
  for rep in range(3):
   perm=np.random.default_rng(seed*1000+rep).permutation(f.N)
   rp={k:(v[:,perm,:][:,:,perm] if isinstance(v,np.ndarray) and v.ndim==3 else v[perm] if isinstance(v,np.ndarray) and v.ndim==1 else v) for k,v in p.items()}
   re=eligible[perm,:][:,perm]
   for mode in ('pair_max','pair_norm_same','pair_norm_cross'):
    before={frozenset(map(int,e)) for e in a.audit_pair_schedule(p,eligible,np.arange(f.N),0,mode,slots=2)['events']}
    after={frozenset((int(perm[i]),int(perm[j]))) for i,j in a.audit_pair_schedule(rp,re,np.arange(f.N),0,mode,slots=2)['events']}
    checks.append(dict(seed=seed,rep=rep,mode=mode,exact=(before==after),diff=len(before^after)))
 assert len(checks)==18 and all(x['exact'] for x in checks),checks
 return dict(status='PASS',checks=18,rows=checks)

def N125():
 p=f.people_small(101);e=f.compatibility_small(p,'general')
 failures=[]
 for label,fn in [
  ('unsupported_mode',lambda:list(a.opportunities(p,e,np.arange(f.N),o.SCENARIOS['mixed_random'],np.zeros(f.N,int),0,'nonsense',1))),
  ('unsupported_slot_count',lambda:list(a.opportunities(p,e,np.arange(f.N),o.SCENARIOS['mixed_random'],np.zeros(f.N,int),0,'pair_max',3)))]:
  try:fn(); raise AssertionError('Unexpectedly accepted invalid '+label)
  except ValueError:failures.append(label)
 with tempfile.TemporaryDirectory() as d:
  for src in (Path(o.__file__),Path(a.__file__)):shutil.copy2(src,Path(d)/src.name)
  path=Path(d)/'esbm_dynamic.py'
  path.write_bytes(path.read_bytes()+b'\n# intentionally corrupted external fixture\n')
  code="import sys;sys.path.insert(0,"+repr(d)+");import esbm_schedule_adapter"
  r=subprocess.run([sys.executable,'-I','-c',code],capture_output=True,text=True,timeout=20)
  assert r.returncode!=0 and 'Origin changed' in r.stderr, r.stderr[-1000:]
  failures.append('original_sha_tamper_detected')
 return dict(status='PASS',fail_closed_checks=3,checks=failures)

def N126():
 with tempfile.TemporaryDirectory() as d:
  for source in (Path(o.__file__),Path(a.__file__),Path(f.__file__)):
   shutil.copy2(source,Path(d)/source.name)
  code=("import sys,json,hashlib;sys.path.insert(0,"+repr(d)+");"
    "import esbm_dynamic as o,esbm_schedule_adapter as a,small_fixture as f;"
    "r=o.simulate(101,'legacy',o.SCENARIOS['mixed_random']);"
    "s=a.simulate(101,'legacy',o.SCENARIOS['mixed_random']);"
    "assert r==s;"
    "t=f.simulate_small(101,'mini',{**o.SCENARIOS['mixed_random'],'schedule_mode':'pair_max','schedule_slots':2});"
    "assert (t['total_relationships_formed'],t['active_partnerships_end'])==(5,4);"
    "print(json.dumps({'legacy_formed':r['total_relationships_formed'],'mini_formed':t['total_relationships_formed'],'mini_active':t['active_partnerships_end']}))")
  z=subprocess.run([sys.executable,'-I','-c',code],capture_output=True,text=True,timeout=30)
  assert z.returncode==0,z.stderr[-1200:]
  result=json.loads(z.stdout.strip().splitlines()[-1])
 assert result['legacy_formed']==224
 return dict(status='PASS',isolated_process=True,did_not_download_external_data=True,verified=result,scope='Same installed Python environment, temporary clean source directory, not independent OS replication')

if __name__=='__main__':
 output=dict(schema='ABH.N122_N126_EXECUTED.v1',external=False,cycles=[])
 for fn in (N122,N123,N124,N125,N126):
  st=time.perf_counter()
  try:v=fn()
  except Exception as exc:v=dict(status='INVALID',error=repr(exc))
  output['cycles'].append(dict(id=fn.__name__,seconds=round(time.perf_counter()-st,3),**v))
  print(fn.__name__,v['status'],flush=True)
  if v['status']!='PASS':break
 Path('BLOCK_D_RESULTS.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf8')
