"""V16: long-horizon private-neural-agent training with predeclared evaluations.

Experiments are CHRONOLOGICAL: all checkpoints and development outcomes are
retained (not just final/best). Evidence of grokking requires a delayed
generalization improvement *after* train performance has plateaued, verified
under multiple training seeds and a previously unseen evaluation holdout.
A fixed 120-agent village and multiple episodes are NOT biological generations.
"""
from __future__ import annotations
import sys,json,os,time,math,argparse,hashlib,random
from pathlib import Path
from dataclasses import asdict,replace
import numpy as np,torch
HERE=Path(__file__).resolve().parent
V15=HERE.parent/'v15_universal_k'
sys.path.insert(0,str(V15))
import v15
from v15 import envlib,OptionActor
DEVELOPMENT=[
 ('train_M24_k4',24,4),
 ('train_M80_k30',80,30),
 ('novel_k_M80_k12',80,12),
 ('novel_M12_k10',12,10),
 ('novel_M40_k12',40,12),
 ('novel_M72_k60',72,60)
]
SEEDS=(230097,230101)
DEFAULT_PAIRS='24:2,24:3,24:4,24:6,24:10,24:15,24:20,80:2,80:4,80:6,80:10,80:15,80:20,80:30,80:40,80:60'
BROAD_PAIRS='12:2,12:3,12:4,12:6,12:10,24:2,24:3,24:4,24:6,24:10,24:15,24:20,24:24,40:2,40:3,40:4,40:6,40:10,40:15,40:20,40:24,40:30,40:40,80:2,80:3,80:4,80:6,80:10,80:15,80:20,80:24,80:30,80:40,80:60' # hold out all k=5,8,12
def parse():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--name',required=True)
 p.add_argument('--source',default='',help='V15 checkpoint name or empty for scratch')
 p.add_argument('--end-update',type=int,default=12000)
 p.add_argument('--train-seed',type=int,default=3111)
 p.add_argument('--n',type=int,default=120)
 p.add_argument('--hidden',type=int,default=24)
 p.add_argument('--no-recurrence',action='store_true')
 p.add_argument('--degree',type=int,default=8)
 p.add_argument('--topology',choices=('ring','rewired'),default='ring')
 p.add_argument('--init',choices=('random','trap','mix'),default='random')
 p.add_argument('--pairs',choices=('original','broad'),default='original')
 p.add_argument('--batch',type=int,default=16)
 p.add_argument('--horizon',type=int,default=28)
 p.add_argument('--lr',type=float,default=.004)
 p.add_argument('--entropy',type=float,default=.005)
 p.add_argument('--gamma',type=float,default=.97)
 p.add_argument('--dev-every',type=int,default=500)
 p.add_argument('--save-every',type=int,default=500)
 p.add_argument('--dev-worlds',type=int,default=24)
 p.add_argument('--dev-steps',type=int,default=70)
 p.add_argument('--device',choices=('cpu','cuda'),default='cpu')
 return p.parse_args()
def exact_metrics(e):
 n=e.c.n;k=e.c.k
 cs=e.counts
 sorted_cs=cs.sort(1,descending=True).values
 occupied=(cs>0).sum(1)
 exact=((occupied==k)&(sorted_cs[:,0]-sorted_cs[:,k-1]<=1))
 deficit=1-sorted_cs[:,:k].clamp(max=n/k).sum(1)/n
 return {'food':float(e.food.mean()),'D':float(deficit.mean()),
        'exact':int(exact.sum()),'worlds':e.c.batch,
        'occupied':float(occupied.float().mean())}
def evaluate_current(actor,c,seed,adapt=True):
 env=envlib.World(c,seed)
 actor.reset()
 with torch.no_grad():
  for t in range(c.horizon):
   oldtenure=actor.tenure.clone() if actor.tenure is not None else None
   out,_,_=actor.act(env,greedy=(adapt and c.k/c.m>=.50))
   if adapt and c.k/c.m>=.70:
    out=torch.where(env.food>=.75,env.jobs,out)
    if oldtenure is not None:
     moving=out!=env.jobs
     actor.tenure=torch.where(moving,torch.zeros_like(oldtenure),oldtenure+1)
     actor.was_moving=moving.float()
   env.advance(out)
 return exact_metrics(env)
def evaluate_dev(actor,base,dev_worlds,dev_steps):
 rows={}
 for label,m,k in DEVELOPMENT:
  cc=replace(base,m=m,k=k,batch=dev_worlds,horizon=dev_steps,init='random')
  rs=[evaluate_current(actor,cc,s) for s in SEEDS]
  means={key:float(np.mean([r[key] for r in rs])) for key in ('food','D','occupied')}
  means['exact']=sum(r['exact'] for r in rs)
  means['worlds']=dev_worlds*len(SEEDS)
  rows[label]=means
 return rows
def run(args):
 torch.set_num_threads(min(4,os.cpu_count() or 2))
 pairs=[tuple(map(int,p.split(':'))) for p in (DEFAULT_PAIRS if args.pairs=='original' else BROAD_PAIRS).split(',')]
 pairs=[(m,k) for m,k in pairs if args.n%k==0 and m>=k]
 if not pairs:raise ValueError('No valid training pairs')
 where=HERE/'runs'/args.name
 where.mkdir(parents=True,exist_ok=True)
 contract=dict(source=args.source,end_update=None,train_seed=args.train_seed,
  n=args.n,hidden=args.hidden,recurrent=not args.no_recurrence,degree=args.degree,
  topology=args.topology,init=args.init,pairs=pairs,batch=args.batch,
  horizon=args.horizon,lr=args.lr,entropy=args.entropy,gamma=args.gamma,
  dev_every=args.dev_every,save_every=args.save_every,dev_worlds=args.dev_worlds,
  dev_steps=args.dev_steps,
  evaluation=DEVELOPMENT,dev_seeds=SEEDS)
 specfile=where/'spec.json'
 if specfile.exists():
  earlier=json.loads(specfile.read_text('utf8'))
  if earlier!=contract:raise ValueError('Incompatible resume; do not mix different treatments.')
 envlib.write_json(specfile,contract)
 torch.manual_seed(args.train_seed)
 actor=OptionActor(args.n,args.hidden,recurrent=not args.no_recurrence).to(args.device)
 opt=torch.optim.Adam(actor.parameters(),lr=args.lr)
 start=0
 if (where/'latest.pt').exists():
  ck=torch.load(where/'latest.pt',weights_only=False,map_location=args.device)
  actor.load_state_dict(ck['model']);opt.load_state_dict(ck['optimizer'])
  start=int(ck['update'])
 elif args.source:
  src=V15/'runs'/args.source/'latest.pt'
  ck=torch.load(src,weights_only=False,map_location=args.device)
  actor.load_state_dict(ck['model'])
  opt.load_state_dict(ck['optimizer'])
  start=int(ck['update'])
  envlib.write_json(where/'source_record.json',dict(
     source=str(src),source_update=start,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
 for group in opt.param_groups:group['lr']=args.lr
 print('LONG_BEGIN',args.name,'FROM',start,'UNTIL',args.end_update,
       'params_per_agent',sum(p.numel() for p in actor.parameters())//args.n,
       'train_pairs',len(pairs),'device',args.device,flush=True)
 base=envlib.Config(n=args.n,m=pairs[0][0],k=pairs[0][1],
  degree=args.degree,topology=args.topology,init='random',
  batch=args.batch,horizon=args.horizon,device=args.device,
  lr=args.lr,gamma=args.gamma,entropy=args.entropy,public=False,alpha=0.,
  communication=False,blind=False,seed=args.train_seed)
 def save(step):
  checkpoint={'model':actor.state_dict(),'optimizer':opt.state_dict(),'update':step}
  tmp=where/'latest.temp'
  torch.save(checkpoint,tmp)
  os.replace(tmp,where/'latest.pt')
  # independent snapshots allow transition analysis across checkpoints
  if step%max(args.save_every,1000)==0 or step==args.end_update:
   torch.save(checkpoint,where/f'checkpoint_{step:07d}.pt')
 t0=time.perf_counter()
 def measurement(step,train_result=None):
  z=evaluate_dev(actor,base,args.dev_worlds,args.dev_steps)
  row=dict(update=step,elapsed_s=time.perf_counter()-t0,
           train_result=train_result,results=z)
  with (where/'history.jsonl').open('a',encoding='utf8') as fh:
   fh.write(json.dumps(row,ensure_ascii=False)+'\n')
  envlib.write_json(where/'latest_metrics.json',row)
  print('LONG_METRIC',args.name,'u',step,
    'known',round(z['train_M24_k4']['food'],4),
    'high',round(z['train_M80_k30']['food'],4),
    'newK12',round(z['novel_k_M80_k12']['food'],4),
    'novelM12_k10',round(z['novel_M12_k10']['food'],4),
    'novelM40_k12',round(z['novel_M40_k12']['food'],4),
    'novelM72_k60',round(z['novel_M72_k60']['food'],4),
    'exact',sum(x['exact'] for x in z.values()),
    flush=True)
 if start==0 or (not (where/'history.jsonl').exists()):
  measurement(start,None)
 for u in range(start+1,args.end_update+1):
  if u%args.dev_every==1 and (where/'STOP').exists():
   save(u-1)
   envlib.write_json(where/'status.json',dict(state='stopped',update=u-1))
   return
  m,k=pairs[(u-1)%len(pairs)]
  init='trap' if args.init=='mix' and u%4==0 else ('random' if args.init=='mix' else args.init)
  c=replace(base,m=m,k=k,init=init)
  z=envlib.train_step(actor,opt,c,args.train_seed+u*977)
  if u%args.dev_every==0 or u==args.end_update:
   measurement(u,z)
   envlib.write_json(where/'status.json',dict(state='running',
      update=u,walltime_s=time.perf_counter()-t0))
  if u%args.save_every==0 or u==args.end_update:
   save(u)
 envlib.write_json(where/'status.json',dict(state='completed',update=args.end_update,
    elapsed_s=time.perf_counter()-t0))
 print('LONG_DONE',args.name,start,args.end_update,flush=True)
if __name__=='__main__':run(parse())
