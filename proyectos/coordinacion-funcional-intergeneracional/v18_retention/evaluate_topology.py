"""Frozen external-network stress test for V18 trained policies.

Training network: ring/degree8 only. Evaluation varies social graph type and
degree, preserving own-food rewards and exactly the same initial world seeds.
A reachability cache from the legacy ring graph is invalidated per world.
"""
from __future__ import annotations
import json,argparse,time,numpy as np,torch
from dataclasses import replace
from pathlib import Path
from v12 import Config,World
from evaluate_v18 import load_model
ROOT=Path(__file__).resolve().parent
TASKS=[(50,4,'trap'),(80,12,'trap'),(80,30,'random'),(72,8,'random')]
GRAPHS=[(t,d) for t in ('ring','rewired') for d in (4,8,16)]
SEEDS=(450001,450007,450011)
def one(actor,c,seed):
    if hasattr(actor,'_cached_reach'):actor._cached_reach=None
    torch.manual_seed(seed+811)
    w=World(c,seed);actor.reset()
    exact_frames=0;ever=torch.zeros(c.batch,dtype=torch.bool,device=c.device)
    with torch.no_grad():
        for _ in range(c.horizon):
            actions,_,_=actor.act(w)
            w.advance(actions)
            counts=w.counts.sort(1,descending=True).values
            active=(w.counts>0).sum(1)
            exact=(active==c.k)&(counts[:,0]-counts[:,c.k-1]<=1)
            exact_frames+=int(exact.sum())
            ever|=exact
    s=w.counts.sort(1,descending=True).values
    active=(w.counts>0).sum(1)
    exact=(active==c.k)&(s[:,0]-s[:,c.k-1]<=1)
    d=1-s[:,:c.k].clamp(max=c.n/c.k).sum(1)/c.n
    return dict(food=float(w.food.mean()),exact=int(exact.sum()),
        ever=int(ever.sum()),exact_frames=exact_frames,worlds=c.batch,
        active=float(active.float().mean()),D=float(d.mean()))
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--models',default='teacher_v17_DISTILL_LATTICE_R8_s3111_fix,teacher_v17_DISTILL_LATTICE_R8_s4111_fix,v18_BC3_s6111,v18_BC3_s7111,v18_ON_ALL_3_s6111,v18_ON_ALL_3_s7111')
    p.add_argument('--worlds',type=int,default=32)
    p.add_argument('--steps',type=int,default=40)
    p.add_argument('--device',choices=['cpu','cuda'],default='cpu')
    a=p.parse_args()
    torch.set_num_threads(3)
    rows=[]
    for name in a.models.split(','):
        x=load_model(name,a.device)
        if not x:
            print('SKIP_NOT_READY',name,flush=True);continue
        actor,u,seed_weights=x
        for topology,degree in GRAPHS:
            for m,k,init in TASKS:
                c=Config(n=120,m=m,k=k,topology=topology,degree=degree,
                     init=init,batch=a.worlds,horizon=a.steps,device=a.device)
                parts=[one(actor,c,seed) for seed in SEEDS]
                record=dict(model=name,update=u,topology=topology,degree=degree,
                      m=m,k=k,init=init,food=float(np.mean([x['food'] for x in parts])),
                      D=float(np.mean([x['D'] for x in parts])),
                      active=float(np.mean([x['active'] for x in parts])),
                      exact=sum(x['exact'] for x in parts),ever_exact=sum(x['ever'] for x in parts),
                      worlds=sum(x['worlds'] for x in parts),
                      by_seed=parts)
                rows.append(record)
                print('TOPO',name,topology,degree,'M',m,'k',k,
                      'food',round(record['food'],4),'exact',record['exact'],
                      '/',record['worlds'],flush=True)
        (ROOT/'results'/'v18_topology_partial.json').write_text(
          json.dumps(dict(rows=rows,seeds=SEEDS),indent=1),encoding='utf8')
    final=dict(rows=rows,seeds=SEEDS,conditions=len(rows),worlds=sum(z['worlds'] for z in rows),
           trained_topology='ring',trained_degree=8,
           cache_reset_per_world=True)
    (ROOT/'results'/'v18_topology.json').write_text(json.dumps(final,indent=1),encoding='utf8')
    print('V18_TOPOLOGY_DONE',len(rows),'conditions',final['worlds'],'societies',flush=True)
if __name__=='__main__':main()
