"""N127-N131 frozen acceptance runner. Own tests, synthetic; 0/3 science."""
import ast, hashlib, json, math, shutil, subprocess, sys, tempfile, time
from collections import Counter
from pathlib import Path
import numpy as np
import esbm_dynamic as original
import esbm_event_engine as engine
import esbm_schedule_adapter as old
import small_fixture as oldmini
import mini_world as mini
SOURCE_SHA="f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b"
assert hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest()==SOURCE_SHA
def N127():
 rows=[]
 for seed in original.SEEDS:
  for name,config in original.SCENARIOS.items():
   a=original.simulate(seed,name,config)
   b=engine.simulate(seed,name,config)
   assert a==b,(seed,name)
   rows.append(dict(seed=seed,scenario=name,formed=a['total_relationships_formed'],active=a['active_partnerships_end']))
 assert len(rows)==60
 return dict(passed=60,rows=rows)
def N128():
 cases=[]
 for seed in (101,211):
  for mode,slots in [('pair_max',1),('pair_greedy',2),('pair_norm_same',2)]:
   config={**original.SCENARIOS['mixed_random'],'schedule_mode':mode,'schedule_slots':slots}
   a=oldmini.simulate_small(seed,'test',config)
   b=mini.simulate(engine,seed,'test',config)
   aa=dict(a);bb=dict(b)
   for key in ('active_share_by_gender',):
    aa.pop(key,None);bb.pop(key,None)
   assert aa==bb,(seed,mode,slots)
   cases.append(dict(seed=seed,mode=mode,slots=slots,formed=b['total_relationships_formed'],active=b['active_partnerships_end']))
 return dict(exact_except_absent_category_policy=6,rows=cases)
def N129():
 results=[]
 for seed in (101,211):
  cfg={**original.SCENARIOS['mixed_random'],'schedule_mode':'pair_max','schedule_slots':2}
  r=mini.simulate(engine,seed,'traced',cfg,trace=True)
  c=Counter(x['stage'] for x in r['events'])
  assert c['exposure']==r['total_impressions']
  assert c['proposal']==r['total_proposals']
  assert c['positive_response']==r['total_positive_responses']
  assert c['negative_response']+c['positive_response']==c['proposal']
  assert c['formation']==r['total_relationships_formed']
  assert c['dissolution']==r['total_dissolutions']
  assert all(0<=x['t']<4 and 0<=x['i']<24 and 0<=x['j']<24 and x['i']!=x['j'] for x in r['events'])
  results.append(dict(seed=seed,events=len(r['events']),stages=dict(c),formed=r['total_relationships_formed']))
 return dict(invariants_passed=2,rows=results)
def N130():
 rows=[]
 for seed in (101,211):
  cfg={**original.SCENARIOS['mixed_random'],'schedule_mode':'pair_max','schedule_slots':1}
  r=mini.simulate(engine,seed,'mini',cfg)
  assert all(v is None or math.isfinite(v) for v in r['active_share_by_gender'].values())
  p=mini.people(seed)
  if seed==101:
   def only_one(_seed):
    v=mini.people(_seed);v['genders'][:]='F';v['scopes'][:]='all';return v
   r2=engine.simulate(seed,'no-M-X',cfg,people_provider=only_one,compatibility_provider=mini.compatibility,population_size=24,steps=4)
   assert r2['active_share_by_gender']['M'] is None and r2['active_share_by_gender']['X'] is None
   assert r2['impression_count_by_gender']['M']==r2['impression_count_by_gender']['X']==0
  rows.append(dict(seed=seed,shares=r['active_share_by_gender'],n_x=int(np.sum(p['genders']=='X'))))
 return dict(missing_category_is_null=True,rows=rows)
def N131():
 source=Path(engine.__file__).read_text()
 tree=ast.parse(source)
 names=[n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
 assert 'exec' not in names and 'eval' not in names and 'compile' not in names
 with tempfile.TemporaryDirectory() as d:
  for f in ('esbm_dynamic.py','esbm_event_engine.py','mini_world.py'):shutil.copy2(Path(__file__).parent/f,Path(d)/f)
  cmd=("import sys,json;sys.path.insert(0,"+repr(d)+");"
  "import esbm_dynamic as o,esbm_event_engine as e,mini_world as m;"
  "assert e.simulate(101,'x',o.SCENARIOS['mixed_random'])==o.simulate(101,'x',o.SCENARIOS['mixed_random']);"
  "r=m.simulate(e,101,'two',{**o.SCENARIOS['mixed_random'],'schedule_mode':'pair_max','schedule_slots':2});"
  "assert (r['total_relationships_formed'],r['active_partnerships_end'])==(5,4);"
  "print(json.dumps({'legacy':224,'mini_formed':r['total_relationships_formed']}))")
  proc=subprocess.run([sys.executable,'-I','-c',cmd],text=True,capture_output=True,timeout=35)
  assert proc.returncode==0,proc.stderr[-2000:]
  output=json.loads(proc.stdout.strip().splitlines()[-1])
  p=mini.people(101);g=mini.compatibility(p,'general')
  for mode,slots in [('unsupported',1),('pair_max',3)]:
   try:list(engine.opportunities(p,g,np.arange(24),original.SCENARIOS['mixed_random'],np.zeros(24,int),0,mode,slots))
   except ValueError:continue
   raise AssertionError('Missing fail-closed on '+mode)
 return dict(isolated_same_environment=True,without_dynamic_source_patch=True,rejects_bad_modes=True,output=output)
def run():
 outcomes=[]
 for i,fn in enumerate((N127,N128,N129,N130,N131)):
  t=time.perf_counter()
  try:result=fn();state='PASS'
  except Exception as exc:result=dict(error=repr(exc));state='INVALID'
  outcomes.append(dict(cycle='N'+str(127+i),status=state,elapsed_seconds=round(time.perf_counter()-t,4),**result))
  print('N'+str(127+i),state,flush=True)
  if state!='PASS':break
 return outcomes
if __name__=='__main__':
 result=dict(schema='ABH_N127_N131_RESULTS',code_sha256=hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest(),cycles=run())
 Path('RESULTS_A.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
