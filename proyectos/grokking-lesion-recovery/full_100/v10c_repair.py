"""V10C: execute the predeclared matched-on-validation-damage sensitivity.
Selected masks were frozen in V10C_MASK_SCAN.json before any repair runs.
Each model seed is an independent replication; masks within a seed are nested.
"""
from pathlib import Path
import csv,copy,json,math,statistics
import numpy as np
import torch
from parity_v10 import MLP,data,measure
from lesion_v10 import repair,first_stable
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
scan=json.loads((ROOT/"V10C_MASK_SCAN.json").read_text(encoding="utf-8"))
assert scan["mask_seed_range"]==[1001,2000]
assert scan["dose"]==150
x,y,ids=data(20261109,500,1000,2000)
results=[]
out=ROOT/"parity_matched_lesions"
out.mkdir(exist_ok=True)
for seeditem in scan["per_seed"]:
 seed=seeditem["seed"]
 chosen=seeditem["selected_first5"]
 print("FROZEN",seed,"num",len(chosen),"masks",[z["mask"] for z in chosen],flush=True)
 for lam in (1e-5,.001):
  name=f"lambda{lam:g}_seed{seed}_lr0.001_width300_nt500"
  ck=torch.load(ROOT/"parity_runs"/name/"ck_008000.pt",map_location="cpu",weights_only=False)
  net=MLP(300);net.load_state_dict(ck["model"])
  base=measure(net,x,y,ids,0)
  if base["train_acc"]!=1. or base["val_acc"]!=1. or base["test_acc"]!=1.:raise RuntimeError("Wrong prelesion 100% checkpoint")
  sub=out/name
  sub.mkdir(exist_ok=True)
  control=repair(copy.deepcopy(net),x,y,ids,400,10,.001)
  with (sub/"control.csv").open("w",newline="",encoding="utf-8") as f:
   wr=csv.DictWriter(f,fieldnames=list(control[0]));wr.writeheader();wr.writerows(control)
  for maskdetail in chosen:
   ms=maskdetail["mask"]
   indices=sorted(np.random.default_rng(ms).choice(300,150,replace=False).tolist())
   damaged=copy.deepcopy(net)
   with torch.no_grad():damaged.mask[indices]=0.
   trajectory=repair(damaged,x,y,ids,400,10,.001)
   valdamage=100*(base["val_acc"]-trajectory[0]["val_acc"])
   assert abs(valdamage-maskdetail["damage_grok_pp" if lam==1e-5 else "damage_continuous_pp"])<.01
   auc={}
   for part in ("val","test"):
    diffs=[c[part+"_acc"]-d[part+"_acc"] for c,d in zip(control,trajectory)]
    auc[part]=sum((diffs[i]+diffs[i+1])/2*(trajectory[i+1]["step"]-trajectory[i]["step"]) for i in range(len(trajectory)-1))
   ftest=first_stable([{**r,"val_acc":r["test_acc"]} for r in trajectory],.99,2)
   with torch.no_grad():
    net.eval()
    vv=net(x[ids["val"]])
    hk=torch.relu(net.a(x[ids["val"]]))
    altered=net.b(hk*damaged.mask)
    valwrong=(altered.argmax(1)!=y[ids["val"]]).nonzero().flatten().tolist()
   item={
     "seed":seed,"lambda":lam,"group":"grok" if lam==1e-5 else "continuous",
     "mask_seed":ms,"dose":150,"indices":indices,
     "initial_val_damage_pp":valdamage,
     "initial_test_damage_pp":100*(base["test_acc"]-trajectory[0]["test_acc"]),
     "initial_train_damage_pp":100*(base["train_acc"]-trajectory[0]["train_acc"]),
     "initial_val_loss":trajectory[0]["val_loss"],
     "recovery99_val_step":first_stable(trajectory,.99,2),
     "recovery99_test_step":ftest,
     "auc_val":auc["val"],"auc_test":auc["test"],
     "normalized_auc_val":auc["val"]/(valdamage/100) if valdamage>0 else None,
     "final_val_acc":trajectory[-1]["val_acc"],"final_test_acc":trajectory[-1]["test_acc"],
     "control_val_final":control[-1]["val_acc"],"control_test_final":control[-1]["test_acc"],
     "incorrect_val_case_indices":valwrong,
    }
   results.append(item)
   with (sub/f"matched_mask{ms}.csv").open("w",newline="",encoding="utf-8") as f:
    wr=csv.DictWriter(f,fieldnames=list(trajectory[0]));wr.writeheader();wr.writerows(trajectory)
   print("MATCHED_REPAIR",seed,lam,ms,"damage",round(valdamage,2),"recov",item["recovery99_val_step"],"auc",round(item["auc_val"],3),flush=True)
 (ROOT/"V10C_MATCHED_RAW.json").write_text(json.dumps({"protocol":"PREREG_V10C.md","scope":"post-hoc damage-matched sensitivity, NOT primary causal effect","results":results},ensure_ascii=False,indent=2),encoding="utf-8")
print("FINISHED",len(results))
