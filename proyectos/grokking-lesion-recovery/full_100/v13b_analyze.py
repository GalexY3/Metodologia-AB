"""V13B fixed-n prospective mask audit and 90% long-horizon sensitivity.

This analysis is POSTHOC to V13, precommitted before V13B new masks.
No need for test partition, masks are nested within network seed pairs.
"""
from pathlib import Path
import json,statistics,math,itertools
ROOT=Path(__file__).resolve().parent
FOLDER=ROOT/"v13b_long_runs"
seeds=[11,12,13,14,18]
arms=[1e-5,.001]
masks=[4201,4202,4203,4204]
rows=[];bad=[]
for seed in seeds:
 for arm in arms:
  folder=FOLDER/f"seed{seed}_prior{arm:g}"
  if not (folder/"control.csv").is_file():bad.append(f"control missing {folder}")
  for ms in masks:
   file=folder/f"kill270_mask{ms}.json"
   curve=folder/f"kill270_mask{ms}.csv"
   if not file.is_file() or not curve.is_file():
    bad.append(f"missing {seed} {arm} {ms}")
    continue
   x=json.loads(file.read_text(encoding="utf-8"))
   rows.append(x)
   if x["seed"]!=seed or x["initial_lambda"]!=arm or x["maskseed"]!=ms:
    bad.append("metadata mismatch "+str(file))
   if len(x["indices"])!=270 or len(set(x["indices"]))!=270:
    bad.append("mask mismatch "+str(file))
   if not all(math.isfinite(x[k]) for k in
       ("initial_val_damage_pp","auc_0_500","auc_500_1000","auc_1000_2000","auc_0_2000","injured_val_final")):
    bad.append("nonfinite "+str(file))
   if abs(x["auc_0_2000"]-(x["auc_0_500"]+x["auc_500_1000"]+x["auc_1000_2000"]))>1e-7:
    bad.append("auc range mismatch "+str(file))
   if x["repair_l1"]!=.0001 or x["common_l1"]!=.0001 or x["control_val_final"]!=1.:
    bad.append("control issue "+str(file))
records={(x["seed"],x["initial_lambda"],x["maskseed"]):x for x in rows}
for seed in seeds:
 for ms in masks:
  a=records.get((seed,1e-5,ms));b=records.get((seed,.001,ms))
  if a is not None and b is not None and a["indices"]!=b["indices"]:
   bad.append("Different physical masks "+str((seed,ms)))
pernetwork=[]
for seed in seeds:
 for arm in arms:
  subset=[records[(seed,arm,ms)] for ms in masks if (seed,arm,ms) in records]
  if len(subset)!=4:bad.append("subset count "+str((seed,arm)))
  row={"seed":seed,"lambda":arm,
       "initial_damage_mean_pp":statistics.mean(v["initial_val_damage_pp"] for v in subset),
       "mean_auc_2000":statistics.mean(v["auc_0_2000"] for v in subset),
       "mean_auc_500":statistics.mean(v["auc_0_500"] for v in subset),
       "mean_final_val_acc":statistics.mean(v["injured_val_final"] for v in subset),
       "mean_restricted_time_2000":statistics.mean(v["recovery99_step"] if v["recovery99_step"] is not None else 2000 for v in subset),
       "n_mask":len(subset)}
  for horizon in (500,1000,1500,2000):
   row[f"recovered_by_{horizon}"]=sum(v[f"recovered_by_{horizon}"] for v in subset)
  pernetwork.append(row)
paired=[]
for seed in seeds:
 A=next(z for z in pernetwork if z["seed"]==seed and z["lambda"]==1e-5)
 B=next(z for z in pernetwork if z["seed"]==seed and z["lambda"]==.001)
 paired.append({"seed":seed,"A_minus_B_auc_2000":A["mean_auc_2000"]-B["mean_auc_2000"],
                "A_minus_B_restricted_time":A["mean_restricted_time_2000"]-B["mean_restricted_time_2000"],
                "A_minus_B_initial_damage_pp":A["initial_damage_mean_pp"]-B["initial_damage_mean_pp"]})
def stats(seq):
 return {"mean":statistics.mean(seq),"values":list(seq),"min":min(seq),"max":max(seq)}
diff=[z["A_minus_B_auc_2000"] for z in paired]
null=[abs(statistics.mean(s*v for s,v in zip(sign,diff))) for sign in itertools.product((-1,1),repeat=5)]
p=sum(v>=abs(statistics.mean(diff))-1e-10 for v in null)/len(null)
agg={"paired_independent_network_n":5,"n_mask_pairs":20,"n_lesion_curves":40,
     "A_initial_damage_mean_pp":statistics.mean(z["initial_damage_mean_pp"] for z in pernetwork if z["lambda"]==1e-5),
     "B_initial_damage_mean_pp":statistics.mean(z["initial_damage_mean_pp"] for z in pernetwork if z["lambda"]==.001),
     "A_auc_2000_mean":statistics.mean(z["mean_auc_2000"] for z in pernetwork if z["lambda"]==1e-5),
     "B_auc_2000_mean":statistics.mean(z["mean_auc_2000"] for z in pernetwork if z["lambda"]==.001),
     "paired_auc_2000_diff":stats(diff),
     "exact_p_two_sided_exploratory":p,
     "A_recovered_at_horizons":{str(t):sum(z[f"recovered_by_{t}"] for z in pernetwork if z["lambda"]==1e-5) for t in (500,1000,1500,2000)},
     "B_recovered_at_horizons":{str(t):sum(z[f"recovered_by_{t}"] for z in pernetwork if z["lambda"]==.001) for t in (500,1000,1500,2000)},
     "A_restricted_time_mean":statistics.mean(z["mean_restricted_time_2000"] for z in pernetwork if z["lambda"]==1e-5),
     "B_restricted_time_mean":statistics.mean(z["mean_restricted_time_2000"] for z in pernetwork if z["lambda"]==.001),
     "seeds_A_lower_auc":sum(z<0 for z in diff),
     "seeds_B_lower_auc":sum(z>0 for z in diff)}
audit={"status":"PASS" if len(rows)==40 and not bad else "FAIL","errors":bad,"n_runs":len(rows),"protocol":"PREREG_V13B_LONG_RECOVERY.md"}
out={"audit":audit,"per_network":pernetwork,"paired":paired,"aggregate":agg,
     "interpretation":"The V13B 2000-step follow-up is posthoc relative to V13, with new masks; no universal irrecoverability; historical initial L1 confounded."}
(ROOT/"V13B_ANALYSIS.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("V13B_AUDIT",audit["status"],"n",len(rows),flush=True)
print("V13B_SUMMARY",json.dumps(agg,ensure_ascii=False,indent=2),flush=True)
print("V13B_PER_SEED",json.dumps(paired,ensure_ascii=False,indent=2),flush=True)
