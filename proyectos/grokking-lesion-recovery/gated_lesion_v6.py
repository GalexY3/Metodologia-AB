"""Lesion + equal-repair-optimizer pilot for the V6 gated architecture.
Each perturbation masks exactly 15 clean + 15 random-label neurons (10% each).
All branches get identical fresh AdamW repair hyperparams, isolating representation
from DIFFERENT AdamW moments and WD used during acquisition.
"""
from __future__ import annotations
import argparse,json,copy,csv,math
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from gated_v6 import GatedNet,build_data,measure
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent

def study(a):
 blob=torch.load(a.checkpoint,map_location="cpu",weights_only=False)
 c=blob["config"]
 x,y,idx=build_data(c["p"],c["noise_total"],c["train_frac"],c["valid_frac"],c["split_seed"])
 net=GatedNet(c["p"],c["dim"],c["branch_hidden"])
 net.load_state_dict(blob["model"])
 if net.clean.mask.numel()!=150 or net.noise.mask.numel()!=150:raise RuntimeError("Expected 300 units")
 rng=np.random.default_rng(a.mask_seed)
 pick_clean=sorted(rng.choice(150,size=a.clean_k,replace=False).tolist())
 pick_noise=sorted(rng.choice(150,size=a.noise_k,replace=False).tolist())
 init=measure(net,x,y,idx,0)
 branches={}
 for arm in ("no_lesion","lesion"):
  m=copy.deepcopy(net)
  if arm=="lesion":
   with torch.no_grad():
    m.clean.mask[pick_clean]=0.
    m.noise.mask[pick_noise]=0.
  opt=torch.optim.AdamW(m.parameters(),lr=a.repair_lr,weight_decay=a.repair_wd)
  rows=[]
  for s in range(a.steps+1):
   if s%a.record_every==0 or s==a.steps:
    row=measure(m,x,y,idx,s);rows.append({"arm":arm,**row})
   if s==a.steps:break
   opt.zero_grad(set_to_none=True)
   loss=F.cross_entropy(m(x[idx["train"]]),y[idx["train"]])
   loss.backward();opt.step()
  branches[arm]=rows
 out=ROOT/"gated_lesions"/(Path(a.checkpoint).parent.name+"_"+Path(a.checkpoint).stem+f"_c{a.clean_k}_n{a.noise_k}_mask{a.mask_seed}")
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True)
 with (out/"metrics.csv").open("w",newline="",encoding="utf-8") as f:
  rows=branches["no_lesion"]+branches["lesion"]
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 baseline=branches["no_lesion"][0]["val_acc"]
 injured=branches["lesion"][0]["val_acc"]
 threshold=baseline*.95
 rec=next((r["step"] for r in branches["lesion"] if r["val_acc"]>=threshold),None)
 diffs=[(base["val_acc"]-les["val_acc"]) for base,les in zip(branches["no_lesion"],branches["lesion"])]
 # Integrate signed deficit, not clipped: a lesion could outperform control at some steps.
 auc=sum((p+q)/2*a.record_every for p,q in zip(diffs[:-1],diffs[1:]))
 result={"checkpoint":str(Path(a.checkpoint).resolve()),"checkpoint_step":blob["step"],
  "mask_seed":a.mask_seed,"masked_clean":pick_clean,"masked_noise":pick_noise,"n_clean":a.clean_k,"n_noise":a.noise_k,
  "repair_optimizer":{"type":"AdamW fresh","lr":a.repair_lr,"wd":a.repair_wd},
  "baseline_validation":baseline,"initial_after_validation":injured,
  "initial_damage_pp":100*(baseline-injured),"first_recovery_to_95pct_original_step":rec,
  "final_lesion_val":branches["lesion"][-1]["val_acc"],
  "final_no_lesion_val":branches["no_lesion"][-1]["val_acc"],
  "integrated_control_minus_lesion_val_auc_step":auc,
  "initial_train_damage_pp":100*(init["train_acc"]-branches["lesion"][0]["train_acc"])}
 (out/"summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print("LESION",json.dumps({"net":Path(a.checkpoint).parent.name,"step":blob["step"],"mask":a.mask_seed,"base":round(baseline,3),"initial":round(injured,3),"lost_pp":round(result["initial_damage_pp"],2),"recovery":rec,"end":round(result["final_lesion_val"],3),"end_control":round(result["final_no_lesion_val"],3),"auc":round(auc,2)}),flush=True)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--checkpoint",required=True)
 p.add_argument("--mask-seed",type=int,default=11)
 p.add_argument("--clean-k",type=int,default=15)
 p.add_argument("--noise-k",type=int,default=15)
 p.add_argument("--repair-lr",type=float,default=.001)
 p.add_argument("--repair-wd",type=float,default=.1)
 p.add_argument("--steps",type=int,default=300)
 p.add_argument("--record-every",type=int,default=10)
 study(p.parse_args())
