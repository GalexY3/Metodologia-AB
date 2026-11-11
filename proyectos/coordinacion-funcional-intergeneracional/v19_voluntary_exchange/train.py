"""V19 independent REINFORCE self-play; individual reward, no shared parameters.

No teacher, fixed role rule, central critic or global welfare used in training.
The reciprocal exchange institution is an environment rule, not learned.
"""
from __future__ import annotations
import argparse,time,os,json,math,torch,numpy as np,random
from pathlib import Path
from exchange import Config,IndependentActors,rollout
ROOT=Path(__file__).resolve().parent
TRAIN_K=(2,3,4,6)
OOD_K=(5,10,12)
def task(u,seed,mode,device,batch,horizon):
    rng=random.Random(seed*1709+u*97)
    # Balanced randomization; all rewards depend on local endowment, not
    # an evaluator-specified global distance to target.
    k=TRAIN_K[u%len(TRAIN_K)]
    top=['ring','rewired'][u%2] if mode=='mixed' else 'ring'
    degree=[8,12][(u//4)%2] if mode=='mixed' else 10
    init=['monolith','random','half','balanced'][u%4]
    return k,top,degree,init

@torch.no_grad()
def evaluate(actor,device,mutual,social,seed=910011,batch=16,horizon=30):
    groups=[
      (k,top,deg,init) for k in (2,3,4,5,6,10)
      for top in ('ring','rewired') for deg in (8,12)
      for init in ('random','monolith')
    ]
    data=[]
    for j,(k,top,degree,init) in enumerate(groups):
        conf=Config(n=60,k=k,degree=degree,topology=top,
                    init=init,batch=batch,horizon=horizon,
                    device=device,mutual=mutual,social=social)
        result=rollout(conf,actor,seed+37*j)
        m=result['metrics']
        data.append(dict(k=k,topology=top,degree=degree,init=init,
                         food=m['food'],exact=m['exact'],worlds=m['worlds'],
                         imbalance=m['imbalance'],coverage=m['coverage'],
                         offer=m['offer'],full=m['full']))
    # Report weighted means over equally weighted scenario cells, not
    # cherry-picked conditions. Distinguish training and unseen K.
    train=[x for x in data if x['k'] in TRAIN_K]
    ood=[x for x in data if x['k'] not in TRAIN_K]
    summary={}
    for name,rows in (('train_k',train),('unseen_k',ood)):
        summary[name]=dict(food=float(np.mean([x['food'] for x in rows])),
           offer=float(np.mean([x['offer'] for x in rows])),
           coverage=float(np.mean([x['coverage'] for x in rows])),
           imbalance=float(np.mean([x['imbalance'] for x in rows])),
           exact=sum(x['exact'] for x in rows),
           worlds=sum(x['worlds'] for x in rows))
    return dict(summary=summary,conditions=data)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--name',required=True)
    ap.add_argument('--seed',type=int,default=3111)
    ap.add_argument('--updates',type=int,default=700)
    ap.add_argument('--hidden',type=int,default=16)
    ap.add_argument('--batch',type=int,default=16)
    ap.add_argument('--horizon',type=int,default=20)
    ap.add_argument('--lr',type=float,default=.003)
    ap.add_argument('--entropy',type=float,default=.005)
    ap.add_argument('--device',choices=['cpu','cuda'],default='cuda')
    ap.add_argument('--mutual',type=int,choices=[0,1],default=1)
    ap.add_argument('--social',type=int,choices=[0,1],default=1)
    ap.add_argument('--topology-train',choices=['ring','mixed'],default='mixed')
    ap.add_argument('--eval-every',type=int,default=100)
    ap.add_argument('--checkpoint-every',type=int,default=100)
    args=ap.parse_args()
    torch.set_num_threads(3)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    dest=ROOT/'runs'/args.name
    dest.mkdir(exist_ok=True,parents=True)
    spec=vars(args)
    specpath=dest/'config.json'
    if specpath.exists():
        previous=json.loads(specpath.read_text('utf8'))
        changed=[k for k in spec if k!='updates' and spec[k]!=previous[k]]
        if changed or args.updates<int(previous['updates']):
            raise RuntimeError(f'Resume config mismatch {changed}')
    specpath.write_text(json.dumps(spec,indent=2),encoding='utf8')
    actor=IndependentActors(60,args.hidden).to(args.device)
    opt=torch.optim.Adam(actor.parameters(),lr=args.lr)
    ck=dest/'latest.pt'
    start=0
    if ck.exists():
        state=torch.load(ck,map_location=args.device,weights_only=False)
        actor.load_state_dict(state['actor'])
        opt.load_state_dict(state['optimizer'])
        start=int(state['update'])
        torch.set_rng_state(state['rng_cpu'])
        if args.device=='cuda':torch.cuda.set_rng_state(state['rng_gpu'])
    param_count=sum(p.numel() for p in actor.parameters())
    print('V19_TRAIN_START',args.name,'resume',start,
          'params_per_agent',param_count//60,'total',param_count,
          'mutual',args.mutual,'social',args.social,
          'mixed',args.topology_train=='mixed',flush=True)
    t0=time.perf_counter()
    if start==0:
        initial=evaluate(actor,args.device,bool(args.mutual),bool(args.social),
                         seed=910011,batch=12,horizon=24)
        (dest/'initial_eval.json').write_text(json.dumps(initial,indent=1),encoding='utf8')
        print('V19_INITIAL',args.name,initial['summary'],flush=True)
    for update in range(start+1,args.updates+1):
        k,top,degree,init=task(update,args.seed,args.topology_train,
            args.device,args.batch,args.horizon)
        c=Config(n=60,k=k,degree=degree,topology=top,batch=args.batch,
                 horizon=args.horizon,device=args.device,init=init,
                 mutual=bool(args.mutual),social=bool(args.social))
        outcome=rollout(c,actor,args.seed*100000+update*79)
        rewards=torch.stack(outcome['rewards'])
        ret=torch.zeros_like(rewards[0])
        returns=[]
        for t in reversed(range(c.horizon)):
            ret=rewards[t]+c.gamma*ret
            returns.append(ret)
        R=torch.stack(returns[::-1])
        baseline=(R.sum(1,keepdim=True)-R)/(c.batch-1)
        advantage=((R-baseline)/R.std(1,unbiased=False,
               keepdim=True).clamp_min(.15)).detach()
        lp=torch.stack(outcome['logs'])
        ents=torch.stack(outcome['ents'])
        loss=-(lp*advantage).mean() - args.entropy*ents.mean()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        # Gradient clipping per private actor. Never aggregate gradients
        # across agents, even though their learning data are correlated.
        grad_norm=torch.zeros(60,device=args.device)
        for p in actor.parameters():
            if p.grad is not None:
                grad_norm+=p.grad.detach().reshape(60,-1).square().sum(1)
        with torch.no_grad():
            factors=(2/(grad_norm.sqrt()+1e-10)).clamp(max=1)
            for p in actor.parameters():
                if p.grad is not None:
                    p.grad.mul_(factors.reshape(60,*([1]*(p.ndim-1))))
        opt.step()
        if update==1 or update%args.eval_every==0 or update==args.updates:
            with torch.no_grad():
                stats=evaluate(actor,args.device,bool(args.mutual),
                      bool(args.social),seed=910011,batch=12,horizon=24)
            record=dict(update=update,training_loss=float(loss.detach()),
               training_food=outcome['metrics']['food'],
               training_give=outcome['metrics']['offer'],
               elapsed_seconds=time.perf_counter()-t0,
               summary=stats['summary'])
            with (dest/'history.jsonl').open('a',encoding='utf8') as f:
                f.write(json.dumps(record)+'\n')
            print('V19_UPDATE',args.name,update,
               'trainfood',round(record['training_food'],4),
               'train_offer',round(record['training_give'],4),
               'dev_train_k', {key:round(v,4) if isinstance(v,float) else v
                   for key,v in stats['summary']['train_k'].items()},
               'dev_ood_k',{key:round(v,4) if isinstance(v,float) else v
                   for key,v in stats['summary']['unseen_k'].items()},
                flush=True)
        if update%args.checkpoint_every==0 or update==args.updates:
            snapshot=dict(update=update,actor=actor.state_dict(),
                optimizer=opt.state_dict(),rng_cpu=torch.get_rng_state(),
                rng_gpu=torch.cuda.get_rng_state() if args.device=='cuda' else None)
            tmp=dest/'checkpoint_tmp.pt'
            torch.save(snapshot,tmp);os.replace(tmp,ck)
            if update%500==0 or update==args.updates:
                torch.save(snapshot,dest/f'checkpoint_{update:06d}.pt')
    (dest/'status.json').write_text(json.dumps(dict(state='complete',
       update=args.updates,elapsed=time.perf_counter()-t0)),encoding='utf8')
    print('V19_TRAIN_DONE',args.name,args.updates,'seconds',
          round(time.perf_counter()-t0,2),flush=True)
if __name__=='__main__':main()
