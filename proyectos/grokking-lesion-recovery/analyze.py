"""Summarize completed exploratory runs without claiming matched semi-grokking."""
from pathlib import Path
import csv,json,statistics,hashlib,datetime
ROOT=Path(__file__).resolve().parent
TRAIN=[]
for p in sorted((ROOT/"runs").glob("*/metrics.csv")):
    with p.open(encoding="utf-8",newline="") as f:rows=list(csv.DictReader(f))
    if len(rows)<6:continue
    items=[{k:float(v) for k,v in row.items()} for row in rows]
    w=5;eligible=[]
    for i in range(0,len(items)-w+1):
        window=items[i:i+w]
        test=[v["test_acc"] for v in window]
        if all(.55<=v<=.65 for v in test) and max(test)-min(test)<=.04 and all(v["train_acc"]>=.99 for v in window):
            eligible.append({"from":int(window[0]["step"]),"to":int(window[-1]["step"]),"range":round(max(test)-min(test),4)})
    first_fit=next((int(v["step"]) for v in items if v["train_acc"]>=.99),None)
    first_test60=next((int(v["step"]) for v in items if v["test_acc"]>=.55),None)
    tail=items[-10:] if len(items)>=10 else []
    tailtest=[v["test_acc"] for v in tail]
    durable=bool(tail) and all(.55<=v<=.65 and v2["train_acc"]>=.99 for v,v2 in zip(tailtest,tail)) and max(tailtest)-min(tailtest)<=.04 and abs(sum(tailtest[:5])/5-sum(tailtest[5:])/5)<=.02
    d={"name":p.parent.name,"first_fit":first_fit,"first_55":first_test60,"final_train":round(items[-1]["train_acc"],4),"final_test":round(items[-1]["test_acc"],4),"max_test":round(max(x["test_acc"] for x in items),4),"plateau_eligible":eligible,"durable_plateau":durable}
    TRAIN.append(d)
LESIONS=[]
for p in sorted((ROOT/"lesions").glob("*/results.json")):
    a=json.loads(p.read_text(encoding="utf-8"))
    d={"checkpoint":Path(a["checkpoint"]).parent.name+"/"+Path(a["checkpoint"]).stem,"step":a["checkpoint_step"],"mask_seed":a["mask_seed"],"base_test":a["base"]["test_acc"]}
    for arm in ("ablate","reset"):
        r=a["arms"][arm]
        d[arm+"_damage_pp"]=r["initial_damage_test_pp"]
        d[arm+"_recov"]=r["recovery_step"]
        d[arm+"_final"]=r["final"]["test_acc"]
    LESIONS.append(d)
summ={}
for cp in sorted(set(x["checkpoint"] for x in LESIONS)):
    l=[x for x in LESIONS if x["checkpoint"]==cp]
    if not l:continue
    summ[cp]={"masks":len(l),"baseline_test":l[0]["base_test"],"damage_ablate_mean_pp":statistics.mean(x["ablate_damage_pp"] for x in l),"damage_ablate_range_pp":[min(x["ablate_damage_pp"] for x in l),max(x["ablate_damage_pp"] for x in l)],"recovery_ablate_within150":sum(x["ablate_recov"] is not None for x in l),"recovery_steps_observed":[x["ablate_recov"] for x in l],"ablate_final_mean":statistics.mean(x["ablate_final"] for x in l),"reset_recovered":sum(x["reset_recov"] is not None for x in l)}
result={"scope":"Exploratory calibration; no causal conclusion about semigrokking","training":TRAIN,"lesions":LESIONS,"summary_by_checkpoint":summ,"eligible_plateau_count":sum(bool(x["plateau_eligible"]) for x in TRAIN),"durable_plateau_count":sum(x["durable_plateau"] for x in TRAIN)}
(ROOT/"analysis.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
lines=["# Exploratory results - 2026-11-09","","**Status:** initial feasibility; the requested matched semigrokking-vs-gradual causal contrast is NOT yet established.","","## Trained networks","","| Model | First fit>=99% | First test>=55% | Final test | Eligible 55-65% plateau |","|---|---:|---:|---:|---|"]
for t in TRAIN:
    lines.append(f"| {t['name']} | {t['first_fit']} | {t['first_55']} | {100*t['final_test']:.2f}% | {'LOCAL' if t['plateau_eligible'] else 'NO'} / {'DURABLE' if t['durable_plateau'] else 'NOT DURABLE'} |")
lines.extend(["","## Random lesions (30 of 300 units)",""])
for cp,s in summ.items():
    steps=",".join("censored" if x is None else str(x) for x in s["recovery_steps_observed"])
    lines.extend([f"**{cp}**: baseline {100*s['baseline_test']:.2f}% test; {s['masks']} random masks, ablation mean immediate loss {s['damage_ablate_mean_pp']:.2f}pp (range {s['damage_ablate_range_pp'][0]:.2f}-{s['damage_ablate_range_pp'][1]:.2f}); recovered by 150 updates in {s['recovery_ablate_within150']}/{s['masks']}; steps [{steps}]; reset recovered in {s['reset_recovered']}/{s['masks']}.",""])
lines.extend(["## Scientific limitations","","The 5 masks are perturbations of the same learned network (NOT independent network replications). Both ablated checkpoints are on a rising generalization curve rather than a stable semi-grokking or smooth plateau. Weight decay and optimization duration differ. Baseline continuation improves without a lesion; recovery to 95% of *starting* baseline does not equal catch-up with continuing control.","","The effect of the learning trajectory cannot be estimated from these comparisons. Further training and blinded reserved seeds are needed after finding the correct matched regimes."])
(ROOT/"REPORT.md").write_text("\n".join(lines),encoding="utf-8")
print(json.dumps({"trained":len(TRAIN),"lesions":len(LESIONS),"eligible_local":result["eligible_plateau_count"],"eligible_durable":result["durable_plateau_count"],"summary":summ},ensure_ascii=False,indent=2))
