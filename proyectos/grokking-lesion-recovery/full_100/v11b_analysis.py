"""V11B local auditor and network-level summaries. Not independent validation."""
from pathlib import Path
import json,statistics,math,collections
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/"V11B_RAW.json").read_text(encoding="utf-8"))["results"]
index={(z["seed"],z["prior_lambda"],z["maskseed"]):z for z in r}
issues=[]
per_seed=[]
for seed in range(5):
 pairs=[]
 for mask in range(2101,2111):
  a=index.get((seed,1e-5,mask));b=index.get((seed,.001,mask))
  if a is None or b is None:issues.append(f"missing {seed}/{mask}");continue
  if a["indices"]!=b["indices"] or len(a["indices"])!=90:issues.append(f"mask mismatch {seed}/{mask}")
  if a["baseline"]["val_acc"]!=1 or b["baseline"]["val_acc"]!=1:issues.append("baseline not 100")
  pairs.append((a,b))
 mean=lambda f:statistics.mean(f(a,b) for a,b in pairs)
 both=[(a,b) for a,b in pairs if a["initial_damage_val_pp"]>2 and b["initial_damage_val_pp"]>2]
 d={"seed":seed,"n_masks":len(pairs),
    "mean_initial_A_pp":mean(lambda a,b:a["initial_damage_val_pp"]),
    "mean_initial_B_pp":mean(lambda a,b:b["initial_damage_val_pp"]),
    "auc_A":mean(lambda a,b:a["auc_val"]),
    "auc_B":mean(lambda a,b:b["auc_val"]),
    "auc_A_minus_B":mean(lambda a,b:a["auc_val"]-b["auc_val"]),
    "both_damaged_n":len(both),
    "normalized_auc_A_minus_B_if_both_damaged":statistics.mean(a["normalized_auc_if_initial_damage"]-b["normalized_auc_if_initial_damage"] for a,b in both) if both else None,
    "n_lesions_damaged_A":sum(a["initial_damage_val_pp"]>2 for a,b in pairs),
    "n_lesions_damaged_B":sum(b["initial_damage_val_pp"]>2 for a,b in pairs),
    "n_recovered_damaged_A":sum(a["time_to99_2consecutive"] is not None for a,b in pairs if a["initial_damage_val_pp"]>2),
    "n_recovered_damaged_B":sum(b["time_to99_2consecutive"] is not None for a,b in pairs if b["initial_damage_val_pp"]>2),
    "last_unlesioned_val_A":pairs[0][0]["control_final"]["val_acc"],
    "last_unlesioned_val_B":pairs[0][1]["control_final"]["val_acc"]}
 per_seed.append(d)
out={"audit":{"status":"PASS" if len(r)==100 and not issues else "FAIL","n_lesions":len(r),"n_independent_seed_pairs":5,"errors":issues,"not_independent_audit":True},"per_seed":per_seed,
 "aggregate":{
  "mean_damage_A_pp":statistics.mean(d["mean_initial_A_pp"] for d in per_seed),
  "mean_damage_B_pp":statistics.mean(d["mean_initial_B_pp"] for d in per_seed),
  "mean_auc_A":statistics.mean(d["auc_A"] for d in per_seed),
  "mean_auc_B":statistics.mean(d["auc_B"] for d in per_seed),
  "mean_auc_A_minus_B":statistics.mean(d["auc_A_minus_B"] for d in per_seed),
  "seedwise_auc_A_minus_B":[d["auc_A_minus_B"] for d in per_seed],
  "A_lower_auc_seeds":sum(d["auc_A_minus_B"]<0 for d in per_seed),
  "seedwise_control_final_val_B":[d["last_unlesioned_val_B"] for d in per_seed],
  "seedwise_control_final_val_A":[d["last_unlesioned_val_A"] for d in per_seed]},
 "warning":"V11B repair uses ZERO L1 and may cause loss of generalization even without a lesion. V11C corrects this by maintaining common L1."
}
(ROOT/"V11B_ANALYSIS.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(out,indent=2,ensure_ascii=False))
