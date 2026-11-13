"""V36 cross-degree fairness: evaluate 3 random-profession controls on V32.

Keeps V32 frozen results unmodified; creates a separate source-backed receipt.
"""
from __future__ import annotations
import json,torch,numpy as np
from pathlib import Path
from targeted_gifts import C
import v32_frozen_audits as base
import v32_institution_choice as engine
ROOT=Path(__file__).resolve().parent
NAMES=[f'v32_MODE{bias}_s{seed}'
   for bias in ('NEUTRAL','RARE') for seed in (3111,4111)]
@torch.no_grad()
def main():
 torch.set_num_threads(2)
 out=[]
 for name in NAMES:
  gift,role,mode,spec=base.load(name,'cuda')
  prev=json.loads((ROOT/'results'/('v32_holdout_'+name+'.json')).read_text('utf8'))
  def get(condition,topo='ring',init='monolith'):
   return next(x for x in prev['rows']
     if x['topology']==topo and x['init']==init and x['condition']==condition)
  records=[]
  for topo,init in (('ring','monolith'),('ring','random'),('rewired','monolith')):
   for rate in (.15,.60):
    vals=[]
    for seed in base.SEEDS:
     c=C(n=spec['n'],k=4,degree=6,topology=topo,batch=12,
       horizon=48,cost=spec['cost'],gamma=spec['gamma'],device='cuda')
     torch.manual_seed(seed*41+202611)
     metric,*_=engine.roll(c,gift,role,mode,seed,init=init,
         interval=spec['role_interval'],move_cost=spec['move_cost'],
         role_baseline='random_'+str(rate))
     vals.append(dict(seed=seed,**metric))
    records.append(dict(topology=topo,init=init,
      condition='role_random_'+str(rate),worlds=72,
      food=float(np.mean([x['food'] for x in vals])),
      by_seed=vals))
  best=max([get('role_random_035')['food']]+[
    x['food'] for x in records if x['topology']=='ring' and x['init']=='monolith'])
  learned=get('learned')['food']
  entry=dict(model=name,degree=6,food=learned,random035=get('role_random_035')['food'],
    best_random_015_035_060=best,advantage_over_best=learned-best,
    added_controls=records)
  out.append(entry)
  print('V36_REFERENCE',name,'food',round(learned,4),
    'random_best',round(best,4),
    'role_advantage',round(learned-best,4),flush=True)
 (ROOT/'results'/'v36_DEGREE6_REFERENCE_CONTROLS.json').write_text(
    json.dumps(dict(models=out,method='Frozen V32 controls at probabilities .15/.35/.60; .35 from original heldout, others newly evaluated. No new neural training.'),indent=1),encoding='utf8')
if __name__=='__main__':main()
