"""Train 24 independent private-policy agents in a directed repeated gift dilemma.

No enforced bilateral exchange or self-reward for gifts. Test conditional
reciprocity by changing recipient visibility after freezing policies.
All learning gradients are based exclusively on the focal agent's own food.
"""
from __future__ import annotations
import argparse,time,os,json,torch,numpy as np
from pathlib import Path
from dataclasses import replace
from targeted_gifts import C,PrivateGiftActor,simulate
ROOT=Path(__file__).resolve().parent

@torch.no_grad()
def evaluate(actor,device,cost,seed=947001,batch=12,horizon=32):
    scenarios=[]
    for k,degree,top in [
      (2,2,'ring'),(2,2,'rewired'),(2,4,'ring'),
      (2,4,'rewired'),(3,2,'ring'),(3,4,'ring')]:
        c=C(n=actor.n,k=k,degree=degree,topology=top,
            batch=batch,horizon=horizon,cost=cost,device=device)
        for i in range(2):
            rows={}
            for mode in ('normal','no_social','scramble'):
                torch.manual_seed(seed+9*k+degree*41+i*1009)
                res=simulate(c,actor,seed+9*k+degree*41+i*1009,
                   mode=mode,watch=True)[0]
                rows[mode]=res
            scenarios.append(dict(k=k,degree=degree,topology=top,
                        seed=i,conditions=rows))
    aggregate={}
    for label,pick in (('trained',lambda r:r['k']==2 and r['degree']==2 and r['topology']=='ring'),
                       ('ood',lambda r:not(r['k']==2 and r['degree']==2 and r['topology']=='ring'))):
        values=[s['conditions']['normal'] for s in scenarios if pick(s)]
        for mode in ('normal','no_social','scramble'):
            w=[s['conditions'][mode] for s in scenarios if pick(s)]
            aggregate[label+'_'+mode]=dict(
               food=float(np.mean([z['food'] for z in w])),
               gift=float(np.mean([z['gift'] for z in w])),
               coverage=float(np.mean([z['coverage'] for z in w])),
               conditional_gift=float(np.mean([z['gift_if_previously_received']
                    if z['gift_if_previously_received'] is not None else 0 for z in w])),
               worlds=sum(x['worlds'] for x in w))
    return aggregate,scenarios

def parse():
    p=argparse.ArgumentParser()
    p.add_argument('--name',required=True)
    p.add_argument('--seed',type=int,default=3111)
    p.add_argument('--n',type=int,default=24)
    p.add_argument('--hidden',type=int,default=20)
    p.add_argument('--init-scale',type=float,default=8)
    p.add_argument('--cost',type=float,default=.12)
    p.add_argument('--gamma',type=float,default=.995)
    p.add_argument('--horizon',type=int,default=64)
    p.add_argument('--batch',type=int,default=32)
    p.add_argument('--updates',type=int,default=1400)
    p.add_argument('--lr',type=float,default=.002)
    p.add_argument('--entropy',type=float,default=.015)
    p.add_argument('--train-topology',choices=['ring','rewired','mixed'],default='ring')
    p.add_argument('--social',type=int,choices=[0,1],default=1)
    p.add_argument('--eval-every',type=int,default=200)
    p.add_argument('--device',choices=('cpu','cuda'),default='cuda')
    return p.parse_args()

def main():
    a=parse()
    assert a.n%2==0 and 0<a.cost<=.2
    torch.set_num_threads(3)
    torch.manual_seed(a.seed);np.random.seed(a.seed)
    folder=ROOT/'runs'/a.name;folder.mkdir(parents=True,exist_ok=True)
    f=folder/'targeted_spec.json'
    if f.exists():
        older=json.loads(f.read_text('utf8'))
        assert all(older[key]==val for key,val in vars(a).items() if key!='updates')
    f.write_text(json.dumps(vars(a),indent=2),encoding='utf8')
    actor=PrivateGiftActor(a.n,a.hidden,a.init_scale).to(a.device)
    opt=torch.optim.Adam(actor.parameters(),lr=a.lr)
    ck=folder/'targeted_latest.pt'
    start=0
    if ck.exists():
        state=torch.load(ck,weights_only=False,map_location=a.device)
        actor.load_state_dict(state['model']);opt.load_state_dict(state['optimizer'])
        torch.set_rng_state(state['rng_cpu'])
        if a.device=='cuda':torch.cuda.set_rng_state(state['rng_gpu'])
        start=state['update']
    print('TARGET_TRAIN_START',a.name,'agents',a.n,
          'parameters_per_agent',sum(p.numel() for p in actor.parameters())//a.n,
          'cost',a.cost,'gamma',a.gamma,'social',a.social,flush=True)
    t0=time.perf_counter()
    if start==0:
        init,_=evaluate(actor,a.device,a.cost)
        print('TARGET_INIT',a.name,
              {k:{p:round(v,4) if isinstance(v,float) else v
                  for p,v in stat.items()} for k,stat in init.items()},flush=True)
    for u in range(start+1,a.updates+1):
        top=(('ring','rewired')[(u//2)%2]
            if a.train_topology=='mixed' else a.train_topology)
        c=C(n=a.n,k=2,degree=2,topology=top,batch=a.batch,
            horizon=a.horizon,cost=a.cost,gamma=a.gamma,
            device=a.device,social=bool(a.social))
        metrics,logs,ents,rews=simulate(c,actor,a.seed*19301+u*31)
        rewards=torch.stack(rews)
        ret=torch.zeros_like(rewards[0])
        sequence=[]
        for reward in reversed(rewards):
            ret=reward+c.gamma*ret
            sequence.append(ret)
        R=torch.stack(sequence[::-1])
        leave_one=(R.sum(1,keepdim=True)-R)/(c.batch-1)
        advantage=((R-leave_one)/R.std(1,unbiased=False,
            keepdim=True).clamp_min(.25)).detach()
        loss=-(torch.stack(logs)*advantage).mean() - a.entropy*torch.stack(ents).mean()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        norms=torch.zeros(a.n,device=a.device)
        for parameter in actor.parameters():
            if parameter.grad is not None:
                norms+=parameter.grad.detach().reshape(a.n,-1).square().sum(1)
        with torch.no_grad():
            scale=(2/(norms.sqrt()+1e-10)).clamp(max=1)
            for parameter in actor.parameters():
                if parameter.grad is not None:
                    parameter.grad.mul_(scale.reshape(a.n,*([1]*(parameter.ndim-1))))
        opt.step()
        if u==1 or u%a.eval_every==0 or u==a.updates:
            dev,_=evaluate(actor,a.device,a.cost)
            row=dict(update=u,loss=float(loss.detach()),
                elapsed_seconds=time.perf_counter()-t0,
                train=metrics,eval=dev)
            with (folder/'targeted_history.jsonl').open('a',encoding='utf8') as fp:
                fp.write(json.dumps(row)+'\n')
            print('TARGET_UPDATE',a.name,u,'train_food',
                round(metrics['food'],4),'train_gift',round(metrics['gift'],4),
                'DEV', {label:{v:round(x,4) if isinstance(x,float) else x
                       for v,x in stat.items()} for label,stat in dev.items()},flush=True)
            snapshot=dict(model=actor.state_dict(),optimizer=opt.state_dict(),
              update=u,rng_cpu=torch.get_rng_state(),
              rng_gpu=torch.cuda.get_rng_state() if a.device=='cuda' else None)
            tmp=folder/'targeted_tmp.pt';torch.save(snapshot,tmp);os.replace(tmp,ck)
    (folder/'targeted_status.json').write_text(json.dumps(
       dict(state='completed',updates=a.updates,seconds=time.perf_counter()-t0)),encoding='utf8')
    print('TARGET_TRAIN_DONE',a.name,a.updates,flush=True)
if __name__=='__main__':main()
