"""V12B local auditor and clustered paired analysis. N = trained network pairs,
not the number of neuronal masks. Test partition remains untouched.
"""
from pathlib import Path
import json,statistics,itertools,math
ROOT=Path(__file__).resolve().parent
v=json.loads((ROOT/"V12B_RAW.json").read_text(encoding="utf-8"))
raw=v["results"]
seeds=v["eligible_network_seeds"]
index={(r["seed"],r["prior_lambda"],r["maskseed"]):r for r in raw}
problems=[];per_seed=[]
for seed in seeds:
 pairs=[]
 for m in range(3201,3211):
  a=index.get((seed,1e-5,m));b=index.get((seed,.001,m))
  if a is None or b is None:problems.append(f"missing {seed}/{m}");continue
  if a["indices"]!=b["indices"] or len(a["indices"])!=90 or len(set(a["indices"]))!=90:
   problems.append(f"bad-mask {seed}/{m}")
  if a["common_l1"]!=.0001 or b["common_l1"]!=.0001:problems.append("wrong common λ")
  if a["repair_l1"]!=.0001 or b["repair_l1"]!=.0001:problems.append("wrong repair λ")
  if a["control_val_final"]<1 or b["control_val_final"]<1:problems.append(f"control-degraded {seed}/{m}")
  if not all(math.isfinite(r["auc_val_deficit_vs_control"]) for r in (a,b)):problems.append("nonfinite")
  pairs.append((a,b))
 if len(pairs)!=10:problems.append(f"missing-runs seed={seed}")
 both=[(a,b) for a,b in pairs if a["initial_val_damage_pp"]>2 and b["initial_val_damage_pp"]>2]
 def avg(which,k):return statistics.mean(z[which][k] for z in pairs)
 a_damage=avg(0,"initial_val_damage_pp")
 b_damage=avg(1,"initial_val_damage_pp")
 a_auc=avg(0,"auc_val_deficit_vs_control")
 b_auc=avg(1,"auc_val_deficit_vs_control")
 per_seed.append({"seed":seed,"masks":len(pairs),
   "damage_A_pp":a_damage,"damage_B_pp":b_damage,
   "auc_A":a_auc,"auc_B":b_auc,"auc_A_minus_B":a_auc-b_auc,
   "masks_both_damaged_gt2pp":len(both),
   "normalized_auc_difference_if_both_damaged":statistics.mean(a["normalized_auc_if_damage_gt2pp"]-b["normalized_auc_if_damage_gt2pp"] for a,b in both) if both else None,
   "A_damaged_gt2pp":sum(a["initial_val_damage_pp"]>2 for a,b in pairs),
   "B_damaged_gt2pp":sum(b["initial_val_damage_pp"]>2 for a,b in pairs),
   "A_recovered_given_damage":sum(a["recovery_step_two_consecutive"] is not None for a,b in pairs if a["initial_val_damage_pp"]>2),
   "B_recovered_given_damage":sum(b["recovery_step_two_consecutive"] is not None for a,b in pairs if b["initial_val_damage_pp"]>2)})
deltas=[z["auc_A_minus_B"] for z in per_seed]
def signflip(xs):
 if not xs:return None
 s=abs(statistics.mean(xs))
 values=[abs(statistics.mean(e*x for e,x in zip(signs,xs))) for signs in itertools.product((-1,1),repeat=len(xs))]
 return sum(z>=s-1e-12 for z in values)/len(values)
out={"audit":{"status":"PASS" if not problems and len(raw)==20*len(seeds) else "FAIL",
    "issues":problems,"n_network_pair_seeds":len(seeds),"n_lesions":len(raw),
    "test_partition_not_used":True},
   "per_seed":per_seed,
   "overall":{"mean_AUC_A":statistics.mean(z["auc_A"] for z in per_seed) if per_seed else None,
     "mean_AUC_B":statistics.mean(z["auc_B"] for z in per_seed) if per_seed else None,
     "mean_paired_AUC_A_minus_B":statistics.mean(deltas) if deltas else None,
     "paired_auc_differences":deltas,
     "mean_initial_damage_A_pp":statistics.mean(z["damage_A_pp"] for z in per_seed) if per_seed else None,
     "mean_initial_damage_B_pp":statistics.mean(z["damage_B_pp"] for z in per_seed) if per_seed else None,
     "favor_A_seeds":sum(z<0 for z in deltas),
     "favor_B_seeds":sum(z>0 for z in deltas),
     "exact_signflip_p_two_sided_exploratory":signflip(deltas),
     "recovered_A":sum(z["A_recovered_given_damage"] for z in per_seed),
     "recovered_B":sum(z["B_recovered_given_damage"] for z in per_seed),
     "damaged_A":sum(z["A_damaged_gt2pp"] for z in per_seed),
     "damaged_B":sum(z["B_damaged_gt2pp"] for z in per_seed)},
    "limits":"regimes remain confounded by historical L1; masked perturbations nested within five networks; n!=100; no equivalence test."}
(ROOT/"V12B_ANALYSIS.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
print("V12B_SUMMARY",json.dumps({"audit":out["audit"],"per_seed":per_seed,"overall":out["overall"]},ensure_ascii=False),flush=True)
