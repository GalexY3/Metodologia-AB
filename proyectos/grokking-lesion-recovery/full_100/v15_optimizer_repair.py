"""V15 permanent lesions from identical weights, varying ONLY AdamW state.

Fresh vs restored optimizer moments after loss under same L1 1e-4.
No test partition accessed. See PREREG_V15_OPTIMIZER_REPAIR.md.
"""
from pathlib import Path
import json,csv,copy,time
import numpy as np
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"v15_repair"
OUT.mkdir(exist_ok=True)
SEEDS=[11,12,13,14,18]
D0SES=[90,180,270]
MASKS=[4501,4502,4503,4504]
x,y,ids=data(20261110,500,1000,2000)
train_x=x[ids["train"]];train_y=y[ids["train"]]
val_x=x[ids["val"]];val_y=y[ids["val"]]
perm={ms:np.random.default_rng(ms).permutation(300).tolist() for ms in MASKS}
@torch.no_grad()
def measure(m,step):
 m.eval()
 a=m(train_x);b=m(val_x)
 return {"step":step,
  "train_acc":float((a.argmax(1)==train_y).float().mean()),
  "val_acc":float((b.argmax(1)==val_y).float().mean()),
  "train_ce":float(F.cross_entropy(a,train_y)),
  "val_ce":float(F.cross_entropy(b,val_y))}
def stepforward(m,mode,old):
 opt=torch.optim.AdamW(m.parameters(),lr=.001,weight_decay=0.)
 if mode=="resumed":
  # In PyTorch 2.15, load_state_dict can reuse storage from the supplied
  # state dict. Copy it so every lesion starts from INDEPENDENT moments.
  isolated=copy.deepcopy(old)
  opt.load_state_dict(isolated)
  if len(opt.state)==0:raise RuntimeError("optimizer not restored")
  for key,(_,state) in zip(old["state"].keys(),opt.state.items()):
   for name,original_tensor in old["state"][key].items():
    if isinstance(original_tensor,torch.Tensor) and original_tensor.data_ptr()==state[name].data_ptr():
     raise RuntimeError("Unsafe AdamW state alias detected: "+str((key,name)))
  assert abs(opt.param_groups[0]["lr"]-.001)<1e-12
  assert abs(opt.param_groups[0]["weight_decay"])<1e-12
 rows=[measure(m,0)]
 for step in range(1,501):
  m.train();opt.zero_grad(set_to_none=True)
  loss=F.cross_entropy(m(train_x),train_y)+.0001*sum(w.abs().sum() for w in m.parameters())
  loss.backward();opt.step()
  if step%10==0:rows.append(measure(m,step))
 return rows
def savecsv(path,rows):
 with path.open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]))
  wr.writeheader();wr.writerows(rows)
def loadcsv(path):
 with path.open(newline="",encoding="utf-8") as f:
  return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]
def recovery(rows):
 return next((int(rows[i]["step"]) for i in range(len(rows)-1)
             if rows[i]["val_acc"]>=.99 and rows[i+1]["val_acc"]>=.99),None)
def run():
 clock=time.perf_counter()
 for seed in SEEDS:
  for initial in (1e-5,.001):
   name=f"seed{seed}_prior{initial:g}"
   payload=torch.load(ROOT/"v15_optimizer_states"/name/"ck_010000_with_optimizer.pt",
    map_location="cpu",weights_only=False)
   assert payload["config"]["weights_verified"]
   model=MLP(300);model.load_state_dict(payload["model"])
   before=measure(model,0)
   assert before["train_acc"]==before["val_acc"]==1.
   for mode in ("fresh","resumed"):
    folder=OUT/name/mode
    folder.mkdir(parents=True,exist_ok=True)
    control_path=folder/"control.csv"
    if control_path.exists():
     control=loadcsv(control_path)
    else:
     control=stepforward(copy.deepcopy(model),mode,payload["optimizer"])
     savecsv(control_path,control)
    assert len(control)==51
    for dose in D0SES:
     for ms in MASKS:
      outname=f"dose{dose:03d}_mask{ms}"
      jsonpath=folder/(outname+".json")
      csvpath=folder/(outname+".csv")
      if jsonpath.exists() and csvpath.exists():continue
      if jsonpath.exists()!=csvpath.exists():raise RuntimeError("partial data "+str(jsonpath))
      injured=copy.deepcopy(model)
      indices=sorted(perm[ms][:dose])
      with torch.no_grad():injured.mask[indices]=0.
      traj=stepforward(injured,mode,payload["optimizer"])
      initial_drop=(1-traj[0]["val_acc"])*100
      t=recovery(traj)
      gaps=[c["val_acc"]-d["val_acc"] for c,d in zip(control,traj)]
      auc=sum((gaps[i]+gaps[i+1])/2*(traj[i+1]["step"]-traj[i]["step"]) for i in range(len(gaps)-1))
      outcome={"seed":seed,"initial_l1":initial,"final_l1":.0001,
       "mode":mode,"step_checkpoint":10000,
       "mask_seed":ms,"dose":dose,"masked_indices":indices,
       "init_damage_val_pp":initial_drop,"init_val_ce":traj[0]["val_ce"],
       "recovery_step":t,"censored_at500":t is None,
       "auc_val_control_deficit":auc,
       "norm_auc_damage_gt2pp":auc/(initial_drop/100) if initial_drop>2 else None,
       "control_val_final":control[-1]["val_acc"],
       "injured_val_final":traj[-1]["val_acc"],
       "same_model_prelesion_weights":True,
       "optimizer_state_is_only_mode_difference":True}
      savecsv(csvpath,traj)
      jsonpath.write_text(json.dumps(outcome,ensure_ascii=False,indent=2),encoding="utf-8")
      print("V15",seed,f"{initial:g}",mode,f"{dose}/300",ms,
       "damage_pp",round(initial_drop,2),"recover",t if t is not None else "CENSORED",
       "auc",round(auc,2),"elapsed",round(time.perf_counter()-clock,1),flush=True)
 print("V15_DONE",round(time.perf_counter()-clock,1),flush=True)
if __name__=="__main__":run()
