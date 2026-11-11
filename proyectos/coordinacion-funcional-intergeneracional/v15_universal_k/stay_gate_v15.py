"""Selective individual-food-based mobility gate over frozen neural proposals.

Development search only: select a fixed threshold on enumerated development
pairs, then evaluate it on new, never inspected M=16/32/48/72.
The gate uses only the individual's own food and public k/M. No global counts.
"""
from pathlib import Path
from dataclasses import replace
import argparse,json,numpy as np,torch,math
import v15
from evaluate_v15 import baseline_analytic
HERE=Path(__file__).resolve().parent
DEV=((12,8),(12,10),(12,12),(24,15),(24,20),(24,24),
     (40,30),(40,40),(60,40),(60,60),(80,60))
HOLD=((16,8),(16,10),(16,12),(16,15),(16,16),
      (32,20),(32,24),(32,30),(48,30),(48,40),
      (72,40),(72,60))
def load(name,device):
    root=HERE/'runs'/name
    spec=json.loads((root/'spec.json').read_text('utf8'))
    arg=spec['args']
    actor=v15.OptionActor(arg['n'],arg['h'],
         recurrent=not arg['no_recurrence']).to(device)
    ck=torch.load(root/'latest.pt',map_location=device,weights_only=False)
    actor.load_state_dict(ck['model'])
    actor.eval()
    return actor,arg,ck['update']
def trial(model,conf,seed,cutoff,mode='gated'):
    e=v15.envlib.World(conf,seed)
    if model is not None:model.reset()
    with torch.no_grad():
        for t in range(conf.horizon):
            if mode=='random':
                new=torch.randint(conf.m,e.jobs.shape,device=conf.device)
            else:
                oldtenure=model.tenure.clone() if model.tenure is not None else None
                proposal,_,_=model.act(e,greedy=(conf.k/conf.m>=.5))
                if cutoff is None or conf.k/conf.m<.7:
                    new=proposal
                else:
                    keep=e.food>=cutoff
                    new=torch.where(keep,e.jobs,proposal)
                    # Actor internal tenure must reflect actually accepted,
                    # rather than vetoed, moves.
                    if oldtenure is not None:
                        moving=(new!=e.jobs)
                        model.tenure=torch.where(moving,torch.zeros_like(oldtenure),
                               oldtenure+1)
                        model.was_moving=moving.float()
            e.advance(new)
    food=e.food.mean(1).cpu().numpy()
    counts=e.counts.cpu().numpy()
    alive=(counts>0).sum(1)
    exact=(alive==conf.k)&(counts.max(1)-np.where(counts>0,counts,9999).min(1)<=1)
    return food,alive,exact
def evaluate(model,args,cutoff,pairs,seeds,batch=64,steps=80,device='cuda'):
    rows=[]
    for m,k in pairs:
        cfg=v15.envlib.Config(n=args['n'],m=m,k=k,degree=args['degree'],
            batch=batch,horizon=steps,device=device)
        neural=[]
        rnd=[]
        for sd in seeds:
            a,_,_=trial(model,cfg,sd,cutoff)
            b,_,_=trial(None,cfg,sd,None,mode='random')
            neural.extend(a.tolist());rnd.extend(b.tolist())
        delta=np.array(neural)-np.array(rnd)
        rec=dict(m=m,k=k,gate=cutoff,ratio=k/m,food=float(np.mean(neural)),
             random=float(np.mean(rnd)),delta=float(delta.mean()),
             lower95=float(delta.mean()-1.96*delta.std(ddof=1)/np.sqrt(len(delta))),
             worlds=len(delta),win_rate=float(np.mean(delta>0)))
        rows.append(rec)
        print('GATE',m,k,'cutoff',cutoff,'food',round(rec['food'],4),
              'random',round(rec['random'],4),'delta',round(rec['delta'],4),
              flush=True)
    return rows
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--name',required=True)
    p.add_argument('--phase',choices=['dev','holdout'],default='dev')
    p.add_argument('--device',default='cuda')
    p.add_argument('--worlds',type=int,default=48)
    p.add_argument('--steps',type=int,default=90)
    p.add_argument('--cutoff',type=float,default=None)
    args=p.parse_args()
    torch.set_num_threads(4)
    model,ar,u=load(args.name,args.device)
    if args.phase=='dev':
        thresholds=(None,.75,.80,.85,.90,.95,.99)
        trials=[]
        for t in thresholds:
            rows=evaluate(model,ar,t,DEV,[291001,291003],args.worlds,args.steps,args.device)
            summary=dict(cutoff=t,rows=rows,wins=sum(x['delta']>0 for x in rows),
                worst_margin=min(x['delta'] for x in rows),
                average_margin=float(np.mean([x['delta'] for x in rows])))
            trials.append(summary)
            print('DEV_GATE_SUMMARY',t,summary['wins'],'/',len(rows),
              'minimum',round(summary['worst_margin'],5),flush=True)
        v15.envlib.write_json(HERE/'evaluations'/(args.name+'_GATE_DEV.json'),
            dict(model=args.name,updates=u,thresholds=trials,
                 note='Exploratory search. Do not report as sealed holdout.'))
    else:
        if args.cutoff is None:raise ValueError('holdout requires selected cutoff')
        rows=evaluate(model,ar,args.cutoff,HOLD,
             [292011,292013,292017,292019],args.worlds,args.steps,args.device)
        v15.envlib.write_json(HERE/'evaluations'/(args.name+'_GATE_HOLDOUT.json'),
            dict(model=args.name,updates=u,cutoff=args.cutoff,holdout_M=[16,32,48,72],
                 rows=rows,selected_from_DEV=True,
                 summary=dict(wins=sum(x['delta']>0 for x in rows),
                              total=len(rows),worst_margin=min(x['delta'] for x in rows))))
        print('GATE_HOLDOUT_SUMMARY',sum(x['delta']>0 for x in rows),'/',len(rows))
if __name__=='__main__':main()
