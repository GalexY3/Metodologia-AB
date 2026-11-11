"""Prospective novel-M frozen test, independent of the original M24/M80 screen.
Policy selected BEFORE examining these M=12/40/60 results:
neural option selection stochastic for k/M < 0.50, argmax otherwise.
M=12,40,60 were absent from all gradient updates.
"""
from pathlib import Path
from dataclasses import replace
import argparse,json,math
import numpy as np,torch
import v15
from evaluate_v15 import simulate,baseline_analytic,CASES
HERE=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--name',required=True)
    ap.add_argument('--device',default='cuda',choices=['cpu','cuda'])
    ap.add_argument('--worlds',type=int,default=64)
    ap.add_argument('--steps',type=int,default=90)
    ap.add_argument('--seeds',default='260111,260113,260117,260119')
    ap.add_argument('--m-values',default='12,40,60')
    args=ap.parse_args()
    torch.set_num_threads(4)
    root=HERE/'runs'/args.name
    spec=json.loads((root/'spec.json').read_text('utf8'))
    params=spec['args']
    conf=v15.envlib.Config(n=params['n'],m=80,k=2,degree=params['degree'],
             batch=args.worlds,horizon=args.steps,device=args.device)
    model=v15.OptionActor(conf.n,params['h'],
             recurrent=not params['no_recurrence']).to(args.device)
    ck=torch.load(root/'latest.pt',weights_only=False,map_location=args.device)
    model.load_state_dict(ck['model']);model.eval()
    ss=[int(z) for z in args.seeds.split(',')]
    ms=[int(z) for z in args.m_values.split(',')]
    cases=[]
    for m in ms:
        for k in CASES:
            if k>m:continue
            c=replace(conf,m=m,k=k)
            vals={}
            for mode in ('adaptive','random'):
                d=[]
                for s in ss:
                    res=simulate(model if mode=='adaptive' else None,c,s,mode=mode)
                    d.append(dict(seed=s,**res))
                score=np.array([x for r in d for x in r['food']])
                exact=np.array([x for r in d for x in r['exact']])
                vals[mode]=dict(food=float(score.mean()),exact=int(exact.sum()),
                     occupied=float(np.mean([x for r in d for x in r['occupied']])),
                     by_seed=d)
            neural=vals['adaptive']
            random=vals['random']
            per_world=np.array([p-q for a,b in zip(neural['by_seed'],random['by_seed'])
                              for p,q in zip(a['food'],b['food'])])
            seed_means=np.array([float(np.mean(np.array(a['food'])-np.array(b['food'])))
                                for a,b in zip(neural['by_seed'],random['by_seed'])])
            std=float(per_world.std(ddof=1))
            # Normal approximation for descriptive within-checkpoint uncertainty;
            # NOT proof across independently trained neural populations.
            margin=float(per_world.mean())
            lower95=margin-1.96*std/math.sqrt(len(per_world))
            cases.append(dict(m=m,k=k,n=conf.n,canonical=conf.n%k==0,
              m_unseen=True,k_trained=any(int(kk)==k for mm,kk in spec['pairs']),
              ratio=k/m,policy='argmax' if k/m>=.5 else 'sample',
              food=neural['food'],random_food=random['food'],
              theoretical_random=baseline_analytic(conf.n,m,k),
              margin=margin,paired_lower95=lower95,
              paired_world_win_rate=float(np.mean(per_world>0)),
              per_seed_margins=seed_means.tolist(),exact=neural['exact'],
              worlds=len(per_world),average_occupied=neural['occupied'],
              conditions=vals))
            print('UNSEEN_M',args.name,'M',m,'k',k,
                  'policy',cases[-1]['policy'],'food',round(neural['food'],4),
                  'random',round(random['food'],4),
                  'delta',round(margin,4),'lo95',round(lower95,4),
                  'world_wins',round(cases[-1]['paired_world_win_rate'],3),
                  flush=True)
    out=HERE/'evaluations'/(args.name+'_UNSEEN_M.json')
    v15.envlib.write_json(out,dict(model=args.name,update=ck['update'],
      policy_threshold=.5,selected_before_seeing_novel_M=True,
      report='One training seed per architecture, four fresh RNG seeds per tested M/k.',
      n_worlds_per_case=args.worlds*len(ss),cases=cases))
    print('NOVEL_M_COMPLETE',args.name,'cases',len(cases),
          'positive',sum(x['margin']>0 for x in cases),
          'normal_lower95_positive',sum(x['paired_lower95']>0 for x in cases),flush=True)

if __name__=='__main__':main()
