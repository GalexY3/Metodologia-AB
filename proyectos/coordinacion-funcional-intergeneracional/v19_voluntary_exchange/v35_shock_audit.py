"""V35: frozen-policy social resilience under degree-preserving shocks.

Surplus restoration, job complementarity, newcomer and resident outcomes
are measured without gradient updates or social welfare reward.
"""
from __future__ import annotations
import argparse,copy,json,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK,start4,adjacent_potential
from v25_holdout import load
from audit_targeted import SEEDS
from exchange import make_graph
from v30_consensual import contract_step,OBSERVATIONS
ROOT=Path(__file__).resolve().parent
SHOCKS=('control','rewire','roles','newcomers')

@torch.no_grad()
def apply_shock(c,w,gift,role,shock,seed,spec):
 if shock=='control':return gift,role,None
 n=c.n
 if shock=='rewire':
  w['graph']=make_graph(n,c.degree,'rewired',seed+105173,c.device)
  w['trust'].zero_();w['incoming'].zero_()
  w['prev_recipient'].fill_(-1)
  return gift,role,None
 if shock=='roles':
  gen=torch.Generator(device=c.device);gen.manual_seed(seed*30019+155)
  permutations=torch.rand(c.batch,n,device=c.device,generator=gen).argsort(1)
  w['roles']=w['roles'].gather(1,permutations)
  return gift,role,None
 if shock=='newcomers':
  gen=torch.Generator(device='cpu');gen.manual_seed(seed+34012)
  ids=torch.randperm(n,generator=gen)[:n//4].sort().values.to(c.device)
  changed=torch.zeros(n,dtype=torch.bool,device=c.device)
  changed[ids]=True
  newgift=copy.deepcopy(gift)
  newrole=copy.deepcopy(role)
  with torch.random.fork_rng(devices=([torch.cuda.current_device()] if c.device=='cuda' else [])):
   torch.manual_seed(seed*73+743)
   freshgift=PrivateGiftActor(n,spec['hidden'],spec['init_scale']).to(c.device)
   freshrole=PrivateOccupationK(n,4,spec['hidden']).to(c.device)
  for dest,src in ((newgift,freshgift),(newrole,freshrole)):
   for name,weight in dest.named_parameters():
    other=dict(src.named_parameters())[name]
    weight.data[ids]=other.data[ids]
   dest.eval().requires_grad_(False)
  gen_roles=torch.Generator(device=c.device)
  gen_roles.manual_seed(seed*8303+421)
  w['roles'][:,ids]=torch.randint(4,(c.batch,len(ids)),device=c.device,generator=gen_roles)
  w['lastfood'][:,ids]=.2
  w['prev_gift'][:,ids]=0
  w['prev_recipient'][:,ids]=-1
  w['cover'][:,ids]=0
  w['full'][:,ids]=0
  w['last_switch'][:,ids]=0
  touched=changed[w['graph']]
  w['trust'][:,touched]=0
  w['incoming'][:,touched]=0
  w['trust'][:,ids,:]=0
  w['incoming'][:,ids,:]=0
  return newgift,newrole,changed
 raise ValueError(shock)

@torch.no_grad()
def simulate(name,seed,shock,worlds=16,device='cuda'):
 gift,role,spec=load(name,device)
 assert spec['settlement']=='mutual' and spec['n']==120
 c=C(n=120,k=4,degree=6,topology='ring',batch=worlds,
   horizon=48,cost=spec['cost'],gamma=spec['gamma'],device=device)
 torch.manual_seed(seed*73+41)
 w=start4(c,seed,'monolith')
 OBSERVATIONS.clear()
 history=[]
 group=None
 for t in range(48):
  if t%spec['role_interval']==0:
   chosen,_,_=role.act(c,w)
   switched=(chosen!=w['roles']).float()
   w['roles']=chosen
   w['last_switch']=switched
  # The t=24 role shock must follow the scheduled occupation choice:
  # otherwise the actor overwrites it before the gift decisions (null shock).
  if t==24:
   gift,role,group=apply_shock(c,w,gift,role,shock,seed,spec)
  actions=[gift.act(c,w,mode='normal') for _ in range(3)]
  dests=torch.stack([x[0] for x in actions],2)
  offers=torch.stack([x[1] for x in actions],2)
  reward,_=contract_step(c,w,dests,offers)
  if t%spec['role_interval']==0:
   reward=reward-spec['move_cost']*switched
   w['lastfood']=reward
  settled=OBSERVATIONS[-1][1]/(worlds*c.n)
  element=dict(round=t+1,food=float(reward.mean()),
    contracts=float(settled),
    coverage=float(w['cover'].mean()),
    role_potential=adjacent_potential(c,w))
  if group is not None:
   element['newcomer_food']=float(reward[:,group].mean())
   element['resident_food']=float(reward[:,~group].mean())
  history.append(element)
 def avg(key,start,end):
  return float(np.mean([x[key] for x in history[start:end]]))
 result=dict(model=name,shock=shock,seed=seed,worlds=worlds,
  food_first24=avg('food',0,24),
  food_25_32=avg('food',24,32),
  food_33_40=avg('food',32,40),
  food_41_48=avg('food',40,48),
  contracts_first24=avg('contracts',0,24),
  contracts_41_48=avg('contracts',40,48),
  potential_first24=avg('role_potential',0,24),
  potential_41_48=avg('role_potential',40,48),
  round_trace=history)
 if shock=='newcomers':
  result['newcomers_last8']=avg('newcomer_food',40,48)
  result['residents_last8']=avg('resident_food',40,48)
 return result

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--worlds',type=int,default=16)
 p.add_argument('--n-seeds',type=int,default=6)
 p.add_argument('--device',choices=('cuda','cpu'),default='cuda')
 a=p.parse_args()
 torch.set_num_threads(2)
 assert 1<=a.n_seeds<=len(SEEDS)
 rows=[];start=time.perf_counter()
 for seed in SEEDS[:a.n_seeds]:
  per={}
  for shock in SHOCKS:
   data=simulate(a.name,seed,shock,worlds=a.worlds,device=a.device)
   per[shock]=data
   if shock=='control':reference=data['food_41_48']
   data['surplus_restoration_vs_control']=(
       (data['food_41_48']-.20)/(reference-.20) if abs(reference-.20)>1e-5 else None)
   rows.append(data)
   print('V35',a.name,seed,shock,'pre',round(data['food_first24'],4),
     'late',round(data['food_41_48'],4),
     'ratio',None if data['surplus_restoration_vs_control'] is None
     else round(data['surplus_restoration_vs_control'],3),
     flush=True)
 original=ROOT/'runs'/a.name/'v25_spec.json'
 original_spec=json.loads(original.read_text('utf8'))
 target=ROOT/'results'/('v35_shocks_'+a.name+'.json')
 target.write_text(json.dumps(dict(model=a.name,original_spec=original_spec,
    seeds=SEEDS[:a.n_seeds],worlds_per_seed=a.worlds,shock_round=25,
    rows=rows,condition_names=SHOCKS,
    caveat='Frozen actors: evaluates immediate behavioral recovery, not neural retraining or inventing contractual rules.'),indent=1),encoding='utf8')
 print('V35_DONE',a.name,'rows',len(rows),
  'elapsed',round(time.perf_counter()-start,1),flush=True)
if __name__=='__main__':main()
