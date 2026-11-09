from pathlib import Path
import csv,json,statistics
ROOT=Path(__file__).resolve().parent
rows=[]
for p in sorted((ROOT/"gated_runs").glob("*/metrics.csv")):
 with p.open(encoding="utf-8",newline="") as f:r=list(csv.DictReader(f))
 if not r:continue
 def first(col,t):
  return next((int(x["step"]) for x in r if float(x[col])>=t),None)
 tail=r[-10:]
 vals=[float(x["val_acc"]) for x in tail]
 dur=len(vals)==10 and max(vals)-min(vals)<=0.02 and abs(statistics.mean(vals[:5])-statistics.mean(vals[5:]))<=.01
 d={"name":p.parent.name,"train_fit99":first("train_acc",.99),"clean_train99":first("clean_train_acc",.99),"clean_val10":first("clean_val_acc",.10),"clean_val50":first("clean_val_acc",.50),"clean_val90":first("clean_val_acc",.90),"global_val55":first("val_acc",.55),"last_val":float(r[-1]["val_acc"]),"last_train":float(r[-1]["train_acc"]),"durable_last10":dur}
 rows.append(d);print(json.dumps(d),flush=True)
(ROOT/"V6_TRAJECTORY_TABLE.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
