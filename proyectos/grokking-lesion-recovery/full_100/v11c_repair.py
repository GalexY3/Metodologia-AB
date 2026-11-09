"""V11C: same group history, shared final L1, and L1 maintained during repair.
Pre-declared seeds 2111..2120, 90/300 units. No lesion selection.
"""
from pathlib import Path
import copy,csv,json
import numpy as np
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data,measure
from lesion_v10 import first_stable
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"v11c_repair";OUT.mkdir(exist_ok=True)
x,y,ids=data(20261109,500,1000,2000)

def repair_l1(model):
 opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0.)
 rows=[measure(model,x,y,ids,0)]
 for step in range(1,501):
  model.train();opt.zero_grad(set_to_none=True)
  loss=F.cross_entropy(model(x[ids["train"]]),y[ids["train"]])+.0001*sum(v.abs().sum() for v in model.parameters())
  loss.backward();opt.step()
  if step%10==0:rows.append(measure(model,x,y,ids,step))
 return rows

records=[]
for seed in range(5):
 for lam in (1e-5,.001):
  name=f"lambda{lam:g}_seed{seed}_lr0.001_width300_nt500"
  cp=ROOT/"v11_common_runs"/f"{name}_commonL1_0.0001_4000"/"ck_009000.pt"
  blob=torch.load(cp,map_location="cpu",weights_only=False)
  net=MLP(300);net.load_state_dict(blob["model"])
  before=measure(net,x,y,ids,0)
  if before["train_acc"]!=1. or before["val_acc"]!=1.:raise ValueError(f"Ineligible {name}")
  dest=OUT/name;dest.mkdir(exist_ok=True)
  control=repair_l1(copy.deepcopy(net))
  with (dest/"control.csv").open("w",newline="",encoding="utf-8") as f:
   wr=csv.DictWriter(f,fieldnames=list(control[0]));wr.writeheader();wr.writerows(control)
  for ms in range(2111,2121):
   ix=sorted(np.random.default_rng(ms).choice(300,90,replace=False).tolist())
   injured=copy.deepcopy(net)
   with torch.no_grad():injured.mask[ix]=0.
   traj=repair_l1(injured)
   before_damage=100*(before["val_acc"]-traj[0]["val_acc"])
   diffs=[c["val_acc"]-d["val_acc"] for c,d in zip(control,traj)]
   auc=sum((diffs[i]+diffs[i+1])/2*(traj[i+1]["step"]-traj[i]["step"]) for i in range(len(diffs)-1))
   item={"seed":seed,"initial_lambda":lam,"common_lambda":.0001,"repair_lambda":.0001,"maskseed":ms,"indices":ix,
     "dose":90,"initial_damage_val_pp":before_damage,
     "damage_initial_train_pp":100*(before["train_acc"]-traj[0]["train_acc"]),
     "initial_val_ce":traj[0]["val_loss"],"control_final":control[-1],
     "injured_final":traj[-1],"auc_val":auc,
     "recovery_val99_two_consecutive_step":first_stable(traj,.99,2),
     "normalized_auc_if_damage":auc/(before_damage/100) if before_damage>2 else None}
   records.append(item)
   with (dest/f"mask{ms}.csv").open("w",newline="",encoding="utf-8") as f:
    wr=csv.DictWriter(f,fieldnames=list(traj[0]));wr.writeheader();wr.writerows(traj)
   print("V11C",seed,lam,ms,"damage",round(before_damage,2),"recovery",item["recovery_val99_two_consecutive_step"],"auc",round(auc,3),flush=True)
 (ROOT/"V11C_RAW.json").write_text(json.dumps({"protocol":"PREREG_V11C.md","scope":"exploratory, common L1 maintained",
   "results":records},indent=2,ensure_ascii=False),encoding="utf-8")
print("COMPLETE",len(records))
