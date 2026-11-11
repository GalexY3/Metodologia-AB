"""Frozen k generalization at N/k noninteger, with near-equal integer quotas.

The original V12 validation rejected n%k!=0 even though payoff is continuous.
We relax ONLY that validation for the stress test, and measure quota gap against
the feasible integer-balanced target (floor/ceil N/k) rather than impossible D=0.
No training occurs here.
"""
import sys,json,argparse,math,statistics
from pathlib import Path
from dataclasses import replace
import torch
import train_k
base=train_k.old
HERE=Path(__file__).resolve().parent

def allow_fraction(c):
    if not (2<=c.k<=c.m<=80):raise ValueError('invalid k/M')
    if c.n<12 or c.n%2:raise ValueError('N must be even')
    if not 1<=c.degree<c.n:raise ValueError('degree')
    if c.init not in ('random','trap'):raise ValueError('init')
    if not 0<=c.alpha<1:raise ValueError('alpha')
base.validate=allow_fraction

def simulate(model,c,seed,horizon=80,baseline='learned'):
    env=base.World(c,seed)
    if model:model.reset()
    with torch.no_grad():
        for _ in range(horizon):
            if baseline=='learned':
                jobs=model.act(env)[0]
            elif baseline=='random':
                jobs=torch.randint(c.m,(c.batch,c.n),device=c.device)
            elif baseline=='imitate':
                idx=torch.randint(c.degree,(c.batch,c.n,1),device=c.device)
                nbr=env.adj[None].expand(c.batch,-1,-1).gather(2,idx).squeeze(2)
                jobs=env.jobs.gather(1,nbr)
            else:raise ValueError(baseline)
            env.advance(jobs)
    q=c.n/c.k
    counts=env.counts.detach().cpu()
    sorted_count=counts.sort(dim=1).values[:,::-1] if False else counts.sort(dim=1,descending=True).values
    exact=(sorted_count[:,c.k:]==0).all(dim=1)&(sorted_count[:,:c.k].max(1).values-
         sorted_count[:,:c.k].min(1).values<=1)
    nonempty=(counts>0).sum(dim=1)
    balanced_sizes=[c.n//c.k]*c.k
    for j in range(c.n%c.k):balanced_sizes[j]+=1
    optimal=sum(s*min(s/q,q/s) for s in balanced_sizes)/c.n
    return dict(food=float(env.food.mean()),best_possible_balanced=optimal,
        ratio_vs_balanced=float(env.food.mean())/optimal,
        exact_integer_balanced=int(exact.sum()),
        worlds=c.batch,active_professions=float(nonempty.float().mean()),
        overrepresented=float((sorted_count[:,0]>q*2).float().mean()))

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--name',required=True)
    a.add_argument('--device',default='cpu',choices=['cpu','cuda'])
    a.add_argument('--batch',type=int,default=48)
    a.add_argument('--steps',type=int,default=80)
    args=a.parse_args()
    folder=HERE/'runs'/args.name
    spec=json.loads((folder/'config.json').read_text('utf8'))
    meta=json.loads((folder/'V14_MODEL_SPEC.json').read_text('utf8'))
    train_k.configure(meta['knows_requested_k'])
    cfg=base.Config(**{**spec['config'],'device':args.device})
    actor=train_k.Actor(cfg.n).to(args.device)
    weights=torch.load(folder/'latest.pt',map_location=args.device,weights_only=False)
    actor.load_state_dict(weights['model']);actor.eval()
    tests=[7,9,11,13,14,16,17,19,21,22,23,25,27,29]
    allrows=[]
    for k in tests:
        world=replace(cfg,m=80,k=k,batch=args.batch,horizon=args.steps)
        for mode in ('learned','random','imitate'):
            rows=[simulate(actor if mode=='learned' else None,world,seed,
                args.steps,baseline=mode) for seed in (981013,981029,981041)]
            z=dict(k=k,m=80,mode=mode,
                food=statistics.mean(x['food'] for x in rows),
                ratio=statistics.mean(x['ratio_vs_balanced'] for x in rows),
                ideal=statistics.mean(x['best_possible_balanced'] for x in rows),
                exact=sum(x['exact_integer_balanced'] for x in rows),
                worlds=sum(x['worlds'] for x in rows),
                occupied=statistics.mean(x['active_professions'] for x in rows),
                subruns=rows)
            allrows.append(z)
            print('NONINT',args.name,'k',k,'mode',mode,'food',
                  round(z['food'],4),'ideal',round(z['ideal'],4),
                  'integerExact',z['exact'],'/'+str(z['worlds']),flush=True)
    base.write_json(HERE/'evaluations'/(args.name+'_NONINTEGER_K.json'),
         dict(model=args.name,training_ks=sorted(set(int(k) for m,k in spec['tasks'])),
         note='Neither the actor nor the objective uses quota rounding; only exact assessment handles integer feasibility.',
         tests=allrows))
    print('NONINTEGER_DONE',args.name)
if __name__=='__main__':
    torch.set_num_threads(4);main()
