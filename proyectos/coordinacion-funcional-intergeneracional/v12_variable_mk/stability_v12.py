"""Audit stable exact solutions, not merely momentary exact end states."""
from pathlib import Path
from dataclasses import replace
import argparse,json
import torch
from v12 import ROOT,Config,World,IndividualAgent,write_json
def main():
    args=argparse.ArgumentParser()
    args.add_argument('--prefix',default='v12_ext_n60_')
    args.add_argument('--worlds',type=int,default=64)
    args.add_argument('--horizon',type=int,default=100)
    a=args.parse_args()
    torch.set_num_threads(3)
    rows=[]
    for folder in sorted((ROOT/'runs').glob(a.prefix+'*')):
        if not (folder/'latest.pt').exists():continue
        setup=json.loads((folder/'config.json').read_text('utf8'))
        cfg=Config(**{**setup['config'],'device':'cpu'})
        model=IndividualAgent(cfg.n)
        st=torch.load(folder/'latest.pt',map_location='cpu',weights_only=False)
        model.load_state_dict(st['model']);model.eval()
        for label,m,k,init in (('known',10,2,'random'),('new',30,5,'random'),
                               ('trap',20,4,'trap')):
            if cfg.n%k:continue
            for greedy in (False,True):
                totals=[]
                for seed in (980011,980031):
                    env=World(replace(cfg,m=m,k=k,batch=a.worlds,horizon=a.horizon,init=init),seed)
                    model.reset()
                    streak=torch.zeros(a.worlds,dtype=torch.int32)
                    best=torch.zeros_like(streak)
                    seen=torch.zeros(a.worlds,dtype=torch.bool)
                    exact_final=torch.zeros_like(seen)
                    churn=[];foods=[];positions=[]
                    with torch.no_grad():
                        for t in range(a.horizon):
                            old=env.jobs
                            new,_,_=model.act(env,greedy=greedy)
                            env.advance(new)
                            d=1-env.counts.topk(k,dim=1).values.clamp(max=cfg.n/k).sum(1)/cfg.n
                            exact=d.abs()<1e-6
                            seen|=exact
                            streak=torch.where(exact,streak+1,0)
                            best=torch.maximum(best,streak)
                            exact_final=exact
                            if t>=a.horizon-20:
                                churn.append(float((old!=new).float().mean()))
                                foods.append(float(env.food.mean()))
                                positions.append(float((env.counts>0).float().sum(1).mean()))
                    totals.append(dict(seed=seed,exact_once=int(seen.sum()),
                        exact_final=int(exact_final.sum()),sustained_3=int((best>=3).sum()),
                        sustained_5=int((best>=5).sum()),food_last20=sum(foods)/len(foods),
                        churn_last20=sum(churn)/len(churn),occupied_last20=sum(positions)/len(positions)))
                row=dict(model=folder.name,update=st['update'],scenario=label,
                  m=m,k=k,init=init,policy='greedy' if greedy else 'stochastic',
                  worlds=a.worlds*len(totals),by_seed=totals,
                  exact_once=sum(x['exact_once'] for x in totals),
                  exact_last=sum(x['exact_final'] for x in totals),
                  sustained_5=sum(x['sustained_5'] for x in totals),
                  food_last20=sum(x['food_last20'] for x in totals)/len(totals),
                  churn_last20=sum(x['churn_last20'] for x in totals)/len(totals))
                rows.append(row)
                print('STABILITY',row['model'],label,row['policy'],
                  'exact_any',row['exact_once'],'sustain5',row['sustained_5'],
                  'food',round(row['food_last20'],4),
                  'churn',round(row['churn_last20'],3),flush=True)
    write_json(ROOT/(a.prefix.rstrip('_')+'_STABILITY.json'),dict(
        kind='POSTHOC_EXPLORATORY_TIME_SERIES_STABILITY',
        worlds_per_seed=a.worlds,horizon=a.horizon,seeds=[980011,980031],results=rows))
    print('STABILITY_COMPLETE')
if __name__=='__main__':main()
