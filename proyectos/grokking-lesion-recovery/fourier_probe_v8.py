"""Exploratory Fourier-seeded B on same mixed task; not a causal isolation."""
from pathlib import Path
import argparse,time,json,csv,hashlib,math,platform
import torch
from torch.nn import functional as F
from gated_v6 import GatedNet,build_data,measure
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(4)
def run(a):
 x,y,idx=build_data(a.p,a.noise_total,a.train_frac,a.valid_frac,a.split_seed)
 torch.manual_seed(a.seed)
 net=GatedNet(a.p,a.dim,a.branch_hidden)
 if a.dim !=32 or a.p!=31: raise ValueError("Fourier init version fixed to p31 dim32")
 with torch.no_grad():
  freq=torch.arange(1,17,dtype=torch.float)
  residues=torch.arange(31,dtype=torch.float).unsqueeze(1)
  theta=2*torch.pi*residues*freq/31
  features=torch.stack([torch.cos(theta),torch.sin(theta)],dim=2).reshape(31,32)
  # sqrt(2) scales each feature to approx unit variance, comparable to normal embedding
  net.clean.emb.weight.copy_(features*2**.5)
 opt=torch.optim.AdamW([{"params":list(net.clean.parameters()),"weight_decay":a.wd_clean},
                         {"params":list(net.noise.parameters()),"weight_decay":a.wd_noise}],lr=a.lr)
 out=ROOT/"fourier_runs"/f"seed{a.seed}_wd{a.wd_clean}_p31_h300"
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True)
 cfg=vars(a).copy()
 cfg["intervention"]="clean_embedding_sin_cos_k1_to16"
 cfg["hash_data"]=hashlib.sha256(x.numpy().tobytes()+y.numpy().tobytes()).hexdigest()
 (out/"config.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
 rows=[measure(net,x,y,idx,0)]
 def checkpoint(step):
  torch.save({"model":net.state_dict(),"optim":opt.state_dict(),"step":step,"config":cfg},out/f"ck_{step:06d}.pt")
 checkpoint(0)
 started=time.perf_counter()
 for step in range(1,a.steps+1):
  net.train();opt.zero_grad(set_to_none=True)
  loss=F.cross_entropy(net(x[idx["train"]]),y[idx["train"]])
  loss.backward();opt.step()
  if step%a.record_every==0 or step==a.steps:
   row=measure(net,x,y,idx,step);rows.append(row)
   if step%a.checkpoint_every==0 or step==a.steps:checkpoint(step)
   if step%2000==0 or step==a.steps:
    print("AT",a.wd_clean,step,"train",round(row["train_acc"],4),"clean_train",round(row["clean_train_acc"],4),"clean_val",round(row["clean_val_acc"],4),"val",round(row["val_acc"],4),flush=True)
 with (out/"metrics.csv").open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 result={"dir":str(out),"elapsed":round(time.perf_counter()-started,2),"last":rows[-1]}
 (out/"result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print("RESULT",a.wd_clean,round(rows[-1]["train_acc"],4),round(rows[-1]["val_acc"],4),flush=True)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--p",type=int,default=31)
 p.add_argument("--noise-total",type=int,default=640)
 p.add_argument("--train-frac",type=float,default=.55)
 p.add_argument("--valid-frac",type=float,default=.20)
 p.add_argument("--split-seed",type=int,default=2731)
 p.add_argument("--seed",type=int,default=0)
 p.add_argument("--dim",type=int,default=32)
 p.add_argument("--branch-hidden",type=int,default=150)
 p.add_argument("--wd-clean",type=float,default=1.0)
 p.add_argument("--wd-noise",type=float,default=.05)
 p.add_argument("--lr",type=float,default=.001)
 p.add_argument("--steps",type=int,default=22000)
 p.add_argument("--record-every",type=int,default=200)
 p.add_argument("--checkpoint-every",type=int,default=2000)
 run(p.parse_args())
