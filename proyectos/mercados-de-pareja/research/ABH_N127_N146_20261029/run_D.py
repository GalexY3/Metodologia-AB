"""Frozen N142–N146 input abuse, identity-equivariance and clean-process checks."""
import ast,hashlib,json,shutil,subprocess,sys,tempfile,time
from pathlib import Path
import numpy as np
import esbm_dynamic as original
import esbm_event_engine as engine
import esbm_schedule_adapter as old
import small_fixture as oldmini
import mini_world as mini
import social_graph as oldgraph
import social_graph_equivariant as newgraph
def plan(edges):
 def callback(p,eligible,available,config,seen,t,mode,slots):
  if t==0:
   for edge in edges:yield edge
 return callback
def N142():
 p=mini.people(101);eligible=mini.compatibility(p,'general')
 yes=[(i,j) for i in range(24) for j in range(i+1,24) if eligible[i,j]]
 bad=[(i,j) for i in range(24) for j in range(i+1,24) if not eligible[i,j]]
 assert len(yes)>3 and bad
 cases=dict(self_edge=[(0,0)],negative_edge=[(-1,0)],out_of_bounds=[(0,24)],
           ineligible=[bad[0]],repeated_dyad=[yes[0],yes[0]])
 anchor=yes[0][0];neighbours=[j for i,j in yes if i==anchor]
 if len(neighbours)<2:
  anchor=next(i for i in range(24) if sum(eligible[i])>1)
  neighbours=[j for j in range(24) if eligible[anchor,j]]
 cases['actor_overcap']=[(anchor,neighbours[0]),(anchor,neighbours[1])]
 rows=[]
 for label,edges in cases.items():
  try:
   mini.simulate(engine,101,'abuse',{**original.SCENARIOS['mixed_random'],'schedule_mode':'pair_max','schedule_slots':1},scheduler=plan(edges))
  except ValueError as ex:rows.append(dict(case=label,rejected=True,reason=str(ex)))
  else:raise AssertionError('Accepted malicious schedule '+label)
 return dict(status='PASS',checks=len(rows),rows=rows)
def N143():
 n=0
 for seed in original.SEEDS:
  for name,cfg in original.SCENARIOS.items():
   assert original.simulate(seed,name,cfg)==engine.simulate(seed,name,cfg)
   n+=1
 mini_checks=[]
 for seed in (101,211):
  for mode,slots in (('pair_max',1),('pair_norm_same',2),('pair_greedy',2)):
   cfg={**original.SCENARIOS['mixed_random'],'schedule_mode':mode,'schedule_slots':slots}
   a=oldmini.simulate_small(seed,'n',cfg)
   b=mini.simulate(engine,seed,'n',cfg)
   a.pop('active_share_by_gender');b.pop('active_share_by_gender')
   assert a==b
   mini_checks.append(dict(seed=seed,mode=mode,slots=slots,exact=True))
 return dict(status='PASS',historical_exact=n,adapter_exact=len(mini_checks),rows=mini_checks)
def transform(p,perm):
 return {k:(v[:,perm,:][:,:,perm] if isinstance(v,np.ndarray) and v.ndim==3 else v[perm] if isinstance(v,np.ndarray) and v.ndim==1 else v) for k,v in p.items()}
def graphset(g):
 return {frozenset((int(i),int(j))) for i,j in g.edges()}
def N144():
 rows=[]
 for seed in range(5000,5010):
  p=mini.people(seed)
  for rep in range(2):
   perm=np.random.default_rng(seed*100+rep).permutation(24)
   pp=transform(p,perm)
   for kind in ('ring','rewired'):
    a=graphset(oldgraph.build(p,seed,kind))
    b={frozenset((int(perm[i]),int(perm[j]))) for i,j in oldgraph.build(pp,seed,kind).edges()}
    rows.append(dict(seed=seed,rep=rep,kind=kind,exact=(a==b),symmetric_difference=len(a^b)))
 assert len(rows)==40
 return dict(status='PASS_VALID_NEGATIVE_DIAGNOSTIC',checks=40,rows=rows,noninvariant=sum(not z['exact'] for z in rows))
def N145():
 rows=[]
 for seed in range(5000,5010):
  p=mini.people(seed);eligible=mini.compatibility(p,'general')
  for rep in range(2):
   perm=np.random.default_rng(seed*100+rep).permutation(24)
   pp=transform(p,perm);e2=eligible[perm,:][:,perm]
   for kind in ('ring','rewired'):
    oldg=newgraph.build(p,seed,kind);newg=newgraph.build(pp,seed,kind)
    a=graphset(oldg);b={frozenset((int(perm[i]),int(perm[j]))) for i,j in newg.edges()}
    assert a==b,(seed,rep,kind,'graph not equivariant')
    if seed in (5000,5001):
     cfg=original.SCENARIOS['mixed_random']
     sched1=newgraph.scheduler(oldg);sched2=newgraph.scheduler(newg)
     x={frozenset(z) for z in sched1(p,eligible,np.arange(24),cfg,np.zeros(24,int),0,'pair_max',1)}
     y={frozenset((int(perm[i]),int(perm[j]))) for i,j in sched2(pp,e2,np.arange(24),cfg,np.zeros(24,int),0,'pair_max',1)}
     assert x==y,(seed,rep,kind,'scheduler not equivariant')
    rows.append(dict(seed=seed,rep=rep,kind=kind,graph_equivariant=True))
 return dict(status='PASS',graph_checks=len(rows),scheduler_checks=8,rows=rows)
def N146():
 src=Path(engine.__file__).read_text();tree=ast.parse(src)
 forbidden={'exec','eval','compile'}
 calls={n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
 assert not forbidden & calls
 with tempfile.TemporaryDirectory() as tmp:
  for name in ('esbm_dynamic.py','esbm_event_engine.py','mini_world.py','social_graph.py','social_graph_equivariant.py'):
   shutil.copy2(Path(__file__).parent/name,Path(tmp)/name)
  script=("import sys,json;sys.path.insert(0,"+repr(tmp)+");"
    "import esbm_dynamic as o,esbm_event_engine as e,mini_world as m,social_graph_equivariant as g;"
    "assert e.simulate(101,'legacy',o.SCENARIOS['mixed_random'])==o.simulate(101,'legacy',o.SCENARIOS['mixed_random']);"
    "p=m.people(101);z=g.build(p,101,'rewired');"
    "r=m.simulate(e,101,'new',{**o.SCENARIOS['mixed_random'],'schedule_mode':'pair_max','schedule_slots':2},scheduler=g.scheduler(z));"
    "print(json.dumps({'legacy':224,'new_active':r['active_partnerships_end'],'connected':True}))")
  r=subprocess.run([sys.executable,'-I','-c',script],capture_output=True,text=True,timeout=35)
  assert r.returncode==0,r.stderr[-2000:]
  out=json.loads(r.stdout.strip().splitlines()[-1])
  f=Path(tmp)/'esbm_dynamic.py'
  f.write_bytes(f.read_bytes()+b'\n# deliberate corruption in temporary directory')
  script2="import sys;sys.path.insert(0,"+repr(tmp)+");import esbm_event_engine"
  rejected=subprocess.run([sys.executable,'-I','-c',script2],capture_output=True,text=True,timeout=20)
  assert rejected.returncode!=0 and 'Origin changed' in rejected.stderr
 return dict(status='PASS',same_environment_isolated_process=True,source_tamper_rejected=True,reproduction=out,independent_OS=False)
def run():
 rows=[]
 for fn in (N142,N143,N144,N145,N146):
  st=time.perf_counter()
  try:z=fn()
  except Exception as ex:z=dict(status='INVALID',error=repr(ex))
  rows.append(dict(id=fn.__name__,seconds=round(time.perf_counter()-st,4),**z))
  print(fn.__name__,z['status'],flush=True)
  if z['status']=='INVALID':break
 return rows
if __name__=='__main__':
 Path('RESULTS_D.json').write_text(json.dumps(dict(schema='ABH_N142_N146_RESULTS',cycles=run()),indent=2,allow_nan=False)+'\n')
