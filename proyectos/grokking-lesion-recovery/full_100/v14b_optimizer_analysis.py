"""V14B optimizer-state control, plus a mechanistic margin probe.
Same 100 mask seeds as V14 (4301..4400), no test data.
"""
from pathlib import Path
import json,statistics,itertools
import numpy as np
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
previous=json.loads((ROOT/"V14_ANALYSIS.json").read_text(encoding="utf-8"))
historical=json.loads((ROOT/"V14_TEMPORAL_CONTROL.json").read_text(encoding="utf-8"))
seeds=[11,12,13,14,18]
x,y,idx=data(20261110,500,1000,2000)
X=x[idx["val"]];Y=y[idx["val"]].bool()
mats=[]
for ms in range(4301,4401):
 z=np.ones(300,dtype=np.float32)
 z[np.random.default_rng(ms).choice(300,90,replace=False)]=0
 mats.append(z)
maskmat=torch.from_numpy(np.stack(mats)).T.contiguous()

@torch.no_grad()
def evaluate(net):
 net.eval()
 h=torch.relu(net.a(X))
 w=net.b.weight[1]-net.b.weight[0];b=net.b.bias[1]-net.b.bias[0]
 logits=h@w+b
 signed=(2*Y.float()-1)*logits
 test=((logits>0)==Y).float()
 a=float(test.mean())
 v=h@(maskmat*w[:,None])+b
 acc=((v>0)==Y[:,None]).float().mean(0)
 imp=h.abs().mean(0)*torch.linalg.vector_norm(net.b.weight,dim=0)
 imp=imp/(imp.sum()+1e-12)
 return {"accuracy":a,
  "mean_damage_pp":float((a-acc).mean()*100),
  "margin_mean":float(signed.mean()),
  "margin_median":float(signed.median()),
  "margin_p10":float(torch.quantile(signed,.1)),
  "val_ce":float(F.binary_cross_entropy_with_logits(logits,Y.float())),
  "effective_contributors":float(1/imp.square().sum())}
original_values={(z["seed"],z["origin"]):z for z in previous["observations"] if z["origin"]==z["final_l1"]}
baselines={(z["seed"],z["prior_l1"]):z for z in historical["baseline_step6000"]}
observations=[]
for seed in seeds:
 for lam in (1e-5,.001):
  name=f"seed{seed}_prior{lam:g}"
  cp=ROOT/"v14b_original_adam_moments"/name/"ck_010000.pt"
  info=json.loads((cp.parent/"result.json").read_text(encoding="utf-8"))
  net=MLP(300);net.load_state_dict(torch.load(cp,map_location="cpu",weights_only=False)["model"])
  res=evaluate(net)
  z={"seed":seed,"lambda":lam,"stable_last3":info["stable_last3"],
     **res,
     "baseline_damage_pp":baselines[(seed,lam)]["mean_damage_pp"],
     "fresh_optimizer_damage_pp":original_values[(seed,lam)]["mean_damage_pp"],
     "resume_minus_fresh_damage_pp":res["mean_damage_pp"]-original_values[(seed,lam)]["mean_damage_pp"]}
  observations.append(z)
  print("V14B_ROB",seed,lam,"baseline",round(z["baseline_damage_pp"],2),
    "fresh",round(z["fresh_optimizer_damage_pp"],2),
    "resumed",round(z["mean_damage_pp"],2),
    "p10margin",round(z["margin_p10"],3),flush=True)
pairs=[]
for seed in seeds:
 a=next(v for v in observations if v["seed"]==seed and v["lambda"]==1e-5)
 b=next(v for v in observations if v["seed"]==seed and v["lambda"]==.001)
 if not a["stable_last3"] or not b["stable_last3"]:raise RuntimeError("Not equally 100%")
 gap0=a["baseline_damage_pp"]-b["baseline_damage_pp"]
 gap1=a["fresh_optimizer_damage_pp"]-b["fresh_optimizer_damage_pp"]
 gap2=a["mean_damage_pp"]-b["mean_damage_pp"]
 pairs.append({"seed":seed,"gap_baseline":gap0,"gap_fresh":gap1,"gap_resumed":gap2,
   "shift_original_optimizer":gap2-gap0,
   "effect_optimizer_reset_on_gap":gap1-gap2,
   "A_margin_p10":a["margin_p10"],"B_margin_p10":b["margin_p10"],
   "A_val_CE":a["val_ce"],"B_val_CE":b["val_ce"]})
def avg(k):return statistics.mean(v[k] for v in pairs)
delta=[z["shift_original_optimizer"] for z in pairs]
nul=[abs(statistics.mean(s*v for s,v in zip(sig,delta))) for sig in itertools.product((-1,1),repeat=5)]
p=sum(z>=abs(statistics.mean(delta))-1e-12 for z in nul)/len(nul)
summary={"n_independent_pair_seeds":5,
 "mean_baseline_gap":avg("gap_baseline"),
 "mean_fresh_optimizer_gap":avg("gap_fresh"),
 "mean_resumed_optimizer_gap":avg("gap_resumed"),
 "mean_shift_with_resumed_optimizer":avg("shift_original_optimizer"),
 "paired_seed_shifts_with_resumed_optimizer":delta,
 "mean_difference_due_to_optimizer_reset":avg("effect_optimizer_reset_on_gap"),
 "signflip_p_two_sided_resumed_shift":p,
 "resumed_gap_sign_counts":{"A_better":sum(z["gap_resumed"]<0 for z in pairs),
  "B_better":sum(z["gap_resumed"]>0 for z in pairs)},
 "mean_margin_p10_A":avg("A_margin_p10"),"mean_margin_p10_B":avg("B_margin_p10")}
result={"protocol":"PREREG_V14B_OPTIMIZER.md",
  "mask_seeds":[4301,4400],"n_masks_per_model":100,
  "observations":observations,"paired":pairs,"summary":summary,
  "test_not_consulted":True,
  "scope":"exploratory, initial L1 conditions confounded with history; optimizer resume vs fresh is a controlled continuation within fixed seed"}
(ROOT/"V14B_ANALYSIS.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("V14B_ANALYSIS_SUMMARY",json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
