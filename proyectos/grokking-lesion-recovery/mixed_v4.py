"""Feasibility V4: shared-task 300-neuron MLP with learnable and random-label branches.
Pilot only. Random-label branch creates a known upper bound on aggregate test accuracy:
this is NOT Varma-style intrinsic semi-grokking of a single homogeneous task.
"""
from pathlib import Path
import os, json, hashlib, time, csv, argparse, platform, random
os.environ.setdefault("OMP_NUM_THREADS","4")
import torch
import numpy as np
from torch import nn
from torch.nn import functional as F
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(4)

class MixedNet(nn.Module):
 def __init__(self,p=31,dim=32,hidden=300):
  super().__init__()
  self.p=p
  self.emb=nn.Embedding(p,dim)
  self.context=nn.Embedding(2,16)
  self.fc=nn.Linear(2*dim+16,hidden)
  self.out=nn.Linear(hidden,p)
  self.register_buffer("mask",torch.ones(hidden))
 def forward(self,x):
  z=torch.cat([self.emb(x[:,:2]).reshape(len(x),-1),self.context(x[:,2])],dim=1)
  return self.out(F.relu(self.fc(z))*self.mask)

def build_data(p=31,noise_total=640,train_frac=.55,valid_frac=.20,seed=2731):
 gen=torch.Generator().manual_seed(seed)
 a,b=torch.meshgrid(torch.arange(p),torch.arange(p),indexing="ij")
 pairs=torch.stack([a.flatten(),b.flatten()],dim=1)
 noise_indices=torch.randperm(p*p,generator=gen)[:noise_total]
 clean_x=torch.cat([pairs,torch.zeros(len(pairs),1,dtype=torch.long)],dim=1)
 noise_x=torch.cat([pairs[noise_indices],torch.ones(noise_total,1,dtype=torch.long)],dim=1)
 clean_y=(pairs[:,0]+pairs[:,1])%p
 noise_y=torch.randint(p,(noise_total,),generator=gen)
 x=torch.cat([clean_x,noise_x])
 y=torch.cat([clean_y,noise_y])
 indices={}
 for label,items in (("clean",torch.arange(len(clean_x))),("noise",torch.arange(len(clean_x),len(x)))):
  items=items[torch.randperm(len(items),generator=gen)]
  n_tr=int(len(items)*train_frac)
  n_val=int(len(items)*valid_frac)
  indices[label+"_train"]=items[:n_tr]
  indices[label+"_val"]=items[n_tr:n_tr+n_val]
  indices[label+"_test"]=items[n_tr+n_val:]
 for split in ("train","val","test"):
  indices[split]=torch.cat([indices["clean_"+split],indices["noise_"+split]])
 return x,y,indices

@torch.no_grad()
def measure(net,x,y,ids,step):
 net.eval()
 logits=net(x)
 r={"step":step}
 for section in ("train","val","test","clean_train","noise_train","clean_val","noise_val","clean_test","noise_test"):
  ix=ids[section]
  r[section+"_acc"]=float((logits[ix].argmax(-1)==y[ix]).float().mean())
  r[section+"_loss"]=float(F.cross_entropy(logits[ix],y[ix]))
 r["weight_l2"]=float(torch.linalg.vector_norm(torch.cat([q.reshape(-1) for q in net.parameters()])))
 return r

def run(args):
 x,y,ix=build_data(args.p,args.noise_total,args.train_frac,args.valid_frac,args.split_seed)
 torch.manual_seed(args.seed)
 random.seed(args.seed)
 net=MixedNet(args.p,args.dim,args.hidden)
 with torch.no_grad():
  if args.init_scale!=1.:
   for w in net.parameters():w.mul_(args.init_scale)
 opt=torch.optim.AdamW(net.parameters(),lr=args.lr,weight_decay=args.wd)
 path=ROOT/"mixed_runs"/f"p{args.p}_nt{args.noise_total}_train{args.train_frac}_wd{args.wd}_scale{args.init_scale}_s{args.seed}"
 path.mkdir(parents=True,exist_ok=True)
 config={k:v for k,v in vars(args).items() if k!="cmd"}
 config.update({"python":platform.python_version(),"torch":torch.__version__,"data_digest":hashlib.sha256(x.numpy().tobytes()+y.numpy().tobytes()).hexdigest(),"split_hashes":{k:hashlib.sha256(v.numpy().tobytes()).hexdigest() for k,v in ix.items()},"n_total":len(x),"n_train":len(ix["train"]),"n_val":len(ix["val"]),"n_test":len(ix["test"])})
 (path/"config.json").write_text(json.dumps(config,indent=2),encoding="utf-8")
 rows=[measure(net,x,y,ix,0)]
 start=time.perf_counter()
 def cp(step):
  torch.save({"model":net.state_dict(),"optimizer":opt.state_dict(),"config":config,"step":step},path/f"ck_{step:06d}.pt")
 cp(0)
 for step in range(1,args.steps+1):
  opt.zero_grad(set_to_none=True)
  loss=F.cross_entropy(net(x[ix["train"]]),y[ix["train"]])
  loss.backward();opt.step()
  if step%args.record_every==0 or step==args.steps:
   r=measure(net,x,y,ix,step)
   rows.append(r)
   if step%args.checkpoint_every==0 or step==args.steps or (.52 <= r["val_acc"] <= .72 and step%args.record_every==0):
    cp(step)
   if step%1000==0:
    print("AT",args.wd,args.train_frac,args.seed,step,round(r["train_acc"],4),round(r["val_acc"],4),round(r["clean_val_acc"],4),round(r["noise_val_acc"],4),flush=True)
 with (path/"metrics.csv").open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 result={"dir":str(path),"runtime_s":round(time.perf_counter()-start,2),"last":rows[-1]}
 (path/"result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print("RESULT",json.dumps(result),flush=True)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--p",type=int,default=31)
 p.add_argument("--noise-total",type=int,default=640)
 p.add_argument("--train-frac",type=float,default=.55)
 p.add_argument("--valid-frac",type=float,default=.2)
 p.add_argument("--split-seed",type=int,default=2731)
 p.add_argument("--seed",type=int,default=0)
 p.add_argument("--dim",type=int,default=32)
 p.add_argument("--hidden",type=int,default=300)
 p.add_argument("--init-scale",type=float,default=1.0)
 p.add_argument("--lr",type=float,default=.001)
 p.add_argument("--wd",type=float,default=1.0)
 p.add_argument("--steps",type=int,default=12000)
 p.add_argument("--record-every",type=int,default=200)
 p.add_argument("--checkpoint-every",type=int,default=2000)
 args=p.parse_args()
 run(args)
