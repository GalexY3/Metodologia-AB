import json
from pathlib import Path
d=json.loads((Path(__file__).resolve().parent/"longitudinal_v2e"/"SUMMARY.json").read_text(encoding="utf-8"))
times=(0,1,2,3,5,8,10,12,16,20,24,30,40,50,60,80,100,120,160,200,240)
for k in (2,3,4):
 print("===== K",k,"PROGRESS_PERCENT =====")
 q={r["mode"]:r for r in d["summary"] if r["k"]==k}
 for t in times:
  print(json.dumps({"x":t,**{a:round(q[a]["progress_curve_mean"][t],1) for a in ("credit2","credit0","random_always","random_T24","stay")}},separators=(",",":")))
 if k==4:
  print("===== K4_CHURN =====")
  for t in times:
   print(json.dumps({"x":t,**{a:round(q[a]["churn_curve_mean"][t]*100,1) for a in ("credit2","credit0","random_always","random_T24","stay")}},separators=(",",":")))
