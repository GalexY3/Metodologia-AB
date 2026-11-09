"""Exploratory counterfactual weight-decay schedules on same task and split.
Resumes original optimizer, controls test leakage by showing only validation in console.
"""
from __future__ import annotations
import argparse,csv,json,sys,time,hashlib,platform,copy
from pathlib import Path
import torch
from torch.nn import functional as F
from mixed_v4 import MixedNet,build_data,measure
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(4)
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--checkpoint",required=True)
 p.add_argument("--schedule",required=True,help="comma-delimited WD:steps")
 p.add_argument("--name",required=True)
 p.add_argument("--record-every",type=int,default=250)
 p.add_argument("--checkpoint-every",type=int,default=2000)
 args=p.parse_args()
 path=Path(args.checkpoint)
 pack=torch.load(path,map_location="cpu",weights_only=False)
 c=pack["config"];x,y,ids=build_data(c["p"],c["noise_total"],c["train_frac"],c["valid_frac"],c["split_seed"])
 hashnow=hashlib.sha256(x.numpy().tobytes()+y.numpy().tobytes()).hexdigest()
 if hashnow!=c["data_digest"]:raise ValueError("Dataset mismatch")
 net=MixedNet(c["p"],c["dim"],c["hidden"])
 net.load_state_dict(pack["model"])
 opt=torch.optim.AdamW(net.parameters(),lr=c["lr"],weight_decay=c["wd"])
 opt.load_state_dict(pack["optimizer"])
 schedule=[(float(chunk.split(":")[0]),int(chunk.split(":")[1])) for chunk in args.schedule.split(",")]
 if not schedule or any(steps<1 for wd,steps in schedule):raise ValueError("Bad schedule")
 out=ROOT/"schedule_runs"/args.name
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True)
 initial_step=int(pack["step"])
 runconfig={"source":str(path),"initial_step":initial_step,"schedule":schedule,"source_config":c,"code":"schedule_v5.py","status":"exploratory"}
 (out/"config.json").write_text(json.dumps(runconfig,indent=2),encoding="utf-8")
 rows=[]
 def record(step,phase):
  m=measure(net,x,y,ids,step)
  m["phase"]=phase
  rows.append(m)
  return m
 r=record(initial_step,-1)
 print("START",args.name,initial_step,"train",round(r["train_acc"],3),"val",round(r["val_acc"],3),flush=True)
 start=time.perf_counter()
 def save(step):
  torch.save({"model":net.state_dict(),"optimizer":opt.state_dict(),"config":c,"step":step,"source":str(path),"schedule":schedule},out/f"ck_{step:06d}.pt")
 save(initial_step)
 step=initial_step
 for phase,(wd,length) in enumerate(schedule):
  for group in opt.param_groups:group["weight_decay"]=wd
  for j in range(1,length+1):
   step+=1
   net.train();opt.zero_grad(set_to_none=True)
   loss=F.cross_entropy(net(x[ids["train"]]),y[ids["train"]]);loss.backward();opt.step()
   if j%args.record_every==0 or j==length:
    r=record(step,phase)
    if step%args.checkpoint_every==0 or j==length or (.55<=r["val_acc"]<=.67 and j%500==0):save(step)
    if j%2000==0 or j==length:print("AT",args.name,phase,wd,step,"train",round(r["train_acc"],3),"val",round(r["val_acc"],3),"clean",round(r["clean_val_acc"],3),flush=True)
 with (out/"metrics.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 result={"name":args.name,"step_final":step,"elapsed":round(time.perf_counter()-start,2),"baseline":rows[0],"last":rows[-1]}
 (out/"result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print("RESULT",args.name,step,round(result["last"]["train_acc"],3),round(result["last"]["val_acc"],3),flush=True)
if __name__=="__main__":main()
