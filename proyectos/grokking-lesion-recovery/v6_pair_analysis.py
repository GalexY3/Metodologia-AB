"""Paired, descriptive lesion analysis. Masks nested in ONE network per condition."""
from pathlib import Path
import csv,statistics,json
ROOT=Path(__file__).resolve().parent
models={
 "wd1":"cleanWD1.0_noiseWD0.05_init1.0_s0_train0.55_ck_022000",
 "wd2.5":"cleanWD2.5_noiseWD0.05_init1.0_s0_train0.55_ck_022000"}
records=[]
for model,label in models.items():
 for seed in range(101,106):
  d=ROOT/"gated_lesions"/(label+f"_c60_n0_mask{seed}")
  if not (d/"summary.json").exists():raise FileNotFoundError(d)
  with (d/"metrics.csv").open(newline="",encoding="utf-8") as f:allrows=list(csv.DictReader(f))
  a=[r for r in allrows if r["arm"]=="lesion"]
  b=[r for r in allrows if r["arm"]=="no_lesion"]
  start_clean=float(b[0]["clean_val_acc"])
  damaged_clean=float(a[0]["clean_val_acc"])
  th=0.95*start_clean
  t=next((int(r["step"]) for r in a if float(r["clean_val_acc"])>=th),None)
  # AUC of CLEAN conditional performance deficit relative to untreated training
  area=0.
  for i in range(1,len(a)):
   delta0=float(b[i-1]["clean_val_acc"])-float(a[i-1]["clean_val_acc"])
   delta1=float(b[i]["clean_val_acc"])-float(a[i]["clean_val_acc"])
   area+=(delta0+delta1)/2*(int(a[i]["step"])-int(a[i-1]["step"]))
  injury=(start_clean-damaged_clean)
  records.append({"model":model,"mask":seed,"baseline_global":float(b[0]["val_acc"]),"damage_global_pp":100*(float(b[0]["val_acc"])-float(a[0]["val_acc"])),"damage_clean_pp":injury*100,"recov_clean":t,"auc_clean":area,"normalized_auc":area/injury if injury>0 else None,"end_clean":float(a[-1]["clean_val_acc"]),"end_control_clean":float(b[-1]["clean_val_acc"])})
summary={}
for m in models:
 dat=[d for d in records if d["model"]==m]
 summary[m]={"masks":len(dat),"mean_damage_global_pp":statistics.mean(r["damage_global_pp"] for r in dat),"mean_damage_clean_pp":statistics.mean(r["damage_clean_pp"] for r in dat),"recovered_clean_95pct":sum(r["recov_clean"] is not None for r in dat),"clean_recovery_steps":[r["recov_clean"] for r in dat],"mean_clean_auc_step":statistics.mean(r["auc_clean"] for r in dat),"mean_normalized_auc_step":statistics.mean(r["normalized_auc"] for r in dat if r["normalized_auc"] is not None),"mean_clean_end":statistics.mean(r["end_clean"] for r in dat)}
paired=[]
for seed in range(101,106):
 x=next(z for z in records if z["model"]=="wd1" and z["mask"]==seed)
 y=next(z for z in records if z["model"]=="wd2.5" and z["mask"]==seed)
 paired.append({"mask":seed,"difference_auc_clean_wd1_minus_wd2_5":x["auc_clean"]-y["auc_clean"],"difference_initial_damage_pp":x["damage_clean_pp"]-y["damage_clean_pp"],"difference_normalized_auc":x["normalized_auc"]-y["normalized_auc"]})
result={"scope":"exploratory N=1 trained network per condition; 5 repeated random masks are NOT n=5 independent networks; both histories show delayed generalization","results":records,"by_model":summary,"paired_mask_differences":paired}
(ROOT/"V6_PAIR_DAMAGE_ANALYSIS.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({"by_model":summary,"paired_masks":paired},indent=2,ensure_ascii=False))
