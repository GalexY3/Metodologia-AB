"""V37 paired holdout evaluation of individual-only newcomer learning.

Compares three frozen variants in otherwise identical 48-round societies:
incumbents only, raw replacement cohort, trained replacement cohort.
"""
from __future__ import annotations
import argparse,copy,json,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C
from v24_k4_joint import start4,adjacent_potential
from v25_holdout import load
from v30_consensual import contract_step,OBSERVATIONS
from audit_targeted import SEEDS
from v37_train import initial_cohort,newcomer_indices,replace_people
ROOT=Path(__file__).resolve().parent

def freeze_cohort(model,source,device):
 oldg,oldr,oldspec=load(source,device)
 model_dir=ROOT/'runs'/model
 spec=json.loads((model_dir/'v37_spec.json').read_text('utf8'))
 status=json.loads((model_dir/'v37_status.json').read_text('utf8'))
 assert spec['source']==source and status['state']=='completed'
 assert status['updates']==spec['updates'] and status['updates']>=1
 cohort_g,cohort_r,ids=initial_cohort(oldg,oldr,oldspec,device,oldspec['seed'])
 assert ids.cpu().tolist()==spec['newcomer_indices']
 fresh_g=copy.deepcopy(cohort_g).eval().requires_grad_(False)
 fresh_r=copy.deepcopy(cohort_r).eval().requires_grad_(False)
 initial=torch.load(model_dir/'initial_cohort.pt',weights_only=False,map_location='cpu')
 fresh_g.load_state_dict(initial['gift'])
 fresh_r.load_state_dict(initial['role'])
 trained_g=copy.deepcopy(fresh_g)
 trained_r=copy.deepcopy(fresh_r)
 latest=torch.load(model_dir/'cohort_latest.pt',weights_only=False,map_location='cpu')
 assert latest['update']==spec['updates']
 trained_g.load_state_dict(latest['gift'])
 trained_r.load_state_dict(latest['role'])
 for older,fresh,trained in ((oldg,fresh_g,trained_g),(oldr,fresh_r,trained_r)):
  allids=torch.arange(oldspec['n'],device=device)
  unchanged=~torch.isin(allids,ids)
  for name,value in older.named_parameters():
   assert torch.equal(value[unchanged],dict(fresh.named_parameters())[name][unchanged])
   assert torch.equal(value[unchanged],dict(trained.named_parameters())[name][unchanged])
  if not any(not torch.equal(dict(fresh.named_parameters())[k][ids],
                            dict(trained.named_parameters())[k][ids]) for k in dict(fresh.named_parameters())):
   raise AssertionError('No new agent weights changed after training')
 return oldg,oldr,(fresh_g,fresh_r),(trained_g,trained_r),ids,oldspec,spec

@torch.no_grad()
def simulate(c,oldg,oldr,newcomers,ids,seed,mode='trained'):
 assert mode in ('none','fresh','trained')
 torch.manual_seed(seed*73+41)
 w=start4(c,seed,'monolith')
 group=torch.zeros(c.n,dtype=torch.bool,device=c.device)
 group[ids]=True
 trace=[]
 for t in range(48):
  if t%8==0:
   before_role=oldr if t<=24 or mode=='none' else newcomers[1]
   chosen,_,_=before_role.act(c,w)
   changed=(chosen!=w['roles']).float()
   w['roles']=chosen
   w['last_switch']=changed
  if t==24 and mode!='none':
   replace_people(c,w,ids,seed)
  action_g=oldg if t<24 or mode=='none' else newcomers[0]
  opts=[action_g.act(c,w,mode='normal') for _ in range(3)]
  dests=torch.stack([a[0] for a in opts],2)
  offers=torch.stack([a[1] for a in opts],2)
  food,_=contract_step(c,w,dests,offers)
  if t%8==0:
   food=food-.015*changed
   w['lastfood']=food
  trace.append(dict(round=t+1,
    food=float(food.mean()),new_subgroup=float(food[:,group].mean()),
    old_subgroup=float(food[:,~group].mean()),
    proposals=float(offers.sum(2).mean()),
    settled_contract_units=OBSERVATIONS[-1][1]/(c.batch*c.n),
    potential=adjacent_potential(c,w)))
 def avg(k,start,end):return float(np.mean([x[k] for x in trace[start:end]]))
 return dict(mode=mode,seed=seed,worlds=c.batch,food_pre=avg('food',0,24),
  food_25_32=avg('food',24,32),food_33_40=avg('food',32,40),
  food_41_48=avg('food',40,48),
  newcomer_pre=avg('new_subgroup',0,24),
  newcomer_41_48=avg('new_subgroup',40,48),
  resident_41_48=avg('old_subgroup',40,48),
  proposals_41_48=avg('proposals',40,48),
  contracts_41_48=avg('settled_contract_units',40,48),
  potential_41_48=avg('potential',40,48),
  rounds=trace)

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--worlds',type=int,default=16)
 p.add_argument('--n-seeds',type=int,default=6)
 p.add_argument('--device',choices=('cpu','cuda'),default='cuda')
 a=p.parse_args()
 assert 1<=a.n_seeds<=len(SEEDS)
 torch.set_num_threads(2)
 spec=json.loads((ROOT/'runs'/a.name/'v37_spec.json').read_text('utf8'))
 oldg,oldr,fresh,trained,ids,source,meta=freeze_cohort(
   a.name,spec['source'],a.device)
 records=[];t0=time.perf_counter()
 for seed in SEEDS[:a.n_seeds]:
  cases={}
  for arm in ('none','fresh','trained'):
   c=C(n=120,k=4,degree=6,topology='ring',batch=a.worlds,horizon=48,
     gamma=source['gamma'],cost=source['cost'],device=a.device)
   case=simulate(c,oldg,oldr,
      fresh if arm=='fresh' else trained,ids,seed,mode=arm)
   cases[arm]=case
  assert abs(cases['none']['food_pre']-cases['fresh']['food_pre'])<1e-7
  assert abs(cases['none']['food_pre']-cases['trained']['food_pre'])<1e-7
  for arm in cases:
   case=cases[arm]
   ref=cases['none']['food_41_48']
   case['surplus_retained']=(case['food_41_48']-.2)/(ref-.2)
   records.append(case)
   print('V37_AUDIT',a.name,seed,arm,'food',round(case['food_41_48'],4),
    'new_food',round(case['newcomer_41_48'],4),
    'old_food',round(case['resident_41_48'],4),
    'surplus',round(case['surplus_retained'],3),flush=True)
 path=ROOT/'results'/('v37_holdout_'+a.name+'.json')
 path.write_text(json.dumps(dict(name=a.name,spec=meta,
   seeds=SEEDS[:a.n_seeds],worlds_per_seed=a.worlds,
   source=spec['source'],cohort_indices=ids.cpu().tolist(),
   rows=records,training_never_updates_old_residents=True),indent=1),encoding='utf8')
 print('V37_AUDIT_DONE',a.name,len(records),'time',round(time.perf_counter()-t0,1),flush=True)
if __name__=='__main__':main()
