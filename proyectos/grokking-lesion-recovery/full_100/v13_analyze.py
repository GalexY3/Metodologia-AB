"""V13 integrity and dose-by-arm recovery analysis.

Unit of replication: five trained network pairs. Four masks per dose are nested
within each trained network; within each mask seed the lesion doses are nested.
Outcome selection uses no test partition. No a posteriori dose selection.
"""
from pathlib import Path
import json,statistics,math,itertools
ROOT=Path(__file__).resolve().parent
FOLDER=ROOT/"v13_dose_runs"
seeds=[11,12,13,14,18]
arms=[1e-5,.001]
doses=[30,60,90,120,150,180,210,240,270]
masks=[4101,4102,4103,4104]
problems=[]
records=[]
for seed in seeds:
 for lam in arms:
  d=FOLDER/f"seed{seed}_prior{lam:g}"
  if not (d/"control.csv").is_file():problems.append(f"no control {seed}/{lam}")
  for dose in doses:
   for ms in masks:
    path=d/f"dose{dose:03d}_mask{ms}.json"
    csv=d/f"dose{dose:03d}_mask{ms}.csv"
    if not path.is_file() or not csv.is_file():
     problems.append(f"missing {seed}/{lam}/{dose}/{ms}")
     continue
    v=json.loads(path.read_text(encoding="utf-8"))
    if (v["seed"]!=seed or v["prior_l1"]!=lam or v["dose"]!=dose
        or v["mask_seed"]!=ms or v["training_checkpoint_step"]!=10000):
     problems.append(f"wrong metadata {seed}/{lam}/{dose}/{ms}")
    if v["common_l1"]!=.0001 or v["repair_l1"]!=.0001:
     problems.append(f"wrong l1 {seed}/{lam}/{dose}/{ms}")
    if len(v["masked_indices"])!=dose or len(set(v["masked_indices"]))!=dose:
     problems.append(f"mask cardinality {seed}/{lam}/{dose}/{ms}")
    if not all(math.isfinite(v[k]) for k in ("initial_val_damage_pp","auc_val_control_minus_injured","injured_val_final")):
     problems.append(f"nonfinite {seed}/{lam}/{dose}/{ms}")
    records.append(v)
by={(v["seed"],v["prior_l1"],v["dose"],v["mask_seed"]):v for v in records}
for seed in seeds:
 for ms in masks:
  for dose in doses:
   a=by.get((seed,1e-5,dose,ms))
   b=by.get((seed,.001,dose,ms))
   if a is None or b is None:continue
   if a["masked_indices"]!=b["masked_indices"]:
    problems.append(f"unpaired indices {seed}/{dose}/{ms}")
   if dose>30:
    a0=by.get((seed,1e-5,dose-30,ms))
    if a0 is not None and not set(a0["masked_indices"]).issubset(a["masked_indices"]):
     problems.append(f"nonnested dose {seed}/{dose}/{ms}")
network=[]
for dose in doses:
 for seed in seeds:
  for lam in arms:
   group=[v for v in records if v["dose"]==dose and v["seed"]==seed and v["prior_l1"]==lam]
   if len(group)!=len(masks):
    problems.append(f"wrong repetitions {dose}/{seed}/{lam}")
    continue
   injured=[z for z in group if z["initial_val_damage_pp"]>2]
   observed=[z for z in injured if z["recovery99_two_consecutive_step"] is not None]
   def avg(name,rows=group):
    return statistics.mean(v[name] for v in rows)
   network.append({"dose":dose,"percent":dose/3,"seed":seed,
    "lambda":lam,"group":"grokking_tardio" if lam==1e-5 else "aprendizaje_rapido",
    "mean_initial_damage_pp":avg("initial_val_damage_pp"),
    "median_initial_damage_pp":statistics.median(z["initial_val_damage_pp"] for z in group),
    "mean_auc":avg("auc_val_control_minus_injured"),
    "n_masks":len(group),"n_damaged_gt2pp":len(injured),
    "n_recovered_gt2pp":len(observed),
    "recovery_proportion_among_damaged":len(observed)/len(injured) if injured else None,
    "restricted_mean_recovery_step_given_damage":statistics.mean(
       z["recovery99_two_consecutive_step"] if z["recovery99_two_consecutive_step"] is not None else 500 for z in injured) if injured else None,
    "median_step_of_observed_recoveries":statistics.median(
       z["recovery99_two_consecutive_step"] for z in observed) if observed else None,
    "mean_auc_normalized_given_damage":statistics.mean(z["normalized_auc_if_damage_gt2pp"] for z in injured) if injured else None,
    "n_immediately_robust_lt2pp":len(group)-len(injured)})
paired=[]
for dose in doses:
 for seed in seeds:
  a=next((r for r in network if r["dose"]==dose and r["seed"]==seed and r["lambda"]==1e-5),None)
  b=next((r for r in network if r["dose"]==dose and r["seed"]==seed and r["lambda"]==.001),None)
  if a is None or b is None:continue
  both=[(by[(seed,1e-5,dose,ms)],by[(seed,.001,dose,ms)]) for ms in masks
        if by[(seed,1e-5,dose,ms)]["initial_val_damage_pp"]>2 and
           by[(seed,.001,dose,ms)]["initial_val_damage_pp"]>2]
  paired.append({"seed":seed,"dose":dose,"percent":dose/3.,
    "mean_damage_diff_A_minus_B_pp":a["mean_initial_damage_pp"]-b["mean_initial_damage_pp"],
    "mean_auc_diff_A_minus_B":a["mean_auc"]-b["mean_auc"],
    "matched_damage_n":len(both),
    "normalized_auc_diff_if_both_damaged":statistics.mean(
        va["normalized_auc_if_damage_gt2pp"]-vb["normalized_auc_if_damage_gt2pp"] for va,vb in both) if both else None})
def exact_signflip(ds):
 if len(ds)!=5:return None
 obs=abs(statistics.mean(ds))
 null=[abs(statistics.mean(s*v for s,v in zip(signs,ds))) for signs in itertools.product((-1,1),repeat=len(ds))]
 return sum(v>=obs-1e-12 for v in null)/len(null)
def pair_bootstrap_ci(ds):
 # exact empirical paired-seed bootstrap over all 5**5 resamples
 if len(ds)!=5:return None
 vals=sorted(statistics.mean(ds[i] for i in idx) for idx in itertools.product(range(5),repeat=5))
 return [vals[int(.025*(len(vals)-1))],vals[int(.975*(len(vals)-1))]]
dose_summary=[]
for dose in doses:
 A=[r for r in network if r["dose"]==dose and r["lambda"]==1e-5]
 B=[r for r in network if r["dose"]==dose and r["lambda"]==.001]
 pairs=[r for r in paired if r["dose"]==dose]
 x=[r["mean_auc_diff_A_minus_B"] for r in pairs]
 dmg=[r["mean_damage_diff_A_minus_B_pp"] for r in pairs]
 both=[r for r in pairs if r["normalized_auc_diff_if_both_damaged"] is not None]
 dose_summary.append({
  "dose":dose,"percent":dose/3.,
  "initial_damage_A_pp":statistics.mean(r["mean_initial_damage_pp"] for r in A),
  "initial_damage_B_pp":statistics.mean(r["mean_initial_damage_pp"] for r in B),
  "mean_auc_A":statistics.mean(r["mean_auc"] for r in A),
  "mean_auc_B":statistics.mean(r["mean_auc"] for r in B),
  "mean_auc_diff_A_minus_B":statistics.mean(x),
  "seedwise_auc_diff_A_minus_B":x,
  "mean_damage_diff_A_minus_B_pp":statistics.mean(dmg),
  "seedwise_damage_diff_A_minus_B_pp":dmg,
  "signflip_p_two_sided_exploratory":exact_signflip(x),
  "seed_bootstrap95_auc_diff_descriptive":pair_bootstrap_ci(x),
  "n_seeds_favor_A":sum(y<0 for y in x),
  "n_seeds_favor_B":sum(y>0 for y in x),
  "A_masks_damaged_gt2pp":sum(r["n_damaged_gt2pp"] for r in A),
  "B_masks_damaged_gt2pp":sum(r["n_damaged_gt2pp"] for r in B),
  "A_masks_recovered_given_damage":sum(r["n_recovered_gt2pp"] for r in A),
  "B_masks_recovered_given_damage":sum(r["n_recovered_gt2pp"] for r in B),
  "A_restricted_mean_time_given_damage":statistics.mean(
      r["restricted_mean_recovery_step_given_damage"] for r in A if r["restricted_mean_recovery_step_given_damage"] is not None),
  "B_restricted_mean_time_given_damage":statistics.mean(
      r["restricted_mean_recovery_step_given_damage"] for r in B if r["restricted_mean_recovery_step_given_damage"] is not None),
  "conditional_both_damaged_seed_count":len(both),
  "mean_normalized_A_minus_B_if_both_damaged":statistics.mean(
      r["normalized_auc_diff_if_both_damaged"] for r in both) if both else None,
 })
status={"status":"PASS" if not problems and len(records)==360 else "FAIL",
        "issues":problems,"network_pair_seeds":seeds,
        "n_doses":len(doses),"n_masks_per_dose_per_model":len(masks),
        "n_lesioned_runs":len(records),"test_not_used":True}
payload={"protocol":"PREREG_V13_DOSE.md",
 "audit":status,"per_network":network,"paired_seed":paired,"dose_summary":dose_summary,
 "interpretation":"Exploratory; historical acquisition L1 confounds grokking, mask replicates nested, different initial functional damage even with same indices; multiple dose comparisons."}
(ROOT/"V13_ANALYSIS.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
for x in dose_summary:
 print("DOSE",x["dose"],f"{x['percent']:.0f}%",
   "damage(A/B)",round(x["initial_damage_A_pp"],1),round(x["initial_damage_B_pp"],1),
   "AUC(A/B)",round(x["mean_auc_A"],1),round(x["mean_auc_B"],1),
   "recovered(A/B)",f"{x['A_masks_recovered_given_damage']}/{x['A_masks_damaged_gt2pp']}",
                          f"{x['B_masks_recovered_given_damage']}/{x['B_masks_damaged_gt2pp']}",
   "seed_favor(A/B)",x["n_seeds_favor_A"],x["n_seeds_favor_B"],
   "signflip_p",x["signflip_p_two_sided_exploratory"],flush=True)
print("V13_AUDIT",status["status"],"runs",len(records),"problems",len(problems),flush=True)
