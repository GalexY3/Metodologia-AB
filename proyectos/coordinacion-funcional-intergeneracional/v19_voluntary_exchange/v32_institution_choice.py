"""V32: individuals jointly learn professions, recipients and institutional mode.

Institution is AVAILABLE in the game but NOT imposed on individuals.
Every individual independently chooses unilateral costly gifts or mutual
voluntary contracts at each round. No group reward, quota or expert.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from torch import nn
from torch.distributions import Bernoulli
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK,start4,adjacent_potential
from v23_joint_cold import gradients_per_agent

ROOT=Path(__file__).resolve().parent

class PrivateInstitutionActor(nn.Module):
 def __init__(self,n,k,hidden=20,initial_bias=0.):
  super().__init__()
  self.n=n;self.k=k
  self.W=nn.Parameter(torch.randn(n,3*k+6,hidden)*.075)
  self.b=nn.Parameter(torch.zeros(n,hidden))
  self.v=nn.Parameter(torch.randn(n,hidden)*.075)
  self.bias=nn.Parameter(torch.full((n,),float(initial_bias)))
 def act(self,c,w,greedy=False,social=True):
  graph=w['graph']
  roles=w['roles']
  neighbors=torch.nn.functional.one_hot(roles[:,graph],c.k).float()
  counts=neighbors.mean(2)
  public=(neighbors*w['prev_gift'][:,graph][...,None]).mean(2)
  own=torch.nn.functional.one_hot(roles,c.k).float()
  ownprev=w['prev_gift']
  past_help=w['trust'].mean(2)
  if not social:
   public=public*0;past_help=past_help*0
  scalar=torch.stack((w['lastfood'],ownprev,past_help,
      w['last_switch'],torch.full_like(ownprev,w['t']/c.horizon),
      w['cover']),2)
  features=torch.cat([counts,public,own,scalar],2)
  h=torch.tanh(torch.einsum('bnf,nfh->bnh',features,self.W)+self.b[None,:,:])
  logit=torch.einsum('bnh,nh->bn',h,self.v)+self.bias[None,:]
  dist=Bernoulli(logits=logit)
  selected=(logit>0).float() if greedy else dist.sample()
  return selected,dist.log_prob(selected),dist.entropy()

def hybrid_step(c,w,dests,offers,mode):
 """Settlement of 3 proposals: unilateral or mutual-only per origin."""
 b,n,slots=dests.shape
 assert offers.shape==(b,n,slots) and mode.shape==(b,n)
 assert slots==c.k-1
 u=offers*(1-mode[:,:,None])
 v=offers*mode[:,:,None]
 unilateral=torch.zeros(b,n,n,device=c.device,dtype=torch.float32)
 unilateral.scatter_add_(2,dests,u)
 conditional=torch.zeros_like(unilateral)
 conditional.scatter_add_(2,dests,v)
 conditional=conditional>0
 bilateral=(conditional&conditional.transpose(1,2)).float()
 delivered=unilateral+bilateral
 sent=delivered.sum(2)
 graph=w['graph']
 incoming=delivered.transpose(1,2).gather(
       2,graph[None,:,:].expand(b,-1,-1))
 goods=(torch.nn.functional.one_hot(w['roles'][:,graph],c.k).float()
             *incoming[:,:,:,None]).sum(2)>0
 own=torch.nn.functional.one_hot(w['roles'],c.k).bool()
 distinct=(goods&(~own)).float().sum(2)
 cover=distinct/(c.k-1)
 full=(distinct>=c.k-1).float()
 food=.20+.55*cover+.25*full-c.cost*sent
 w['incoming']=(incoming>0).float()
 w['trust']=torch.maximum(w['incoming'],c.memory_decay*w['trust'])
 w['prev_gift']=(sent>0).float()
 w['prev_recipient']=dests[:,:,0]
 w['lastfood']=food
 w['cover']=cover
 w['full']=full
 w['t']+=1
 return food,dict(proposals=float(offers.sum().detach()),
    delivered=float(sent.sum().detach()),
    bilateral=float(bilateral.sum().detach()),
    distinct=float(distinct.sum().detach()))

def roll(c,gift,role,institution,seed,init='mixed',interval=8,
         move_cost=.015,mode_override=None,social=True,
         role_baseline=None,gift_blocked=False):
 w=start4(c,seed,init)
 rews=[];lg=[];eg=[];lr=[];er=[];rt=[];lm=[];em=[]
 sums=dict(proposals=0.,delivered=0.,bilateral=0.,distinct=0.)
 adoption=[];movement=[];lastfood=[]
 for t in range(c.horizon):
  if t%interval==0:
   if role_baseline=="fixed":
    newrole=w['roles'];lprole=erole=None
   elif role_baseline is not None and role_baseline.startswith('random_'):
    p=float(role_baseline.split('_',1)[1])
    replacement=torch.randint(c.k,(c.batch,c.n),device=c.device)
    newrole=torch.where(torch.rand(c.batch,c.n,device=c.device)<p,
               replacement,w['roles'])
    lprole=erole=None
   else:
    newrole,lprole,erole=role.act(c,w,history=social)
   changed=(newrole!=w['roles']).float()
   w['roles']=newrole
   w['last_switch']=changed
   movement.append(changed)
   if lprole is not None:
    lr.append(lprole);er.append(erole);rt.append(t)
  if mode_override in ('unilateral','mutual','random'):
   if mode_override=='unilateral':m=torch.zeros(c.batch,c.n,device=c.device)
   elif mode_override=='mutual':m=torch.ones(c.batch,c.n,device=c.device)
   else:m=(torch.rand(c.batch,c.n,device=c.device)<.5).float()
   lmode=emode=None
  else:
   m,lmode,emode=institution.act(c,w,social=social)
  adoption.append(m.mean().detach())
  if lmode is not None:
   lm.append(lmode);em.append(emode)
  actions=[gift.act(c,w,mode=('normal' if social else 'no_social'))
      for _ in range(c.k-1)]
  dests=torch.stack([z[0] for z in actions],2)
  offers=torch.stack([z[1] for z in actions],2)
  if gift_blocked:offers=torch.zeros_like(offers)
  lp=torch.stack([z[2] for z in actions]).sum(0)
  ent=torch.stack([z[3] for z in actions]).sum(0)
  reward,vals=hybrid_step(c,w,dests,offers,m)
  for k in sums:sums[k]+=vals[k]
  if t%interval==0:
   reward=reward-move_cost*changed
   w['lastfood']=reward
  rews.append(reward)
  lastfood.append(reward.mean().detach())
  lg.append(lp);eg.append(ent)
 counts=torch.nn.functional.one_hot(w['roles'],c.k).float().sum(1)
 denominator=c.batch*c.n*c.horizon
 metric=dict(food=float(torch.stack(lastfood).mean()),
     last_food=float(rews[-1].mean()),
     adoption=float(torch.stack(adoption).mean()),
     proposals_per_agent=sums['proposals']/denominator,
     transfers_per_agent=sums['delivered']/denominator,
     matched_contracts_per_agent=sums['bilateral']/denominator,
     realized_coverage=sums['distinct']/(denominator*(c.k-1)),
     useful_fraction=(sums['distinct']/sums['delivered']
        if sums['delivered']>0 else 0),
     potential_coverage=adjacent_potential(c,w),
     balanced=float((counts==c.n/c.k).all(1).float().mean()),
     nonempty_professions=float((counts>0).float().sum(1).mean()),
     switches=float(torch.stack(movement).sum(0).mean()))
 return metric,torch.stack(rews),lg,eg,lr,er,rt,lm,em

@torch.no_grad()
def evaluate(gift,role,inst,a,seed=132118,worlds=12):
 results=[]
 for topology,init in (('ring','monolith'),('ring','random'),
                       ('rewired','monolith')):
  for mode in (None,'unilateral','mutual','random'):
   c=C(n=a.n,k=4,degree=6,topology=topology,batch=worlds,
       horizon=a.horizon,cost=a.cost,gamma=a.gamma,device=a.device)
   rndseed=seed+(topology=='rewired')*779+(init=='random')*191
   torch.manual_seed(rndseed*59)
   m,*_=roll(c,gift,role,inst,rndseed,init=init,
      interval=a.role_interval,move_cost=a.move_cost,
      mode_override=mode)
   results.append(dict(topology=topology,init=init,
        condition=('learned' if mode is None else mode),**m))
 return results

def cli():
 p=argparse.ArgumentParser()
 p.add_argument('--name',required=True)
 p.add_argument('--seed',type=int,required=True)
 p.add_argument('--mode-bias',type=float,choices=(0.,-2.),required=True)
 p.add_argument('--n',type=int,default=48)
 p.add_argument('--k',type=int,default=4)
 p.add_argument('--updates',type=int,default=1000)
 p.add_argument('--batch',type=int,default=12)
 p.add_argument('--horizon',type=int,default=48)
 p.add_argument('--cost',type=float,default=.04)
 p.add_argument('--low-cost',type=float,default=.002)
 p.add_argument('--flat',type=int,default=400)
 p.add_argument('--rise',type=int,default=250)
 p.add_argument('--hidden',type=int,default=20)
 p.add_argument('--init-scale',type=float,default=8.)
 p.add_argument('--role-interval',type=int,default=8)
 p.add_argument('--move-cost',type=float,default=.015)
 p.add_argument('--gamma',type=float,default=.995)
 p.add_argument('--lr-gift',type=float,default=.002)
 p.add_argument('--lr-role',type=float,default=.003)
 p.add_argument('--lr-mode',type=float,default=.003)
 p.add_argument('--ent-gift',type=float,default=.015)
 p.add_argument('--ent-role',type=float,default=.01)
 p.add_argument('--ent-mode',type=float,default=.01)
 p.add_argument('--eval-every',type=int,default=200)
 p.add_argument('--device',choices=('cuda','cpu'),default='cuda')
 return p

def cost_at(a,u):
 if u<=a.flat:return a.low_cost
 return a.low_cost+(a.cost-a.low_cost)*min(1.,(u-a.flat)/a.rise)

def main():
 a=cli().parse_args()
 assert a.n%a.k==0 and a.k==4 and a.updates>=a.flat+a.rise
 assert a.horizon%a.role_interval==0 and a.batch>=2
 torch.set_num_threads(2)
 torch.manual_seed(a.seed);np.random.seed(a.seed)
 folder=ROOT/'runs'/a.name
 folder.mkdir(parents=True,exist_ok=False)
 (folder/'v32_spec.json').write_text(json.dumps(vars(a),indent=2),encoding='utf8')
 gift=PrivateGiftActor(a.n,a.hidden,a.init_scale).to(a.device)
 role=PrivateOccupationK(a.n,a.k,a.hidden).to(a.device)
 inst=PrivateInstitutionActor(a.n,a.k,a.hidden,a.mode_bias).to(a.device)
 og=torch.optim.Adam(gift.parameters(),lr=a.lr_gift)
 orole=torch.optim.Adam(role.parameters(),lr=a.lr_role)
 om=torch.optim.Adam(inst.parameters(),lr=a.lr_mode)
 t0=time.perf_counter()
 for update in range(1,a.updates+1):
  price=cost_at(a,update)
  c=C(n=a.n,k=4,degree=6,topology='ring',batch=a.batch,
      horizon=a.horizon,cost=price,gamma=a.gamma,device=a.device)
  m,rewards,lg,eg,lr,er,rt,lm,em=roll(c,gift,role,inst,
      a.seed*19301+31*update,init='mixed',
      interval=a.role_interval,move_cost=a.move_cost)
  G=torch.zeros_like(rewards[0]);ret=[]
  for x in reversed(rewards):
   G=x+a.gamma*G;ret.append(G)
  returns=torch.stack(ret[::-1])
  base=(returns.sum(1,keepdim=True)-returns)/(a.batch-1)
  adv=((returns-base)/returns.std(1,unbiased=False,
       keepdim=True).clamp_min(.25)).detach()
  gift_loss=-(torch.stack(lg)*adv).mean()-a.ent_gift*torch.stack(eg).mean()
  role_loss=-(torch.stack(lr)*adv[rt]).mean()-a.ent_role*torch.stack(er).mean()
  mode_loss=-(torch.stack(lm)*adv).mean()-a.ent_mode*torch.stack(em).mean()
  og.zero_grad(set_to_none=True);orole.zero_grad(set_to_none=True)
  om.zero_grad(set_to_none=True)
  (gift_loss+role_loss+mode_loss).backward()
  for actor in (gift,role,inst):gradients_per_agent(actor,a.n)
  og.step();orole.step();om.step()
  if update==1 or update%a.eval_every==0 or update==a.updates:
   rng=torch.get_rng_state()
   rnggpu=torch.cuda.get_rng_state() if a.device=='cuda' else None
   with torch.no_grad():test=evaluate(gift,role,inst,a)
   torch.set_rng_state(rng)
   if rnggpu is not None:torch.cuda.set_rng_state(rnggpu)
   with (folder/'v32_history.jsonl').open('a',encoding='utf8') as f:
    f.write(json.dumps(dict(update=update,training_cost=price,
       train=m,development=test,elapsed=time.perf_counter()-t0,
       loss_gift=float(gift_loss.detach()),loss_role=float(role_loss.detach()),
       loss_mode=float(mode_loss.detach())))+'\n')
   temp=folder/'joint_tmp.pt'
   torch.save(dict(gift=gift.state_dict(),role=role.state_dict(),
      mode=inst.state_dict(),optimizer_gift=og.state_dict(),
      optimizer_role=orole.state_dict(),optimizer_mode=om.state_dict(),
      update=update,rng_cpu=torch.get_rng_state(),
      rng_gpu=torch.cuda.get_rng_state() if a.device=='cuda' else None),temp)
   os.replace(temp,folder/'joint_latest.pt')
   z=next(x for x in test if x['topology']=='ring' and
            x['init']=='monolith' and x['condition']=='learned')
   print('V32',a.name,'u',update,'COST',round(price,4),
     'FOOD',round(z['food'],4),'MODE_CONTRACT',round(z['adoption'],3),
     'UNITS',round(z['transfers_per_agent'],3),
     'FULL',round(z['realized_coverage'],3),
     'time',round(time.perf_counter()-t0,1),flush=True)
 (folder/'v32_status.json').write_text(json.dumps(dict(state='completed',
    updates=a.updates,elapsed_seconds=time.perf_counter()-t0)))
 print('V32_FINISHED',a.name,flush=True)
if __name__=='__main__':main()
