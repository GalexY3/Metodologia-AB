"""V46: EXACT differentiable Markov-game private gradient vs opponent shaping.

Two independent agents per pair and 24 independent pairs. Five private logits
per agent (first action and memory-one CC/CD/DC/DD equivalents). We never use
a joint/social reward to update either player's policy.
"""
from __future__ import annotations
import argparse,json,os,time,hashlib,math
from pathlib import Path
import numpy as np,torch
from torch import nn
ROOT=Path(__file__).resolve().parent
N=48;B=.2;V=.55/3.;C=.04;GAMMA=.995;H=48
STATES=((0.,0.),(0.,1.),(1.,0.),(1.,1.))
_A=torch.tensor([0.,0.,1.,1.])
_Z=torch.tensor([0.,1.,0.,1.])
_SWAP=torch.tensor([0,2,1,3])

def components(own,other):
 """Batched Markov chain viewed FROM the own agent's perspective.

 Both arguments are [pairs,5]; other policy state inputs are swapped.
 State 00,01,10,11 is last (own donated, other donated).
 """
 assert own.ndim==2 and own.shape[-1]==5 and own.shape==other.shape
 oi=torch.sigmoid(own[:,0])
 oj=torch.sigmoid(other[:,0])
 p=torch.sigmoid(own[:,1:])
 pj=torch.sigmoid(other[:,1:][:,_SWAP.to(other.device)])
 # First-period transition distribution to the previous-action state at t=1.
 first=torch.stack(((1-oi)*(1-oj),(1-oi)*oj,oi*(1-oj),oi*oj),dim=1)
 # P[s,next_state] = Pr(current joint action pair | previous state s)
 trans=torch.stack(((1-p)*(1-pj),(1-p)*pj,p*(1-pj),p*pj),dim=-1)
 assert trans.shape==(len(own),4,4)
 return oi,oj,p,pj,first,trans

def finite_sum(transition,reward,beta,horizon=H):
 """S = [I-(beta P)^(T-1)] (I-beta P)^-1 r."""
 assert horizon>=2 and 0<=beta<1
 eye=torch.eye(4,device=reward.device,dtype=reward.dtype)
 eye=eye[None,:,:].expand(len(reward),-1,-1)
 matrix=beta*transition
 infinite=torch.linalg.solve(eye-matrix,reward.unsqueeze(-1)).squeeze(-1)
 power=torch.linalg.matrix_power(matrix,horizon-1)
 return infinite-torch.bmm(power,infinite.unsqueeze(-1)).squeeze(-1)

def expected(own,other,q=.95,gamma=GAMMA,metric="food",
             force_first=None,horizon=H):
 oi,oj,p,pj,first,trans=components(own,other)
 if force_first is not None:
  assert force_first in (0.,1.)
  oi=torch.full_like(oi,force_first)
  first=torch.stack(((1-oi)*(1-oj),(1-oi)*oj,oi*(1-oj),oi*oj),dim=1)
 if metric=="food":
  first_reward=B+V*oj-C*oi
  state_reward=B+V*pj-C*p
 elif metric=="gift":
  first_reward=oi
  state_reward=p
 elif metric=="mutual":
  first_reward=oi*oj
  state_reward=p*pj
 else:raise ValueError(metric)
 beta=q*gamma
 tail=finite_sum(trans,state_reward,beta,horizon)
 result=first_reward+beta*(first*tail).sum(1)
 return result

def paired_values(logits,q=.95):
 even=logits[::2];odd=logits[1::2]
 return expected(even,odd,q=q),expected(odd,even,q=q)

def gradients(logits,q,method,alpha):
 """Obtain each person's OWN objective derivative, not social gradient."""
 assert method in ("NL","LOLA","LOOK")
 even=logits[::2];odd=logits[1::2]
 if method=="NL" or alpha==0:
  je=expected(even,odd,q=q)
  jo=expected(odd,even,q=q)
  ge=torch.autograd.grad(je.sum(),even,retain_graph=True)[0]
  go=torch.autograd.grad(jo.sum(),odd)[0]
 else:
  je=expected(even,odd,q=q)
  jo=expected(odd,even,q=q)
  ge=torch.autograd.grad(je.sum(),even,create_graph=True,retain_graph=True)[0]
  go=torch.autograd.grad(jo.sum(),odd,create_graph=True,retain_graph=True)[0]
  other_after=odd+alpha*go
  own_after=even+alpha*ge
  if method=="LOOK":
   # Opponent is adapted but its update is NOT differentiated through.
   other_after=other_after.detach()
   own_after=own_after.detach()
  imagined_e=expected(even,other_after,q=q)
  imagined_o=expected(odd,own_after,q=q)
  ge=torch.autograd.grad(imagined_e.sum(),even,retain_graph=True)[0]
  go=torch.autograd.grad(imagined_o.sum(),odd)[0]
 return torch.stack((ge,go),dim=1).reshape(N,5)

@torch.no_grad()
def measurements(logits,q=.95):
 even=logits[::2];odd=logits[1::2]
 score=paired_values(logits,q)
 first=(score[0]+score[1])*0.5
 norm=sum(q**t for t in range(H))
 food_e=expected(even,odd,q=q,gamma=1.,metric="food")/norm
 food_o=expected(odd,even,q=q,gamma=1.,metric="food")/norm
 gifts_e=expected(even,odd,q=q,gamma=1.,metric="gift")/norm
 gifts_o=expected(odd,even,q=q,gamma=1.,metric="gift")/norm
 mutual_e=expected(even,odd,q=q,gamma=1.,metric="mutual")/norm
 mutual_o=expected(odd,even,q=q,gamma=1.,metric="mutual")/norm
 c_e=expected(even,odd,q=q,force_first=1.)-expected(even,odd,q=q,force_first=0.)
 c_o=expected(odd,even,q=q,force_first=1.)-expected(odd,even,q=q,force_first=0.)
 stacked=lambda a,b:torch.stack((a,b),dim=1).reshape(N)
 causal=stacked(c_e,c_o)
 gifts=stacked(gifts_e,gifts_o)
 mutual=stacked(mutual_e,mutual_o)
 food=stacked(food_e,food_o)
 p=torch.sigmoid(logits)
 # p[last own gave?=1,last partner gave?=1]-p[own=1,partner=0]
 # p[own=0,other=1]-p[own=0,other=0]
 response_if_gave=p[:,4]-p[:,3]
 response_if_didnt=p[:,2]-p[:,1]
 social_responds=(response_if_gave>0) & (response_if_didnt>0)
 grim=(p[:,0]>.7)&(p[:,4]>.7)&(p[:,1]<.3)&(p[:,3]<.3)
 return dict(food=float(food.mean()),food_min=float(food.min()),
  gifts=float(gifts.mean()),mutual=float(mutual.mean()),
  private_discounted=float(stacked(*score).mean()),
  causal=float(causal.mean()),positive_agents=int((causal>0).sum()),
  causal_min=float(causal.min()),
  responder_mean=float(response_if_gave.mean()),
  responder_positive=int((response_if_gave>0).sum()),
  responder_both_positive=int(social_responds.sum()),
  grim_count=int(grim.sum()),mean_initial_gift=float(p[:,0].mean()),
  mean_CC=float(p[:,4].mean()),mean_DD=float(p[:,1].mean()),
  causal_agents=causal.cpu().tolist(),food_agents=food.cpu().tolist(),
  gifts_agents=gifts.cpu().tolist(),
  policy_logits=logits.cpu().tolist())

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--seed",type=int,required=True)
 p.add_argument("--method",choices=("NL","LOLA","LOOK"),required=True)
 p.add_argument("--alpha",type=float,required=True)
 p.add_argument("--q",type=float,choices=(.95,.2),default=.95)
 p.add_argument("--updates",type=int,default=1000)
 p.add_argument("--lr",type=float,default=.03)
 p.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 p.add_argument("--save-every",type=int,default=200)
 a=p.parse_args()
 assert a.alpha in (0.,1.,5.,20.)
 if a.method=="NL":assert a.alpha==0
 else:assert a.alpha>0
 assert a.updates>=1
 torch.set_num_threads(2)
 torch.manual_seed(a.seed)
 logits=nn.Parameter(torch.randn(N,5,device=a.device)*.05)
 opt=torch.optim.Adam([logits],lr=a.lr)
 directory=ROOT/"runs"/a.name
 directory.mkdir(parents=True,exist_ok=False)
 spec=dict(vars(a),n=N,n_pairs=N//2,cost=C,value=V,
  food_base=B,gamma=GAMMA,horizon=H,
  training_objective="own exact discounted food return",
  opponent_gradient="private opponent payoff; no shared objective",
  opponents="paired permanent; distinct individual parameter vectors",
  contract_rule=False,teacher=False)
 (directory/"v46_spec.json").write_text(json.dumps(spec,indent=2),encoding="utf8")
 start=time.perf_counter()
 for update in range(1,a.updates+1):
  grad=gradients(logits,q=a.q,method=a.method,alpha=a.alpha)
  assert torch.isfinite(grad).all(),f"nonfinite gradients at {update}"
  opt.zero_grad(set_to_none=True)
  logits.grad=-grad
  opt.step()
  if update==1 or update%a.save_every==0 or update==a.updates:
   stats=measurements(logits,q=a.q)
   report=dict(update=update,elapsed_seconds=time.perf_counter()-start,
     score={k:v for k,v in stats.items() if k not in
      ("causal_agents","food_agents","gifts_agents","policy_logits")},
     gradient_norm=float(grad.norm().detach()))
   with (directory/"v46_history.jsonl").open("a",encoding="utf8") as handle:
    handle.write(json.dumps(report)+"\n")
   tmp=directory/"checkpoint_tmp.pt"
   torch.save(dict(logits=logits.detach().cpu().clone(),
      optimizer=opt.state_dict(),update=update),tmp)
   os.replace(tmp,directory/"v46_latest.pt")
   print("V46",a.name,"u",update,
    "FOOD",round(stats["food"],4),"GIFT",round(stats["gifts"],4),
    "MUTUAL",round(stats["mutual"],4),"CAUSAL",round(stats["causal"],4),
    "POS",stats["positive_agents"],"GRAD",round(report["gradient_norm"],5),
    "ELAPSED",round(report["elapsed_seconds"],1),flush=True)
 (directory/"v46_status.json").write_text(json.dumps(dict(
  state="completed",updates=a.updates,elapsed_seconds=time.perf_counter()-start)),
   encoding="utf8")
 print("V46_FINISHED",a.name,flush=True)
if __name__=="__main__":main()
