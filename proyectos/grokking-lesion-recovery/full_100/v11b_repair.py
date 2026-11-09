"""V11B reconstruction after BOTH histories share 4000 steps common L1.
No mask/outcome-based selection. See PREREG_V11B.md.
"""
from pathlib import Path
import copy,csv,json,math
import torch
import numpy as np
from parity_v10 import MLP,data,measure
from lesion_v10 import repair,first_stable
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"v11b_repair"
OUT.mkdir(exist_ok=True)
x,y,ids=data(20261109,500,1000,2000)
records=[]
for seed in range(5):
 for lam in (1e-5,.001):
  name=f"lambda{lam:g}_seed{seed}_lr0.001_width300_nt500"
  cp=ROOT/"v11_common_runs"/f"{name}_commonL1_0.0001_4000"/"ck_009000.pt"
  blob=torch.load(cp,map_location="cpu",weights_only=False)
  m=MLP(300);m.load_state_dict(blob["model"])
  initial=measure(m,x,y,ids,0)
  assert initial["train_acc"]==initial["val_acc"]==1.,f"Model ineligible {name}"
  folder=OUT/name
  folder.mkdir(exist_ok=True)
  cont=repair(copy.deepcopy(m),x,y,ids,500,10,.001)
  with (folder/"control.csv").open("w",newline="",encoding="utf-8") as f:
   writer=csv.DictWriter(f,fieldnames=list(cont[0]));writer.writeheader();writer.writerows(cont)
  for maskseed in range(2101,2111):
   picks=sorted(np.random.default_rng(maskseed).choice(300,90,replace=False).tolist())
   d=copy.deepcopy(m)
   with torch.no_grad():d.mask[picks]=0.
   traj=repair(d,x,y,ids,500,10,.001)
   damage_pp=100*(initial["val_acc"]-traj[0]["val_acc"])
   diff=[c["val_acc"]-r["val_acc"] for c,r in zip(cont,traj)]
   auc=sum((diff[i]+diff[i+1])/2*(traj[i+1]["step"]-traj[i]["step"]) for i in range(len(diff)-1))
   rt=first_stable(traj,.99,2)
   item={"seed":seed,"prior_lambda":lam,"common_lambda":.0001,
         "maskseed":maskseed,"dose":90,"indices":picks,
         "baseline":initial,"injured_initial":traj[0],
         "initial_damage_val_pp":damage_pp,
         "control_final":cont[-1],"injured_final":traj[-1],
         "time_to99_2consecutive":rt,"auc_val":auc,
         "normalized_auc_if_initial_damage":auc/(damage_pp/100) if damage_pp>=2 else None}
   records.append(item)
   with (folder/f"mask{maskseed}.csv").open("w",newline="",encoding="utf-8") as f:
    writer=csv.DictWriter(f,fieldnames=list(traj[0]));writer.writeheader();writer.writerows(traj)
   print("V11B",seed,lam,maskseed,"damage_pp",round(damage_pp,2),"recover",rt,"auc",round(auc,3),flush=True)
 (ROOT/"V11B_RAW.json").write_text(json.dumps({"scope":"exploratory, reg-common repair; n=5 seed pairs",
  "protocol":"PREREG_V11B.md","n_masks_per_network":10,"results":records},indent=2,ensure_ascii=False),encoding="utf-8")
print("FINISHED",len(records))
