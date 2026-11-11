"""Within-checkpoint ablation: is the explicit requested-k input actually used?

Both conditions use identical weights and world seeds. Zeroing task features
at eval time is an out-of-distribution intervention, so effect may include
input-shift artifacts; report alongside separately retrained hidden-k control.
"""
from dataclasses import replace
from pathlib import Path
import torch,json,argparse,statistics
import train_k
old=train_k.old
HERE=Path(__file__).resolve().parent
def main():
    a=argparse.ArgumentParser()
    a.add_argument('--name',required=True)
    a.add_argument('--device',choices=['cuda','cpu'],default='cuda')
    a.add_argument('--batch',type=int,default=64)
    a.add_argument('--steps',type=int,default=80)
    args=a.parse_args()
    folder=HERE/'runs'/args.name
    spec=json.loads((folder/'config.json').read_text('utf8'))
    cfg=old.Config(**{**spec['config'],'device':args.device})
    actor=train_k.Actor(cfg.n).to(args.device)
    ck=torch.load(folder/'latest.pt',map_location=args.device,weights_only=False)
    actor.load_state_dict(ck['model']);actor.eval()
    scores=[]
    for m in (40,80):
        for k in (2,3,4,5,6,8,10,12,15,20,24,30):
            if m==80 and k in (2,3,4,6):continue
            for visible in (True,False):
                train_k.configure(visible)
                world=replace(cfg,m=m,k=k)
                rows=[old.evaluate(actor,world,seed,batch=args.batch,horizon=args.steps)['final']
                       for seed in (983001,983007)]
                z=dict(m=m,k=k,k_hint_active=visible,food=statistics.mean(r['food'] for r in rows),
                  D=statistics.mean(r['d'] for r in rows),exact=sum(r['exact'] for r in rows),
                  worlds=args.batch*len(rows))
                scores.append(z)
                print('GOAL_ABLATE',args.name,m,k,'input',int(visible),
                      round(z['food'],4),'exact',z['exact'],flush=True)
    old.write_json(HERE/'evaluations'/(args.name+'_GOAL_ABLATION.json'),
                   dict(name=args.name,updates=ck['update'],records=scores,
                        caution='Zeroing k features at test time can cause distribution shift.'))
    print('GOAL_ABLATION_DONE')
if __name__=='__main__':
    torch.set_num_threads(4)
    main()
