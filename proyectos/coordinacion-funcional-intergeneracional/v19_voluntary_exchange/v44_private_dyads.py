"""V44 private policy-gradient learning of dyadic reciprocity without contracts.

All 48 agents have independent MLP parameters. Only own discounted food is
optimized. No hardcoded response, reputation, contract, group reward or teacher.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from torch import nn
from torch.distributions import Bernoulli
ROOT=Path(__file__).resolve().parent
N=48;VALUE=.55/3.;BASE=.2;COST=.04;GAMMA=.995
MAX_STEPS=48

class PrivateDyadic(nn.Module):
 def __init__(self,n=N,hidden=16):
  super().__init__();self.n=n;self.hidden=hidden
  self.W=nn.Parameter(torch.randn(n,5,hidden)*.075)
  self.b=nn.Parameter(torch.zeros(n,hidden))
  self.v=nn.Parameter(torch.randn(n,hidden)*.075)
  self.bias=nn.Parameter(torch.zeros(n))
 def logits(self,own_last,other_last,lastfood,first,see_partner):
  b,n=own_last.shape
  partner=other_last if see_partner else torch.zeros_like(other_last)
  inputs=torch.stack((own_last,partner,lastfood,
    torch.full_like(own_last,float(first)),
    torch.ones_like(own_last)),dim=-1)
  hid=torch.tanh(torch.einsum("bnf,nfh->bnh",inputs,self.W)+self.b[None,:,:])
  return torch.einsum("bnh,nh->bn",hid,self.v)+self.bias[None,:]
 def act(self,own_last,other_last,lastfood,first,see_partner):
  logits=self.logits(own_last,other_last,lastfood,first,see_partner)
  dist=Bernoulli(logits=logits)
  action=dist.sample()
  return action,dist.log_prob(action),dist.entropy()

def simulation(actor,seed,batch=16,q=.95,see_partner=True,device="cpu",
    force_t0=None,forced_subject=None,record=True,survival_worlds=None):
 assert 0<=q<=1
 torch.manual_seed(seed*31+44007)
 rng=torch.Generator(device=device)
 rng.manual_seed(seed*839+441103)
 partner=torch.arange(N,device=device)^1
 ownlast=torch.zeros(batch,N,device=device)
 lastfood=torch.full_like(ownlast,BASE)
 alive=torch.ones(batch,dtype=torch.bool,device=device)
 reward_log=[];log_probs=[];entropies=[]
 food_sum=0.;gift_sum=0.;mutual_sum=0.;total_living=0.
 pairtrace=[]
 for t in range(MAX_STEPS):
  if t>0 and q<1:
   if survival_worlds is None:
    alive &= torch.rand(batch,device=device,generator=rng)<q
   else:
    assert batch==survival_worlds*N
    alive &= (torch.rand(survival_worlds,device=device,generator=rng)<q).repeat_interleave(N)
  if not bool(alive.any()):break
  g,lp,ent=actor.act(ownlast,ownlast[:,partner],lastfood,
    t==0,see_partner)
  if t==0 and force_t0 is not None:
   if forced_subject is None:
    g[:,:]=float(force_t0)
   else:
    g[torch.arange(batch,device=device),forced_subject]=float(force_t0)
  food=BASE+VALUE*g[:,partner]-COST*g
  active=alive.float()[:,None]
  reward_log.append(food*active)
  log_probs.append(lp*active)
  entropies.append(ent*active)
  gift_sum+=float((g*active).sum().detach())
  mutual=(g*g[:,partner])
  mutual_sum+=float((mutual*active).sum().detach())
  food_sum+=float((food*active).sum().detach())
  total_living+=float(alive.sum())
  pairtrace.append(dict(round=t+1,active=float(alive.float().mean()),
    gifts=float((g*active).sum().detach())/(alive.sum().item()*N),
    food=float((food*active).sum().detach())/(alive.sum().item()*N)))
  ownlast=g
  lastfood=food
 # If q1 or qclose1 full horizon is max48; if all die earlier, returns valid.
 rewards=torch.stack(reward_log)
 logs=torch.stack(log_probs)
 ents=torch.stack(entropies)
 measures=dict(food=food_sum/max(1.,total_living*N),
  gifts=gift_sum/max(1.,total_living*N),
  mutual=mutual_sum/max(1.,total_living*N),
  lifetime=total_living/batch,
  rounds=len(pairtrace),
  traces=pairtrace)
 return measures,rewards,logs,ents

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--seed",type=int,required=True)
 p.add_argument("--q",type=float,required=True)
 p.add_argument("--partner-info",choices=("yes","no"),required=True)
 p.add_argument("--updates",type=int,default=1000)
 p.add_argument("--batch",type=int,default=16)
 p.add_argument("--lr",type=float,default=.003)
 p.add_argument("--ent",type=float,default=.005)
 p.add_argument("--eval-every",type=int,default=200)
 p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 a=p.parse_args()
 assert a.updates>=1 and a.batch>=3
 assert a.q in (.2,.95)
 torch.set_num_threads(2)
 torch.manual_seed(a.seed);np.random.seed(a.seed)
 actor=PrivateDyadic().to(a.device)
 opt=torch.optim.Adam(actor.parameters(),lr=a.lr)
 folder=ROOT/"runs"/a.name
 folder.mkdir(parents=True,exist_ok=False)
 settings=dict(vars(a),N=N,k=4,n_pairs=N//2,
  food_base=BASE,value_of_received_complementary=VALUE,
  cost=COST,gamma=GAMMA,material_settlement="unilateral",
  role_mapping="every consecutive pair complementary",
  source="random individual private actor weights; no pretrained contract")
 (folder/"v44_spec.json").write_text(json.dumps(settings,indent=2),encoding="utf8")
 t0=time.perf_counter()
 for u in range(1,a.updates+1):
  stats,rewards,logs,entropy=simulation(actor,
    seed=a.seed*19301+31*u,batch=a.batch,q=a.q,
    see_partner=(a.partner_info=="yes"),device=a.device)
  G=torch.zeros_like(rewards[0]);ordered=[]
  for x in reversed(rewards):
   G=x+GAMMA*G
   ordered.append(G)
  ret=torch.stack(ordered[::-1])
  baseline=(ret.sum(1,keepdim=True)-ret)/(a.batch-1)
  advantage=((ret-baseline)/ret.std(1,unbiased=False,
     keepdim=True).clamp_min(.20)).detach()
  # Normalization by active steps changes no reward or relative incentives.
  alive_per_step=(rewards.abs().sum(2)>0).float()
  divisor=alive_per_step.sum().clamp_min(1.)*N
  loss=-((logs*advantage).sum()+a.ent*entropy.sum())/divisor
  opt.zero_grad(set_to_none=True)
  loss.backward()
  opt.step()
  if u==1 or u%a.eval_every==0 or u==a.updates:
   cpu=torch.get_rng_state()
   gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None
   with torch.no_grad():
    evals=[]
    for seed in (970001,970007,970009):
     v,*_=simulation(actor,seed,batch=12,q=a.q,
        see_partner=(a.partner_info=="yes"),device=a.device)
     evals.append({key:value for key,value in v.items() if key!="traces"})
   torch.set_rng_state(cpu)
   if gpu is not None:torch.cuda.set_rng_state(gpu)
   report=dict(update=u,train={k:v for k,v in stats.items() if k!="traces"},
     development={k:float(np.mean([x[k] for x in evals])) for k in evals[0]},
     elapsed=time.perf_counter()-t0,loss=float(loss.detach()))
   with (folder/"v44_history.jsonl").open("a",encoding="utf8") as handle:
    handle.write(json.dumps(report)+"\n")
   tmp=folder/"v44_tmp.pt"
   torch.save(dict(actor=actor.state_dict(),optimizer=opt.state_dict(),
      update=u,rng_cpu=torch.get_rng_state(),
      rng_gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None),tmp)
   os.replace(tmp,folder/"dyadic_latest.pt")
   print("V44",a.name,"u",u,"FOOD",round(report["development"]["food"],4),
     "GIFT",round(report["development"]["gifts"],4),
     "MUTUAL",round(report["development"]["mutual"],4),
     "LIFE",round(report["development"]["lifetime"],2),
     "elapsed",round(report["elapsed"],1),flush=True)
 (folder/"v44_status.json").write_text(json.dumps(
    dict(state="completed",updates=a.updates,elapsed=time.perf_counter()-t0)),encoding="utf8")
 print("V44_FINISHED",a.name,flush=True)

if __name__=="__main__":main()
