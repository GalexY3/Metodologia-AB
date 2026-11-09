"""V13 dose-response postablation recovery on V12 final-common-L1 networks.

Predefined before injury, see PREREG_V13_DOSE.md. All masks new; nested
permutations allow within-seed increasing-dose comparisons. No test data is
consulted. Writes one file per lesion so interrupted runs can resume exactly.
"""
from pathlib import Path
import json,csv,copy,time,hashlib
import numpy as np
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data

torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
RUNS=ROOT/"v12_runs"
OUT=ROOT/"v13_dose_runs"
OUT.mkdir(exist_ok=True)
GATES=json.loads((ROOT/"V12_GATES.json").read_text(encoding="utf-8"))
SEEDS=GATES["eligible_for_lesions"]
assert SEEDS==[11,12,13,14,18],SEEDS
D0SES=[30,60,90,120,150,180,210,240,270]
MASKS=[4101,4102,4103,4104]
x,y,idx=data(20261110,500,1000,2000)
train_x=x[idx["train"]];train_y=y[idx["train"]]
val_x=x[idx["val"]];val_y=y[idx["val"]]
perms={ms:np.random.default_rng(ms).permutation(300).tolist() for ms in MASKS}

@torch.no_grad()
def measure(net,step):
 net.eval()
 tr=net(train_x);va=net(val_x)
 return {"step":step,
  "train_accuracy":float((tr.argmax(1)==train_y).float().mean()),
  "val_accuracy":float((va.argmax(1)==val_y).float().mean()),
  "train_ce":float(F.cross_entropy(tr,train_y)),
  "val_ce":float(F.cross_entropy(va,val_y))}

def continue_train(net):
 opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=0)
 rows=[measure(net,0)]
 for step in range(1,501):
  net.train();opt.zero_grad(set_to_none=True)
  pred=net(train_x)
  loss=F.cross_entropy(pred,train_y)+.0001*sum(z.abs().sum() for z in net.parameters())
  loss.backward();opt.step()
  if step%10==0:rows.append(measure(net,step))
 return rows

def put_csv(path,rows):
 with path.open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]))
  wr.writeheader();wr.writerows(rows)

def first_recovery(rows):
 for i in range(len(rows)-1):
  if rows[i]["val_accuracy"]>=.99 and rows[i+1]["val_accuracy"]>=.99:
   return int(rows[i]["step"])
 return None

def run():
 started=time.perf_counter()
 for seed in SEEDS:
  for lam in (1e-5,.001):
   base=RUNS/f"seed{seed}_prior{lam:g}"
   cp=base/"ck_010000.pt"
   payload=torch.load(cp,map_location="cpu",weights_only=False)
   net=MLP(300);net.load_state_dict(payload["model"])
   original=measure(net,0)
   assert original["train_accuracy"]==original["val_accuracy"]==1.,(seed,lam,original)
   modeldir=OUT/f"seed{seed}_prior{lam:g}"
   modeldir.mkdir(exist_ok=True)
   con_path=modeldir/"control.csv"
   if con_path.exists():
    with con_path.open(newline="",encoding="utf-8") as f:control=list(csv.DictReader(f))
    control=[{k:float(v) for k,v in row.items()} for row in control]
    assert len(control)==51
   else:
    control=continue_train(copy.deepcopy(net))
    put_csv(con_path,control)
   assert control[0]["val_accuracy"]==1.
   for dose in D0SES:
    for ms in MASKS:
     key=f"dose{dose:03d}_mask{ms}"
     output_csv=modeldir/(key+".csv")
     result_json=modeldir/(key+".json")
     if output_csv.exists() and result_json.exists():
      continue
     if output_csv.exists()!=result_json.exists():
      raise RuntimeError("Partial lesion artifacts, manual inspect "+str(result_json))
     masked=copy.deepcopy(net)
     picked=sorted(perms[ms][:dose])
     assert len(set(picked))==dose
     with torch.no_grad():
      masked.mask[picked]=0.
     traj=continue_train(masked)
     init_drop=100*(original["val_accuracy"]-traj[0]["val_accuracy"])
     gap=[c["val_accuracy"]-r["val_accuracy"] for c,r in zip(control,traj)]
     auc=sum((gap[j]+gap[j+1])/2*(traj[j+1]["step"]-traj[j]["step"]) for j in range(len(gap)-1))
     t=first_recovery(traj)
     result={"seed":seed,"prior_l1":lam,
             "group":"grokking_tardio" if lam==1e-5 else "aprendizaje_rapido",
             "common_l1":.0001,"repair_l1":.0001,
             "training_checkpoint_step":10000,
             "mask_seed":ms,"dose":dose,"fraction":dose/300.,
             "masked_indices":picked,
             "permutation_sha256":hashlib.sha256(np.array(perms[ms],dtype=np.int16).tobytes()).hexdigest(),
             "initial_val_damage_pp":init_drop,
             "initial_val_ce_delta":traj[0]["val_ce"]-original["val_ce"],
             "initial_train_damage_pp":100*(original["train_accuracy"]-traj[0]["train_accuracy"]),
             "recovery99_two_consecutive_step":t,"censored_at_500":t is None,
             "auc_val_control_minus_injured":auc,
             "normalized_auc_if_damage_gt2pp":auc/(init_drop/100.) if init_drop>2 else None,
             "control_val_final":control[-1]["val_accuracy"],
             "injured_val_final":traj[-1]["val_accuracy"],
             "invalid_numerical":not all(np.isfinite(z) for z in [init_drop,auc,traj[-1]["val_accuracy"]])}
     if result["invalid_numerical"]:raise RuntimeError("Non-finite result: "+str(result))
     put_csv(output_csv,traj)
     result_json.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
     print("V13",seed,f"{lam:g}",f"{dose}/300",ms,
           "injury_pp",round(init_drop,2),
           "recover",t if t is not None else "CENSORED",
           "auc",round(auc,2),
           "elapsed",round(time.perf_counter()-started,1),flush=True)
 print("V13_COMPLETE",round(time.perf_counter()-started,1),flush=True)

if __name__=="__main__":run()
