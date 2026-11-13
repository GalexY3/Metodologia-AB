"""V38: frozen factorial cohort competence, nested 0–30 trained newcomers.

No new policy training or changes to resident policies. Each environment
seed draws one independent permutation of 30 newborn identities, with
nested chosen subsets across six training-quota levels.
"""
from __future__ import annotations
import argparse,copy,json,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C
from audit_targeted import SEEDS
from v37_audit import freeze_cohort,simulate
ROOT=Path(__file__).resolve().parent
LEVELS=(0,6,12,18,24,30)

@torch.no_grad()
def mixing(fresh,trained,chosen):
 new=[]
 for initial,learned in zip(fresh,trained):
  mixed=copy.deepcopy(initial)
  current=dict(mixed.named_parameters())
  future=dict(learned.named_parameters())
  for key,param in current.items():
   param[chosen]=future[key][chosen]
  mixed.eval().requires_grad_(False)
  new.append(mixed)
 return tuple(new)

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--worlds',type=int,default=16)
 p.add_argument('--n-seeds',type=int,default=6)
 p.add_argument('--device',choices=('cuda','cpu'),default='cuda')
 a=p.parse_args()
 torch.set_num_threads(2)
 assert 1<=a.n_seeds<=len(SEEDS)
 metadata=json.loads((ROOT/'runs'/a.name/'v37_spec.json').read_text('utf8'))
 oldg,oldr,fresh,trained,ids,source,spec=freeze_cohort(
  a.name,metadata['source'],a.device)
 assert len(ids)==30
 records=[];start=time.perf_counter()
 for seed in SEEDS[:a.n_seeds]:
  generator=torch.Generator(device='cpu')
  generator.manual_seed(seed*5+38037)
  order=ids.cpu()[torch.randperm(30,generator=generator)].to(a.device)
  def Cobj():
   return C(n=120,k=4,degree=6,topology='ring',batch=a.worlds,
      horizon=48,gamma=source['gamma'],cost=source['cost'],device=a.device)
  without=simulate(Cobj(),oldg,oldr,fresh,ids,seed,mode='none')
  data={}
  for trained_n in LEVELS:
   actors=mixing(fresh,trained,order[:trained_n])
   x=simulate(Cobj(),oldg,oldr,actors,ids,seed,mode='trained')
   assert abs(x['food_pre']-without['food_pre'])<1e-7
   x['mode']='mixed'
   x['trained_count']=trained_n
   x['trained_fraction']=trained_n/30
   x['excess_surplus_retained']=(x['food_41_48']-.2)/(without['food_41_48']-.2)
   x['permutation_seed']=seed*5+38037
   data[trained_n]=x
  # Endpoint invariants: same baseline, same snapshots and RNG as V37.
  stored=json.loads((ROOT/'results'/('v37_holdout_'+a.name+'.json')).read_text('utf8'))
  s0=next(q for q in stored['rows'] if q['seed']==seed and q['mode']=='fresh')
  s30=next(q for q in stored['rows'] if q['seed']==seed and q['mode']=='trained')
  assert abs(data[0]['food_41_48']-s0['food_41_48'])<1e-6
  assert abs(data[30]['food_41_48']-s30['food_41_48'])<1e-6
  left,right=data[0]['food_41_48'],data[30]['food_41_48']
  for trained_n in LEVELS:
   x=data[trained_n]
   q=trained_n/30
   x['synergy_food']=x['food_41_48']-((1-q)*left+q*right)
   records.append(x)
   print('V38',a.name,seed,'trained',trained_n,
     'food',round(x['food_41_48'],4),
     'new',round(x['newcomer_41_48'],4),
     'old',round(x['resident_41_48'],4),
     'synergy',round(x['synergy_food'],4),flush=True)
 output=ROOT/'results'/('v38_composition_'+a.name+'.json')
 output.write_text(json.dumps(dict(model=a.name,source=metadata['source'],
    seeds=SEEDS[:a.n_seeds],worlds_per_seed=a.worlds,
    trained_quota=LEVELS,per_environment_nested=True,
    cohort_indices=ids.cpu().tolist(),rows=records,
    no_policy_training_during_v38=True),indent=1),encoding='utf8')
 print('V38_DONE',a.name,len(records),'elapsed',round(time.perf_counter()-start,1),flush=True)
if __name__=='__main__':main()
