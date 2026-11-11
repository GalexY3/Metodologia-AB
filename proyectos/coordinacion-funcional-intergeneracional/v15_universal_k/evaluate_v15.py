"""Frozen, no-oracle, paired-world test vs random / V14 / imitation.

Primary benchmark: k dividing N, for which the exact balanced k-role
partition is (by design) a global food optimum. Each result is per k, not
just an average. Additional fractional-k tests are marked noncanonical.
"""
from pathlib import Path
from dataclasses import replace
import argparse,torch,numpy as np,json,math,statistics,sys
import v15
envlib=v15.envlib
HERE=Path(__file__).resolve().parent
CASES=[2,3,4,5,6,8,10,12,15,20,24,30,40,60]
AUX=[7,9,11,13,17,19,29,80]
def simulate(actor,c,seed,mode='neural',greedy=False):
    e=envlib.World(c,seed)
    if actor:actor.reset()
    init=e.jobs.detach().cpu().numpy()
    with torch.no_grad():
        for _ in range(c.horizon):
            if mode=='neural':
                target,_,_=actor.act(e,greedy=greedy)
            elif mode=='random':
                target=torch.randint(c.m,e.jobs.shape,device=c.device)
            elif mode=='frozen':
                target=e.jobs
            elif mode=='imitate':
                idx=torch.randint(c.degree,(c.batch,c.n,1),device=c.device)
                nbr=e.adj[None].expand(c.batch,-1,-1).gather(2,idx).squeeze(2)
                target=e.jobs.gather(1,nbr)
            elif mode=='random_hold':
                # Independent renewal 1/10 each turn, otherwise keep last role
                change=torch.rand(e.jobs.shape,device=c.device)<.1
                target=torch.where(change,torch.randint(c.m,e.jobs.shape,device=c.device),e.jobs)
            else:raise ValueError(mode)
            e.advance(target)
    counts=e.counts.detach().cpu().numpy().astype(int)
    own_food=e.food.mean(dim=1).detach().cpu().numpy()
    occ=(counts>0).sum(axis=1)
    sorted_counts=-np.sort(-counts,axis=1)
    exact=(occ==c.k)&(sorted_counts[:,0]-sorted_counts[:,c.k-1]<=1)
    q=c.n/c.k
    d=1-np.minimum(sorted_counts[:,:c.k],q).sum(1)/c.n
    return dict(food=[float(x) for x in own_food],
        exact=[int(x) for x in exact],
        occupied=[int(x) for x in occ],
        d=[float(x) for x in d],
        init_occupied=[int(x) for x in (np.eye(c.m,dtype=int)[init].sum(axis=1)>0).sum(axis=1)])

def baseline_analytic(n,m,k):
    # Binomial size of the selected agent's profession, with replacement:
    # 1 + Binomial(N-1, 1/M) workers; expectation independent of final time.
    p=1/m;q=n/k
    mass=(1-p)**(n-1)
    expected=0.
    for j in range(n):
        s=j+1
        expected+=mass*min(s/q,q/s)
        mass=mass*(n-1-j)/(j+1)*p/(1-p)
    return expected

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--name',required=True)
    p.add_argument('--worlds',type=int,default=64)
    p.add_argument('--steps',type=int,default=80)
    p.add_argument('--seeds',default='151001,151003,151007,151009')
    p.add_argument('--device',choices=['cpu','cuda'],default='cuda')
    p.add_argument('--aux',action='store_true')
    args=p.parse_args()
    torch.set_num_threads(4)
    folder=HERE/'runs'/args.name
    spec=json.loads((folder/'spec.json').read_text('utf8'))
    train_args=spec['args']
    cfg=envlib.Config(n=train_args['n'],m=80,k=2,
        degree=train_args['degree'],batch=args.worlds,
        horizon=args.steps,device=args.device)
    actor=v15.OptionActor(cfg.n,hidden=train_args['h'],
              recurrent=not train_args['no_recurrence']).to(args.device)
    st=torch.load(folder/'latest.pt',weights_only=False,map_location=args.device)
    actor.load_state_dict(st['model']);actor.eval()
    output=[]
    seeds=[int(x) for x in args.seeds.split(',')]
    cases=CASES+(AUX if args.aux else [])
    for m in (24,80):
        for k in cases:
            if k>m:continue
            c=replace(cfg,m=m,k=k)
            conditions={}
            for mode in ('neural','neural_greedy','random','imitate','random_hold'):
                per_seed=[]
                for seed in seeds:
                    sd=simulate(actor if mode.startswith('neural') else None,c,seed,
                       mode='neural' if mode.startswith('neural') else mode,
                       greedy=(mode=='neural_greedy'))
                    per_seed.append(dict(seed=seed,**sd))
                foods=np.array([z for s in per_seed for z in s['food']])
                exacts=np.array([z for s in per_seed for z in s['exact']])
                occupied=np.array([z for s in per_seed for z in s['occupied']])
                ds=np.array([z for s in per_seed for z in s['d']])
                conditions[mode]=dict(mean_food=float(foods.mean()),
                    sd_food=float(foods.std()),mean_occupied=float(occupied.mean()),
                    mean_d=float(ds.mean()),exact=int(exacts.sum()),
                    worlds=len(foods),by_seed=per_seed)
            baseline=conditions['random']['mean_food']
            neural=conditions['neural']['mean_food']
            result=dict(m=m,k=k,canonical=(c.n%k==0),
                    trained=(m,k) in spec['pairs'],
                    random_analytic=baseline_analytic(cfg.n,m,k),
                    advantage_over_random=neural-baseline,
                    conditions=conditions)
            output.append(result)
            print('RESULT',args.name,'M',m,'k',k,
                  'train',int(result['trained']),'learned',round(neural,4),
                  'greedy',round(conditions['neural_greedy']['mean_food'],4),
                  'random',round(baseline,4),'difference',round(neural-baseline,4),
                  'exact',conditions['neural']['exact'],'/',conditions['neural']['worlds'],
                  flush=True)
    outputfile=HERE/'evaluations'/(args.name+'_FROZEN.json')
    envlib.write_json(outputfile,dict(model=args.name,checkpoint=st['update'],
           seed_list=seeds,worlds_per_seed=args.worlds,horizon=args.steps,
           procedures=('neural','neural_greedy','random','imitate','random_hold'),
           interpretation='Only k|N is canonical optimum from exactly k evenly filled groups. Other k have noninteger target quotas.',
           results=output))
    print('EVALUATION_COMPLETE',args.name,len(output),'conditions',flush=True)
if __name__=='__main__':main()
