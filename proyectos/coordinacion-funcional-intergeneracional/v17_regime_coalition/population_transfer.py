"""V17 zero-shot transfer of handcoded dual protocol across population sizes.

No parameter fitting on these N. Change N via module globals for the isolated
protocol benchmark; no trained neural weights are used. Separate experiment
from V17 MARL with N=120.
"""
from pathlib import Path
import argparse,time,json,itertools
import numpy as np
import coalition_protocols as c
import dual_regime_protocols as dual
HERE=Path(__file__).resolve().parent

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--worlds',type=int,default=32)
 ap.add_argument('--replicates',type=int,default=3)
 ap.add_argument('--steps',type=int,default=30)
 ap.add_argument('--shard-index',type=int,default=0)
 ap.add_argument('--shard-count',type=int,default=1)
 args=ap.parse_args()
 cases=[
  (60,40,3),(60,50,4),(60,60,6),(60,80,10),
  (72,50,4),(72,80,6),(72,80,8),(72,80,12),
  (180,50,4),(180,80,6),(180,80,10),(180,80,20),
  (240,50,4),(240,80,6),(240,80,12),(240,80,20),(240,80,40),(240,80,60)]
 # All tasks have integer quotas. 
 cases=[z for z in cases if z[0]%z[2]==0 and z[2]<=z[1]]
 starts=['random','trap','block']
 models=['dual_individual','dual_beacon','dual_honest','dual_recruit','dual_scramble']
 graphs=[('ring',8),('rewired',8),('ring',16),('rewired',16)]
 # R8 vs R16 is a network diffusion radius, not a time step of food.
 variants=[(r,mode) for r in (8,16) for mode in models]
 rows=[];t0=time.perf_counter()
 for j,(case,ini,(topo,degree),(rounds,model)) in enumerate(
     itertools.product(cases,starts,graphs,variants)):
  if j%args.shard_count!=args.shard_index:continue
  N,m,k=case
  c.N=N
  dual.N=N
  seed0=511301+N*17+m*31+k*11+degree*3+(ini=='trap')*17+(ini=='block')*43
  z=[dual.dual_once(seed0+u*10103,model,m,k,degree,topo,b=args.worlds,
      steps=args.steps,gamma=1.,rho=.6,init=ini,rounds=rounds) for u in range(args.replicates)]
  rec=dict(n=N,m=m,k=k,init=ini,degree=degree,topology=topo,
    rounds=rounds,model=model,food=float(np.mean([v['food'] for v in z])),
    D=float(np.mean([v['D'] for v in z])),
    active=float(np.mean([v['active'] for v in z])),
    exact=sum(v['exact'] for v in z),
    worlds=sum(v['worlds'] for v in z),
    each_seed=z)
  rows.append(rec)
  if len(rows)%60==0:
   print('POP_PROGRESS',len(rows),N,m,k,ini,model,
      round(rec['food'],4),'exact',rec['exact'],
      'seconds',round(time.perf_counter()-t0),flush=True)
  if len(rows)%120==0:save(rows,args,t0)
 save(rows,args,t0)
 print('POP_TRANSFER_DONE',len(rows),'scenarios',
   sum(z['worlds'] for z in rows),'societies',
   'elapsed',round(time.perf_counter()-t0),flush=True)
 for model in models:
  z=[r for r in rows if r['model']==model]
  print('POP_AGG',model,'food',round(float(np.mean([r['food'] for r in z])),4),
        'exact',sum(r['exact'] for r in z),flush=True)

def save(rows,args,t0):
 out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
 target=out/f'population_transfer_shard{args.shard_index}of{args.shard_count}.json'
 target.write_text(json.dumps(dict(
    description='Transfer to unseen N with no NN training',
    args=vars(args),elapsed_seconds=time.perf_counter()-t0,
    rows=rows),indent=1),encoding='utf8')
if __name__=='__main__':main()
