"""Sealed V3B C1/C2/C3 independent learners versus no-learning baselines.

Prerecorded in PREREG_V3B_C1C2.md. No tuning after locked tests.
Primary units for inference across learning = 3 training seeds, NOT 300 worlds.
"""
import hashlib,json,statistics,math,sys,time
from pathlib import Path
import torch
from individual_agents import IndependentActors
from environment_v3 import IndependentSociety
from environment import Configuration
from train_independent import random_floor
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"holdout_v3b"
OUT.mkdir(exist_ok=True)
torch.set_num_threads(2)
SEEDS=(311,312,313)
K=(2,3,4)
MODES=("C1","C2","C3","random_always","random_T24","stay")
BATCH=100
STEPS=120

def weight_path(seed,mode):
 return ROOT/"runs"/f"v3b_seed{seed}_{mode}_updates120"/"FINAL_MODEL.pt"

def digest(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def lock_info():
 weights={(s,m):weight_path(s,m) for s in SEEDS for m in ("C1","C2")}
 for p in weights.values():
  if not p.exists():raise RuntimeError("Missing model "+str(p))
 return {"protocol":"PREREG_V3B_C1C2.md",
  "test_script_hash":digest(ROOT/"evaluate_v3b.py"),
  "env_hash":digest(ROOT/"environment_v3.py"),
  "society_hash":digest(ROOT.parent/"v2_rl"/"environment.py"),
  "policy_hash":digest(ROOT/"individual_agents.py"),
  "train_script_hash":digest(ROOT/"train_independent.py"),
  "weights":{f"{s}_{m}":digest(path) for (s,m),path in weights.items()},
  "seeds":list(SEEDS),"k":list(K),"conditions":list(MODES),
  "batch":BATCH,"ticks":STEPS,
  "eval_seed_formula":"990000+10000*trainseed+100*k",
  "training_updates_during_evaluation":0,
  "stability":"D<=0.06 AND churn<=0.05 over last 10 ticks"}

@torch.no_grad()
def run_case(seed,k,mode,agents):
 e=IndependentSociety(Configuration(rows=6,cols=6,batch=BATCH,seed=seed,
                                    randomize_majority=True))
 e.reset(k=k)
 torch.manual_seed(seed+31*len(mode))
 ds=[e.tv().clone()]
 ch=[]
 sent=[]
 request_matches=[]
 n=e.n
 actor=agents["C1"] if mode=="C1" else agents["C2"]
 for t in range(STEPS):
  observation=e.observe()
  if mode=="stay" or (mode=="random_T24" and t>=24):
   outgoing=torch.zeros((BATCH,n),dtype=torch.long)
   incoming,requests,payload=e.deliveries(observation,outgoing)
   next_color=e.colors.clone()
  else:
   random=mode in ("random_always","random_T24")
   communication=mode in ("C2","random_always","random_T24")
   outgoing,_,_=actor.act_send(observation,e.k,uniform=random,
                         disable_messages=not communication)
   incoming,requests,payload=e.deliveries(observation,outgoing)
   next_color,_,_=actor.act_choose(observation,e.k,incoming,requests,payload,
                                   uniform=random)
  metrics=e.step(outgoing,next_color,incoming,requests)
  ds.append(metrics["tv"].clone())
  ch.append(metrics["churn"].clone())
  sent.append(metrics["messages"].clone())
  request_matches.append(metrics["choice_matches_request"].clone())
 v=torch.stack(ds);c=torch.stack(ch)
 floors=random_floor(n,k)
 stable=((v[-10:]<=.06)&(c[-10:]<=.05)).all(0)
 return {"training_seed":agents["training_seed"],"k":k,
  "condition":mode,"test_seed":seed,"n":n,"test_worlds":BATCH,"ticks":STEPS,
  "average_initial_D":float(v[0].mean()),
  "average_final_D":float(v[-1].mean()),
  "average_tail_D":float(v[-10:].mean()),
  "ratio_final_D_to_IID":float(v[-1].mean())/floors,
  "random_IID_D_exact":floors,
  "average_D_AUC":float(v[1:].mean()),
  "average_last10_churn":float(c[-10:].mean()),
  "stable_count":int(stable.sum()),
  "exact_count":int((v[-1].abs()<1e-6).sum()),
  "ever_near_count":int((v<=.06).any(0).sum()),
  "average_send_rate":float(torch.stack(sent).mean()),
  "average_request_match_rate":float(torch.stack(request_matches).mean()),
  "final_world_D":v[-1].tolist(),
  "stable_by_world":stable.tolist(),
  "D_curve_mean":v.mean(1).tolist(),
  "churn_curve_mean":torch.cat((torch.zeros(1),c.mean(1))).tolist()}

def main():
 start=time.perf_counter()
 lock=lock_info()
 lock_path=OUT/"LOCK.json"
 if lock_path.exists():
  other=json.loads(lock_path.read_text(encoding="utf-8"))
  if other!=lock:raise RuntimeError("Code or models changed after locking")
 else:lock_path.write_text(json.dumps(lock,ensure_ascii=False,indent=2),encoding="utf-8")
 print("V3B_EVAL_LOCKED",len(lock["weights"]),"models",flush=True)
 all_summary=[]
 for trainseed in SEEDS:
  agents={"training_seed":trainseed}
  for mode in ("C1","C2"):
   z=torch.load(weight_path(trainseed,mode),map_location="cpu",weights_only=False)
   if z["update"]!=120:raise RuntimeError("Wrong checkpoint")
   net=IndependentActors(n=36,hidden=z["config"]["hidden"])
   net.load_state_dict(z["model"]);net.eval()
   agents[mode]=net
  for k in K:
   eval_seed=990000+10000*trainseed+100*k
   for mode in MODES:
    target=OUT/f"seed{trainseed}_k{k}_{mode}.json"
    if target.exists():
     v=json.loads(target.read_text(encoding="utf-8"))
    else:
     v=run_case(eval_seed,k,mode,agents)
     target.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
    all_summary.append({name:val for name,val in v.items() if name not in
                      ("final_world_D","stable_by_world","D_curve_mean","churn_curve_mean")})
    print("V3B_HOLDOUT",trainseed,k,mode,
         "D",round(v["average_final_D"],5),
         "ratio",round(v["ratio_final_D_to_IID"],3),
         "stable",v["stable_count"],"/100",
         "exact",v["exact_count"],
         "churn",round(v["average_last10_churn"],3),
         "time",round(time.perf_counter()-start,1),flush=True)
 assert len(all_summary)==len(SEEDS)*len(K)*len(MODES)
 diffs=[]
 for trainseed in SEEDS:
  for k in K:
   x=next(r for r in all_summary if r["training_seed"]==trainseed and r["k"]==k and r["condition"]=="C1")
   y=next(r for r in all_summary if r["training_seed"]==trainseed and r["k"]==k and r["condition"]=="C2")
   z=next(r for r in all_summary if r["training_seed"]==trainseed and r["k"]==k and r["condition"]=="C3")
   diffs.append({"seed":trainseed,"k":k,
    "C2_minus_C1_final_D":y["average_final_D"]-x["average_final_D"],
    "C3_minus_C2_final_D":z["average_final_D"]-y["average_final_D"],
    "C2_minus_C1_stable_fraction":(y["stable_count"]-x["stable_count"])/BATCH,
    "C3_minus_C2_stable_fraction":(z["stable_count"]-y["stable_count"])/BATCH})
 report={"lock":lock,"n_training_cohorts":len(SEEDS),
     "n_condition_task_seed_batches":len(all_summary),
     "n_test_societies_per_task_condition":len(SEEDS)*BATCH,
     "condition_summary":all_summary,"paired_differences":diffs,
     "cautions":["C3 is deployment ablation under input-distribution shift",
                 "The baseline's 24-tick stopping clock is researcher-defined",
                 "Three independent training seeds, test worlds nested under weights",
                 "No testing at k>4 or new population sizes",
                 "Global reward remains an information channel available to all agents"]}
 out=OUT/"SUMMARY.json"
 if out.exists():raise RuntimeError("Refuse to overwrite summary")
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 print("V3B_HOLDOUT_COMPLETE",len(all_summary),"batches",round(time.perf_counter()-start,1),flush=True)
if __name__=="__main__":main()
