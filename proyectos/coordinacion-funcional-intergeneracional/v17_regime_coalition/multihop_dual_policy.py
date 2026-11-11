"""V17 multihop-aware dual coalition policy (non-neural mechanism benchmark).

Compare 1/2/4/8/16-hop sign inference over public payoff and relayed labels,
then separate 8/16-hop intent/destination propagation. The main actions
remain individual with no global-reward objective.
"""
from __future__ import annotations
from pathlib import Path
import itertools,argparse,json,time
import numpy as np
import coalition_protocols as c
from multihop_regime import classify
HERE=Path(__file__).resolve().parent
N=120

def simulate(seed,m,k,degree,topo,init,rad_sign,rad_offer,
             b=32,steps=24,gamma=1.,rho=.6):
 rng=np.random.default_rng(seed)
 adj=c.v12.graph(N,degree,topo,seed=seed+1007)
 jobs=c.jobs_init(rng,b,m,k,init)
 reach=None if rad_sign==1 else c.reachable(adj,rad_sign)
 q=N/k
 ever=np.zeros(b,dtype=bool)
 first=np.full(b,-1,dtype=int)
 for t in range(steps):
  counts,size,food=c.evaluate_state(jobs,m,k)
  order=np.sort(counts,axis=1)[:,::-1]
  active=(counts>0).sum(1)
  exact=(active==k)&(order[:,0]-order[:,k-1]<=1)
  first[exact&~ever]=t;ever|=exact
  neigh=jobs[:,adj]
  if rad_sign==1:
   # Existing local sign rule with integer-lattice disambiguation.
   loc=(neigh==jobs[:,:,None]).mean(2)
   sign=c.infer_sign(size,food,loc,q)
  else:
   # R-hop message delivery of career labels and unique agent IDs;
   # mask forbids any unavailable role information.
   match=(jobs[:,:,None]==jobs[:,None,:])
   seen=(match&reach[None,:,:]).sum(2)-1
   sign=classify(food,q,seen,reach)
  # Choose local modal occupation if underfull, analog to Dual V17.
  popularity=(neigh[:,:,:,None]==neigh[:,:,None,:]).sum(-1)
  modal_index=(popularity+rng.random(popularity.shape)*1e-5).argmax(-1)
  modal=np.take_along_axis(neigh,modal_index[...,None],axis=2).squeeze(2)
  join=(sign<0)&(rng.random((b,N))<rho*(1-food))&(modal!=jobs)
  pledge=(sign>0)&(rng.random((b,N))<gamma*(1-food))
  proposal=rng.integers(0,m,size=(b,N))
  for _ in range(6):
   taken=np.any(neigh==proposal[:,:,None],axis=2)|(proposal==jobs)
   proposal=np.where(taken,rng.integers(0,m,size=(b,N)),proposal)
  # All insufficiently occupied groups advertise their profession, even
  # if a member may also join a different group simultaneously.
  under=(sign<0)&(food<1-1e-7)
  candidates=rng.random((b,N))*.05
  founders=1+rng.random((b,N))
  tokens=np.where(under,candidates,np.where(pledge,founders,np.inf))
  offer=np.where(under,jobs,proposal)
  destination,_=c.wave_gossip(rng,tokens,offer,adj,rad_offer,'honest')
  jobs=np.where(pledge,destination,np.where(join,modal,jobs)).astype(np.int16)
 counts,size,food=c.evaluate_state(jobs,m,k)
 order=np.sort(counts,axis=1)[:,::-1];active=(counts>0).sum(1)
 exact=(active==k)&(order[:,0]-order[:,k-1]<=1)
 first[exact&~ever]=steps;ever|=exact
 D=1-np.minimum(order[:,:k],q).sum(1)/N
 return dict(food=float(food.mean()),active=float(active.mean()),
    D=float(D.mean()),exact=int(exact.sum()),ever_exact=int(ever.sum()),
    worlds=b,food_by_world=food.mean(1).tolist())

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--worlds',type=int,default=24)
 ap.add_argument('--replicates',type=int,default=2)
 ap.add_argument('--steps',type=int,default=24)
 ap.add_argument('--shard-index',type=int,default=0)
 ap.add_argument('--shard-count',type=int,default=1)
 args=ap.parse_args()
 cases=[(50,4),(80,12),(80,30),(80,60)]
 starts=['random','trap','block']
 degrees=[8,16]
 topologies=['ring','rewired']
 radius_sign=[1,2,4,8,16]
 radius_offer=[8,16]
 rows=[];t0=time.perf_counter()
 for j,((m,k),init,degree,topo,rs,ro) in enumerate(itertools.product(
        cases,starts,degrees,topologies,radius_sign,radius_offer)):
  if j%args.shard_count!=args.shard_index:continue
  vals=[simulate(777001+seedno*13007+31*m+11*k+degree,
     m,k,degree,topo,init,rs,ro,
     b=args.worlds,steps=args.steps) for seedno in range(args.replicates)]
  rec=dict(m=m,k=k,init=init,degree=degree,topology=topo,
    radius_sign=rs,radius_offer=ro,food=float(np.mean([x['food'] for x in vals])),
    active=float(np.mean([x['active'] for x in vals])),
    D=float(np.mean([x['D'] for x in vals])),
    exact=int(sum(x['exact'] for x in vals)),
    worlds=sum(x['worlds'] for x in vals),by_seed=vals)
  rows.append(rec)
  if len(rows)%24==0:
   print('MHDUAL_PROGRESS',len(rows),'k',k,'sign',rs,'offer',ro,
     'food',round(rec['food'],4),'exact',rec['exact'],
     'seconds',round(time.perf_counter()-t0),flush=True)
  if len(rows)%96==0:save(rows,args,t0)
 save(rows,args,t0)
 print('MHDUAL_COMPLETE',len(rows),'cases',
    sum(x['worlds'] for x in rows),'societies','seconds',
    round(time.perf_counter()-t0),flush=True)

def save(rows,args,t0):
 out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
 (out/f'multihop_dual_shard{args.shard_index}of{args.shard_count}.json').write_text(
   json.dumps(dict(args=vars(args),rows=rows,
    elapsed=time.perf_counter()-t0,
    caveat='R=16 may reconstruct all career counts via graph messages; no direct central census is supplied.'),indent=1),encoding='utf8')
if __name__=='__main__':main()
