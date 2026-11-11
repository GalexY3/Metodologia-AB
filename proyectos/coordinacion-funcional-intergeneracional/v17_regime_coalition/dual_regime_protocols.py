"""V17 dual-regime local learning scaffold.

Subcritical people can move toward professions already represented among
neighbors; supercritical people may pledge/found with multihop signaling.
No true global counts in decisions: these are used only to score outcomes.
This tests both sides of the payoff curve, especially underfragmented traps
AND initially overfragmented random societies.
"""
from __future__ import annotations
from pathlib import Path
import sys,time,argparse,json,itertools,math
import numpy as np
import coalition_protocols as c
HERE=Path(__file__).resolve().parent
N=c.N

def dual_once(seed,model,m=50,k=4,degree=8,topology='ring',b=32,steps=24,
              gamma=1.,rho=.75,init='random',rounds=8):
 rng=np.random.default_rng(seed)
 adj=c.v12.graph(N,degree,topology,seed=seed+1007)
 jobs=c.jobs_init(rng,b,m,k,init)
 q=N/k
 ever=np.zeros(b,dtype=bool)
 first=np.full(b,-1,dtype=int)
 for t in range(steps):
  counts,size,food=c.evaluate_state(jobs,m,k)
  active=(counts>0).sum(1)
  ord=np.sort(counts,axis=1)[:,::-1]
  exact=(active==k)&(ord[:,0]-ord[:,k-1]<=1)
  first[exact&(~ever)]=t
  ever|=exact
  # Sign estimator uses only own food + external local neighborhood.
  neigh=jobs[:,adj]
  ext=(neigh==jobs[:,:,None]).mean(2)
  sign=c.infer_sign(size,food,ext,q)
  # SUBCRITICAL: copy a locally prevalent occupation, breaking the
  # 'all under-filled stay forever' deadlock seen under random starts.
  # Random tie breaker never privileges numeric role labels.
  # Note: sender's personal food is NOT shared in this control.
  popularity=(neigh[:,:,:,None]==neigh[:,:,None,:]).sum(-1)
  j=(popularity+rng.random(popularity.shape)*.0001).argmax(-1)
  modal=np.take_along_axis(neigh,j[...,None],axis=-1).squeeze(-1)
  bootstrap=(sign<0)&(rng.random((b,N))<
                    np.clip(rho*(1-food),0,1))&(modal!=jobs)
  # SUPERCRITICAL: promise to move before choosing destinations.
  pledge=(sign>0)&(rng.random((b,N))<
                  np.clip(gamma*(1-food),0,1))
  proposal=rng.integers(0,m,size=(b,N)).astype(np.int16)
  for _ in range(5):
   bad=(proposal==jobs)|np.any(neigh==proposal[:,:,None],axis=2)
   proposal=np.where(bad,rng.integers(0,m,size=(b,N)),proposal)
  if model=='dual_individual':
   target=proposal
  elif model=='dual_beacon':
   beacon=rng.integers(0,m,size=(b,1))
   target=np.broadcast_to(beacon,(b,N))
  else:
   token=np.where(pledge,rng.random((b,N)),np.inf)
   if 'recruit' in model:
    under=(sign<0)&(food<1-1e-7)
    recruiting=rng.random((b,N))*.05
    candidates=np.where(under,recruiting,np.inf)
    prior=candidates<token
    token=np.minimum(token,candidates)
    proposal=np.where(prior,jobs,proposal)
   target,_=c.wave_gossip(rng,token,proposal,adj,rounds,
                        'honest')
   if model=='dual_scramble':
    random_index=rng.integers(0,N,size=(b,N))
    target=np.take_along_axis(proposal,random_index,axis=1)
  # Subcritical coalescence and supercritical founding are simultaneous,
  # and neither consults the current counts of another profession.
  new=np.where(bootstrap,modal,jobs)
  new=np.where(pledge,target,new)
  jobs=new.astype(np.int16)
 counts,size,food=c.evaluate_state(jobs,m,k)
 ord=np.sort(counts,axis=1)[:,::-1]
 active=(counts>0).sum(1)
 exact=(active==k)&(ord[:,0]-ord[:,k-1]<=1)
 first[exact&(~ever)]=steps
 ever|=exact
 d=1-np.minimum(ord[:,:k],q).sum(1)/N
 return dict(food=float(food.mean()),D=float(d.mean()),
      active=float(active.mean()),exact=int(exact.sum()),
      ever_exact=int(ever.sum()),first=first.tolist(),worlds=b,
      per_world_food=food.mean(1).tolist())

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--mode',choices=['pilot','broad','holdout'],default='pilot')
 ap.add_argument('--shard-index',type=int,default=0)
 ap.add_argument('--shard-count',type=int,default=1)
 ap.add_argument('--worlds',type=int,default=24)
 ap.add_argument('--replicates',type=int,default=2)
 ap.add_argument('--steps',type=int,default=24)
 args=ap.parse_args()
 if args.mode=='pilot':
  tasks=[(50,4,'random'),(50,4,'trap'),(80,12,'random'),(80,12,'trap')]
  degrees=[8,16];topos=['ring']
  rhos=[.3,.6,1.];rounds=[8,16]
 elif args.mode=='broad':
  tasks=[(24,4,'random'),(24,4,'trap'),(50,4,'random'),(50,4,'trap'),
         (80,12,'random'),(80,12,'trap'),(80,30,'random'),(80,30,'trap'),
         (80,60,'random'),(80,60,'trap')]
  degrees=[4,8,16];topos=['ring','rewired']
  rhos=[.25,.5,.8];rounds=[8,16]
 else:
  # Independent future tasks/degrees, not used to select the pilot mechanism.
  tasks=[(36,3,'random'),(36,3,'trap'),(48,6,'random'),(48,6,'trap'),
         (64,4,'random'),(64,4,'trap'),(72,8,'random'),(72,8,'trap'),
         (80,20,'random'),(80,20,'trap'),(80,40,'random'),(80,40,'trap')]
  degrees=[6,12];topos=['rewired']
  rhos=[.6,1.];rounds=[8,16]
 models=['dual_individual','dual_beacon','dual_honest',
         'dual_recruit','dual_scramble']
 clock=time.perf_counter()
 rows=[]
 for rowidx,((m,k,init),degree,topo,rho,R,model) in enumerate(itertools.product(
        tasks,degrees,topos,rhos,rounds,models)):
  if rowidx%args.shard_count!=args.shard_index:continue
  seed_base=119911+31*m+7*k+13*degree+(init=='trap')*37
  vals=[dual_once(seed_base+j*100003,model,m,k,degree,topo,
                 b=args.worlds,steps=args.steps,
                 gamma=1.,rho=rho,init=init,rounds=R)
        for j in range(args.replicates)]
  record=dict(m=m,k=k,init=init,degree=degree,topology=topo,
        rho=rho,rounds=R,model=model,
        food=float(np.mean([v['food'] for v in vals])),
        D=float(np.mean([v['D'] for v in vals])),
        active=float(np.mean([v['active'] for v in vals])),
        exact=sum(v['exact'] for v in vals),
        ever_exact=sum(v['ever_exact'] for v in vals),
        worlds=sum(v['worlds'] for v in vals),seeds=vals)
  rows.append(record)
  if len(rows)%25==0:
   print('DUAL_PROGRESS',args.mode,len(rows),m,k,init,'last',
       round(record['food'],3),'elapsed',
       round(time.perf_counter()-clock),flush=True)
  if len(rows)%100==0:
   out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
   (out/f'dual_{args.mode}_shard{args.shard_index}of{args.shard_count}.json').write_text(json.dumps(
      dict(mode=args.mode,rows=rows),indent=1),encoding='utf8')
 out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
 (out/f'dual_{args.mode}_shard{args.shard_index}of{args.shard_count}.json').write_text(json.dumps(
    dict(mode=args.mode,rows=rows,elapsed_s=time.perf_counter()-clock,
     worlds=args.worlds,replicates=args.replicates,steps=args.steps),indent=1),
   encoding='utf8')
 print('DUAL_COMPLETE',args.mode,'conditions',len(rows),'societies',
       sum(x['worlds'] for x in rows),'seconds',
       round(time.perf_counter()-clock),flush=True)
 for init in ('random','trap'):
  for model in models:
   z=[v for v in rows if v['init']==init and v['model']==model]
   print('DUAL_AGG',init,model,'meanfood',round(float(np.mean([x['food'] for x in z])),4),
     'exact',sum(x['exact'] for x in z),'ever',sum(x['ever_exact'] for x in z),flush=True)
if __name__=='__main__':main()
