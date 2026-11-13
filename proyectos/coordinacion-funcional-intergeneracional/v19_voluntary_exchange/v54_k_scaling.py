"""V54: scale FREE individual role choice across k=2..12 at fixed N=120.

Occupational MLP parameters are private (first axis N). Frozen donation
strategies from V47 are resampled at the SAME identity slots across k.
Material payoff normalized to common optimum .88, including voluntary
gift costs; fixed production capacity is tested only in frozen holdouts.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from torch import nn
from torch.distributions import Categorical
from torch.nn import functional as F
ROOT=Path(__file__).resolve().parent
N=120;H=48;GAMMA=.995;BASE=.20;COST_TOTAL=.12
MOVE_COST=.015;SWITCH_INTERVAL=8
KS=(2,3,4,5,6,8,10,12)
METHODS=("LOLA20","NL")
TECHS=("ELASTIC","FIXED3","PER_LINK04")
CONTROLS=("learned","fixed","random_0.15","random_0.35",
 "random_0.60","oracle_roles")

def topology(k,device="cpu"):
 assert k in KS and N%k==0
 neighbor=np.asarray([[i//k*k+j for j in range(k) if j!=i%k] for i in range(N)])
 inverse=np.empty_like(neighbor)
 for i in range(N):
  for s,j in enumerate(neighbor[i]):
   inverse[i,s]=list(neighbor[j]).index(i)
 assert np.all(neighbor[neighbor,inverse]==np.arange(N)[:,None])
 return (torch.as_tensor(neighbor,dtype=torch.long,device=device),
  torch.as_tensor(inverse,dtype=torch.long,device=device))

class PrivateOccupationK(nn.Module):
 def __init__(self,k,n=N,width=24):
  super().__init__()
  self.k=k;self.n=n;self.width=width
  self.w1=nn.Parameter(torch.randn(n,2*k+3,width)*.05)
  self.b1=nn.Parameter(torch.zeros(n,width))
  self.w2=nn.Parameter(torch.randn(n,width,k)*.05)
  self.b2=nn.Parameter(torch.zeros(n,k))
 def logits(self,roles,neighbors,food,switched,t):
  nworld=len(roles)
  own=F.one_hot(roles,self.k).float()
  occ=F.one_hot(roles[:,neighbors],self.k).float().mean(2)
  data=torch.cat((own,occ,food[...,None],
    torch.full_like(food[...,None],t/H),switched[...,None]),dim=-1)
  assert data.shape==(nworld,self.n,2*self.k+3)
  h=torch.tanh(torch.einsum("bnf,nfh->bnh",data,self.w1)+self.b1)
  return torch.einsum("bnh,nhk->bnk",h,self.w2)+self.b2
 def act(self,roles,neighbors,food,switched,t):
  dist=Categorical(logits=self.logits(roles,neighbors,food,switched,t))
  action=dist.sample()
  return action,dist.log_prob(action),dist.entropy()

def donor_source(method,donor_seed,device="cpu"):
 assert method in METHODS and donor_seed in (3111,4111)
 name=f"v47_Q95_{method}_s{donor_seed}"
 ck=torch.load(ROOT/"runs"/name/"v47_latest.pt",
  map_location="cpu",weights_only=False)
 assert ck["update"]==1000
 source=ck["logits"].detach().float()
 assert source.shape==(48,5)
 # Fixed identity allocation independent of k, and identical mapping
 # for a given method and neuron seed.
 rng=np.random.default_rng(540091+donor_seed*17)
 mapping=np.tile(rng.permutation(48),3)[:N]
 return source[mapping].to(device).detach(),mapping.tolist()

def roles_initial(seed,batch,k,kind,device):
 if kind=="monolith":
  return torch.zeros((batch,N),dtype=torch.long,device=device)
 if kind=="random":
  return torch.randint(k,(batch,N),device=device)
 if kind=="mixed":
  result=torch.randint(k,(batch,N),device=device)
  result[::2]=0
  return result
 raise ValueError(kind)

def config(k,batch,device):
 neighbors,inverse=topology(k,device)
 return dict(k=k,batch=batch,device=device,neighbors=neighbors,inverse=inverse)

def take_received(action,neighbors,inverse):
 return action[:,neighbors,inverse]

def physical_return(roles,neighbor_roles,received,action,k,technology):
 covered=(F.one_hot(neighbor_roles,k).bool()&received[...,None].bool())
 distinct=(covered.any(dim=2)&(~F.one_hot(roles,k).bool())).float().sum(-1)
 complete=(distinct==(k-1)).float()
 coverage=distinct/(k-1)
 cost=(COST_TOTAL/(k-1) if technology=="ELASTIC" else .04)
 food=BASE+.55*coverage+.25*complete-cost*action.float().sum(-1)
 return food,coverage,complete

def apply_capacity(given,technology):
 if technology!="FIXED3" or given.shape[-1]<=3:return given
 # Select up to 3 offered recipients uniformly, with exogenous draw
 # already consumed by the same episode RNG; no invisible resource bonus.
 proposal=given.bool()
 scores=torch.rand(proposal.shape,device=given.device)
 scores=torch.where(proposal,scores,torch.full_like(scores,-1.))
 idx=scores.topk(3,dim=-1).indices
 kept=torch.zeros_like(proposal)
 kept.scatter_(-1,idx,True)
 return (proposal&kept).long()

def episode(c,donor,policy,seed,init="mixed",technology="ELASTIC",
  baseline="learned",collect_grad=True):
 k=c["k"];batch=c["batch"];device=c["device"];degree=k-1
 neighbor=c["neighbors"];inverse=c["inverse"]
 assert technology in TECHS and baseline in CONTROLS
 torch.manual_seed(seed*73+41)
 roles=roles_initial(seed,batch,k,init,device)
 prev_food=torch.full((batch,N),BASE,device=device)
 switched=torch.zeros((batch,N),device=device)
 ownlast=torch.zeros((batch,N,degree),dtype=torch.long,device=device)
 recvlast=torch.zeros_like(ownlast)
 reward_stream=[];role_logs=[];role_ent=[];role_times=[]
 sums=dict(food=0.,coverage=0.,full=0.,balanced=0.,gifts=0.,
  moves=0.)
 final={}
 for t in range(H):
  if t%SWITCH_INTERVAL==0:
   if baseline=="fixed":chosen=roles;lp=ent=None
   elif baseline=="oracle_roles":
    chosen=torch.arange(N,device=device)[None,:].expand(batch,N)%k
    lp=ent=None
   elif baseline.startswith("random_"):
    chance=float(baseline.split("_",1)[1])
    proposal=torch.randint(k,roles.shape,device=device)
    chosen=torch.where(torch.rand(roles.shape,device=device)<chance,proposal,roles)
    lp=ent=None
   else:
    chosen,lp,ent=policy.act(roles,neighbor,prev_food,switched,t)
   switched=(chosen!=roles).float()
   roles=chosen
   sums["moves"]+=float(switched.sum().detach())
   if lp is not None and collect_grad:
    role_logs.append(lp);role_ent.append(ent);role_times.append(t)
  if t==0:
   probability=torch.sigmoid(donor[:,0])[None,:,None].expand(batch,N,degree)
  else:
   state=1+2*ownlast+recvlast
   probability=torch.sigmoid(donor)[torch.arange(N,device=device)[None,:,None],state]
  gift=torch.bernoulli(probability).long()
  gift=apply_capacity(gift,technology)
  recv=take_received(gift,neighbor,inverse)
  neighbor_roles=roles[:,neighbor]
  food,coverage,complete=physical_return(roles,neighbor_roles,recv,gift,k,technology)
  if t%SWITCH_INTERVAL==0:
   food=food-MOVE_COST*switched
  reward_stream.append(food)
  prev_food=food
  # Group complete iff k different roles among k persons (one of each).
  role_counts=F.one_hot(roles,k).view(batch,N//k,k,k).sum(2)
  balanced=(role_counts==1).all(-1).float()
  sums["food"]+=float(food.mean().detach())
  sums["coverage"]+=float(coverage.mean().detach())
  sums["full"]+=float(complete.mean().detach())
  sums["balanced"]+=float(balanced.mean().detach())
  sums["gifts"]+=float(gift.float().sum(-1).mean().detach())
  if t==H-1:
   final=dict(terminal_food=float(food.mean().detach()),
    terminal_balance=float(balanced.mean().detach()),
    terminal_full=float(complete.mean().detach()))
  ownlast=gift;recvlast=recv
 metrics=dict(
  food=sums["food"]/H,
  coverage=sums["coverage"]/H,
  full=sums["full"]/H,
  group_complete=sums["balanced"]/H,
  gifts_per_person=sums["gifts"]/H,
  gifts_per_link=sums["gifts"]/(H*degree),
  move_per_person=sums["moves"]/(batch*N),
  **final)
 return metrics,torch.stack(reward_stream),role_logs,role_ent,role_times

@torch.no_grad()
def development(c,donor,actor,role_seed):
 out=[]
 for init in ("monolith","random"):
  metric,*_=episode(c,donor,actor,role_seed*29+540005,init=init)
  out.append(dict(init=init,**metric))
 return out

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--k",type=int,choices=KS,required=True)
 parser.add_argument("--method",choices=METHODS,required=True)
 parser.add_argument("--role-seed",type=int,choices=(7111,8111),required=True)
 parser.add_argument("--donor-seed",type=int,choices=(3111,4111),required=True)
 parser.add_argument("--name",required=True)
 parser.add_argument("--updates",type=int,default=1400)
 parser.add_argument("--batch",type=int,default=12)
 parser.add_argument("--lr",type=float,default=.003)
 parser.add_argument("--ent",type=float,default=.01)
 parser.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 parser.add_argument("--save-every",type=int,default=200)
 a=parser.parse_args()
 assert a.updates>0 and a.batch>=2
 torch.set_num_threads(2)
 donor,donor_map=donor_source(a.method,a.donor_seed,a.device)
 torch.manual_seed(a.role_seed)
 actor=PrivateOccupationK(a.k).to(a.device)
 optimizer=torch.optim.Adam(actor.parameters(),lr=a.lr)
 folder=ROOT/"runs"/a.name
 folder.mkdir(parents=True,exist_ok=False)
 spec=dict(vars(a),n=N,group_size=a.k,n_teams=N//a.k,horizon=H,
  degree=a.k-1,payoff_formula="BASE+.55*coverage+.25*full-[.12/(k-1)]*sent-.015*switch",
  donation_policy_frozen=True,role_policy_private=True,
  team_network_exogenous=True,profession_choices_unrestricted=True,
  donor_mapping=donor_map,donation_cost_total=COST_TOTAL,
  normalization="ELASTIC: full cooperation payoff 0.88 for each k",
  baseline_random_roles="no exogenous role balance")
 (folder/"v54_spec.json").write_text(json.dumps(spec,indent=2),encoding="utf8")
 c=config(a.k,a.batch,a.device)
 initial=time.perf_counter()
 for u in range(1,a.updates+1):
  metrics,rewards,logp,entropy,times=episode(c,donor,actor,
     a.role_seed*23117+u*31,init="mixed")
  future=torch.zeros_like(rewards[0]);rs=[]
  for r in reversed(rewards):
   future=r+GAMMA*future;rs.append(future)
  rs=torch.stack(rs[::-1])
  baseline=(rs.sum(1,keepdim=True)-rs)/(a.batch-1)
  advantage=((rs-baseline)/
   rs.std(1,unbiased=False,keepdim=True).clamp_min(.25)).detach()
  loss=-(torch.stack(logp)*advantage[times]).mean() - a.ent*torch.stack(entropy).mean()
  optimizer.zero_grad(set_to_none=True)
  loss.backward()
  assert all(p.grad is not None and torch.isfinite(p.grad).all()
    for p in actor.parameters())
  optimizer.step()
  if u==1 or u%a.save_every==0 or u==a.updates:
   rng=torch.get_rng_state()
   with torch.no_grad():evaluations=development(config(a.k,16,a.device),donor,actor,a.role_seed)
   torch.set_rng_state(rng)
   record=dict(update=u,train=metrics,development=evaluations,
    loss=float(loss.detach()),elapsed_seconds=time.perf_counter()-initial)
   with (folder/"v54_history.jsonl").open("a",encoding="utf8") as fh:
    fh.write(json.dumps(record)+"\n")
   temp=folder/"checkpoint_tmp.pt"
   torch.save(dict(actor=actor.state_dict(),optimizer=optimizer.state_dict(),
      update=u),temp)
   os.replace(temp,folder/"v54_latest.pt")
   mon=next(x for x in evaluations if x["init"]=="monolith")
   print("V54",a.name,"u",u,"food",round(mon["food"],4),
    "balance",round(mon["terminal_balance"],4),"gifts",round(mon["gifts_per_link"],3),
    "elapsed",round(record["elapsed_seconds"],1),flush=True)
 (folder/"v54_status.json").write_text(json.dumps(dict(state="completed",
  updates=a.updates,elapsed_seconds=time.perf_counter()-initial)),encoding="utf8")
 print("V54_FINISHED",a.name,flush=True)

if __name__=="__main__":main()
