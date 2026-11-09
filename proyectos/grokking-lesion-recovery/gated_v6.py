"""V6 isolated task channels, exactly 300 hidden units. Instrumental design only.
Clean modular addition and memorized random labels have separate subnets (150+150).
This makes source of partial accuracy explicit; NOT intrinsic single-task semi-grokking.
"""
from __future__ import annotations
from pathlib import Path
import argparse,sys,json,csv,hashlib,platform,time
import torch
from torch import nn
from torch.nn import functional as F
from mixed_v4 import build_data
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent

class Branch(nn.Module):
 def __init__(self,p=31,dim=32,h=150):
  super().__init__()
  self.emb=nn.Embedding(p,dim)
  self.fc=nn.Linear(2*dim,h)
  self.out=nn.Linear(h,p)
  self.register_buffer("mask",torch.ones(h))
 def forward(self,x):
  t=self.emb(x).reshape(-1,2*self.emb.embedding_dim)
  return self.out(F.relu(self.fc(t))*self.mask)

class GatedNet(nn.Module):
 def __init__(self,p=31,dim=32,h=150):
  super().__init__()
  self.clean=Branch(p,dim,h)
  self.noise=Branch(p,dim,h)
 def forward(self,x):
  a=self.clean(x[:,:2]); b=self.noise(x[:,:2])
  return torch.where(x[:,2,None]==0,a,b)

@torch.no_grad()
def measure(model,x,y,ids,step):
 model.eval()
 z=model(x)
 ret={"step":step}
 for k in ("train","val","test","clean_train","noise_train","clean_val","noise_val","clean_test","noise_test"):
  ix=ids[k]; ret[k+"_acc"]=float((z[ix].argmax(-1)==y[ix]).float().mean())
  ret[k+"_loss"]=float(F.cross_entropy(z[ix],y[ix]))
 return ret

def run(a):
 x,y,idx=build_data(a.p,a.noise_total,a.train_frac,a.valid_frac,a.split_seed)
 torch.manual_seed(a.seed)
 model=GatedNet(a.p,a.dim,a.branch_hidden)
 if a.init_scale!=1.:
  with torch.no_grad():
   for param in model.parameters():param.mul_(a.init_scale)
 opt=torch.optim.AdamW([{"params":list(model.clean.parameters()),"weight_decay":a.wd_clean},
       {"params":list(model.noise.parameters()),"weight_decay":a.wd_noise}],
       lr=a.lr)
 path=ROOT/"gated_runs"/f"cleanWD{a.wd_clean}_noiseWD{a.wd_noise}_init{a.init_scale}_s{a.seed}_train{a.train_frac}"
 if path.exists():raise FileExistsError(path)
 path.mkdir(parents=True)
 cfg=vars(a).copy()
 cfg["data_sha256"]=hashlib.sha256(x.numpy().tobytes()+y.numpy().tobytes()).hexdigest()
 cfg["runtime"]={"torch":torch.__version__,"python":platform.python_version(),"ntrain":len(idx["train"]),"nval":len(idx["val"]),"ntest":len(idx["test"])}
 (path/"config.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
 rows=[measure(model,x,y,idx,0)]
 def checkpoint(step):
  torch.save({"model":model.state_dict(),"optim":opt.state_dict(),"step":step,"config":cfg},path/f"ck_{step:06d}.pt")
 checkpoint(0)
 ts=time.perf_counter()
 for step in range(1,a.steps+1):
  model.train();opt.zero_grad(set_to_none=True)
  loss=F.cross_entropy(model(x[idx["train"]]),y[idx["train"]]);loss.backward();opt.step()
  if step%a.record_every==0 or step==a.steps:
   r=measure(model,x,y,idx,step);rows.append(r)
   if step%a.checkpoint_every==0 or step==a.steps or (r["val_acc"]>.50 and step%500==0):checkpoint(step)
   if step%2000==0 or step==a.steps:
    print("AT",a.wd_clean,a.init_scale,step,
       "train",round(r["train_acc"],3),"val",round(r["val_acc"],3),
       "clean_train",round(r["clean_train_acc"],3),"clean_val",round(r["clean_val_acc"],3),
       "noise_train",round(r["noise_train_acc"],3),flush=True)
 with (path/"metrics.csv").open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 result={"folder":str(path),"elapsed":round(time.perf_counter()-ts,2),"final":rows[-1]}
 (path/"summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print("RESULT",a.wd_clean,a.init_scale,json.dumps({k:round(rows[-1][k],4) for k in ("train_acc","val_acc","clean_train_acc","clean_val_acc","noise_train_acc")}),flush=True)

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
 p.add_argument("--init-scale",type=float,default=1.)
 p.add_argument("--wd-clean",type=float,default=1.)
 p.add_argument("--wd-noise",type=float,default=.05)
 p.add_argument("--lr",type=float,default=.001)
 p.add_argument("--steps",type=int,default=18000)
 p.add_argument("--record-every",type=int,default=200)
 p.add_argument("--checkpoint-every",type=int,default=3000)
 run(p.parse_args())
