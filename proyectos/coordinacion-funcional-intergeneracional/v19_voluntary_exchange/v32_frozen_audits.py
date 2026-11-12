"""V32 institution choice: frozen held-out tests and matched mode-intervention.

All actors' parameters are frozen. The counterfactual forces only person i's
round-zero institutional choice; all other choices remain freely stochastic.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK,start4
from v32_institution_choice import PrivateInstitutionActor,hybrid_step,roll
from audit_targeted import SEEDS
ROOT=Path(__file__).resolve().parent
STATE_FIELDS=('roles','prev_gift','prev_recipient','incoming','trust',
      'lastfood','full','cover','last_switch')

def load(name,device):
 p=ROOT/'runs'/name
 spec=json.loads((p/'v32_spec.json').read_text('utf8'))
 status=json.loads((p/'v32_status.json').read_text('utf8'))
 assert status['state']=='completed' and status['updates']==spec['updates']
 chk=torch.load(p/'joint_latest.pt',map_location='cpu',weights_only=False)
 assert chk['update']==status['updates']==spec['updates']
 gift=PrivateGiftActor(spec['n'],spec['hidden'],spec['init_scale']).to(device)
 role=PrivateOccupationK(spec['n'],spec['k'],spec['hidden']).to(device)
 mode=PrivateInstitutionActor(spec['n'],spec['k'],spec['hidden'],spec['mode_bias']).to(device)
 gift.load_state_dict(chk['gift'])
 role.load_state_dict(chk['role'])
 mode.load_state_dict(chk['mode'])
 for actor in (gift,role,mode):
  actor.eval().requires_grad_(False)
 return gift,role,mode,spec

def relocated(gift,role,mode,spec,device):
 gen=torch.Generator(device='cpu');gen.manual_seed(20261112)
 perm=torch.randperm(spec['n'],generator=gen)
 def rep(state):
  return {k:(v.index_select(0,perm.to(v.device)).clone()
    if v.ndim>0 and v.shape[0]==spec['n'] else v.clone()) for k,v in state.items()}
 d=PrivateGiftActor(spec['n'],spec['hidden'],spec['init_scale']).to(device)
 r=PrivateOccupationK(spec['n'],spec['k'],spec['hidden']).to(device)
 m=PrivateInstitutionActor(spec['n'],spec['k'],spec['hidden'],spec['mode_bias']).to(device)
 d.load_state_dict(rep(gift.state_dict()));r.load_state_dict(rep(role.state_dict()))
 m.load_state_dict(rep(mode.state_dict()))
 for a in (d,r,m):a.eval().requires_grad_(False)
 return d,r,m

@torch.no_grad()
def heldout(name,worlds,steps,device):
 gift,role,mode,spec=load(name,device)
 d2,r2,m2=relocated(gift,role,mode,spec,device)
 configurations=[
  ('learned',gift,role,mode,None,True,None,False),
  ('always_mutual',gift,role,mode,'mutual',True,None,False),
  ('always_unilateral',gift,role,mode,'unilateral',True,None,False),
  ('random_mode',gift,role,mode,'random',True,None,False),
  ('no_social',gift,role,mode,None,False,None,False),
  ('role_fixed',gift,role,mode,None,True,'fixed',False),
  ('role_random_035',gift,role,mode,None,True,'random_0.35',False),
  ('donations_blocked',gift,role,mode,None,True,None,True),
  ('relocated_people',d2,r2,m2,None,True,None,False)]
 out=[]
 for topo,init in (('ring','monolith'),('ring','random'),('rewired','monolith')):
  rows={name:[] for name,*_ in configurations}
  for seed in SEEDS:
   c=C(n=spec['n'],k=4,degree=6,topology=topo,
      batch=worlds,horizon=steps,cost=spec['cost'],gamma=spec['gamma'],device=device)
   for label,g,r,m,forcing,social,rolebaseline,blocked in configurations:
    torch.manual_seed(seed*41+202611)
    values,*_=roll(c,g,r,m,seed,init=init,
      interval=spec['role_interval'],move_cost=spec['move_cost'],
      mode_override=forcing,social=social,role_baseline=rolebaseline,
      gift_blocked=blocked)
    rows[label].append(dict(seed=seed,**values))
  keys=['food','last_food','adoption','proposals_per_agent',
        'transfers_per_agent','matched_contracts_per_agent',
        'realized_coverage','useful_fraction','potential_coverage',
        'balanced','nonempty_professions','switches']
  for label,values in rows.items():
   data=dict(model=name,topology=topo,init=init,condition=label,
     worlds=worlds*len(SEEDS),
     **{key:float(np.mean([v[key] for v in values])) for key in keys},
     by_seed=values)
   out.append(data)
   if topo=='ring' and init=='monolith':
    print('V32_HOLDOUT',name,label,'food',round(data['food'],4),
      'adopt',round(data['adoption'],3),
      'units',round(data['transfers_per_agent'],3),flush=True)
 (ROOT/'results'/('v32_holdout_'+name+'.json')).write_text(
  json.dumps(dict(name=name,training_spec=spec,
    worlds_per_seed=worlds,seeds=SEEDS,rows=out),indent=1),encoding='utf8')
 print('V32_HOLDOUT_DONE',name,len(out),flush=True)

@torch.no_grad()
def forced(c,gift,role,mode,seed,init,social,value,interval=8,move_cost=.015):
 n=c.n;big=replace(c,batch=c.batch*n)
 torch.manual_seed(seed*29+2207)
 original=start4(c,seed,init)
 w={'graph':original['graph'],'t':0}
 for k in STATE_FIELDS:w[k]=original[k].repeat_interleave(n,0)
 subject=torch.arange(n,device=c.device).repeat(c.batch)
 ids=torch.arange(big.batch,device=c.device)
 total=torch.zeros(big.batch,device=c.device)
 first=None
 for t in range(c.horizon):
  if t%interval==0:
   newrole,_,_=role.act(big,w,history=social)
   changed=(newrole!=w['roles']).float()
   w['roles']=newrole
   w['last_switch']=changed
  institutions,_,_=mode.act(big,w,social=social)
  if t==0:
   institutions=institutions.clone()
   institutions[ids,subject]=value
  actions=[gift.act(big,w,mode=('normal' if social else 'no_social'))
      for _ in range(big.k-1)]
  dests=torch.stack([z[0] for z in actions],2)
  offers=torch.stack([z[1] for z in actions],2)
  food,_=hybrid_step(big,w,dests,offers,institutions)
  if t%interval==0:
   food=food-move_cost*changed
   w['lastfood']=food
  own=food[ids,subject]
  total+=(c.gamma**t)*own
  if t==0:first=own.clone()
 reshape=lambda x:x.reshape(c.batch,n).detach().cpu().numpy()
 return dict(total=reshape(total),initial=reshape(first),
    future=reshape(total-first))

@torch.no_grad()
def causal(name,worlds,steps,device):
 gift,role,mode,spec=load(name,device)
 results=[]
 for topo,init in (('ring','monolith'),('ring','random'),
                   ('rewired','monolith')):
  c=C(n=spec['n'],k=4,degree=6,topology=topo,
    batch=worlds,horizon=steps,cost=spec['cost'],
    gamma=spec['gamma'],device=device)
  for social in (True,False):
   by_seed=[]
   for seed in SEEDS:
    contract=forced(c,gift,role,mode,seed,init,social,1,
        interval=spec['role_interval'],move_cost=spec['move_cost'])
    unilateral=forced(c,gift,role,mode,seed,init,social,0,
        interval=spec['role_interval'],move_cost=spec['move_cost'])
    diff={k:contract[k]-unilateral[k] for k in contract}
    by_seed.append(dict(seed=seed,per_agent={key:v.mean(0).tolist()
      for key,v in diff.items()}))
   x=np.array([a['per_agent']['total'] for a in by_seed])
   instant=np.array([a['per_agent']['initial'] for a in by_seed])
   row=dict(model=name,topology=topo,init=init,
      mode=('normal' if social else 'no_social'),mean_total=float(x.mean()),
      mean_initial=float(instant.mean()),
      mean_future=float(x.mean()-instant.mean()),
      positive_agents=int((x.mean(0)>0).sum()),
      per_agent=x.mean(0).tolist(),by_seed=by_seed)
   results.append(row)
   print('V32_CAUSAL',name,topo,init,row['mode'],'total',
     round(row['mean_total'],4),'instant',round(row['mean_initial'],4),
     'pos',row['positive_agents'],'/',spec['n'],flush=True)
 (ROOT/'results'/('v32_causal_'+name+'.json')).write_text(
  json.dumps(dict(name=name,spec=spec,worlds_per_seed=worlds,
    horizon=steps,seeds=SEEDS,rows=results,
    intervention='Force only one person contractual versus unilateral choice at t=0; all other actions and later mode choices are stochastic.'),indent=1),
  encoding='utf8')
 print('V32_CAUSAL_DONE',name,len(results),flush=True)

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--kind',choices=('holdout','causal'),required=True)
 p.add_argument('--worlds',type=int,default=12)
 p.add_argument('--steps',type=int,default=48)
 p.add_argument('--device',choices=('cuda','cpu'),default='cuda')
 a=p.parse_args();torch.set_num_threads(2)
 start=time.perf_counter()
 if a.kind=='holdout':heldout(a.name,a.worlds,a.steps,a.device)
 else:causal(a.name,a.worlds,a.steps,a.device)
 print('V32_EVAL_SECONDS',round(time.perf_counter()-start,1),flush=True)
if __name__=='__main__':main()
