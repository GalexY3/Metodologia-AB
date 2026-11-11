"""V17 private-neural two-phase pledge policy over local communication.

For each actor: observe own reward, own history and neighbor job histogram.
Policy samples a pledge intent; proposed destination is chosen locally and
propagated through R rounds of graph messages BEFORE any profession changes.
Conditional quorum checks count only received signaled pledges; no occupation
census or collective reward enters any policy. All actors have disjoint weights.
"""
from __future__ import annotations
import sys,math,os,random,time,json,argparse
from dataclasses import replace,asdict
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Bernoulli
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'v12_variable_mk'))
import v12 as envlib
NF=12

class PledgeActor(nn.Module):
 def __init__(self,n,h=16,rounds=8,quorum=True,features='lattice',
              scramble=False,gate=True):
  super().__init__()
  self.n=n;self.h=h;self.rounds=rounds
  self.quorum=quorum;self.features=features
  self.scramble=scramble;self.gate=gate
  self._cached_reach=None
  self.wx=nn.Parameter(torch.randn(n,NF,h)*(.6/math.sqrt(NF)))
  self.b=nn.Parameter(torch.zeros(n,h))
  self.v=nn.Parameter(torch.randn(n,h)*(.3/math.sqrt(h)))
  self.bias=nn.Parameter(torch.zeros(n))
  self.reset()
 def reset(self):
  self.emafood=None;self.emaown=None;self.prevjob=None;self.history=None
 def act(self,e,greedy=False,disable_messages=False,alter_messages=False):
  c=e.c;b,n=e.jobs.shape;q=n/c.k
  loc=e.local()
  own=loc.gather(2,e.jobs[...,None]).squeeze(2)
  if self.emafood is None or self.emafood.shape!=e.food.shape:
   self.emafood=e.food.detach()
   self.emaown=own.detach()
   self.prevjob=e.jobs.detach()
  self.emafood=(.8*self.emafood+.2*e.food).detach()
  self.emaown=(.75*self.emaown+.25*own).detach()
  r=e.food
  sub=q*r;sup=q/r.clamp_min(1e-6)
  a=(sub>=1-1e-6)&(sub<q-1e-6)&((sub-sub.round()).abs()<2e-4)
  z=(sup>q+1e-6)&(sup<=n+1e-6)&((sup-sup.round()).abs()<2e-4)
  inferred=torch.where(a&~z,-torch.ones_like(r),
      torch.where(z&~a,torch.ones_like(r),
       torch.where(r>=1-1e-6,torch.zeros_like(r),
        torch.where(own>(q-1)/(n-1),torch.ones_like(r),-torch.ones_like(r)))))
  if self.features=='raw':
   signed=torch.zeros_like(inferred)
   lattice=torch.zeros_like(r)
  elif self.features=='local':
   signed=torch.where(own>(q-1)/(n-1),torch.ones_like(r),-torch.ones_like(r))
   lattice=torch.zeros_like(r)
  elif self.features=='oracle':
   # ILLEGAL input in decentralized model; diagnostic bound only
   signed=torch.sign(e.counts.gather(1,e.jobs)-q)
   lattice=torch.ones_like(r)
  else:
   signed=inferred
   lattice=((sub-sub.round()).abs()-(sup-sup.round()).abs()).clamp(-1,1)
  def cst(v):return torch.full_like(r,float(v))
  obs=torch.stack([r,1-r,own,self.emaown,self.emafood,
    cst(c.k/c.m),cst(q/n),cst(math.log(q)/math.log(n)),
    signed,lattice,(self.prevjob!=e.jobs).float(),
    cst(e.t/c.horizon)],dim=-1)
  h=torch.tanh(torch.einsum('bnd,ndh->bnh',obs,self.wx)+self.b[None,:,:])
  logits=torch.einsum('bnh,nh->bn',h,self.v)+self.bias[None,:]
  dist=Bernoulli(logits=logits)
  sampled=(logits>0).float() if greedy else dist.sample()
  canmove=(signed>0) if self.gate else (r<.9999)
  pledge=sampled.bool()&canmove
  logp=dist.log_prob(sampled)*canmove.float()
  entropy=dist.entropy()*canmove.float()
  # A candidate is a profession not found locally. Proposal is independent
  # of any global state or catalogue ranking.
  new=torch.randint(c.m,(b,n),device=c.device)
  for _ in range(4):
   occupied=loc.gather(2,new[...,None]).squeeze(2)>0
   failed=occupied|(new==e.jobs)
   new=torch.where(failed,torch.randint(c.m,(b,n),device=c.device),new)
  if self.rounds>0 and not disable_messages:
   key=torch.where(pledge,torch.rand((b,n),device=c.device),
                   torch.full((b,n),float('inf'),device=c.device))
   target=new.clone()
   for _ in range(self.rounds):
    nkey=key[:,e.adj]
    offers=target[:,e.adj]
    # If alter_messages, each actor receives independently randomized
    # senders (preserves marginal offer contents but breaks spatial links).
    if alter_messages:
     sel=torch.randint(n,(b,n,c.degree),device=c.device)
     nkey=key.gather(1,sel.reshape(b,-1)).reshape(b,n,c.degree)
     offers=target.gather(1,sel.reshape(b,-1)).reshape(b,n,c.degree)
    table=torch.cat([key[...,None],nkey],dim=-1)
    which=table.argmin(-1,keepdim=True)
    candidates=torch.cat([target[...,None],offers],dim=-1)
    key=table.gather(2,which).squeeze(2)
    target=candidates.gather(2,which).squeeze(2)
   # Do not allow messages themselves to become artificial reward.
   new=target
   if self.scramble:
    # Strong counterfactual: unlink each receiver's message to
    # the consensus by swapping proposed labels among individual actors.
    index=torch.randint(n,(b,n),device=c.device)
    new=target.gather(1,index)
   if self.quorum:
    # Reconstruct R-hop reachable population from neighborhood identities.
    # Only intended pledges are counted; occupations are not counted.
    adj=e.adj
    if self._cached_reach is not None and c.topology=='ring':
     reach=self._cached_reach
    else:
     reach=torch.eye(n,device=c.device,dtype=torch.bool)
     for _ in range(self.rounds):reach=reach|reach[adj].any(1)
     if c.topology=='ring':self._cached_reach=reach
    match=new[:,:,None]==new[:,None,:]
    heard=(reach[None,:,:]&match&pledge[:,None,:]).sum(-1)
    # Strict improvement at originally empty role: d/q > own current food.
    pledge &=heard>(q*r)
  elif self.quorum:
   # Without messages, each agent only knows its own pledge.
   pledge &=1>(q*r)
  self.prevjob=e.jobs.detach().clone()
  jobs=torch.where(pledge,new,e.jobs)
  return jobs,logp,entropy

def parse():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--n',type=int,default=120)
 p.add_argument('--h',type=int,default=16)
 p.add_argument('--rounds',type=int,default=8)
 p.add_argument('--quorum',action='store_true')
 p.add_argument('--scramble',action='store_true')
 p.add_argument('--gate',action='store_true')
 p.add_argument('--features',choices=['raw','local','lattice','oracle'],default='lattice')
 p.add_argument('--updates',type=int,default=800)
 p.add_argument('--batch',type=int,default=12)
 p.add_argument('--horizon',type=int,default=12)
 p.add_argument('--lr',type=float,default=.006)
 p.add_argument('--entropy',type=float,default=.005)
 p.add_argument('--gamma',type=float,default=.97)
 p.add_argument('--seed',type=int,default=3111)
 p.add_argument('--device',choices=['cpu','cuda'],default='cuda')
 p.add_argument('--topology',choices=['ring','rewired'],default='ring')
 p.add_argument('--degree',type=int,default=8)
 p.add_argument('--init',choices=['random','trap','mix'],default='mix')
 p.add_argument('--eval-every',type=int,default=100)
 p.add_argument('--save-every',type=int,default=100)
 return p.parse_args()

PAIRS=[(50,4),(80,12),(24,4),(80,30),(80,60),(50,2),(80,6),(80,10)]
EVAL=[('trap_M50_k4',50,4,'trap'),('random_M50_k4',50,4,'random'),
      ('trap_M80_k12',80,12,'trap'),('unseen_M72_k8',72,8,'random'),
      ('unseen_M40_k5',40,5,'random')]

def main(args):
 torch.set_num_threads(min(4,os.cpu_count() or 2))
 base=envlib.Config(n=args.n,m=50,k=4,degree=args.degree,topology=args.topology,
    batch=args.batch,horizon=args.horizon,device=args.device,
    lr=args.lr,entropy=args.entropy,gamma=args.gamma,alpha=0.,
    communication=False,blind=False,public=False)
 out=HERE/'runs'/args.name
 out.mkdir(parents=True,exist_ok=True)
 spec={**vars(args),'pairs':PAIRS,'evaluations':EVAL,
       'model':'private neural conditional quorum with two-phase signaling',
       'policy_reward':'own realized food only',
       'global_counts_as_input':args.features=='oracle'}
 contract=out/'spec.json'
 if contract.exists() and json.loads(contract.read_text('utf8'))!=spec:
  raise ValueError('Cannot resume with different experiment parameters')
 envlib.write_json(contract,spec)
 torch.manual_seed(args.seed)
 net=PledgeActor(args.n,args.h,args.rounds,args.quorum,args.features,args.scramble,args.gate).to(args.device)
 opt=torch.optim.Adam(net.parameters(),lr=args.lr)
 print('PLEDGE_MODEL',args.name,'params_per_agent',
       sum(x.numel() for x in net.parameters())//args.n,
       'rounds',args.rounds,'features',args.features,
       'true_message',not args.scramble,
       'privileged',args.features=='oracle',flush=True)
 ck=out/'latest.pt';start=0
 if ck.exists():
  z=torch.load(ck,map_location=args.device,weights_only=False)
  net.load_state_dict(z['model']);opt.load_state_dict(z['optimizer']);start=int(z['update'])
 def eval_all():
  result={}
  for tag,m,k,init in EVAL:
   cc=replace(base,m=m,k=k,init=init,batch=24,horizon=20)
   x=envlib.evaluate(net,cc,771111+109*m+13*k,batch=24,horizon=20)['final']
   result[tag]=x
  return result
 if not (out/'history.jsonl').exists():
  with torch.no_grad():
   x=eval_all()
  print('PLEDGE_INITIAL',args.name,
     {k:round(v['food'],4) for k,v in x.items()},flush=True)
 def save(update):
  tmp=out/'latest.temp'
  torch.save(dict(update=update,model=net.state_dict(),optimizer=opt.state_dict()),tmp)
  os.replace(tmp,ck)
  if update%500==0 or update==args.updates:
   torch.save(dict(update=update,model=net.state_dict(),optimizer=opt.state_dict()),
       out/f'checkpoint_{update:06d}.pt')
 started=time.perf_counter()
 for u in range(start+1,args.updates+1):
  m,k=PAIRS[(u-1)%len(PAIRS)]
  init='trap' if args.init=='mix' and (u%2==0) else (
       'random' if args.init=='mix' else args.init)
  cc=replace(base,m=m,k=k,init=init)
  tr=envlib.train_step(net,opt,cc,args.seed+u*977)
  if u==1 or u%args.eval_every==0 or u==args.updates:
   with torch.no_grad():scores=eval_all()
   row=dict(update=u,train=dict(init=init,m=m,k=k,**tr),results=scores,
      time_seconds=round(time.perf_counter()-started,2))
   with (out/'history.jsonl').open('a',encoding='utf8') as fh:
    fh.write(json.dumps(row,ensure_ascii=False)+'\n')
   envlib.write_json(out/'status.json',dict(state='training',**row))
   print('PLEDGE_METRIC',args.name,u,'train',round(tr['food'],4),
     'trap',round(scores['trap_M50_k4']['food'],4),
     'trap_exact',scores['trap_M50_k4']['exact'],
     'novel',round(scores['unseen_M72_k8']['food'],4),flush=True)
  if u%args.save_every==0 or u==args.updates:save(u)
 envlib.write_json(out/'status.json',dict(state='completed',
    last_update=args.updates,last_results=scores))
 print('PLEDGE_TRAIN_DONE',args.name,args.updates,flush=True)
if __name__=='__main__':main(parse())
