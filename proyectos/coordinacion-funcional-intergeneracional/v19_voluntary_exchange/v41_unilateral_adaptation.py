"""V41: one-time loss of contractual enforcement, continued private RL under unilateral gifts.

Four source policies (contract and unilateral history) with two sensory branches
each. No contract rule, teacher, altruism bonus or reward sharing during V41.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
from types import SimpleNamespace
import numpy as np,torch
from targeted_gifts import C
import v25_multi_capacity as base
from v25_holdout import load
from v23_joint_cold import gradients_per_agent
ROOT=Path(__file__).resolve().parent

def development(donor,role,spec,social,seed=194141,batch=12):
 records=[]
 for topo,init in (("ring","monolith"),("ring","random"),("rewired","monolith")):
  c=C(n=48,k=4,degree=6,topology=topo,batch=batch,
      horizon=48,cost=.04,gamma=spec["gamma"],device=spec["device"])
  torch.manual_seed(seed+{"ring":17,"rewired":31}[topo]+{"monolith":11,"random":19}[init])
  m,*_=base.roll(c,donor,role,seed,init=init,
    interval=spec["role_interval"],move_cost=spec["move_cost"],social=social)
  records.append(dict(topology=topo,init=init,**m))
 return records

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--source",required=True)
 p.add_argument("--updates",type=int,default=1000)
 p.add_argument("--batch",type=int,default=12)
 p.add_argument("--horizon",type=int,default=48)
 p.add_argument("--eval-every",type=int,default=200)
 p.add_argument("--social",choices=("yes","no"),required=True)
 p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
 a=p.parse_args()
 torch.set_num_threads(2)
 assert a.batch>=2 and a.horizon==48 and a.updates>=1
 donor,role,source=load(a.source,a.device)
 assert source["n"]==48 and source["k"]==4 and source["cost"]==.04
 if a.source.startswith("v30_MUTUAL_"):
  assert source["settlement"]=="mutual"
  source_kind="contract"
 elif a.source.startswith("v29_L_D6_"):
  assert source["relational_feature"]=="legacy" and not source["no_social_training"]
  source_kind="unilateral"
 else:raise ValueError("unsupported frozen starting model")
 source_checkpoint=torch.load(ROOT/"runs"/a.source/"joint_latest.pt",
   map_location="cpu",weights_only=False)
 assert source_checkpoint["update"] in (700,850)
 donor.requires_grad_(True);role.requires_grad_(True)
 opt_d=torch.optim.Adam(donor.parameters(),lr=source["lr_gift"])
 opt_r=torch.optim.Adam(role.parameters(),lr=source["lr_role"])
 opt_d.load_state_dict(source_checkpoint["opt_gift"])
 opt_r.load_state_dict(source_checkpoint["opt_role"])
 folder=ROOT/"runs"/a.name
 folder.mkdir(parents=True,exist_ok=False)
 settings=dict(vars(a),source_history_type=source_kind,source_spec=source,
  source_update=source_checkpoint["update"],source_optimizers_restored=True,
  n=48,k=4,degree=6,cost=.04,settlement="unilateral",
  role_interval=source["role_interval"],move_cost=source["move_cost"],
  hidden=source["hidden"],init_scale=source["init_scale"],
  gamma=source["gamma"],lr_gift=source["lr_gift"],lr_role=source["lr_role"],
  ent_gift=source["ent_gift"],ent_role=source["ent_role"],seed=source["seed"])
 (folder/"v41_spec.json").write_text(json.dumps(settings,indent=2),encoding="utf8")
 # Auxiliary v25 metadata enables reuse of the independent frozen auditors.
 (folder/"v25_spec.json").write_text(json.dumps(settings,indent=2),encoding="utf8")
 torch.manual_seed(source["seed"]+411000)
 if a.device=="cuda":torch.cuda.manual_seed_all(source["seed"]+411000)
 np.random.seed(source["seed"]+411000)
 t0=time.perf_counter()
 with (folder/"v41_history.jsonl").open("w",encoding="utf8") as history:
  for u in range(1,a.updates+1):
   c=C(n=48,k=4,degree=6,topology="ring",batch=a.batch,
    horizon=48,cost=.04,gamma=source["gamma"],device=a.device)
   measure,rewards,glog,gent,rlog,rent,role_times=base.roll(c,donor,role,
      seed=source["seed"]*19301+31*u+411000,
      init="mixed",interval=source["role_interval"],
      move_cost=source["move_cost"],social=(a.social=="yes"))
   G=torch.zeros_like(rewards[0]);rev=[]
   for value in reversed(rewards):
    G=value+c.gamma*G;rev.append(G)
   G=torch.stack(rev[::-1])
   others=(G.sum(1,keepdim=True)-G)/(a.batch-1)
   advantages=((G-others)/G.std(1,unbiased=False,
      keepdim=True).clamp_min(.25)).detach()
   loss_g=-(torch.stack(glog)*advantages).mean()-source["ent_gift"]*torch.stack(gent).mean()
   loss_r=-(torch.stack(rlog)*advantages[role_times]).mean()-source["ent_role"]*torch.stack(rent).mean()
   opt_d.zero_grad(set_to_none=True);opt_r.zero_grad(set_to_none=True)
   (loss_g+loss_r).backward()
   gradients_per_agent(donor,48);gradients_per_agent(role,48)
   opt_d.step();opt_r.step()
   if u==1 or u%a.eval_every==0 or u==a.updates:
    cpu=torch.get_rng_state()
    gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None
    with torch.no_grad():
     specs=SimpleNamespace(**settings)
     evals=development(donor,role,settings,a.social=="yes")
    torch.set_rng_state(cpu)
    if gpu is not None:torch.cuda.set_rng_state(gpu)
    row=dict(update=u,train=measure,development=evals,
      elapsed=time.perf_counter()-t0)
    history.write(json.dumps(row)+"\n");history.flush()
    tmp=folder/"temp_checkpoint.pt"
    torch.save(dict(gift=donor.state_dict(),role=role.state_dict(),
       opt_gift=opt_d.state_dict(),opt_role=opt_r.state_dict(),
       update=u,rng_cpu=torch.get_rng_state(),
       rng_gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None),tmp)
    os.replace(tmp,folder/"joint_latest.pt")
    observed=next(x for x in evals if x["topology"]=="ring" and x["init"]=="monolith")
    print("V41",a.name,"step",u,"food",round(observed["food"],4),
      "donations",round(observed["gifts_per_person"],3),
      "coverage",round(observed["distinct_coverage"],3),
      "elapsed",round(row["elapsed"],1),flush=True)
 (folder/"v25_status.json").write_text(json.dumps(dict(state="completed",
  updates=a.updates,elapsed_seconds=time.perf_counter()-t0)),encoding="utf8")
 (folder/"v41_status.json").write_text(json.dumps(dict(state="completed",
  updates=a.updates,elapsed_seconds=time.perf_counter()-t0)),encoding="utf8")
 print("V41_COMPLETED",a.name,flush=True)
if __name__=="__main__":main()
