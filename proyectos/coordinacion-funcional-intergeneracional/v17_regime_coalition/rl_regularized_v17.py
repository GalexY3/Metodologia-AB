"""V17 private REINFORCE plus frozen teacher policy regularizer.

The policy prior is an EXPLICIT researcher-supervised intervention; learned
rewards are strictly own realized food. This experiment tests whether
individual actor-critic policy updates can preserve a previously discovered
cooperation protocol, not whether they discover it autonomously.
"""
from __future__ import annotations
from dataclasses import replace
import os,time,json,math,argparse
from pathlib import Path
import torch,numpy as np
from torch.nn import functional as F
import neural_pledge
import neural_dual_v2
from v12 import Config
from distill_dual_policy import obs_actor,generate_state,TASKS,estimate
envlib=neural_pledge.envlib
HERE=Path(__file__).resolve().parent
def parse():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--source',default='v17_DISTILL_LATTICE_R8_s3111_fix')
 p.add_argument('--regularize',type=float,default=.2)
 p.add_argument('--updates',type=int,default=500)
 p.add_argument('--lr',type=float,default=.002)
 p.add_argument('--seed',type=int,default=5111)
 p.add_argument('--batch',type=int,default=12)
 p.add_argument('--horizon',type=int,default=20)
 p.add_argument('--device',choices=['cpu','cuda'],default='cuda')
 p.add_argument('--eval-every',type=int,default=100)
 return p.parse_args()
def main(args):
 torch.set_num_threads(4)
 root=HERE/'runs'/args.name
 root.mkdir(parents=True,exist_ok=True)
 source=HERE/'runs'/args.source
 spec=json.loads((source/'teacher_spec.json').read_text('utf8'))
 info=vars(args)
 (root/'spec.json').write_text(json.dumps(info,indent=2),encoding='utf8')
 policy=neural_dual_v2.DualNet(120,spec['h'],spec['rounds'],
     spec['quorum'],spec['features'],False,True).to(args.device)
 frozen=neural_dual_v2.DualNet(120,spec['h'],spec['rounds'],
     spec['quorum'],spec['features'],False,True).to(args.device)
 ck=torch.load(source/'teacher_latest.pt',map_location=args.device,weights_only=False)
 policy.load_state_dict(ck['model'])
 frozen.load_state_dict(ck['model'])
 for param in frozen.parameters():param.requires_grad_(False)
 optimizer=torch.optim.Adam(policy.parameters(),lr=args.lr)
 started=time.perf_counter()
 print('REG_RL_START',args.name,'lambda',args.regularize,flush=True)
 def dev(u):
  metrics=estimate(policy,args.device,seed=951001,batch=24,steps=24)
  row=dict(update=u,lambda_bc=args.regularize,
     trap=metrics['M50_k4_trap'],ood=metrics['M72_k8_random'],
     evaluations=metrics,elapsed=time.perf_counter()-started)
  with (root/'history.jsonl').open('a',encoding='utf8') as fh:
   fh.write(json.dumps(row)+'\n')
  envlib.write_json(root/'status.json',dict(state='running',**row))
  print('REG_RL',args.name,u,'trap',round(row['trap']['food'],4),
        'exact',row['trap']['exact'],
        'novel',round(row['ood']['food'],4),flush=True)
 def checkpoint(u):
  tmp=root/'tmp.pt'
  torch.save(dict(update=u,model=policy.state_dict(),
   optimizer=optimizer.state_dict(),lambda_bc=args.regularize),tmp)
  os.replace(tmp,root/'latest.pt')
  if u%250==0 or u==args.updates:
   torch.save(dict(update=u,model=policy.state_dict(),
    optimizer=optimizer.state_dict()),root/f'checkpoint_{u:04d}.pt')
 dev(0)
 for u in range(1,args.updates+1):
  m,k=TASKS[(u-1)%len(TASKS)]
  init='trap' if u%2 else 'random'
  c=Config(n=120,m=m,k=k,degree=8,batch=args.batch,
    horizon=args.horizon,device=args.device,
    init=init,alpha=0.,gamma=.97,entropy=.006)
  result=envlib.rollout(policy,c,args.seed+u*977)
  r=torch.stack(result['rewards'])
  v=torch.zeros_like(r[0])
  returns=[]
  for rew in reversed(r):
   v=rew+c.gamma*v
   returns.append(v)
  returns=torch.stack(returns[::-1])
  baseline=(returns.sum(1,keepdim=True)-returns)/(c.batch-1)
  std=returns.std(dim=1,unbiased=False,keepdim=True).clamp_min(.2)
  advantage=((returns-baseline)/std).detach()
  logprobs=torch.stack(result['logs'])
  ent=torch.stack(result['ents'])
  pg=-(logprobs*advantage).mean()-c.entropy*ent.mean()
  # Maintain policy imitation *on OFF-POLICY private states* drawn from
  # deliberately varied quotas. Each reference output uses only own food
  # and neighborhood observations; no global simulator labels.
  regtask=TASKS[(u*7)%len(TASKS)]
  cm=replace(c,m=regtask[0],k=regtask[1])
  kinds=('trap','neartrap','optimum','random','overfragmented','partiallyfragmented')
  e=generate_state(cm,args.seed+u*1709,kinds[u%len(kinds)])
  logits,sign=obs_actor(e,policy)
  with torch.no_grad():
   teacher,tsign=obs_actor(e,frozen)
   expected=teacher.sigmoid()
  mask=torch.stack((sign>0,sign<0,sign<0),dim=2).float()
  penalty=(F.binary_cross_entropy_with_logits(logits,expected,reduction='none')*
      mask).sum()/mask.sum().clamp_min(1)
  loss=pg+args.regularize*penalty
  optimizer.zero_grad(set_to_none=True)
  loss.backward()
  # Clip per-agent independent actor gradients.
  norms=torch.zeros(120,device=args.device)
  for param in policy.parameters():
   if param.grad is not None:
    norms+=param.grad.detach().reshape(120,-1).square().sum(1)
  norms=norms.sqrt()
  with torch.no_grad():
   scale=(2/(norms+1e-10)).clamp(max=1)
   for param in policy.parameters():
    if param.grad is not None:
     param.grad.mul_(scale.reshape(120,*([1]*(param.ndim-1))))
  optimizer.step()
  if u%args.eval_every==0 or u==args.updates:
   dev(u);checkpoint(u)
 envlib.write_json(root/'status.json',dict(state='completed',
    updates=args.updates,regularize=args.regularize))
 print('REG_RL_COMPLETED',args.name,args.updates,flush=True)
if __name__=='__main__':main(parse())
