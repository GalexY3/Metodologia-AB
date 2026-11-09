"""V14 2x3 intervention on L1 final schedule, same initial checkpoints.
See PREREG_V14_FACTORIAL.md. No test partition is consulted.
"""
from pathlib import Path
import csv,json,time,copy,hashlib
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"v14_factorial"
OUT.mkdir(exist_ok=True)
SEEDS=[11,12,13,14,18]
ORIGINS=(1e-5,.001)
FINALS=(1e-5,.0001,.001)
x,y,idx=data(20261110,500,1000,2000)
tr_x=x[idx["train"]];tr_y=y[idx["train"]]
va_x=x[idx["val"]];va_y=y[idx["val"]]

@torch.no_grad()
def measure(model,step):
 model.eval();a=model(tr_x);b=model(va_x)
 return {"step":step,
  "train_accuracy":float((a.argmax(1)==tr_y).float().mean()),
  "val_accuracy":float((b.argmax(1)==va_y).float().mean()),
  "train_ce":float(F.cross_entropy(a,tr_y)),
  "val_ce":float(F.cross_entropy(b,va_y)),
  "model_l2":float(torch.sqrt(sum(z.detach().square().sum() for z in model.parameters())))}

def save_csv(path,rows):
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]))
  w.writeheader();w.writerows(rows)

def run():
 started=time.perf_counter()
 for seed in SEEDS:
  for orig in ORIGINS:
   origin_name=f"seed{seed}_prior{orig:g}"
   original=ROOT/"v12_runs"/origin_name/"ck_006000.pt"
   state=torch.load(original,map_location="cpu",weights_only=False)
   for final_lambda in FINALS:
    folder=OUT/origin_name/f"finalL1_{final_lambda:g}"
    folder.mkdir(parents=True,exist_ok=True)
    resultfile=folder/"result.json"
    checkpoint=folder/"ck_010000.pt"
    metricfile=folder/"metrics.csv"
    if resultfile.exists() and checkpoint.exists() and metricfile.exists():
     continue
    if any(p.exists() for p in (resultfile,checkpoint,metricfile)):
     raise RuntimeError("Partial factorial run "+str(folder))
    model=MLP(300);model.load_state_dict(state["model"])
    old=measure(model,6000)
    assert old["train_accuracy"]==old["val_accuracy"]==1.,(seed,orig,old)
    opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0.)
    logs=[old]
    for i in range(1,4001):
     model.train();opt.zero_grad(set_to_none=True)
     loss=F.cross_entropy(model(tr_x),tr_y)+final_lambda*sum(v.abs().sum() for v in model.parameters())
     loss.backward();opt.step()
     if i%500==0:logs.append(measure(model,6000+i))
    eligible=all(z["train_accuracy"]==1. and z["val_accuracy"]==1. for z in logs[-3:])
    conf={
      "seed":seed,"initial_l1":orig,"final_l1":final_lambda,
      "start_step":6000,"final_step":10000,
      "shared_split_seed":20261110,
      "train_eval_only":True,
      "same_init_from_checkpoint":str(original),
      "final_accuracy_valid":logs[-1]["val_accuracy"],
      "final_last3_full":eligible,
      "protocol":"PREREG_V14_FACTORIAL.md"}
    torch.save({"model":model.state_dict(),"config":conf,"step":10000},checkpoint)
    save_csv(metricfile,logs)
    resultfile.write_text(json.dumps(conf,ensure_ascii=False,indent=2),encoding="utf-8")
    print("V14_TRAIN",seed,f"initial{orig:g}",f"final{final_lambda:g}",
      "validation",round(logs[-1]["val_accuracy"],4),
      "last3_full",eligible,
      "time_s",round(time.perf_counter()-started,1),flush=True)
 print("V14_TRAIN_DONE",round(time.perf_counter()-started,1),flush=True)

if __name__=="__main__":run()
