"""V14B continue original optimizer from step6000, without changing original L1.
Compare frozen V14 fresh-optimizer runs under exactly same objective and duration.
"""
from pathlib import Path
import json,csv,time
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"v14b_original_adam_moments"
OUT.mkdir(exist_ok=True)
SEEDS=[11,12,13,14,18]
ORIG=(1e-5,.001)
x,y,ids=data(20261110,500,1000,2000)
X=x[ids["train"]];Y=y[ids["train"]];XV=x[ids["val"]];YV=y[ids["val"]]
@torch.no_grad()
def metric(m,step):
 m.eval()
 a=m(X);b=m(XV)
 return {"step":step,
   "train_acc":float((a.argmax(1)==Y).float().mean()),
   "val_acc":float((b.argmax(1)==YV).float().mean()),
   "val_ce":float(F.cross_entropy(b,YV)),
   "train_ce":float(F.cross_entropy(a,Y))}

def run():
 start=time.perf_counter()
 for seed in SEEDS:
  for lam in ORIG:
   name=f"seed{seed}_prior{lam:g}"
   cp=ROOT/"v12_runs"/name/"ck_006000.pt"
   original=torch.load(cp,map_location="cpu",weights_only=False)
   if "optimizer" not in original:raise ValueError("Missing original optimizer state: "+str(cp))
   m=MLP(300);m.load_state_dict(original["model"])
   opt=torch.optim.AdamW(m.parameters(),lr=.001,weight_decay=0.)
   opt.load_state_dict(original["optimizer"])
   if len(opt.state)==0:raise ValueError("Optimizer moments unavailable after load")
   for group in opt.param_groups:
    if abs(group["lr"]-.001)>1e-12 or abs(group["weight_decay"])>1e-12:
     raise ValueError("Hyperparameter mismatch in restored optimizer")
   base=metric(m,6000)
   assert base["train_acc"]==base["val_acc"]==1.
   output=OUT/name
   output.mkdir(exist_ok=True)
   c=output/"ck_010000.pt";f=output/"metrics.csv";j=output/"result.json"
   if all(z.exists() for z in (c,f,j)):continue
   if any(z.exists() for z in (c,f,j)):raise RuntimeError("Partial run "+str(output))
   history=[base]
   for step in range(6001,10001):
    m.train();opt.zero_grad(set_to_none=True)
    ce=F.cross_entropy(m(X),Y)
    penalty=lam*sum(v.abs().sum() for v in m.parameters())
    (ce+penalty).backward()
    opt.step()
    if step%500==0:history.append(metric(m,step))
   stable=all(z["train_acc"]==z["val_acc"]==1. for z in history[-3:])
   info={"seed":seed,"original_l1":lam,"final_l1":lam,
      "optimizer_original_moments_restored":True,
      "trained_additional_steps":4000,"step":10000,
      "stable_last3":stable,
      "final_val_acc":history[-1]["val_acc"],
      "protocol":"PREREG_V14B_OPTIMIZER.md"}
   torch.save({"model":m.state_dict(),"config":info,"step":10000},c)
   with f.open("w",newline="",encoding="utf-8") as file:
    writer=csv.DictWriter(file,fieldnames=list(history[0]))
    writer.writeheader();writer.writerows(history)
   j.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
   print("V14B",seed,f"original_L1{lam:g}","val",history[-1]["val_acc"],
         "stable",stable,"elapsed",round(time.perf_counter()-start,1),flush=True)
 print("V14B_DONE",round(time.perf_counter()-start,1),flush=True)
if __name__=="__main__":run()
