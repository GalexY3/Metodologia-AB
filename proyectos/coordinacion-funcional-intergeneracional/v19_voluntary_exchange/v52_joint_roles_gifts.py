"""V52 joint learning of independent private occupation and giving policies.

Same K4 material/social world as V51; gift logits now trainable. Two sources:
random actor from scratch or an imported V47 private opponent-aware donor.
Both components learn by own actual food-only REINFORCE.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from torch import nn
from torch.distributions import Bernoulli
from torch.nn import functional as F
from v51_endogenous_roles import (PrivateRoleActor,context,initial_roles,
 load_frozen_gifts,N,K,G,S,ROLE_COST,SWITCH_INTERVAL)
from v46_exact_opponent_shaping import B,V,C,GAMMA,H
ROOT=Path(__file__).resolve().parent

def rollout(c,gifts,roles_model,seed,init="mixed",role_baseline=None,
            forced=None,subjects=None,return_own=False):
 batch=c["batch"];device=c["device"]
 graph=c["neighbor"];rev=c["reverse"];tmax=c["horizon"]
 torch.manual_seed(seed*73+41)
 roles=initial_roles(seed,batch,init,device)
 lastfood=torch.full((batch,N),B,device=device)
 moved=torch.zeros(batch,N,device=device)
 own_last=torch.zeros(batch,N,S,dtype=torch.long,device=device)
 recv_last=torch.zeros_like(own_last)
 giftlogs=[];giftentropy=[];occupationlogs=[];occupentropy=[];occupation_times=[]
 rewards=[]
 total_food=total_gifts=total_full=total_cover=total_balance=total_switch=0.
 own_return=torch.zeros(batch,device=device) if return_own else None
 initial=None
 for t in range(tmax):
  if t%SWITCH_INTERVAL==0:
   if role_baseline=="fixed":
    next_roles=roles;rl=ren=None
   elif role_baseline is not None and role_baseline.startswith("random_"):
    rate=float(role_baseline.split("_",1)[1])
    trial=torch.randint(K,roles.shape,device=device)
    next_roles=torch.where(torch.rand(roles.shape,device=device)<rate,trial,roles)
    rl=ren=None
   else:
    next_roles,rl,ren=roles_model.sample(roles,graph,lastfood,moved,t)
   moved=(next_roles!=roles).float();roles=next_roles
   if rl is not None:
    occupationlogs.append(rl);occupentropy.append(ren);occupation_times.append(t)
  if t==0:
   selected=gifts[:,0][None,:,None].expand(batch,N,S)
  else:
   state=1+2*own_last+recv_last
   selected=gifts[torch.arange(N,device=device)[None,:,None],state]
  dist=Bernoulli(logits=selected)
  given=dist.sample().long()
  if t==0 and forced is not None:
   assert subjects is not None and subjects.shape==(batch,)
   given=given.clone()
   given[torch.arange(batch,device=device),subjects,0]=int(forced)
  logs=dist.log_prob(given.float()).sum(2)
  ent=dist.entropy().sum(2)
  recv=given[:,graph,rev]
  sender_role=roles[:,graph]
  source_coverage=((F.one_hot(sender_role,K).bool() & recv[...,None].bool()).any(2)
      & ~F.one_hot(roles,K).bool()).float().sum(2)
  completed=(source_coverage==3).float()
  cover=source_coverage/3.
  reward=B+.55*cover+.25*completed-C*given.float().sum(2)
  if t%SWITCH_INTERVAL==0:
   reward=reward-ROLE_COST*moved
   total_switch+=float(moved.sum().detach())
  lastfood=reward
  rewards.append(reward)
  giftlogs.append(logs);giftentropy.append(ent)
  total_food+=float(reward.mean().detach())
  total_gifts+=float(given.float().sum(2).mean().detach())
  total_full+=float(completed.mean().detach())
  total_cover+=float(cover.mean().detach())
  role_counts=F.one_hot(roles,K).view(batch,G,K,K).sum(2)
  balance=(role_counts==1).all(2).float()
  total_balance+=float(balance.mean().detach())
  if return_own:
   val=reward[torch.arange(batch,device=device),subjects]
   own_return+=GAMMA**t*val
   if t==0:initial=val.clone()
  own_last=given;recv_last=recv
 summary=dict(food=total_food/tmax,gifts=total_gifts/tmax,
  gift_slot_rate=total_gifts/(tmax*S),
  coverage=total_cover/tmax,full=total_full/tmax,
  balanced_teams=total_balance/tmax,
  role_switches_per_agent=total_switch/(batch*N),
  terminal_food=float(reward.mean().detach()),
  terminal_full=float(completed.mean().detach()),
  terminal_occupations=float(balance.mean().detach()))
 return (summary,torch.stack(rewards),torch.stack(giftlogs),
  torch.stack(giftentropy),occupationlogs,occupentropy,occupation_times,
  own_return,initial)

@torch.no_grad()
def development(donor,role,device,seed=194152):
 c=context(16,device)
 values=[]
 for init in ("monolith","random"):
  row,*_=rollout(c,donor,role,seed,init=init)
  values.append(dict(init=init,**row))
 return values

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--gift-seed",type=int,required=True)
 p.add_argument("--role-seed",type=int,required=True)
 p.add_argument("--source",choices=("scratch","prior"),required=True)
 p.add_argument("--updates",type=int,default=1500)
 p.add_argument("--batch",type=int,default=12)
 p.add_argument("--lr-gift",type=float,default=.003)
 p.add_argument("--lr-role",type=float,default=.003)
 p.add_argument("--ent-gift",type=float,default=.005)
 p.add_argument("--ent-role",type=float,default=.01)
 p.add_argument("--save-every",type=int,default=300)
 p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 a=p.parse_args()
 assert a.updates>=1 and a.batch>=2
 assert a.gift_seed in (3111,4111) and a.role_seed in (7111,8111)
 torch.set_num_threads(2)
 if a.source=="scratch":
  torch.manual_seed(a.gift_seed)
  gift=nn.Parameter(torch.randn(N,5,device=a.device)*.05)
 else:gift=nn.Parameter(load_frozen_gifts(
    f"v47_Q95_LOLA20_s{a.gift_seed}",a.device).detach().clone())
 torch.manual_seed(a.role_seed)
 profession=PrivateRoleActor().to(a.device)
 opt_g=torch.optim.Adam([gift],lr=a.lr_gift)
 opt_r=torch.optim.Adam(profession.parameters(),lr=a.lr_role)
 folder=ROOT/"runs"/a.name
 folder.mkdir(parents=True,exist_ok=False)
 spec=dict(vars(a),N=N,K=K,G=G,horizon=H,
  cost_gift=C,cost_role=ROLE_COST,discount=GAMMA,
  reward="private food only; no group reward or teacher",
  joint_training=True,source_prior=("V47-LOLA20" if a.source=="prior" else None))
 (folder/"v52_spec.json").write_text(json.dumps(spec,indent=2),encoding="utf8")
 c=context(a.batch,a.device)
 start=time.perf_counter()
 for u in range(1,a.updates+1):
  row,return_stream,lg,eg,lr,er,rt,*_=rollout(c,gift,profession,
    a.role_seed*19301+31*u,init="mixed")
  cum=torch.zeros_like(return_stream[0]);history=[]
  for reward in reversed(return_stream):
   cum=reward+GAMMA*cum;history.append(cum)
  returns=torch.stack(history[::-1])
  others=(returns.sum(1,keepdim=True)-returns)/(a.batch-1)
  advantage=((returns-others)/returns.std(1,unbiased=False,
   keepdim=True).clamp_min(.25)).detach()
  gl=-(lg*advantage).mean()-a.ent_gift*eg.mean()
  rl=-(torch.stack(lr)*advantage[rt]).mean()-a.ent_role*torch.stack(er).mean()
  opt_g.zero_grad(set_to_none=True);opt_r.zero_grad(set_to_none=True)
  (gl+rl).backward()
  opt_g.step();opt_r.step()
  if u==1 or u%a.save_every==0 or u==a.updates:
   rng=torch.get_rng_state()
   with torch.no_grad():evals=development(gift,profession,a.device)
   torch.set_rng_state(rng)
   result=dict(update=u,train=row,development=evals,
    elapsed=time.perf_counter()-start,
    loss_gift=float(gl.detach()),loss_role=float(rl.detach()))
   with (folder/"v52_history.jsonl").open("a",encoding="utf8") as out:
    out.write(json.dumps(result)+"\n")
   temp=folder/"checkpoint_tmp.pt"
   torch.save(dict(gift=gift.detach().cpu().clone(),
    role=profession.state_dict(),
    opt_gift=opt_g.state_dict(),opt_role=opt_r.state_dict(),
    update=u),temp)
   os.replace(temp,folder/"v52_latest.pt")
   m=next(x for x in evals if x["init"]=="monolith")
   print("V52",a.name,"u",u,"food",round(m["food"],4),
    "roles",round(m["terminal_occupations"],4),
    "gifts",round(m["gift_slot_rate"],4),
    "full",round(m["full"],4),
    "elapsed",round(result["elapsed"],1),flush=True)
 (folder/"v52_status.json").write_text(json.dumps(dict(
   state="completed",updates=a.updates,elapsed_seconds=time.perf_counter()-start)),encoding="utf8")
 print("V52_FINISHED",a.name,flush=True)
if __name__=="__main__":main()
