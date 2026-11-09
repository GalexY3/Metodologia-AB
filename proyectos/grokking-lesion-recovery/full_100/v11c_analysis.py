"""V11C local integrity and clustered analysis, n=5 paired training runs.
"""
from pathlib import Path
import json,statistics,math,itertools
ROOT=Path(__file__).resolve().parent
allrows=json.loads((ROOT/"V11C_RAW.json").read_text(encoding="utf-8"))["results"]
by={(r["seed"],r["initial_lambda"],r["maskseed"]):r for r in allrows}
errors=[];seeds=[]
for seed in range(5):
 pairs=[]
 for maskseed in range(2111,2121):
  a=by.get((seed,1e-5,maskseed));b=by.get((seed,.001,maskseed))
  if a is None or b is None:errors.append(f"missing {seed}/{maskseed}");continue
  if a["indices"]!=b["indices"] or len(set(a["indices"]))!=90:errors.append(f"mask mismatch {seed}/{maskseed}")
  if any(r["common_lambda"]!=.0001 or r["repair_lambda"]!=.0001 or r["dose"]!=90 for r in (a,b)):errors.append("bad treatment")
  pairs.append((a,b))
 def mean(field,index):return statistics.mean(r[index][field] for r in pairs)
 damage_a=mean("initial_damage_val_pp",0);damage_b=mean("initial_damage_val_pp",1)
 auc_a=mean("auc_val",0);auc_b=mean("auc_val",1)
 damaged_pairs=[(a,b) for a,b in pairs if a["initial_damage_val_pp"]>2 and b["initial_damage_val_pp"]>2]
 v={"seed":seed,"masks":len(pairs),
     "damage_A_pp":damage_a,"damage_B_pp":damage_b,
     "auc_A":auc_a,"auc_B":auc_b,"auc_A_minus_B":auc_a-auc_b,
     "paired_both_damaged_n":len(damaged_pairs),
     "normalized_AUC_gap_if_both_damaged":statistics.mean(a["normalized_auc_if_damage"]-b["normalized_auc_if_damage"] for a,b in damaged_pairs) if damaged_pairs else None,
     "recovered_A":sum(a["recovery_val99_two_consecutive_step"] is not None for a,b in pairs if a["initial_damage_val_pp"]>2),
     "recovered_B":sum(b["recovery_val99_two_consecutive_step"] is not None for a,b in pairs if b["initial_damage_val_pp"]>2),
     "damaged_A":sum(a["initial_damage_val_pp"]>2 for a,b in pairs),
     "damaged_B":sum(b["initial_damage_val_pp"]>2 for a,b in pairs),
     "control_final_acc_A":pairs[0][0]["control_final"]["val_acc"],
     "control_final_acc_B":pairs[0][1]["control_final"]["val_acc"]}
 seeds.append(v)
 diffs=[z["auc_A_minus_B"] for z in seeds]
 mean_diff=statistics.mean(diffs)
 # Sign-flip exact randomization-style sensitivity for pair-level zero-effect symmetry.
 signflip=[statistics.mean(s*val for s,val in zip(signs,diffs)) for signs in itertools.product((-1,1),repeat=5)]
 p_twosided=sum(abs(t)>=abs(mean_diff)-1e-12 for t in signflip)/len(signflip)
 m={
 "n_independent_network_pairs":5,"n_physical_mask_pairs":50,
 "mean_damage_A_pp":statistics.mean(z["damage_A_pp"] for z in seeds),
 "mean_damage_B_pp":statistics.mean(z["damage_B_pp"] for z in seeds),
 "mean_auc_A":statistics.mean(z["auc_A"] for z in seeds),
 "mean_auc_B":statistics.mean(z["auc_B"] for z in seeds),
 "mean_pair_auc_gap_A_minus_B":mean_diff,
 "mean_normalized_auc_gap_conditional":statistics.mean(z["normalized_AUC_gap_if_both_damaged"] for z in seeds if z["normalized_AUC_gap_if_both_damaged"] is not None),
 "seed_A_lower_auc":sum(x<0 for x in diffs),"seed_B_lower_auc":sum(x>0 for x in diffs),
 "recovered_A":sum(z["recovered_A"] for z in seeds),
 "recovered_B":sum(z["recovered_B"] for z in seeds),
 "damaged_A":sum(z["damaged_A"] for z in seeds),
 "damaged_B":sum(z["damaged_B"] for z in seeds),
 "exact_signflip_p_two_sided_exploratory":p_twosided,
}
out={"audit":{"status":"PASS" if len(allrows)==100 and not errors else "FAIL",
 "errors":errors,"n_lesions":len(allrows),"not_independent":True},
 "per_seed":seeds,"aggregate":m,
 "interpretation":"not an estimate of grokking causal effect; L1 acquisition regimes differ, masks nested, validation used for design"}
(ROOT/"V11C_ANALYSIS.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(out,indent=2,ensure_ascii=False))
