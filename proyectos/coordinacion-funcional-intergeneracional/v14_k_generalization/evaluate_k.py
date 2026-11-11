"""Frozen-policy transfer audit for requested-k independent actors."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import torch,sys,json,argparse,statistics
import train_k
old=train_k.old
HERE=Path(__file__).resolve().parent

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--name',required=True)
    a.add_argument('--batch',type=int,default=48)
    a.add_argument('--steps',type=int,default=80)
    a.add_argument('--seeds',default='971531,971777,971999')
    a.add_argument('--device',default='cpu',choices=['cuda','cpu'])
    args=a.parse_args()
    torch.set_num_threads(4)
    folder=HERE/'runs'/args.name
    spec=json.loads((folder/'config.json').read_text('utf8'))
    cfg=spec['config']
    info=json.loads((folder/'V14_MODEL_SPEC.json').read_text('utf8'))
    train_k.configure(info['knows_requested_k'])
    base=old.Config(**{**cfg,'device':args.device})
    model=train_k.Actor(base.n).to(args.device)
    ck=torch.load(folder/'latest.pt',map_location=args.device,weights_only=False)
    model.load_state_dict(ck['model']);model.eval()
    train_ks={int(k) for m,k in spec['tasks']}
    train_ms={int(m) for m,k in spec['tasks']}
    tests=[('training',12,k) for k in (2,3,4,6)]
    tests += [('new_M40',40,k) for k in (2,3,4,5,6,8,10,12,15,20,24,30) if base.n%k==0]
    tests += [('new_M80',80,k) for k in (5,8,10,12,15,20,24,30) if base.n%k==0]
    seeds=[int(x) for x in args.seeds.split(',')]
    records=[]
    for group,m,k in tests:
        c=replace(base,m=m,k=k,batch=args.batch,horizon=args.steps,init='random')
        for mode in ('learned','greedy','random','imitate'):
            if mode in ('random','imitate') and group=='training' and k not in (2,4):
                continue
            runs=[]
            for seed in seeds:
                kwargs=dict(batch=args.batch,horizon=args.steps)
                if mode=='learned':
                    x=old.evaluate(model,c,seed,**kwargs)['final']
                elif mode=='greedy':
                    x=old.evaluate(model,c,seed,greedy=True,**kwargs)['final']
                else:
                    x=old.evaluate(None,c,seed,baseline=mode,**kwargs)['final']
                runs.append(x)
            rec=dict(model=args.name,n=base.n,group=group,
                m=m,k=k,k_trained=k in train_ks,m_trained=m in train_ms,
                mode=mode,weights_update=int(ck['update']),
                avg_food=statistics.mean(x['food'] for x in runs),
                avg_D=statistics.mean(x['d'] for x in runs),
                occupied=statistics.mean(x['occupied'] for x in runs),
                exact=sum(x['exact'] for x in runs),
                worlds=args.batch*len(seeds),
                by_seed=[dict(seed=seed,**x) for seed,x in zip(seeds,runs)])
            records.append(rec)
            print('TEST',args.name,group,'M',m,'k',k,mode,
                'food',round(rec['avg_food'],4),'D',round(rec['avg_D'],4),
                'exact',rec['exact'],'/'+str(rec['worlds']),flush=True)
    out=HERE/'evaluations'/(args.name+'_EVAL.json')
    old.write_json(out,dict(name=args.name,n=base.n,
      k_hint=info['knows_requested_k'],seed_list=seeds,
      worlds_per_seed=args.batch,horizon=args.steps,
      frozen_checkpoint_update=int(ck['update']),training_k=sorted(train_ks),
      training_M=sorted(train_ms),evals=records))
    print('EVAL_COMPLETE',args.name,len(records),'conditions',flush=True)
if __name__=='__main__':main()
