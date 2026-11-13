"""V43: train private agents under varying relationship horizons and clock cues.

Factorial 2×2: deterministic vs geometric termination; observable time
vs hidden time. Baseline deterministic-clocked rollout must exactly match
V25/V41. Unilateral delivery, unchanged food and cost functions, no teacher.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C
from v24_k4_joint import start4,PrivateOccupationK
from v25_multi_capacity import step_multi
from v25_holdout import load
from v23_joint_cold import gradients_per_agent
ROOT=Path(__file__).resolve().parent

def local_potential(c,w):
 neighborhood=w["roles"][:,w["graph"]]
 possible=torch.nn.functional.one_hot(neighborhood,c.k).bool().any(2)
 own=torch.nn.functional.one_hot(w["roles"],c.k).bool()
 return ((possible&~own).float().sum(2)/(c.k-1)).mean(1)

def roll(c,gift,role,seed,q=1.,hidden_clock=False,init="mixed",
         interval=8,move_cost=.015,role_baseline=None):
 assert 0<q<=1
 world=start4(c,seed,init)
 alive=torch.ones(c.batch,device=c.device,dtype=torch.bool)
 rlist=[];glog=[];gent=[];rlog=[];rent=[];rt=[]
 sums=dict(food=0.,gifts=0.,coverage=0.,full=0.,potential=0.,steps=0.)
 active_by_round=[]
 for t in range(c.horizon):
  if t>0 and q<1.:
   alive=alive&(torch.rand(c.batch,device=c.device)<q)
  active=alive.float()
  activeagent=active[:,None]
  observations=({**world,"t":0} if hidden_clock else world)
  if t%interval==0:
   if role_baseline=="fixed":
    chosen=world["roles"];lp_r=ent_r=None
   elif role_baseline is not None and role_baseline.startswith("random_"):
    p=float(role_baseline.split("_",1)[1])
    replace=(torch.rand(c.batch,c.n,device=c.device)<p)
    random=torch.randint(c.k,(c.batch,c.n),device=c.device)
    chosen=torch.where(replace,random,world["roles"])
    lp_r=ent_r=None
   else:chosen,lp_r,ent_r=role.act(c,observations,history=True)
   changed=(chosen!=world["roles"]).float()
   world["roles"]=chosen;world["last_switch"]=changed
   if lp_r is not None:
    rlog.append(lp_r*activeagent)
    rent.append(ent_r*activeagent)
    rt.append(t)
  # The original actor samples three independent destination/give decisions.
  observations=({**world,"t":0} if hidden_clock else world)
  drawn=[gift.act(c,observations,mode="normal") for _ in range(c.k-1)]
  destinations=torch.stack([a[0] for a in drawn],2)
  gifts=torch.stack([a[1] for a in drawn],2)
  lp=torch.stack([a[2] for a in drawn]).sum(0)
  entropy=torch.stack([a[3] for a in drawn]).sum(0)
  food,_=step_multi(c,world,destinations,gifts)
  if t%interval==0:
   food=food-move_cost*changed
   world["lastfood"]=food
  rlist.append(food*activeagent)
  glog.append(lp*activeagent)
  gent.append(entropy*activeagent)
  live_count=float(active.sum())
  sums["steps"]+=live_count
  sums["food"]+=float((food*activeagent).sum().detach())
  sums["gifts"]+=float((gifts.sum(2)*activeagent).sum().detach())
  sums["coverage"]+=float((world["cover"]*activeagent).sum().detach())
  sums["full"]+=float((world["full"]*activeagent).sum().detach())
  sums["potential"]+=float((local_potential(c,world)*active).sum().detach())
  active_by_round.append(live_count/c.batch)
 denom=max(1.,sums["steps"]*c.n)
 metrics=dict(food=sums["food"]/denom,
  gifts_per_person=sums["gifts"]/denom,
  coverage=sums["coverage"]/denom,
  complete=sums["full"]/denom,
  potential=sums["potential"]/max(1.,sums["steps"]),
  mean_alive_rounds=sums["steps"]/c.batch,
  last_round_survival=active_by_round[-1],
  total_alive_agent_rounds=sums["steps"]*c.n)
 return metrics,torch.stack(rlist),glog,gent,rlog,rent,rt

def development(gift,role,spec,q,hidden_clock,seed=194141,worlds=12):
 records=[]
 for topo,init in (("ring","monolith"),("ring","random"),("rewired","monolith")):
  c=C(n=48,k=4,degree=6,topology=topo,batch=worlds,
    horizon=48,cost=.04,gamma=spec["gamma"],device=spec["device"])
  torch.manual_seed(seed+{"ring":17,"rewired":31}[topo]+{"monolith":11,"random":19}[init])
  vals,*_=roll(c,gift,role,seed,init=init,q=q,
    hidden_clock=hidden_clock,interval=spec["role_interval"],
    move_cost=spec["move_cost"])
  records.append(dict(topology=topo,init=init,**vals))
 return records

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--source",required=True)
 p.add_argument("--updates",type=int,default=1000)
 p.add_argument("--batch",type=int,default=12)
 p.add_argument("--eval-every",type=int,default=200)
 p.add_argument("--duration",choices=("fixed","hazard"),required=True)
 p.add_argument("--clock",choices=("visible","hidden"),required=True)
 p.add_argument("--q",type=float,default=.98)
 p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
 a=p.parse_args()
 assert a.updates>=1 and a.batch>=2
 if a.duration=="fixed":assert a.q==.98
 else:assert a.q==.98
 torch.set_num_threads(2)
 gift,role,original=load(a.source,a.device)
 assert original["settlement"]=="mutual" and original["n"]==48 and original["k"]==4
 assert original["cost"]==.04 and original["seed"] in (3111,4111)
 checkpoint=torch.load(ROOT/"runs"/a.source/"joint_latest.pt",
    map_location="cpu",weights_only=False)
 assert checkpoint["update"]==700
 gift.requires_grad_(True);role.requires_grad_(True)
 og=torch.optim.Adam(gift.parameters(),lr=original["lr_gift"])
 orole=torch.optim.Adam(role.parameters(),lr=original["lr_role"])
 og.load_state_dict(checkpoint["opt_gift"])
 orole.load_state_dict(checkpoint["opt_role"])
 spec=dict(vars(a),source_spec=original,source_update=700,
  settlement="unilateral",n=48,k=4,cost=.04,degree=6,
  gamma=original["gamma"],seed=original["seed"],
  hidden=original["hidden"],init_scale=original["init_scale"],
  lr_gift=original["lr_gift"],lr_role=original["lr_role"],
  ent_gift=original["ent_gift"],ent_role=original["ent_role"],
  role_interval=original["role_interval"],move_cost=original["move_cost"],
  effective_q=(1. if a.duration=="fixed" else a.q),
  hidden_clock=(a.clock=="hidden"))
 folder=ROOT/"runs"/a.name;folder.mkdir(parents=True,exist_ok=False)
 (folder/"v43_spec.json").write_text(json.dumps(spec,indent=2),encoding="utf8")
 torch.manual_seed(original["seed"]+411000)
 if a.device=="cuda":torch.cuda.manual_seed_all(original["seed"]+411000)
 np.random.seed(original["seed"]+411000)
 t0=time.perf_counter()
 with (folder/"v43_history.jsonl").open("w",encoding="utf8") as hist:
  for u in range(1,a.updates+1):
   c=C(n=48,k=4,degree=6,topology="ring",batch=a.batch,
    horizon=48,cost=.04,gamma=original["gamma"],device=a.device)
   metrics,rewards,lg,eg,lr,er,rt=roll(c,gift,role,
     seed=original["seed"]*19301+31*u+411000,
     init="mixed",q=spec["effective_q"],
     hidden_clock=spec["hidden_clock"],
     interval=original["role_interval"],move_cost=original["move_cost"])
   discounted=torch.zeros_like(rewards[0]);history=[]
   for reward in reversed(rewards):
    discounted=reward+c.gamma*discounted
    history.append(discounted)
   returns=torch.stack(history[::-1])
   others=(returns.sum(1,keepdim=True)-returns)/(a.batch-1)
   advantages=((returns-others)/returns.std(1,unbiased=False,
      keepdim=True).clamp_min(.25)).detach()
   lgift=-(torch.stack(lg)*advantages).mean()-original["ent_gift"]*torch.stack(eg).mean()
   lrole=-(torch.stack(lr)*advantages[rt]).mean()-original["ent_role"]*torch.stack(er).mean()
   og.zero_grad(set_to_none=True);orole.zero_grad(set_to_none=True)
   (lgift+lrole).backward()
   gradients_per_agent(gift,48);gradients_per_agent(role,48)
   og.step();orole.step()
   if u==1 or u%a.eval_every==0 or u==a.updates:
    cpu=torch.get_rng_state()
    gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None
    with torch.no_grad():
     evals=development(gift,role,spec,spec["effective_q"],spec["hidden_clock"])
    torch.set_rng_state(cpu)
    if gpu is not None:torch.cuda.set_rng_state(gpu)
    entry=dict(update=u,train=metrics,development=evals,
      elapsed_seconds=time.perf_counter()-t0)
    hist.write(json.dumps(entry)+"\n");hist.flush()
    tmp=folder/"checkpoint_tmp.pt"
    torch.save(dict(gift=gift.state_dict(),role=role.state_dict(),
     opt_gift=og.state_dict(),opt_role=orole.state_dict(),update=u,
     rng_cpu=torch.get_rng_state(),
     rng_gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None),tmp)
    os.replace(tmp,folder/"joint_latest.pt")
    lead=next(x for x in evals if x["topology"]=="ring" and x["init"]=="monolith")
    print("V43",a.name,"u",u,"FOOD",round(lead["food"],4),
      "GIFTS",round(lead["gifts_per_person"],4),
      "ALIVE",round(lead["mean_alive_rounds"],2),
      "TIME",round(entry["elapsed_seconds"],1),flush=True)
 (folder/"v43_status.json").write_text(json.dumps(dict(state="completed",
   updates=a.updates,elapsed_seconds=time.perf_counter()-t0)),encoding="utf8")
 print("V43_FINISHED",a.name,flush=True)
if __name__=="__main__":main()
