"""V15 audit and paired analysis: fresh vs resumed AdamW after same lesion.

Exactly same weights and masks in both optimization arms. Four masks are nested
in five independent trained seed-pairs. Test data never consulted.
"""
from pathlib import Path
import json,statistics,math,itertools
ROOT=Path(__file__).resolve().parent
FOLDER=ROOT/"v15_repair"
SEEDS=[11,12,13,14,18]
LAMS=(1e-5,.001)
MODES=("fresh","resumed")
DOSES=(90,180,270)
MASKS=(4501,4502,4503,4504)
bad=[];recs=[]
for seed in SEEDS:
 for lam in LAMS:
  for mode in MODES:
   folder=FOLDER/f"seed{seed}_prior{lam:g}"/mode
   if not (folder/"control.csv").is_file():bad.append("missing control "+str(folder))
   for dose in DOSES:
    for ms in MASKS:
     path=folder/f"dose{dose:03d}_mask{ms}.json"
     curve=folder/f"dose{dose:03d}_mask{ms}.csv"
     if not path.is_file() or not curve.is_file():bad.append("missing files "+str(path));continue
     o=json.loads(path.read_text(encoding="utf-8"))
     recs.append(o)
     if (o["seed"]!=seed or o["initial_l1"]!=lam or o["mode"]!=mode
        or o["dose"]!=dose or o["mask_seed"]!=ms):
      bad.append("metadata "+str(path))
     if len(set(o["masked_indices"]))!=dose:bad.append("mask count "+str(path))
     if o["final_l1"]!=.0001 or o["step_checkpoint"]!=10000:
      bad.append("wrong final hyperparams "+str(path))
     if any(not math.isfinite(o[k]) for k in ("init_damage_val_pp","auc_val_control_deficit","injured_val_final")):
      bad.append("nonfinite "+str(path))
index={(r["seed"],r["initial_l1"],r["mode"],r["dose"],r["mask_seed"]):r for r in recs}
for seed in SEEDS:
 for dose in DOSES:
  for ms in MASKS:
   versions=[index.get((seed,lam,mode,dose,ms)) for lam in LAMS for mode in MODES]
   if any(r is None for r in versions):bad.append("missing fourway "+str((seed,dose,ms)));continue
   names=[tuple(r["masked_indices"]) for r in versions]
   if not all(n==names[0] for n in names):bad.append("mask mismatch "+str((seed,dose,ms)))
   for lam in LAMS:
    a=index[(seed,lam,"fresh",dose,ms)]
    b=index[(seed,lam,"resumed",dose,ms)]
    if abs(a["init_damage_val_pp"]-b["init_damage_val_pp"])>1e-7:
     bad.append("initial damage differs for identical model/mask "+str((seed,lam,dose,ms)))
permodel=[]
for dose in DOSES:
 for seed in SEEDS:
  for lam in LAMS:
   mask_pairs=[(index[(seed,lam,"fresh",dose,ms)],index[(seed,lam,"resumed",dose,ms)]) for ms in MASKS]
   effective=[(a,b) for a,b in mask_pairs if a["init_damage_val_pp"]>2]
   permodel.append({"dose":dose,"seed":seed,"history_l1":lam,
    "mean_initial_damage_pp":statistics.mean(a["init_damage_val_pp"] for a,b in mask_pairs),
    "mean_AUC_fresh":statistics.mean(a["auc_val_control_deficit"] for a,b in mask_pairs),
    "mean_AUC_resumed":statistics.mean(b["auc_val_control_deficit"] for a,b in mask_pairs),
    "mean_AUC_fresh_minus_resumed":statistics.mean(a["auc_val_control_deficit"]-b["auc_val_control_deficit"] for a,b in mask_pairs),
    "n_damaged_gt2":len(effective),
    "n_recovered_fresh":sum(a["recovery_step"] is not None for a,b in effective),
    "n_recovered_resumed":sum(b["recovery_step"] is not None for a,b in effective),
    "restricted_mean_time_fresh":statistics.mean(a["recovery_step"] if a["recovery_step"] is not None else 500 for a,b in effective) if effective else None,
    "restricted_mean_time_resumed":statistics.mean(b["recovery_step"] if b["recovery_step"] is not None else 500 for a,b in effective) if effective else None,
    "mean_normalized_AUC_fresh_minus_resumed":statistics.mean(a["norm_auc_damage_gt2pp"]-b["norm_auc_damage_gt2pp"] for a,b in effective) if effective else None,
    "control_val_final_fresh":mask_pairs[0][0]["control_val_final"],
    "control_val_final_resumed":mask_pairs[0][1]["control_val_final"]})
def sf(vals):
 if not vals:return None
 obs=abs(statistics.mean(vals))
 null=[abs(statistics.mean(s*v for s,v in zip(sgn,vals))) for sgn in itertools.product((-1,1),repeat=len(vals))]
 return sum(t>=obs-1e-12 for t in null)/len(null)
summary=[]
for dose in DOSES:
 A=[p for p in permodel if p["dose"]==dose and p["history_l1"]==1e-5]
 B=[p for p in permodel if p["dose"]==dose and p["history_l1"]==.001]
 af=[z["mean_AUC_fresh"] for z in A]
 ar=[z["mean_AUC_resumed"] for z in A]
 bf=[z["mean_AUC_fresh"] for z in B]
 br=[z["mean_AUC_resumed"] for z in B]
 dA=[a["mean_AUC_fresh_minus_resumed"] for a in A]
 dB=[b["mean_AUC_fresh_minus_resumed"] for b in B]
 summary.append({
  "dose":dose,"percent":dose/3,
  "initial_damage_A_pp":statistics.mean(z["mean_initial_damage_pp"] for z in A),
  "initial_damage_B_pp":statistics.mean(z["mean_initial_damage_pp"] for z in B),
  "mean_auc_A_fresh":statistics.mean(af),"mean_auc_A_resumed":statistics.mean(ar),
  "mean_auc_B_fresh":statistics.mean(bf),"mean_auc_B_resumed":statistics.mean(br),
  "optimizer_effect_A_fresh_minus_resumed":statistics.mean(dA),
  "optimizer_effect_B_fresh_minus_resumed":statistics.mean(dB),
  "optimizer_effect_seed_A":dA,"optimizer_effect_seed_B":dB,
  "optimizer_effect_A_signflip_p":sf(dA),
  "optimizer_effect_B_signflip_p":sf(dB),
  "seed_A_optim_resumed_better":sum(z>0 for z in dA),
  "seed_B_optim_resumed_better":sum(z>0 for z in dB),
  "A_minus_B_gap_fresh":statistics.mean(af)-statistics.mean(bf),
  "A_minus_B_gap_resumed":statistics.mean(ar)-statistics.mean(br),
  "pairwise_gap_fresh":[x-y for x,y in zip(af,bf)],
  "pairwise_gap_resumed":[x-y for x,y in zip(ar,br)],
  "damaged_A":sum(z["n_damaged_gt2"] for z in A),
  "damaged_B":sum(z["n_damaged_gt2"] for z in B),
  "A_recovered_fresh":sum(z["n_recovered_fresh"] for z in A),
  "A_recovered_resumed":sum(z["n_recovered_resumed"] for z in A),
  "B_recovered_fresh":sum(z["n_recovered_fresh"] for z in B),
  "B_recovered_resumed":sum(z["n_recovered_resumed"] for z in B),
  "A_control_val_all100":all(z["control_val_final_fresh"]==z["control_val_final_resumed"]==1. for z in A),
  "B_control_val_all100":all(z["control_val_final_fresh"]==z["control_val_final_resumed"]==1. for z in B)})
status={"status":"PASS" if not bad and len(recs)==240 else "FAIL","issues":bad,
        "n_runs":len(recs),"n_independent_seed_pairs":5,"n_masks_per_dose_per_model":4,
        "same_model_weights_fresh_resumed":True,
        "same_initial_damage_verified":not any("initial damage differs" in z for z in bad)}
out={"audit":status,"protocol":"PREREG_V15_OPTIMIZER_REPAIR.md",
     "per_model":permodel,"by_dose":summary,
     "scope":"exploratory; optimizer state causally varied within identical weights and lesion, grokking history remains confounded by initial L1; test not used"}
(ROOT/"V15_ANALYSIS.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("V15_AUDIT",json.dumps(status,ensure_ascii=False),flush=True)
for q in summary:
 print("V15_DOSE",int(q["percent"]),"AUC_A_fresh/resumed",round(q["mean_auc_A_fresh"],1),round(q["mean_auc_A_resumed"],1),
   "AUC_B_fresh/resumed",round(q["mean_auc_B_fresh"],1),round(q["mean_auc_B_resumed"],1),
   "recoveryA(fresh/resumed)",f"{q['A_recovered_fresh']}/{q['damaged_A']}",f"{q['A_recovered_resumed']}/{q['damaged_A']}",
   "recoveryB(fresh/resumed)",f"{q['B_recovered_fresh']}/{q['damaged_B']}",f"{q['B_recovered_resumed']}/{q['damaged_B']}",
   "optEffect(A,B)",round(q["optimizer_effect_A_fresh_minus_resumed"],2),round(q["optimizer_effect_B_fresh_minus_resumed"],2),
   "optEffectFavorsResumed(A,B)",q["seed_A_optim_resumed_better"],q["seed_B_optim_resumed_better"],flush=True)
