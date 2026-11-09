"""V7 exploratory paired multi-seed analysis (seeds 0..2, masks 101..105).
NEVER treat 15 mask repetitions as 15 independent model replications.
"""
from pathlib import Path
import csv,json,statistics,math
ROOT=Path(__file__).resolve().parent
SEEDS=(0,1,2);MASKS=(101,102,103,104,105);WDS=(1.0,2.5)
results=[];models=[]
def loadcsv(path):
 with path.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
for seed in SEEDS:
 for wd in WDS:
  label=f"cleanWD{wd}_noiseWD0.05_init1.0_s{seed}_train0.55"
  train=ROOT/"gated_runs"/label
  s=json.loads((train/"summary.json").read_text(encoding="utf-8"))["final"]
  models.append({"seed":seed,"wd":wd,"train_acc":s["train_acc"],"clean_val_acc":s["clean_val_acc"],"val_acc":s["val_acc"],"noise_train_acc":s["noise_train_acc"]})
  for mask in MASKS:
   path=ROOT/"gated_lesions"/f"{label}_ck_022000_c60_n0_mask{mask}"
   if not (path/"metrics.csv").exists():raise FileNotFoundError(path)
   data=loadcsv(path/"metrics.csv")
   a=[r for r in data if r["arm"]=="lesion"]
   b=[r for r in data if r["arm"]=="no_lesion"]
   init=float(b[0]["clean_val_acc"]);injured=float(a[0]["clean_val_acc"])
   delta=init-injured
   rec=next((int(row["step"]) for row in a if float(row["clean_val_acc"])>=.95*init),None)
   auc=0.
   for i in range(1,len(a)):
    d0=float(b[i-1]["clean_val_acc"])-float(a[i-1]["clean_val_acc"])
    d1=float(b[i]["clean_val_acc"])-float(a[i]["clean_val_acc"])
    auc+=(d0+d1)/2*(int(a[i]["step"])-int(a[i-1]["step"]))
   results.append({"seed":seed,"wd":wd,"mask":mask,"initial_damage_clean_pp":100*delta,"recovery_step":rec,"auc_clean_step":auc,"normalized_auc_step":auc/delta if delta>0 else None,"end_clean":float(a[-1]["clean_val_acc"]),"end_control_clean":float(b[-1]["clean_val_acc"])})
eligibility=[]
for seed in SEEDS:
 a=next(m for m in models if m["seed"]==seed and m["wd"]==1.)
 b=next(m for m in models if m["seed"]==seed and m["wd"]==2.5)
 okay=(a["train_acc"]>=.99 and b["train_acc"]>=.99 and a["clean_val_acc"]>=.98 and b["clean_val_acc"]>=.98 and .58<=a["val_acc"]<=.64 and .58<=b["val_acc"]<=.64 and abs(a["val_acc"]-b["val_acc"])<=.02)
 eligibility.append({"seed":seed,"eligible":okay,"acc_wd1":a["val_acc"],"acc_wd2_5":b["val_acc"]})
by_network=[]
for seed in SEEDS:
 for wd in WDS:
  data=[x for x in results if x["seed"]==seed and x["wd"]==wd]
  by_network.append({"seed":seed,"wd":wd,"mean_initial_damage_pp":statistics.mean(x["initial_damage_clean_pp"] for x in data),"mean_auc":statistics.mean(x["auc_clean_step"] for x in data),"mean_norm_auc":statistics.mean(x["normalized_auc_step"] for x in data if x["normalized_auc_step"] is not None),"recovered_95pct":sum(x["recovery_step"] is not None for x in data),"mean_end_clean":statistics.mean(x["end_clean"] for x in data)})
paired=[]
for seed in SEEDS:
 a=next(x for x in by_network if x["seed"]==seed and x["wd"]==1.)
 b=next(x for x in by_network if x["seed"]==seed and x["wd"]==2.5)
 paired.append({"seed":seed,"difference_damage_pp_A_minus_B":a["mean_initial_damage_pp"]-b["mean_initial_damage_pp"],"difference_auc_A_minus_B":a["mean_auc"]-b["mean_auc"],"difference_normalized_auc_A_minus_B":a["mean_norm_auc"]-b["mean_norm_auc"]})
agg={"model_unit_n":len(SEEDS),"masks_per_model":len(MASKS),
 "mean_auc_difference":statistics.mean(x["difference_auc_A_minus_B"] for x in paired),
 "range_auc_difference":[min(x["difference_auc_A_minus_B"] for x in paired),max(x["difference_auc_A_minus_B"] for x in paired)],
 "mean_norm_auc_difference":statistics.mean(x["difference_normalized_auc_A_minus_B"] for x in paired)}
status="ELIGIBLE_FOR_DELAYED_VS_SHORTER_DELAY_PILOT" if all(x["eligible"] for x in eligibility) else "INELIGIBLE_PAIR_PRESENT"
res={"status":status,"scope":"Exploratory; both arms can show delayed generalization; artificial ceiling; WD treatment differs","model_summaries":models,"gates":eligibility,"individual_masks":results,"by_network":by_network,"seed_paired":paired,"aggregate_descriptive":agg}
(ROOT/"V7_ANALYSIS.json").write_text(json.dumps(res,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({"status":status,"gates":eligibility,"by_network":by_network,"seed_paired":paired,"aggregate_descriptive":agg},indent=2,ensure_ascii=False))
