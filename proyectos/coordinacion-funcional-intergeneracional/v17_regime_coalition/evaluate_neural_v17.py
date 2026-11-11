"""Out-of-sample frozen neural actor vs intervention on communication channel.

No retraining. Each scenario repeated over four fresh seeds x 48 worlds.
Compare actual policy against no messages and shuffled sender identity; this
is a within-checkpoint robustness check, not proof of emergent cooperation.
"""
from pathlib import Path
from dataclasses import replace
import torch,numpy as np,json,sys,math,argparse
import neural_pledge,neural_dual,neural_dual_v2
from v12 import Config,World
HERE=Path(__file__).resolve().parent
CASES=((50,4,'trap'),(50,4,'random'),(80,12,'trap'),
      (80,12,'random'),(80,30,'random'),(72,8,'trap'),(72,8,'random'))
MODES=('normal','shuffled','removed')
SEEDS=(890211,890221,890231,890241)
def load(name,device):
 root=HERE/'runs'/name
 spec=json.loads((root/'spec.json').read_text('utf8'))
 if name.startswith('v17_PLEDGE'):
  cls=neural_pledge.PledgeActor
 elif '_V2_' in name:
  cls=neural_dual_v2.DualNet
 else:
  cls=neural_dual.DualNet
 # Teacher biased initializations are still represented by standard final weights.
 mod=cls(spec['n'],spec['h'],spec['rounds'],spec['quorum'],
         spec['features'],spec['scramble'],spec['gate']).to(device)
 weights=torch.load(root/'latest.pt',weights_only=False,map_location=device)
 mod.load_state_dict(weights['model'])
 mod.eval()
 return mod,spec,int(weights['update'])
def run_once(actor,c,seed,mode):
 e=World(c,seed)
 actor.reset()
 with torch.no_grad():
  for t in range(c.horizon):
   jobs,_,_=actor.act(e,disable_messages=(mode=='removed'),
                      alter_messages=(mode=='shuffled'))
   e.advance(jobs)
 counts=e.counts
 ord=counts.sort(1,descending=True).values
 occupied=(counts>0).sum(1)
 exact=(occupied==c.k)&(ord[:,0]-ord[:,c.k-1]<=1)
 deficit=1-ord[:,:c.k].clamp(max=c.n/c.k).sum(1)/c.n
 return dict(food=float(e.food.mean()),D=float(deficit.mean()),
       exact=int(exact.sum()),occupied=float(occupied.float().mean()),
       worlds=c.batch)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--names',default='v17_DUAL_LATTICE_R8_s3111,v17_DUAL_LOCAL_R8_s3111,v17_DUAL_NOQUORUM_R16_s3111,v17_PLEDGE_LATTICE_R8_s3111,v17_DUAL_V2_PRIOR_R8_s3111')
 ap.add_argument('--device',default='cuda')
 ap.add_argument('--worlds',type=int,default=48)
 ap.add_argument('--steps',type=int,default=30)
 args=ap.parse_args()
 torch.set_num_threads(4)
 rows=[]
 for name in args.names.split(','):
  ck=HERE/'runs'/name/'latest.pt'
  if not ck.exists():
   print('SKIP_MISSING',name,flush=True);continue
  actor,spec,update=load(name,args.device)
  for m,k,init in CASES:
   c=Config(n=spec['n'],m=m,k=k,degree=spec['degree'],
     topology=spec['topology'],batch=args.worlds,horizon=args.steps,
     init=init,device=args.device)
   for mode in MODES:
    z=[run_once(actor,c,seed,mode) for seed in SEEDS]
    row=dict(model=name,checkpoint=update,m=m,k=k,init=init,
     mode=mode,food=float(np.mean([v['food'] for v in z])),
     D=float(np.mean([v['D'] for v in z])),
     occupied=float(np.mean([v['occupied'] for v in z])),
     exact=sum(v['exact'] for v in z),
     worlds=sum(v['worlds'] for v in z),by_seed=z)
    rows.append(row)
    print('NEURAL_FROZEN',name,m,k,init,mode,
      'food',round(row['food'],4),'occupied',round(row['occupied'],2),
      'exact',row['exact'],'/',row['worlds'],flush=True)
 target=HERE/'results'/'neural_frozen_v17.json'
 target.write_text(json.dumps(dict(steps=args.steps,worlds_per_seed=args.worlds,
      seeds=SEEDS,rows=rows,
      note='All policies frozen. Quorum and messaging are predefined modules; no performance claim on learned cooperation.'),indent=1),encoding='utf8')
 print('NEURAL_FROZEN_DONE',len(rows),'conditions',sum(x['worlds'] for x in rows),'societies',flush=True)
if __name__=='__main__':main()
