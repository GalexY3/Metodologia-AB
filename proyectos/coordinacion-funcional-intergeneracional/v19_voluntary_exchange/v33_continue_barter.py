"""Continue pretrained-from-scratch V30 contractual specialists, no teacher.

Two separate continuations from the same 700-update checkpoint:
all private actor parameters or only privately learned occupational actor.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK
from v23_joint_cold import gradients_per_agent
import v25_multi_capacity as base
import v30_consensual as contract
ROOT=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--source',required=True)
 p.add_argument('--mode',choices=('joint','role_only'),required=True)
 p.add_argument('--total-updates',type=int,default=2100)
 p.add_argument('--eval-every',type=int,default=200)
 p.add_argument('--device',choices=('cpu','cuda'),default='cpu')
 a=p.parse_args()
 torch.set_num_threads(2)
 folder=ROOT/'runs'/a.source
 oldspec=json.loads((folder/'v25_spec.json').read_text('utf8'))
 oldstatus=json.loads((folder/'v25_status.json').read_text('utf8'))
 assert oldspec['settlement']=='mutual'
 assert oldstatus['state']=='completed' and oldstatus['updates']==700
 assert a.total_updates>oldstatus['updates']
 checkpoint=torch.load(folder/'joint_latest.pt',map_location='cpu',weights_only=False)
 assert checkpoint['update']==oldstatus['updates']
 output=ROOT/'runs'/a.name
 output.mkdir(parents=True,exist_ok=False)
 spec=dict(oldspec,updates=a.total_updates,device=a.device,
     continuation_from=a.source,continuation_mode=a.mode,
     previously_trained=700,additional_updates=a.total_updates-700,
     constant_cost_during_continuation=oldspec['cost'])
 (output/'v25_spec.json').write_text(json.dumps(spec,indent=2),encoding='utf8')
 donor=PrivateGiftActor(spec['n'],spec['hidden'],spec['init_scale']).to(a.device)
 role=PrivateOccupationK(spec['n'],spec['k'],spec['hidden']).to(a.device)
 donor.load_state_dict(checkpoint['gift'])
 role.load_state_dict(checkpoint['role'])
 opt_gift=torch.optim.Adam(donor.parameters(),lr=spec['lr_gift'])
 opt_role=torch.optim.Adam(role.parameters(),lr=spec['lr_role'])
 opt_gift.load_state_dict(checkpoint['opt_gift'])
 opt_role.load_state_dict(checkpoint['opt_role'])
 if a.mode=='role_only':donor.requires_grad_(False)
 contract.install('mutual')
 if a.device=='cpu':
   torch.set_rng_state(checkpoint['rng_cpu'])
 else:
   torch.manual_seed(spec['seed']+700)
   if checkpoint.get('rng_gpu') is not None:
     torch.cuda.set_rng_state(checkpoint['rng_gpu'])
 t0=time.perf_counter()
 for u in range(701,a.total_updates+1):
  c=C(n=spec['n'],k=spec['k'],degree=6,topology='ring',
      batch=spec['batch'],horizon=spec['horizon'],
      cost=spec['cost'],gamma=spec['gamma'],device=a.device)
  metrics,rewards,lg,ge,lr,er,rt=contract.traced_roll(
    c,donor,role,spec['seed']*19301+31*u,init='mixed',
    interval=spec['role_interval'],move_cost=spec['move_cost'])
  G=torch.zeros_like(rewards[0]);history=[]
  for value in reversed(rewards):
   G=value+c.gamma*G;history.append(G)
  ret=torch.stack(history[::-1])
  leave=(ret.sum(1,keepdim=True)-ret)/(c.batch-1)
  advantage=((ret-leave)/ret.std(1,unbiased=False,
       keepdim=True).clamp_min(.25)).detach()
  role_loss=-(torch.stack(lr)*advantage[rt]).mean()-spec['ent_role']*torch.stack(er).mean()
  if a.mode=='joint':
    gift_loss=-(torch.stack(lg)*advantage).mean()-spec['ent_gift']*torch.stack(ge).mean()
    loss=gift_loss+role_loss
  else:
    gift_loss=torch.tensor(0.,device=a.device)
    loss=role_loss
  opt_role.zero_grad(set_to_none=True)
  opt_gift.zero_grad(set_to_none=True)
  loss.backward()
  gradients_per_agent(role,spec['n'])
  if a.mode=='joint':
    gradients_per_agent(donor,spec['n'])
    opt_gift.step()
  opt_role.step()
  if u==701 or u in (900,1100,1400,1700,2100) or u==a.total_updates:
    rngcpu=torch.get_rng_state()
    rnggpu=torch.cuda.get_rng_state() if a.device=='cuda' else None
    with torch.no_grad():
      from types import SimpleNamespace
      settings=SimpleNamespace(n=spec['n'],k=spec['k'],horizon=spec['horizon'],
          cost=spec['cost'],gamma=spec['gamma'],
          role_interval=spec['role_interval'],move_cost=spec['move_cost'],
          device=a.device)
      development=base.evaluate(donor,role,settings)
    torch.set_rng_state(rngcpu)
    if rnggpu is not None:torch.cuda.set_rng_state(rnggpu)
    entry=dict(update=u,train=metrics,
      development=development,elapsed=time.perf_counter()-t0,
      role_loss=float(role_loss.detach()),gift_loss=float(gift_loss.detach()))
    with (output/'v25_history.jsonl').open('a',encoding='utf8') as f:
       f.write(json.dumps(entry)+'\n')
    tmp=output/'tmp_joint.pt'
    torch.save(dict(gift=donor.state_dict(),role=role.state_dict(),
       opt_gift=opt_gift.state_dict(),opt_role=opt_role.state_dict(),
       update=u,rng_cpu=torch.get_rng_state(),
       rng_gpu=torch.cuda.get_rng_state() if a.device=='cuda' else None),tmp)
    os.replace(tmp,output/'joint_latest.pt')
    main=next(x for x in development if x['topology']=='ring' and
       x['init']=='monolith' and x['condition']=='normal')
    print('V33',a.name,'u',u,'FOOD',round(main['food'],4),
      'CONTRACTS',round(main['settled_units_per_person'],3),
      'POTENTIAL',round(main['potential_coverage'],3),
      'BALANCED',round(main['balanced'],3),
      'elapsed',round(time.perf_counter()-t0,1),flush=True)
 (output/'v25_status.json').write_text(json.dumps(dict(state='completed',
    updates=a.total_updates,elapsed_seconds=time.perf_counter()-t0)),encoding='utf8')
 print('V33_FINISHED',a.name,flush=True)
if __name__=='__main__':main()
