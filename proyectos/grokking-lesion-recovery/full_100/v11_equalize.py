"""V11: shared-L1 continuation from two acquisition histories.
Designed before running, see PREREG_V11.md. Does not estimate a pure causal
effect of grokking; both histories used different L1.
"""
from pathlib import Path
import argparse,csv,json,platform,copy,time
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data,measure
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(4)
def main(a):
 x,y,indices=data(20261109,500,1000,2000)
 for seed in a.seeds:
  for lam in (1e-5,.001):
   for common in a.common_lambdas:
    name=f"lambda{lam:g}_seed{seed}_lr0.001_width300_nt500"
    ckfile=ROOT/"parity_runs"/name/"ck_005000.pt"
    ck=torch.load(ckfile,map_location="cpu",weights_only=False)
    if ck["step"]!=5000:raise RuntimeError("Wrong baseline checkpoint")
    net=MLP(300);net.load_state_dict(ck["model"])
    baseline=measure(net,x,y,indices,5000)
    if min(baseline["train_acc"],baseline["val_acc"],baseline["test_acc"])<1.:
     print("INELIGIBLE",name,"baseline",baseline,flush=True)
     continue
    dest=ROOT/"v11_common_runs"/f"{name}_commonL1_{common:g}_4000"
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True)
    cfg={"source":str(ckfile),"source_step":5000,"source_initial_l1":lam,
         "common_l1":common,"seed":seed,"source_eligible":True,
         "repair_lr":.001,"optimizer":"fresh AdamW, wd0",
         "total_additional_steps":4000,"protocol":"PREREG_V11.md"}
    (dest/"config.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
    opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=0.)
    rows=[baseline]
    def snap(step):
     torch.save({"model":net.state_dict(),"optimizer":opt.state_dict(),"config":cfg,"step":step},dest/f"ck_{step:06d}.pt")
    snap(5000);t0=time.perf_counter()
    for i in range(1,4001):
     net.train();opt.zero_grad(set_to_none=True)
     logits=net(x[indices["train"]])
     loss=F.cross_entropy(logits,y[indices["train"]])+common*sum(q.abs().sum() for q in net.parameters())
     loss.backward();opt.step()
     if i%250==0 or i==4000:
      meas=measure(net,x,y,indices,5000+i)
      rows.append(meas)
      if i%1000==0:
       snap(5000+i)
       print("V11",seed,f"prior{lam:g}",f"common{common:g}","step",5000+i,"tr",round(meas["train_acc"],3),"val",round(meas["val_acc"],3),"CE",round(meas["val_loss"],6),flush=True)
    with (dest/"metrics.csv").open("w",newline="",encoding="utf-8") as f:
     wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    print("DONE",seed,lam,common,round(time.perf_counter()-t0,2),round(rows[-1]["val_acc"],3),flush=True)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--seeds",nargs="+",type=int,default=list(range(5)))
 p.add_argument("--common-lambdas",nargs="+",type=float,default=[0.,.0001])
 main(p.parse_args())
