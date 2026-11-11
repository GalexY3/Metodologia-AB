"""Held-out evaluation and intervention on independent learned gift policies.

1. Frozen 24-agent networks on new world seeds and network rewiring.
2. Agent-level causal perturbation: randomly matched rollout with a single
   donor forced to give vs refuse at t=0 while all peers are free to react.
3. Compare with unconditional, random, and explicit tit-for-tat heuristics.
No optimization or teaching occurs in this script.
"""
from __future__ import annotations
import argparse,json,os,torch,numpy as np,time
from pathlib import Path
from targeted_gifts import C,PrivateGiftActor,create,step,simulate
ROOT=Path(__file__).resolve().parent
SEEDS=(970001,970007,970009,970021,970031,970037)
CASES=((2,2,'ring'),(2,2,'rewired'),(2,4,'ring'),(2,4,'rewired'),
       (3,2,'ring'),(3,4,'ring'))
MODES=('normal','scramble','no_social',
       'always','random','never','titfortat')
def load(name,device):
    folder=ROOT/'runs'/name
    spec=json.loads((folder/'targeted_spec.json').read_text('utf8'))
    ck=torch.load(folder/'targeted_latest.pt',map_location=device,weights_only=False)
    actor=PrivateGiftActor(spec['n'],spec['hidden'],spec['init_scale']).to(device)
    actor.load_state_dict(ck['model'])
    actor.eval()
    return actor,spec,int(ck['update'])
@torch.no_grad()
def branches(c,actor,seed,mode,i,forced):
    torch.manual_seed(seed*41+211+i)
    w=create(c,seed)
    food=[]
    incoming=[]
    sending=[]
    for t in range(c.horizon):
        dest,gift,_,_=actor.act(c,w,mode)
        if t==0:
            gift=gift.clone()
            gift[:,i]=float(forced)
        r=step(c,w,dest,gift)
        food.append(r[:,i].clone())
        incoming.append(w['incoming'][:,i,:].sum(1).clone())
        sending.append(gift[:,i].clone())
    rewards=torch.stack(food)
    messages=torch.stack(incoming)
    offers=torch.stack(sending)
    discount=c.gamma**torch.arange(c.horizon,device=c.device)
    return dict(
      immediate=float(rewards[0].mean()),
      future_return=float((rewards[1:]*discount[1:,None]).sum(0).mean()),
      total_return=float((rewards*discount[:,None]).sum(0).mean()),
      future_incoming=float(messages[1:].mean()),
      future_giving=float(offers[1:].mean()),
      first_next_incoming=float(messages[1].mean())
    )
@torch.no_grad()
def causal(c,actor,mode='normal',people=(0,4,8,12,16,20)):
    records=[]
    for j,seed in enumerate(SEEDS):
        for person in people:
            give=branches(c,actor,seed,mode,person,1)
            refuse=branches(c,actor,seed,mode,person,0)
            rec=dict(seed=seed,person=person,mode=mode,worlds=c.batch,
                     delta_immediate=give['immediate']-refuse['immediate'],
                     delta_future=give['future_return']-refuse['future_return'],
                     delta_total=give['total_return']-refuse['total_return'],
                     delta_incoming=give['future_incoming']-refuse['future_incoming'],
                     delta_next_incoming=give['first_next_incoming']-refuse['first_next_incoming'],
                     delta_future_giving=give['future_giving']-refuse['future_giving'])
            records.append(rec)
    return dict(
      mode=mode,records=records,
      mean_immediate=float(np.mean([x['delta_immediate'] for x in records])),
      mean_future=float(np.mean([x['delta_future'] for x in records])),
      mean_total=float(np.mean([x['delta_total'] for x in records])),
      mean_incoming=float(np.mean([x['delta_incoming'] for x in records])),
      mean_next_incoming=float(np.mean([x['delta_next_incoming'] for x in records])),
      successes_total=int(sum(x['delta_total']>0 for x in records)),
      pairs=len(records))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--name',required=True)
    p.add_argument('--worlds',type=int,default=32)
    p.add_argument('--steps',type=int,default=48)
    p.add_argument('--device',choices=('cpu','cuda'),default='cuda')
    p.add_argument('--causal',action='store_true')
    a=p.parse_args()
    torch.set_num_threads(3)
    actor,spec,u=load(a.name,a.device)
    rows=[]
    t0=time.perf_counter()
    for k,degree,topo in CASES:
        c=C(n=spec['n'],k=k,degree=degree,topology=topo,
          batch=a.worlds,horizon=a.steps,cost=spec['cost'],
          gamma=spec['gamma'],device=a.device)
        for mode in MODES:
            data=[]
            for seed in SEEDS:
                torch.manual_seed(51*seed+31)
                baseline=mode if mode in ('always','random','never','titfortat') else None
                z,*_=simulate(c,actor,seed,mode='normal' if baseline else mode,
                               baseline=baseline,watch=True)
                data.append(z)
            row=dict(model=a.name,update=u,k=k,topology=topo,degree=degree,
               mode=mode,worlds=sum(x['worlds'] for x in data),
               food=float(np.mean([x['food'] for x in data])),
               gift=float(np.mean([x['gift'] for x in data])),
               coverage=float(np.mean([x['coverage'] for x in data])),
               full=float(np.mean([x['full'] for x in data])),
               conditional_gift=float(np.mean([
                   x['gift_if_previously_received'] or 0 for x in data])),
               by_seed=data)
            rows.append(row)
        print('TARGET_AUDIT_SCENARIO',a.name,k,topo,degree,
            [(v['mode'],round(v['food'],4),round(v['gift'],4))
                   for v in rows[-len(MODES):]],flush=True)
    diagnostic={}
    if a.causal:
        c=C(n=spec['n'],k=2,degree=2,topology='ring',
             batch=a.worlds,horizon=a.steps,cost=spec['cost'],
             gamma=spec['gamma'],device=a.device)
        for mode in ('normal','scramble','no_social'):
            diagnostic[mode]=causal(c,actor,mode=mode)
            print('TARGET_CAUSAL',a.name,mode,
               'immediate',round(diagnostic[mode]['mean_immediate'],4),
               'future',round(diagnostic[mode]['mean_future'],4),
               'total',round(diagnostic[mode]['mean_total'],4),
               'next_incoming',round(diagnostic[mode]['mean_next_incoming'],4),
               'positive_pairs',diagnostic[mode]['successes_total'],
               '/',diagnostic[mode]['pairs'],flush=True)
    data=dict(model=a.name,checkpoint=u,steps=a.steps,seeds=SEEDS,
       conditions=len(rows),worlds=sum(x['worlds'] for x in rows),
       scenarios=rows,causal=diagnostic,
       caveat='Counterfactual one-period intervention, with fixed learned weights and paired stochastic seeds. No claims of spontaneous cooperation without causal positive net benefit.')
    out=ROOT/'results';out.mkdir(exist_ok=True,parents=True)
    target=out/('audit_targeted_'+a.name+'.json')
    target.write_text(json.dumps(data,indent=1),encoding='utf8')
    print('TARGET_AUDIT_COMPLETE',a.name,u,len(rows),
       data['worlds'],'worlds',round(time.perf_counter()-t0),flush=True)
if __name__=='__main__':main()
