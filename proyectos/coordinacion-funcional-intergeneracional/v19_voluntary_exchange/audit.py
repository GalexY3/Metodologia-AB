"""V19 frozen independent evaluation with causal interventions and local baselines.

Exact grouping is evaluated against balanced quotas N/k although only k
professions are initially available: the number of candidate role labels is
supplied, not learned. All fresh world seeds are distinct from development.
"""
from __future__ import annotations
import argparse,os,time,json,torch,numpy as np,math
from pathlib import Path
from exchange import Config,IndependentActors,create_world,observe,advance,metrics
ROOT=Path(__file__).resolve().parent
HOLDOUT_SEEDS=(887001,887003,887009,887011)
TRAIN_K=(2,3,4,6)
UNKNOWN_K=(5,10,12)
ROLE_K=TRAIN_K+UNKNOWN_K
MODELS=('normal','shuffled_social','no_social','force_offer_one','force_offer_zero')
BASELINES=('random_half','random_full','random_none','local_rare_full','local_rare_soft_full','frozen_full')

def load_actor(name,device):
    path=ROOT/'runs'/name
    spec=json.loads((path/'config.json').read_text('utf8'))
    ck=torch.load(path/'latest.pt',map_location=device,weights_only=False)
    actor=IndependentActors(60,spec['hidden']).to(device)
    actor.load_state_dict(ck['actor'])
    actor.eval()
    return actor,spec,int(ck['update'])
def choose(c,w,actor,mode):
    if mode in MODELS:
        use_mode=('normal' if mode in ('normal','force_offer_one','force_offer_zero') else mode)
        forced=1. if mode=='force_offer_one' else 0. if mode=='force_offer_zero' else None
        jobs,gives,_,_=actor.act(c,w,mode=use_mode,force_offer=forced)
        return jobs,gives
    if mode not in BASELINES:raise ValueError(mode)
    if mode=='frozen_full':return w['roles'].clone(),torch.ones_like(w['offers'])
    if mode.startswith('random'):
        jobs=torch.randint(c.k,(c.batch,c.n),device=c.device)
        if mode=='random_half':gives=(torch.rand(c.batch,c.n,device=c.device)<.5).float()
        else:gives=torch.full_like(w['offers'],1. if mode=='random_full' else 0.)
        return jobs,gives
    count=observe(c,w)['counts']
    if mode=='local_rare_full':
        # Use random jitter only to break equally scarce roles.
        jitter=torch.rand_like(count)*1e-5
        jobs=(count+jitter).argmin(2)
    else:
        jobs=torch.distributions.Categorical(logits=-8*count).sample()
    return jobs,torch.ones_like(w['offers'])
def once(c,actor,seed,mode):
    torch.manual_seed(seed*53+13)
    w=create_world(c,seed)
    ever=torch.zeros(c.batch,device=c.device,dtype=torch.bool)
    first=torch.zeros(c.batch,device=c.device,dtype=torch.int32)-1
    exact_world_frames=0
    food_history=[]
    with torch.no_grad():
        for t in range(c.horizon):
            roles,offers=choose(c,w,actor,mode)
            advance(c,w,roles,offers)
            q=c.n//c.k
            cnt=torch.nn.functional.one_hot(w['roles'],c.k).sum(1)
            good=(cnt==q).all(1)
            first[(good&~ever)]=t+1
            ever|=good
            exact_world_frames+=int(good.sum())
            if t in (0,c.horizon//2-1,c.horizon-1):
                food_history.append(float(w['reward'].mean()))
        output=metrics(c,w)
    output.update(seed=seed,ever_exact=int(ever.sum()),
        exact_world_frames=exact_world_frames,
        median_first_exact=float(torch.median(first[first>=0].float()))
             if bool((first>=0).any()) else None,
        food_history=food_history)
    return output

def run(args):
    torch.set_num_threads(3)
    actor=None;spec=None;update=0
    if args.model!='baseline':
        actor,spec,update=load_actor(args.model,args.device)
    modes=BASELINES if args.model=='baseline' else tuple(args.modes.split(','))
    if args.model=='baseline':
        mutual=bool(args.mutual)
        social=True
    else:
        mutual=bool(spec['mutual'])
        social=bool(spec['social'])
    conditions=[]
    for k in ROLE_K:
        for top in ('ring','rewired'):
            for degree in args.degrees:
                for init in ('monolith','random'):
                    conditions.append((k,top,degree,init))
    t0=time.perf_counter()
    rows=[]
    for j,(k,top,degree,init) in enumerate(conditions):
        c=Config(n=60,k=k,topology=top,degree=degree,init=init,
           batch=args.worlds,horizon=args.steps,device=args.device,
           mutual=mutual,social=social)
        for mode in modes:
            z=[once(c,actor,seed+1001*j,mode) for seed in HOLDOUT_SEEDS]
            worlds=sum(v['worlds'] for v in z)
            row=dict(model=args.model,checkpoint=update,mode=mode,
                trained_mutual=mutual,trained_social=social,
                k=k,heldout_k=k in UNKNOWN_K,
                topology=top,degree=degree,init=init,
                worlds=worlds,food=float(np.mean([v['food'] for v in z])),
                offer=float(np.mean([v['offer'] for v in z])),
                full=float(np.mean([v['full'] for v in z])),
                coverage=float(np.mean([v['coverage'] for v in z])),
                mutual_edges=float(np.mean([v['mutual_edges'] for v in z])),
                groups=float(np.mean([v['groups'] for v in z])),
                imbalance=float(np.mean([v['imbalance'] for v in z])),
                exact=sum(v['exact'] for v in z),
                ever_exact=sum(v['ever_exact'] for v in z),
                exact_world_frames=sum(v['exact_world_frames'] for v in z),
                raw_by_seed=z)
            rows.append(row)
        if (j+1)%8==0 or j+1==len(conditions):
            sub=[r for r in rows if r['mode']==modes[0]]
            print('AUDIT_PROGRESS',args.model,j+1,'/',len(conditions),
              'mode',modes[0],
              'food',round(float(np.mean([v['food'] for v in sub])),4),
              'offers',round(float(np.mean([v['offer'] for v in sub])),4),
              'worlds',sum(x['worlds'] for x in rows),
              'seconds',round(time.perf_counter()-t0),flush=True)
            save(args,rows,True,t0)
    save(args,rows,False,t0)
    print('V19_HOLDOUT_DONE',args.model,len(rows),'rows',
        sum(x['worlds'] for x in rows),'worlds',
        'seconds',round(time.perf_counter()-t0),flush=True)
    for mode in modes:
      for label,kset in (('trained',TRAIN_K),('unseen',UNKNOWN_K)):
        z=[x for x in rows if x['mode']==mode and x['k'] in kset]
        print('AUDIT_AGG',args.model,mode,label,
          'food',round(float(np.mean([x['food'] for x in z])),4),
          'offer',round(float(np.mean([x['offer'] for x in z])),4),
          'coverage',round(float(np.mean([x['coverage'] for x in z])),4),
          'imbalance',round(float(np.mean([x['imbalance'] for x in z])),4),
          'exact',sum(x['exact'] for x in z),'/',sum(x['worlds'] for x in z),
          flush=True)

def save(args,rows,partial,elapsed):
    dest=ROOT/'results';dest.mkdir(parents=True,exist_ok=True)
    name=('partial_' if partial else 'holdout_')+args.model+'.json'
    path=dest/name
    tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(dict(model=args.model,rows=rows,
       seeds=HOLDOUT_SEEDS,steps=args.steps,
       task_init=['monolith','random'],degree=args.degrees,
       pretrained_k=TRAIN_K,heldout_k=UNKNOWN_K,
       status='incomplete' if partial else 'completed',
       elapsed_seconds=time.perf_counter()-elapsed),indent=1),
        encoding='utf8')
    os.replace(tmp,path)

def parse():
    p=argparse.ArgumentParser()
    p.add_argument('--model',required=True)
    p.add_argument('--modes',default=','.join(MODELS))
    p.add_argument('--worlds',type=int,default=24)
    p.add_argument('--steps',type=int,default=40)
    p.add_argument('--degrees',type=lambda x:tuple(int(v) for v in x.split(',')),
       default=(8,12))
    p.add_argument('--device',choices=['cpu','cuda'],default='cuda')
    p.add_argument('--mutual',type=int,choices=[0,1],default=1)
    return p.parse_args()
if __name__=='__main__':run(parse())
