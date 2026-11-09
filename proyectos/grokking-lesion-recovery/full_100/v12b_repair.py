"""V12B: replicate post-lesion recovery on new seed pairs and a new dataset.
No test partition is consulted during training, eligibility, or lesion analysis.
See PREREG_V12B.md. All masks random and fixed *before* recovery.
"""
from pathlib import Path
import json,copy,csv
import numpy as np
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data

torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
data_root=ROOT/"v12_runs"
output=ROOT/"v12b_repair"
output.mkdir(exist_ok=True)
gates=json.loads((ROOT/"V12_GATES.json").read_text(encoding="utf-8"))
seeds=gates["eligible_for_lesions"]
# The first-stage and second-stage validation gates have already been frozen.
assert seeds == json.loads((ROOT/"V12_ROBUSTNESS.json").read_text(encoding="utf-8"))["eligible_seeds"]
x,y,idx=data(20261110,500,1000,2000)
train_x=x[idx["train"]];train_y=y[idx["train"]]
val_x=x[idx["val"]];val_y=y[idx["val"]]
assert len(val_y)==1000 and len(train_y)==500

@torch.no_grad()
def measure(m,step):
 m.eval()
 tr=m(train_x);va=m(val_x)
 return {"step":step,
  "train_acc":float((tr.argmax(1)==train_y).float().mean()),
  "val_acc":float((va.argmax(1)==val_y).float().mean()),
  "train_ce":float(F.cross_entropy(tr,train_y)),
  "val_ce":float(F.cross_entropy(va,val_y))}

def trajectory(model):
 optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0.)
 rec=[measure(model,0)]
 for step in range(1,501):
  model.train()
  optimizer.zero_grad(set_to_none=True)
  z=model(train_x)
  loss=F.cross_entropy(z,train_y)+.0001*sum(v.abs().sum() for v in model.parameters())
  loss.backward()
  optimizer.step()
  if step%10==0:rec.append(measure(model,step))
 return rec

def savecsv(path,arr):
 with path.open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=list(arr[0]))
  wr.writeheader();wr.writerows(arr)

def rec_time(arr):
 for i in range(len(arr)-1):
  if arr[i]["val_acc"]>=.99 and arr[i+1]["val_acc"]>=.99:
   return arr[i]["step"]
 return None

def run():
 rows=[]
 for seed in seeds:
  for lam in (1e-5,.001):
   name=f"seed{seed}_prior{lam:g}"
   cp=data_root/name/"ck_010000.pt"
   ck=torch.load(cp,map_location="cpu",weights_only=False)
   net=MLP(300);net.load_state_dict(ck["model"])
   base=measure(net,0)
   if base["train_acc"]<1. or base["val_acc"]<1.:raise RuntimeError("Ineligible model")
   dir=output/name
   dir.mkdir(exist_ok=True)
   control=trajectory(copy.deepcopy(net))
   savecsv(dir/"control.csv",control)
   for maskseed in range(3201,3211):
    indices=sorted(np.random.default_rng(maskseed).choice(300,90,replace=False).tolist())
    damaged=copy.deepcopy(net)
    with torch.no_grad():damaged.mask[indices]=0
    tr=trajectory(damaged)
    damage=100*(1.0-tr[0]["val_acc"])
    area=0.0
    for j in range(1,len(tr)):
     d0=control[j-1]["val_acc"]-tr[j-1]["val_acc"]
     d1=control[j]["val_acc"]-tr[j]["val_acc"]
     area+=(d0+d1)/2*(tr[j]["step"]-tr[j-1]["step"])
    obj={"seed":seed,"prior_lambda":lam,"dose":90,"maskseed":maskseed,
      "indices":indices,"common_l1":.0001,"repair_l1":.0001,
      "initial_val_damage_pp":damage,
      "initial_train_damage_pp":100*(1-tr[0]["train_acc"]),
      "initial_val_ce":tr[0]["val_ce"],
      "recovery_step_two_consecutive":rec_time(tr),
      "auc_val_deficit_vs_control":area,
      "normalized_auc_if_damage_gt2pp":area/(damage/100) if damage>2 else None,
      "control_val_final":control[-1]["val_acc"],
      "injured_val_final":tr[-1]["val_acc"]}
    rows.append(obj)
    savecsv(dir/f"mask{maskseed}.csv",tr)
    print("V12B",seed,f"{lam:g}",maskseed,
     "damage_pp",round(damage,2),"recovery_step",obj["recovery_step_two_consecutive"],
     "auc",round(area,3),flush=True)
  (ROOT/"V12B_RAW.json").write_text(json.dumps({
    "protocol":"PREREG_V12B.md","test_not_inspected":True,
    "scope":"new split and seeds; inherited L1 regimes confounded",
    "eligible_network_seeds":seeds,"results":rows},indent=2,ensure_ascii=False),encoding="utf-8")
 print("V12B_COMPLETE",len(rows),flush=True)

if __name__=="__main__":run()
