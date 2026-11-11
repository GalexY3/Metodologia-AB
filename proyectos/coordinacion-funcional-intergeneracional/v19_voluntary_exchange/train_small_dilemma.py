"""Independent neural learning of costly gifts in a *repeated* social dilemma.

Purpose: determine whether local social feedback, individualized networks,
initial diversity, long temporal credit assignment, and low node degree can
support reciprocal cooperation without a teacher or hard-coded bilateral
contract. This is NOT V19's reciprocal-exchange institution.

A gift always costs c>0 to the donor at the moment of giving and can only
benefit other agents. The donor can benefit later only if recipients adapt.
Role-fixed is a deliberately separate diagnostic, not proof of learned division
of labor. Role-learning arms test the combined task separately.
"""
from __future__ import annotations
import argparse,json,os,random,time
from pathlib import Path
import numpy as np,torch
from exchange import Config,IndependentActors,create_world
from public_goods_dilemma import advance
ROOT=Path(__file__).resolve().parent
class PrivateActor(IndependentActors):
    def __init__(self,n,hidden,scale):
        super().__init__(n,hidden)
        with torch.no_grad():
            self.offer_w1.mul_(scale)
            self.offer_w2.mul_(scale)
            # This changes diversity of initial conditional responses;
            # it does NOT hardcode the direction of reciprocity.
            self.offer_b2.add_(torch.randn(n)*.4)

def simulate(c,actor,seed,fixed_roles,mode='normal',capture=False):
    world=create_world(c,seed)
    logprobs=[];entropies=[];returns=[]
    cond_tally=torch.zeros(4)
    for t in range(c.horizon):
        previous=(world['offers'][:,world['adj']].mean(2)>=.5).float()
        roles,offers,lpjob,lpgive,entjob,entgive=actor.act(c,world,
             mode=mode,return_parts=True)
        if fixed_roles:
            roles=world['roles'].clone()
            lp=lpgive
            ent=entgive
        else:
            lp=lpjob+lpgive
            ent=entjob+entgive
        r=advance(c,world,roles,offers)
        if capture and t>0:
            # Empirical conditioning; not an intervention.
            hi=previous>.5
            lo=~hi
            cond_tally[0]+=offers[hi].sum().cpu()
            cond_tally[1]+=int(hi.sum())
            cond_tally[2]+=offers[lo].sum().cpu()
            cond_tally[3]+=int(lo.sum())
        logprobs.append(lp)
        entropies.append(ent)
        returns.append(r)
    q=c.n//c.k
    counts=torch.nn.functional.one_hot(world['roles'],c.k).sum(1)
    exact=(counts==q).all(1)
    ms=dict(food=float(world['reward'].mean()),
       offer=float(world['offers'].mean()),
       coverage=float(world['coverage'].mean()),
       full=float(world['full'].mean()),
       exact=int(exact.sum()),
       worlds=c.batch,
       imbal=float((counts-q).abs().sum(1).float().mean()/(2*c.n)))
    if capture:
        ah=cond_tally[0]/cond_tally[1].clamp_min(1)
        al=cond_tally[2]/cond_tally[3].clamp_min(1)
        ms['conditional_donation_diff']=float(ah-al)
    return ms,logprobs,entropies,returns

@torch.no_grad()
def eval_actor(actor,args,seed=902001):
    values=[]
    for k in (2,3,4):
        if args.n%k:continue
        for degree in (2,4,8):
            if degree>=args.n:continue
            for topo in ('ring','rewired'):
                for world_seed in (seed+7*k+degree*11,seed+1507+9*k+degree*11):
                    c=Config(n=args.n,k=k,degree=degree,
                      topology=topo,batch=12,horizon=32,
                      device=args.device,init='balanced' if args.roles_fixed else 'random',
                      cost=args.cost,gamma=args.gamma,social=not args.no_social)
                    z,*_=simulate(c,actor,world_seed,args.roles_fixed,
                                  capture=True)
                    z.update(k=k,degree=degree,topology=topo,seed=world_seed)
                    values.append(z)
    result={}
    for subset,items in [('train', [v for v in values if v['k'] in args.train_k]),
                         ('ood',[v for v in values if v['k'] not in args.train_k])]:
        if items:
            result[subset]=dict(
               food=float(np.mean([x['food'] for x in items])),
               offer=float(np.mean([x['offer'] for x in items])),
               coverage=float(np.mean([x['coverage'] for x in items])),
               conditional_donation_diff=float(np.mean([x['conditional_donation_diff'] for x in items])),
               exact=sum(x['exact'] for x in items),
               worlds=sum(x['worlds'] for x in items))
    return result,values

def parse():
    p=argparse.ArgumentParser()
    p.add_argument('--name',required=True)
    p.add_argument('--seed',type=int,default=3111)
    p.add_argument('--n',type=int,default=24)
    p.add_argument('--train-k',type=lambda z:tuple(int(v) for v in z.split(',')),default=(2,3))
    p.add_argument('--degree',type=int,default=2)
    p.add_argument('--topology',choices=('ring','rewired','mixed'),default='ring')
    p.add_argument('--roles-fixed',action='store_true')
    p.add_argument('--no-social',action='store_true')
    p.add_argument('--init-scale',type=float,default=8.)
    p.add_argument('--hidden',type=int,default=16)
    p.add_argument('--batch',type=int,default=24)
    p.add_argument('--horizon',type=int,default=48)
    p.add_argument('--cost',type=float,default=.06)
    p.add_argument('--gamma',type=float,default=.99)
    p.add_argument('--entropy',type=float,default=.02)
    p.add_argument('--lr',type=float,default=.002)
    p.add_argument('--updates',type=int,default=1600)
    p.add_argument('--eval-every',type=int,default=200)
    p.add_argument('--device',choices=('cpu','cuda'),default='cuda')
    return p.parse_args()

def main():
    a=parse()
    a.train_k=a.train_k
    assert a.n>=8 and 0<a.cost<=.2 and all(a.n%k==0 for k in a.train_k)
    torch.set_num_threads(3)
    torch.manual_seed(a.seed);np.random.seed(a.seed)
    dest=ROOT/'runs'/a.name
    dest.mkdir(parents=True,exist_ok=True)
    config=dict(vars(a));config['train_k']=list(a.train_k)
    specfile=dest/'small_spec.json'
    if specfile.exists():
        prev=json.loads(specfile.read_text('utf8'))
        assert all(config[key]==prev[key] for key in config if key!='updates') and a.updates>=prev['updates']
    specfile.write_text(json.dumps(config,indent=2),encoding='utf8')
    actor=PrivateActor(a.n,a.hidden,a.init_scale).to(a.device)
    optimizer=torch.optim.Adam(actor.parameters(),lr=a.lr)
    ck=dest/'small_latest.pt'
    start=0
    if ck.exists():
        state=torch.load(ck,weights_only=False,map_location=a.device)
        actor.load_state_dict(state['model'])
        optimizer.load_state_dict(state['optimizer'])
        start=int(state['update'])
        torch.set_rng_state(state['cpu_rng'])
        if a.device=='cuda':torch.cuda.set_rng_state(state['gpu_rng'])
    print('SMALL_START',a.name,'n',a.n,'learn_roles',not a.roles_fixed,
       'own_agent_parameters',sum(p.numel() for p in actor.parameters())//a.n,
       'initial_gradient_scale',a.init_scale,flush=True)
    if start==0:
        init,v=eval_actor(actor,a)
        print('SMALL_INIT',a.name,init,flush=True)
    started=time.perf_counter()
    for u in range(start+1,a.updates+1):
        k=a.train_k[(u-1)%len(a.train_k)]
        topo=(('ring','rewired')[(u//len(a.train_k))%2]
              if a.topology=='mixed' else a.topology)
        c=Config(n=a.n,k=k,degree=a.degree,topology=topo,
           batch=a.batch,horizon=a.horizon,device=a.device,
           init='balanced' if a.roles_fixed else ['balanced','random','half'][u%3],
           cost=a.cost,gamma=a.gamma,social=not a.no_social)
        state,logs,ents,rews=simulate(c,actor,a.seed*100001+u*571,
             a.roles_fixed)
        seq=torch.stack(rews)
        ret=torch.zeros_like(seq[0]);rl=[]
        for r in reversed(seq):
            ret=r+a.gamma*ret
            rl.append(ret)
        R=torch.stack(rl[::-1])
        base=(R.sum(1,keepdim=True)-R)/(c.batch-1)
        advantage=((R-base)/R.std(1,keepdim=True,unbiased=False).clamp_min(.2)).detach()
        objective=-(torch.stack(logs)*advantage).mean() - a.entropy*torch.stack(ents).mean()
        optimizer.zero_grad(set_to_none=True);objective.backward()
        norms=torch.zeros(a.n,device=a.device)
        for p in actor.parameters():
            if p.grad is not None:norms+=p.grad.detach().reshape(a.n,-1).square().sum(1)
        with torch.no_grad():
            scale=(2/(norms.sqrt()+1e-10)).clamp(max=1)
            for p in actor.parameters():
                if p.grad is not None:p.grad.mul_(scale.reshape(a.n,*([1]*(p.ndim-1))))
        optimizer.step()
        if u==1 or u%a.eval_every==0 or u==a.updates:
            val,raw=eval_actor(actor,a)
            row=dict(update=u,training=state,eval=val,elapsed_seconds=time.perf_counter()-started)
            with (dest/'small_history.jsonl').open('a',encoding='utf8') as fp:
                fp.write(json.dumps(row)+'\n')
            print('SMALL_UPDATE',a.name,u,
              'train_food',round(state['food'],4),
              'train_offer',round(state['offer'],4),
              'TEST', {q:{key:round(v,4) if isinstance(v,float) else v for key,v in x.items()}
                   for q,x in val.items()},flush=True)
        if u%a.eval_every==0 or u==a.updates:
            tmp=dest/'small_tmp.pt'
            torch.save(dict(model=actor.state_dict(),
                  optimizer=optimizer.state_dict(),update=u,
                  cpu_rng=torch.get_rng_state(),
                  gpu_rng=torch.cuda.get_rng_state() if a.device=='cuda' else None),tmp)
            os.replace(tmp,ck)
    (dest/'small_status.json').write_text(json.dumps(dict(state='completed',
        updates=a.updates,elapsed_seconds=time.perf_counter()-started)),encoding='utf8')
    print('SMALL_DONE',a.name,a.updates,flush=True)
if __name__=='__main__':main()
