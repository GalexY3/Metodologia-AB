"""Held-out-world exploratory evaluation of V13 network treatments & MHU.

Freeze weights; evaluate social graph seen at train and unseen graph instance.
For each world compute mark-spectrum normalized against a fixed-count
random-assignment analytic null, so role population size cannot fake MHU.
"""
from __future__ import annotations
import argparse,json,sys,math
from pathlib import Path
from dataclasses import replace
import numpy as np,torch
import network_v13 as nw
from network_v13 import base,HERE
from mhu_v13 import aggregation,partial_spectrum,reference_balanced,window_variance_ratio

def frozen_run(actor,cfg,seed,graph_seed,baseline="learned",
              init="random",horizon=60,batch=64,greedy=False,
              record=False):
    nw.TOPO_SEED=graph_seed
    c=replace(cfg,batch=batch,horizon=horizon,init="random")
    e=base.World(c,seed)
    if init!="random":
        xy=nw.coordinates(c.n,c.topology,graph_seed)
        labels=[]
        for b in range(batch):
            t=reference_balanced(c.n,c.m,c.k,xy,seed+b*23,
                kind=("low_spectral" if init=="mhu_constructed" else "random"),
                swaps=1800)
            labels.append(t)
        e.jobs=torch.as_tensor(np.stack(labels),device=c.device)
        e.food,e.counts=base.food(e.jobs,c.m,c.k)
        e.lastfood=e.food.clone()
        e.global_now=e.food.mean(1)
        e.global_before=e.global_now.clone()
    if actor is not None:actor.reset()
    spatial=nw.coordinates(c.n,c.topology,graph_seed)
    checkpoints=(0,5,15,30,horizon)
    results={}
    trajectories=[]
    def check(t):
        jobs=e.jobs.detach().cpu().numpy()
        foods=e.food.detach().cpu().numpy()
        e_counts=e.counts.detach().cpu().numpy()
        n=c.n;q=n/c.k
        d=1-np.minimum(np.sort(e_counts,axis=1)[:,-c.k:],q).sum(1)/n
        s=aggregation(jobs,spatial)
        windows=[window_variance_ratio(row,spatial)['mean_ratio'] for row in jobs] if t in (0,horizon) else []
        metrics=dict(t=t,food=float(foods.mean()),d=float(d.mean()),
          exact=int((d<1e-8).sum()),occupied=float((e_counts>0).sum(1).mean()),
          alive_spectrum=s,
          finite_window_ratio=float(np.mean([v for v in windows if v is not None])) if any(v is not None for v in windows) else None)
        results[str(t)]=metrics
        if record:
            trajectories.append(dict(t=t,jobs=jobs[0].tolist(),
               occupied=e_counts[0].astype(int).tolist(),food=float(foods[0].mean()),
               mhu=partial_spectrum(jobs[0],spatial)))
    with torch.no_grad():
        check(0)
        for t in range(1,horizon+1):
            if baseline=="learned":
                nxt,_,_=actor.act(e,greedy=greedy)
            elif baseline=="random":
                nxt=torch.randint(c.m,(c.batch,c.n),device=c.device)
            elif baseline=="frozen":
                nxt=e.jobs
            elif baseline=="imitate":
                valid=e.adj>=0
                degrees=valid.sum(1)
                order=(torch.rand(c.batch,c.n,device=c.device)*degrees[None]).long()
                nbr=e.adj[None].expand(c.batch,-1,-1).gather(2,order[...,None]).squeeze(2)
                nxt=e.jobs.gather(1,nbr)
            else:raise ValueError(baseline)
            e.advance(nxt)
            if t in checkpoints:check(t)
    return dict(seeds=dict(world_seed=seed,graph_seed=graph_seed),
                baseline=baseline,init=init,greedy=greedy,checks=results,
                replay=trajectories)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--prefix',default='v13_N120_')
    p.add_argument('--name-ends',default='',help='filter suffix, e.g. _s4202')
    p.add_argument('--worlds',type=int,default=48)
    p.add_argument('--steps',type=int,default=60)
    p.add_argument('--seed',type=int,default=733001)
    p.add_argument('--no-positives',action='store_true')
    args=p.parse_args()
    torch.set_num_threads(3)
    result=[]
    for folder in sorted((HERE/'runs').glob(args.prefix+'*')):
        if args.name_ends and not folder.name.endswith(args.name_ends):continue
        if not (folder/'latest.pt').exists():continue
        cc=json.loads((folder/'config.json').read_text('utf8'))
        c=base.Config(**{**cc['config'],'device':'cpu'})
        ck=torch.load(folder/'latest.pt',map_location='cpu',weights_only=False)
        actor=base.IndividualAgent(c.n)
        actor.load_state_dict(ck['model'])
        actor.eval()
        info=json.loads((folder/'NETWORK.json').read_text('utf8'))
        cases=[('known_k2_m10',10,2),('known_k4_m20',20,4),
               ('unseen_k3_m30',30,3),('unseen_k5_m30',30,5),
               ('unseen_k6_m50',50,6)]
        experiments=[]
        for label,m,k in cases:
            if c.n%k:continue
            ec=replace(c,m=m,k=k)
            graph_seeds=[info['graph_seed']]
            if label=='unseen_k5_m30':graph_seeds+=[info['graph_seed']+221]
            for gs in graph_seeds:
                settings=[('learned','random',False)]
                if label in ('known_k2_m10','unseen_k5_m30'):
                    settings.extend([('imitate','random',False),
                                     ('random','random',False)])
                if not args.no_positives and label=='known_k4_m20' and gs==info['graph_seed']:
                    settings.extend([('frozen','balanced_random',False),
                                     ('frozen','mhu_constructed',False),
                                     ('learned','mhu_constructed',False)])
                for baseline,init,greedy in settings:
                    e1=frozen_run(actor if baseline=='learned' else None,ec,
                             seed=args.seed,graph_seed=gs,baseline=baseline,
                             init=init,horizon=args.steps,batch=args.worlds,
                             greedy=greedy,record=(baseline=='learned' and init=='random'))
                    e2=frozen_run(actor if baseline=='learned' else None,ec,
                             seed=args.seed+13,graph_seed=gs,baseline=baseline,
                             init=init,horizon=args.steps,batch=args.worlds,
                             greedy=greedy,record=False)
                    for res in (e1,e2):res['replay']=res.get('replay',[])[:]
                    meanfood=float(np.mean([x['checks'][str(args.steps)]['food'] for x in (e1,e2)]))
                    ratios=[x['checks'][str(args.steps)]['alive_spectrum']['mean_ratio'] for x in (e1,e2)]
                    ratio=float(np.mean([x for x in ratios if x is not None])) if any(x is not None for x in ratios) else None
                    rec=dict(task=label,m=m,k=k,topology=c.topology,degree=c.degree,
                      graph_seed=gs,baseline=baseline,init=init,n_worlds=args.worlds*2,
                      food=meanfood,low_spectral_ratio=ratio,
                      d=float(np.mean([x['checks'][str(args.steps)]['d'] for x in (e1,e2)])),
                      exact=sum(x['checks'][str(args.steps)]['exact'] for x in (e1,e2)),
                      by_seed=[e1,e2])
                    experiments.append(rec)
                    print('SCAN',folder.name,label,baseline,init,'graph',gs,
                          'food',round(rec['food'],3),'Snull_ratio',
                          round(ratio,3) if ratio is not None else 'NA',
                          'exact',rec['exact'],flush=True)
        result.append(dict(name=folder.name,update=ck['update'],network=info,
                           config=cc,experiments=experiments))
        base.write_json(HERE/'evaluations'/(folder.name+'_EVAL.json'),result[-1])
    base.write_json(HERE/'evaluations'/('SUMMARY_'+args.prefix+'_'+(args.name_ends or 'all')+'.json'),dict(
      definition='finite partial low-q occupation-mark spectrum divided by exact conditional shuffled-mark expected intensity',
      modes=[(1,0),(0,1),(1,1),(1,-1),(2,0),(0,2)],
      exploratory=True,seed=args.seed,worlds_per_seed=args.worlds,
      horizon=args.steps,models=[dict(name=x['name'],update=x['update'],
        network=x['network'],summary=[
          {k:v for k,v in t.items() if k!='by_seed'} for t in x['experiments']])
        for x in result]))
    print('V13_SCAN_COMPLETE',len(result),'trained networks',flush=True)
if __name__=='__main__':main()
