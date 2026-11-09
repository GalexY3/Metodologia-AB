"""V10C: analytic and integrity audit of damage-matched lesion experiment.
Network seed is the independent replication (n=5); masks are clustered.
"""
from pathlib import Path
import json,statistics,math
ROOT=Path(__file__).resolve().parent
scan=json.loads((ROOT/"V10C_MASK_SCAN.json").read_text(encoding="utf-8"))
raw=json.loads((ROOT/"V10C_MATCHED_RAW.json").read_text(encoding="utf-8"))["results"]
assert len(raw)==50
bykey={(r["seed"],r["lambda"],r["mask_seed"]):r for r in raw}
issues=[]
pairrows=[]
for seedobj in scan["per_seed"]:
 seed=seedobj["seed"]
 for m in seedobj["selected_first5"]:
  mask=m["mask"]
  a=bykey.get((seed,1e-5,mask))
  b=bykey.get((seed,.001,mask))
  if a is None or b is None:issues.append(f"missing {seed}/{mask}");continue
  if (a["indices"]!=b["indices"] or len(set(a["indices"]))!=150
      or abs(a["initial_val_damage_pp"]-b["initial_val_damage_pp"])>5.001
      or not 9.999<=a["initial_val_damage_pp"]<=40.001
      or not 9.999<=b["initial_val_damage_pp"]<=40.001):
   issues.append(f"bad match {seed}/{mask}")
  aw=set(a["incorrect_val_case_indices"])
  bw=set(b["incorrect_val_case_indices"])
  overlap=len(aw&bw)
  union=len(aw|bw)
  pairrows.append({
   "seed":seed,"mask":mask,
   "damage_A_pp":a["initial_val_damage_pp"],"damage_B_pp":b["initial_val_damage_pp"],
   "damage_gap_pp":a["initial_val_damage_pp"]-b["initial_val_damage_pp"],
   "val_error_jaccard":overlap/union if union else 1.,
   "different_wrong_cases":len(aw^bw),
   "auc_A":a["auc_val"],"auc_B":b["auc_val"],
   "auc_gap_A_minus_B":a["auc_val"]-b["auc_val"],
   "normalized_auc_gap_A_minus_B":a["normalized_auc_val"]-b["normalized_auc_val"],
   "test_auc_gap_A_minus_B":a["auc_test"]-b["auc_test"],
   "recovery_step_A":a["recovery99_val_step"],
   "recovery_step_B":b["recovery99_val_step"],
   "recovered_A":a["recovery99_val_step"] is not None,
   "recovered_B":b["recovery99_val_step"] is not None,
  })
per_seed=[]
for seed in range(5):
 p=[r for r in pairrows if r["seed"]==seed]
 if len(p)!=5:issues.append(f"seed {seed} count {len(p)}")
 per_seed.append({
  "seed":seed,"n_masks":len(p),
  "mean_damage_A_pp":statistics.mean(r["damage_A_pp"] for r in p),
  "mean_damage_B_pp":statistics.mean(r["damage_B_pp"] for r in p),
  "mean_abs_damage_gap_pp":statistics.mean(abs(r["damage_gap_pp"]) for r in p),
  "mean_error_case_jaccard":statistics.mean(r["val_error_jaccard"] for r in p),
  "mean_A_auc":statistics.mean(r["auc_A"] for r in p),
  "mean_B_auc":statistics.mean(r["auc_B"] for r in p),
  "mean_paired_auc_A_minus_B":statistics.mean(r["auc_gap_A_minus_B"] for r in p),
  "mean_normalized_auc_gap_A_minus_B":statistics.mean(r["normalized_auc_gap_A_minus_B"] for r in p),
  "mean_test_auc_gap_A_minus_B":statistics.mean(r["test_auc_gap_A_minus_B"] for r in p),
  "recovered_A":sum(r["recovered_A"] for r in p),
  "recovered_B":sum(r["recovered_B"] for r in p),
  # 410 denotes no observed recovery by end of horizon, not a measured event at 410.
  "restricted_time_to_recovery_A":statistics.mean(r["recovery_step_A"] if r["recovery_step_A"] is not None else 410 for r in p),
  "restricted_time_to_recovery_B":statistics.mean(r["recovery_step_B"] if r["recovery_step_B"] is not None else 410 for r in p),
 })
aggregate={
 "n_independent_seed_pairs":len(per_seed),
 "n_matched_mask_pairs":len(pairrows),
 "mean_paired_AUC_gap":statistics.mean(x["mean_paired_auc_A_minus_B"] for x in per_seed),
 "mean_paired_normalized_AUC_gap":statistics.mean(x["mean_normalized_auc_gap_A_minus_B"] for x in per_seed),
 "mean_initial_damage_A_pp":statistics.mean(x["mean_damage_A_pp"] for x in per_seed),
 "mean_initial_damage_B_pp":statistics.mean(x["mean_damage_B_pp"] for x in per_seed),
 "average_wrong_case_jaccard":statistics.mean(x["mean_error_case_jaccard"] for x in per_seed),
 "seeds_with_A_lower_AUC":sum(x["mean_paired_auc_A_minus_B"]<0 for x in per_seed),
 "seeds_with_B_lower_AUC":sum(x["mean_paired_auc_A_minus_B"]>0 for x in per_seed),
 "recovered_A_total":sum(x["recovered_A"] for x in per_seed),
 "recovered_B_total":sum(x["recovered_B"] for x in per_seed),
}
aud={"status":"PASS" if not issues else "FAIL","issues":issues,
  "n_seeds":5,"masks_per_seed":5,"same_mask_physical":True,"mask_selection_blind_to_recovery":True,
  "scope":"post hoc lesion severity matching; strength L1 still differs between groups"}
final={"audit":aud,"summary":aggregate,"per_seed":per_seed,"paired_masks":pairrows,
       "important":"Matching only accuracy damage does not equate error identities, losses or gradient geometry. Correlation not causation; masks nested in 5 seeds."}
(ROOT/"V10C_MATCHED_ANALYSIS.json").write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"audit":aud,"summary":aggregate,"per_seed":per_seed},ensure_ascii=False,indent=2))
