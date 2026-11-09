"""V12 preregistered robustness replication.
Uses validation labels ONLY. No test data inspected by this script.
Same 100 physical masks per model within pairs; pair seed is replicate.
"""
from pathlib import Path
import json,statistics,itertools,math
import numpy as np
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data

torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
DIR=ROOT/"v12_runs"
gate=json.loads((ROOT/"V12_GATES.json").read_text(encoding="utf-8"))
seeds=list(gate["eligible_for_lesions"])
x,y,idx=data(20261110,500,1000,2000)
xx=x[idx["val"]];yy=y[idx["val"]]
# Explicitly do not access the test partition until audit is frozen.
mask_seeds=list(range(3101,3201))
stack=[]
for ms in mask_seeds:
 indices=np.random.default_rng(ms).choice(300,90,replace=False)
 arr=np.ones(300,dtype=np.float32)
 arr[indices]=0.
 stack.append(arr)
maskmat=torch.from_numpy(np.stack(stack)).T.contiguous()

@torch.no_grad()
def evaluate(seed,lam,step):
 directory=DIR/f"seed{seed}_prior{lam:g}"
 filename=directory/f"ck_{step:06d}.pt"
 if not filename.is_file():raise FileNotFoundError(filename)
 ck=torch.load(filename,map_location="cpu",weights_only=False)
 model=MLP(300)
 model.load_state_dict(ck["model"])
 model.eval()
 h=torch.relu(model.a(xx))
 w=model.b.weight[1]-model.b.weight[0]
 bias=model.b.bias[1]-model.b.bias[0]
 baseline=h@w+bias
 original=((baseline>0)==yy.bool()).float().mean()
 if float(original)<1.:
  raise RuntimeError(f"V12 checkpoint not fully eligible: {seed} {lam} {step} {float(original)}")
 augmented=h@(maskmat*w[:,None])+bias
 correct=((augmented>0)==yy.bool()[:,None]).float().mean(0)
 losses=F.binary_cross_entropy_with_logits(augmented,yy.float()[:,None].expand(-1,100),reduction="none").mean(0)
 basece=F.binary_cross_entropy_with_logits(baseline,yy.float())
 damage=(float(original)-correct)*100.
 weight_norm=torch.linalg.vector_norm(model.b.weight,dim=0)
 imp=h.abs().mean(0)*weight_norm
 shares=imp/(imp.sum()+1e-12)
 concentration=1.0/float((shares**2).sum())
 sorted_shares=shares.sort(descending=True).values
 return {"seed":seed,"lambda":lam,"step":step,"validation_accuracy_before":float(original),
         "damage_mean_pp":float(damage.mean()),"damage_median_pp":float(damage.median()),
         "damage_std_pp":float(damage.std(unbiased=False)),
         "damage_per_mask_pp":[float(z) for z in damage.tolist()],
         "ce_before":float(basece),
         "mean_ce_after":float(losses.mean()),"mean_ce_increase":float(losses.mean()-basece),
         "effective_neuron_count":concentration,
         "top5_share":float(sorted_shares[:5].sum()),
         "top10_share":float(sorted_shares[:10].sum())}

def run():
 results=[]
 comparisons=[]
 for seed in seeds:
  for step in (6000,10000):
   pair=[]
   for lam in (1e-5,.001):
    r=evaluate(seed,lam,step)
    results.append(r);pair.append(r)
    print("V12ROB",seed,lam,step,"damage",round(r["damage_mean_pp"],3),
          "n_eff",round(r["effective_neuron_count"],2),flush=True)
   a,b=pair
   comparisons.append({"seed":seed,"step":step,"A_minus_B_damage_pp":a["damage_mean_pp"]-b["damage_mean_pp"],
                       "A_minus_B_effective_neurons":a["effective_neuron_count"]-b["effective_neuron_count"],
                       "A_damage_pp":a["damage_mean_pp"],"B_damage_pp":b["damage_mean_pp"]})
 paired=[]
 for seed in seeds:
  bef=next(i for i in comparisons if i["seed"]==seed and i["step"]==6000)
  aft=next(i for i in comparisons if i["seed"]==seed and i["step"]==10000)
  paired.append({"seed":seed,"before_difference":bef["A_minus_B_damage_pp"],
     "after_difference":aft["A_minus_B_damage_pp"],
     "change_after_minus_before":aft["A_minus_B_damage_pp"]-bef["A_minus_B_damage_pp"],
     "absolute_gap_reduction":abs(bef["A_minus_B_damage_pp"])-abs(aft["A_minus_B_damage_pp"])})
 values=[z["change_after_minus_before"] for z in paired]
 def summary(values):
  if not values:return None
  return {"mean":statistics.mean(values),"minimum":min(values),"maximum":max(values),
    "values":values,"sd_sample":statistics.stdev(values) if len(values)>1 else None}
 def signif(vals):
  if len(vals)==0 or len(vals)>15:return None
  obs=abs(statistics.mean(vals))
  null=[abs(statistics.mean(s*v for s,v in zip(signs,vals))) for signs in itertools.product((-1,1),repeat=len(vals))]
  return sum(z>=obs-1e-12 for z in null)/len(null)
 res={"protocol":"PREREG_V12.md","test_evaluated":False,
      "all_seeds_requested":list(range(10,20)),
      "eligible_seeds":seeds,"seed_pair_n":len(seeds),
      "mask_seed_range":[3101,3200],
      "outcomes_by_model":results,"comparisons":comparisons,
      "paired_changes":paired,
      "summary":{"before_gap":summary([z["before_difference"] for z in paired]),
        "after_gap":summary([z["after_difference"] for z in paired]),
        "reduction_abs_gap":summary([z["absolute_gap_reduction"] for z in paired]),
        "change_after_minus_before":summary(values),
        "signflip_two_sided_exploratory":signif(values)},
      "limitations":"This is the effect of earlier L1 schedules plus their histories, not a causal isolated grokking effect."}
 (ROOT/"V12_ROBUSTNESS.json").write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding="utf-8")
 print("SUMMARY",json.dumps({"eligible":seeds,"summary":res["summary"]},ensure_ascii=False),flush=True)

if __name__=="__main__":run()
