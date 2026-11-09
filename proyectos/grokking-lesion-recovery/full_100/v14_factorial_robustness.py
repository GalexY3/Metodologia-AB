"""V14 paired robustness across final L1 schedules, fixed final training length.
No test partition; post-L1 interventions branch from exactly same checkpoint.
"""
from pathlib import Path
import json,statistics,itertools
import numpy as np
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(4)
DIR=ROOT/"v14_factorial"
SEEDS=[11,12,13,14,18]
ORIG=(1e-5,.001)
FINALS=(1e-5,.0001,.001)
x,y,ix=data(20261110,500,1000,2000)
xv=x[ix["val"]];yv=y[ix["val"]]
masks=[]
for ms in range(4301,4401):
 pick=np.random.default_rng(ms).choice(300,90,replace=False)
 mask=np.ones(300,dtype=np.float32)
 mask[pick]=0.
 masks.append(mask)
masked=torch.from_numpy(np.stack(masks)).T.contiguous()
results=[]
@torch.no_grad()
def evaluate(seed,origin,final_lambda):
 folder=DIR/f"seed{seed}_prior{origin:g}"/f"finalL1_{final_lambda:g}"
 conf=json.loads((folder/"result.json").read_text(encoding="utf-8"))
 model=MLP(300)
 model.load_state_dict(torch.load(folder/"ck_010000.pt",map_location="cpu",weights_only=False)["model"])
 model.eval()
 h=torch.relu(model.a(xv))
 w=model.b.weight[1]-model.b.weight[0]
 bias=model.b.bias[1]-model.b.bias[0]
 z=h@w+bias
 truth=yv.bool()
 base=float(((z>0)==truth).float().mean())
 z_m=h@(masked*w[:,None])+bias
 acc=((z_m>0)==truth[:,None]).float().mean(0)
 damage=(base-acc)*100.
 val_ce=float(F.binary_cross_entropy_with_logits(z,yv.float()))
 injured_ce=float(F.binary_cross_entropy_with_logits(z_m,yv.float()[:,None].expand(-1,100)))
 contributions=h.abs().mean(0)*torch.linalg.vector_norm(model.b.weight,dim=0)
 importance=contributions/(contributions.sum()+1e-12)
 effective=float(1.0/importance.square().sum())
 top=torch.sort(importance,descending=True).values
 return {"seed":seed,"origin":origin,"final_l1":final_lambda,
  "full_last3":conf["final_last3_full"],
  "validation_accuracy":base,"val_ce":val_ce,
  "mean_damage_pp":float(damage.mean()),
  "mean_damage_ce":injured_ce-val_ce,
  "median_damage_pp":float(damage.median()),
  "mask_damage":[float(v) for v in damage.tolist()],
  "n_masks":100,"effective_contributors":effective,
  "top5_importance_mass":float(top[:5].sum()),
  "top10_importance_mass":float(top[:10].sum())}
for seed in SEEDS:
 for orig in ORIG:
  for post in FINALS:
   r=evaluate(seed,orig,post)
   results.append(r)
   print("V14_ROB",seed,f"initial{orig:g}",f"final{post:g}",
         "eligible",r["full_last3"],
         "damage",round(r["mean_damage_pp"],3),
         "effective",round(r["effective_contributors"],2),flush=True)
key={(r["seed"],r["origin"],r["final_l1"]):r for r in results}
within=[]
for seed in SEEDS:
 for orig in ORIG:
  arms=[key[(seed,orig,post)] for post in FINALS]
  if all(r["full_last3"] for r in arms):
   within.append({"seed":seed,"origin":orig,
     "damage_low":arms[0]["mean_damage_pp"],
     "damage_medium":arms[1]["mean_damage_pp"],
     "damage_high":arms[2]["mean_damage_pp"],
     "low_minus_medium":arms[0]["mean_damage_pp"]-arms[1]["mean_damage_pp"],
     "high_minus_medium":arms[2]["mean_damage_pp"]-arms[1]["mean_damage_pp"],
     "low_minus_high":arms[0]["mean_damage_pp"]-arms[2]["mean_damage_pp"]})
between=[]
for seed in SEEDS:
 for post in FINALS:
  a=key[(seed,1e-5,post)];b=key[(seed,.001,post)]
  between.append({"seed":seed,"final_l1":post,"matched_100":a["full_last3"] and b["full_last3"],
    "A_damage":a["mean_damage_pp"],"B_damage":b["mean_damage_pp"],
    "A_minus_B_damage_pp":a["mean_damage_pp"]-b["mean_damage_pp"]})
def pair_stats(xs):
 if not xs:return None
 return {"n":len(xs),"mean":statistics.mean(xs),
         "seed_values":xs,"favor_negative":sum(z<0 for z in xs),"favor_positive":sum(z>0 for z in xs)}
def signflip_p(xs):
 if not xs or len(xs)>10:return None
 obs=abs(statistics.mean(xs))
 nul=[abs(statistics.mean(s*v for s,v in zip(sig,xs))) for sig in itertools.product((-1,1),repeat=len(xs))]
 return sum(abs(z)>=obs-1e-12 for z in nul)/len(nul)
summary={"final_l1_comparisons":{},"within_original_model":{}}
for post in FINALS:
 arr=[z["A_minus_B_damage_pp"] for z in between if z["final_l1"]==post and z["matched_100"]]
 summary["final_l1_comparisons"][str(post)]={
  "matched_pair_eligible":len(arr),
  "paired_diff":pair_stats(arr),
  "signflip_p_exploratory":signflip_p(arr)}
for orig in ORIG:
 arr=[z for z in within if z["origin"]==orig]
 for dim in ("low_minus_medium","high_minus_medium","low_minus_high"):
  vals=[r[dim] for r in arr]
  summary["within_original_model"][f"initial={orig}, {dim}"]={"paired":pair_stats(vals),"signflip_p":signflip_p(vals)}
out={"protocol":"PREREG_V14_FACTORIAL.md",
  "status":"experimental factorial followup, noncausal attribution to grokking",
  "mask_seeds":[4301,4400],"n_masks_each":100,
  "observations":results,"within_same_historical_checkpoint":within,
  "between_histories_at_same_final_l1":between,"summary":summary,
  "test_not_consulted":True,
  "caution":"Past grokking history is confounded by initial L1; interventions on final L1 are causal within same checkpoint; mask repeats clustered within 5 independent initial seed pairs."}
(ROOT/"V14_ANALYSIS.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("V14_SUMMARY",json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
