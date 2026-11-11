"""V17 behavior distillation into 120 SEPARATE neural policies from a local teacher.

The teacher is a hand-designed local policy (no oracle global census):
  over quota: pledge with prob gamma*(1-food)
  under quota: join modal with prob rho*(1-food)
  under quota: advertise current role with prob 0.98
These targets are computed from each person's own reward+local neighbors.
Each agent has private weights and independent gradients, but supervised
teacher signals ARE injected and success must not be called emergent MARL.
After distillation a separate experiment optionally applies private REINFORCE.
"""
from __future__ import annotations
import argparse,os,math,json,random,time
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
from torch import nn
from torch.nn import functional as F
import neural_dual_v2 as dual
import neural_pledge as trainer
from v12 import World,Config,food
HERE=Path(__file__).resolve().parent
TASKS=((24,2),(24,4),(24,6),(24,10),(24,12),(50,4),(50,5),
       (50,10),(80,2),(80,4),(80,6),(80,10),(80,12),(80,15),
       (80,20),(80,30),(80,40),(80,60))
DEVELOP=((50,4,'trap'),(50,4,'random'),(80,12,'trap'),
         (80,12,'random'),(80,30,'random'),
         (72,8,'trap'),(72,8,'random'),(40,5,'random'))
def obs_actor(e,model):
 c=e.c;b,n=e.jobs.shape;q=n/c.k
 loc=e.local()
 own=loc.gather(2,e.jobs[...,None]).squeeze(2)
 r=e.food
 sub=q*r;sup=q/r.clamp_min(1e-6)
 under=(sub>=1-1e-5)&(sub<q-1e-5)&((sub-sub.round()).abs()<2e-4)
 over=(sup>q+1e-5)&(sup<=n+1e-5)&((sup-sup.round()).abs()<2e-4)
 local=torch.where(own>(q-1)/(n-1),torch.ones_like(r),-torch.ones_like(r))
 sign=torch.where(under&~over,-torch.ones_like(r),
       torch.where(over&~under,torch.ones_like(r),
        torch.where(r>=1-1e-5,torch.zeros_like(r),local)))
 if model.features=='raw':
  signfeat=torch.zeros_like(sign)
  residue=torch.zeros_like(r)
 elif model.features=='local':
  signfeat=local
  residue=torch.zeros_like(r)
 else:
  signfeat=sign
  residue=((sub-sub.round()).abs()-(sup-sup.round()).abs()).clamp(-1,1)
 def const(v):return torch.full_like(r,float(v))
 x=torch.stack([r,1-r,own,own,r,
    const(c.k/c.m),const(q/n),const(math.log(q)/math.log(n)),
    signfeat,residue,torch.zeros_like(r),
    const(e.t/c.horizon),const(c.degree/n),const(math.log(c.m)/math.log(80))],2)
 hidden=torch.tanh(torch.einsum('bnd,ndh->bnh',x,model.wx)+model.b[None,:,:])
 logits=torch.einsum('bnh,nhv->bnv',hidden,model.v)+model.bias[None,:,:]
 return logits,sign
def generate_state(cfg,seed,kind):
 e=World(replace(cfg,init='random'),seed)
 b,n=e.jobs.shape
 if kind!='random':
  q=n/cfg.k
  if kind=='monolith':groups=1
  elif kind=='trap':groups=max(1,cfg.k//2)
  elif kind=='neartrap':groups=max(1,cfg.k-1)
  elif kind=='optimum':groups=cfg.k
  elif kind=='overfragmented':groups=min(cfg.m,cfg.k*2)
  elif kind=='partiallyfragmented':groups=min(cfg.m,max(1,(cfg.k*3)//2))
  else:raise ValueError(kind)
  assert 1<=groups<=cfg.m,(groups,cfg.m,cfg.k,kind)
  for j in range(b):
   roles=torch.randperm(cfg.m,device=cfg.device)[:groups]
   indices=torch.randperm(n,device=cfg.device)%groups
   e.jobs[j]=roles[indices]
  e.food,e.counts=food(e.jobs,cfg.m,cfg.k)
  e.lastfood=e.food.clone()
 return e
def estimate(model,device,seed=951001,batch=24,steps=30):
 # Same tasks across training seeds; development only, not a sealed holdout.
 outputs={}
 with torch.no_grad():
  for m,k,ini in DEVELOP:
   c=Config(n=model.n,m=m,k=k,degree=8,batch=batch,horizon=steps,
            device=device,init=ini)
   results=[]
   for sid in (seed,seed+97):
    e=World(c,sid)
    model.reset()
    for _ in range(steps):
     jobs,_,_=model.act(e)
     e.advance(jobs)
    cnt=e.counts
    occupied=(cnt>0).sum(1)
    ordered=cnt.sort(1,descending=True).values
    exact=(occupied==k)&(ordered[:,0]-ordered[:,k-1]<=1)
    results.append(dict(food=float(e.food.mean()),exact=int(exact.sum()),
                        occupied=float(occupied.float().mean()),worlds=batch))
   outputs[f'M{m}_k{k}_{ini}']={
      'food':float(np.mean([x['food'] for x in results])),
      'exact':sum(x['exact'] for x in results),
      'occupied':float(np.mean([x['occupied'] for x in results])),
      'worlds':sum(x['worlds'] for x in results)}
 return outputs

def parse():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--init-seed',type=int,default=3111)
 p.add_argument('--updates',type=int,default=1000)
 p.add_argument('--rl-updates',type=int,default=0)
 p.add_argument('--h',type=int,default=16)
 p.add_argument('--rounds',type=int,default=8)
 p.add_argument('--quorum',action='store_true')
 p.add_argument('--features',choices=('lattice','raw','local'),default='lattice')
 p.add_argument('--batch',type=int,default=20)
 p.add_argument('--rho',type=float,default=.6)
 p.add_argument('--lr',type=float,default=.004)
 p.add_argument('--device',choices=('cuda','cpu'),default='cuda')
 p.add_argument('--eval-every',type=int,default=200)
 return p.parse_args()
def main(args):
 torch.set_num_threads(min(4,os.cpu_count() or 2))
 root=HERE/'runs'/args.name
 root.mkdir(parents=True,exist_ok=True)
 config=vars(args)
 setup=root/'teacher_spec.json'
 if setup.exists() and json.loads(setup.read_text('utf8'))!=config:
  raise RuntimeError('Incompatible resume')
 setup.write_text(json.dumps(config,indent=2),encoding='utf8')
 torch.manual_seed(args.init_seed)
 model=dual.DualNet(120,args.h,args.rounds,args.quorum,args.features,
                    scramble=False,gate=True).to(args.device)
 optimizer=torch.optim.Adam(model.parameters(),lr=args.lr)
 history=root/'teacher_history.jsonl'
 ck=root/'teacher_latest.pt'
 start=0
 if ck.exists():
  st=torch.load(ck,map_location=args.device,weights_only=False)
  model.load_state_dict(st['model']);optimizer.load_state_dict(st['optimizer'])
  start=int(st['update'])
 print('DISTILL_BEGIN',args.name,'params_per_agent',
   sum(p.numel() for p in model.parameters())//120,
   'tasks',len(TASKS),'updates',args.updates,flush=True)
 def checkpoint(u):
  checkpoint=dict(model=model.state_dict(),optimizer=optimizer.state_dict(),update=u)
  temporary=root/'teacher.tmp'
  torch.save(checkpoint,temporary)
  os.replace(temporary,ck)
  if u%500==0 or u==args.updates:
   torch.save(checkpoint,root/f'teacher_{u:06d}.pt')
 if not history.exists():
  metrics=estimate(model,args.device)
  print('DISTILL_INITIAL',args.name,'trap',metrics['M50_k4_trap'],flush=True)
 clock=time.perf_counter()
 kinds=('random','trap','neartrap','optimum','overfragmented','partiallyfragmented','monolith')
 for u in range(start+1,args.updates+1):
  m,k=TASKS[(u-1)%len(TASKS)]
  cfg=Config(n=120,m=m,k=k,degree=8,batch=args.batch,
              horizon=20,device=args.device)
  e=generate_state(cfg,args.init_seed+971*u,kinds[u%len(kinds)])
  logits,sign=obs_actor(e,model)
  r=e.food
  # These teacher targets are private role-wise probabilities, never
  # computed from true population counts or other people's rewards.
  pledge=torch.clamp(1-r,.01,.99)
  join=torch.clamp(args.rho*(1-r),.01,.99)
  advertise=torch.full_like(r,.98)
  labels=torch.stack((pledge,join,advertise),dim=2)
  mask=torch.stack((sign>0,sign<0,sign<0),dim=2)
  ce=F.binary_cross_entropy_with_logits(logits,labels,reduction='none')
  # Learning signal is PER-INDIVIDUAL teacher, average only for
  # computational batching of disjoint parameter gradients.
  loss=(ce*mask.float()).sum()/mask.sum().clamp_min(1)
  optimizer.zero_grad(set_to_none=True)
  loss.backward()
  optimizer.step()
  if u==1 or u%args.eval_every==0 or u==args.updates:
   score=estimate(model,args.device,seed=951001,batch=24,steps=24)
   row=dict(update=u,loss=float(loss.detach()),
     elapsed=time.perf_counter()-clock,results=score)
   with history.open('a',encoding='utf8') as fh:
    fh.write(json.dumps(row)+'\n')
   print('DISTILL_METRIC',args.name,u,'loss',round(float(loss),5),
       'trap',round(score['M50_k4_trap']['food'],4),
       'trap_exact',score['M50_k4_trap']['exact'],
       'newK8',round(score['M72_k8_random']['food'],4),
       flush=True)
  if u%args.eval_every==0 or u==args.updates:checkpoint(u)
 # RL fine-tuning as separate explicitly labeled stage. No auto-completion
 # of staged RL if supervised task is interrupted.
 if args.rl_updates>0:
  trainer.PledgeActor=dual.DualNet
  opt_rl=torch.optim.Adam(model.parameters(),lr=.002)
  rlhistory=root/'rl_history.jsonl'
  for step in range(1,args.rl_updates+1):
   m,k=TASKS[(step-1)%len(TASKS)]
   kind='trap' if step%2 else 'random'
   c=Config(n=120,m=m,k=k,degree=8,init=kind,batch=12,
            horizon=20,device=args.device,lr=.002,entropy=.006,
            gamma=.97)
   z=trainer.envlib.train_step(model,opt_rl,c,args.init_seed+step*1069)
   if step==1 or step%args.eval_every==0 or step==args.rl_updates:
    e=estimate(model,args.device)
    row=dict(rl_step=step,training=z,evaluation=e)
    with rlhistory.open('a',encoding='utf8') as fh:fh.write(json.dumps(row)+'\n')
    print('DISTILL_RL_METRIC',args.name,step,'trap',round(e['M50_k4_trap']['food'],4),
       'exact',e['M50_k4_trap']['exact'],flush=True)
  torch.save(dict(model=model.state_dict(),optimizer=opt_rl.state_dict(),
                   update=args.rl_updates,source_teacher_updates=args.updates),
        root/'rl_latest.pt')
 (root/'status.json').write_text(json.dumps(dict(state='completed',
      teacher_updates=args.updates,rl_updates=args.rl_updates)),encoding='utf8')
 print('DISTILL_COMPLETE',args.name,args.updates,args.rl_updates,flush=True)
if __name__=='__main__':main(parse())
