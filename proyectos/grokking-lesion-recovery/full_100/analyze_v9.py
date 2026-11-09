"""V9 exploratory analysis with network-level paired summaries and mask validation."""
from pathlib import Path
from collections import defaultdict
import json,statistics,csv,math
ROOT=Path(__file__).resolve().parent
d=json.loads((ROOT/"lesion_v9_summary.json").read_text(encoding="utf-8"))
records=d["observations"]
issues=[]
bykey={(z["seed"],z["wd"],z["dose"],z["mask_seed"]):z for z in records}
for seed in (0,1,2):
 for dose in (30,60,90):
  for mask in (101,102,103,104,105):
   a=bykey.get((seed,1.,dose,mask))
   b=bykey.get((seed,3.,dose,mask))
   if a is None or b is None:issues.append(f"missing {seed} {dose} {mask}");continue
   if len(set(a["neuron_indices"]))!=dose or a["neuron_indices"]!=b["neuron_indices"]:issues.append(f"mask mismatch {seed} {dose} {mask}")
   for z in (a,b):
    if z["before"]["val_accuracy"]!=1.:issues.append("before non100 val")
    if z["before"]["test_accuracy"]!=1.:issues.append("before non100 test")
    if z["before"]["train_accuracy"]!=1.:issues.append("before non100 train")
    if z["training_steps_at_lesion"]!=12000:issues.append("wrong training step")
    if not math.isfinite(z["auc_val_control_minus_lesion"]):issues.append("nonfinite AUC")
network=[]
for seed in (0,1,2):
 for wd in (1.,3.):
  for dose in (30,60,90):
   rs=[z for z in records if z["seed"]==seed and z["wd"]==wd and z["dose"]==dose]
   if len(rs)!=5:issues.append("count")
   network.append({"seed":seed,"wd":wd,"dose":dose,
                   "mean_damage_pp":statistics.mean(z["damage_val_pp"] for z in rs),
                   "mean_auc":statistics.mean(z["auc_val_control_minus_lesion"] for z in rs),
                   "meaningful_damage":sum(z["meaningful_initial_damage"] for z in rs),
                   "recovered_to99":sum(z["recovery_step_two_consecutive"] is not None for z in rs),
                   "mean_recovery_steps_all":statistics.mean(z["recovery_step_two_consecutive"] for z in rs if z["recovery_step_two_consecutive"] is not None),
                   "median_damage_pp":statistics.median(z["damage_val_pp"] for z in rs)})
paired=[]
for seed in (0,1,2):
 for dose in (30,60,90):
  a=next(z for z in network if z["seed"]==seed and z["wd"]==1 and z["dose"]==dose)
  b=next(z for z in network if z["seed"]==seed and z["wd"]==3 and z["dose"]==dose)
  paired.append({"seed":seed,"dose":dose,"damage_gap_wd1_minus_wd3_pp":a["mean_damage_pp"]-b["mean_damage_pp"],
                 "auc_gap_wd1_minus_wd3":a["mean_auc"]-b["mean_auc"]})
summary={}
for dose in (30,60,90):
 p=[z for z in paired if z["dose"]==dose]
 summary[dose]={"mean_paired_damage_gap_pp":statistics.mean(z["damage_gap_wd1_minus_wd3_pp"] for z in p),
                "per_seed_damage_gap_pp":[round(z["damage_gap_wd1_minus_wd3_pp"],3) for z in p],
                "mean_paired_auc_gap":statistics.mean(z["auc_gap_wd1_minus_wd3"] for z in p),
                "per_seed_auc_gap":[round(z["auc_gap_wd1_minus_wd3"],3) for z in p]}
status={"status":"PASS" if not issues and len(records)==90 else "FAIL","lesion_trials":len(records),"model_seeds":3,"paired_masks_per_dose":15,"issues":issues,
        "interpretation":"both WD1 and WD3 pathways grok; this is not grok vs non-grok"}
result={"audit":status,"network_summaries":network,"paired_seed_differences":paired,"by_dose":summary}
(ROOT/"V9_ANALYSIS.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({"audit":status,"by_dose":summary,"network_summaries":network},indent=2,ensure_ascii=False))
