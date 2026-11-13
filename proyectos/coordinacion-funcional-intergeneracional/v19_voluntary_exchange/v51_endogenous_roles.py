"""V51 private independent occupation-learning on fixed K4 social teams.

Gift policies are frozen pretrained V47 individual Bernoulli logits.
Role actors are unshared, initialized from scratch, and trained by own
food only. No exogenous role quotas, social reward, or forced reciprocity.
"""
from __future__ import annotations
import argparse,copy,json,os,time
from pathlib import Path
import numpy as np,torch
from torch import nn
from torch.distributions import Categorical
from torch.nn import functional as F
from v46_exact_opponent_shaping import N,B,V,C,GAMMA,H
from v24_k4_joint import start4
ROOT=Path(__file__).resolve().parent
K=4;G=N//K;SWITCH_INTERVAL=8;ROLE_COST=.015;S=3

NEIGHBORS=np.zeros((N,S),dtype=np.int64)
for i in range(N):
 group=range(i//K*K, (i//K+1)*K)
 NEIGHBORS[i]=[j for j in group if j!=i]
REVERSE=np.zeros((N,S),dtype=np.int64)
for i in range(N):
 for s,j in enumerate(NEIGHBORS[i]):
  REVERSE[i,s]=list(NEIGHBORS[j]).index(i)
assert np.all(NEIGHBORS[NEIGHBORS,REVERSE]==np.arange(N)[:,None])

class PrivateRoleActor(nn.Module):
 def __init__(self,n=N,width=16):
  super().__init__()
  self.n=n;self.width=width
  self.w1=nn.Parameter(torch.randn(n,11,width)*.05)
  self.b1=nn.Parameter(torch.zeros(n,width))
  self.w2=nn.Parameter(torch.randn(n,width,K)*.05)
  self.b2=nn.Parameter(torch.zeros(n,K))
 def logits(self,roles,neighbor,food,prior_switch,t):
  own=F.one_hot(roles.long(),K).float()
  other=F.one_hot(roles[:,neighbor].long(),K).float().mean(2)
  info=torch.cat((own,other,food[...,None],
    torch.full_like(food[...,None],float(t)/H),prior_switch[...,None]),dim=2)
  assert info.shape==(len(roles),self.n,11)
  features=torch.tanh(torch.einsum("bnf,nfh->bnh",info,self.w1)+self.b1[None,:,:])
  return torch.einsum("bnh,nhk->bnk",features,self.w2)+self.b2[None,:,:]
 def sample(self,roles,neighbor,food,prior_switch,t):
  distribution=Categorical(logits=self.logits(roles,neighbor,food,prior_switch,t))
  selected=distribution.sample()
  return selected,distribution.log_prob(selected),distribution.entropy()

def load_frozen_gifts(source,device):
 checkpoint=torch.load(ROOT/"runs"/source/"v47_latest.pt",
    map_location="cpu",weights_only=False)
 assert checkpoint["update"]==1000 and "LOLA20" in source or (
    checkpoint["update"]==1000 and "_NL_" in source)
 values=checkpoint["logits"].to(device).detach()
 assert values.shape==(N,5)
 return values

def initial_roles(seed,batch,init,device):
 torch.manual_seed(seed*73+41)
 if init=="monolith":return torch.zeros(batch,N,dtype=torch.long,device=device)
 if init=="random":return torch.randint(K,(batch,N),dtype=torch.long,device=device)
 if init=="mixed":
  roles=torch.randint(K,(batch,N),dtype=torch.long,device=device)
  roles[::2]=0
  return roles
 raise ValueError(init)

def scenario(c,donor,occupational,seed,init="mixed",baseline=None,
             role_cost=ROLE_COST):
 """One episode; role actions sampled every 8 rounds, donor actions every round."""
 batch=c["batch"];device=c["device"]
 neighbor=c["neighbor"];reverse=c["reverse"]
 torch.manual_seed(seed*73+41)
 roles=initial_roles(seed,batch,init,device)
 food_prev=torch.full((batch,N),.20,device=device)
 prior_switch=torch.zeros(batch,N,device=device)
 gifts_prev=torch.zeros(batch,N,S,dtype=torch.long,device=device)
 received_prev=torch.zeros_like(gifts_prev)
 reward_list=[];logp=[];entropy=[];decision_steps=[]
 total_food=0.;total_sent=0.;total_full=0.;total_cover=0.;total_balanced=0.;total_sw=0.
 for t in range(c["horizon"]):
  if t%SWITCH_INTERVAL==0:
   if baseline=="fixed":
    nextrole=roles;lp=en=None
   elif baseline is not None and baseline.startswith("random_"):
    rate=float(baseline.split("_",1)[1])
    trial=torch.randint(K,roles.shape,device=device)
    nextrole=torch.where(torch.rand(roles.shape,device=device)<rate,trial,roles)
    lp=en=None
   else:
    nextrole,lp,en=occupational.sample(roles,neighbor,food_prev,prior_switch,t)
   changed=(nextrole!=roles).float()
   roles=nextrole;prior_switch=changed
   if lp is not None:
    logp.append(lp);entropy.append(en);decision_steps.append(t)
  if t==0:pj=torch.sigmoid(donor[:,0])[None,:,None].expand(batch,N,S)
  else:
   state=1+2*gifts_prev+received_prev
   pj=torch.sigmoid(donor)[torch.arange(N,device=device)[None,:,None],state]
  action=torch.bernoulli(pj).long()
  received=action[:,neighbor,reverse]
  sender_roles=roles[:,neighbor]
  distinct=((F.one_hot(sender_roles,K).bool()&received[...,None].bool()).any(2)
       & ~F.one_hot(roles,K).bool()).float().sum(2)
  full=(distinct==3).float()
  cover=distinct/3
  value=B+.55*cover+.25*full-C*action.float().sum(2)
  if t%SWITCH_INTERVAL==0:
   value=value-role_cost*prior_switch
   total_sw+=float(prior_switch.sum().detach())
  food_prev=value
  rewards=value
  reward_list.append(rewards)
  total_food+=float(rewards.mean().detach())
  total_sent+=float(action.float().sum(2).mean().detach())
  total_full+=float(full.mean().detach())
  total_cover+=float(cover.mean().detach())
  counts=F.one_hot(roles,K).view(batch,G,K,K).sum(2)
  total_balanced+=float((counts==1).all(2).float().mean().detach())
  gifts_prev=action
  received_prev=received
 return (dict(food=total_food/c["horizon"],gifts=total_sent/c["horizon"],
   full=total_full/c["horizon"],coverage=total_cover/c["horizon"],
   balanced_teams=total_balanced/c["horizon"],
   switches_per_person=total_sw/(batch*N),
   terminal_food=float(rewards.mean().detach()),
   terminal_full=float(full.mean().detach()),
   terminal_balanced_teams=float((counts==1).all(2).float().mean().detach())),
   torch.stack(reward_list),logp,entropy,decision_steps)

def context(batch,device,horizon=H):
 return dict(batch=batch,device=device,horizon=horizon,
  neighbor=torch.as_tensor(NEIGHBORS,device=device,dtype=torch.long),
  reverse=torch.as_tensor(REVERSE,device=device,dtype=torch.long))

@torch.no_grad()
def development(donor,role,device,seed=194151):
 c=context(16,device)
 outcome=[]
 for init in ("monolith","random"):
  stats,*_=scenario(c,donor,role,seed,init=init)
  outcome.append(dict(init=init,**stats))
 return outcome

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--source",required=True)
 p.add_argument("--role-seed",type=int,required=True)
 p.add_argument("--updates",type=int,default=1500)
 p.add_argument("--batch",type=int,default=12)
 p.add_argument("--lr",type=float,default=.003)
 p.add_argument("--ent",type=float,default=.01)
 p.add_argument("--save-every",type=int,default=300)
 p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 a=p.parse_args()
 assert a.updates>=1 and a.batch>=2
 torch.set_num_threads(2)
 donor=load_frozen_gifts(a.source,a.device)
 torch.manual_seed(a.role_seed)
 role=PrivateRoleActor().to(a.device)
 optimizer=torch.optim.Adam(role.parameters(),lr=a.lr)
 folder=ROOT/"runs"/a.name
 folder.mkdir(parents=True,exist_ok=False)
 spec=dict(vars(a),n=N,k=K,teams=G,team_size=K,
  source_gift_policy_frozen=True,initial_roles="mixed monolith/random",
  move_cost=ROLE_COST,role_decision_interval=SWITCH_INTERVAL,
  cost_each_gift=C,source_policy_type="V47 private exact opponent shaping")
 (folder/"v51_spec.json").write_text(json.dumps(spec,indent=2),encoding="utf8")
 config=context(a.batch,a.device)
 start=time.perf_counter()
 for u in range(1,a.updates+1):
  metrics,rewards,logs,entropies,times=scenario(config,donor,role,
   a.role_seed*19301+31*u,init="mixed")
  cumulative=torch.zeros_like(rewards[0]);values=[]
  for reward in reversed(rewards):
   cumulative=reward+GAMMA*cumulative
   values.append(cumulative)
  returns=torch.stack(values[::-1])
  baseline=(returns.sum(1,keepdim=True)-returns)/(a.batch-1)
  advantage=((returns-baseline)/returns.std(1,unbiased=False,
    keepdim=True).clamp_min(.25)).detach()
  loss=-(torch.stack(logs)*advantage[times]).mean()-a.ent*torch.stack(entropies).mean()
  optimizer.zero_grad(set_to_none=True)
  loss.backward()
  optimizer.step()
  if u==1 or u%a.save_every==0 or u==a.updates:
   rng=torch.get_rng_state()
   with torch.no_grad():evals=development(donor,role,a.device)
   torch.set_rng_state(rng)
   entry=dict(update=u,train=metrics,development=evals,
    loss=float(loss.detach()),elapsed=time.perf_counter()-start)
   with (folder/"v51_history.jsonl").open("a",encoding="utf8") as handle:
    handle.write(json.dumps(entry)+"\n")
   tmp=folder/"checkpoint_tmp.pt"
   torch.save(dict(actor=role.state_dict(),optimizer=optimizer.state_dict(),
    update=u),tmp)
   os.replace(tmp,folder/"v51_latest.pt")
   m=next(x for x in evals if x["init"]=="monolith")
   print("V51",a.name,"u",u,"food",round(m["food"],4),
    "complete",round(m["balanced_teams"],4),
    "coverage",round(m["full"],4),
    "gifts",round(m["gifts"],4),
    "elapsed",round(entry["elapsed"],1),flush=True)
 (folder/"v51_status.json").write_text(json.dumps(dict(
    state="completed",updates=a.updates,elapsed_seconds=time.perf_counter()-start)),encoding="utf8")
 print("V51_FINISHED",a.name,flush=True)

if __name__=="__main__":main()
