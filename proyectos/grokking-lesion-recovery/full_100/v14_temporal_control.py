"""V14: isolate extra-time vs changing final L1 using identical new lesion masks.
Loads V12 phase1 checkpoints at step6000 and all V14 final forks at step10000.
A/B acquisition-history contrast remains confounded by original L1.
"""
from pathlib import Path
import json,statistics,itertools
import numpy as np
import torch
from parity_v10 import MLP,data
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
v14=json.loads((ROOT/"V14_ANALYSIS.json").read_text(encoding="utf-8"))
seeds=[11,12,13,14,18]
x,y,ix=data(20261110,500,1000,2000)
xx=x[ix["val"]]; yy=y[ix["val"]].bool()
masks=[]
for ms in range(4301,4401):
 arr=np.ones(300,dtype=np.float32)
 arr[np.random.default_rng(ms).choice(300,90,replace=False)]=0.
 masks.append(arr)
maskmat=torch.from_numpy(np.stack(masks)).T.contiguous()
@torch.no_grad()
def baseline_model(seed,orig):
 ck=torch.load(ROOT/"v12_runs"/f"seed{seed}_prior{orig:g}"/"ck_006000.pt",
  map_location="cpu",weights_only=False)
 model=MLP(300);model.load_state_dict(ck["model"]);model.eval()
 h=torch.relu(model.a(xx))
 w=model.b.weight[1]-model.b.weight[0]
 b=model.b.bias[1]-model.b.bias[0]
 original=float(((h@w+b>0)==yy).float().mean())
 acc=((h@(maskmat*w[:,None])+b>0)==yy[:,None]).float().mean(0)
 return {"seed":seed,"prior_l1":orig,"step":6000,"accuracy":original,
  "mean_damage_pp":float((original-acc).mean()*100),
  "mask_damage":[float(z) for z in ((original-acc)*100).tolist()]}
baseline=[baseline_model(seed,orig) for seed in seeds for orig in (1e-5,.001)]
base={(r["seed"],r["prior_l1"]):r for r in baseline}
fin={(r["seed"],r["origin"],r["final_l1"]):r for r in v14["observations"]}
scenarios={
 "original_L1_maintained":(1e-5,.001),
 "common_L1_medium":(.0001,.0001),
 "crossed_L1_reversed":(.001,1e-5)
}
comparisons=[];summaries={}
def signflip(vals):
 n=len(vals)
 obs=abs(statistics.mean(vals))
 null=[abs(statistics.mean(s*v for s,v in zip(sig,vals))) for sig in itertools.product((-1,1),repeat=n)]
 return sum(z>=obs-1e-12 for z in null)/len(null)
for name,(finalA,finalB) in scenarios.items():
 rows=[]
 for seed in seeds:
  a0=base[(seed,1e-5)]
  b0=base[(seed,.001)]
  a=fin[(seed,1e-5,finalA)]
  b=fin[(seed,.001,finalB)]
  if not(a["full_last3"] and b["full_last3"]):raise RuntimeError("Ineligible pair")
  before=a0["mean_damage_pp"]-b0["mean_damage_pp"]
  after=a["mean_damage_pp"]-b["mean_damage_pp"]
  rows.append({"scenario":name,"seed":seed,
    "initial_gap_pp":before,"final_gap_pp":after,
    "shift_final_minus_initial_pp":after-before,
    "initial_damage_A":a0["mean_damage_pp"],"initial_damage_B":b0["mean_damage_pp"],
    "final_damage_A":a["mean_damage_pp"],"final_damage_B":b["mean_damage_pp"]})
  comparisons.append(rows[-1])
 summaries[name]={"n_pairs":len(rows),
   "average_gap_initial_pp":statistics.mean(r["initial_gap_pp"] for r in rows),
   "average_gap_final_pp":statistics.mean(r["final_gap_pp"] for r in rows),
   "mean_shift_pp":statistics.mean(r["shift_final_minus_initial_pp"] for r in rows),
   "per_seed_final_gap":[r["final_gap_pp"] for r in rows],
   "per_seed_shift":[r["shift_final_minus_initial_pp"] for r in rows],
   "n_seeds_gap_shrank_in_magnitude":sum(abs(r["final_gap_pp"])<abs(r["initial_gap_pp"]) for r in rows),
   "signflip_p_two_sided_shift":signflip([r["shift_final_minus_initial_pp"] for r in rows])}
# Direct effect of changing the post-6000 L1 within a fixed *individual* network.
within=[]
for seed in seeds:
 for orig in (1e-5,.001):
  lo=fin[(seed,orig,1e-5)]
  mid=fin[(seed,orig,.0001)]
  hi=fin[(seed,orig,.001)]
  assert lo["full_last3"] and mid["full_last3"] and hi["full_last3"]
  within.append({"seed":seed,"origin":orig,
   "damage_low":lo["mean_damage_pp"],"damage_medium":mid["mean_damage_pp"],
   "damage_high":hi["mean_damage_pp"],
   "low_minus_mid":lo["mean_damage_pp"]-mid["mean_damage_pp"],
   "high_minus_mid":hi["mean_damage_pp"]-mid["mean_damage_pp"],
   "low_minus_high":lo["mean_damage_pp"]-hi["mean_damage_pp"]})
aggregate_within={}
for dim in ("low_minus_mid","high_minus_mid","low_minus_high"):
 vals=[r[dim] for r in within]
 aggregate_within[dim]={"n_models":10,"mean_effect_pp":statistics.mean(vals),
     "range_pp":[min(vals),max(vals)],
     "signed_effects":vals,
     "n_positive":sum(x>0 for x in vals),"n_negative":sum(x<0 for x in vals)}
output={
 "protocol":"PREREG_V14_FACTORIAL.md",
 "mask_seeds":[4301,4400],
 "baseline_step6000":baseline,
 "scenario_comparisons":comparisons,
 "scenario_summary":summaries,
 "within_network_final_L1_interventions":within,
 "aggregate_within_network_interventions":aggregate_within,
 "interpretation":"If unchanged-L1 also converges, extra training time explains at least part of shrinkage previously attributed to common L1. Effect of changing final L1 is directly controlled within checkpoint but causal role of grokking alone remains unidentified.",
 "test_not_consulted":True}
(ROOT/"V14_TEMPORAL_CONTROL.json").write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
print("V14_TEMPORAL_SCENARIOS",json.dumps(summaries,ensure_ascii=False,indent=2),flush=True)
print("V14_WITHIN_MODEL_L1",json.dumps(aggregate_within,ensure_ascii=False,indent=2),flush=True)
