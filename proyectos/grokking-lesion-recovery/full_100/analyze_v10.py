"""V10B model-level paired audit/analysis. Mask repetitions are nested in seed."""
from pathlib import Path
import json,statistics,math
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/"V10_LESION_RAW.json").read_text(encoding="utf-8"))
records=data["observations"]
p={(r["seed"],r["lambda"],r["dose"],r["mask"]):r for r in records}
issues=[]
for seed in range(5):
 for dose in (30,90,150):
  for mask in (101,102,103,104,105):
   a=p.get((seed,1e-5,dose,mask));b=p.get((seed,.001,dose,mask))
   if a is None or b is None:issues.append(f"missing {seed},{dose},{mask}");continue
   for r in (a,b):
    if len(r["indices"])!=dose or len(set(r["indices"]))!=dose:issues.append("wrong lesion")
    if any(r["base"][k]!=1. for k in ("train_acc","val_acc","test_acc")):issues.append("not perfect initial")
    if r["mask"]!=mask:issues.append("wrong mask id")
    if not math.isfinite(r["mean_auc_val_control_deficit"]):issues.append("nonfinite")
   if a["indices"]!=b["indices"]:issues.append("not paired masks")
network=[]
for seed in range(5):
 for lam in (1e-5,.001):
  for dose in (30,90,150):
   group=[r for r in records if r["seed"]==seed and r["lambda"]==lam and r["dose"]==dose]
   if len(group)!=5:issues.append("rep count")
   damaged=[r for r in group if r["meaningful_damage"]]
   network.append({"seed":seed,"lambda":lam,"group":"grok" if lam==1e-5 else "continuous","dose":dose,
       "mean_initial_damage_pp":statistics.mean(z["initial_damage_val_pp"] for z in group),
       "median_initial_damage_pp":statistics.median(z["initial_damage_val_pp"] for z in group),
       "mean_auc":statistics.mean(z["mean_auc_val_control_deficit"] for z in group),
       "mean_normalized_auc_if_damage":statistics.mean(z["auc_per_unit_initial_damage"] for z in damaged) if damaged else None,
       "n_meaningful_damage":len(damaged),
       "n_recovered_meaningful":sum(z["recovery_two_consecutive_val99_step"] is not None for z in damaged),
       "recovery_steps_meaningful":[z["recovery_two_consecutive_val99_step"] for z in damaged],
       "mean_end_val":statistics.mean(z["injured_final"]["val_acc"] for z in group)})
paired=[]
for seed in range(5):
 for dose in (30,90,150):
  a=next(z for z in network if z["seed"]==seed and z["lambda"]==1e-5 and z["dose"]==dose)
  b=next(z for z in network if z["seed"]==seed and z["lambda"]==.001 and z["dose"]==dose)
  matched=[(p[(seed,1e-5,dose,mask)],p[(seed,.001,dose,mask)]) for mask in (101,102,103,104,105)]
  both=[(x,y) for x,y in matched if x["meaningful_damage"] and y["meaningful_damage"]]
  paired.append({"seed":seed,"dose":dose,"A_minus_B_damage_pp":a["mean_initial_damage_pp"]-b["mean_initial_damage_pp"],
       "A_minus_B_auc":a["mean_auc"]-b["mean_auc"],"both_meaningfully_damaged_masks":len(both),
       "normalized_auc_A_minus_B_both_damaged":statistics.mean(x["auc_per_unit_initial_damage"]-y["auc_per_unit_initial_damage"] for x,y in both) if both else None})
by_dose={}
for dose in (30,90,150):
 z=[p for p in paired if p["dose"]==dose]
 by_dose[str(dose)]={
    "means":{"A_initial_damage_pp":statistics.mean(n["mean_initial_damage_pp"] for n in network if n["dose"]==dose and n["group"]=="grok"),
             "B_initial_damage_pp":statistics.mean(n["mean_initial_damage_pp"] for n in network if n["dose"]==dose and n["group"]=="continuous"),
             "A_auc":statistics.mean(n["mean_auc"] for n in network if n["dose"]==dose and n["group"]=="grok"),
             "B_auc":statistics.mean(n["mean_auc"] for n in network if n["dose"]==dose and n["group"]=="continuous")},
    "network_paired_damage_pp":[n["A_minus_B_damage_pp"] for n in z],
    "network_paired_auc":[n["A_minus_B_auc"] for n in z],
    "total_masks_damaged_both":sum(n["both_meaningfully_damaged_masks"] for n in z),
    "paired_norm_auc_diffs_if_both_damaged":[n["normalized_auc_A_minus_B_both_damaged"] for n in z if n["normalized_auc_A_minus_B_both_damaged"] is not None]}
aud={"status":"PASS" if len(records)==150 and not issues else "FAIL",
     "n_lesions":len(records),"n_independent_seed_pairs":5,"n_mask_pairs":75,
     "issues":issues,"status_claim":"not a causal estimate of grokking: L1 differs"}
result={"audit":aud,"by_dose":by_dose,"by_network":network,"paired_seed":paired}
(ROOT/"V10_ANALYSIS.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({"audit":aud,"by_dose":by_dose,"by_network":network},indent=2,ensure_ascii=False))
