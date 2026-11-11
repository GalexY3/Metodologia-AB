"""V18 frozen, paired-world audit of neural coordination retention.

A retained teacher, a pure RL fine-tune, and BC-regularized RL fine-tunes are
evaluated on the SAME fresh seeds, with intervention on the message channel.
No training occurs here. Exact-at-end and ever-exact are distinguished.
"""
from __future__ import annotations
import os,sys,json,argparse,statistics,time
from dataclasses import replace
from pathlib import Path
import numpy as np,torch
ROOT=Path(__file__).resolve().parent
V17=ROOT.parent/'v17_regime_coalition'
V12=ROOT.parent/'v12_variable_mk'
sys.path.insert(0,str(V17))
sys.path.insert(0,str(V12))
from neural_dual_v2 import DualNet
from v12 import Config,World

CASES=[
 ('ood_M36_k3_trap',36,3,'trap'),('train_M50_k4_trap',50,4,'trap'),
 ('train_M50_k4_random',50,4,'random'),('ood_M40_k5_random',40,5,'random'),
 ('trained_M80_k6_trap',80,6,'trap'),('ood_M72_k8_trap',72,8,'trap'),
 ('ood_M72_k8_random',72,8,'random'),('trained_M80_k12_trap',80,12,'trap'),
 ('trained_M80_k20_random',80,20,'random'),
 ('trained_M80_k30_random',80,30,'random'),
 ('trained_M80_k40_trap',80,40,'trap'),
 ('trained_M80_k60_random',80,60,'random')
]
MODES=('normal','scrambled_senders','no_messages')
SEEDS=(2027011,2027013,2027017,2027019)

def load_model(name,device):
    if name.startswith('teacher_'):
        src=name.removeprefix('teacher_')
        folder=V17/'runs'/src
        conf=json.loads((folder/'teacher_spec.json').read_text('utf8'))
        ck=folder/'teacher_latest.pt'
        update='teacher_900'
        trainseed=conf.get('init_seed')
    else:
        folder=(ROOT if name.startswith(('v18_ON_','v18_OFF_')) else V17)/'runs'/name
        conf_rl=json.loads((folder/'spec.json').read_text('utf8'))
        source=V17/'runs'/conf_rl['source']
        conf=json.loads((source/'teacher_spec.json').read_text('utf8'))
        ck=folder/'latest.pt'
        update=conf_rl['updates']
        trainseed=conf['init_seed']
    if not ck.exists():return None
    actor=DualNet(120,conf['h'],conf['rounds'],conf['quorum'],
                  conf['features'],False,True).to(device)
    snap=torch.load(ck,map_location=device,weights_only=False)
    actor.load_state_dict(snap['model']);actor.eval()
    return actor,update,trainseed

def roll(actor,c,seed,mode):
    torch.manual_seed(seed+171)
    e=World(c,seed)
    actor.reset()
    ever=torch.zeros(c.batch,device=c.device,dtype=torch.bool)
    n_exact_frames=0
    first=np.full(c.batch,-1,dtype=int)
    max_food=torch.zeros(c.batch,device=c.device)
    with torch.no_grad():
        for t in range(c.horizon):
            jobs,_,_=actor.act(e,disable_messages=(mode=='no_messages'),
               alter_messages=(mode=='scrambled_senders'))
            e.advance(jobs)
            order=e.counts.sort(1,descending=True).values
            occupied=(e.counts>0).sum(1)
            exact=(occupied==c.k)&(order[:,0]-order[:,c.k-1]<=1)
            n_exact_frames+=int(exact.sum())
            first[(exact&~ever).cpu().numpy()]=t+1
            ever|=exact
            max_food=torch.maximum(max_food,e.food.mean(1))
        order=e.counts.sort(1,descending=True).values
        occupied=(e.counts>0).sum(1)
        final_exact=(occupied==c.k)&(order[:,0]-order[:,c.k-1]<=1)
        D=1-order[:,:c.k].clamp(max=c.n/c.k).sum(1)/c.n
    return dict(seed=seed,food=float(e.food.mean()),
      mean_D=float(D.float().mean()),occupied=float(occupied.float().mean()),
      exact=int(final_exact.sum()),ever_exact=int(ever.sum()),
      exact_agent_world_frames=n_exact_frames,
      mean_best_food=float(max_food.mean()),
      median_first_exact=float(np.median(first[first>=0])) if np.any(first>=0) else None,
      worlds=c.batch,steps=c.horizon)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--models',default='teacher_v17_DISTILL_LATTICE_R8_s3111_fix,teacher_v17_DISTILL_LATTICE_R8_s4111_fix,v18_BC0_s6111,v18_BC08_s6111,v18_BC3_s6111,v18_BC0_s7111,v18_BC08_s7111,v18_BC3_s7111')
    p.add_argument('--worlds',type=int,default=32)
    p.add_argument('--steps',type=int,default=40)
    p.add_argument('--device',choices=('cpu','cuda'),default='cuda')
    a=p.parse_args()
    torch.set_num_threads(3)
    rows=[]
    dest=ROOT/'results'
    dest.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter()
    for name in a.models.split(','):
        material=load_model(name,a.device)
        if material is None:
            print('MODEL_MISSING',name,flush=True)
            continue
        actor,update,seed_of_weights=material
        for label,m,k,init in CASES:
            c=Config(n=120,m=m,k=k,degree=8,
              batch=a.worlds,horizon=a.steps,init=init,device=a.device)
            for mode in MODES:
                observations=[roll(actor,c,s,mode) for s in SEEDS]
                worlds=sum(x['worlds'] for x in observations)
                row=dict(model=name,update=update,train_seed=seed_of_weights,
                    case=label,m=m,k=k,initialization=init,
                    mode=mode,food=float(np.mean([x['food'] for x in observations])),
                    D=float(np.mean([x['mean_D'] for x in observations])),
                    occupied=float(np.mean([x['occupied'] for x in observations])),
                    exact=sum(x['exact'] for x in observations),
                    ever_exact=sum(x['ever_exact'] for x in observations),
                    exact_frames=sum(x['exact_agent_world_frames'] for x in observations),
                    worlds=worlds,total_world_frames=worlds*a.steps,
                    raw_by_seed=observations)
                rows.append(row)
                print('V18_FROZEN',name,label,mode,
                    'food',round(row['food'],4),'exact',row['exact'],
                    'ever',row['ever_exact'],'/',worlds,flush=True)
        (dest/'v18_frozen_partial.json').write_text(json.dumps(
            dict(steps=a.steps,seeds=SEEDS,rows=rows,
                 note='Frozen checkpoints, independent fresh world seeds.'),indent=1),
            encoding='utf8')
        print('MODEL_COMPLETE',name,len(rows),flush=True)
    final=dict(steps=a.steps,seeds=SEEDS,rows=rows,
       total_conditions=len(rows),society_runs=sum(x['worlds'] for x in rows),
       elapsed_seconds=time.perf_counter()-start,
       note='One observation is one interacting society; not independent individuals. Self-reward for all RL gradients. Teacher provides explicit programmed objectives.')
    (dest/'v18_frozen.json').write_text(json.dumps(final,indent=1),encoding='utf8')
    print('V18_EVAL_COMPLETE',len(rows),'conditions',
          final['society_runs'],'societies',flush=True)
if __name__=='__main__':main()
