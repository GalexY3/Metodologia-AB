"""Compare BC anchoring on the states that actors actually encounter.

Unlike off-policy BC on synthetic states, the regularization loss is
evaluated on one (or every) trajectory observation from the evolving village.
Reward term is solely realized own food. Teacher policy is explicitly
provided and frozen: this is regularized RL, NOT emergent cooperation.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import replace
import sys,os,torch,json,time,argparse,numpy as np
from torch.nn import functional as F
ROOT=Path(__file__).resolve().parent
V17=ROOT.parent/'v17_regime_coalition'
V12=ROOT.parent/'v12_variable_mk'
sys.path.insert(0,str(V17));sys.path.insert(0,str(V12))
from neural_dual_v2 import DualNet
from distill_dual_policy import obs_actor,generate_state,TASKS,estimate
from v12 import Config,World,write_json

def parse():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--source',default='v17_DISTILL_LATTICE_R8_s3111_fix')
 p.add_argument('--seed',type=int,default=6111)
 p.add_argument('--regularize',type=float,default=3.)
 p.add_argument('--updates',type=int,default=450)
 p.add_argument('--mode',choices=['on_single','on_all','off_synthetic'],default='on_single')
 p.add_argument('--batch',type=int,default=12)
 p.add_argument('--horizon',type=int,default=20)
 p.add_argument('--lr',type=float,default=.002)
 p.add_argument('--eval-every',type=int,default=150)
 p.add_argument('--device',choices=['cuda','cpu'],default='cuda')
 return p.parse_args()

def run(a):
 torch.set_num_threads(3)
 torch.manual_seed(a.seed)
 src=V17/'runs'/a.source
 conf=json.loads((src/'teacher_spec.json').read_text('utf8'))
 init=torch.load(src/'teacher_latest.pt',map_location=a.device,weights_only=False)
 actor=DualNet(120,conf['h'],conf['rounds'],conf['quorum'],conf['features'],False,True).to(a.device)
 teacher=DualNet(120,conf['h'],conf['rounds'],conf['quorum'],conf['features'],False,True).to(a.device)
 actor.load_state_dict(init['model']);teacher.load_state_dict(init['model'])
 for p in teacher.parameters():p.requires_grad_(False)
 opt=torch.optim.Adam(actor.parameters(),lr=a.lr)
 dest=ROOT/'runs'/a.name;dest.mkdir(parents=True,exist_ok=True)
 specfile=dest/'spec.json'
 if specfile.exists():
  old=json.loads(specfile.read_text('utf8'))
  previous={k:v for k,v in old.items() if k!='updates'}
  now={k:v for k,v in vars(a).items() if k!='updates'}
  if previous!=now or a.updates<int(old['updates']):
   raise RuntimeError('Only an extension of total updates is allowed when resuming')
 write_json(specfile,vars(a))
 ck=dest/'latest.pt';start=0
 if ck.exists():
  c=torch.load(ck,map_location=a.device,weights_only=False)
  actor.load_state_dict(c['model']);opt.load_state_dict(c['optimizer'])
  start=c['update']
 def record(u,loss=0.):
  results=estimate(actor,a.device,seed=951001,batch=24,steps=24)
  row=dict(update=u,loss=float(loss.detach()) if hasattr(loss,'detach') else float(loss),results=results)
  with (dest/'history.jsonl').open('a',encoding='utf8') as f:
   f.write(json.dumps(row)+'\n')
  print('ONPOLICY_RESULT',a.name,u,
    'TRAP',round(results['M50_k4_trap']['food'],4),
    'EXACT',results['M50_k4_trap']['exact'],
    'OOD8',round(results['M72_k8_random']['food'],4),flush=True)
 def save(u):
  tmp=dest/'tmp.pt'
  torch.save(dict(model=actor.state_dict(),optimizer=opt.state_dict(),
                  update=u,source=a.source),tmp)
  os.replace(tmp,ck)
  if u%300==0 or u==a.updates:
   torch.save(dict(model=actor.state_dict(),update=u),
                 dest/f'checkpoint_{u:05d}.pt')
 if not (dest/'history.jsonl').exists():record(start)
 for update in range(start+1,a.updates+1):
  m,k=TASKS[(update-1)%len(TASKS)]
  cfg=Config(n=120,m=m,k=k,degree=8,
        batch=a.batch,horizon=a.horizon,device=a.device,
        init='trap' if update%2 else 'random',
        alpha=0.,gamma=.97,entropy=.006)
  env=World(cfg,a.seed+update*977)
  actor.reset()
  logs=[];ents=[];foods=[];reg_terms=[]
  chosen_step=(update-1)%cfg.horizon
  for t in range(cfg.horizon):
   if a.mode=='on_all' or (a.mode=='on_single' and t==chosen_step):
    logits,sign=obs_actor(env,actor)
    with torch.no_grad():
     reference,_=obs_actor(env,teacher)
     target=reference.sigmoid()
    mask=torch.stack((sign>0,sign<0,sign<0),dim=-1).float()
    cost=(F.binary_cross_entropy_with_logits(logits,target,reduction='none')*mask).sum()/mask.sum().clamp_min(1)
    reg_terms.append(cost)
   jobs,lp,ent=actor.act(env)
   logs.append(lp);ents.append(ent)
   foods.append(env.advance(jobs))
  r=torch.stack(foods)
  ret=torch.zeros_like(r[0]);returns=[]
  for v in r.flip(0):
   ret=v+cfg.gamma*ret
   returns.append(ret)
  R=torch.stack(returns[::-1])
  baseline=(R.sum(1,keepdim=True)-R)/(cfg.batch-1)
  advantage=((R-baseline)/R.std(1,keepdim=True,unbiased=False).clamp_min(.2)).detach()
  pg=-(torch.stack(logs)*advantage).mean()-cfg.entropy*torch.stack(ents).mean()
  if a.mode=='off_synthetic':
   cm=replace(cfg,m=TASKS[(update*7)%len(TASKS)][0],
       k=TASKS[(update*7)%len(TASKS)][1])
   e=generate_state(cm,a.seed+update*1709,
      ('trap','neartrap','optimum','random','overfragmented','partiallyfragmented')[update%6])
   logits,sign=obs_actor(e,actor)
   with torch.no_grad():reference,_=obs_actor(e,teacher)
   mask=torch.stack((sign>0,sign<0,sign<0),dim=-1).float()
   reg_terms.append((F.binary_cross_entropy_with_logits(
       logits,reference.sigmoid(),reduction='none')*mask).sum()/mask.sum().clamp_min(1))
  loss=pg+a.regularize*torch.stack(reg_terms).mean()
  opt.zero_grad(set_to_none=True)
  loss.backward()
  with torch.no_grad():
   norms=torch.zeros(120,device=a.device)
   for p in actor.parameters():
    if p.grad is not None:norms+=p.grad.reshape(120,-1).square().sum(1)
   scale=(2/(norms.sqrt()+1e-10)).clamp(max=1)
   for p in actor.parameters():
    if p.grad is not None:p.grad.mul_(scale.reshape(120,*([1]*(p.ndim-1))))
  opt.step()
  if update%a.eval_every==0 or update==a.updates:
   record(update,loss);save(update)
 write_json(dest/'status.json',dict(state='completed',update=a.updates,mode=a.mode))
 print('ONPOLICY_COMPLETE',a.name,a.updates,flush=True)
if __name__=='__main__':run(parse())
