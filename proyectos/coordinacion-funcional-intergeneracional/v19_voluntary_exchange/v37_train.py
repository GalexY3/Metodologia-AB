"""V37: individual-only RL of newcomer cohort under fixed incumbent policies.

Each rollout models 24 rounds of a functioning old village, replaces exactly
30 designated positions, then trains only the 30 newcomers' PRIVATE weights
from their own subsequent food returns. Original 90 residents never update.
"""
from __future__ import annotations
import argparse,copy,json,os,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK,start4
from v25_holdout import load
from v30_consensual import contract_step
from v23_joint_cold import gradients_per_agent
ROOT=Path(__file__).resolve().parent

def newcomer_indices(n,seed,device='cpu'):
 gen=torch.Generator(device='cpu')
 gen.manual_seed(seed+37001)
 return torch.randperm(n,generator=gen)[:n//4].sort().values.to(device)

def initial_cohort(old_gift,old_role,spec,device,seed):
 n=spec['n']
 ids=newcomer_indices(n,seed,device)
 newcomer_gift=copy.deepcopy(old_gift).requires_grad_(True)
 newcomer_role=copy.deepcopy(old_role).requires_grad_(True)
 with torch.random.fork_rng(devices=([torch.cuda.current_device()] if device=='cuda' else [])):
  torch.manual_seed(seed*73+3701)
  freshgift=PrivateGiftActor(n,spec['hidden'],spec['init_scale']).to(device)
  freshrole=PrivateOccupationK(n,spec['k'],spec['hidden']).to(device)
 with torch.no_grad():
  for changed,source in ((newcomer_gift,freshgift),(newcomer_role,freshrole)):
   src=dict(source.named_parameters())
   for name,param in changed.named_parameters():
    param[ids]=src[name][ids]
 return newcomer_gift,newcomer_role,ids

def replace_people(c,w,ids,seed):
 new=torch.zeros(c.n,dtype=torch.bool,device=c.device)
 new[ids]=True
 rng=torch.Generator(device=c.device)
 rng.manual_seed(seed*8303+421)
 w['roles'][:,ids]=torch.randint(c.k,(c.batch,len(ids)),device=c.device,generator=rng)
 w['lastfood'][:,ids]=.20
 w['prev_gift'][:,ids]=0
 w['prev_recipient'][:,ids]=-1
 w['cover'][:,ids]=0
 w['full'][:,ids]=0
 w['last_switch'][:,ids]=0
 touched=new[w['graph']]
 w['trust'][:,touched]=0
 w['incoming'][:,touched]=0
 w['trust'][:,ids,:]=0
 w['incoming'][:,ids,:]=0
 return new

def episode(c,inc_gift,inc_role,cohort_gift,cohort_role,ids,seed,
            init='mixed',move_cost=.015,interval=8):
 """The only REINFORCE terms are created AFTER the newcomer arrival."""
 torch.manual_seed(seed*73+41)
 world=start4(c,seed,init)
 r_post=[];gift_lp=[];gift_en=[];role_lp=[];role_en=[];role_time=[]
 metrics=dict(pre=[],post=[],new=[],resident=[],matched=[])
 newcomer_mask=torch.zeros(c.n,dtype=torch.bool,device=c.device)
 newcomer_mask[ids]=True
 for t in range(48):
  active=t>=24
  actor_g=cohort_gift if active else inc_gift
  actor_r=cohort_role if t>24 else inc_role
  # Original occupants make the last occupation decision before arrival.
  if t%interval==0:
   if t<24:
    with torch.no_grad():occupations,_,_=actor_r.act(c,world)
   else:
    occupations,lp,ent=actor_r.act(c,world)
    if t>24:role_lp.append(lp);role_en.append(ent);role_time.append(t-24)
   changed=(occupations!=world['roles']).float()
   world['roles']=occupations
   world['last_switch']=changed
  if t==24:
   replace_people(c,world,ids,seed)
  if t<24:
   with torch.no_grad():
    samples=[actor_g.act(c,world,mode='normal') for _ in range(3)]
  else:
   samples=[actor_g.act(c,world,mode='normal') for _ in range(3)]
   gift_lp.append(torch.stack([x[2] for x in samples]).sum(0))
   gift_en.append(torch.stack([x[3] for x in samples]).sum(0))
  dest=torch.stack([x[0] for x in samples],2)
  offers=torch.stack([x[1] for x in samples],2)
  food,_=contract_step(c,world,dest,offers)
  if t%interval==0:
   food=food-move_cost*changed
   world['lastfood']=food
  metrics['pre' if t<24 else 'post'].append(float(food.mean().detach()))
  if active:
   r_post.append(food)
   metrics['new'].append(float(food[:,newcomer_mask].mean().detach()))
   metrics['resident'].append(float(food[:,~newcomer_mask].mean().detach()))
   metrics['matched'].append(float(offers.sum(2).mean().detach()))
 return (torch.stack(r_post),gift_lp,gift_en,role_lp,role_en,role_time,
         {key:float(np.mean(val)) for key,val in metrics.items() if val})

def unitprice(a,update,target_cost):
 if update<=a.flat:return a.low_cost
 return a.low_cost+(target_cost-a.low_cost)*min(1.,(update-a.flat)/a.rise)

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--source',required=True)
 p.add_argument('--updates',type=int,default=700)
 p.add_argument('--batch',type=int,default=12)
 p.add_argument('--flat',type=int,default=250)
 p.add_argument('--rise',type=int,default=200)
 p.add_argument('--low-cost',type=float,default=.002)
 p.add_argument('--eval-every',type=int,default=140)
 p.add_argument('--device',choices=('cuda','cpu'),default='cuda')
 a=p.parse_args()
 assert a.updates>=a.flat+a.rise
 torch.set_num_threads(2)
 donor,role,source=load(a.source,a.device)
 assert source['n']==120 and source['k']==4 and source['settlement']=='mutual'
 assert source['cost'] in (.04,.12)
 for obj in (donor,role):obj.eval().requires_grad_(False)
 cohort_g,cohort_r,ids=initial_cohort(donor,role,source,a.device,source['seed'])
 # The 90 incumbent parameter groups match bit-for-bit.
 for orig,new in ((donor,cohort_g),(role,cohort_r)):
  for name,w in orig.named_parameters():
   assert torch.equal(w[~torch.isin(torch.arange(source['n'],device=a.device),ids)],
     dict(new.named_parameters())[name][~torch.isin(torch.arange(source['n'],device=a.device),ids)])
 start_g=copy.deepcopy(cohort_g.state_dict());start_r=copy.deepcopy(cohort_r.state_dict())
 optimizer_g=torch.optim.Adam(cohort_g.parameters(),lr=source['lr_gift'])
 optimizer_r=torch.optim.Adam(cohort_r.parameters(),lr=source['lr_role'])
 folder=ROOT/'runs'/a.name;folder.mkdir(parents=True,exist_ok=False)
 metadata=dict(vars(a),source_spec=source,
      newcomer_indices=ids.cpu().tolist(),
      new_count=len(ids),
      newcomer_initialization_seed=source['seed']*73+3701)
 (folder/'v37_spec.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
 torch.save(dict(gift=start_g,role=start_r),folder/'initial_cohort.pt')
 np.random.seed(source['seed'])
 torch.manual_seed(source['seed']+370001)
 t0=time.perf_counter()
 mask=torch.zeros(source['n'],device=a.device)
 mask[ids]=1.
 mask=mask[None,None,:]
 for update in range(1,a.updates+1):
  c=C(n=120,k=4,degree=6,topology='ring',batch=a.batch,
       horizon=48,cost=unitprice(a,update,source['cost']),gamma=source['gamma'],
       device=a.device)
  returns,lg,eg,lr,er,rt,metrics=episode(c,donor,role,cohort_g,cohort_r,
     ids,seed=source['seed']*19301+31*update,
     init='mixed',interval=source['role_interval'],
     move_cost=source['move_cost'])
  total=torch.zeros_like(returns[0]);values=[]
  for reward in reversed(returns):
   total=reward+c.gamma*total
   values.append(total)
  G=torch.stack(values[::-1])
  baseline=(G.sum(1,keepdim=True)-G)/(c.batch-1)
  advantage=((G-baseline)/G.std(1,unbiased=False,
     keepdim=True).clamp_min(.25)).detach()
  lp_g=torch.stack(lg);en_g=torch.stack(eg)
  g_loss=-((lp_g*advantage+source['ent_gift']*en_g)*mask).sum()/(24*c.batch*len(ids))
  lp_r=torch.stack(lr);en_r=torch.stack(er)
  role_loss=-((lp_r*advantage[rt]+source['ent_role']*en_r)*mask).sum()/(len(rt)*c.batch*len(ids))
  optimizer_g.zero_grad(set_to_none=True)
  optimizer_r.zero_grad(set_to_none=True)
  (g_loss+role_loss).backward()
  for actor in (cohort_g,cohort_r):
   gradients_per_agent(actor,source['n'])
   for weight in actor.parameters():
    weight.grad[mask.reshape(-1)==0]=0
  optimizer_g.step();optimizer_r.step()
  if update==1 or update%a.eval_every==0 or update==a.updates:
   cpu=torch.get_rng_state()
   gpu=torch.cuda.get_rng_state() if a.device=='cuda' else None
   with torch.no_grad():
    finalc=C(n=120,k=4,degree=6,topology='ring',batch=a.batch,
        horizon=48,cost=source['cost'],gamma=source['gamma'],device=a.device)
    _,_,_,_,_,_,development=episode(finalc,donor,role,cohort_g,cohort_r,
      ids,seed=710000+source['seed'],init='monolith',
      interval=source['role_interval'],move_cost=source['move_cost'])
   torch.set_rng_state(cpu)
   if gpu is not None:torch.cuda.set_rng_state(gpu)
   with (folder/'v37_history.jsonl').open('a',encoding='utf8') as file:
    file.write(json.dumps(dict(update=update,price=c.cost,train=metrics,
       development=development,elapsed=time.perf_counter()-t0))+'\n')
   temporary=folder/'checkpoint_tmp.pt'
   torch.save(dict(gift=cohort_g.state_dict(),role=cohort_r.state_dict(),
      opt_gift=optimizer_g.state_dict(),opt_role=optimizer_r.state_dict(),
      update=update),temporary)
   os.replace(temporary,folder/'cohort_latest.pt')
   print('V37',a.name,'u',update,'PRICE',round(c.cost,4),
     'TRAIN_NEW',round(metrics['new'],4),'TRAIN_OLD',round(metrics['resident'],4),
     'DEV_NEW',round(development['new'],4),
     'DEV_RESIDENT',round(development['resident'],4),
     'time',round(time.perf_counter()-t0,1),flush=True)
 (folder/'v37_status.json').write_text(json.dumps(dict(state='completed',
   updates=a.updates,elapsed=time.perf_counter()-t0)),encoding='utf8')
 print('V37_FINISHED',a.name,flush=True)
if __name__=='__main__':main()
