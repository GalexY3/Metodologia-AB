"""V11: compare robustness after shared-L1 continuation at equal competence.
The same masks (seeds 2001..2100) are used within every paired seed.
Mask replicates are clustered within five network seed pairs.
"""
from pathlib import Path
import json,csv,statistics,math
import numpy as np
import torch
from parity_v10 import MLP,data,measure
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(4)
x,y,ids=data(20261109,500,1000,2000)
xv=x[ids["val"]];yv=y[ids["val"]].bool()
masks=[]
for ms in range(2001,2101):
 picks=np.random.default_rng(ms).choice(300,90,replace=False)
 mask=np.ones(300,dtype="float32")
 mask[picks]=0.
 masks.append(mask)
maskmat=torch.tensor(np.stack(masks),dtype=torch.float).T
records=[]
def load(seed,lam,common,step):
 name=f"lambda{lam:g}_seed{seed}_lr0.001_width300_nt500"
 path=ROOT/"v11_common_runs"/f"{name}_commonL1_{common:g}_4000"/f"ck_{step:06d}.pt"
 ck=torch.load(path,map_location="cpu",weights_only=False)
 model=MLP(300)
 model.load_state_dict(ck["model"])
 return model
@torch.no_grad()
def stats(net):
 h=torch.relu(net.a(xv))
 w=net.b.weight[1]-net.b.weight[0]
 bias=net.b.bias[1]-net.b.bias[0]
 baseline=(h@w+bias)>0
 baseacc=float((baseline==yv).float().mean())
 maskscores=h@(maskmat*w[:,None])+bias
 per_mask=(maskscores>0)==yv[:,None]
 scores=per_mask.float().mean(0).numpy()
 initial=(baseacc-scores)*100
 contributions=h.abs().mean(0)*torch.linalg.vector_norm(net.b.weight.detach(),dim=0)
 probs=contributions/(contributions.sum()+1e-12)
 entropy_eff=float(1/(probs.square().sum()+1e-12))
 tops=torch.sort(probs,descending=True).values
 # compute BCE log loss based on two-logit difference (equivalent to CE).
 bce=torch.nn.functional.binary_cross_entropy_with_logits(maskscores,yv.float()[:,None].expand(-1,100),reduction="none").mean(0)
 clean_bce=float(torch.nn.functional.binary_cross_entropy_with_logits(h@w+bias,yv.float()))
 return {
  "accuracy":baseacc,"mean_mask_damage_pp":float(np.mean(initial)),
  "median_mask_damage_pp":float(np.median(initial)),
  "p90_damage_pp":float(np.quantile(initial,.9)),
  "mean_mask_bce_increase":float(bce.mean()-clean_bce),
  "individual_damage_pp":[round(float(v),6) for v in initial],
  "mean_mask_after_acc":float(scores.mean()),
  "effective_contributors":entropy_eff,
  "top5_share":float(tops[:5].sum()),
  "top10_share":float(tops[:10].sum()),
  "initial_validation_ce":clean_bce
 }
for common in (0.,.0001):
 for step in (5000,7000,9000):
  for seed in range(5):
   for lam in (1e-5,.001):
    try:
     model=load(seed,lam,common,step)
     r={"common":common,"step":step,"seed":seed,"prior_lambda":lam,**stats(model)}
     records.append(r)
     print("ROBUST",seed,lam,common,step,"acc",round(r["accuracy"],3),
       "mean_damage",round(r["mean_mask_damage_pp"],3),"neffective",round(r["effective_contributors"],2),flush=True)
    except FileNotFoundError as e:
     raise
comparison=[]
for common in (0.,.0001):
 for step in (5000,7000,9000):
  for seed in range(5):
   a=next(z for z in records if z["common"]==common and z["step"]==step and z["seed"]==seed and z["prior_lambda"]==1e-5)
   b=next(z for z in records if z["common"]==common and z["step"]==step and z["seed"]==seed and z["prior_lambda"]==.001)
   valid=abs(a["accuracy"]-1.)<1e-9 and abs(b["accuracy"]-1.)<1e-9
   comparison.append({"common":common,"step":step,"seed":seed,"both_100":valid,
     "A_minus_B_damage_pp":a["mean_mask_damage_pp"]-b["mean_mask_damage_pp"],
     "A_minus_B_neffective":a["effective_contributors"]-b["effective_contributors"]})
summary={}
for common in (0.,.0001):
 for step in (5000,7000,9000):
  sel=[v for v in comparison if v["common"]==common and v["step"]==step]
  elig=[v for v in sel if v["both_100"]]
  summary[f"common_{common}_step_{step}"]={"eligible_pairs":len(elig),
   "all5_eligible":len(elig)==5,
   "mean_A_minus_B_damage_pp_if_eligible":statistics.mean(v["A_minus_B_damage_pp"] for v in elig) if elig else None,
   "seedwise_A_minus_B_damage_pp_if_eligible":[v["A_minus_B_damage_pp"] for v in elig],
   "mean_A_minus_B_neffective_if_eligible":statistics.mean(v["A_minus_B_neffective"] for v in elig) if elig else None}
res={"protocol":"PREREG_V11.md","scope":"exploratory, noncausal; masks nested in seed",
 "mask_seeds":[2001,2100],"n_masks_per_model":100,
 "all_results":records,"paired":comparison,"summary":summary}
(ROOT/"V11_ROBUSTNESS.json").write_text(json.dumps(res,indent=2,ensure_ascii=False),encoding="utf-8")
print("SUMMARY",json.dumps(summary,indent=2,ensure_ascii=False))
