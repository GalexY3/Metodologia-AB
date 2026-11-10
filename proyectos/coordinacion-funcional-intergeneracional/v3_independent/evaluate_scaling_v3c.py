"""Heldout V3C tests across N/hidden/update regimes.

Code and metric choices fixed after prereg, BEFORE inspecting V3C holdout.
No retraining or automatic checkpoint selection. 6 conditions per k; each
world sample is nested under ONE independent training cohort.
"""
from pathlib import Path
import argparse,hashlib,json,time,math
import torch
from individual_agents import IndependentActors
from environment_v3 import IndependentSociety
from environment import Configuration
from train_scaling_v3c import random_floor

torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
CONDITIONS=("C1","C2","C3","random_always","random_T24","stay")
KS=(2,3,4)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def cp(n,h,seed,mode,updates):
 return ROOT/"runs"/f"v3c_N{n}_H{h}_seed{seed}_{mode}_updates{updates}"/"FINAL_MODEL.pt"

@torch.no_grad()
def test_society(actor,world_seed,k,rows,cols,batch,steps,mode):
 n=rows*cols
 torch.manual_seed(world_seed+len(mode)*313)
 env=IndependentSociety(Configuration(rows=rows,cols=cols,batch=batch,
                                      seed=world_seed,randomize_majority=True))
 env.reset(k=k)
 ds=[env.tv().clone()]
 churn=[]
 msg=[]
 match=[]
 for step in range(steps):
  o=env.observe()
  if mode=="stay" or (mode=="random_T24" and step>=24):
   send=torch.zeros((batch,n),dtype=torch.long)
   incoming,request,payload=env.deliveries(o,send)
   choices=env.colors.clone()
  else:
   uniform=(mode in ("random_always","random_T24"))
   send,_,_=actor.act_send(o,env.k,uniform=uniform,
         disable_messages=(mode in ("C1","C3")))
   incoming,request,payload=env.deliveries(o,send)
   choices,_,_=actor.act_choose(o,env.k,incoming,request,payload,
                                 uniform=uniform)
  r=env.step(send,choices,incoming,request)
  ds.append(r["tv"].clone())
  churn.append(r["churn"].clone())
  msg.append(r["messages"].clone())
  match.append(r["choice_matches_request"].clone())
 v=torch.stack(ds);c=torch.stack(churn)
 floor=random_floor(n,k)
 good=((v[-10:]<=.06)&(c[-10:]<=.05)).all(0)
 return {"n":n,"k":k,"world_seed":world_seed,"mode":mode,
   "batch":batch,"steps":steps,
   "IID_expectation_D":floor,
   "average_initial_D":float(v[0].mean()),
   "average_final_D":float(v[-1].mean()),
   "average_last10_D":float(v[-10:].mean()),
   "ratio_final_D_to_IID":float(v[-1].mean())/floor,
   "average_D_AUC":float(v[1:].mean()),
   "average_last10_churn":float(c[-10:].mean()),
   "stable_count":int(good.sum()),
   "final_exact_count":int((v[-1].abs()<1e-6).sum()),
   "ever_near_count":int((v<=.06).any(0).sum()),
   "final_near_count":int((v[-1]<=.06).sum()),
   "mean_send_rate":float(torch.stack(msg).mean()),
   "mean_request_match":float(torch.stack(match).mean()),
   "final_D_per_world":v[-1].tolist(),
   "stable_per_world":good.tolist(),
   "D_curve_mean":v.mean(1).tolist(),
   "churn_curve_mean":torch.cat((torch.zeros(1),c.mean(1))).tolist()}

def main(args):
 n=args.rows*args.cols
 base=ROOT/"holdout_v3c"/f"N{n}_H{args.hidden}_U{args.updates}_seed{args.seed}"
 base.mkdir(parents=True,exist_ok=True)
 ck={m:cp(n,args.hidden,args.seed,m,args.updates) for m in ("C1","C2")}
 if any(not path.exists() for path in ck.values()):
  raise RuntimeError("Final models missing. No use of partial milestones: "+str(ck))
 batch=args.worlds
 lock={
  "protocol":"PREREG_V3C_SCALING.md",
  "n":n,"rows":args.rows,"cols":args.cols,"hidden":args.hidden,
  "updates":args.updates,"training_seed":args.seed,
  "batch":batch,"ticks":args.steps,
  "k":list(KS),"modes":list(CONDITIONS),
  "world_seed_formula":"9000000 + N*10000 + hidden*100 + trainingseed*10 + k",
  "script_sha":sha(ROOT/"evaluate_scaling_v3c.py"),
  "actor_sha":sha(ROOT/"individual_agents.py"),
  "env_sha":sha(ROOT/"environment_v3.py"),
  "base_env_sha":sha(ROOT.parent/"v2_rl"/"environment.py"),
  "trainer_sha":sha(ROOT/"train_scaling_v3c.py"),
  "models_sha":{mode:sha(path) for mode,path in ck.items()},
  "no_gradient_evaluation":True,
  "stability":"D<=.06 and churn<=.05 in 10 last turns"
 }
 p=base/"LOCK.json"
 if p.exists():
  if json.loads(p.read_text(encoding="utf-8"))!=lock:
   raise RuntimeError("Test lock violation: changing files or weights")
 else:p.write_text(json.dumps(lock,ensure_ascii=False,indent=2),encoding="utf-8")
 a={}
 for mode,path in ck.items():
  z=torch.load(path,weights_only=False,map_location="cpu")
  assert z["update"]==args.updates and z["config"]["hidden"]==args.hidden
  net=IndependentActors(n=n,hidden=args.hidden)
  net.load_state_dict(z["model"])
  net.eval()
  a[mode]=net
 rows_out=[]
 t0=time.perf_counter()
 for k in KS:
  world_seed=9000000+n*10000+args.hidden*100+args.seed*10+k
  for mode in CONDITIONS:
   p=base/f"k{k}_{mode}.json"
   if p.exists():
    v=json.loads(p.read_text(encoding="utf-8"))
   else:
    actor=a["C1"] if mode=="C1" else a["C2"]
    v=test_society(actor,world_seed,k,args.rows,args.cols,
                   batch,args.steps,mode)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
   rows_out.append({u:w for u,w in v.items() if u not in
     ("final_D_per_world","stable_per_world","D_curve_mean","churn_curve_mean")})
   print("V3C_HELDOUT","N",n,"H",args.hidden,"U",args.updates,"k",k,mode,
     "D",round(v["average_final_D"],5),"IIDratio",round(v["ratio_final_D_to_IID"],3),
     "stable",v["stable_count"],"/",batch,"churn",round(v["average_last10_churn"],3),
     "elapsed",round(time.perf_counter()-t0,1),flush=True)
 report=base/"SUMMARY.json"
 if report.exists():raise RuntimeError("Refuse overwrite summary")
 report.write_text(json.dumps({"lock":lock,"rows":rows_out,
  "one_independent_training_cohort":True,
  "caveats":["Test worlds share the same fixed N individual policy models",
             "The stop-at-24 control is an externally written clock",
             "0% continuous random stability does not mean poor D",
             "N increases change number of independently trained brains"]},
   ensure_ascii=False,indent=2),encoding="utf-8")
 print("V3C_HELDOUT_DONE",n,args.hidden,args.updates,
    len(rows_out),"batches",round(time.perf_counter()-t0,1),flush=True)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rows",type=int,required=True)
 p.add_argument("--cols",type=int,required=True)
 p.add_argument("--hidden",type=int,required=True)
 p.add_argument("--updates",type=int,required=True)
 p.add_argument("--seed",type=int,default=411)
 p.add_argument("--worlds",type=int,default=48)
 p.add_argument("--steps",type=int,default=120)
 main(p.parse_args())
