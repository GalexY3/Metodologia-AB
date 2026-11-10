"""Prospectively locked posthoc V4D reward-change diagnostic (500 updates).

This experiment is exploratory, designed AFTER seeing V4 10k failure.
Each person still has independent θ_i; no shared credit or policy weights.
"""
import torch,json,hashlib,time
from pathlib import Path
from actors10 import IndependentActors10
from evaluate_v4 import run,ref_iid
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"holdout_delta500"
OUT.mkdir(exist_ok=True)
B=100
T=120
K=(2,3,4)
MODES=("C1","C2","C3","C1_greedy","C2_greedy","random_always","random_T24","stay")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cp(mode):
 return ROOT/"runs"/f"tenstates_N36_H64_seed421_{mode}_u500"/"FINAL_MODEL.pt"
def main():
 models={m:cp(m) for m in ("C1","C2")}
 for mode,path in models.items():
  if not path.exists():raise RuntimeError(f"Missing FINAL_MODEL.pt for {mode}. No partial models.")
 lock={"protocol":"PREREG_V4_DELTA500.md",
       "scope":"exploratory_posthoc_v4_10k_negative_outcome",
       "evaluater_sha":sha(ROOT/"evaluate_delta500.py"),
       "base_eval_sha":sha(ROOT/"evaluate_v4.py"),
       "policy_sha":sha(ROOT/"actors10.py"),
       "society_sha":sha(ROOT/"society10.py"),
       "train_script_sha":sha(ROOT/"train_v4.py"),
       "models_sha":{m:sha(p) for m,p in models.items()},
       "seed_initial_weights":421,"world_seed_formula":"5700000+100*k",
       "n_worlds":B,"horizon":T,"k":list(K),"modes":list(MODES)}
 lp=OUT/"LOCK.json"
 if lp.exists():
  if json.loads(lp.read_text(encoding="utf-8"))!=lock:
   raise RuntimeError("Code or checkpoints changed post lock")
 else:lp.write_text(json.dumps(lock,ensure_ascii=False,indent=2),encoding="utf-8")
 actors={}
 for mode,p in models.items():
  raw=torch.load(p,weights_only=False,map_location="cpu")
  if raw.get("update")!=500 or raw["config"].get("reward_kind")!="delta" \
     or raw["config"].get("churn_penalty")!=0:
   raise RuntimeError("Checkpoint wrong experimental intervention")
  a=IndependentActors10(n=36,hidden=64)
  a.load_state_dict(raw["model"]);a.eval()
  actors[mode]=a
 results=[]
 t0=time.perf_counter()
 for k in K:
  base=ref_iid(k)
  for mode in MODES:
   file=OUT/f"k{k}_{mode}.json"
   if file.exists():
    r=json.loads(file.read_text(encoding="utf-8"))
   else:
    network=actors["C1"] if mode.startswith("C1") else actors["C2"]
    r=run(network,k,mode,5700000+100*k,base)
    file.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
   results.append({key:value for key,value in r.items() if key not in
    ("D_curve","churn_curve","occupied_curve",
     "final_D_worlds","final_occupied_worlds","exact_final_worlds")})
   print("DELTA500_HOLDOUT",k,mode,
    "D",round(r["D_final"],4),"D_IID_ratio",round(r["ratio_to_iid10"],3),
    "occupied",round(r["occupied_final_mean"],2),
    "exact",r["exact_count_final"],
    "stable",r["stable_strict_count"],
    "churn",round(r["churn_tail10"],3),
    "seconds",round(time.perf_counter()-t0,1),flush=True)
 out=OUT/"SUMMARY.json"
 if out.exists():raise RuntimeError("Refuse summary overwrite")
 out.write_text(json.dumps(
   {"lock":lock,"rows":results,
    "interpretation":"Exploratory pilot after V4 10k failure. One training seed; 100 test worlds share weights."},
     indent=2,ensure_ascii=False),encoding="utf-8")
 print("DELTA500_HOLDOUT_DONE",len(results),flush=True)
if __name__=="__main__":main()
