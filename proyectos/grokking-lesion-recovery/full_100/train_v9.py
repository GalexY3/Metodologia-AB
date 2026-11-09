"""V9: same 300-unit MLP, same modular task and reserved split, training-path search.
Explore learning curves; never infer continuous learning from the final score alone.
"""
import argparse,random,json,csv,time,hashlib,platform,sys,copy
from pathlib import Path
import torch
from torch.nn import functional as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from study import Net
torch.set_num_threads(4)
HERE=Path(__file__).resolve().parent
def build(p=31, frac=.55, seed=20261109):
 a,b=torch.meshgrid(torch.arange(p),torch.arange(p),indexing="ij")
 x=torch.stack([a.reshape(-1),b.reshape(-1)],dim=1)
 y=(x[:,0]+x[:,1])%p
 idx=torch.randperm(len(y),generator=torch.Generator().manual_seed(seed))
 ntr=int(len(y)*frac)
 tr=idx[:ntr]
 remaining=idx[ntr:]
 val=remaining[:len(remaining)//2]
 test=remaining[len(remaining)//2:]
 return x,y,{"train":tr,"val":val,"test":test}
@torch.no_grad()
def measure(m,x,y,ix,step):
 m.eval();z=m(x)
 out={"step":step}
 for k,v in ix.items():
  out[k+"_accuracy"]=float((z[v].argmax(1)==y[v]).float().mean())
  out[k+"_loss"]=float(F.cross_entropy(z[v],y[v]))
 logits=z[ix["val"]]
 logits_sorted=logits.topk(2,dim=1).values
 out["val_margin"]=float((logits_sorted[:,0]-logits_sorted[:,1]).mean())
 out["weight_norm"]=float(torch.sqrt(sum((p.detach()**2).sum() for p in m.parameters())))
 return out
def run(a):
 x,y,ix=build(a.p,a.fraction,a.split_seed)
 torch.manual_seed(a.seed);random.seed(a.seed)
 m=Net(a.p,a.dim,a.hidden)
 if a.init_scale!=1.:
  with torch.no_grad():
   for p in m.parameters():p.mul_(a.init_scale)
 opt=torch.optim.AdamW(m.parameters(),lr=a.lr,weight_decay=a.wd)
 name=f"wd{a.wd}_scale{a.init_scale}_lr{a.lr}_seed{a.seed}_split{a.split_seed}"
 root=HERE/"runs"/name
 if root.exists():raise FileExistsError(root)
 root.mkdir(parents=True)
 cfg=vars(a).copy()
 cfg.update({"python":platform.python_version(),"torch":torch.__version__,"split_hashes":{k:hashlib.sha256(v.numpy().tobytes()).hexdigest() for k,v in ix.items()},"n_train":len(ix["train"]),"n_val":len(ix["val"]),"n_test":len(ix["test"])})
 (root/"config.json").write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding="utf-8")
 def save(step):
  torch.save({"model":m.state_dict(),"optimizer":opt.state_dict(),"config":cfg,"step":step},root/f"checkpoint_{step:06d}.pt")
 records=[measure(m,x,y,ix,0)];save(0)
 prev_cons=0
 begin=time.perf_counter()
 for step in range(1,a.steps+1):
  m.train()
  opt.zero_grad(set_to_none=True)
  loss=F.cross_entropy(m(x[ix["train"]]),y[ix["train"]])
  loss.backward()
  opt.step()
  if step%a.log_every==0 or step==a.steps:
   v=measure(m,x,y,ix,step);records.append(v)
   if v["train_accuracy"]>=.99 and v["val_accuracy"]==1.:prev_cons+=1
   else:prev_cons=0
   if step%a.save_every==0 or step==a.steps or (prev_cons==5 or prev_cons==10):save(step)
   if step%1000==0 or step==a.steps:
    print("METRIC",name,step,"train",round(v["train_accuracy"],4),"val",round(v["val_accuracy"],4),"valloss",round(v["val_loss"],3),flush=True)
 with (root/"history.csv").open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)
 result={"name":name,"elapsed_s":round(time.perf_counter()-begin,2),"final":records[-1],"checkpoint_final":str(root/f"checkpoint_{a.steps:06d}.pt")}
 (root/"summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print("DONE",json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--p",type=int,default=31)
 p.add_argument("--fraction",type=float,default=.55)
 p.add_argument("--split-seed",type=int,default=20261109)
 p.add_argument("--seed",type=int,default=0)
 p.add_argument("--dim",type=int,default=32)
 p.add_argument("--hidden",type=int,default=300)
 p.add_argument("--wd",type=float,default=1.)
 p.add_argument("--lr",type=float,default=.001)
 p.add_argument("--init-scale",type=float,default=1.)
 p.add_argument("--steps",type=int,default=12000)
 p.add_argument("--log-every",type=int,default=100)
 p.add_argument("--save-every",type=int,default=3000)
 run(p.parse_args())
