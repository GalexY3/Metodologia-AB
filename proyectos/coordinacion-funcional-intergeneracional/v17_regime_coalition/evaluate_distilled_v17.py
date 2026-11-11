"""Frozen OOD audit of behavior-cloned independent neural actors.

Teacher targets were individual-state contingent but researcher provided.
All weights frozen here. Benchmarks include tasks never used in distillation.
"""
from __future__ import annotations
import json,torch,numpy as np,argparse
from pathlib import Path
from v12 import Config
from neural_dual_v2 import DualNet
from evaluate_neural_v17 import run_once
HERE=Path(__file__).resolve().parent
CASES=((36,3,'trap'),(36,3,'random'),(48,6,'trap'),
       (50,4,'trap'),(50,4,'random'),(72,8,'trap'),(72,8,'random'),
       (80,12,'trap'),(80,12,'random'),(80,20,'trap'),
       (80,40,'random'),(80,40,'trap'))
SEEDS=(992001,992003,992007,992009)
MODES=('normal','shuffled','removed')
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--names',default='v17_DISTILL_LATTICE_R8_s3111_fix,v17_DISTILL_LATTICE_R8_s4111_fix,v17_DISTILL_RAW_R8_s3111_fix,v17_DISTILL_LATTICE_R16_s3111_fix,v17_DISTILL_FINETUNE_R8_s3111_fix')
 ap.add_argument('--worlds',type=int,default=48)
 ap.add_argument('--steps',type=int,default=30)
 ap.add_argument('--device',default='cuda')
 args=ap.parse_args()
 torch.set_num_threads(4)
 results=[]
 for name in args.names.split(','):
  folder=HERE/'runs'/name
  specfile=folder/'teacher_spec.json'
  if not specfile.exists():
   print('SKIP_NO_CONFIG',name,flush=True);continue
  spec=json.loads(specfile.read_text('utf8'))
  stages=[('teacher',folder/'teacher_latest.pt')]
  if (folder/'rl_latest.pt').exists():
   stages.append(('after_rl',folder/'rl_latest.pt'))
  for stage,path in stages:
   if not path.exists():
    print('SKIP_MISSING_CHECKPOINT',name,stage,flush=True);continue
   actor=DualNet(120,spec['h'],spec['rounds'],spec['quorum'],
        spec['features'],False,True).to(args.device)
   ck=torch.load(path,map_location=args.device,weights_only=False)
   actor.load_state_dict(ck['model']);actor.eval()
   for m,k,init in CASES:
    c=Config(n=120,m=m,k=k,degree=8,batch=args.worlds,
      horizon=args.steps,init=init,device=args.device)
    for mode in MODES:
     z=[run_once(actor,c,seed,mode) for seed in SEEDS]
     row=dict(model=name,stage=stage,update=ck['update'],
       m=m,k=k,init=init,mode=mode,
       food=float(np.mean([v['food'] for v in z])),
       D=float(np.mean([v['D'] for v in z])),
       occupied=float(np.mean([v['occupied'] for v in z])),
       exact=sum(v['exact'] for v in z),
       worlds=sum(v['worlds'] for v in z),
       by_seed=z,heldout_k=(k in (3,6,8,20,40)))
     results.append(row)
     print('DISTILLED_FROZEN',name,stage,m,k,init,mode,
       'food',round(row['food'],4),'exact',row['exact'],
       '/',row['worlds'],flush=True)
   print('DISTILLED_MODEL_COMPLETE',name,stage,len(results),flush=True)
 out=HERE/'results'/'distilled_frozen_v17.json'
 out.write_text(json.dumps(dict(seeds=SEEDS,steps=args.steps,
    worlds_per_seed=args.worlds,rows=results,
    caveat='Models trained by explicit teacher labels, not independent discovery of coordination.'),indent=1),encoding='utf8')
 print('DISTILLED_FROZEN_DONE',len(results),
   'conditions',sum(z['worlds'] for z in results),'societies',flush=True)
if __name__=='__main__':main()
