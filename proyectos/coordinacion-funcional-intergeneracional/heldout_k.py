"""One-shot zero-update evaluation at unseen k=5,6,7,8.

Check known validation and trained-theta existence BEFORE consulting unseen
episodes. No hyperparameter tuning, no learning updates or training on k>4.
"""
from pathlib import Path
import json,time,statistics,hashlib
import numpy as np
from model import Society,Parameters
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"results_p0"
prior=json.loads((OUT/"known_validation.json").read_text(encoding="utf-8"))
assert prior["status"]=="known-k pilot; k5..8 not used"
assert set(prior["train_episode_k_values"])=={2,3,4}
weightsfile=OUT/"trained_theta.npz"
theta=np.load(weightsfile)["theta"]
initial_hash=hashlib.sha256(weightsfile.read_bytes()).hexdigest()
lock={
 "model_sha256":hashlib.sha256((ROOT/"model.py").read_bytes()).hexdigest(),
 "training_theta_npz_sha256":initial_hash,
 "train_episodes":prior["train_episodes"],
 "train_k":[2,3,4],
 "heldout_k":[5,6,7,8],
 "heldout_seed_range":"6000+k*100+s, s=0..9",
 "num_seeds_per_k":10,
 "policy":["stay","copy","random","minority","untrained","learned"],
 "evaluation_learning":False,
 "ticks":140,
 "locked_params":prior["locked_hyperparams"],
 "success":"TV<=0.06 and churn<=0.05 for the final 10 ticks"}
lockpath=OUT/"HELDOUT_LOCK.json"
if lockpath.exists():raise RuntimeError("Heldout already opened; no repeat without explicit audit")
lockpath.write_text(json.dumps(lock,ensure_ascii=False,indent=2),encoding="utf-8")
print("HELDOUT_LOCKED",lock,flush=True)
start=time.perf_counter()
policies=lock["policy"]
records=[]
for k in lock["heldout_k"]:
 for s in range(10):
  seed=6000+k*100+s
  for policy in policies:
   society=Society(k,seed,Parameters(),theta=theta if policy=="learned" else None)
   weights_start=society.theta.copy()
   result=society.run(140,policy=policy,learning=False)
   if not np.array_equal(weights_start,society.theta):
    raise RuntimeError("Evaluation leaked learned parameter updates")
   compact={key:value for key,value in result.items() if key!="colors_final"}
   compact["train_cohort_seed"]=20261109
   records.append(compact)
   if policy=="learned" or policy=="minority":
    print("HELDOUT",k,seed,policy,"tv",round(result["tail_tv_mean"],3),
      "churn",round(result["tail_churn_mean"],3),
      "stable",result["stable_at_end"],
      "elapsed",round(time.perf_counter()-start,1),flush=True)
summaries=[]
for k in lock["heldout_k"]:
 for policy in policies:
  subset=[z for z in records if z["k"]==k and z["policy"]==policy]
  summaries.append({"k":k,"policy":policy,"n":len(subset),
   "stable_count":sum(z["stable_at_end"] for z in subset),
   "mean_tail_tv":statistics.mean(z["tail_tv_mean"] for z in subset),
   "mean_tail_churn":statistics.mean(z["tail_churn_mean"] for z in subset),
   "mean_tail_richness":statistics.mean(z["tail_local_richness"] for z in subset)})
obj={"protocol":"PROTOCOL_V0.md","locked_source":lock,
 "test_seeds_per_k":10,"test_outcomes":records,"summary":summaries,
 "cautions":["One trained cohort is not an independent population of training seeds",
 "The minority heuristic was manually designed; learned weights have hand-designed rarity features",
 "Test is zero-shot with respect to weights, but local observations and memory adapt per tick",
 "Do not tweak policy using these test outcomes and then re-use them as untouched test"]}
(OUT/"heldout_once.json").write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
print("HELDOUT_SUMMARY",json.dumps(summaries,ensure_ascii=False),flush=True)
print("HELDOUT_P0_DONE",round(time.perf_counter()-start,1),flush=True)
