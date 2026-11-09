"""Apply prospectively documented V10B eligibility gates based on training/validation curves.
Outputs are exploratory: test accuracy was logged during initial training.
"""
from pathlib import Path
import csv,json,statistics
ROOT=Path(__file__).resolve().parent
rows=[]
for seed in range(5):
 for lam in (1e-5,.001):
  name=f"lambda{lam:g}_seed{seed}_lr0.001_width300_nt500"
  p=ROOT/"parity_runs"/name
  if not (p/"metrics.csv").exists():
   rows.append({"seed":seed,"lam":lam,"name":name,"present":False,"eligible":False});continue
  with (p/"metrics.csv").open(newline="",encoding="utf-8") as f:
   hist=list(csv.DictReader(f))
  z=[{k:float(v) for k,v in r.items()} for r in hist]
  fit=next((int(x["step"]) for x in z if x["train_acc"]>=.99),None)
  gen95=next((int(x["step"]) for x in z if x["val_acc"]>=.95),None)
  gen100=next((int(x["step"]) for x in z if x["val_acc"]>=1.),None)
  lag=gen95-fit if fit is not None and gen95 is not None else None
  post=[r for r in z if fit is not None and fit<=r["step"]<=fit+1000]
  delayedlow= bool(post) and (max((r["step"] for r in post if r["val_acc"]<=.65),default=fit)-fit>=1000)
  finalok=(len(z)>=5 and all(r["train_acc"]==1. and r["val_acc"]==1. for r in z[-5:]) and z[-1]["test_acc"]==1.)
  history_ok= (lag is not None and lag>=1000 and delayedlow) if lam==1e-5 else (lag is not None and lag<1000 and not delayedlow)
  info={"seed":seed,"lam":lam,"name":name,"present":True,"train99_step":fit,"val95_step":gen95,
      "val100_step":gen100,"lag_to_val95":lag,"delayed_val_below65_for1000":delayedlow,
      "final_train":z[-1]["train_acc"],"final_val":z[-1]["val_acc"],"final_test":z[-1]["test_acc"],
      "last5_full":finalok,"history_gate":history_ok,"eligible":bool(history_ok and finalok)}
  rows.append(info)
pair_gates=[]
for seed in range(5):
 a=next(i for i in rows if i["seed"]==seed and i["lam"]==1e-5)
 b=next(i for i in rows if i["seed"]==seed and i["lam"]==.001)
 pair_gates.append({"seed":seed,"paired_eligible":a["eligible"] and b["eligible"]})
result={"individual":rows,"pairs":pair_gates,"eligible_seeds":[r["seed"] for r in pair_gates if r["paired_eligible"]]}
(ROOT/"V10_ELIGIBILITY.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2,ensure_ascii=False))
