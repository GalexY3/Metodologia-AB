"""Post-training, exploratory (NOT sealed) cross-task/cross-M evaluations.

Freeze each trained agent's individual weights. Compare known k/M, untrained
k and larger profession sets M=30,50; also start from an unfair Nash trap.
The same code evaluates C0, C1, public-report and reward-0.1 treatments.
"""
import argparse,json,os
from pathlib import Path
from dataclasses import asdict,replace
import torch
from v12 import Config,IndividualAgent,evaluate,write_json,ROOT

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--prefix',default='v12_n60_')
 p.add_argument('--eval-batch',type=int,default=64)
 p.add_argument('--seeds',default='970011,970031')
 args=p.parse_args()
 torch.set_num_threads(3)
 seeds=list(map(int,args.seeds.split(',')))
 result=[]
 for folder in sorted((ROOT/'runs').glob(args.prefix+'*')):
  if not (folder/'latest.pt').exists():continue
  setup=json.loads((folder/'config.json').read_text(encoding='utf8'))
  saved=setup['config']
  cfg=Config(**{**saved,'device':'cpu'})
  model=IndividualAgent(cfg.n)
  checkpoint=torch.load(folder/'latest.pt',map_location='cpu',weights_only=False)
  model.load_state_dict(checkpoint['model'])
  model.eval()
  tasks=[('known_M10_k2',10,2,'random'),('known_M20_k4',20,4,'random'),
         ('unseen_M30_k3',30,3,'random'),('unseen_M30_k5',30,5,'random'),
         ('unseen_M50_k6',50,6,'random'),('unseen_M50_k10',50,10,'random'),
         ('NashTrap_M20_k2',20,2,'trap'),('NashTrap_M20_k4',20,4,'trap')]
  tests=[]
  for label,m,k,initial in tasks:
   if cfg.n%k:continue
   ec=replace(cfg,m=m,k=k,init=initial,horizon=60,batch=args.eval_batch)
   strategies=[('learned_stochastic',dict(greedy=False)),
               ('learned_greedy',dict(greedy=True))]
   if cfg.communication:
    strategies.extend([
      ('messages_blocked',dict(disable_messages=True)),
      ('messages_shuffled',dict(alter_messages=True))])
   if label in ('known_M10_k2','unseen_M30_k5','NashTrap_M20_k4'):
    strategies.extend([
      ('random',dict(baseline='random')),
      ('frozen',dict(baseline='frozen')),
      ('local_imitation',dict(baseline='imitate'))])
   for name,kw in strategies:
    byseed=[]
    for s in seeds:
     # Same seed for world initialization, stochastic sampling may not
     # remain paired when message channels are blocked/shuffled.
     x=evaluate(model if name not in ('random','frozen','local_imitation') else None,
           ec,seed=s,batch=args.eval_batch,horizon=60,**kw)
     byseed.append(x['final'])
    avgfood=sum(z['food'] for z in byseed)/len(byseed)
    avgd=sum(z['d'] for z in byseed)/len(byseed)
    exact=sum(z['exact'] for z in byseed)
    tests.append(dict(task=label,m=m,k=k,initial=initial,mode=name,
                  seeds=seeds,by_seed=byseed,mean_food=avgfood,
                  mean_d=avgd,exact=exact,total_worlds=args.eval_batch*len(seeds)))
    print(folder.name,label,name,'food',round(avgfood,4),
         'D',round(avgd,4),'exact',exact,flush=True)
  result.append(dict(name=folder.name,updates=checkpoint['update'],config=saved,tests=tests))
 write_json(ROOT/(args.prefix.rstrip('_')+'_TRANSFER.json'),dict(
    kind='POSTHOC_EXPLORATORY_EVALUATIONS_NOT_SEALED',
    procedure='frozen independent models on fresh world seeds',
    seeds=seeds,worlds_per_seed=args.eval_batch,horizon=60,
    models=result,
    caution='C1 ablations do not preserve identical action sampling streams when messaging changes.'))
 print('EVALUATION_DONE',len(result),'models',flush=True)
if __name__=='__main__':main()
