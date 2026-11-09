"""P0 exploratory training/known-k validation only. HELDOUT k5..8 unopened.

Fixes data split and policy parameters in PROTOCOL_V0.md. Produces theta,
train log and known-k validation. Do not tune using unseen-k test results.
"""
from pathlib import Path
import json,statistics,time
import numpy as np
from model import Society,Parameters,train_individual_policies,INITIAL_THETA
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"results_p0"
OUT.mkdir(exist_ok=True)
parameters=Parameters()
t0=time.perf_counter()
cohort=20261109
theta,training=train_individual_policies(cohort,episodes_per_k=8,ticks=120,p=parameters)
np.savez_compressed(OUT/"trained_theta.npz",theta=theta,seed=cohort)
(OUT/"training_known.json").write_text(json.dumps(training,ensure_ascii=False,indent=2),encoding="utf-8")
print("TRAINED_KNOWN_ONLY",len(training),"theta_initial_mean",INITIAL_THETA.tolist(),
      "theta_final_mean",np.mean(theta,axis=0).round(3).tolist(),"time",round(time.perf_counter()-t0,2),flush=True)
policies=["stay","copy","random","minority","untrained","learned"]
results=[]
for k in (2,3,4):
 for s in range(4):
  seed=5000+100*k+s
  for policy in policies:
   soc=Society(k,seed,parameters,theta=theta if policy=="learned" else None)
   result=soc.run(140,policy,learning=False)
   results.append({key:value for key,value in result.items() if key!="colors_final"})
   print("KNOWN",k,seed,policy,"tv",round(result["tail_tv_mean"],3),
         "churn",round(result["tail_churn_mean"],3),
         "richness",round(result["tail_local_richness"],3),
         "stable",result["stable_at_end"],
         "elapsed",round(time.perf_counter()-t0,1),flush=True)
summary=[]
for k in (2,3,4):
 for policy in policies:
  rows=[r for r in results if r["k"]==k and r["policy"]==policy]
  summary.append({"k":k,"policy":policy,
   "n_seeds":len(rows),
   "mean_tail_tv":statistics.mean(r["tail_tv_mean"] for r in rows),
   "mean_tail_churn":statistics.mean(r["tail_churn_mean"] for r in rows),
   "mean_local_richness":statistics.mean(r["tail_local_richness"] for r in rows),
   "stable_count":sum(r["stable_at_end"] for r in rows)})
package={"status":"known-k pilot; k5..8 not used",
  "protocol":"PROTOCOL_V0.md","n":120,
  "train_episode_k_values":[r["k"] for r in training],
  "train_episodes":len(training),
  "training_seed":cohort,
  "eval_known_seeds":[5000+100*k+s for k in (2,3,4) for s in range(4)],
  "locked_hyperparams":parameters.__dict__,
  "theta_initial_mean":INITIAL_THETA.tolist(),
  "theta_trained_mean":np.mean(theta,axis=0).tolist(),
  "raw":results,"summary":summary}
(OUT/"known_validation.json").write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding="utf-8")
print("KNOWN_PILOT_SUMMARY",json.dumps(summary,ensure_ascii=False),flush=True)
print("KNOWN_PILOT_DONE",round(time.perf_counter()-t0,1),flush=True)
