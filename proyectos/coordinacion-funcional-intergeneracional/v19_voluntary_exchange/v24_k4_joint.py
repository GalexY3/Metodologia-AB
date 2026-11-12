"""V24 exploratory k=4 extension of V23 cold simultaneous learning.

Private actors choose among k occupations and give targeted costly donations.
No quota, shared policy, normative role target, imitation or pooled reward.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from torch import nn
from torch.distributions import Categorical
from targeted_gifts import C,PrivateGiftActor,create,step
from v23_joint_cold import gradients_per_agent,cost_at
ROOT=Path(__file__).resolve().parent

class PrivateOccupationK(nn.Module):
 def __init__(self,n,k,hidden=20):
  super().__init__()
  self.n=n;self.k=k
  self.W=nn.Parameter(torch.randn(n,3*k+6,hidden)*.075)
  self.b=nn.Parameter(torch.zeros(n,hidden))
  self.V=nn.Parameter(torch.randn(n,hidden,k)*.075)
  self.bias=nn.Parameter(torch.zeros(n,k))
 def act(self,c,w,greedy=False,history=True):
  roles=w["roles"]
  graph=w["graph"]
  neighbor=roles[:,graph]
  onehot=torch.nn.functional.one_hot(neighbor,c.k).float()
  counts=onehot.mean(2)
  public=(onehot*w["prev_gift"][:,graph][...,None]).mean(2)
  own=torch.nn.functional.one_hot(roles,c.k).float()
  own_last=w["lastfood"]
  own_prev=w["prev_gift"]
  prior_help=w["trust"].mean(2)
  if not history:
   public=public*0
   own_prev=own_prev*0
   prior_help=prior_help*0
  scalars=torch.stack((own_last,own_prev,prior_help,
              w["last_switch"],torch.full_like(own_last,w["t"]/c.horizon),
              w["cover"]),dim=2)
  f=torch.cat((counts,public,own,scalars),dim=2)
  assert f.shape[-1]==self.W.shape[1]
  h=torch.tanh(torch.einsum("bnf,nfh->bnh",f,self.W)+self.b[None,:,:])
  logits=torch.einsum("bnh,nhk->bnk",h,self.V)+self.bias[None,:,:]
  dist=Categorical(logits=logits)
  selected=logits.argmax(2) if greedy else dist.sample()
  return selected,dist.log_prob(selected),dist.entropy()

def start4(c,seed,init="mixed"):
 w=create(c,seed)
 gen=torch.Generator(device=c.device);gen.manual_seed(seed+1661007)
 mono=torch.randint(c.k,(c.batch,1),device=c.device,generator=gen)
 random=torch.randint(c.k,(c.batch,c.n),device=c.device,generator=gen)
 if init=="mixed":
  roles=torch.where((torch.arange(c.batch,device=c.device)%2==0)[:,None],
     mono,random)
 elif init=="monolith":roles=mono.expand(c.batch,c.n).clone()
 elif init=="random":roles=random
 elif init=="balanced":roles=w["roles"]
 else:raise ValueError(init)
 w["roles"]=roles
 w["last_switch"]=torch.zeros(c.batch,c.n,device=c.device)
 return w

def adjacent_potential(c,w):
 neighbor=w["roles"][:,w["graph"]]
 types=torch.nn.functional.one_hot(neighbor,c.k).bool().any(2)
 own=torch.nn.functional.one_hot(w["roles"],c.k).bool()
 return float(((types&~own).float().sum(2)/(c.k-1)).mean())

def roll(c,donor,role,seed,init="mixed",interval=8,
         move_cost=.015,social=True,baseline=None):
 w=start4(c,seed,init)
 rlist=[];g_log=[];g_ent=[];r_log=[];r_ent=[];role_times=[]
 gifts=[];switched=[];full=[];cov=[];potential=[]
 for t in range(c.horizon):
  if t%interval==0:
   if baseline=="fixed":
    destrole=w["roles"];lp=ent=None
   elif baseline is not None and baseline.startswith("random_"):
    pr=float(baseline.split("_",1)[1])
    choose=(torch.rand(c.batch,c.n,device=c.device)<pr)
    candidate=torch.randint(c.k,(c.batch,c.n),device=c.device)
    destrole=torch.where(choose,candidate,w["roles"]);lp=ent=None
   else:
    destrole,lp,ent=role.act(c,w,history=social)
   change=(destrole!=w["roles"]).float()
   w["roles"]=destrole
   w["last_switch"]=change
   switched.append(change)
   if lp is not None:
    role_times.append(t);r_log.append(lp);r_ent.append(ent)
  dest,gift,lp,ent=donor.act(c,w,mode=("normal" if social else "no_social"))
  r=step(c,w,dest,gift)
  if t%interval==0:
   r=r-move_cost*change;w["lastfood"]=r
  gifts.append(gift.mean().detach())
  g_log.append(lp);g_ent.append(ent)
  cov.append(w["cover"].mean().detach())
  full.append(w["full"].mean().detach())
  if t==c.horizon-1:potential.append(adjacent_potential(c,w))
  rlist.append(r)
 end_counts=torch.nn.functional.one_hot(w["roles"],c.k).float().sum(1)
 balanced=(end_counts==c.n/c.k).all(1).float().mean()
 metrics=dict(food=float(torch.stack(rlist).mean()),
   last_food=float(rlist[-1].mean()),gift=float(torch.stack(gifts).mean()),
   coverage=float(torch.stack(cov).mean()),full=float(torch.stack(full).mean()),
   potential_coverage=potential[0],balanced=float(balanced),
   nonempty_professions=float((end_counts>0).float().sum(1).mean()),
   switches=float(torch.stack(switched).sum(0).mean()))
 return metrics,torch.stack(rlist),g_log,g_ent,r_log,r_ent,role_times

@torch.no_grad()
def evaluate(donor,role,a,seed=981881,worlds=12):
 result=[]
 for topology,degree in (("ring",6),("rewired",6)):
  for init in ("monolith","random","balanced"):
   for cond in ("normal","no_history","fixed"):
    c=C(n=a.n,k=a.k,degree=degree,topology=topology,batch=worlds,
        horizon=a.horizon,device=a.device,cost=a.cost,gamma=a.gamma)
    torch.manual_seed(seed+degree*71+(topology=="rewired")*127+
       {"monolith":1,"random":2,"balanced":3}[init])
    m,*_=roll(c,donor,role,seed+degree*71+(topology=="rewired")*127+
       {"monolith":1,"random":2,"balanced":3}[init],init=init,
       interval=a.role_interval,move_cost=a.move_cost,
       social=cond!="no_history",baseline=("fixed" if cond=="fixed" else None))
    result.append(dict(topology=topology,degree=degree,init=init,
      condition=cond,**m))
 return result

def parser():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--seed",type=int,required=True)
 p.add_argument("--n",type=int,default=48)
 p.add_argument("--k",type=int,default=4)
 p.add_argument("--updates",type=int,default=800)
 p.add_argument("--transition",type=int,default=500)
 p.add_argument("--batch",type=int,default=12)
 p.add_argument("--horizon",type=int,default=48)
 p.add_argument("--degree",type=int,default=6)
 p.add_argument("--hidden",type=int,default=20)
 p.add_argument("--init-scale",type=float,default=8)
 p.add_argument("--cost",type=float,default=.12)
 p.add_argument("--low-cost",type=float,default=.01)
 p.add_argument("--schedule",choices=("smooth","constant"),default="smooth")
 p.add_argument("--role-interval",type=int,default=8)
 p.add_argument("--move-cost",type=float,default=.015)
 p.add_argument("--gamma",type=float,default=.995)
 p.add_argument("--lr-gift",type=float,default=.002)
 p.add_argument("--lr-role",type=float,default=.003)
 p.add_argument("--ent-gift",type=float,default=.015)
 p.add_argument("--ent-role",type=float,default=.01)
 p.add_argument("--eval-every",type=int,default=200)
 p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
 return p

def main():
 a=parser().parse_args()
 assert a.k==4 and a.n%a.k==0 and a.n>a.degree and a.degree%2==0
 assert a.horizon%a.role_interval==0 and a.batch>=2
 torch.set_num_threads(2);torch.manual_seed(a.seed);np.random.seed(a.seed)
 folder=ROOT/"runs"/a.name;folder.mkdir(parents=True,exist_ok=False)
 (folder/"v24_spec.json").write_text(json.dumps(vars(a),indent=2),encoding="utf8")
 gift=PrivateGiftActor(a.n,a.hidden,a.init_scale).to(a.device)
 role=PrivateOccupationK(a.n,a.k,a.hidden).to(a.device)
 og=torch.optim.Adam(gift.parameters(),lr=a.lr_gift)
 orole=torch.optim.Adam(role.parameters(),lr=a.lr_role)
 t0=time.perf_counter()
 for u in range(1,a.updates+1):
  cost=cost_at(a,u)
  c=C(n=a.n,k=a.k,degree=a.degree,topology="ring",
       batch=a.batch,horizon=a.horizon,cost=cost,gamma=a.gamma,device=a.device)
  m,rewards,gl,ge,rl,re,rt=roll(c,gift,role,a.seed*19301+u*31,
       init="mixed",interval=a.role_interval,move_cost=a.move_cost)
  ret=[];g=torch.zeros_like(rewards[0])
  for x in reversed(rewards):
   g=x+a.gamma*g;ret.append(g)
  R=torch.stack(ret[::-1])
  leave=(R.sum(1,keepdim=True)-R)/(a.batch-1)
  advantage=((R-leave)/R.std(1,unbiased=False,keepdim=True).clamp_min(.25)).detach()
  Lg=-(torch.stack(gl)*advantage).mean()-a.ent_gift*torch.stack(ge).mean()
  Lr=-(torch.stack(rl)*advantage[rt]).mean()-a.ent_role*torch.stack(re).mean()
  og.zero_grad(set_to_none=True);orole.zero_grad(set_to_none=True)
  (Lg+Lr).backward()
  gradients_per_agent(gift,a.n);gradients_per_agent(role,a.n)
  og.step();orole.step()
  if u==1 or u%a.eval_every==0 or u==a.updates:
   oldcpu=torch.get_rng_state()
   oldgpu=torch.cuda.get_rng_state() if a.device=="cuda" else None
   with torch.no_grad():v=evaluate(gift,role,a)
   torch.set_rng_state(oldcpu)
   if oldgpu is not None:torch.cuda.set_rng_state(oldgpu)
   record=dict(update=u,cost=cost,train=m,development=v,
      loss_gift=float(Lg.detach()),loss_role=float(Lr.detach()),
      elapsed_seconds=time.perf_counter()-t0)
   with (folder/"v24_history.jsonl").open("a",encoding="utf8") as fh:
    fh.write(json.dumps(record)+"\n")
   state=dict(gift=gift.state_dict(),role=role.state_dict(),
       optimizer_gift=og.state_dict(),optimizer_role=orole.state_dict(),
       update=u,rng_cpu=torch.get_rng_state(),
       rng_gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None)
   tmp=folder/"joint_tmp.pt";torch.save(state,tmp)
   os.replace(tmp,folder/"joint_latest.pt")
   target=next(x for x in v if x["topology"]=="ring" and x["init"]=="monolith"
            and x["condition"]=="normal")
   print("V24",a.name,"u",u,"COST",round(cost,3),
      "FOOD",round(target["food"],4),
      "GIFT",round(target["gift"],4),
      "COVER",round(target["coverage"],4),
      "POTENTIAL",round(target["potential_coverage"],4),
      "FULL",round(target["full"],4),
      "BALANCED",round(target["balanced"],4),
      "elapsed",round(time.perf_counter()-t0,1),flush=True)
 (folder/"v24_status.json").write_text(json.dumps(
   dict(state="completed",updates=a.updates,
       elapsed_seconds=time.perf_counter()-t0)),encoding="utf8")
 print("V24_FINISHED",a.name,flush=True)
if __name__=="__main__":main()
