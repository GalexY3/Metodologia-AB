"""V36: frozen all-person institution choice tests on degree-4 network.

Uses the V32 frozen auditor with the original 9 comparisons and appends
the pre-registered additional role-random baselines at 0.15 and 0.60.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C as OriginalC
import v32_frozen_audits as base
import v32_institution_choice as engine
ROOT=Path(__file__).resolve().parent

def graph4(*args,**kwargs):
 assert kwargs.get('degree',6)==6
 kwargs['degree']=4
 return OriginalC(*args,**kwargs)

@torch.no_grad()
def extra_random(name,worlds,steps,device):
 gift,role,mode,spec=base.load(name,device)
 filename=ROOT/'results'/('v32_holdout_'+name+'.json')
 dataset=json.loads(filename.read_text('utf8'))
 assert len(dataset['rows'])==27
 keys=('food','last_food','adoption','proposals_per_agent',
       'transfers_per_agent','matched_contracts_per_agent',
       'realized_coverage','useful_fraction','potential_coverage',
       'balanced','nonempty_professions','switches')
 for topology,init in (('ring','monolith'),('ring','random'),('rewired','monolith')):
  for rate in ('0.15','0.60'):
   vals=[]
   for seed in base.SEEDS:
    c=graph4(n=spec['n'],k=4,degree=6,topology=topology,
     batch=worlds,horizon=steps,cost=spec['cost'],
     gamma=spec['gamma'],device=device)
    torch.manual_seed(seed*41+202611)
    m,*_=engine.roll(c,gift,role,mode,seed,init=init,
      interval=spec['role_interval'],move_cost=spec['move_cost'],
      role_baseline='random_'+rate)
    vals.append(dict(seed=seed,**m))
   dataset['rows'].append(dict(model=name,topology=topology,
     init=init,condition='role_random_'+rate,
     worlds=worlds*len(base.SEEDS),
     **{key:float(np.mean([x[key] for x in vals])) for key in keys},
     by_seed=vals))
 assert len(dataset['rows'])==33
 filename.write_text(json.dumps(dataset,indent=1),encoding='utf8')
 print('V36_EXTRA_ROLE_BASELINES',name,'nrows',len(dataset['rows']),flush=True)

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--kind',choices=('holdout','causal'),required=True)
 p.add_argument('--worlds',type=int,default=12)
 p.add_argument('--steps',type=int,default=48)
 p.add_argument('--device',choices=('cuda','cpu'),default='cuda')
 a=p.parse_args()
 spec=json.loads((ROOT/'runs'/a.name/'v32_spec.json').read_text('utf8'))
 assert spec['v36_degree']==4
 base.C=graph4
 engine.C=graph4
 torch.set_num_threads(2)
 if a.kind=='holdout':
  base.heldout(a.name,a.worlds,a.steps,a.device)
  extra_random(a.name,a.worlds,a.steps,a.device)
 else:
  base.causal(a.name,a.worlds,a.steps,a.device)
if __name__=='__main__':main()
