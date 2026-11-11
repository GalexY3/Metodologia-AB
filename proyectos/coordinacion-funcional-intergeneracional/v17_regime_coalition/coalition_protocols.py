"""V17 experimental laboratory of two-phase conditional-quorum occupation changes.

These are analytically specified decentralized protocols, NOT neural agents.
They are baselines/scaffolds to test whether communication can help overcome
individual-payoff nucleation barriers with no global census observation.
No rollout policy accesses true counts, except the intentionally inadmissible
'oracle_partition' upper bound. Communication rounds are explicitly charged.
"""
from __future__ import annotations
import os,sys,json,argparse,math,itertools,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'v12_variable_mk'))
import v12
N=120

def evaluate_state(jobs,m,k):
 b,n=jobs.shape
 counts=np.zeros((b,m),dtype=np.int32)
 np.add.at(counts,(np.arange(b)[:,None],jobs),1)
 size=np.take_along_axis(counts,jobs,axis=1).astype(float)
 q=n/k
 reward=np.minimum(size/q,q/size)
 return counts,size,reward

def jobs_init(rng,b,m,k,init='trap'):
 n=N
 jobs=np.empty((b,n),dtype=np.int16)
 for z in range(b):
  if init=='trap':
   t=max(1,k//2)
   roles=rng.choice(m,t,replace=False)
   a=np.arange(n)%t
   rng.shuffle(a)
   jobs[z]=roles[a]
  elif init=='random':
   jobs[z]=rng.integers(0,m,size=n)
  elif init=='block':
   t=max(1,k//2)
   roles=rng.choice(m,t,replace=False)
   jobs[z]=roles[np.minimum(t-1,np.arange(n)*t//n)]
  else:raise ValueError(init)
 return jobs

def infer_sign(size,food,loc,q):
 # size is deliberately unused: it is ground truth for evaluation only.
 lower=q*food;upper=q/food
 sub=(lower>=1-1e-7)&(lower<q-1e-6)&(abs(lower-np.rint(lower))<2e-5)
 over=(upper>q+1e-6)&(upper<=N+1e-6)&(abs(upper-np.rint(upper))<2e-5)
 unique_sub=sub&~over
 unique_over=over&~sub
 local_sign=np.where(loc>(q-1)/(N-1),1,-1)
 return np.where(unique_sub,-1,np.where(unique_over,1,np.where(food>1-1e-7,0,local_sign)))

def reachable(adj,rounds):
 reach=np.eye(N,dtype=bool)
 for _ in range(rounds):
  reach=reach|reach[adj].any(1)
 return reach

def wave_gossip(rng,token,proposal,adj,rounds,mode):
 # token [b,n], label[b,n]. Each agent receives locally forwarded offers.
 # For permutation control, replace each received neighbor message with one
 # from an independently chosen random sender (NOT from local neighbors).
 b,n=token.shape
 keys=token.copy();labels=proposal.copy()
 for _ in range(rounds):
  if mode=='rewire_messages':
   senders=rng.integers(0,n,size=(b,n,adj.shape[1]))
   neighborhood=np.take_along_axis(keys[:,None,:].repeat(n,axis=1),
                         senders,axis=2)
   offers=np.take_along_axis(labels[:,None,:].repeat(n,axis=1),
                         senders,axis=2)
  else:
   neighborhood=keys[:,adj]
   offers=labels[:,adj]
  whole=np.concatenate([keys[:,:,None],neighborhood],axis=2)
  idx=whole.argmin(2)
  candidates=np.concatenate([labels[:,:,None],offers],axis=2)
  keys=np.take_along_axis(whole,idx[:,:,None],axis=2).squeeze(2)
  labels=np.take_along_axis(candidates,idx[:,:,None],axis=2).squeeze(2)
 return labels,keys

def run_one(seed,model,m=50,k=4,degree=8,topology='ring',
            b=32,steps=16,rounds=8,gamma=1.,init='trap',
            recruitment=False,quorum=False):
 rng=np.random.default_rng(seed)
 adj=v12.graph(N,degree,topology,seed=seed+1007)
 jobs=jobs_init(rng,b,m,k,init)
 visited_exact=np.zeros(b,dtype=bool)
 first_exact=np.full(b,-1,dtype=int)
 meanfoods=[]
 jumps=0
 q=N/k
 if rounds>0 and quorum:reach=reachable(adj,rounds)
 else:reach=None
 for t in range(steps):
  counts,size,reward=evaluate_state(jobs,m,k)
  # Ground truth used for SCORE ONLY.
  active=(counts>0).sum(1)
  exact=(active==k)&((counts.max(1)==counts[counts>0].max()) if False else
     (np.sort(counts,axis=1)[:,-1]-np.sort(counts,axis=1)[:,-k]<=1))
  newly=exact&(~visited_exact)
  first_exact[newly]=t
  visited_exact|=exact
  meanfoods.append(float(reward.mean()))
  if model=='random_all':
   jobs=rng.integers(0,m,size=(b,N)).astype(np.int16)
   continue
  if model=='oracle_partition':
   for w in range(b):
    targets=rng.choice(m,k,replace=False)
    idx=np.arange(N)%k
    rng.shuffle(idx);jobs[w]=targets[idx]
   continue
  loc=(jobs[:,adj]==jobs[:,:,None]).mean(2)
  sg=infer_sign(size,reward,loc,q)
  p=np.clip(gamma*(1-reward),0,1)
  pledge=(sg>0)&(rng.random((b,N))<p)
  # Uniform privately proposed target; intended to be locally vacant
  # by repeated rejection sampling (max 8 attempts).
  target=rng.integers(0,m,size=(b,N)).astype(np.int16)
  for _ in range(8):
   occupied_local=np.any(jobs[:,adj]==target[:,:,None],axis=2)
   bad=(target==jobs)|occupied_local
   if not bad.any():break
   replacement=rng.integers(0,m,size=(b,N)).astype(np.int16)
   target=np.where(bad,replacement,target)
  if model=='individual':
   finaltarget=target
  elif model=='public_beacon':
   # PUBLIC COORDINATION CONTROL, no messages, shared event label.
   public=rng.integers(0,m,size=(b,1))
   finaltarget=np.broadcast_to(public,(b,N)).copy()
  else:
   token=rng.random((b,N))
   # All individuals forward offers, only applicants originate new ones.
   token=np.where(pledge,token,np.inf)
   if recruitment:
    # If an actually under-full individual can identify its own state
    # from its food + external local signal, advertise profession as a
    # potential recruitment destination. Priority over startup offers.
    hungry=(sg<0)&(reward<1-1e-7)
    # Rank each candidate recruiter by a local job-specific lottery.
    rr=rng.random((b,N))*.05
    prefer=np.where(hungry,rr,np.inf)
    pick=prefer<token
    token=np.where(pick,prefer,token+1)
    target=np.where(pick,jobs,target)
   finaltarget,winning_token=wave_gossip(
      rng,token,target,adj,rounds,
      'rewire_messages' if model=='rewire_messages' else 'honest')
   # A shuffled final vote destroys common target but preserves the
   # distribution of independently proposed labels within each world.
   if model=='scrambled_target':
    offers=target
    ids=rng.integers(0,N,size=(b,N))
    finaltarget=np.take_along_axis(offers,ids,axis=1)
   if quorum:
    # Every participant can count pledges from its R-hop connected
    # environment using signed unique identities exchanged as messages.
    # A quorum involves intending movers to the SAME target.
    eligible=np.zeros_like(pledge)
    for w in range(b):
     agreement=(finaltarget[w,:,None]==finaltarget[w,None,:])
     inreach=reach&agreement&pledge[w][None,:]
     reachcount=inreach.sum(1)
     # Improvement strict for emigrant receiving d workers in target:
     # d > q*personal_food_before. Conservatively count pledges.
     eligible[w]=(reachcount>q*reward[w])
    pledge &=eligible
  new=np.where(pledge,finaltarget,jobs).astype(np.int16)
  jumps+=int((new!=jobs).sum())
  jobs=new
 counts,size,food=evaluate_state(jobs,m,k)
 active=(counts>0).sum(1)
 order=np.sort(counts,axis=1)[:,::-1]
 exact=(active==k)&(order[:,0]-order[:,k-1]<=1)
 newly=exact&(~visited_exact)
 first_exact[newly]=steps
 visited_exact|=exact
 D=1-np.minimum(order[:,:k],q).sum(1)/N
 return dict(food=float(food.mean()),food_sd=float(food.mean(1).std()),
     exact=int(exact.sum()),ever_exact=int(visited_exact.sum()),
     worlds=b,first_exact=first_exact.tolist(),
     mean_active=float(active.mean()),mean_D=float(D.mean()),
     migration_events=jumps,mean_pre_food=float(np.mean(meanfoods)),
     final_food_by_world=food.mean(1).tolist(),
     end_active_by_world=active.tolist())

def parse():
 ap=argparse.ArgumentParser()
 ap.add_argument('--mode',choices=('pilot','broad','holdout'),default='pilot')
 ap.add_argument('--worlds',type=int,default=32)
 ap.add_argument('--steps',type=int,default=16)
 ap.add_argument('--replicates',type=int,default=3)
 return ap.parse_args()

def main(args):
 if args.mode=='pilot':
  tasks=[(50,4,'trap'),(50,4,'block'),(50,4,'random'),(80,12,'trap')]
  degrees=(4,8)
  topologies=('ring',)
  gammas=(.5,1.)
  models=[('individual',0,False,False),('public_beacon',0,False,False),
     ('honest',1,False,False),('honest',2,False,False),
     ('honest',4,False,False),('honest',8,False,False),
     ('honest',16,False,False),('honest',8,False,True),
     ('honest',16,True,True),('rewire_messages',8,False,True),
     ('scrambled_target',8,False,True)]
 elif args.mode=='broad':
  tasks=[(20,2,'trap'),(24,4,'trap'),(50,4,'trap'),(80,6,'trap'),
         (80,12,'trap'),(80,30,'trap'),(80,60,'trap'),
         (50,4,'block'),(80,30,'random')]
  degrees=(4,8,16)
  topologies=('ring','rewired')
  gammas=(.6,1.)
  models=[('individual',0,False,False),
     ('honest',2,False,True),('honest',4,False,True),
     ('honest',8,False,True),('honest',16,False,True),
     ('honest',8,True,True),('honest',16,True,True),
     ('scrambled_target',8,False,True),
     ('rewire_messages',8,False,True),
     ('public_beacon',0,False,False)]
 else:
  # frozen after reading pilot/broad; holdout should use fresh worlds and
  # never be used to choose hyperparameters after inspection.
  tasks=[(50,4,'trap'),(50,4,'block'),(60,6,'trap'),
         (80,10,'trap'),(80,20,'trap'),(80,40,'trap')]
  degrees=(6,12)
  topologies=('rewired',)
  gammas=(.8,)
  models=[('individual',0,False,False),('honest',8,False,True),
          ('honest',16,True,True),('scrambled_target',8,False,True)]
 rows=[];clock=time.perf_counter()
 for m,k,init in tasks:
  for d,topo,gamma,(model,rounds,recruit,quorum) in itertools.product(
      degrees,topologies,gammas,models):
   if k>m:continue
   condition=dict(m=m,k=k,init=init,degree=d,topology=topo,
                  gamma=gamma,model=model,rounds=rounds,
                  recruit=recruit,quorum=quorum)
   # identical seeds per m/k/topology/gamma across treatments
   zs=[]
   for seed_no in range(args.replicates):
    seed=600000+10_007*seed_no+113*m+19*k+37*d+(topo=='rewired')*991+(init=='block')*33
    zs.append(run_one(seed,model,m,k,d,topo,args.worlds,args.steps,
                    rounds,gamma,init,recruit,quorum))
   row=dict(**condition,
      food=float(np.mean([z['food'] for z in zs])),
      D=float(np.mean([z['mean_D'] for z in zs])),
      active=float(np.mean([z['mean_active'] for z in zs])),
      exact=int(sum(z['exact'] for z in zs)),
      ever_exact=int(sum(z['ever_exact'] for z in zs)),
      worlds=int(sum(z['worlds'] for z in zs)),
      migration_events=int(sum(z['migration_events'] for z in zs)),
      by_seed=[dict(seed_no=j,**z) for j,z in enumerate(zs)])
   rows.append(row)
   if (len(rows)%15==0):
    print('COALITION_PROGRESS',args.mode,len(rows),'M',m,'k',k,init,
      'last_food',round(row['food'],4),'last_ever_exact',row['ever_exact'],
      'elapsed',round(time.perf_counter()-clock),flush=True)
   # Save incrementally; a quota/network failure should not discard data.
   if len(rows)%30==0:
    out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
    (out/f'coalition_{args.mode}.json').write_text(
       json.dumps(dict(mode=args.mode,steps=args.steps,n=args.worlds,
          replicates=args.replicates,rows=rows),indent=1),encoding='utf8')
 out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
 (out/f'coalition_{args.mode}.json').write_text(
    json.dumps(dict(mode=args.mode,steps=args.steps,worlds_per_seed=args.worlds,
       replicates=args.replicates,elapsed_seconds=time.perf_counter()-clock,
       rows=rows),indent=1),encoding='utf8')
 print('COALITION_COMPLETE',args.mode,'conditions',len(rows),
       'societies',sum(x['worlds'] for x in rows),'elapsed_s',
       round(time.perf_counter()-clock,1),flush=True)
 for model in sorted(set(z['model'] for z in rows)):
  z=[r for r in rows if r['model']==model]
  print('AGGREGATE',args.mode,model,'cases',len(z),
    'meanfood',round(float(np.mean([x['food'] for x in z])),4),
    'exact',sum(x['exact'] for x in z),
    'everexact',sum(x['ever_exact'] for x in z),flush=True)
if __name__=='__main__':main(parse())
