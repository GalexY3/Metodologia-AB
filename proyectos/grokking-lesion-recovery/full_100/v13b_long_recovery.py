"""V13B: 90% ablation with new masks and 2000-step repair horizon.
See PREREG_V13B_LONG_RECOVERY.md. Explicitly post hoc relative to V13.
"""
from pathlib import Path
import json,csv,copy,time
import numpy as np
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data
torch.set_num_threads(4)

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"v13b_long_runs"
OUT.mkdir(exist_ok=True)
SEEDS=json.loads((ROOT/"V12_GATES.json").read_text(encoding="utf-8"))["eligible_for_lesions"]
assert SEEDS==[11,12,13,14,18]
MASKS=[4201,4202,4203,4204]
x,y,ids=data(20261110,500,1000,2000)
train_x=x[ids["train"]];train_y=y[ids["train"]]
val_x=x[ids["val"]];val_y=y[ids["val"]]

@torch.no_grad()
def metric(m,step):
 m.eval()
 ztrain=m(train_x);zval=m(val_x)
 return {"step":step,
  "train_accuracy":float((ztrain.argmax(1)==train_y).float().mean()),
  "val_accuracy":float((zval.argmax(1)==val_y).float().mean()),
  "train_ce":float(F.cross_entropy(ztrain,train_y)),
  "val_ce":float(F.cross_entropy(zval,val_y))}

def train(model):
 opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0.)
 rows=[metric(model,0)]
 for step in range(1,2001):
  model.train();opt.zero_grad(set_to_none=True)
  z=model(train_x)
  loss=F.cross_entropy(z,train_y)+.0001*sum(v.abs().sum() for v in model.parameters())
  loss.backward();opt.step()
  if step%25==0:rows.append(metric(model,step))
 return rows

def csvwrite(path,rows):
 with path.open("w",newline="",encoding="utf-8") as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]))
  writer.writeheader();writer.writerows(rows)

def csvread(path):
 with path.open(newline="",encoding="utf-8") as f:
  return [{k:float(v) for k,v in z.items()} for z in csv.DictReader(f)]

def first_stable(rows):
 return next((int(rows[i]["step"]) for i in range(len(rows)-1)
  if rows[i]["val_accuracy"]>=.99 and rows[i+1]["val_accuracy"]>=.99),None)

def integrate(rows,control,start,end):
 area=0.
 for i in range(1,len(rows)):
  x0=int(rows[i-1]["step"]);x1=int(rows[i]["step"])
  if x0<start or x1>end:continue
  d0=control[i-1]["val_accuracy"]-rows[i-1]["val_accuracy"]
  d1=control[i]["val_accuracy"]-rows[i]["val_accuracy"]
  area+=(d0+d1)/2*(x1-x0)
 return area

def run():
 start=time.perf_counter()
 for seed in SEEDS:
  for lam in (1e-5,.001):
   name=f"seed{seed}_prior{lam:g}"
   ck=torch.load(ROOT/"v12_runs"/name/"ck_010000.pt",map_location="cpu",weights_only=False)
   net=MLP(300);net.load_state_dict(ck["model"])
   base=metric(net,0)
   assert base["train_accuracy"]==base["val_accuracy"]==1.
   folder=OUT/name
   folder.mkdir(exist_ok=True)
   control_path=folder/"control.csv"
   if control_path.exists():
    control=csvread(control_path)
   else:
    control=train(copy.deepcopy(net))
    csvwrite(control_path,control)
   assert len(control)==81
   for ms in MASKS:
    basename=f"kill270_mask{ms}"
    outjson=folder/(basename+".json")
    outcsv=folder/(basename+".csv")
    if outjson.exists() and outcsv.exists():continue
    if outjson.exists()!=outcsv.exists():raise RuntimeError("Partial evidence "+basename)
    picked=sorted(np.random.default_rng(ms).permutation(300)[:270].tolist())
    damaged=copy.deepcopy(net)
    with torch.no_grad():damaged.mask[picked]=0
    traj=train(damaged)
    initdamage=(1-traj[0]["val_accuracy"])*100
    rec=first_stable(traj)
    item={"seed":seed,"initial_lambda":lam,"common_l1":.0001,"repair_l1":.0001,
     "masked_neurons":270,"total_neurons":300,"maskseed":ms,"indices":picked,
     "initial_val_damage_pp":initdamage,"initial_val_ce_increase":traj[0]["val_ce"]-base["val_ce"],
     "recovery99_step":rec,"censored_at2000":rec is None,
     "recovered_by_500":rec is not None and rec<=500,
     "recovered_by_1000":rec is not None and rec<=1000,
     "recovered_by_1500":rec is not None and rec<=1500,
     "recovered_by_2000":rec is not None and rec<=2000,
     "auc_0_500":integrate(traj,control,0,500),
     "auc_500_1000":integrate(traj,control,500,1000),
     "auc_1000_2000":integrate(traj,control,1000,2000),
     "auc_0_2000":integrate(traj,control,0,2000),
     "control_val_final":control[-1]["val_accuracy"],
     "injured_val_final":traj[-1]["val_accuracy"],
     "injured_train_final":traj[-1]["train_accuracy"]}
    csvwrite(outcsv,traj)
    outjson.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding="utf-8")
    print("V13B",seed,lam,ms,"initial_damage_pp",round(initdamage,1),
          "recover_step",rec if rec is not None else "CENSORED",
          "final_val",round(traj[-1]["val_accuracy"],3),
          "elapsed",round(time.perf_counter()-start,1),flush=True)
 print("V13B_COMPLETED",round(time.perf_counter()-start,1),flush=True)

if __name__=="__main__":run()
