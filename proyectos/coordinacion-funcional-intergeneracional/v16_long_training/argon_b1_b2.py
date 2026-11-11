"""Independent audit of Argon's mathematical diagnostics and B1/B2 interventions.

No weight updates. Distinguish diagnostics that use privileged global counts
(ORACLE ONLY) from implementable local neural policies. All experiments reuse
the original individual food payoff. No external pages are produced.
"""
from __future__ import annotations
import argparse,json,sys,math
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'v15_universal_k'))
import v15
envlib=v15.envlib
CASES=[(12,10),(16,15),(24,4),(24,20),(40,12),(40,30),
       (50,4),(80,12),(80,30),(80,60)]
SEEDS=[202601,202607,202609]
MODES=['original_gate','no_gate','scaled_gate','local_sign_gate','oracle_sign_gate']
def load(name,device):
 root=HERE.parent/'v15_universal_k'/'runs'/name
 spec=json.loads((root/'spec.json').read_text('utf8'))['args']
 actor=v15.OptionActor(spec['n'],spec['h'],recurrent=not spec['no_recurrence']).to(device)
 ck=torch.load(root/'latest.pt',weights_only=False,map_location=device)
 actor.load_state_dict(ck['model'])
 actor.eval()
 return actor,spec
def measure_sign(env):
 c=env.c
 selfc=env.counts.gather(1,env.jobs)
 local=env.local().gather(2,env.jobs[...,None]).squeeze(2)
 true=torch.sign(selfc.float()-(c.n/c.k))
 estimate=torch.sign(c.k*local-1)
 mask=true!=0
 tp=((true>0)&(estimate>0)&mask).sum().item()
 pos=((true>0)&mask).sum().item()
 tn=((true<0)&(estimate<0)&mask).sum().item()
 neg=((true<0)&mask).sum().item()
 alln=int(mask.sum())
 accurate=int(((true==estimate)&mask).sum())
 return dict(accuracy=accurate/max(1,alln),
    congestion_recall=tp/max(1,pos),
    deficit_recall=tn/max(1,neg),
    true_critical_fraction=float((true==0).float().mean()),
    evaluated_agents=alln)
def run_one(model,conf,seed,mode,init):
 c=replace(conf,init=init)
 env=envlib.World(c,seed)
 model.reset()
 initial=measure_sign(env)
 with torch.no_grad():
  for turn in range(c.horizon):
   previous_tenure=model.tenure.clone() if model.tenure is not None else None
   # Use published V15 hybrid inference policy.
   proposal,_,_=model.act(env,greedy=(c.k/c.m>=.5))
   current=env.food
   q=c.n/c.k
   if mode=='original_gate':
    keep=(current>=.75)&(c.k/c.m>=.7)
   elif mode=='no_gate':
    keep=torch.zeros_like(current,dtype=torch.bool)
   elif mode=='scaled_gate':
    # Argon suggests adapting the gate threshold to task resolution.
    keep=(current>=1-c.k/c.n)&(c.k/c.m>=.7)
   elif mode=='local_sign_gate':
    # Permitted LOCAL observation only. Protects seemingly under/critical.
    f=env.local().gather(2,env.jobs[...,None]).squeeze(2)
    under=(c.k*f<=1.)
    keep=(current>=.75)&under&(c.k/c.m>=.7)
   elif mode=='oracle_sign_gate':
    # ILLEGAL as learned actor input; counterfactual upper bound ONLY!
    group_size=env.counts.gather(1,env.jobs)
    under=group_size.float()<=q
    keep=(current>=.75)&under&(c.k/c.m>=.7)
   else:raise ValueError(mode)
   jobs=torch.where(keep,env.jobs,proposal)
   if previous_tenure is not None:
    changed=jobs!=env.jobs
    model.tenure=torch.where(changed,torch.zeros_like(previous_tenure),
                              previous_tenure+1)
    model.was_moving=changed.float()
   env.advance(jobs)
 final=measure_sign(env)
 food=float(env.food.mean())
 counts=env.counts
 occupied=(counts>0).sum(1)
 ordered=counts.sort(1,descending=True).values
 exact=(occupied==c.k)&(ordered[:,0]-ordered[:,c.k-1]<=1)
 D=1-ordered[:,:c.k].float().clamp(max=q).sum(1)/c.n
 return dict(food=food,occupied=float(occupied.float().mean()),
             exact=int(exact.sum()),worlds=c.batch,D=float(D.mean()),
             initial_sign=initial,final_sign=final)
def analytic_checks():
 N=120
 out=[]
 for k,m in ((4,1),(4,2),(4,3),(8,6),(10,9),(80,60)):
  q=N/k;size=N/m
  if N%m:continue
  payoff=q/size if size>=q else size/q
  threshold=m*N/(k*k)
  out.append(dict(k=k,m=m,group_size=int(size),payoff=payoff,
      unilateral_founder=1/q,coalition_equal_threshold=threshold,
      smallest_strict_improving_size=int(math.floor(threshold)+1),
      suggested_ceil=int(math.ceil(threshold))))
 # A counterexample to Argon's claim that U1 implies exactly k groups,
 # when N=120,k80 and M=120.
 N=120;k=80;q=N/k;l=math.floor(q);h=math.ceil(q)
 u=lambda n:min(1,n/l,h/n)
 out_u1=dict(N=N,k=k,M=120,food_k80=float(sum(n*u(n) for n in ([2]*40+[1]*40))/N),
             food_k120=float(sum(u(1) for _ in range(N))/N),
             distinct_optimal_k=[80,120])
 return out,out_u1
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--name',default='v15_ops_mlp16_s4111')
 p.add_argument('--device',default='cuda')
 p.add_argument('--worlds',type=int,default=48)
 p.add_argument('--steps',type=int,default=60)
 args=p.parse_args()
 torch.set_num_threads(3)
 model,cfg=load(args.name,args.device)
 results=[]
 for m,k in CASES:
  for init in ('random','trap'):
   w=v15.envlib.Config(n=cfg['n'],m=m,k=k,degree=cfg['degree'],
           batch=args.worlds,horizon=args.steps,device=args.device)
   for mode in MODES:
    vals=[run_one(model,w,seed,mode,init) for seed in SEEDS]
    rec=dict(m=m,k=k,init=init,mode=mode,
      food=float(np.mean([z['food'] for z in vals])),
      occupied=float(np.mean([z['occupied'] for z in vals])),
      D=float(np.mean([z['D'] for z in vals])),
      exact=sum(z['exact'] for z in vals),worlds=sum(z['worlds'] for z in vals),
      initial_sign={f:float(np.mean([x['initial_sign'][f] for x in vals])) for f in ('accuracy','congestion_recall','deficit_recall','true_critical_fraction')},
      final_sign={f:float(np.mean([x['final_sign'][f] for x in vals])) for f in ('accuracy','congestion_recall','deficit_recall','true_critical_fraction')})
    results.append(rec)
    print('ARGON_B2',args.name,'M',m,'k',k,'start',init,'treatment',mode,
          'food',round(rec['food'],4),'groups',round(rec['occupied'],2),
          'D',round(rec['D'],3),'exact',rec['exact'],
          'sign accuracy',round(rec['initial_sign']['accuracy'],3),
          flush=True)
 threshold,u1=analytic_checks()
 out=HERE/'diagnostics'/(args.name+'_ARGON_B1B2.json')
 envlib.write_json(out,dict(model=args.name,steps=args.steps,per_condition_worlds=args.worlds*len(SEEDS),
     test_seeds=SEEDS,cases=CASES,operations=MODES,
     exact_coalition_thresholds=threshold,noninteger_U1_counterexample=u1,
     experiment='Frozen V15 model; original food payoff; oracle treatment labeled illegal upper bound; local sign only uses allowed neighborhood.',
     results=results))
 print('ARGON_AUDIT_DONE',len(results),'treatments',flush=True)
if __name__=='__main__':main()
